from datetime import datetime


# Get current date in a readable format
def get_current_date():
    return datetime.now().strftime("%B %d, %Y")


file_planner_instructions = """Your goal is to determine which files need to be searched in order to complete the user's task.

Instructions:
- List all of the files that you think would be relevant for the user's task.
- Write the filepaths the same exact way as in the project structure.

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

Format: 
- Format your response as a JSON object with ALL of these exact keys:
   - "additional_file_paths": A list of file paths that should be added to the context.
   - "remove_file_paths": A list of file paths that should be removed from the context.

User task:
{user_task}

Project structure: 
{project_structure}

Fetched files:
{context}
"""

answer_instructions = """Generate a high-quality answer to the user's question based on the provided summaries.

Important:
You must answer only in {language}.

Instructions:
- The current date is {current_date}.
- You are the final step of a multi-step research process, don't mention that you are the final step. 
- You have access to all the information gathered from the previous steps.
- You have access to the user's question.
- Generate a high-quality answer to the user's question based on the provided summaries and the user's question.
- you MUST include all the citations from the summaries in the answer correctly.

User Context:
- {research_topic}

Summaries:
{summaries}"""

enhance_text_instruction = """Given the user task/question make it more understandable and more clear. Also, determine one of the languages the input is in: macedonian, albanian and english.

Format: 
- Format your response as a JSON object with ALL of these exact keys:
   - "enhance_user_message": User message that is made clearer.
   - "language": mkd, eng or alb.

User task:
{user_task}
"""
