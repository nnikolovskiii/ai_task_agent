from __future__ import annotations

from typing import Annotated, TypedDict

from langgraph.graph import add_messages


# Graph state
class State(TypedDict):
    messages: Annotated[list, add_messages]
    project_path: str
    context: str
    user_task: str
    all_file_paths: Annotated[set, lambda x, y: x.union(y)]
    project_structure: str
