import os
import subprocess
import sys
from google.genai import types

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

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Run a Python file and return its output.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(type=types.Type.STRING, description="The path to the Python file to execute."),
            "args": types.Schema(type=types.Type.ARRAY, items=types.Schema(type=types.Type.STRING), description="Optional arguments to pass to the Python file.")
        },
    )
)