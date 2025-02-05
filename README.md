# USACO-Benchmark

## Pre-requisites

- [Ollama](https://ollama.com/)
- 7-zip / p7zip
    - [Windows] (https://www.7-zip.org/)
    - macOS: `brew install p7zip`
    - Linux: pre-installed on most distros. 
- Have [pulled any Ollama models](https://github.com/ollama/ollama/blob/main/docs/api.md#pull-a-model) you want to use or wrote the [Ollama model file](https://github.com/ollama/ollama/blob/main/docs/modelfile.md) for custom models or fine tuning
- Python 3.8+

## Hardware Requirements

**Apple** Recommended: Apple Silicon (any M-series) with at least 32GB of memory, excluding Air models

**Windows/Linux** Systems:

- For 7B models, at least 8GB RAM is recommended.
- For 13B models, at least 16GB RAM is recommended.
- For 70B models, at least 64GB RAM is recommended.

For more detailed information on GPU Requirements, please see [this resource](https://github.com/ollama/ollama/blob/main/docs/gpu.md) from Ollama

## Installation

Clone the repository and install the requirements:

```bash
git clone https://github.com/1usaco/USACO-Benchmark
cd USACO-Benchmark
pip install -r requirements.txt
```

## Usage

There are three stages for this benchmark:

### 1. Download the supporting files folder from the [GitHub releases](https://github.com/1usaco/USACO-Benchmark/releases) page
Note: `supporting_files` archive is under 2GB, but uncompressing will consume 6.1GB (after deleting the original archive).

Specifically, you need to download all `supporting_files.7z.*` into the root of the repo.
Then, create a folder named `supporting_files`, run the following to cat the files into one `supporting_files.7z` file, and unzip with 7zip.
```bash
mkdir supporting_files
cat supporting_files.7z.* > supporting_files.7z
7z x supporting_files.7z supporting_files
```

Make sure to delete all leftover artifacts.

### 2. Generate completions from AI
NOTE: Generating completions means generating arbitrary code! Make sure to run this in a safe environment.

First, update `config.json` with the following format.
```json
{"model": "<model_name>", "language": "python", "use_hints": False}
```

To generate completions from the AI, run the following command:

```bash
python3 generate_completions.py
```

This will generate completions for all the problems in the problems.json file. The completions will be stored in the `completions` directory.
Note: Each setting creates a unique completions folder. If a folder already exists when attempting to run a completion, it will overwrite that existing folder.

OpenAI Batch API has support, just run `generate_completions_with_openai_solutions.py`. If you would like to use a different model service than OpenAI, like Anthropic for example. then you can write you own. Just make sure to adhere to a `completions.json` protocol of `{str<problem_id>: str<solution_text>}`. Specifically, each `problem_id` key, which are strings, are mapped to a solution text, which is also a string. The prompting and code extraction should be mapped as well. Then, be sure to update `solutions.json` parameter of `FileHelper` anywhere the solutions parameter is set to use. 

### 3. Evaluating the completions against test cases
NOTE: Evaluating completions means running arbitrary code to verify test cases meet input and outputs. Make sure to run this in a safe environment.

To evaluate the completions against the test cases, run the following command:

```bash
python3 evaluate_completions.py
```

Evaluations also uses the `config.json` file to identify which completion folder to validate.

# Authors

[Jacob Trentini](https://www.linkedin.com/in/jacobtrentini/)
[Victor Liu](https://google.com)
[Yiming Peng](https://google.com)

Mentor: [Dr. Zong](https://google.com)
