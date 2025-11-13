import json
import re
from typing import Dict, List, Any, Tuple

class LLMJudgeEvaluatorCore:
    def __init__(self, model_name: str = "llama3.1:8b"):
        self.model_name = model_name
        self.evaluation_rubric = {
            "correctness": {
                "weight": 0.45,
                "description": "Does the code correctly solve the problem? Does it handle edge cases?",
                "levels": {
                    "excellent": (9, 10, "Perfect implementation meeting all requirements"),
                    "good": (7, 8.9, "Mostly correct with minor issues"),
                    "fair": (5, 6.9, "Partially correct but significant gaps"),
                    "poor": (0, 4.9, "Incorrect or completely missing functionality")
                }
            },
            "efficiency": {
                "weight": 0.30,
                "description": "Is the code optimized? Appropriate algorithms and data structures?",
                "levels": {
                    "excellent": (9, 10, "Optimal solution with best time/space complexity"),
                    "good": (7, 8.9, "Efficient with minor optimizations possible"),
                    "fair": (5, 6.9, "Suboptimal but functional"),
                    "poor": (0, 4.9, "Inefficient or problematic approach")
                }
            },
            "readability": {
                "weight": 0.25,
                "description": "Is the code clean, well-organized, and easy to understand?",
                "levels": {
                    "excellent": (9, 10, "Exceptionally clean and well-documented"),
                    "good": (7, 8.9, "Readable with minor style issues"),
                    "fair": (5, 6.9, "Somewhat readable but needs improvement"),
                    "poor": (0, 4.9, "Difficult to read and understand")
                }
            }
        }
    
    def create_judge_prompt(self, exercise_requirement: str, student_code: str, criterion: str, language: str = "python") -> str:        
        rubric_info = self.evaluation_rubric[criterion]
        
        system_prompt = f"""
        You are an expert {language.upper()} programming judge specializing in evaluating code for **{criterion.upper()}**.
        
        EVALUATION RUBRIC FOR {criterion.upper()}:
        {rubric_info['description']}
        
        SCORING LEVELS:
        {json.dumps(rubric_info['levels'], indent=2)}
        
        EXERCISE REQUIREMENT:
        {exercise_requirement}

        CODE TO EVALUATE:
        ```{language}
        {student_code}
        ```

        Please evaluate ONLY for {criterion} and provide your judgment in this EXACT JSON format:

        {{
            "criterion": "{criterion}",
            "score": <number_between_0_and_10>,
            "confidence": <number_between_0_and_1>,
            "level": "<excellent|good|fair|poor>",
            "reasoning": "<detailed explanation for this specific criterion>",
            "specific_evidence": [
                "<concrete example 1 from the code>",
                "<concrete example 2 from the code>"
            ]
        }}

        Focus ONLY on {criterion}. Be specific and reference actual code elements.
        """
        
        return system_prompt

    def create_chief_judge_prompt(self, exercise_requirement: str, student_code: str, individual_judgments: List[Dict], language: str = "python") -> str:
        
        judgments_str = json.dumps(individual_judgments, indent=2)
        
        system_prompt = f"""
        You are the CHIEF JUDGE synthesizing evaluations from multiple specialized judges.

        EXERCISE REQUIREMENT:
        {exercise_requirement}

        CODE EVALUATED:
        ```{language}
        {student_code}
        ```

        INDIVIDUAL JUDGE EVALUATIONS:
        {judgments_str}

        RUBRIC WEIGHTS:
        {json.dumps({k: v['weight'] for k, v in self.evaluation_rubric.items()}, indent=2)}

        Your task is to:
        1. Calculate weighted final score
        2. Provide comprehensive overall assessment
        3. Resolve any inconsistencies between judges
        4. Generate actionable feedback

        Provide your final evaluation in this EXACT format:

        **1. FINAL SCORE (0-10):** <weighted_score>
        **2. OVERALL ASSESSMENT:** <comprehensive_overview>
        **3. WEIGHTED BREAKDOWN:**
        {''.join([f'**{criterion}:** <score> (weight: {info["weight"]})' + '\\n' for criterion, info in self.evaluation_rubric.items()])}
        **4. KEY STRENGTHS:** 
        - <strength1>
        - <strength2>
        **5. CRITICAL ISSUES:**
        - <issue1>
        - <issue2>
        **6. ACTIONABLE IMPROVEMENTS:**
        - <improvement1>
        - <improvement2>
        **7. LEARNING PATH:**
        - <learning_step1>
        - <learning_step2>
        **8. JUDGE CONSENSUS:** <high|medium|low> <explanation>

        Be precise and reference specific evidence from individual judgments.
        """
        
        return system_prompt

    def parse_final_evaluation(self, response_text: str) -> Dict[str, Any]:
        evaluation = {
            "final_score": 0,
            "overall_assessment": "",
            "weighted_breakdown": {},
            "key_strengths": [],
            "critical_issues": [],
            "actionable_improvements": [],
            "learning_path": [],
            "judge_consensus": "",
            "raw_response": response_text
        }
        
        try:
            score_match = re.search(r'\*\*1\.\s*FINAL SCORE\s*\(0-10\):\*\*\s*(\d+(?:\.\d+)?)', response_text)
            if score_match:
                evaluation["final_score"] = float(score_match.group(1))
            
            overview_match = re.search(r'\*\*2\.\s*OVERALL ASSESSMENT:\*\*\s*(.*?)(?=\*\*3\.|$)', response_text, re.DOTALL)
            if overview_match:
                evaluation["overall_assessment"] = overview_match.group(1).strip()
            
            breakdown_section = re.search(r'\*\*3\.\s*WEIGHTED BREAKDOWN:\*\*(.*?)(?=\*\*4\.|$)', response_text, re.DOTALL)
            if breakdown_section:
                breakdown_text = breakdown_section.group(1)
                for criterion in self.evaluation_rubric.keys():
                    pattern = fr'\*\*{criterion}:\*\*\s*(\d+(?:\.\d+)?)'
                    match = re.search(pattern, breakdown_text, re.IGNORECASE)
                    if match:
                        evaluation["weighted_breakdown"][criterion] = float(match.group(1))
            
            sections = {
                "key_strengths": (r'\*\*4\.\s*KEY STRENGTHS:\*\*(.*?)(?=\*\*5\.|$)', True),
                "critical_issues": (r'\*\*5\.\s*CRITICAL ISSUES:\*\*(.*?)(?=\*\*6\.|$)', True),
                "actionable_improvements": (r'\*\*6\.\s*ACTIONABLE IMPROVEMENTS:\*\*(.*?)(?=\*\*7\.|$)', True),
                "learning_path": (r'\*\*7\.\s*LEARNING PATH:\*\*(.*?)(?=\*\*8\.|$)', True),
                "judge_consensus": (r'\*\*8\.\s*JUDGE CONSENSUS:\*\*(.*?)(?=$)', False)
            }
            
            for key, (pattern, is_list) in sections.items():
                match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL)
                if match:
                    content = match.group(1).strip()
                    if is_list:
                        items = self._extract_list_items(content)
                        evaluation[key] = items
                    else:
                        evaluation[key] = content
                        
        except Exception as e:
            evaluation["error"] = f"Parsing error"
            
        return evaluation

    def _extract_list_items(self, content: str) -> List[str]:
        items = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('-') or re.match(r'^\s*[•*]\s*', line):
                item = re.sub(r'^[-\s•*]+\s*', '', line).strip()
                if item and len(item) > 3:
                    items.append(item)
            elif line and not line.startswith('**') and len(line) > 10:
                items.append(line)
        
        seen = set()
        unique_items = []
        for item in items:
            if item not in seen:
                seen.add(item)
                unique_items.append(item)
        
        return unique_items[:6]
