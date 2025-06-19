from __future__ import annotations

import operator
from typing import TypedDict, Literal, Annotated, Optional

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph, add_messages
from pydantic import BaseModel, Field

from agent.gemini_transcript import transcribe_audio_file
from agent.audio_generation import generate_audio_output
from agent.utils import bytes_to_wav
from src.agent.file_utils import get_project_structure_as_string, concat_files_in_str
from src.agent.models import FileReflectionList, SearchFilePathsList, EnhanceTextInstruction
from src.agent.prompts import file_planner_instructions, answer_instructions, \
    get_current_date, enhance_text_instruction

load_dotenv()


# Graph state
class State(TypedDict):
    messages: Annotated[list, add_messages]
    project_path: str
    contexts: Annotated[list, operator.add]
    file_reflection: FileReflectionList
    all_file_paths: Annotated[set, lambda x, y: x.union(y)]
    audio_file: str
    enhanced_message: str
    voice_output: Optional[bool]
    language: str
    audio: str


model_name = "gemini-2.5-flash-lite-preview-06-17"

llm = ChatGoogleGenerativeAI(model=model_name)


# Schema for structured output to use in evaluation
class Feedback(BaseModel):
    grade: Literal["funny", "not funny"] = Field(
        description="Decide if the joke is funny or not.",
    )
    feedback: str = Field(
        description="If the joke is not funny, provide feedback on how to improve it.",
    )


# Augment the LLM with schema for structured output
evaluator = llm.with_structured_output(Feedback)


def enhance_node(state: State):
    """
    Enhances the user message to make it more understandable and clear.
    """


    audio_str = state.get("audio", None)
    last_message = state["messages"][-1]

    user_task = last_message.content
    if audio_str is not None:
        audio_file_path = bytes_to_wav(audio_str)

        print(f"Audio file detected. Starting transcription for: {audio_file_path}")
        user_task = transcribe_audio_file(audio_file_path)
        print(f"Transcription result: {user_task}")

    structured_llm = llm.with_structured_output(EnhanceTextInstruction)

    formatted_prompt = enhance_text_instruction.format(
        user_task=user_task
    )

    print("Enhancing user message...")
    result: EnhanceTextInstruction = structured_llm.invoke(formatted_prompt)
    enhanced_message = result.enhance_user_message
    print(f"Enhanced message: {enhanced_message}")

    return {"enhanced_message": enhanced_message, "language": result.language}


def llm_call_generator(state: State):
    """
    Transcribes audio, then uses the text to find relevant files.
    """
    enhanced_message = state["enhanced_message"]
    project_path = "/home/nnikolovskii/data/nlb_data"

    user_task = enhanced_message

    project_structure = get_project_structure_as_string(project_path)
    structured_llm = llm.with_structured_output(SearchFilePathsList)

    formatted_prompt = file_planner_instructions.format(
        user_task=user_task,
        project_structure=project_structure,
    )

    print("Invoking LLM to find relevant file paths...")
    result: SearchFilePathsList = structured_llm.invoke(formatted_prompt)
    context = concat_files_in_str(result.file_paths)
    return {"contexts": [context], "all_file_paths": set(result.file_paths)}


def finalize_answer(state: State):
    """
    This node is now a generator. It `yield`s each chunk of the response as an
    AIMessage, allowing `langgraph` to stream the output.
    """
    context = state["contexts"][-1]
    voice_output = state.get("voice_output", False) # Default to False if not present
    language = state["language"]

    if language == "mkd":
        language = "Macedonian"
    elif language == "alb":
        language = "Albanian"
    elif language == "eng":
        language = "English"

    print("--- Calling Finalize Answer Node ---")
    messages = state["messages"]
    last_ai_message = messages[-1]
    # Changed from ChatGoogleGenerativeAI to ChatOpenAI
    formatted_prompt = answer_instructions.format(
        current_date=get_current_date(),
        research_topic=state["messages"][-1].content,
        summaries=context,
        language=language
    )
    response = llm.invoke(formatted_prompt)
    print(response.text)

    return {"messages": [AIMessage(content=response.content)]}


optimizer_builder = StateGraph(State)

optimizer_builder.add_node("enhance_node", enhance_node)
optimizer_builder.add_node("llm_call_generator", llm_call_generator)
optimizer_builder.add_node("finalize_answer", finalize_answer)

optimizer_builder.add_edge(START, "enhance_node")
optimizer_builder.add_edge("enhance_node", "llm_call_generator")
optimizer_builder.add_edge("llm_call_generator", "finalize_answer")
optimizer_builder.add_edge("finalize_answer", END)


# Compile the workflow
graph = optimizer_builder.compile()  # Renamed from optimizer_workflow

# # Invoke
# state = graph.invoke(
#     {"messages": [HumanMessage("Кои услови треба да ги исполнам за да извадам инвестициски кредит?")],
#      "project_path": "/home/nnikolovskii/data/nlb_data",
#      "audio_file": "/home/nnikolovskii/PycharmProjects/langgraph-demo/src/data/karticki.ogg",
#      "voice_output": True})
