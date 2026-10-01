import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class GroqPlannerService:
    """
    MANTRA OS Multi-Step Planner.

    Converts a natural-language command into a structured
    multi-step execution plan for the Orchestrator.
    """

    def __init__(self):
        self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError("GROQ_API_KEY is not configured")

        self.client = Groq(api_key=self.api_key)

        self.model = os.getenv(
            "MODEL_NAME",
            "llama-3.1-8b-instant"
        )

    def get_structured_plan(self, system_prompt, user_command):

        try:

            response = self.client.chat.completions.create(
                model=self.model,

                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_command
                    }
                ],

                response_format={
                    "type": "json_object"
                },

                temperature=0.1
            )

            content = response.choices[0].message.content

            plan = json.loads(content)

            # Validate the basic structure
            if not isinstance(plan, dict):
                return {
                    "error": "Planner returned invalid JSON object"
                }

            if "steps" not in plan:
                return {
                    "error": "Planner response does not contain steps",
                    "raw_plan": plan
                }

            if not isinstance(plan["steps"], list):
                return {
                    "error": "Planner steps must be a list",
                    "raw_plan": plan
                }

            # Normalize step IDs
            for index, step in enumerate(plan["steps"], start=1):

                if isinstance(step, dict):
                    step["id"] = index

            return plan

        except json.JSONDecodeError as e:

            print(f"MANTRA Planner JSON Error: {e}")

            return {
                "error": "Planner returned invalid JSON",
                "details": str(e)
            }

        except Exception as e:

            print(f"Groq API Error: {e}")

            return {
                "error": "Failed to generate plan via Groq",
                "details": str(e)
            }