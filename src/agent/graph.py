from __future__ import annotations

import operator
from typing import TypedDict, Literal, Annotated, Optional

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph, add_messages
from pydantic import BaseModel, Field

from agent.gemini_transcript import transcribe_audio_file
from agent.audio_generation import generate_audio_output
from agent.img_input import multimodal_generation
from agent.utils import bytes_to_wav, bytes_to_image
from src.agent.file_utils import get_project_structure_as_string, concat_files_in_str
from src.agent.models import FileReflectionList, SearchFilePathsList, EnhanceTextInstruction, Route
from src.agent.prompts import file_planner_instructions, answer_instructions, \
    get_current_date, enhance_text_instruction, about_me_instructions, not_capable_instruction, routing_instruction, \
    image_text_instruction, file_reflection_instructions

load_dotenv()


# Graph state
class State(TypedDict):
    messages: Annotated[list, add_messages]
    project_path: str
    context: str
    file_reflection: FileReflectionList
    all_file_paths: Annotated[set, lambda x, y: x.union(y)]
    audio_file: str
    enhanced_message: str
    voice_output: Optional[bool]
    language: str
    audio: str
    user_task: str
    decision: str
    image: str
    image_file_path: str


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


def define_user_task(state: State):
    audio_str = state.get("audio", None)
    image_str = state.get("image", None)
    last_message = state["messages"][-1]

    user_task = last_message.content
    if audio_str is not None:
        audio_file_path = bytes_to_wav(audio_str)

        print(f"Audio file detected. Starting transcription for: {audio_file_path}")
        user_task = transcribe_audio_file(audio_file_path)
        print(f"Transcription result: {user_task}")

    if image_str is not None:
        image_file_path = bytes_to_image(image_str)
    else:
        image_file_path = None
    return {"user_task": user_task, "image_file_path": image_file_path}


def enhance_node(state: State):
    """
    Enhances the user message to make it more understandable and clear.
    """
    user_task = state["user_task"]

    structured_llm = llm.with_structured_output(EnhanceTextInstruction)

    formatted_prompt = enhance_text_instruction.format(
        user_task=user_task
    )

    print("Enhancing user message...")
    result: EnhanceTextInstruction = structured_llm.invoke(formatted_prompt)
    enhanced_message = result.enhance_user_message
    print(f"Enhanced message: {enhanced_message}")

    audio_str = state.get("audio", None)
    if audio_str:
        return {"enhanced_message": enhanced_message, "language": "mkd"}

    return {"enhanced_message": enhanced_message, "language": result.language}


def llm_call_router(state: State):
    """Route the input to the appropriate node"""

    router = llm.with_structured_output(Route)
    user_task = state["enhanced_message"]

    formatted_prompt = routing_instruction.format(
        user_task=user_task,
    )

    decision = router.invoke(formatted_prompt)

    return {"decision": decision.step}


def route_decision(state: State):
    image_file_path = state["image_file_path"]
    if image_file_path is not None:
        return "image_text_input"

    if state["decision"] == "about_me":
        return "about_me"
    elif state["decision"] == "info":
        return "llm_file_explore"
    elif state["decision"] == "not_suitable":
        return "not_suitable"


def llm_call_evaluator(state: State):
    """LLM evaluates the files in context and suggests additions/removals"""
    last_message = state["messages"][-1]
    project_path = state["project_path"]
    context = state["context"]
    all_file_paths = state["all_file_paths"]

    project_structure = get_project_structure_as_string(project_path)
    count = 0

    while True:
        structured_llm = llm.with_structured_output(FileReflectionList)
        formatted_prompt = file_reflection_instructions.format(
            user_task=last_message.content,
            project_structure=project_structure,
            context=context
        )
        count += 1
        if count > 3:
            return {"context", context}

        result: FileReflectionList = structured_llm.invoke(formatted_prompt)
        print(result)

        if result.additional_file_paths is None:
            break
        new_files = [file_path for file_path in result.additional_file_paths if file_path not in all_file_paths]

        if len(new_files) == 0:
            break
        else:
            all_file_paths.update(set(new_files))
            context = concat_files_in_str(list(all_file_paths))

    print("*************************************")
    print(context)
    return {"file_reflection": result}


def llm_file_explore(state: State):
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
    return {"context": context, "all_file_paths": set(result.file_paths), "project_path": project_path}


def finalize_answer(state: State):
    """
    This node is now a generator. It `yield`s each chunk of the response as an
    AIMessage, allowing `langgraph` to stream the output.
    """
    context = state["context"]
    user_task = state["enhanced_message"]
    voice_output = state.get("voice_output", False)  # Default to False if not present
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
        research_topic=user_task,
        summaries=context,
        language=language
    )
    response = llm.invoke(formatted_prompt)
    print(response.text)

    return {"messages": [AIMessage(content=response.content)]}


def about_me(state: State):
    user_task = state["enhanced_message"]

    language = state["language"]

    if language == "mkd":
        language = "Macedonian"
    elif language == "alb":
        language = "Albanian"
    elif language == "eng":
        language = "English"

    formatted_prompt = about_me_instructions.format(
        user_task=user_task,
        language=language
    )
    response = llm.invoke(formatted_prompt)
    print(response.text)

    return {"messages": [AIMessage(content=response.content)]}


def not_suitable(state: State):
    user_task = state["enhanced_message"]

    language = state["language"]

    if language == "mkd":
        language = "Macedonian"
    elif language == "alb":
        language = "Albanian"
    elif language == "eng":
        language = "English"
    formatted_prompt = not_capable_instruction.format(
        user_task=user_task,
        language=language
    )
    response = llm.invoke(formatted_prompt)
    print(response.text)

    return {"messages": [AIMessage(content=response.content)]}


def image_text_input(state: State):
    user_task = state["enhanced_message"]
    image_file_path = state["image_file_path"]

    language = state["language"]

    if language == "mkd":
        language = "Macedonian"
    elif language == "alb":
        language = "Albanian"
    elif language == "eng":
        language = "English"
    formatted_prompt = image_text_instruction.format(
        user_task=user_task,
        language=language
    )
    response = multimodal_generation(image_file_path, formatted_prompt)
    print(response.text)

    return {"messages": [AIMessage(content=response.text)]}


optimizer_builder = StateGraph(State)

optimizer_builder.add_node("enhance_node", enhance_node)
optimizer_builder.add_node("llm_file_explore", llm_file_explore)
optimizer_builder.add_node("finalize_answer", finalize_answer)
optimizer_builder.add_node("define_user_task", define_user_task)
optimizer_builder.add_node("llm_call_router", llm_call_router)
optimizer_builder.add_node("about_me", about_me)
optimizer_builder.add_node("not_suitable", not_suitable)
optimizer_builder.add_node("image_text_input", image_text_input)
optimizer_builder.add_node("llm_call_evaluator", llm_call_evaluator)

optimizer_builder.add_edge(START, "define_user_task")
optimizer_builder.add_edge("define_user_task", "enhance_node")
optimizer_builder.add_conditional_edges(
    "llm_call_router",
    route_decision,
    {
        "about_me": "about_me",
        "not_suitable": "not_suitable",
        "llm_file_explore": "llm_file_explore",
        "image_text_input": "image_text_input",

    },
)
optimizer_builder.add_edge("enhance_node", "llm_call_router")
optimizer_builder.add_edge("llm_file_explore", "llm_call_evaluator")
optimizer_builder.add_edge("llm_call_evaluator", "finalize_answer")

optimizer_builder.add_edge("finalize_answer", END)
optimizer_builder.add_edge("about_me", END)
optimizer_builder.add_edge("not_suitable", END)
optimizer_builder.add_edge("image_text_input", END)

graph = optimizer_builder.compile()  # Renamed from optimizer_workflow

# # Invoke
# state = graph.invoke(
#     {"messages": [HumanMessage("Кои услови треба да ги исполнам за да извадам инвестициски кредит?")],
#      "project_path": "/home/nnikolovskii/data/nlb_data",
#      "audio_file": "/home/nnikolovskii/PycharmProjects/langgraph-demo/src/data/karticki.ogg",
#      "voice_output": True})
