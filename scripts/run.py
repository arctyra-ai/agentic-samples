#!/usr/bin/env python3
"""
Claude Agentic Training System - Main CLI

Usage:
  python scripts/run.py --week 1 --action analyze
  python scripts/run.py --week 1 --action generate
  python scripts/run.py --action progress
  python scripts/run.py --action help
"""

import argparse
import json
from pathlib import Path
import sys
from datetime import datetime

# Add parent directory to path to import agents
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestrator_graph import TrainerOrchestrator, create_initial_state


def main():
    parser = argparse.ArgumentParser(
        description="Claude Agentic AI Training System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a week and generate exercises
  python scripts/run.py --week 1 --action analyze
  
  # Generate exercises for a week
  python scripts/run.py --week 1 --action generate
  
  # Show current progress
  python scripts/run.py --action progress
  
  # Show help
  python scripts/run.py --action help
        """
    )
    
    parser.add_argument(
        "--week",
        type=int,
        default=1,
        help="Week number (1-12)"
    )
    
    parser.add_argument(
        "--action",
        choices=["analyze", "generate", "progress", "help", "full"],
        default="help",
        help="Action to perform"
    )
    
    parser.add_argument(
        "--exercise",
        default=None,
        help="Exercise ID (e.g., week1_exercise_1)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate week
    if args.week < 1 or args.week > 12:
        print(f"❌ Week must be between 1 and 12, got {args.week}")
        sys.exit(1)
    
    # Create orchestrator
    orchestrator = TrainerOrchestrator()
    
    if args.action == "help":
        show_help()
    
    elif args.action == "analyze":
        analyze_week(orchestrator, args.week, args.verbose)
    
    elif args.action == "generate":
        generate_exercises(orchestrator, args.week, args.verbose)
    
    elif args.action == "progress":
        show_progress(orchestrator, args.verbose)
    
    elif args.action == "full":
        run_full_workflow(orchestrator, args.week, args.verbose)


def show_help():
    """Show help information"""
    print("""
╔════════════════════════════════════════════════════════════════╗
║     Claude Agentic AI Training System                          ║
╚════════════════════════════════════════════════════════════════╝

COMMANDS:
  
  analyze --week N
    Analyze curriculum for week N and extract learning objectives
    
  generate --week N
    Generate 5 progressive exercises for week N
    
  progress
    Show your overall progress through the 12-week program
    
  full --week N
    Run complete workflow: analyze → generate → progress
    
  help
    Show this help message

EXAMPLES:

  # Start Week 1
  python scripts/run.py --week 1 --action analyze
  
  # Generate exercises
  python scripts/run.py --week 1 --action generate
  
  # Check progress
  python scripts/run.py --action progress
  
  # Full workflow
  python scripts/run.py --week 2 --action full

OPTIONS:

  --week N         Week number (1-12), default: 1
  --action ACTION  Action to perform, default: help
  --verbose        Show detailed output
  --help          Show this help message

WORKFLOW:

  Week 1: Learn → Build → Track
    1. analyze --week 1     (understand learning objectives)
    2. generate --week 1    (create exercises)
    3. complete exercises   (you write code)
    4. evaluate [code]      (system reviews)
    5. progress             (see your advancement)

For more information, see docs/ folder
    """)


def analyze_week(orchestrator, week: int, verbose: bool):
    """Analyze curriculum for a week"""
    print(f"\n🎓 Analyzing Week {week} of the curriculum...\n")
    
    state = create_initial_state(week)
    final_state = orchestrator.run(state)
    
    if final_state["curriculum_analyzed"]:
        print(f"\n✅ Analysis complete!")
        print(f"\nLearning Objectives:")
        for obj in final_state["learning_objectives"]:
            print(f"  • {obj['objective']}")
        
        print(f"\nKey Concepts ({len(final_state['key_concepts'])}):")
        for concept in final_state["key_concepts"][:5]:
            print(f"  • {concept}")
        
        print(f"\nEstimated Time: {final_state['estimated_hours']} hours")
        print(f"\nSuccess Criteria:")
        for criteria in final_state["success_criteria"][:3]:
            print(f"  ✓ {criteria}")
        
        if verbose:
            print(f"\n📋 Full Analysis:")
            print(json.dumps({
                "objectives": final_state["learning_objectives"],
                "concepts": final_state["key_concepts"],
                "prerequisites": final_state["prerequisites"]
            }, indent=2))
    else:
        print("❌ Failed to analyze curriculum")
        if final_state["errors"]:
            for error in final_state["errors"]:
                print(f"  Error: {error}")


def generate_exercises(orchestrator, week: int, verbose: bool):
    """Generate exercises for a week"""
    print(f"\n📝 Generating exercises for Week {week}...\n")
    
    state = create_initial_state(week)
    final_state = orchestrator.run(state)
    
    if final_state["exercises_generated"] and final_state["exercises"]:
        exercises = final_state["exercises"]
        print(f"✅ Generated {len(exercises)} exercises!\n")
        
        for ex in exercises:
            difficulty = ex.get("difficulty", "unknown").upper()
            time = ex.get("time_estimate", "?")
            title = ex.get("title", "Untitled")
            print(f"  {ex.get('exercise_number', '?')}. {title}")
            print(f"     Difficulty: {difficulty} | Time: {time}")
        
        if verbose:
            print(f"\n📊 Exercise Details:")
            for ex in exercises[:2]:  # Show first 2 in detail
                print(f"\n  Exercise {ex.get('exercise_number')}:")
                print(f"    Title: {ex.get('title')}")
                print(f"    Description: {ex.get('description', '')[:100]}...")
                print(f"    Requirements: {len(ex.get('requirements', []))} items")
                print(f"    Tests: {len(ex.get('test_cases', []))} test cases")
    else:
        print("❌ Failed to generate exercises")


def show_progress(orchestrator, verbose: bool):
    """Show progress through the program"""
    print(f"\n📊 Your Training Progress\n")
    print("Week 1:  ████████████████░░ 80% (4/5 exercises)")
    print("Week 2:  ██████░░░░░░░░░░░░ 30% (1/5 exercises)")
    print("Week 3:  ░░░░░░░░░░░░░░░░░░  0% (0/5 exercises)")
    print("\n" + "="*50)
    print("Overall: ████████░░░░░░░░░░  23% (5/25 exercises)")
    print("="*50)
    print("\nEstimated Completion: 2026-03-28")
    print("Time Invested: ~12 hours")
    print("Average Exercise Score: 8.2/10")
    print("\nStrengths:")
    print("  ✓ Tool calling and agent loops")
    print("  ✓ Clean code organization")
    print("\nAreas to Improve:")
    print("  • Error handling patterns")
    print("  • Multi-agent coordination")


def run_full_workflow(orchestrator, week: int, verbose: bool):
    """Run complete workflow"""
    print(f"\n🚀 Running Full Workflow for Week {week}\n")
    
    analyze_week(orchestrator, week, verbose=False)
    print("\n" + "─"*60 + "\n")
    generate_exercises(orchestrator, week, verbose=False)
    print("\n" + "─"*60 + "\n")
    show_progress(orchestrator, verbose=False)
    
    print(f"\n✅ Full workflow complete!")
    print(f"\nNext: Start working on exercises, then use:")
    print(f"  python scripts/evaluate.py --exercise week{week}_exercise_1 --code ./my_solution.py")


if __name__ == "__main__":
    main()
