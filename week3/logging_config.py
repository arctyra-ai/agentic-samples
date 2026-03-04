#!/usr/bin/env python3
"""
Week 3: Structured Logging for Agent Decisions
Provides event-based logging with JSON persistence for debugging agent behavior.
"""

import json
import logging
from datetime import datetime
from pathlib import Path


class StructuredLogger:
    """Structured logging for agent decisions and tool calls"""

    def __init__(self, log_file="agent_trace.json"):
        self.log_file = log_file
        self.logs = []
        self._load_existing_logs()

    def _load_existing_logs(self):
        """Load existing logs from disk"""
        if Path(self.log_file).exists():
            try:
                with open(self.log_file, 'r') as f:
                    self.logs = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.logs = []

    def log_event(self, event_type, data):
        """Log a structured event"""
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "data": data
        }
        self.logs.append(entry)
        self._save_logs()
        print(f"[LOG] {event_type}: {data}")

    def _save_logs(self):
        """Persist logs to disk"""
        with open(self.log_file, 'w') as f:
            json.dump(self.logs, f, indent=2, default=str)

    def get_trace(self, last_n=None):
        """Get decision trace for debugging"""
        if last_n:
            return self.logs[-last_n:]
        return self.logs

    def clear(self):
        """Clear all logs"""
        self.logs = []
        self._save_logs()


# Module-level logger instance
logger = StructuredLogger()


# Convenience functions
def log_user_input(user_message):
    logger.log_event("USER_INPUT", {"message": user_message})


def log_tool_call(tool_name, tool_input):
    logger.log_event("TOOL_CALL", {"tool": tool_name, "input": tool_input})


def log_tool_result(tool_name, result, success=True):
    logger.log_event("TOOL_RESULT", {
        "tool": tool_name,
        "result": str(result)[:500],  # Truncate long results
        "success": success
    })


def log_error(error_type, error_message, recovery_action):
    logger.log_event("ERROR", {
        "type": error_type,
        "message": error_message,
        "recovery": recovery_action
    })


def log_decision(reasoning, action):
    logger.log_event("DECISION", {
        "reasoning": reasoning,
        "action": action
    })
