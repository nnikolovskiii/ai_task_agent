import os
from pathlib import Path
from typing import List

DEFAULT_IGNORE_PATTERNS = {'.git', '.venv', ".idea", ".pytest_cache",
                           '.git', '__pycache__', "__init__.py", ".angular",
                           ".github", ".vscode", "dist", "node_modules",
                           ".chainlit", ".files", ".junie", ".langgraph_api", "data"}


def get_project_structure_as_string(folder_path, ignore_patterns=None):
    """
    Generates a tree-like string representation of the project structure for the given folder path,
    excluding files and folders that match the ignore patterns by their basename.

    How to use `ignore_patterns`:
    - To ignore ".venv" IN ADDITION to default ignores ('.git', '__pycache__', '.DS_Store'):
      pass ignore_patterns=ProjectHelper.DEFAULT_IGNORE_PATTERNS.union({".venv"})
    - To ignore ONLY ".venv" and not other defaults:
      pass ignore_patterns={".venv"}
    - To ignore NOTHING (show all, overriding defaults):
      pass ignore_patterns=set()
    - If `ignore_patterns` is None (default), ProjectHelper.DEFAULT_IGNORE_PATTERNS is used.

    Args:
        folder_path (str): The path to the root folder of the project.
        ignore_patterns (set, optional): A set of file or folder basenames to ignore.
                                        Defaults to ProjectHelper.DEFAULT_IGNORE_PATTERNS.

    Returns:
        str: A formatted tree-like string representation of the project structure.
             Returns an error message if folder_path does not exist or is not a directory.
    """

    final_ignore_patterns = DEFAULT_IGNORE_PATTERNS if ignore_patterns is None else ignore_patterns

    if not os.path.exists(folder_path):
        return f"Error: The path '{folder_path}' does not exist."
    if not os.path.isdir(folder_path):
        return f"Error: The path '{folder_path}' is not a directory."

    project_root_name = folder_path

    output_lines = [f"└── {project_root_name}/"]

    structure_map = {}

    for current_root, dir_names, file_names in os.walk(folder_path, topdown=True):

        dir_names[:] = [d for d in dir_names if d not in final_ignore_patterns]

        children_of_current_root = []

        for name in sorted(dir_names):
            children_of_current_root.append((name, True))

        for name in sorted(file_names):
            if name not in final_ignore_patterns:
                children_of_current_root.append((name, False))

        if children_of_current_root:
            structure_map[current_root] = children_of_current_root

    def generate_tree_lines(dir_path_to_scan, current_prefix=""):
        lines = []

        children = structure_map.get(dir_path_to_scan, [])

        for index, (name, is_directory) in enumerate(children):
            is_last_item = (index == len(children) - 1)

            connector = "└── " if is_last_item else "├── "

            prefix_for_next_level = current_prefix + ("    " if is_last_item else "│   ")

            display_name = f"{name}/" if is_directory else name
            lines.append(f"{current_prefix}{connector}{display_name}")

            if is_directory:
                full_child_dir_path = os.path.join(dir_path_to_scan, name)
                lines.extend(generate_tree_lines(full_child_dir_path, prefix_for_next_level))
        return lines

    tree_item_lines = generate_tree_lines(folder_path, "")
    output_lines.extend(tree_item_lines)

    return "\n".join(output_lines)


from pathlib import Path
from typing import List
from pypdf import PdfReader # New import for PDF handling

def read_file(file_path: str) -> str | None:
    """
    Read contents of a file.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: File contents or None if error occurs.
    """
    path = Path(file_path)

    if not path.exists():
        print(f"File does not exist: {path}")
        return None

    if not path.is_file():
        print(f"Path is not a regular file: {path}")
        return None

    try:
        with open(path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading text file {path}: {str(e)}")
        return None

def read_pdf(file_path: str) -> str | None:
    """
    Read contents of a PDF file.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        str: Extracted text from the PDF or None if error occurs.
    """
    path = Path(file_path)

    if not path.exists():
        print(f"File does not exist: {path}")
        return None

    if not path.is_file():
        print(f"Path is not a regular file: {path}")
        return None

    try:
        reader = PdfReader(path)
        text_content = ""
        for page in reader.pages:
            # Extract text from each page, add a newline for separation
            extracted_text = page.extract_text()
            if extracted_text: # Only add if text was actually extracted
                text_content += extracted_text + "\n"
        return text_content.strip() # Remove trailing newline if any
    except Exception as e:
        print(f"Error reading PDF file {path}: {str(e)}")
        return None

def concat_files_in_str(file_paths: List[str]) -> str:
    """
    Concatenates the contents of specified files (text or PDF) into a single string,
    with titles for each file.

    Args:
        file_paths (List[str]): A list of paths to the files.

    Returns:
        str: A concatenated string of file contents.
    """
    file_title_format = """================================================
FILE: {file_path}
================================================"""
    result = ""

    for file_path in file_paths:
        path_obj = Path(file_path)
        content = None

        if not path_obj.exists():
            print(f"Skipping non-existent path: {file_path}")
            continue

        if path_obj.is_dir():
            print(f"Skipping directory: {file_path}")
            continue

        if path_obj.suffix.lower() == '.pdf':
            content = read_pdf(file_path)
        elif path_obj.is_file(): # Covers .txt, .py, .md, etc.
            content = read_file(file_path)
        else:
            print(f"Skipping unsupported file type or special file: {file_path}")
            continue

        if content is not None:
            file_title = file_title_format.format(
                file_path=file_path
            )
            result += f"{file_title}\n{content}\n\n"

    return result