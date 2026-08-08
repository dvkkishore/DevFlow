import os
import subprocess
import sys

def run_python_file(working_directory, file_path, args=[]):
    abs_working_directory = os.path.abspath(working_directory)
    abs_file_path = os.path.abspath(os.path.join(working_directory, file_path))
    
    if not os.path.isfile(abs_file_path):
        return f"Error: The file '{file_path}' is not a file."
    
    if not abs_file_path.startswith(abs_working_directory):
        return f"Error: The file '{file_path}' is not within the working directory"

    if not file_path.endswith(".py"):
        return f"Error: The file '{file_path}' is not a Python file."

    try:
        # Execute the Python file and capture its output
        cmd = [sys.executable, abs_file_path]
        cmd.extend(args)
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        return result.stdout
    except Exception as e:
        return (
            f"Error executing file '{file_path}':\n"
            f"STDOUT:\n{e.stdout}\n"
            f"STDERR:\n{e.stderr}"
        )