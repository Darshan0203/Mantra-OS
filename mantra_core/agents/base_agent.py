from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """
    Abstract base class for all MANTRA OS agents.
    Provides standard messaging capabilities via the MessageBus.
    """
    def __init__(self, name: str, bus=None):
        self.name = name
        self.bus = bus
        if self.bus:
            self.bus.register_agent(name, self)

    async def send_message(self, to_agent: str, task: str, data: Dict[str, Any] = None):
        """
        Sends a structured message to another agent.
        """
        if self.bus:
            message = {
                "from": self.name,
                "to": to_agent,
                "task": task,
                "data": data or {}
            }
            await self.bus.send_direct(to_agent, message)
        else:
            print(f"[AGENT:{self.name}] Error: No message bus connected.")

    @abstractmethod
    async def handle_message(self, message: Dict[str, Any]):
        """
        Processes incoming messages. Must be implemented by subclasses.
        """
        pass
