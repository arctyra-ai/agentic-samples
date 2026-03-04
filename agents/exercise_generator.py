"""
Exercise Generator Agent
Creates 5 progressive exercises for a given week based on learning objectives.
"""

import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from orchestrator_state import Exercise, TrainerState

load_dotenv()


class ExerciseGenerator:
    """
    Generates training exercises based on learning objectives.
    Creates 5 exercises per week with progressive difficulty.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-20250805"
    
    def generate_exercises(
        self, 
        week: int, 
        objectives: list, 
        concepts: list,
        difficulty_progression: list = None
    ) -> list:
        """
        Generate 5 progressive exercises for a week.
        
        Args:
            week: Week number
            objectives: Learning objectives for the week
            concepts: Key concepts to cover
            difficulty_progression: Desired progression (beginner, intermediate, advanced)
            
        Returns:
            List of 5 Exercise dictionaries
        """
        
        if not difficulty_progression:
            difficulty_progression = ["beginner", "beginner", "intermediate", "intermediate", "advanced"]
        
        prompt = f"""
You are creating 5 progressive exercises for Week {week} of an agentic AI training program.

LEARNING OBJECTIVES:
{json.dumps([obj if isinstance(obj, dict) else {'objective': str(obj)} for obj in objectives], indent=2)}

KEY CONCEPTS:
{json.dumps(concepts)}

DIFFICULTY PROGRESSION:
{json.dumps(difficulty_progression)}

TASK:
Create exactly 5 exercises that:
1. Start easy (Exercise 1) and progress to hard (Exercise 5)
2. Each builds on the previous one
3. Covers all key concepts
4. Includes starter code
5. Has clear success criteria

EXERCISE TEMPLATE FOR EACH:
{{
    "id": "week{week}_exercise_1",
    "week": {week},
    "exercise_number": 1,
    "title": "Exercise Title",
    "difficulty": "beginner",
    "time_estimate": "30 mins",
    "description": "Clear description of what to build",
    "learning_focus": ["concept1", "concept2"],
    "starter_code": "# Starter code here\\npass",
    "requirements": [
        "Must satisfy requirement 1",
        "Must satisfy requirement 2"
    ],
    "test_cases": [
        {{
            "input": "example input",
            "expected_output_contains": ["expected", "output"],
            "description": "Test description"
        }}
    ],
    "hints": [
        {{"hint_number": 1, "hint_text": "Consider...", "show_after": "struggle"}},
        {{"hint_number": 2, "hint_text": "Try...", "show_after": "request"}}
    ],
    "bonus_challenge": "Optional bonus challenge"
}}

CREATE 5 EXERCISES with increasing difficulty.
Return ONLY valid JSON array, no other text.
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 2000
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
                return []
            
            # Parse JSON
            try:
                json_start = text_content.find('[')
                json_end = text_content.rfind(']') + 1
                json_str = text_content[json_start:json_end]
                exercises = json.loads(json_str)
                return exercises if isinstance(exercises, list) else []
            except json.JSONDecodeError:
                print(f"JSON parsing error: {text_content[:200]}")
                return []
                
        except Exception as e:
            print(f"Error generating exercises: {e}")
            return []
    
    def update_state(
        self, 
        state: TrainerState,
        difficulty_progression: list = None
    ) -> TrainerState:
        """
        Update state with generated exercises.
        """
        exercises = self.generate_exercises(
            state["week"],
            state["learning_objectives"],
            state["key_concepts"],
            difficulty_progression
        )
        
        if not exercises:
            state["errors"].append("Failed to generate exercises")
            return state
        
        state["exercises_generated"] = True
        state["exercises"] = exercises
        
        if exercises:
            state["current_exercise"] = exercises[0]
        
        state["decision_log"].append({
            "agent": "ExerciseGenerator",
            "week": state["week"],
            "exercises_created": len(exercises)
        })
        
        return state


def main():
    """Test the exercise generator"""
    generator = ExerciseGenerator()
    
    # Example objectives and concepts
    objectives = [
        {"objective": "Understand agent loops", "description": "Learn how agents reason and act"},
        {"objective": "Implement tool calling", "description": "Use Claude's tool calling API"}
    ]
    
    concepts = [
        "Agent loops",
        "Tool calling",
        "Conversation memory",
        "Function definitions"
    ]
    
    print("Generating Week 1 exercises...")
    exercises = generator.generate_exercises(1, objectives, concepts)
    
    print(f"\nGenerated {len(exercises)} exercises:")
    for ex in exercises:
        print(f"  - {ex.get('title', 'Untitled')} ({ex.get('difficulty', 'unknown')})")
    
    if exercises:
        print(f"\nFirst exercise details:")
        print(json.dumps(exercises[0], indent=2)[:500])


if __name__ == "__main__":
    main()
