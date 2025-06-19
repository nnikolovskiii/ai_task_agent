from operator import add
from typing import List, Annotated, TypedDict
import atexit


from langchain.schema.runnable.config import RunnableConfig
from langchain_cohere import CohereRerank
from langchain_core.documents import Document
from langchain_core.messages import AnyMessage, HumanMessage, AIMessage
# Changed import from Google to OpenAI
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.types import Send

from src.agent.prompts import query_writer_instructions, get_current_date, reflection_instructions, \
    answer_instructions
from src.agent.init_weaviate import initialize_rag_components


class SearchQueryList(TypedDict):
    query: List[str]


class Reflection(TypedDict):
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: List[str]


DEFAULT_WEAVIATE_COLLECTION_NAME = "SavaCollection"
DEFAULT_WEAVIATE_TEXT_KEY = "text"
SEMANTIC_RESULTS_K = 50
BM25_RESULTS_LIMIT = 50
RERANK_TOP_N = 5


class OverallState(TypedDict):
    messages: Annotated[list, add_messages]
    query_list: List[str]
    search_query: Annotated[List[str], add]
    web_research_result: Annotated[List[str], add]
    sources_gathered: Annotated[List[dict], add]
    is_sufficient: bool
    knowledge_gap: str
    follow_up_queries: List[str]
    research_loop_count: int
    number_of_ran_queries: int
    initial_search_query_count: int
    max_research_loops: int


vector_store, weaviate_client, embedding_model = initialize_rag_components()


def _close_weaviate_connection():
    if weaviate_client:
        print("--- Closing Weaviate client connection on exit. ---")
        weaviate_client.close()


if weaviate_client:
    atexit.register(_close_weaviate_connection)

if vector_store and weaviate_client:
    retriever = vector_store.as_retriever(search_kwargs={'k': SEMANTIC_RESULTS_K})
    cohere_reranker = CohereRerank(model="rerank-english-v3.0", top_n=RERANK_TOP_N)
else:
    print("RAG components not fully initialized. The agent will not be able to retrieve documents.")
    retriever = None
    cohere_reranker = None


def get_research_topic(messages: list[AnyMessage]) -> str:
    """Extracts the research topic from the user's message."""
    if messages and isinstance(messages[-1], HumanMessage):
        return messages[-1].content
    return "No research topic found."


def generate_query(state: OverallState):
    """Node that generates search queries based on the User's question."""
    print("--- Calling Generate Query Node ---")
    state["initial_search_query_count"] = state.get("initial_search_query_count", 3)
    # Changed from ChatGoogleGenerativeAI to ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)
    structured_llm = llm.with_structured_output(SearchQueryList)
    formatted_prompt = query_writer_instructions.format(
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )
    result = structured_llm.invoke(formatted_prompt)
    return {"query_list": result.get('query', []), "initial_search_query_count": 3,}


def continue_to_rag_research(state: OverallState):
    """Routing function to start parallel RAG research for each query."""
    print("--- Routing to RAG Research ---")
    return [
        Send("rag_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["query_list"])
    ]


def rag_research(state: OverallState):
    """Node that performs hybrid RAG search for a given query."""
    user_query = state["search_query"][-1]
    print(f"--- Calling RAG Research Node for query: '{user_query}' ---")

    if not retriever or not weaviate_client or not cohere_reranker:
        print("ERROR: RAG components are not available. Skipping research.")
        return {
            "web_research_result": ["Could not perform research due to missing components."],
            "sources_gathered": [],
            "search_query": [user_query]
        }

    collection = weaviate_client.collections.get(DEFAULT_WEAVIATE_COLLECTION_NAME)
    bm25_response = collection.query.bm25(
        query=user_query,
        query_properties=[DEFAULT_WEAVIATE_TEXT_KEY],
        limit=BM25_RESULTS_LIMIT
    )
    bm25_docs = [Document(page_content=obj.properties[DEFAULT_WEAVIATE_TEXT_KEY]) for obj in bm25_response.objects]
    semantic_docs = retriever.invoke(user_query)
    unranked_docs = list({doc.page_content: doc for doc in bm25_docs + semantic_docs}.values())
    reranked_docs = cohere_reranker.compress_documents(documents=unranked_docs,
                                                       query=user_query) if unranked_docs else []

    if not reranked_docs:
        research_summary = "No relevant documents found."
        sources = []
    else:
        research_summary = "\n\n---\n\n".join([doc.page_content for doc in reranked_docs])
        sources = [{"source": doc.metadata.get("source", f"Doc {i + 1}"), "content": doc.page_content} for i, doc in
                   enumerate(reranked_docs)]

    return {
        "web_research_result": [research_summary],
        "sources_gathered": sources,
    }


def reflection(state: OverallState) -> dict:
    """Node that reflects on the gathered information and decides if more research is needed."""
    print("--- Calling Reflection Node ---")
    research_loop_count = state.get("research_loop_count", 0) + 1
    # Changed from ChatGoogleGenerativeAI to ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    structured_llm = llm.with_structured_output(Reflection)
    print("&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&&")
    print(len(state["web_research_result"]))
    formatted_prompt = reflection_instructions.format(
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
        number_queries=state["initial_search_query_count"],
    )
    result = structured_llm.invoke(formatted_prompt)
    return {
        "is_sufficient": result['is_sufficient'],
        "knowledge_gap": result['knowledge_gap'],
        "follow_up_queries": result['follow_up_queries'],
        "research_loop_count": research_loop_count,
        "number_of_ran_queries": len(state["search_query"]),
    }


def evaluate_research(state: OverallState) :
    """Routing function that decides whether to continue research or finalize the answer."""
    print("--- Evaluating Research ---")
    max_research_loops = state.get("max_research_loops", 2)
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        print("--- Decision: Finalize Answer ---")
        return "finalize_answer"
    else:
        print("--- Decision: Continue Research with Follow-up Queries ---")
        return [
            Send("rag_research", {"search_query": follow_up_query, "id": state["number_of_ran_queries"] + idx})
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]


def finalize_answer(state: OverallState):
    """
    This node is now a generator. It `yield`s each chunk of the response as an
    AIMessage, allowing `langgraph` to stream the output.
    """
    print("--- Calling Finalize Answer Node ---")
    messages = state["messages"]
    last_ai_message = messages[-1]
    # Changed from ChatGoogleGenerativeAI to ChatOpenAI
    llm = ChatOpenAI(model="gpt-4o", temperature=0.5)
    formatted_prompt = answer_instructions.format(
        current_date=get_current_date(),
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
        sources=state["sources_gathered"]
    )
    response = llm.invoke(formatted_prompt)

    return {"messages": [AIMessage(content=response.content)]}


builder = StateGraph(OverallState)

builder.add_node("generate_query", generate_query)
builder.add_node("rag_research", rag_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)

builder.add_edge(START, "generate_query")
builder.add_conditional_edges("generate_query", continue_to_rag_research)
builder.add_edge("rag_research", "reflection")
builder.add_conditional_edges("reflection", evaluate_research, {
    "finalize_answer": "finalize_answer",
    "rag_research": "rag_research"
})
builder.add_edge("finalize_answer", END)

graph = builder.compile()
