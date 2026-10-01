from mantra_core.agents.planner_agent import PlannerAgent
from mantra_core.agents.execution_agent import ExecutionAgent
from mantra_core.agents.memory_agent import MemoryAgent
from mantra_core.agents.context_agent import ContextAgent
from mantra_core.execution_manager import ExecutionManager
from mantra_core.multimodal_processor import MultiModalProcessor
from mantra_core.personalization_engine import PersonalizationEngine
from mantra_core.feedback_manager import FeedbackManager
from mantra_core.message_bus import MessageBus
import time

class Orchestrator:
    def __init__(self):
        self.bus = MessageBus()
        # Initialize agents with the message bus
        self.planner = PlannerAgent(bus=self.bus)
        self.executor = ExecutionAgent(bus=self.bus)
        self.memory = MemoryAgent(bus=self.bus)
        self.context = ContextAgent(bus=self.bus)
        self.processor = MultiModalProcessor()
        self.personalization = PersonalizationEngine()
        self.feedback = FeedbackManager(bus=self.bus)
        # New Execution Manager for autonomous loops
        self.manager = ExecutionManager(self.executor, self.context)

    async def run(self, raw_command, modality="text"):
        """
        Orchestration pipeline:
        raw_input -> normalize -> plan -> execute loop -> update context/memory
        """
        # 1. Normalize Input
        processed_input = self.processor.process_input(raw_command, modality)
        command = processed_input["text"]
        start_time = time.time()

        # 2. Get context, preferences, and lessons
        current_context = self.context.get_context()
        preferences = self.personalization.get_preferences(self.memory.stats)
        lessons = self.memory.get_relevant_lessons(command)
        
        current_context["preferences"] = preferences
        current_context["past_lessons"] = lessons # Inject lessons for self-improvement
        
        memory_summary = self.memory.get_memory_summary()
        
        # 3. Planning Phase
        plan_result = await self.planner.generate_plan(command, current_context, memory_summary)
        
        if "error" in plan_result:
            return {"status": "failed", "error": plan_result["error"]}

        # 4. Execution Phase (Autonomous Loop)
        execution_result = await self.manager.execute_plan(plan_result)
        
        # 5. SELF-IMPROVEMENT LOOP: Process Feedback
        feedback_entry, lesson = self.feedback.create_feedback_entry(command, plan_result, execution_result, start_time)
        print(f"[FEEDBACK] Task: {command} | Status: {feedback_entry['status']} | Duration: {feedback_entry['duration']}s")
        
        if lesson:
            print(f"[LEARNING] New Lesson: {lesson}")
            self.memory.store_lesson(lesson)

        # 6. Post-Execution Updates
        if execution_result["status"] == "success":
            self.memory.add_to_history({
                "command": command,
                "plan": plan_result.get("plan", []),
                "actions": execution_result.get("results", []),
                "status": execution_result["status"]
            })
            for action in execution_result["results"]:
                self.memory.update_statistics(action)
                self.context.update_context(action)

        return {
            "status": execution_result["status"],
            "result": {
                "plan": plan_result,
                "actions": execution_result.get("results") or execution_result.get("completed_steps"),
                "context": self.context.get_context()
            }
        }
