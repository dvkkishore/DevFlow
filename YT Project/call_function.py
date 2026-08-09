from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python_file import run_python_file
from google.genai import types

working_directory = "."  # Current directory

def call_function(function_call, verbose=False):
    """
    Calls the specified function based on the function_call object.

    Args:
        function_call (types.FunctionCall): The function call object containing the function name and arguments.
        verbose (bool): If True, prints verbose logs.

    Returns:
        The result of the called function.
    """
    if verbose:
        print(f"Function call: {function_call.name} with arguments: {function_call.args}")
    else:
        print(f"Function call: {function_call.name}")

    result = ""
    if function_call.name == "get_files_info":
        result = get_files_info(working_directory, **function_call.args)
    elif function_call.name == "get_file_content":
        result = get_file_content(working_directory, **function_call.args)
    elif function_call.name == "write_file":
        result = write_file(working_directory, **function_call.args)
    elif function_call.name == "run_python_file":
        result = run_python_file(working_directory, **function_call.args)

    return types.Content(
    role="user",
    parts=[types.Part.from_function_response(
        name=function_call.name,
        response={"error": f"Unknown function: {function_call.name} failed with error: {result}"} if result is None else {"result": f"Result: {result}"})
        ]
    )