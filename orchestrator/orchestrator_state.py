"""
State schema for the agentic training system.
Defines the data structure that flows through all agents.
"""

from typing import TypedDict, List, Dict, Any, Optional
from datetime import datetime


class LearningObjective(TypedDict):
    """A single learning objective for a week"""
    objective: str
    description: str
    estimated_hours: float


class ExerciseHint(TypedDict):
    """A hint for an exercise"""
    hint_number: int
    hint_text: str
    show_after: str  # "struggle", "request", "always"


class TestCase(TypedDict):
    """A test case for an exercise"""
    input: str
    expected_output_contains: List[str]
    description: str


class Exercise(TypedDict):
    """A complete exercise"""
    id: str
    week: int
    exercise_number: int
    title: str
    difficulty: str  # "beginner", "intermediate", "advanced"
    time_estimate: str
    description: str
    learning_focus: List[str]
    starter_code: str
    requirements: List[str]
    test_cases: List[TestCase]
    hints: List[ExerciseHint]
    bonus_challenge: Optional[str]


class CodeReviewIssue(TypedDict):
    """An issue found in code review"""
    line: Optional[int]
    severity: str  # "low", "medium", "high"
    issue: str
    suggestion: str


class CodeReviewResult(TypedDict):
    """Results of code review"""
    exercise_id: str
    passes_tests: bool
    code_quality_score: float
    issues: List[CodeReviewIssue]
    improvements: List[str]
    score_breakdown: Dict[str, float]
    pass_fail: str


class FeedbackMessage(TypedDict):
    """A feedback message for the user"""
    what_went_well: str
    concept_explanation: str
    why_it_matters: str
    common_mistakes: List[str]
    your_mistake: Optional[str]


class LearningResource(TypedDict):
    """A learning resource"""
    type: str  # "concept", "example", "video", "article"
    title: str
    explanation: str
    example: Optional[str]


class ProgressSnapshot(TypedDict):
    """A snapshot of user's progress"""
    week: int
    exercises_completed: int
    exercises_total: int
    completion_percentage: float
    average_score: float
    trend: str
    strengths: List[str]
    areas_to_improve: List[str]


class TrainerState(TypedDict):
    """Complete state for the trainer system"""
    
    # Input/Context
    week: int
    exercise_id: str
    user_code: Optional[str]
    user_query: Optional[str]
    
    # Curriculum Analysis
    curriculum_analyzed: bool
    learning_objectives: List[LearningObjective]
    key_concepts: List[str]
    estimated_hours: float
    prerequisites: List[str]
    success_criteria: List[str]
    
    # Exercises
    exercises_generated: bool
    exercises: List[Exercise]
    current_exercise: Optional[Exercise]
    
    # Code Review
    review_completed: bool
    code_review_result: Optional[CodeReviewResult]
    
    # Feedback
    feedback_provided: bool
    feedback_message: Optional[FeedbackMessage]
    learning_resources: List[LearningResource]
    next_steps: List[str]
    
    # Progress
    progress: Optional[ProgressSnapshot]
    completion_percentage: float
    estimated_completion_date: Optional[str]
    
    # Metadata
    timestamp: str
    decision_log: List[Dict[str, Any]]
    errors: List[str]


# Type for easier reference
TrainingState = TrainerState
