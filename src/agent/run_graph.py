from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from agent.core.configs import graph

project_path = ""


user_task = """Get all the chat components implementation, with the hooks and types. Get all the ui compontents as well."""



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
