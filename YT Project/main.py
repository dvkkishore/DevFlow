import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info

def main():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")

    client = genai.Client(api_key=api_key)

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

    response = client.models.generate_content(
        model="gemini-3.6-flash", 
        contents=messages,
    )    

    if response is None or response.usage_metadata is None:
        return

    print(response.text)

    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}") 
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}") 

main()