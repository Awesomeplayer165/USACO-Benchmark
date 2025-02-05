class Hints:
    false = "False"
    true = "True"
    openai = "openai"
    openai_error_prompt = "openai-error_prompt"

class FileHelper:
    file_directory: str
    file_problem_path: str
    file_test_cases_path: str
    file_completions_path: str
    file_solutions_path: str
    file_openai_solutions_path: str
    config: dict = {}

    file_contents: dict = {} # memory buffer of file content, updated privately

    solutions_contents: dict = {} # memory buffer of solutions content, updated privately

    openai_solutions_contents: dict = {} # memory buffer of openai solutions content, updated privately

    # file_directory: directory where files are stored. Usually the supporting_files directory, but can be customized in setup.py
    # file_problem_name: name of problems file. Found in the file_directory
    # file_test_cases_directory: name of the test cases file. Found in the file_directory
    # reset: if True, will delete the test cases directory and start fresh. Default is False
    # openai_solutions_name: name of openai solutions content. default: 'openai_solutions.json'
    def __init__(self, file_directory: str, file_problem_name: str, file_test_cases_directory: str, file_completions_directory: str, file_solutions_path: str, reset: bool = False, openai_solutions_name: str = "openai_solutions.json"):
        # standardize with / at the end
        self.config = self._read_config()       
        file_completions_directory = file_completions_directory + f'-{self.config["language"]}-{self.config["model"]}-hints{self.config["hints"]}/' if not file_completions_directory.endswith('/') else file_completions_directory[:-1] + f'-{self.config["language"]}-{self.config["model"]}-hints{self.config["hints"]}/'
        file_completions_directory = file_completions_directory.replace(":", "_")
        file_directory = file_directory + '/' if not file_directory.endswith('/') else file_directory
        file_test_cases_directory = file_test_cases_directory + '/' if not file_test_cases_directory.endswith('/') else file_test_cases_directory

        # file_completions_directory = file_completions_directory.replace(":", "_")

        # set the file paths wrt to the name-parameters
        self.file_directory = file_directory
        self.file_problem_path = file_directory + file_problem_name
        self.file_test_cases_path = file_directory + file_test_cases_directory
        self.file_completions_path = file_directory + file_completions_directory
        self.file_solutions_path = file_directory + file_solutions_path
        self.file_openai_solutions_path = file_directory + openai_solutions_name
        # create the supporting_files directory if it doesn't exist
        if not os.path.exists(file_directory):
            os.makedirs(file_directory)

        if reset:
            # remove test cases directory to start fresh
            shutil.rmtree(self.file_test_cases_path, ignore_errors=True)

            shutil.rmtree(self.file_completions_path, ignore_errors=True)

            # create the test cases directory
            os.makedirs(self.file_test_cases_path)
            os.makedirs(self.file_completions_path)

        # read what we have so far and update our file_contents buffer.
        self.file_contents = self._read_problems()
        self.solutions_contents = self._read_solutions()
        self.openai_solutions_contents = self._read_openai_solutions()

    def append_problem_to_file(self, problem_text: str, problem_link: str):
        with open(self.file_problem_path, 'w') as file:
            problem_link = problem_link.split('=')[-1]
            self.file_contents[problem_link] = problem_text
            file.write(json.dumps(self.file_contents))
            print(f"Successfully wrote {problem_link}")

    # primarily used privately to read and update the file_contents buffer
    def _read_problems(self) -> dict:
        try:
            with open(self.file_problem_path, 'r') as file:
                return json.loads(file.read()) or {}
        except json.decoder.JSONDecodeError:
            print("Error reading problems file. Please make sure it is a valid JSON file. Ignoring")
            return {}
        except FileNotFoundError:
            return {}

    def _read_solutions(self) -> dict:
        try:
            with open(self.file_solutions_path, 'r') as file:
                return json.loads(file.read()) or {}
        except json.decoder.JSONDecodeError:
            print("Error reading solutions file. Please make sure it is a valid JSON file. Ignoring")
            return {}
        except FileNotFoundError:
            return {}

    def _read_config(self) -> dict:
        try:
            with open(f'{os.getcwd()}/config.json', 'r') as file:
                return json.loads(file.read()) or {}
        except json.decoder.JSONDecodeError:
            print("Error reading config file. Please make sure it is a valid JSON file. Ignoring")
            return {}
        except FileNotFoundError:
            return {}

    def _read_openai_solutions(self) -> dict:
        try:
            with open(self.file_openai_solutions_path, 'r') as file:
                return json.loads(file.read()) or {}
        except json.decoder.JSONDecodeError:
            print("Error reading config file. Please make sure it is a valid JSON file. Ignoring")
            return {}
        except FileNotFoundError:
            return {}
            
    # downloads and saves the test cases links to disk, then zips them with the corresponding problem link as the name.
    def save_test_cases(self, test_cases_download_links: dict):
        for problem_link, test_cases_link in test_cases_download_links.items():
            print(f"Downloading test cases from {problem_link}")
            test_cases = requests.get(test_cases_link)
            zipPath = self.file_test_cases_path + problem_link.split('=')[-1]
            with open(zipPath + '.zip', 'wb') as file:
                file.write(test_cases.content)
                print(f"Successfully downloaded and saved test cases from {problem_link}")

            with ZipFile(zipPath + '.zip', 'r') as zip_ref:
                zip_ref.extractall(zipPath)
                print(f"Successfully extracted test cases from {problem_link}")

            # we unzipped to a folder, so we don't need to original .zip file
            os.remove(zipPath + '.zip')

    def append_solution_to_file(self, downloaded_solutions: dict):
        if not downloaded_solutions:
            print("No solutions found... Skipping")
            return
        with open(self.file_solutions_path, 'w') as file:
            for problem_link, solution_text in downloaded_solutions.items():
                problem_id = problem_link.split('=')[-1]
                self.solutions_contents[problem_id] = solution_text
                print(f"Successfully wrote solution {problem_link}")

            file.write(json.dumps(self.solutions_contents))

    def append_openai_solution_to_file(self, openai_solutions: dict):
        if not openai_solutions:
            print("No openai solutions found... Skipping")
            return
        with open(self.file_openai_solutions_path, 'w') as file:
            for problem_id, completion_text in openai_solutions.items():
                self.openai_solutions_contents[problem_id] = completion_text
                print(f"Successfully wrote openai solution {problem_id}")

            file.write(json.dumps(self.openai_solutions_contents))