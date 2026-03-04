"""
Code Reviewer Agent
Reviews user solutions and provides code quality assessment, bug detection,
and technical feedback.
"""

import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from orchestrator_state import CodeReviewResult, TrainerState

load_dotenv()


class CodeReviewer:
    """
    Reviews code solutions for correctness, quality, and learning alignment.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-20250805"
    
    def review_code(
        self,
        exercise_id: str,
        user_code: str,
        requirements: list,
        test_cases: list = None,
        learning_focus: list = None
    ) -> dict:
        """
        Review user's code solution.
        
        Args:
            exercise_id: ID of the exercise
            user_code: User's code to review
            requirements: Exercise requirements
            test_cases: Test cases to validate against
            learning_focus: What the exercise is focused on learning
            
        Returns:
            Code review result dictionary
        """
        
        test_cases_str = json.dumps(test_cases, indent=2) if test_cases else "No test cases provided"
        learning_focus_str = ", ".join(learning_focus) if learning_focus else "Not specified"
        
        prompt = f"""
You are a code reviewer for an agentic AI training program.

EXERCISE ID: {exercise_id}
LEARNING FOCUS: {learning_focus_str}

REQUIREMENTS:
{json.dumps(requirements, indent=2)}

TEST CASES:
{test_cases_str}

USER'S CODE:
```python
{user_code}
```

TASK:
Review this code thoroughly. Return a JSON object with:

1. passes_tests: Does it meet the requirements? (true/false)
2. code_quality_score: 0-10 score for code quality
3. issues: List of bugs, errors, or concerns
4. improvements: List of improvements
5. score_breakdown: Scores for functionality, quality, learning_alignment, documentation
6. pass_fail: "PASS", "PASS_WITH_NOTES", or "NEEDS_WORK"

REVIEW FORMAT:
{{
    "exercise_id": "{exercise_id}",
    "passes_tests": true/false,
    "code_quality_score": 8.5,
    "analysis": {{
        "correctness": {{
            "passes": ["requirement1 met", "requirement2 met"],
            "issues": ["issue1", "issue2"],
            "severity": "low/medium/high"
        }},
        "code_quality": {{
            "strengths": ["strength1", "strength2"],
            "improvements": ["improvement1", "improvement2"]
        }},
        "learning_alignment": {{
            "demonstrates": ["concept1", "concept2"],
            "missing": ["concept1"]
        }}
    }},
    "issues": [
        {{"line": 42, "severity": "medium", "issue": "Unhandled exception", "suggestion": "Add try/except"}},
    ],
    "improvements": [
        "Add docstrings",
        "Consider using TypedDict",
        "Add error handling"
    ],
    "score_breakdown": {{
        "functionality": 9,
        "code_quality": 8,
        "learning_alignment": 8,
        "documentation": 7
    }},
    "pass_fail": "PASS"
}}

Be thorough but encouraging. Focus on learning.
Return ONLY valid JSON, no other text.
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 1500
                },
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract text
            text_content = None
            for block in response.content:
                if block.type == "text":
                    text_content = block.text
                    break
            
            if not text_content:
                return {
                    "exercise_id": exercise_id,
                    "error": "No response from reviewer",
                    "passes_tests": False
                }
            
            # Parse JSON
            try:
                json_start = text_content.find('{')
                json_end = text_content.rfind('}') + 1
                json_str = text_content[json_start:json_end]
                review = json.loads(json_str)
                review["success"] = True
                return review
            except json.JSONDecodeError:
                return {
                    "exercise_id": exercise_id,
                    "error": "Failed to parse review",
                    "raw_response": text_content[:200],
                    "passes_tests": False
                }
                
        except Exception as e:
            return {
                "exercise_id": exercise_id,
                "error": f"Review failed: {str(e)}",
                "passes_tests": False
            }
    
    def update_state(self, state: TrainerState) -> TrainerState:
        """
        Update state with code review results.
        """
        if not state["user_code"]:
            state["errors"].append("No code to review")
            return state
        
        exercise = state.get("current_exercise")
        if not exercise:
            state["errors"].append("No current exercise")
            return state
        
        review_result = self.review_code(
            state["exercise_id"],
            state["user_code"],
            exercise.get("requirements", []),
            exercise.get("test_cases", []),
            exercise.get("learning_focus", [])
        )
        
        state["review_completed"] = True
        state["code_review_result"] = review_result
        
        state["decision_log"].append({
            "agent": "CodeReviewer",
            "exercise": state["exercise_id"],
            "passes": review_result.get("passes_tests", False),
            "quality_score": review_result.get("code_quality_score", 0)
        })
        
        return state


def main():
    """Test the code reviewer"""
    reviewer = CodeReviewer()
    
    # Sample code to review
    sample_code = """
from anthropic import Anthropic

client = Anthropic()

def add_task(title):
    return f"Added: {title}"

def list_tasks():
    return "Your tasks: task1, task2"

# Simple agent loop
messages = [{"role": "user", "content": "Add a task"}]
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=messages,
    max_tokens=100
)

print(response.content[0].text)
"""
    
    requirements = [
        "Agent responds to natural language",
        "Can add tasks",
        "Can list tasks"
    ]
    
    print("Reviewing code...")
    review = reviewer.review_code(
        "week1_exercise_1",
        sample_code,
        requirements,
        learning_focus=["Agent loops", "Tool calling"]
    )
    
    print("\nCode Review Results:")
    print(json.dumps(review, indent=2)[:800])


if __name__ == "__main__":
    main()
