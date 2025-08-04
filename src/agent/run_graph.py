from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from agent.core.configs import graph

project_path = "/home/nnikolovskii/notes"


user_task = """Do not write code. For AI tasks project tasks: 

- the voice thing isnt integrated with the app. it say completed but it is not.
- i need a way to track how much it costs to run every task and logs on how long the tasks is and so on so on.
"""


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
