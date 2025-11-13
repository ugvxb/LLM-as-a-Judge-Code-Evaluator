import sys

from modulo.llm_judge_core import LLMJudgeEvaluatorCore
from modulo.llm_judge_api import LLMJudgeEvaluatorAPI
from modulo.llm_judge_output import LLMJudgeEvaluatorOutput
from modulo.utils import read_file

def main():
    if len(sys.argv) < 4:
        print("Usage: python main.py question.md answer.py output.txt [language] [model_name]")
        print("Example: python main.py question.md answer.py results.txt python llama3.1:8b")
        return
    
    question_file = sys.argv[1]
    answer_file = sys.argv[2]
    output_file = sys.argv[3]
    language = sys.argv[4] if len(sys.argv) > 4 else "python"
    model_name = sys.argv[5] if len(sys.argv) > 5 else "llama3.1:8b"
    
    exercise_requirement = read_file(question_file)
    if not exercise_requirement:
        print("Failed to read exercise requirement file")
        return
    
    student_code = read_file(answer_file)
    if not student_code:
        print("Failed to read student code file")
        return
    
    evaluator_core = LLMJudgeEvaluatorCore(model_name=model_name)
    evaluator_api = LLMJudgeEvaluatorAPI(model_name=model_name, evaluator_core=evaluator_core)
    evaluator_output = LLMJudgeEvaluatorOutput(evaluator_core=evaluator_core)
    
    print(" Starting LLM-as-a-Judge evaluation...")
    print(f" Exercise: {question_file}")
    print(f" Code: {answer_file}")
    print(f" Language: {language}")
    print(f" Model: {model_name}")
    
    evaluation_result = evaluator_api.evaluate_with_multiple_judges(exercise_requirement, student_code, language)
    
    evaluator_output.display_evaluation_result(evaluation_result)
    
    saved_file = evaluator_output.save_evaluation_to_file(exercise_requirement, student_code, evaluation_result, language, output_file)
    
    if saved_file:
        print(f"Evaluation completed! Results saved to: {saved_file}")
    else:
        print("Error occurred while saving results")

if __name__ == "__main__":
    main()
