#!/usr/bin/env python3
"""
Code Evaluation Script - Review solutions and provide feedback

Usage:
  python scripts/evaluate.py --exercise week1_exercise_1 --code ./solution.py
  python scripts/evaluate.py --exercise week1_exercise_1 --code ./solution.py --show-feedback
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents_code_reviewer import CodeReviewer
from agents_feedback_provider import FeedbackProvider
from orchestrator_state import TrainerState


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate your training exercise solution",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Review your code
  python scripts/evaluate.py --exercise week1_exercise_1 --code ./solution.py
  
  # Get detailed feedback
  python scripts/evaluate.py --exercise week1_exercise_1 --code ./solution.py --show-feedback
        """
    )
    
    parser.add_argument(
        "--exercise",
        required=True,
        help="Exercise ID (e.g., week1_exercise_1)"
    )
    
    parser.add_argument(
        "--code",
        required=True,
        help="Path to your code file"
    )
    
    parser.add_argument(
        "--show-feedback",
        action="store_true",
        help="Show detailed feedback and learning resources"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output with all details"
    )
    
    args = parser.parse_args()
    
    # Load code file
    code_path = Path(args.code)
    if not code_path.exists():
        print(f"❌ Code file not found: {args.code}")
        sys.exit(1)
    
    try:
        user_code = code_path.read_text()
    except Exception as e:
        print(f"❌ Error reading code file: {e}")
        sys.exit(1)
    
    # Parse exercise ID
    try:
        week = int(args.exercise.split('_')[0][4:])
    except:
        week = 1
    
    print(f"\n{'='*60}")
    print(f"CODE REVIEW: {args.exercise}")
    print(f"{'='*60}\n")
    
    # Review code
    reviewer = CodeReviewer()
    
    # Sample requirements (in real system, would come from exercise definition)
    requirements = [
        "Code must be syntactically correct",
        "Must use Claude API correctly",
        "Should have clear structure"
    ]
    
    review = reviewer.review_code(
        args.exercise,
        user_code,
        requirements,
        learning_focus=["Agent loops", "Tool calling"]
    )
    
    # Display review results
    if "error" in review:
        print(f"❌ Review failed: {review['error']}")
        sys.exit(1)
    
    # Show results
    passes = review.get("passes_tests", False)
    quality_score = review.get("code_quality_score", 0)
    
    print(f"✅ Tests: {'PASS' if passes else 'FAIL'}")
    print(f"📊 Quality Score: {quality_score}/10")
    
    if review.get("issues"):
        print(f"\n⚠️  Issues Found ({len(review['issues'])}):")
        for issue in review["issues"][:5]:
            severity = issue.get("severity", "info").upper()
            line = issue.get("line", "?")
            msg = issue.get("issue", "Unknown issue")
            print(f"  [{severity}] Line {line}: {msg}")
    
    if review.get("improvements"):
        print(f"\n💡 Improvements:")
        for improvement in review["improvements"][:3]:
            print(f"  • {improvement}")
    
    if args.show_feedback:
        print(f"\n{'─'*60}")
        print("DETAILED FEEDBACK & LEARNING")
        print(f"{'─'*60}\n")
        
        # Get feedback
        feedback_provider = FeedbackProvider()
        feedback = feedback_provider.provide_feedback(
            args.exercise,
            ["Agent loops", "Tool calling"],
            week,
            review,
            ["Agent loops", "Tool definitions", "Memory management"]
        )
        
        if not "error" in feedback:
            if "what_went_well" in feedback.get("personalized_feedback", {}):
                print(f"✅ What Went Well:")
                print(f"   {feedback['personalized_feedback']['what_went_well'][:200]}...")
            
            if "concept_explanation" in feedback.get("concept_deep_dive", {}):
                print(f"\n📚 Concept Explanation:")
                concept_title = feedback['concept_deep_dive'].get('title', 'Unknown')
                print(f"   Title: {concept_title}")
            
            if "next_steps" in feedback:
                print(f"\n➡️  Next Steps:")
                for i, step in enumerate(feedback["next_steps"][:3], 1):
                    print(f"   {i}. {step}")
            
            if "motivational_message" in feedback:
                print(f"\n🎉 {feedback['motivational_message'][:150]}...")
    
    # Summary
    print(f"\n{'='*60}")
    if passes and quality_score >= 7:
        print("✅ READY FOR NEXT EXERCISE")
    elif passes:
        print("🟡 ACCEPTABLE - Consider improvements before advancing")
    else:
        print("❌ NEEDS REVISION - Address issues and resubmit")
    print(f"{'='*60}\n")
    
    # Save review (optional)
    if args.verbose:
        review_file = Path(f"reviews/{args.exercise}_review.json")
        review_file.parent.mkdir(parents=True, exist_ok=True)
        review_file.write_text(json.dumps(review, indent=2))
        print(f"💾 Review saved to: {review_file}\n")


if __name__ == "__main__":
    main()
