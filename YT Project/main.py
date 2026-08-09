import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info
from functions.get_file_content import schema_get_file_content
from functions.write_file import schema_write_file
from functions.run_python_file import schema_run_python_file
from call_function import call_function

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

    system_prompt = """
        You are a helpful assistant.
        When a user makes a request, make a function call plan. You can perform the following functions:
        - get_files_info: Get information about files in a directory.
        - get_file_content: Get the content of a file.
        - write_file: Overwrites an existing file or writes content to a new file if it doesn't exist.
        - run_python_file: Run a Python file and return the output.
        
        All paths provided by the user will be relative to the working directory, you do not need specify the working directory in the function call for security reasons.
    """

    if len(sys.argv) < 2:
        print("Please provide a prompt as a command line argument.")
        sys.exit(1)

    verbose = False  # Set to True to enable verbose logging
    if len(sys.argv) > 2 and sys.argv[2].lower() == "--verbose":
        verbose = True

    prompt = sys.argv[1]    
    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)])
    ]

    available_functions = types.Tool(
        function_declarations=[schema_get_files_info, schema_get_file_content, schema_write_file, schema_run_python_file],
    )

    config = types.GenerateContentConfig(
        tools = [available_functions],
        system_instruction=system_prompt
    )

    max_iterations = 20
    for iteration in range(max_iterations):
        response = client.models.generate_content(
            model="gemini-3.5-flash-lite", 
            contents=messages,
            config=config
        )    
            
        if response is None or response.usage_metadata is None:
            return

        if verbose:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}") 
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}") 

        if response.candidates:
            for candidate in response.candidates:
                if candidate is None or candidate.content is None:
                    continue

                messages.append(candidate.content)

        if response.function_calls:
            for function_call in response.function_calls:
                result = call_function(function_call, verbose)
                messages.append(result)

        else:
            print(response.text)
            return

main()