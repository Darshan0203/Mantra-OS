from mantra_core.agents.base_agent import BaseAgent
from typing import Dict, Any

class MonitorAgent(BaseAgent):
    """
    Agent responsible for verifying the status and success of execution steps.
    In a real-world scenario, this would check system state, UI elements, or API responses.
    """
    def __init__(self, bus=None):
        super().__init__("monitor", bus)

    async def handle_message(self, message: Dict[str, Any]):
        """
        Processes monitoring tasks.
        """
        print(f"[AGENT:monitor] Received message: {message['task']}")
        pass

    def verify_step(self, step, action_result):
        """
        Verifies if a step was successful based on the action result.
        Returns: (is_success, feedback_message)
        """
        # Simple heuristic for now: if no error in result, it's a success
        if action_result and "error" not in action_result:
            return True, f"Step '{step.get('description')}' verified successfully."
        
        error_msg = action_result.get("error", "Unknown error occurred during execution.")
        return False, f"Step failed: {error_msg}"

    def should_retry(self, step, retry_count):
        """
        Logic to decide if a failed step should be retried.
        """
        MAX_RETRIES = 2
        return retry_count < MAX_RETRIES
