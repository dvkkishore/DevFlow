import os
from config import MAX_CHARACTERS

def get_file_content(working_directory, file_path):
    abs_working_directory = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    if not os.path.isfile(abs_file_path):
        return f"Error: The file '{file_path}' is not a file."
    
    if not abs_file_path.startswith(abs_working_directory):
        return f"Error: The file '{file_path}' is not within the working directory"

    file_content = ""
    try:
        with open(abs_file_path, "r") as f:
            file_content = f.read(MAX_CHARACTERS)
            if len(file_content) == MAX_CHARACTERS:
                file_content += "\n\n[Content truncated due to size limit.]"
    except Exception as e:
        return f"Error reading file '{file_path}': {e}"

    return file_content