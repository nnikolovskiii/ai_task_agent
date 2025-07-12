from __future__ import annotations

import os
from typing import TypedDict, Literal, Annotated

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.constants import START, END
from langgraph.graph import StateGraph, add_messages
from pydantic import BaseModel, Field

from .agent import tool_node, llm_call, should_continue
from .state import State
from ..prompts.prompts import final_context_instruction, make_plan_instruction
from ..tools.llm_tools import llm_with_tools, reasoner
from ..tools.file_utils import get_project_structure_as_string, concat_files_in_str
from ..models.models import FileReflectionList, SearchFilePathsList
from ..prompts.prompts import file_planner_instructions, file_reflection_instructions

load_dotenv()


# Schema for structured output to use in evaluation
class Feedback(BaseModel):
    grade: Literal["funny", "not funny"] = Field(
        description="Decide if the joke is funny or not.",
    )
    feedback: str = Field(
        description="If the joke is not funny, provide feedback on how to improve it.",
    )


def llm_file_explore(state: State):
    """
    Transcribes audio, then uses the text to find relevant files.
    """
    user_task = state["user_task"]
    project_path = state["project_path"]

    project_structure = get_project_structure_as_string(project_path)
    structured_llm = llm_with_tools.with_structured_output(SearchFilePathsList)

    formatted_prompt = file_planner_instructions.format(
        user_task=user_task,
        project_structure=project_structure,
        project_path=project_path,
    )

    print("Invoking LLM to find relevant file paths...")
    result: SearchFilePathsList = structured_llm.invoke(formatted_prompt)
    context = concat_files_in_str(result.file_paths)
    return {"context": context, "all_file_paths": set(result.file_paths), "project_path": project_path,
            "project_structure": project_structure}


def llm_call_evaluator(state: State):
    """LLM evaluates the files in context and suggests additions/removals"""
    user_task = state["user_task"]
    project_path = state["project_path"]
    context = state["context"]
    all_file_paths = state["all_file_paths"]

    project_structure = get_project_structure_as_string(project_path)
    count = 0

    while True:
        structured_llm = reasoner.with_structured_output(FileReflectionList)
        formatted_prompt = file_reflection_instructions.format(
            user_task=state["user_task"],
            project_structure=project_structure,
            context=context,
            project_path=project_path,

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
    print(all_file_paths)
    return {"file_reflection": result, "context": context}


def build_context(state: State):
    """LLM evaluates the files in context and suggests additions/removals"""
    user_task = state["user_task"]
    project_structure = state["project_structure"]
    context = state["context"]
    project_path = state["project_path"]

    final_context = final_context_instruction.format(
        context=context,
        project_structure=project_structure,
        project_path=project_path,
    )

    output_path = os.path.join(os.getcwd(), 'context.txt')
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(final_context)
    return {"context": final_context}


def make_plan(state: State):
    """Plan the changes"""
    user_task = state["user_task"]
    project_structure = state["project_structure"]
    context = state["context"]

    instruction = make_plan_instruction.format(
        user_task=user_task,
        context=context,
    )

    result = reasoner.invoke(instruction)
    output_path = os.path.join(os.getcwd(), 'example.md')
    with open(output_path, 'w', encoding='utf-8') as output_file:
        output_file.write(result.content)

    return {"messages": [HumanMessage(content=result.content)]}

optimizer_builder = StateGraph(State)

optimizer_builder.add_node("llm_file_explore", llm_file_explore)
optimizer_builder.add_node("llm_call_evaluator", llm_call_evaluator)
optimizer_builder.add_node("build_context", build_context)
optimizer_builder.add_node("make_plan", make_plan)

optimizer_builder.add_edge(START, "llm_file_explore")
optimizer_builder.add_edge("llm_file_explore", "llm_call_evaluator")
optimizer_builder.add_edge("llm_call_evaluator", "build_context")
optimizer_builder.add_edge("build_context", END)

# optimizer_builder.add_edge("build_context", "make_plan")
# optimizer_builder.add_edge(START, "llm_call")
#
# optimizer_builder.add_node("llm_call", llm_call)
# optimizer_builder.add_node("environment", tool_node)
#
# # Add edges to connect nodes
# optimizer_builder.add_conditional_edges(
#     "llm_call",
#     should_continue,
#     {
#         # Name returned by should_continue : Name of next node to visit
#         "Action": "environment",
#         END: END,
#     },
# )
# optimizer_builder.add_edge("environment", "llm_call")
#

graph = optimizer_builder.compile()
