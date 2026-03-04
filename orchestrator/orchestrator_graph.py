"""
LangGraph Orchestrator
Coordinates all 5 agents in a multi-agent training system.
Uses LangGraph for state management and control flow.
"""

from langgraph.graph import StateGraph, START, END
from typing import Literal
from datetime import datetime
from orchestrator_state import TrainerState
from agents_curriculum_analyzer import CurriculumAnalyzer
from agents_exercise_generator import ExerciseGenerator
from agents_code_reviewer import CodeReviewer
from agents_feedback_provider import FeedbackProvider
from agents_progress_tracker import ProgressTracker


class TrainerOrchestrator:
    """
    Orchestrates the multi-agent training system using LangGraph.
    """
    
    def __init__(self):
        self.curriculum_analyzer = CurriculumAnalyzer()
        self.exercise_generator = ExerciseGenerator()
        self.code_reviewer = CodeReviewer()
        self.feedback_provider = FeedbackProvider()
        self.progress_tracker = ProgressTracker()
        
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the LangGraph state graph.
        """
        
        # Create the graph
        builder = StateGraph(TrainerState)
        
        # Add nodes (agents)
        builder.add_node("analyze_curriculum", self._analyze_curriculum_node)
        builder.add_node("generate_exercises", self._generate_exercises_node)
        builder.add_node("review_code", self._review_code_node)
        builder.add_node("provide_feedback", self._provide_feedback_node)
        builder.add_node("track_progress", self._track_progress_node)
        builder.add_node("complete", self._complete_node)
        
        # Add edges
        builder.add_edge(START, "analyze_curriculum")
        builder.add_edge("analyze_curriculum", "generate_exercises")
        builder.add_edge("generate_exercises", "review_code")
        builder.add_edge("review_code", "provide_feedback")
        builder.add_edge("provide_feedback", "track_progress")
        builder.add_edge("track_progress", "complete")
        builder.add_edge("complete", END)
        
        return builder.compile()
    
    def _analyze_curriculum_node(self, state: TrainerState) -> TrainerState:
        """Analyze curriculum for the week"""
        print(f"\n🎓 Analyzing curriculum for Week {state['week']}...")
        
        # In production, load actual curriculum
        curriculum_context = f"Week {state['week']} curriculum content"
        
        state = self.curriculum_analyzer.update_state(state, curriculum_context)
        
        print(f"   ✓ Extracted {len(state['learning_objectives'])} learning objectives")
        return state
    
    def _generate_exercises_node(self, state: TrainerState) -> TrainerState:
        """Generate exercises based on curriculum analysis"""
        print(f"\n📝 Generating 5 exercises for Week {state['week']}...")
        
        state = self.exercise_generator.update_state(state)
        
        if state["exercises_generated"]:
            print(f"   ✓ Generated {len(state['exercises'])} exercises")
        else:
            print(f"   ✗ Failed to generate exercises")
        
        return state
    
    def _review_code_node(self, state: TrainerState) -> TrainerState:
        """Review user's code solution"""
        if not state.get("user_code"):
            print(f"\n⏭️  No code to review, skipping...")
            return state
        
        print(f"\n🔍 Reviewing code for {state['exercise_id']}...")
        
        state = self.code_reviewer.update_state(state)
        
        if state.get("code_review_result"):
            passes = state["code_review_result"].get("passes_tests", False)
            score = state["code_review_result"].get("code_quality_score", 0)
            print(f"   ✓ Review complete - Tests: {'PASS' if passes else 'FAIL'}, Quality: {score}/10")
        
        return state
    
    def _provide_feedback_node(self, state: TrainerState) -> TrainerState:
        """Provide personalized feedback"""
        if not state.get("code_review_result"):
            print(f"\n⏭️  No review results, skipping feedback...")
            return state
        
        print(f"\n💡 Providing personalized feedback...")
        
        state = self.feedback_provider.update_state(state)
        
        print(f"   ✓ Feedback provided with {len(state.get('next_steps', []))} next steps")
        
        return state
    
    def _track_progress_node(self, state: TrainerState) -> TrainerState:
        """Track overall progress"""
        print(f"\n📊 Tracking progress...")
        
        # Update with progress tracking
        state = self.progress_tracker.update_state(state, completed_exercises=1, exercise_scores=[8.0])
        
        if state.get("progress"):
            percent = state["progress"].get("overall_percent", 0)
            print(f"   ✓ Overall progress: {percent}%")
            print(f"   ✓ Estimated completion: {state['estimated_completion_date']}")
        
        return state
    
    def _complete_node(self, state: TrainerState) -> TrainerState:
        """Mark workflow as complete"""
        state["timestamp"] = datetime.now().isoformat()
        print(f"\n✅ Workflow complete!")
        return state
    
    def run(self, initial_state: TrainerState) -> TrainerState:
        """
        Run the training workflow.
        
        Args:
            initial_state: Initial trainer state
            
        Returns:
            Final state after workflow completion
        """
        print("\n" + "="*60)
        print("AGENTIC AI TRAINING SYSTEM")
        print("="*60)
        
        final_state = self.graph.invoke(initial_state)
        
        print("\n" + "="*60)
        print("WORKFLOW SUMMARY")
        print("="*60)
        print(f"Week: {final_state['week']}")
        print(f"Exercises generated: {len(final_state.get('exercises', []))}")
        print(f"Code reviewed: {final_state.get('review_completed', False)}")
        print(f"Feedback provided: {final_state.get('feedback_provided', False)}")
        print(f"Progress tracked: {final_state.get('progress') is not None}")
        print(f"Errors: {len(final_state.get('errors', []))}")
        
        return final_state


def create_initial_state(week: int, user_code: str = None) -> TrainerState:
    """Create initial state for workflow"""
    
    return TrainerState(
        week=week,
        exercise_id=f"week{week}_exercise_1",
        user_code=user_code,
        user_query=None,
        curriculum_analyzed=False,
        learning_objectives=[],
        key_concepts=[],
        estimated_hours=8,
        prerequisites=[],
        success_criteria=[],
        exercises_generated=False,
        exercises=[],
        current_exercise=None,
        review_completed=False,
        code_review_result=None,
        feedback_provided=False,
        feedback_message=None,
        learning_resources=[],
        next_steps=[],
        progress=None,
        completion_percentage=0,
        estimated_completion_date=None,
        timestamp=datetime.now().isoformat(),
        decision_log=[],
        errors=[]
    )


def main():
    """Test the orchestrator"""
    
    # Create orchestrator
    orchestrator = TrainerOrchestrator()
    
    # Test workflow 1: Analyze week + generate exercises
    print("\n🚀 Test 1: Analyze Week 1 and Generate Exercises")
    state1 = create_initial_state(week=1)
    final_state1 = orchestrator.run(state1)
    
    # Test workflow 2: With user code
    print("\n\n🚀 Test 2: Complete workflow with code review")
    sample_code = """
from anthropic import Anthropic

client = Anthropic()

def add_task(title):
    return f"Added: {title}"

# Agent loop here
"""
    
    state2 = create_initial_state(week=1, user_code=sample_code)
    state2["exercise_id"] = "week1_exercise_1"
    final_state2 = orchestrator.run(state2)
    
    # Print results
    print("\n\n📋 Final State Summary:")
    print(f"Decisions made: {len(final_state2['decision_log'])}")
    for decision in final_state2['decision_log']:
        print(f"  - {decision}")


if __name__ == "__main__":
    main()
