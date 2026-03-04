#!/usr/bin/env python3
"""
Week 12: Test Scenarios for Software Dev Agent System
5 realistic scenarios testing different system behaviors.
"""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "week7"))

try:
    from software_dev_agents import run_software_dev_system
    AVAILABLE = True
except ImportError as e:
    AVAILABLE = False
    IMPORT_ERROR = str(e)


class SoftwareDevScenarios:
    """Test realistic scenarios"""

    @staticmethod
    def scenario_1_simple():
        """Simple feature - expected: no conflicts, smooth approval"""
        return run_software_dev_system(
            "Add ability to mark tasks as high priority"
        )

    @staticmethod
    def scenario_2_complex():
        """Complex feature - expected: multiple dependencies, more agents involved"""
        return run_software_dev_system(
            "Implement user authentication with OAuth2, email verification, "
            "and role-based access control"
        )

    @staticmethod
    def scenario_3_conflict():
        """Security conflict - expected: Security REJECT triggers human review"""
        return run_software_dev_system(
            "Add public API endpoint without authentication"
        )

    @staticmethod
    def scenario_4_performance():
        """Performance concern - expected: QA raises performance flag"""
        return run_software_dev_system(
            "Add search across 10M tasks with regex matching"
        )

    @staticmethod
    def scenario_5_failure():
        """Edge case - expected: graceful handling of empty requirement"""
        return run_software_dev_system("")


def run_all_scenarios():
    """Run all test scenarios and report results"""
    if not AVAILABLE:
        print(f"Cannot run scenarios: {IMPORT_ERROR}")
        return []

    scenarios = [
        ("1. Simple Feature", SoftwareDevScenarios.scenario_1_simple),
        ("2. Complex Feature", SoftwareDevScenarios.scenario_2_complex),
        ("3. Security Conflict", SoftwareDevScenarios.scenario_3_conflict),
        ("4. Performance Concern", SoftwareDevScenarios.scenario_4_performance),
        ("5. Failure/Edge Case", SoftwareDevScenarios.scenario_5_failure),
    ]

    results = []
    for name, scenario_func in scenarios:
        try:
            result = scenario_func()
            approval = result.get("voting_result", {}).get("result", "N/A")
            human = result.get("human_decision", "N/A")
            n_votes = len(result.get("votes", []))
            n_log = len(result.get("decision_log", []))

            results.append({
                "scenario": name,
                "status": "PASS",
                "approval": approval,
                "human_decision": human,
                "votes": n_votes,
                "log_entries": n_log
            })
        except Exception as e:
            results.append({
                "scenario": name,
                "status": "FAIL",
                "error": str(e)
            })

    return results


def print_results(results):
    """Pretty-print scenario results"""
    print("\n" + "=" * 70)
    print("  SOFTWARE DEV AGENT SYSTEM - SCENARIO TEST RESULTS")
    print("=" * 70)

    for r in results:
        if r["status"] == "PASS":
            icon = "PASS"
            print(f"\n  [{icon}] {r['scenario']}")
            print(f"         Voting: {r['approval']} | Human: {r['human_decision']}")
            print(f"         Votes: {r['votes']} | Log entries: {r['log_entries']}")
        else:
            icon = "FAIL"
            print(f"\n  [{icon}] {r['scenario']}")
            print(f"         Error: {r['error']}")

    # Summary
    passed = sum(1 for r in results if r["status"] == "PASS")
    total = len(results)
    print(f"\n{'='*70}")
    print(f"  SUMMARY: {passed}/{total} scenarios passed")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    results = run_all_scenarios()
    print_results(results)
