"""
Feedback Provider Agent
Provides personalized learning feedback based on code review results.
Explains concepts and guides the user toward mastery.
"""

import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from orchestrator_state import TrainerState

load_dotenv()


class FeedbackProvider:
    """
    Provides personalized learning feedback and concept explanations.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-20250805"
    
    def provide_feedback(
        self,
        exercise_id: str,
        learning_focus: list,
        week: int,
        review_result: dict,
        key_concepts: list = None
    ) -> dict:
        """
        Provide personalized feedback based on code review.
        
        Args:
            exercise_id: Exercise ID
            learning_focus: What the exercise is focused on
            week: Week number
            review_result: Code review results
            key_concepts: Key concepts for the week
            
        Returns:
            Feedback dictionary with explanations and guidance
        """
        
        review_str = json.dumps(review_result, indent=2)[:1000]
        concepts_str = ", ".join(key_concepts) if key_concepts else "Not specified"
        focus_str = ", ".join(learning_focus) if learning_focus else "Not specified"
        
        prompt = f"""
You are an expert agentic AI instructor providing personalized feedback.

EXERCISE: {exercise_id}
WEEK: {week}
LEARNING FOCUS: {focus_str}
KEY CONCEPTS: {concepts_str}

CODE REVIEW RESULTS:
{review_str}

TASK:
Provide encouraging, detailed feedback that:
1. Celebrates what went well
2. Explains concepts the user might have struggled with
3. Connects to the bigger picture of agentic AI
4. Provides concrete next steps
5. Suggests follow-up exercises

FEEDBACK TEMPLATE:
{{
    "exercise_id": "{exercise_id}",
    "personalized_feedback": {{
        "what_went_well": "Your implementation shows X, which is excellent...",
        "concept_explanation": "Here's how X works: ...",
        "why_it_matters": "This is important because...",
        "common_mistakes": ["mistake1", "mistake2"],
        "your_mistake": null or "You had this issue..."
    }},
    "concept_deep_dive": {{
        "title": "Understanding Tool Calling",
        "explanation": "Tool calling is the mechanism where...",
        "why_important": "This is crucial for building...",
        "how_it_scales": "This pattern scales to...",
        "connection_to_agents": "In multi-agent systems..."
    }},
    "learning_resources": [
        {{
            "type": "concept",
            "title": "Agent Loops",
            "explanation": "The fundamental pattern...",
            "example": "Here's an example..."
        }},
        {{
            "type": "pattern",
            "title": "Error Handling in Agents",
            "explanation": "When tools fail..."
        }}
    ],
    "next_steps": [
        "Step 1: Add feature X",
        "Step 2: Test with Y",
        "Step 3: Move to Exercise 2"
    ],
    "follow_up_exercises": [
        "week{week}_exercise_2",
        "week{week}_exercise_3_advanced"
    ],
    "motivational_message": "Great work! You're building a strong foundation..."
}}

Be warm, encouraging, and educational.
Return ONLY valid JSON, no other text.
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2500,
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
                    "error": "No response from feedback provider"
                }
            
            # Parse JSON
            try:
                json_start = text_content.find('{')
                json_end = text_content.rfind('}') + 1
                json_str = text_content[json_start:json_end]
                feedback = json.loads(json_str)
                feedback["success"] = True
                return feedback
            except json.JSONDecodeError:
                return {
                    "exercise_id": exercise_id,
                    "error": "Failed to parse feedback",
                    "raw_response": text_content[:300]
                }
                
        except Exception as e:
            return {
                "exercise_id": exercise_id,
                "error": f"Feedback generation failed: {str(e)}"
            }
    
    def update_state(self, state: TrainerState) -> TrainerState:
        """
        Update state with feedback.
        """
        if not state.get("code_review_result"):
            state["errors"].append("No review results to provide feedback on")
            return state
        
        exercise = state.get("current_exercise", {})
        
        feedback = self.provide_feedback(
            state["exercise_id"],
            exercise.get("learning_focus", []),
            state["week"],
            state["code_review_result"],
            state["key_concepts"]
        )
        
        state["feedback_provided"] = True
        state["feedback_message"] = feedback
        
        if "learning_resources" in feedback:
            state["learning_resources"] = feedback.get("learning_resources", [])
        
        if "next_steps" in feedback:
            state["next_steps"] = feedback.get("next_steps", [])
        
        state["decision_log"].append({
            "agent": "FeedbackProvider",
            "exercise": state["exercise_id"],
            "feedback_generated": True
        })
        
        return state


def main():
    """Test the feedback provider"""
    provider = FeedbackProvider()
    
    # Sample review result
    review_result = {
        "passes_tests": True,
        "code_quality_score": 8.5,
        "issues": [],
        "improvements": ["Add docstrings", "Better error handling"],
        "pass_fail": "PASS"
    }
    
    print("Generating feedback...")
    feedback = provider.provide_feedback(
        "week1_exercise_1",
        ["Agent loops", "Tool calling"],
        1,
        review_result,
        ["Agent loops", "Tool definitions", "Conversation memory"]
    )
    
    print("\nFeedback Generated:")
    print(json.dumps(feedback, indent=2)[:800])


if __name__ == "__main__":
    main()
