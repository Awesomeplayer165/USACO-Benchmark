import traceback
import multiprocessing as mp
import os
import json
from file_helper import FileHelper

class Process(mp.Process):
    def __init__(self, *args, **kargs):
        mp.Process.__init__(self, *args, **kargs)
        self._pconn, self._cconn = mp.Pipe()
        self._exception = None

    def run(self):
        try:
            mp.Process.run(self)
            self._cconn.send(None)
        except Exception as e:
            tb = traceback.format_exc()
            self._cconn.send((e, tb))
            # raise e  # You can still raise this exception if you need to

    @property
    def exception(self):
        if self._pconn.poll():
            self._exception = self._pconn.recv()
        return self._exception

def append_test_case_value(problem_id: int, value, test_cases):
    if problem_id in test_cases:
        test_cases[problem_id].append(value)
    else:
        test_cases[problem_id] = [value]

def run_completion(problem_id, fileHelper):
    print(f"{fileHelper.file_completions_path}{problem_id}.py")
    src = open(f"{fileHelper.file_completions_path}{problem_id}.py").read().lstrip("Python").lstrip("python")
    exec(src)

def run_tests():
    fileHelper = FileHelper(f"{os.getcwd()}/supporting_files/", "problems.json", "test_cases/", "completions/", "solutions.json", reset=False)

    test_cases = {} # test case number: ["FAIL", "PASS", ..] (in order of test cases)
    problems = fileHelper.file_contents

    if not os.path.exists("input.in"):
         open("input.in", "").write("")

    if not os.path.exists("output.out"):
        open("output.out", "w").write("")

    #print(f"Problems Found: {len(problems)}, Completions Found: {len(completions)} (Ideally, these should be equal)")

    for problem_id in problems:
        total_cases = 0
        try:
            total_cases = int(len(os.listdir(f'{fileHelper.file_test_cases_path}{problem_id}/')) / 2)
        except:
            print(f"Skipping problem {problem_id} because of missing test cases")
            continue

        print(f"Testing problem {problem_id} with {total_cases} test cases")

        for i in range(1, int(total_cases + 1)):
            try:
                inFile = open(f"{fileHelper.file_test_cases_path}{problem_id}/{i}.in", "r").read()
                outFile = open(f"{fileHelper.file_test_cases_path}{problem_id}/{i}.out", "r").read()

                open("input.in", "w").write(inFile)
                process = Process(target=run_completion, args=(problem_id, fileHelper, ), name=f"Test {i}")
                process.start()
                process.join(5)
                process.terminate()
                process.kill()
                test_cases[problem_id] = [] if len(test_cases.get(problem_id, [])) == 0 else test_cases[problem_id]

                if process.exception:
                    print("run_tests for each process.exception block")
                    error, traceback = process.exception
                    print(traceback)
                    append_test_case_value(problem_id, (f"{error.__class__.__name__}: {str(error)}"), test_cases)
                elif open("output.out", "r").read().strip() == outFile:
                    print(f"Test {i}/{total_cases} of {problem_id} passed")
                    append_test_case_value(problem_id, "PASS", test_cases)
                else:
                    print(f"Test {i}/{total_cases} of {problem_id} failed")
                    append_test_case_value(problem_id, "FAIL", test_cases)

            except Exception as e:
                print("run_tests for each except block")
                print(traceback.format_exc())
                print(f"Test {i}/{total_cases} of {problem_id} errored with {e.__class__.__name__}")
                append_test_case_value(problem_id, e.__class__.__name__)

        open(f"completion_results-{fileHelper.config['language']}-{fileHelper.config['model']}-hints{fileHelper.config['hints']}.jsonl", "a").write(json.dumps({problem_id: test_cases[problem_id]}) + "\n")

if __name__ == "__main__":
    run_tests()
