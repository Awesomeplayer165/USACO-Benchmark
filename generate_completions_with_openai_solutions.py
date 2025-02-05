import os
import json
import time
import numpy as np
from openai import OpenAI
from file_helper import FileHelper
import threading

# If you are using OpenAI's API, make sure to change `solutions.json` to `openai_solutions.json` (if you are using the paper's provided generated solutions.
# If you are using another service or model, like Anthropic Claude, make sure it conforms to {str<problem_id>: str<solution_text>}
fileHelper = FileHelper(f"{os.getcwd()}/supporting_files/", "problems.json", "test_cases/", "completions/", "solutions.json", reset=False)

client = OpenAI(
    api_key="" # Paste in here or read from an environment file
)

solutions = {}

error_prompt = """
1. AVOID SYNTAX ERRORS. These can be caused by incorrect or missing parenthesis.
For example,
`print("Hello"` and `print("Hello"]`.
2. AVOID EXTRANEOUS TEXT IN THE CODE. DO NOT PUT ADDITIONAL MESSAGES AT THE END OF THE CODE.
3. AVOID INDENTATION ERRORS. DO NOT INDENT ANYTHING 1 EXTRA TAB. KEEP INDENTATION WITH LOOPS AND IF STATEMENTS CONSISTENT.
For example,
```python
for i in range(N):
print(i)
```
THIS IS INVALID.
4. AVOID VALUE ERRORS. READ THE INPUT CORRECTLY. Follow the format of the sample input EXACTLY.
For example, do not read in 2 integers when there only exists 1 to read. THIS WILL CAUSE AN ERROR
Furthermore, this is also a value error
`int("abc")`
5. AVOID NAME ERRORS. ONLY USE MODULES THAT DO NOT REQUIRE PIP INSTALL. Do not use variables that have not been defined yet.
6. MAKE SURE TO CALL THE FUNCTION THAT YOU HAVE DEFINED IN THE GLOBAL SCOPE.
"""

# This file helps send request Batch API completions to OpenAI
# Once you get the results from OpenAI, run it through `convert_openai_batch_output.py`
# which transforms OpenAI's batch API response to the expected format for this benchmark.

# for solutions with jsonl
# with open("supporting_files/llama3-solutions.jsonl") as file:
#     for line in file:
#         jsonLine = json.loads(line)
#         key = list(jsonLine.keys())[0]
        # solutions[key] = jsonLine[key]

# for solutions with .json
with open("supporting_files/openai_solutions.json") as file:
    solutions = json.load(file)

# human judge solutions
# solutions = fileHelper.solutions_contents

# def create_request(problem: str, openai_solution: str, language: str = "python"):
#     return (f"""    do NOT include any comments or explanations in your response. Read the input from the file input.in and write the output to the file output.out. DO NOT INTERACT WITH STDIN/STDOUT, DO NOT USE `INPUT()` OR `PRINT()`. only use file I/O. Only use 'input.in' and 'output.out' file ouptputs, regardless of other filenames the problem statement gives. Use {language}:
#             \n\nProblem statement:\n{problem}
#             \n\n\Step by Step solution:\n {openai_solution}""")

def create_request(problem: str, judge_solution: str, language: str = "python"):
    return (f"""    do NOT include any comments or explanations in your response. Read the input from the file input.in and write the output to the file output.out. DO NOT INTERACT WITH STDIN/STDOUT, DO NOT USE `INPUT()` OR `PRINT()`. only use file I/O. Only use 'input.in' and 'output.out' file ouptputs, regardless of other filenames the problem statement gives. Use {language}:
            {error_prompt}
            \n\nProblem statement:\n{problem}
            \n\n\Step by Step instructions:\n {judge_solution}""")

def create_request(problem: str, language: str = "python"):
    return (f"""    do NOT include any comments or explanations in your response. Read the input from the file input.in and write the output to the file output.out. DO NOT INTERACT WITH STDIN/STDOUT, DO NOT USE `INPUT()` OR `PRINT()`. only use file I/O. Only use 'input.in' and 'output.out' file ouptputs, regardless of other filenames the problem statement gives. Use {language}:
        \n\nProblem statement:\n{problem}""")

def generate_problem_id_batch(problem_id: str, problem: str, openai_solution: str) -> dict:
    return {
        "custom_id": f"{problem_id}",
        "method": "POST",
        "url": "/v1/chat/completions",
        "body": {
            "model": json.load(open("config.json"))["model"],
            "messages": [
                {"role": "system", "content": "You are a helpful assistant in programming"},
                {
                    "role": "user",
                    "content": create_request(problem, openai_solution)
                }
            ]
        },
    }

def submit_batch(problems: list[str], n: int):
    openai_batch_file = f"openai_completion_batch_{n}.jsonl"

    if os.path.exists(openai_batch_file):
        os.remove(openai_batch_file)

    for problem_id in problems:
        with open(openai_batch_file, "a") as file:
            file.write(json.dumps(generate_problem_id_batch(problem_id, problems[problem_id], solutions[problem_id])) + "\n")
    
    batch_input_file = client.files.create(
        file=open(openai_batch_file, "rb"),
        purpose="batch"
    )

    batch_input_file_id = batch_input_file.id

    client.batches.create(
        input_file_id=batch_input_file_id,
        endpoint="/v1/chat/completions",
        completion_window="24h",
        metadata={
            "description": "OpenAI Generations"
        }
    )

problems = fileHelper.file_contents

print(len(problems))
print(len(solutions))

def prepare_batch(index, splitted_problems):
    print("submit time")
    submit_batch({problem_id: problems[problem_id] for problem_id in splitted_problems}, index)

# A makeshift scheduling system for BatchAPI since OpenAI does not provide one themselves without paying more money

n = 18

split_problems = np.array_split(list(problems.keys()), n)

def wait_or_skip_event():
    input("Press Enter to continue...")

for index, splitted_problems in enumerate(split_problems):
    print(f"Submitting batch {index}")

    input_thread = threading.Thread(target=wait_or_skip_event)
    input_thread.start()
    input_thread.join(timeout=400)

    prepare_batch(index, splitted_problems)

    if input_thread.is_alive():
        input_thread.join()
    

