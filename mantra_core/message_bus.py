import asyncio
from typing import Dict, List, Callable, Any

class MessageBus:
    """
    A lightweight message bus for inter-agent communication.
    Supports publish/subscribe and direct messaging.
    """
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.agents: Dict[str, Any] = {}

    def register_agent(self, name: str, agent: Any):
        """
        Registers an agent with the bus.
        """
        self.agents[name] = agent
        print(f"[BUS] Agent '{name}' registered.")

    def subscribe(self, topic: str, callback: Callable):
        """
        Subscribes a callback to a specific topic.
        """
        if topic not in self.subscribers:
            self.subscribers[topic] = []
        self.subscribers[topic].append(callback)
        print(f"[BUS] New subscription to topic: {topic}")

    async def publish(self, topic: str, message: Dict[str, Any]):
        """
        Publishes a message to all subscribers of a topic.
        """
        if topic in self.subscribers:
            tasks = [cb(message) for cb in self.subscribers[topic]]
            await asyncio.gather(*tasks)

    async def send_direct(self, to_agent: str, message: Dict[str, Any]):
        """
        Sends a direct message to a specific agent's handle_message method.
        """
        if to_agent in self.agents:
            agent = self.agents[to_agent]
            if hasattr(agent, "handle_message"):
                await agent.handle_message(message)
            else:
                print(f"[BUS] Warning: Agent '{to_agent}' has no handle_message method.")
        else:
            print(f"[BUS] Error: Agent '{to_agent}' not found.")
