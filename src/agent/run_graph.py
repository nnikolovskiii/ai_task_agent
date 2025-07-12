from langchain_core.messages import HumanMessage

from agent import graph
from agent.tools.file_utils import read_file

# Read the content of example.md and set it as user_task
user_task = """langgraph-api-1       | 2025-07-12T11:02:48.793690Z [error    ] Traceback (most recent call last):
langgraph-api-1       |   File "/usr/lib/python3.11/site-packages/starlette/routing.py", line 694, in lifespan
langgraph-api-1       |     async with self.lifespan_context(app) as maybe_state:
langgraph-api-1       |   File "/usr/lib/python3.11/contextlib.py", line 210, in __aenter__
langgraph-api-1       |     return await anext(self.gen)
langgraph-api-1       |            ^^^^^^^^^^^^^^^^^^^^^
langgraph-api-1       |   File "/usr/lib/python3.11/site-packages/langgraph_runtime_postgres/lifespan.py", line 84, in lifespan
langgraph-api-1       |     await graph.collect_graphs_from_env(True)
langgraph-api-1       |   File "/api/langgraph_api/graph.py", line 386, in collect_graphs_from_env
langgraph-api-1       |   File "/api/langgraph_api/utils/config.py", line 135, in run_in_executor
langgraph-api-1       |   File "/usr/lib/python3.11/concurrent/futures/thread.py", line 58, in run
langgraph-api-1       |     result = self.fn(*self.args, **self.kwargs)
langgraph-api-1       |              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
langgraph-api-1       |   File "/api/langgraph_api/utils/config.py", line 126, in wrapper
langgraph-api-1       |   File "/api/langgraph_api/graph.py", line 431, in _graph_from_spec
langgraph-api-1       |   File "<frozen importlib._bootstrap_external>", line 940, in exec_module
langgraph-api-1       |   File "<frozen importlib._bootstrap>", line 241, in _call_with_frames_removed
langgraph-api-1       |   File "/deps/agent/src/agent/core/graph.py", line 9, in <module>
langgraph-api-1       |     from google import genai
langgraph-api-1       | ModuleNotFoundError: No module named 'google'
langgraph-api-1       | Could not import python module for graph:
langgraph-api-1       | GraphSpec(id='agent', path='/deps/agent/src/agent/core/graph.py', module=None, variable='graph', config={}, description=None)
langgraph-api-1       |  [uvicorn.error] api_revision=b2a367f api_variant=licensed langgraph_api_version=0.2.86 thread_name=MainThread
langgraph-api-1       | 2025-07-12T11:02:48.793977Z [error    ] Application startup failed. Exiting. [uvicorn.error] api_revision=b2a367f api_variant=licensed langgraph_api_version=0.2.86 thread_name=MainThread
langgraph-api-1 exited with code 3
"""

state = graph.invoke(
    {"user_task": user_task, "project_path": "/home/nnikolovskii/sandbox",
     "messages": HumanMessage(content=user_task)
     })
