"""
Progress Tracker Agent
Monitors user progress through the 12-week curriculum.
Provides insights, motivation, and progression guidance.
"""

import json
import os
from datetime import datetime, timedelta
from anthropic import Anthropic
from dotenv import load_dotenv
from orchestrator_state import TrainerState

load_dotenv()


class ProgressTracker:
    """
    Tracks learning progress and provides insights.
    """
    
    def __init__(self):
        self.client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        self.model = "claude-opus-4-20250805"
        self.log_file = "training_progress.json"
    
    def calculate_progress(
        self,
        week: int,
        completed_exercises: int = 0,
        exercise_scores: list = None
    ) -> dict:
        """
        Calculate progress metrics.
        
        Args:
            week: Current week
            completed_exercises: Number of exercises completed
            exercise_scores: List of scores (0-10)
            
        Returns:
            Progress metrics dictionary
        """
        
        total_exercises_by_week = 5
        completed_this_week = min(completed_exercises, total_exercises_by_week)
        completion_percent_week = (completed_this_week / total_exercises_by_week) * 100
        
        total_weeks = 12
        overall_percent = ((week - 1) * 100 / total_weeks) + (completion_percent_week / total_weeks)
        
        avg_score = sum(exercise_scores) / len(exercise_scores) if exercise_scores else 0
        
        # Estimate completion date
        hours_per_week = 10
        weeks_remaining = total_weeks - week
        days_remaining = weeks_remaining * 7
        estimated_completion = datetime.now() + timedelta(days=days_remaining)
        
        return {
            "week": week,
            "exercises_completed_this_week": completed_this_week,
            "exercises_total_this_week": total_exercises_by_week,
            "completion_percent_week": round(completion_percent_week, 1),
            "overall_percent": round(overall_percent, 1),
            "average_score": round(avg_score, 1),
            "estimated_completion_date": estimated_completion.strftime("%Y-%m-%d"),
            "weeks_remaining": weeks_remaining
        }
    
    def generate_insights(
        self,
        week: int,
        progress: dict,
        strengths: list = None,
        weaknesses: list = None,
        completed_concepts: list = None
    ) -> dict:
        """
        Generate progress insights using Claude.
        
        Args:
            week: Current week
            progress: Progress metrics
            strengths: Areas user is strong in
            weaknesses: Areas to improve
            completed_concepts: Concepts mastered
            
        Returns:
            Insights dictionary
        """
        
        progress_str = json.dumps(progress, indent=2)
        strengths_str = ", ".join(strengths) if strengths else "Not assessed"
        weaknesses_str = ", ".join(weaknesses) if weaknesses else "Not assessed"
        concepts_str = ", ".join(completed_concepts) if completed_concepts else "Not assessed"
        
        prompt = f"""
You are analyzing a user's progress through an agentic AI training program.

CURRENT PROGRESS:
{progress_str}

STRENGTHS:
{strengths_str}

AREAS TO IMPROVE:
{weaknesses_str}

CONCEPTS MASTERED:
{concepts_str}

TASK:
Generate comprehensive progress insights. Return JSON with:

1. progress_summary: Overall progress assessment
2. strengths: What user is doing well
3. areas_to_improve: Where to focus next
4. learning_velocity: Are they progressing faster or slower?
5. milestones_achieved: What they've accomplished
6. upcoming_challenges: What's next
7. recommendations: Specific guidance
8. motivational_message: Encouragement and celebration

FORMAT:
{{
    "progress_summary": "You're {percent}% complete and making good progress...",
    "strengths": ["strength1", "strength2"],
    "areas_to_improve": ["area1", "area2"],
    "learning_velocity": "increasing/steady/needs_acceleration",
    "milestones_achieved": [
        "Built your first agent",
        "Mastered tool calling"
    ],
    "upcoming_challenges": [
        "Multi-agent coordination",
        "State management at scale"
    ],
    "recommendations": [
        "Review Week X concept Y",
        "Practice pattern Z",
        "Move to harder exercises"
    ],
    "motivational_message": "Congratulations! You've made substantial progress..."
}}

Be specific, encouraging, and insightful.
Return ONLY valid JSON, no other text.
"""
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1500,
                thinking={
                    "type": "enabled",
                    "budget_tokens": 1000
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
                return {"error": "No insights generated"}
            
            # Parse JSON
            try:
                json_start = text_content.find('{')
                json_end = text_content.rfind('}') + 1
                json_str = text_content[json_start:json_end]
                insights = json.loads(json_str)
                insights["success"] = True
                return insights
            except json.JSONDecodeError:
                return {"error": "Failed to parse insights", "raw": text_content[:200]}
                
        except Exception as e:
            return {"error": f"Insights generation failed: {str(e)}"}
    
    def update_state(
        self,
        state: TrainerState,
        completed_exercises: int = 0,
        exercise_scores: list = None
    ) -> TrainerState:
        """
        Update state with progress tracking.
        """
        progress = self.calculate_progress(
            state["week"],
            completed_exercises,
            exercise_scores or []
        )
        
        state["progress"] = progress
        state["completion_percentage"] = progress["overall_percent"]
        state["estimated_completion_date"] = progress["estimated_completion_date"]
        
        # Generate insights
        insights = self.generate_insights(
            state["week"],
            progress,
            state.get("strengths", []),
            state.get("areas_to_improve", []),
            state["key_concepts"]
        )
        
        if "success" in insights:
            state["decision_log"].append({
                "agent": "ProgressTracker",
                "week": state["week"],
                "completion_percent": progress["overall_percent"],
                "average_score": progress["average_score"]
            })
        else:
            state["errors"].append("Failed to generate progress insights")
        
        return state


def main():
    """Test the progress tracker"""
    tracker = ProgressTracker()
    
    # Calculate progress
    print("Week 1 Progress:")
    progress = tracker.calculate_progress(1, 3, [8.5, 9.0, 8.2])
    print(json.dumps(progress, indent=2))
    
    # Generate insights
    print("\nGenerating insights...")
    insights = tracker.generate_insights(
        1,
        progress,
        strengths=["Tool calling", "Code organization"],
        weaknesses=["Error handling"],
        completed_concepts=["Agent loops", "Tool definitions", "Conversation memory"]
    )
    
    print("\nProgress Insights:")
    print(json.dumps(insights, indent=2)[:800])


if __name__ == "__main__":
    main()
