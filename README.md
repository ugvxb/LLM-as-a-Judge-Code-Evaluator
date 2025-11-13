# LLM-as-a-Judge Code Evaluator

![LLM-as-a-Judge Code Evaluator](LLM-as-a-Judge%20Code%20Evaluator.png)

This project implements an LLM-as-a-Judge system for evaluating student code against exercise requirements. It leverages the Ollama framework to interact with large language models, using them as "judges" to assess code based on predefined criteria such as correctness, efficiency, and readability.

## Features

- **Multi-Criteria Evaluation**: Code is evaluated across multiple dimensions (e.g., correctness, efficiency, readability) using a detailed rubric.
- **LLM-Powered Judging**: Utilizes Ollama-compatible LLMs to act as individual judges for each criterion.
- **Chief Judge Synthesis**: A "chief judge" LLM synthesizes individual judgments, calculates a weighted final score, and provides an overall assessment with actionable feedback.
- **Flexible Model Selection**: Supports specifying different Ollama models for evaluation.
- **Detailed Output**: Generates a comprehensive evaluation report including scores, reasoning, strengths, critical issues, and improvement suggestions.

## How it Works

The system operates in two main phases:

1.  **Individual Judging**: For each predefined criterion (e.g., correctness), a specialized prompt is constructed and sent to an LLM (the "individual judge"). The LLM evaluates the student's code against the exercise requirement and the specific criterion, returning a structured judgment (score, confidence, reasoning, evidence).
2.  **Chief Judging**: Once all individual judgments are collected, a "chief judge" LLM receives all individual judgments, the original exercise requirement, and the student's code. It then synthesizes this information to provide a final weighted score, an overall assessment, and detailed feedback.

## Setup

### Prerequisites

-   **Ollama**: Ensure Ollama is installed and running on your system. You can download it from [https://ollama.com/](https://ollama.com/).
-   **Python 3.x**: The project is written in Python.

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/ugvxb/LLM-as-a-Judge-Code-Evaluator
    cd LLM-as-a-Judge-Code-Evaluator
    ```

2.  **Install Python dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Based on the code, the primary dependency is `ollama`. Install `ollama`: `pip install ollama`)*

3.  **Download an Ollama model**:
    Before running the evaluator, you need to pull an LLM model using Ollama. The default model used in this project is `llama3.1:8b`.
    ```bash
    ollama pull llama3.1:8b
    ```
    You can use any other compatible model by specifying it during runtime.

## Usage

To run the LLM-as-a-Judge evaluator, use the `main.py` script:

```bash
python main.py <question_file.md> <answer_file.py> <output_file.txt> [language] [model_name]
```

### Arguments

-   `<question_file.md>`: Path to a Markdown file containing the exercise requirements or problem description.
-   `<answer_file.py>`: Path to the student's code file to be evaluated.
-   `<output_file.txt>`: Path where the detailed evaluation results will be saved.
-   `[language]` (optional): The programming language of the student's code (default: `python`).
-   `[model_name]` (optional): The name of the Ollama model to use for judging (default: `llama3.1:8b`).

### Example

```bash
python main.py question.md answer.py results.txt python llama3.1:8b
```

This command will evaluate the `answer.py` code based on the `question.md` requirements, using the `llama3.1:8b` Ollama model, and save the results to `results.txt`.

## Project Structure

```
.
├── main.py                     # Main script to run the evaluation
├── requirements.txt            # Python dependencies
├── question.md                 # Example exercise requirement
├── answer.py                   # Example student code
├── result.txt                  # Example output file
└── modulo/
    ├── llm_judge_api.py        # Handles LLM interaction (Ollama calls, response parsing)
    ├── llm_judge_core.py       # Defines evaluation rubric, prompt creation, and result parsing
    ├── llm_judge_output.py     # Handles displaying and saving evaluation results
    └── utils.py                # Utility functions (e.g., file reading)
```

## References

-   **Ollama Documentation**: [https://docs.ollama.com/](https://docs.ollama.com/)

