from mantra_core.agents.base_agent import BaseAgent
from typing import Dict, Any
import time

class FeedbackManager(BaseAgent):
    """
    Captures and processes feedback from task executions.
    """
    def __init__(self, bus=None):
        super().__init__("feedback", bus)

    async def handle_message(self, message: Dict[str, Any]):
        """
        Processes feedback-related messages.
        """
        print(f"[AGENT:feedback] Received message: {message['task']}")
        pass

    def create_feedback_entry(self, command, plan, execution_result, start_time):
        """
        Creates a structured feedback entry from an execution.
        """
        duration = time.time() - start_time
        status = execution_result.get("status", "unknown")
        
        entry = {
            "command": command,
            "status": status,
            "duration": round(duration, 2),
            "plan_steps": len(plan.get("plan", [])),
            "errors": execution_result.get("error") if status == "failed" else None
        }
        
        # If it failed, extract a "Lesson"
        lesson = None
        if status == "failed":
            lesson = f"Command '{command}' failed with error: {entry['errors']}. Avoid this plan in the future."
            
        return entry, lesson
