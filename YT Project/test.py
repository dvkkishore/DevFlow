from functions.get_file_content import get_file_content
from functions.get_files_info import get_files_info
from functions.write_file import write_file
from functions.run_python_file import run_python_file

def main():
    working_directory = "YT Project"  # Current directory
    print(run_python_file(working_directory, "dummy/dummy.py"))

main()