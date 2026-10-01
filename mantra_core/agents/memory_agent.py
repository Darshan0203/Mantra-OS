from mantra_core.agents.base_agent import BaseAgent
from mantra_core.utils.vector_memory import VectorMemory
from typing import Dict, Any

class MemoryAgent(BaseAgent):
    def __init__(self, bus=None):
        super().__init__("memory", bus)
        # Traditional in-memory history
        self.history = []
        self.user_preferences = {
            "default_music_app": "spotify",
            "default_messaging_app": "whatsapp"
        }
        # New Semantic Vector Memory
        self.vector_mem = VectorMemory()
        self.stats = {
            "app_usage": {},    # {app_name: count}
            "intent_patterns": {} # {intent: {app: count}}
        }

    def update_statistics(self, action_result):
        """
        Updates usage statistics based on the last action.
        """
        app = action_result.get("app")
        intent = action_result.get("intent")

        if app and app != "unknown":
            self.stats["app_usage"][app] = self.stats["app_usage"].get(app, 0) + 1
            
            if intent:
                if intent not in self.stats["intent_patterns"]:
                    self.stats["intent_patterns"][intent] = {}
                self.stats["intent_patterns"][intent][app] = self.stats["intent_patterns"][intent].get(app, 0) + 1

    def store_lesson(self, lesson_text):
        """
        Stores a failure/success lesson in semantic memory.
        """
        if lesson_text:
            self.vector_mem.store(lesson_text, {"text": lesson_text, "type": "lesson"})

    def get_relevant_lessons(self, command):
        """
        Retrieves similar past failures/lessons for a command.
        """
        results = self.vector_mem.retrieve(command, top_k=2)
        return [res["text"] for res in results if res.get("type") == "lesson"]

    def add_to_history(self, entry):
        """
        Adds a transaction record to history and vector storage.
        """
        self.history.append(entry)
        # Store in vector DB for semantic recall (command is the index key)
        self.vector_mem.store(entry['command'], entry)

    def retrieve_semantic_context(self, current_command, top_k=2):
        """
        Retrieves relevant past interactions based on the current command.
        """
        return self.vector_mem.retrieve(current_command, top_k=top_k)

    def get_history(self, limit=5):
        return self.history[-limit:]

    def get_preferences(self):
        return self.user_preferences

    def update_preference(self, key, value):
        self.user_preferences[key] = value

    def get_memory_summary(self):
        """
        Returns a condensed summary of history and preferences for the LLM.
        """
        recent_history = self.get_history(limit=3)
        history_str = "\n".join([f"- {h['command']}" for h in recent_history])
        
        return {
            "user_preferences": self.user_preferences,
            "recent_commands": history_str if history_str else "No previous commands."
        }

    async def handle_message(self, message: Dict[str, Any]):
        """
        Processes memory requests (e.g., store fact, retrieve history).
        """
        print(f"[AGENT:memory] Received message: {message['task']}")
        pass
