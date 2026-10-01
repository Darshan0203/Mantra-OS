import os
import json

from groq import Groq
from dotenv import load_dotenv
from mantra_core.agents.base_agent import BaseAgent
from typing import Dict, Any

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(ENV_FILE, override=True)


class PlannerAgent(BaseAgent):

    def __init__(self, bus=None):
        super().__init__("planner", bus)

        self.api_key = os.getenv("GROQ_API_KEY")
        self.model = os.getenv(
            "MODEL_NAME",
            "openai/gpt-oss-20b"
        )

        self.client = (
            Groq(api_key=self.api_key)
            if self.api_key
            else None
        )

    async def handle_message(self, message: Dict[str, Any]):
        """
        Handle incoming planning requests.
        """

        print(
            f"[AGENT:planner] Received message: "
            f"{message.get('task')}"
        )

        # Implementation for direct planning requests if needed
        pass

    async def generate_plan(self, command, context, memory):

        # ---------------------------------------------------------
        # MOCK MODE
        # ---------------------------------------------------------

        if self.api_key and self.api_key.startswith("gsk_mock"):

            print(
                f"[MOCK MODE] Generating mock plan for: {command}"
            )

            return {
                "plan": [
                    {
                        "step_id": 1,
                        "description": f"Process command: {command}",
                        "action_type": "automated_action"
                    }
                ]
            }

        # ---------------------------------------------------------
        # LOCAL FALLBACK
        # ---------------------------------------------------------

        if not self.api_key:
            return self._generate_local_plan(
                command,
                context,
                memory
            )

        # ---------------------------------------------------------
        # CREATE GROQ CLIENT
        # ---------------------------------------------------------

        if not self.client:
            self.client = Groq(
                api_key=self.api_key
            )

        # ---------------------------------------------------------
        # SYSTEM PROMPT
        # IMPORTANT:
        # This MUST be outside the "if not self.client" block.
        # ---------------------------------------------------------

        system_prompt = """
You are the Advanced Planner Agent for MANTRA OS.

Your job is to convert the user's natural-language command into a
STRUCTURED, SEQUENTIAL execution plan for Android.

MANTRA OS can perform actions across multiple Android applications.
You MUST decompose complex commands into every required step.

========================
CORE PLANNING RULES
========================

1. ALWAYS DECOMPOSE MULTI-STEP TASKS

If the user asks for multiple actions, create multiple sequential
steps.

Example:

"Open YouTube, search Python tutorials, open the first video,
then open WhatsApp and send the video link to Rahul."

This MUST become a sequence similar to:

1. launch YouTube
2. search YouTube
3. select first search result
4. obtain the current video URL
5. launch WhatsApp
6. open Rahul's chat
7. send the URL

Never collapse a multi-step task into one generic action.

2. PRESERVE EXECUTION ORDER

Steps must be executed in the exact order required to complete
the user's goal.

A later step may depend on the result of an earlier step.

3. PASS DATA BETWEEN STEPS

When a later action needs information produced by an earlier action,
use a step reference.

Example:

{
    "step_id": 4,
    "action_type": "get_current_url",
    "app": "youtube"
}

Then:

{
    "step_id": 7,
    "action_type": "send_message",
    "app": "whatsapp",
    "contact": "Rahul",
    "message": "{{step_4.result}}"
}

4. USE THE CORRECT APP

If the user explicitly names an application, use that application.

Known applications include:

- youtube
- whatsapp
- spotify
- chrome
- instagram
- settings

Do not substitute another application when the user explicitly
requested one.

5. APP ACTIONS

Use these action_type values when appropriate:

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

6. SEARCH TASKS

For a search request:

launch_app
→ search
→ select_first_result/open_result

Example:

"Search YouTube for Python tutorials"

becomes:

{
    "step_id": 1,
    "description": "Open YouTube",
    "action_type": "launch_app",
    "app": "youtube"
}

{
    "step_id": 2,
    "description": "Search YouTube for Python tutorials",
    "action_type": "search",
    "app": "youtube",
    "value": "Python tutorials"
}

{
    "step_id": 3,
    "description": "Open the first search result",
    "action_type": "select_first_result",
    "app": "youtube"
}

7. CROSS-APP TASKS

When a task moves from one application to another:

- finish the required action in the first app
- capture required data
- launch the second app
- continue the task using the captured data

Example:

YouTube → get video URL → WhatsApp → send URL.

8. CONTACT TASKS

For messaging:

launch_app
→ open_contact
→ send_message

Example:

{
    "step_id": 6,
    "description": "Open Rahul's WhatsApp chat",
    "action_type": "open_contact",
    "app": "whatsapp",
    "contact": "Rahul"
}

9. MEMORY AND CONTEXT

Use SESSION CONTEXT, USER MEMORY, USER PREFERENCES, and
PAST FAILURES & LESSONS when useful.

However, never allow memory or preferences to override an
explicit application or contact specified by the user.

10. DO NOT INVENT RESULTS

The planner creates ACTIONS, not fabricated results.

For example, do not invent a YouTube URL.

Use:

get_current_url

when the URL must be obtained from the running application.

========================
OUTPUT FORMAT
========================

Return VALID JSON ONLY.

The root object MUST contain:

{
    "goal": "short description of the user's goal",
    "plan": [
        {
            "step_id": 1,
            "description": "human readable action",
            "action_type": "action",
            "app": "application"
        }
    ]
}

Additional fields such as:

value
contact
message
element

may be included when required.

Every step MUST have:

- step_id
- description
- action_type

Use app whenever the action belongs to a specific application.

Step IDs MUST start at 1 and increase sequentially.

========================
EXAMPLE
========================

User command:

"Open YouTube, search for Python tutorials, open the first video,
then open WhatsApp and send the video link to Rahul."

Output:

{
    "goal": "Send the first Python tutorial video from YouTube to Rahul on WhatsApp",
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
            "description": "Get the URL of the currently open YouTube video",
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

========================
CONTEXT
========================

SESSION CONTEXT:
[[CONTEXT]]

USER MEMORY:
[[MEMORY]]

USER PREFERENCES:
[[PREFERENCES]]

PAST FAILURES & LESSONS:
[[LESSONS]]

Return JSON only. No markdown. No explanation outside the JSON.
"""

        # ---------------------------------------------------------
        # INJECT CONTEXT
        # ---------------------------------------------------------

        full_prompt = system_prompt.replace(
            "[[CONTEXT]]",
            json.dumps(context)
        )

        full_prompt = full_prompt.replace(
            "[[MEMORY]]",
            json.dumps(memory)
        )

        full_prompt = full_prompt.replace(
            "[[PREFERENCES]]",
            json.dumps(
                context.get("preferences", {})
            )
        )

        full_prompt = full_prompt.replace(
            "[[LESSONS]]",
            json.dumps(
                context.get("past_lessons", [])
            )
        )

        # ---------------------------------------------------------
        # GROQ REQUEST
        # ---------------------------------------------------------

        try:

            response = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": full_prompt
                    },
                    {
                        "role": "user",
                        "content": command
                    }
                ],
                model=self.model,
                response_format={
                    "type": "json_object"
                }
            )

            return json.loads(
                response.choices[0].message.content
            )

        except Exception as e:

            print(
                f"[PLANNER ERROR] {e}"
            )

            return self._generate_local_plan(
                command,
                context,
                memory,
                error=str(e)
            )

    def _resolve_music_app(
        self,
        command,
        context,
        memory
    ):

        command_lower = command.lower()

        for app in ("spotify", "youtube"):

            if app in command_lower:
                return app

        intent_defaults = context.get(
            "preferences",
            {}
        ).get(
            "intent_defaults",
            {}
        )

        if intent_defaults.get("play_music"):
            return intent_defaults["play_music"]

        last_app = context.get("last_app")

        if last_app in {"spotify", "youtube"}:
            return last_app

        recent_commands = memory.get(
            "recent_commands",
            ""
        )

        for item in recent_commands.lower().splitlines():

            if "spotify" in item:
                return "spotify"

            if "youtube" in item:
                return "youtube"

        return "spotify"

    def _extract_contact(self, command):

        tokens = command.replace(
            "?",
            ""
        ).split()

        if "to" in tokens:

            idx = tokens.index("to")

            if idx + 1 < len(tokens):
                return tokens[idx + 1].strip().title()

        if "pratiksha" in command.lower():
            return "Pratiksha"

        return "Unknown"

    def _generate_local_plan(
        self,
        command,
        context,
        memory,
        error=None
    ):

        command_lower = command.lower().strip()

        plan = []

        # ---------------------------------------------------------
        # OPEN / START APP
        # ---------------------------------------------------------

        if command_lower.startswith(
            ("open ", "start ")
        ):

            app = "unknown"

            for candidate in (
                "youtube",
                "spotify",
                "whatsapp",
                "browser",
                "settings"
            ):

                if candidate in command_lower:
                    app = candidate
                    break

            plan = [
                {
                    "step_id": 1,
                    "description": f"Open {app}",
                    "action_type": "launch_app",
                    "app": app
                }
            ]

        # ---------------------------------------------------------
        # PLAY MUSIC
        # ---------------------------------------------------------

        elif (
            "play" in command_lower
            or "music" in command_lower
            or "songs" in command_lower
        ):

            app = self._resolve_music_app(
                command,
                context,
                memory
            )

            plan = [
                {
                    "step_id": 1,
                    "description": f"Play music on {app}",
                    "action_type": "play_music",
                    "app": app
                }
            ]

        # ---------------------------------------------------------
        # SEND MESSAGE
        # ---------------------------------------------------------

        elif "send" in command_lower:

            app = (
                "whatsapp"
                if "whatsapp" in command_lower
                else context.get("last_app")
                or "whatsapp"
            )

            contact = self._extract_contact(
                command
            )

            # Today's notes
            if "today's notes" in command_lower:

                plan = [
                    {
                        "step_id": 1,
                        "description": f"Open {app}",
                        "action_type": "launch_app",
                        "app": app
                    },
                    {
                        "step_id": 2,
                        "description": f"Search for {contact}",
                        "action_type": "ui_click",
                        "element": f"chat_{contact.lower()}"
                    },
                    {
                        "step_id": 3,
                        "description": (
                            f"Send today's notes to "
                            f"{contact} on {app}"
                        ),
                        "action_type": "send_message",
                        "app": app,
                        "contact": contact,
                        "message": "today's notes"
                    }
                ]

            else:

                message = (
                    "hello"
                    if (
                        "hello" in command_lower
                        or "hey" in command_lower
                    )
                    else "automated message from MANTRA OS"
                )

                plan = [
                    {
                        "step_id": 1,
                        "description": (
                            f"Send '{message}' to "
                            f"{contact} on {app}"
                        ),
                        "action_type": "send_message",
                        "app": app,
                        "contact": contact,
                        "message": message
                    }
                ]

        # ---------------------------------------------------------
        # LAST COMMAND
        # ---------------------------------------------------------

        elif "last command" in command_lower:

            recent = memory.get(
                "recent_commands",
                "No previous commands."
            )

            plan = [
                {
                    "step_id": 1,
                    "description": (
                        f"Recall recent commands: {recent}"
                    ),
                    "action_type": "speak"
                }
            ]

        # ---------------------------------------------------------
        # UNKNOWN
        # ---------------------------------------------------------

        else:

            plan = [
                {
                    "step_id": 1,
                    "description": f"Process command: {command}",
                    "action_type": "unknown"
                }
            ]

        result = {
            "plan": plan,
            "planner_backend": "local"
        }

        if error:
            result["fallback_reason"] = error

        return result


if __name__ == "__main__":

    planner = PlannerAgent()

    print(
        planner.generate_plan(
            "send hello to pratiksha on whatsapp",
            {},
            {}
        )
    )