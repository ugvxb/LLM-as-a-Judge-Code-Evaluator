import time
import re
import json
from typing import Dict, List, Any
from ollama import chat
from ollama import ChatResponse
from .llm_judge_core import LLMJudgeEvaluatorCore

class LLMJudgeEvaluatorAPI:
    def __init__(self, model_name: str = "llama3.1:8b", evaluator_core: LLMJudgeEvaluatorCore = None):
        self.model_name = model_name
        self.evaluator_core = evaluator_core if evaluator_core else LLMJudgeEvaluatorCore(model_name)

    def call_llm_judge(self, prompt: str, max_retries: int = 3) -> Dict[str, Any]:
        for attempt in range(max_retries):
            try:
                response: ChatResponse = chat(
                    model=self.model_name,
                    messages=[{'role': 'user', 'content': prompt}]
                )
                
                if hasattr(response, 'message') and hasattr(response.message, 'content'):
                    response_text = response.message.content
                elif isinstance(response, dict) and 'message' in response and 'content' in response['message']:
                    response_text = response['message']['content']
                else:
                    response_text = str(response)
                
                try:
                    return json.loads(response_text)
                except json.JSONDecodeError:
                    pass
                
                json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                if json_match:
                    json_string = json_match.group()
                    
                    simplified_json = self._simplify_json_response(json_string)
                    
                    try:
                        return json.loads(simplified_json)
                    except json.JSONDecodeError:
                        return self._extract_judgment_manually(response_text)
                else:
                    return self._extract_judgment_manually(response_text)
                    
            except Exception as e:
                if attempt < max_retries - 1:
                    time.sleep(2)
                else:
                    return {"error": f"All retries failed: {e}"}
        
        return {"error": "Unexpected error"}

    def _simplify_json_response(self, json_string: str) -> str:
        result = {}
        
        for field in ['criterion', 'score', 'confidence', 'level']:
            match = re.search(f'"{field}":\\s*"([^"]*)"', json_string)
            if match:
                result[field] = match.group(1)
            else:
                match = re.search(f'"{field}":\\s*([0-9.]+)', json_string)
                if match:
                    result[field] = float(match.group(1)) if field in ['score', 'confidence'] else match.group(1)
        
        reasoning_match = re.search(r'"reasoning":\s*"([^"]*)"', json_string, re.DOTALL)
        if reasoning_match:
            reasoning = reasoning_match.group(1)
            reasoning = reasoning[:500].replace('\n', ' ').replace('"', "'")
            result["reasoning"] = reasoning
        
        result["specific_evidence"] = [{"note": "Evidence available in raw response"}]
        
        return json.dumps(result)

    def _extract_judgment_manually(self, response_text: str) -> Dict[str, Any]:
        judgment = {
            "criterion": "unknown",
            "score": 0.0,
            "confidence": 0.5,
            "level": "unknown",
            "reasoning": "Automatic parsing failed",
            "specific_evidence": []
        }
        
        criterion_match = re.search(r'"criterion":\s*"([^"]*)"', response_text)
        if criterion_match:
            judgment["criterion"] = criterion_match.group(1)
        
        score_match = re.search(r'"score":\s*([0-9.]+)', response_text)
        if score_match:
            judgment["score"] = float(score_match.group(1))
        
        confidence_match = re.search(r'"confidence":\s*([0-9.]+)', response_text)
        if confidence_match:
            judgment["confidence"] = float(confidence_match.group(1))
        
        level_match = re.search(r'"level":\s*"([^"]*)"', response_text)
        if level_match:
            judgment["level"] = level_match.group(1)
        
        reasoning_match = re.search(r'"reasoning":\s*"([^"]*)"', response_text, re.DOTALL)
        if reasoning_match:
            judgment["reasoning"] = reasoning_match.group(1).replace('\\n', ' ').strip()
        
        return judgment

    def call_ollama_chat(self, prompt: str) -> str:
        try:
            response: ChatResponse = chat(
                model=self.model_name,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                    },
                ]
            )
            
            if hasattr(response, 'message') and hasattr(response.message, 'content'):
                return response.message.content
            elif isinstance(response, dict) and 'message' in response and 'content' in response['message']:
                return response['message']['content']
            else:
                return str(response)
                
        except Exception as e:
            return f"Error"

    def evaluate_with_multiple_judges(self, exercise_requirement: str, student_code: str, language: str = "python") -> Dict[str, Any]:
        print("Starting multi-judge evaluation...")
        
        individual_judgments = []
        failed_criteria = []
        
        for criterion in self.evaluator_core.evaluation_rubric.keys():
            print(f"    Judge evaluating: {criterion}")
            
            prompt = self.evaluator_core.create_judge_prompt(exercise_requirement, student_code, criterion, language)
            judgment = self.call_llm_judge(prompt)
            
            if "error" not in judgment:
                individual_judgments.append(judgment)
                print(f"    {criterion}: {judgment.get('score', 'N/A')}/10")
            else:
                failed_criteria.append(criterion)
                print(f"    {criterion}: Failed")
            
            time.sleep(1)
        
        print("   Chief judge synthesizing evaluations...")
        chief_prompt = self.evaluator_core.create_chief_judge_prompt(exercise_requirement, student_code, individual_judgments, language)
        chief_text = self.call_ollama_chat(chief_prompt)
        
        final_evaluation = self.evaluator_core.parse_final_evaluation(chief_text)
        final_evaluation["individual_judgments"] = individual_judgments
        final_evaluation["failed_criteria"] = failed_criteria
        final_evaluation["raw_chief_response"] = chief_text
        
        return final_evaluation
