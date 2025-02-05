import json
import os
import glob
from file_helper import FileHelper

fileHelper = FileHelper(f"{os.getcwd()}/supporting_files/", "problems.json", "test_cases/", "completions/", "solutions.json", reset=False)

batch_outputs_folder = './batch_outputs_hintstrue_error_prompt_completions/'


files = glob.glob(os.path.join(batch_outputs_folder, '*'))

for file_path in files:
	with open(file_path, 'r') as file:
		content = file.read()

files = os.listdir(batch_outputs_folder)

problems_to_solutions = {}

for file in files:
	with open(os.path.join(batch_outputs_folder, file), 'r') as f:
		for line in f:
			data = json.loads(line)
			problems_to_solutions[data['custom_id']] = data["response"]["body"]["choices"][0]["message"]["content"]

print(problems_to_solutions.keys())
print(len(problems_to_solutions))

missing_problems = fileHelper.file_contents.keys() - problems_to_solutions.keys()
print(missing_problems)

with open("supporting_files/chatgpt4o-hintsTrue-error_prompt.json", "w") as file: # Make sure to aptly name this file
	file.write(json.dumps(problems_to_solutions))

# Head over to `transform_openai_to_folder.py` next!