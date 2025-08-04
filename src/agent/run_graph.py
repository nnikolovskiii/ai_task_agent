from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig

from agent.core.configs import graph

project_path = "/home/nnikolovskii/notes"


user_task = """### Work Update: Chat Interface Improvements & Next Steps  

#### **Completed Work**  
- Redesigned the chat interface to enhance its visual appeal and usability.  
- The new design is a significant improvement over the previous version, though minor refinements may still be needed.  

#### **Next Steps**  
1. **Message Management for the Model**  
   - Currently, all messages are sent to the model, but only some are necessary.  
   - Need to implement a system to filter or prioritize relevant messages.  
   - Possible approaches:  
     - Iterative processing  
     - Modular yet simple architecture (balancing flexibility and ease of use)  

2. **Expanding Data Source Connections**  
   - The system currently connects to a single source but should integrate with multiple sources.  
   - Key considerations:  
     - How monitoring gaps align with research topics  
     - Best practices for multi-source integration  
   - Next action: Discuss with my manager to determine the optimal implementation strategy.  

---  """


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
