"""
Curriculum Analyzer Agent
Reads the training curriculum and extracts learning objectives, 
concepts, and success criteria for a given week.
"""

import json
import os
from anthropic import Anthropic
from dotenv import load_dotenv
from orchestrator_state import LearningObjective, TrainerState

load_dotenv()


class CurriculumAnalyzer:
    """
    Analyzes the training curriculum and extracts learning information.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-20250805"  # Latest Opus
    
    def analyze_week(self, week: int, curriculum_context: str = "") -> dict:
        """
        Analyze a specific week of the curriculum.
        
        Args:
            week: Week number (1-12)
            curriculum_context: Full curriculum text or file content
            
        Returns:
            Dictionary with learning objectives, concepts, success criteria
        """
        
        prompt = f"""
You are analyzing the agentic AI training curriculum.

WEEK TO ANALYZE: Week {week}

CURRICULUM CONTEXT:
{curriculum_context[:5000]}  # First 5000 chars to avoid token limit

TASK:
Extract and analyze Week {week} of the curriculum. Return a JSON object with:

1. learning_objectives: List of specific learning objectives
2. key_concepts: List of key concepts to master
3. estimated_hours: Estimated hours to complete
4. prerequisites: What must be known before this week
5. success_criteria: How to know you've mastered this week
6. exercise_difficulty_progression: How exercises should progress
7. connection_to_building: How this week connects to building the trainer system

RETURN FORMAT:
{{
    "week": {week},
    "title": "Week {week} Title",
    "learning_objectives": [
        {{"objective": "...", "description": "..."}},
        ...
    ],
    "key_concepts": ["concept1", "concept2", ...],
    "estimated_hours": 10,
    "prerequisites": ["Python 3.10+", ...],
    "success_criteria": ["Can build a working agent", ...],
    "exercise_difficulty_progression": ["beginner", "beginner", "intermediate", "intermediate", "advanced"],
    "connection_to_building": "This week you'll learn X which is crucial for building Y agent",
    "topics": ["topic1", "topic2", ...],
    "key_code_patterns": ["pattern1", "pattern2", ...]
}}

Be specific and detailed. This analysis will drive exercise generation.
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 1000  # Extended thinking
                },
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            # Extract the text response
            text_content = None
            for block in response.content:
                if block.type == "text":
                    text_content = block.text
                    break
            
            if not text_content:
                return {
                    "error": "No text response from Claude",
                    "week": week
                }
            
            # Parse JSON from response
            try:
                # Find JSON in response (it might be wrapped in text)
                json_start = text_content.find('{')
                json_end = text_content.rfind('}') + 1
                json_str = text_content[json_start:json_end]
                analysis = json.loads(json_str)
                analysis["success"] = True
                return analysis
            except json.JSONDecodeError:
                return {
                    "error": "Could not parse JSON response",
                    "week": week,
                    "raw_response": text_content[:500]
                }
                
        except Exception as e:
            return {
                "error": f"Error analyzing week: {str(e)}",
                "week": week
            }
    
    def update_state(self, state: TrainerState, curriculum_context: str) -> TrainerState:
        """
        Update trainer state with curriculum analysis.
        
        Args:
            state: Current trainer state
            curriculum_context: Full curriculum text
            
        Returns:
            Updated state with curriculum analysis
        """
        analysis = self.analyze_week(state["week"], curriculum_context)
        
        if "error" in analysis:
            state["errors"].append(analysis["error"])
            return state
        
        # Convert analysis to state format
        objectives = [
            LearningObjective(
                objective=obj.get("objective", ""),
                description=obj.get("description", ""),
                estimated_hours=state["estimated_hours"] / len(analysis.get("learning_objectives", [1]))
            )
            for obj in analysis.get("learning_objectives", [])
        ]
        
        state["curriculum_analyzed"] = True
        state["learning_objectives"] = objectives
        state["key_concepts"] = analysis.get("key_concepts", [])
        state["estimated_hours"] = analysis.get("estimated_hours", 8)
        state["prerequisites"] = analysis.get("prerequisites", [])
        state["success_criteria"] = analysis.get("success_criteria", [])
        
        state["decision_log"].append({
            "agent": "CurriculumAnalyzer",
            "week": state["week"],
            "objectives_extracted": len(objectives),
            "concepts_identified": len(state["key_concepts"])
        })
        
        return state


def main():
    """Test the curriculum analyzer"""
    analyzer = CurriculumAnalyzer()
    
    # Read curriculum
    try:
        with open("../docs/agentic_ai_training_program.md", "r") as f:
            curriculum = f.read()
    except FileNotFoundError:
        print("Note: agentic_ai_training_program.md not found")
        curriculum = "Sample curriculum context"
    
    # Analyze Week 1
    print("Analyzing Week 1...")
    result = analyzer.analyze_week(1, curriculum)
    
    print("\nWeek 1 Analysis:")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
