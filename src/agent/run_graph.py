from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from agent.core.configs import graph

project_path = "/home/nnikolovskii/dev/personal-app/frontend"


user_task = """Wherever there is api call make i want it to be from .env."""


config = RunnableConfig(recursion_limit=250)

state = graph.invoke(
    {
        "user_task": user_task,
        "project_path": project_path,
        "messages": HumanMessage(content=user_task),
    }
    ,
    config=config
)
