#!/usr/bin/env python3
"""
Week 2: Persistent Memory & Conversation History
TaskMemory: persistent task storage (disk-backed JSON)
ConversationMemory: conversation history management (in-memory)
"""

import json
import os
from datetime import datetime
from pathlib import Path


class TaskMemory:
    """Persistent task storage backed by JSON file"""

    def __init__(self, storage_file="tasks.json"):
        self.storage_file = storage_file
        self.tasks = self._load_tasks()
        self.next_id = max([t["id"] for t in self.tasks], default=0) + 1

    def _load_tasks(self):
        """Load tasks from disk"""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                return json.load(f)
        return []

    def _save_tasks(self):
        """Save tasks to disk"""
        with open(self.storage_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def add_task(self, title, description="", priority="medium", due_date=None):
        """Validate and add task"""
        if not title or not isinstance(title, str):
            raise ValueError("Task title must be non-empty string")
        if len(title) > 200:
            raise ValueError("Task title must be less than 200 characters")
        if any(t["title"].lower() == title.lower() for t in self.tasks):
            raise ValueError(f"Task '{title}' already exists")

        task = {
            "id": self.next_id,
            "title": title,
            "description": description,
            "priority": priority,
            "due_date": due_date,
            "completed": False,
            "created_at": datetime.now().isoformat()
        }

        self.tasks.append(task)
        self.next_id += 1
        self._save_tasks()
        return task

    def list_tasks(self, filter_by="all", sort_by="priority"):
        """List tasks with filtering and sorting"""
        filtered = self.tasks

        if filter_by == "completed":
            filtered = [t for t in filtered if t["completed"]]
        elif filter_by == "pending":
            filtered = [t for t in filtered if not t["completed"]]

        if sort_by == "priority":
            priority_order = {"high": 0, "medium": 1, "low": 2}
            filtered = sorted(filtered, key=lambda t: priority_order.get(t.get("priority", "medium"), 1))
        elif sort_by == "date":
            filtered = sorted(filtered, key=lambda t: t.get("due_date") or "")

        return filtered

    def search_tasks(self, keyword):
        """Search tasks by keyword in title or description"""
        keyword = keyword.lower()
        return [t for t in self.tasks if keyword in t["title"].lower() or keyword in t["description"].lower()]

    def mark_complete(self, task_id):
        """Mark task complete"""
        task = self._get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        task["completed"] = True
        self._save_tasks()
        return task

    def update_task(self, task_id, **kwargs):
        """Update task fields"""
        task = self._get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        allowed_fields = {"title", "description", "priority", "due_date"}
        for key in kwargs:
            if key not in allowed_fields:
                raise ValueError(f"Cannot update field '{key}'")

        task.update(kwargs)
        self._save_tasks()
        return task

    def delete_task(self, task_id):
        """Delete task by ID"""
        task = self._get_task(task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")
        self.tasks = [t for t in self.tasks if t["id"] != task_id]
        self._save_tasks()
        return task

    def _get_task(self, task_id):
        """Get task by ID"""
        for task in self.tasks:
            if task["id"] == task_id:
                return task
        return None

    def get_stats(self):
        """Get task statistics"""
        return {
            "total": len(self.tasks),
            "completed": len([t for t in self.tasks if t["completed"]]),
            "pending": len([t for t in self.tasks if not t["completed"]]),
            "high_priority": len([t for t in self.tasks if t.get("priority") == "high" and not t["completed"]])
        }


class ConversationMemory:
    """Conversation history management for LLM context"""

    def __init__(self):
        self.messages = []

    def add_message(self, role, content):
        """Add message to history"""
        self.messages.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

    def get_history(self, last_n=None):
        """Get conversation history formatted for LLM (no timestamps)"""
        history = self.messages
        if last_n:
            history = history[-last_n:]
        return [{"role": m["role"], "content": m["content"]} for m in history]

    def clear(self):
        """Clear history"""
        self.messages = []
