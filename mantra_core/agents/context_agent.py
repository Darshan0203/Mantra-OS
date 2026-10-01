from mantra_core.agents.base_agent import BaseAgent
from typing import Dict, Any

class ContextAgent(BaseAgent):
    def __init__(self, bus=None):
        super().__init__("context", bus)
        # Current session state
        self.state = {
            "last_app": None,
            "last_action": None,
            "last_intent": None,
            "last_contact": None,
            "current_screen": "home", # Default screen
            "ui_metadata": {},        # High-level UI info (buttons, lists, etc.)
            "active_tasks": []
        }

    def update_context(self, action_result):
        """
        Updates context based on the last action performed.
        """
        if "app" in action_result:
            self.state["last_app"] = action_result["app"]
        if "action" in action_result:
            self.state["last_action"] = action_result["action"]
        if "intent" in action_result:
            self.state["last_intent"] = action_result["intent"]
        if "contact" in action_result:
            self.state["last_contact"] = action_result["contact"]
        if "screen" in action_result:
            self.state["current_screen"] = action_result["screen"]
        if "ui_metadata" in action_result:
            self.state["ui_metadata"] = action_result["ui_metadata"]

    def get_context(self):
        return self.state

    async def handle_message(self, message: Dict[str, Any]):
        """
        Processes context updates or retrieval.
        """
        print(f"[AGENT:context] Received message: {message['task']}")
        if message["task"] == "update":
            self.update_context(message["data"])

    def reset_context(self):
        self.state = {
            "last_app": None,
            "last_action": None,
            "last_contact": None,
            "active_tasks": []
        }
