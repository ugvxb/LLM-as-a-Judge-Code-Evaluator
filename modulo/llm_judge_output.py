import datetime
from typing import Dict, List, Any
from .llm_judge_core import LLMJudgeEvaluatorCore

class LLMJudgeEvaluatorOutput:
    def __init__(self, evaluator_core: LLMJudgeEvaluatorCore = None):
        self.evaluator_core = evaluator_core if evaluator_core else LLMJudgeEvaluatorCore()

    def display_evaluation_result(self, evaluation: Dict[str, Any]):
        print("\n" + "=" * 80)
        print(" LLM-AS-A-JUDGE EVALUATION RESULTS")
        print("=" * 80)
        
        if "error" in evaluation:
            print(f"Error: {evaluation['error']}")
            return
        
        score = evaluation.get("final_score", 0)
        print(f" FINAL SCORE: {score:.1f}/10.0")
        
        if evaluation.get("overall_assessment"):
            print(f"\n OVERALL ASSESSMENT:")
            print(f"   {evaluation['overall_assessment']}")
        
        if evaluation.get("weighted_breakdown"):
            print(f"\n WEIGHTED BREAKDOWN:")
            for criterion, score in evaluation["weighted_breakdown"].items():
                weight = self.evaluator_core.evaluation_rubric[criterion]["weight"] * 100
                print(f"   {criterion.title():<15}: {score:<4.1f} (weight: {weight}%)")
        
        if evaluation.get("individual_judgments"):
            print(f"\n  INDIVIDUAL JUDGE SCORES:")
            for judgment in evaluation["individual_judgments"]:
                criterion = judgment.get("criterion", "unknown")
                score = judgment.get("score", 0)
                confidence = judgment.get("confidence", 0)
                level = judgment.get("level", "unknown")
                print(f"   {criterion.title():<15}: {score:<4.1f} ({level}, confidence: {confidence:.2f})")
        
        sections = [
            (" KEY STRENGTHS", "key_strengths"),
            (" CRITICAL ISSUES", "critical_issues"), 
            (" ACTIONABLE IMPROVEMENTS", "actionable_improvements"),
            (" LEARNING PATH", "learning_path")
        ]
        
        for title, key in sections:
            if evaluation.get(key):
                print(f"\n{title}:")
                for i, item in enumerate(evaluation[key], 1):
                    print(f"   {i}. {item}")
        
        if evaluation.get("judge_consensus"):
            print(f"\n🤝 JUDGE CONSENSUS:")
            print(f"   {evaluation['judge_consensus']}")
        
        print("=" * 80)

    def save_evaluation_to_file(self, exercise_requirement: str, student_code: str, evaluation: Dict[str, Any], language: str = "python", output_file: str = None):
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            if not output_file:
                output_file = f"llm_judge_evaluation_{timestamp}.txt"
            
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("LLM-AS-A-JUDGE EVALUATION REPORT\n")
                f.write("=" * 60 + "\n\n")
                
                f.write(f"Evaluation Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Programming Language: {language}\n")
                f.write(f"Model Used: {self.evaluator_core.model_name}\n")
                f.write(f"Final Score: {evaluation.get('final_score', 0):.1f}/10.0\n\n")
                
                f.write("EXERCISE REQUIREMENT:\n")
                f.write("-" * 40 + "\n")
                f.write(f"{exercise_requirement}\n\n")
                
                f.write("STUDENT CODE:\n")
                f.write("-" * 40 + "\n")
                f.write(f"```{language}\n{student_code}\n```\n\n")
                
                f.write("FINAL EVALUATION:\n")
                f.write("-" * 40 + "\n")
                f.write(f"Score: {evaluation.get('final_score', 0):.1f}/10.0\n\n")
                
                if evaluation.get('overall_assessment'):
                    f.write("Overall Assessment:\n")
                    f.write(f"{evaluation['overall_assessment']}\n\n")
                
                if evaluation.get("weighted_breakdown"):
                    f.write("WEIGHTED BREAKDOWN:\n")
                    f.write("-" * 40 + "\n")
                    for criterion, score in evaluation["weighted_breakdown"].items():
                        weight = self.evaluator_core.evaluation_rubric[criterion]["weight"] * 100
                        f.write(f"{criterion.title():<15}: {score:<4.1f} (weight: {weight}%)\n")
                    f.write("\n")
                
                if evaluation.get("individual_judgments"):
                    f.write("INDIVIDUAL JUDGE SCORES:\n")
                    f.write("-" * 40 + "\n")
                    for judgment in evaluation["individual_judgments"]:
                        criterion = judgment.get("criterion", "unknown")
                        score = judgment.get("score", 0)
                        confidence = judgment.get("confidence", 0)
                        level = judgment.get("level", "unknown")
                        f.write(f"{criterion.title():<15}: {score:<4.1f} ({level}, confidence: {confidence:.2f})\n")
                    f.write("\n")
                
                sections = [
                    ("KEY STRENGTHS", "key_strengths"),
                    ("CRITICAL ISSUES", "critical_issues"),
                    ("ACTIONABLE IMPROVEMENTS", "actionable_improvements"), 
                    ("LEARNING PATH", "learning_path")
                ]
                
                for title, key in sections:
                    if evaluation.get(key):
                        f.write(f"{title.replace('_', ' ').upper()}:\n")
                        f.write("-" * 40 + "\n")
                        if isinstance(evaluation[key], list):
                            for i, item in enumerate(evaluation[key], 1):
                                f.write(f"{i}. {item}\n")
                        else:
                            f.write(f"{evaluation[key]}\n")
                        f.write("\n")
                
                if evaluation.get("judge_consensus"):
                    f.write("JUDGE CONSENSUS:\n")
                    f.write("-" * 40 + "\n")
                    f.write(f"{evaluation['judge_consensus']}\n\n")
                
                f.write("=" * 60 + "\n")
                f.write("End of Evaluation Report\n")
            
            print(f" Results saved to: {output_file}")
            return output_file
            
        except Exception as e:
            return None
