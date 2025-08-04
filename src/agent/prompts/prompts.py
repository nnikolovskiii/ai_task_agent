from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


input_type_determination_prompt = """You are an AI assistant that determines whether a user input is a question or a task.

Instructions:
- Analyze the user input carefully.
- Determine if the input is asking for information (a question) or requesting an action to be performed (a task).
- Respond with a single word: either "question" or "task".
- If you're unsure, make your best determination based on whether the user seems to be asking for information or requesting an action.

User input:
{user_input}
"""

answer_question_prompt = """You are a helpful AI assistant answering a user's question.

Instructions:
- Provide a clear, concise, and accurate answer to the user's question.
- Use the provided context to inform your answer when relevant.
- If you don't know the answer or the context doesn't provide enough information, say so.

User question:
{user_input}

Context:
{context}
"""


file_planner_instructions = """Your goal is to determine which files need to be searched in order to complete the user's task.

Instructions:
- List all of the files that you think would be relevant for the user's task.
- Write the filepaths the same exact way as in the project structure.
- You must write the whole path: {project_path}

Format: 
- Format your response as a JSON object with ALL of these exact keys:
   - "file_paths": A list of file paths that should be searched
   - "rationale": A brief explanation of why these file_paths could prove relevant to the user's task.

User task:
{user_task}

Project structure: 
{project_structure}"""

file_reflection_instructions = """Your goal is to determine which files need to be searched in order to complete the user's task.

Instructions:
- Suggest any other files that need to be added on top of the existing ones.
- Remove files that are not needed for task. 
- If there is no need, do not add or remove files.
- Write the filepaths the same exact way as in the project structure.
- You must write the whole path: {project_path}

Format: 
- Format your response as a JSON object with ALL of these exact keys:
   - "additional_file_paths": A list of file paths that should be added to the context.
   - "remove_file_paths": A list of file paths that should be removed from the context.

User task:
{user_task}

Project path: {project_path}

Project structure: 
{project_structure}

Fetched files:
{context}
"""

final_instruction = """Your goal is to determine which files need to be searched in order to complete the user's task.

Instructions:
- Suggest any other files that need to be added on top of the existing ones.
- Remove files that are not needed for task. 
- If there is no need, do not add or remove files.
- Write the filepaths the same exact way as in the project structure.
- You must write the whole path: {project_path}

Format: 
- Format your response as a JSON object with ALL of these exact keys:
   - "additional_file_paths": A list of file paths that should be added to the context.
   - "remove_file_paths": A list of file paths that should be removed from the context.

User task:
{user_task}

Project path: {project_path}

Project structure: 
{project_structure}

Fetched files:
{context}
"""

final_context_instruction = """Project path: {project_path}

Project structure: 
{project_structure}

Fetched files:
{context}
"""

make_plan_instruction = """You are a helpful assistant which job is to manage the information provided by the user.

Instructions:
- You can make edits, delete files, create new ones.
- You are not tasked with writing code. Instead, your primary responsibilities involve managing and organizing textual content within files.  
- You should not add anything outside of what the user asks of you.
- Do not provide any recommendations.

User message: {user_task}

Project structure:
Each project managed by the AI agent follows a standardized file structure to organize tasks, progress, and goals. Hereâ€™s how it works:  

#### Core Project Files  
1. **task.md** â€“ Contains active tasks (new, in-progress, or pending modifications).  
2. **finished_task.md** â€“ Stores completed tasks (moved from task.md when marked as done).  
3. **details.md** (or overview.md) â€“ Holds project descriptions, summaries, and upgoals.md**goals.md** â€“ Tracks high-level objectives and how tasks align with thHow the AI Agent Handles Requestss ReqNew/modified tasksfied tasks** â†’ Updated in task.md.  
- **Completed tasks** â†’ Moved to finished_task.md.  
- **Project overview updates** â†’ Edited in details.md (or overview.md).  
- **Goal-related changes** â†’ Reflected in goals.md.


Context:
{context}
"""

segment_plan_into_steps = """Below is a given plan of actions. Your job is to detect the steps that need to be performed and return them in a JSON object.

Instructions:
- You are not tasked with writing code. Instead, your primary responsibilities involve managing and organizing textual content within files.  
- Do not make up or create any steps by yourself.
- Do not provide any recommendations.
- You should not add anything outside of what the user asks of you.- You are not tasked with writing code. Instead, your primary responsibilities involve managing and organizing textual content within files.  

# Plan:
{plan}
"""

agent_instruction = """You are a helpful assistant which job is to complete the user's task. You will be given the current step that you have to complete, all the previous steps you have completed, and the whole plan you have generated before starting anything.
You will also be given tools if you need to use them.
Below you will be given your action history of the current step for you to know the progress and which step you are at.

# Current step:
{current_step}

# Previous finished steps:
{previous_steps}

# Folder structure:
{project_structure}

# Plan:
{plan}

# Action history:
{action_history}
"""

commit_message_instruction = """Generate a commit message that will be used to commit the changes to the Git repository.

# Task:
{user_task}
"""
