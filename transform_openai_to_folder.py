import os
import json

# Define the folder name
folder_name = 'supporting_files/completions-python-chatgpt4o-hintsTrue-error_prompt'

# Create the folder if it doesn't exist
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Load the JSON content from the file
with open('supporting_files/chatgpt4o-hintsTrue-error_prompt.json', 'r') as json_file:
    data = json.load(json_file)

# Loop through the JSON content and create individual files
for key, content in data.items():
    file_name = f"{key}.py"
    file_content = f"""{content}
# problem_id {key}
"""
    # Write the content to the file
    with open(os.path.join(folder_name, file_name), 'w') as output_file:
        output_file.write(file_content)

print(f"Files have been created in the '{folder_name}' folder.")
