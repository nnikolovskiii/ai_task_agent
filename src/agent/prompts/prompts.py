from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


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

make_plan_instruction = """Task: {user_task}

Context:
{context}
"""