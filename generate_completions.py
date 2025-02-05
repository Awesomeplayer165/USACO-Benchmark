import json
import os
import ollama
from file_helper import FileHelper, Hints
import time
import shutil

fileHelper = FileHelper(f"{os.getcwd()}/supporting_files/", "problems.json", "test_cases/", "completions/", "solutions.json", reset=False)
problems = fileHelper.file_contents

class CompletionInfo:
    problem_id: int
    code: str
    time_to_generate: float

    def __init__(self, problem_id: int, code: str, time_to_generate: float):
        self.problem_id = problem_id
        self.code = code
        self.time_to_generate = time_to_generate

def construct_completion_text(problem: str, language: str) -> str:
    # look for input format and ouptut format and force it to I/O to specific dummy files we know
    # so we can manipulate the inputs and read the outputs
    
    firstIndex = problem.find("INPUT FORMAT")
    secondIndex = problem[firstIndex:].find(":") + firstIndex
    problem = problem[:firstIndex] + "INPUT FORMAT (file input.in)" + problem[secondIndex:]

    firstIndex = problem.find("OUTPUT FORMAT")
    secondIndex = problem[firstIndex:].find(":") + firstIndex
    problem = problem[:firstIndex] + "OUTPUT FORMAT (file output.out)" + problem[secondIndex:]

    return (f'''
    # problem.py
    """
    {problem}
    do NOT include any comments or explanations in your response. Read the input from the file input.in and write the output to the file output.out. DO NOT INTERACT WITH STDIN/STDOUT, DO NOT USE `INPUT()` OR `PRINT()`. only use file I/O. Use {language}:
    """
    ''')

def get_completion(problem_id: int, language: str) -> CompletionInfo:
    problem = problems[problem_id]

    if fileHelper.config["hints"] == Hints.openai_error_prompt:
        problem += "Here is a english-solution to the problem that might help you understand the problem better:\n"
        problem += fileHelper.solutions_contents[problem_id]

    if fileHelper.config["hints"] == Hints.true:
        problem += "Here is a english-solution to the problem that might help you understand the problem better:\n"
        problem += fileHelper.solutions_contents[problem_id]
    
    if fileHelper.config["hints"] == Hints.gpt4o:
        print("OpenAI models should be run through the dedicated `generate_completions_with_openai_solutions.py` script, utilizing OpenAI's Batch API. ")
        exit(1)

    start = time.time()

    response = ollama.generate(
        model = fileHelper.config["model"],
        prompt = construct_completion_text(problem, language),
    )["response"]

    end = time.time()
    timeToGenerate = end - start
    if '```' in response:
        response = response[response.find('```')+3:response.rfind('```')] # remove code block and explanations
    if response.startswith("python"):
        response = response[6:]
    response += f"\n#problem_{problem_id}"
    print(f"Generated ID{problem_id}. Time elapsed: {timeToGenerate}s")
    return CompletionInfo(problem_id, response, timeToGenerate)

def get_completions():
    shutil.rmtree(fileHelper.file_completions_path, ignore_errors=True)
    os.makedirs(fileHelper.file_completions_path)

    for problem_id in problems:
        completion = get_completion(problem_id, fileHelper.config["language"])

        open(f"{fileHelper.file_completions_path}{problem_id}.py", "w").write(completion.code)

    print("Finished generating completions, check the completions directory for the generated code.")

get_completions()
