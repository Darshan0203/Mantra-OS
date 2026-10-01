# Entry point for the command processing logic
# This follows the expected project structure.

from mantra_core.orchestrator import Orchestrator

class CommandProcessor:
    def __init__(self):
        self.orchestrator = Orchestrator()

    async def process(self, command: str):
        return await self.orchestrator.run(command)
