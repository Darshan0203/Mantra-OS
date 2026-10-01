from mantra_core.agents.base_agent import BaseAgent
from typing import Dict, Any


class ExecutionAgent(BaseAgent):

    def __init__(self, bus=None):
        super().__init__("executor", bus)

    async def handle_message(self, message: Dict[str, Any]):
        """
        Handle execution tasks.
        """
        print(f"[AGENT:executor] Received message: {message.get('task')}")

        if message.get("task") == "translate_plan":
            return self.translate_to_actions(
                message.get("plan", {})
            )

        return None

    def translate_to_actions(self, plan):
        """
        Converts planner steps into explicit executable actions.

        Planner action types supported:

        launch_app
        search
        select_first_result
        open_result
        get_current_url
        open_contact
        send_message
        ui_click
        ui_type
        ui_scroll
        play_music
        speak
        """

        actions = []

        for step in plan.get("plan", []):

            action_type = str(
                step.get("action_type", "")
            ).lower().strip()

            description = str(
                step.get("description", "")
            ).strip()

            app = step.get("app")

            print(
                f"[EXECUTION AGENT] "
                f"Step {step.get('step_id')}: "
                f"{action_type}"
            )

            # ---------------------------------------------------------
            # 1. LAUNCH APP
            # ---------------------------------------------------------
            if action_type == "launch_app":

                actions.append({
                    "action": "launch_app",
                    "app": app or self._extract_app(description),
                    "intent": "open_app"
                })

            # ---------------------------------------------------------
            # 2. SEARCH
            # ---------------------------------------------------------
            elif action_type == "search":

                search_value = (
                    step.get("value")
                    or step.get("query")
                    or step.get("text")
                    or self._extract_search_query(description)
                )

                actions.append({
                    "action": "search",
                    "app": app or self._extract_app(description),
                    "query": search_value,
                    "intent": "search"
                })

            # ---------------------------------------------------------
            # 3. SELECT FIRST RESULT
            # ---------------------------------------------------------
            elif action_type == "select_first_result":

                actions.append({
                    "action": "select_first_result",
                    "app": app or self._extract_app(description),
                    "intent": "select_first_result"
                })

            # ---------------------------------------------------------
            # 4. OPEN RESULT
            # ---------------------------------------------------------
            elif action_type == "open_result":

                actions.append({
                    "action": "open_result",
                    "app": app or self._extract_app(description),
                    "intent": "open_result"
                })

            # ---------------------------------------------------------
            # 5. GET CURRENT URL
            # ---------------------------------------------------------
            elif action_type == "get_current_url":

                actions.append({
                    "action": "get_current_url",
                    "app": app or self._extract_app(description),
                    "intent": "get_current_url"
                })

            # ---------------------------------------------------------
            # 6. OPEN CONTACT
            # ---------------------------------------------------------
            elif action_type == "open_contact":

                contact = (
                    step.get("contact")
                    or self._extract_contact(description)
                )

                actions.append({
                    "action": "open_contact",
                    "app": app or "whatsapp",
                    "contact": contact,
                    "intent": "open_contact"
                })

            # ---------------------------------------------------------
            # 7. SEND MESSAGE
            # ---------------------------------------------------------
            elif action_type == "send_message":

                contact = step.get("contact")

                message = (
                    step.get("message")
                    or step.get("text")
                    or ""
                )

                actions.append({
                    "action": "send_message",
                    "app": app or "whatsapp",
                    "contact": contact,
                    "message": message,
                    "intent": "messaging"
                })

            # ---------------------------------------------------------
            # 8. UI CLICK
            # ---------------------------------------------------------
            elif action_type == "ui_click":

                target = (
                    step.get("element")
                    or step.get("target")
                    or self._extract_target(description)
                )

                actions.append({
                    "action": "perform_action",
                    "type": "click",
                    "target": target,
                    "app": app,
                    "intent": "ui_automation"
                })

            # ---------------------------------------------------------
            # 9. UI TYPE
            # ---------------------------------------------------------
            elif action_type == "ui_type":

                target = (
                    step.get("element")
                    or step.get("target")
                    or self._extract_target(description)
                )

                text = (
                    step.get("text")
                    or step.get("value")
                    or ""
                )

                actions.append({
                    "action": "perform_action",
                    "type": "input",
                    "target": target,
                    "text": text,
                    "app": app,
                    "intent": "ui_automation"
                })

            # ---------------------------------------------------------
            # 10. UI SCROLL
            # ---------------------------------------------------------
            elif action_type == "ui_scroll":

                direction = (
                    step.get("direction")
                    or "down"
                )

                actions.append({
                    "action": "perform_action",
                    "type": "scroll",
                    "direction": direction,
                    "app": app,
                    "intent": "ui_automation"
                })

            # ---------------------------------------------------------
            # 11. PLAY MUSIC
            # ---------------------------------------------------------
            elif action_type == "play_music":

                actions.append({
                    "action": "play_music",
                    "app": app or self._extract_app(description),
                    "intent": "play_music"
                })

            # ---------------------------------------------------------
            # 12. SPEAK
            # ---------------------------------------------------------
            elif action_type == "speak":

                actions.append({
                    "action": "speak",
                    "text": (
                        step.get("text")
                        or description
                    ),
                    "intent": "speak"
                })

            # ---------------------------------------------------------
            # UNKNOWN ACTION
            # ---------------------------------------------------------
            else:

                print(
                    f"[EXECUTION AGENT] "
                    f"WARNING: Unsupported action type: "
                    f"{action_type}"
                )

                actions.append({
                    "action": "info",
                    "message": description,
                    "app": app,
                    "intent": action_type
                })

        return actions

    # ================================================================
    # HELPERS
    # ================================================================

    def _extract_app(self, text):
        apps = [
            "whatsapp",
            "youtube",
            "spotify",
            "browser",
            "chrome",
            "contacts",
            "settings"
        ]

        text = text.lower()

        for app in apps:
            if app in text:
                return app

        return "unknown"

    def _extract_contact(self, text):
        """
        Basic contact extraction.

        Example:
        'Open Rahul's WhatsApp chat'
        → Rahul
        """

        text = text.replace("'s", "")
        words = text.split()

        for i, word in enumerate(words):

            if word.lower() in ("contact", "chat", "to"):
                if i + 1 < len(words):
                    return words[i + 1].strip(".,!?")

        return "unknown"

    def _extract_search_query(self, text):
        """
        Extract a simple search query from descriptions.

        Example:
        'Search YouTube for Python tutorials'
        → Python tutorials
        """

        text_lower = text.lower()

        if " for " in text_lower:
            parts = text.split(" for ", 1)

            if len(parts) == 2:
                return parts[1].strip()

        return text

    def _extract_target(self, text):
        """
        Extract UI target from descriptions.
        """

        text_lower = text.lower()

        if "click" in text_lower:

            parts = text_lower.split("click", 1)

            if len(parts) > 1:
                return parts[1].strip()

        return "unknown"


if __name__ == "__main__":

    agent = ExecutionAgent()

    sample_plan = {
        "plan": [
            {
                "step_id": 1,
                "description": "Open YouTube",
                "action_type": "launch_app",
                "app": "youtube"
            },
            {
                "step_id": 2,
                "description": "Search YouTube for Python tutorials",
                "action_type": "search",
                "app": "youtube",
                "value": "Python tutorials"
            },
            {
                "step_id": 3,
                "description": "Open the first search result",
                "action_type": "select_first_result",
                "app": "youtube"
            },
            {
                "step_id": 4,
                "description": "Get the URL of the current video",
                "action_type": "get_current_url",
                "app": "youtube"
            },
            {
                "step_id": 5,
                "description": "Open WhatsApp",
                "action_type": "launch_app",
                "app": "whatsapp"
            },
            {
                "step_id": 6,
                "description": "Open Rahul's WhatsApp chat",
                "action_type": "open_contact",
                "app": "whatsapp",
                "contact": "Rahul"
            },
            {
                "step_id": 7,
                "description": "Send the YouTube video link to Rahul",
                "action_type": "send_message",
                "app": "whatsapp",
                "contact": "Rahul",
                "message": "{{step_4.result}}"
            }
        ]
    }

    print(
        agent.translate_to_actions(sample_plan)
    )