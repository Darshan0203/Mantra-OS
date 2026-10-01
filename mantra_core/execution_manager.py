import asyncio
import time

from mantra_core.agents.monitor_agent import MonitorAgent
from mantra_core.os_layer import OSLayer
from mantra_core.system_call_handler import SystemCallHandler
from mantra_core.browser.youtube_executor import YouTubeExecutor


class ExecutionManager:

    def __init__(self, executor, context):
        self.executor = executor
        self.context = context

        self.monitor = MonitorAgent()
        self.os = OSLayer()
        self.syscall_handler = SystemCallHandler()

        self.youtube = None

        self.timeout = 120
        self.max_retries = 2

    async def execute_plan(self, plan):

        steps = plan.get("plan", [])

        if not steps:
            return {
                "status": "failed",
                "error": "Planner returned an empty plan."
            }

        execution_results = []
        step_results = {}

        start_time = time.time()

        print(
            f"\n[EXECUTION MANAGER] "
            f"Starting autonomous loop for {len(steps)} steps..."
        )

        try:

            for step in steps:

                if time.time() - start_time > self.timeout:
                    return {
                        "status": "failed",
                        "error": "Global execution timeout reached.",
                        "completed_steps": execution_results
                    }

                step_id = step.get("step_id")
                description = step.get(
                    "description",
                    "Unknown step"
                )

                success = False
                retries = 0

                current_step = dict(step)

                current_step = self._resolve_step_references(
                    current_step,
                    step_results
                )

                while not success:

                    print(
                        f"\n  > Executing Step {step_id}: "
                        f"{description} "
                        f"(Try {retries + 1})"
                    )

                    try:

                        actions = self.executor.translate_to_actions(
                            {"plan": [current_step]}
                        )

                        if not actions:
                            raise RuntimeError(
                                f"No executable action generated "
                                f"for step {step_id}"
                            )

                        action = actions[0]

                        if (
                            isinstance(action, dict)
                            and action.get("error")
                        ):
                            raise RuntimeError(
                                action["error"]
                            )

                        print(
                            f"    [TRANSLATOR] {action}"
                        )

                        # =================================================
                        # YOUTUBE → PLAYWRIGHT
                        # =================================================

                        app = str(
                            action.get("app", "")
                        ).lower().strip()

                        if app == "youtube":

                            print(
                                "    [ROUTER] "
                                "YouTube action → Playwright"
                            )

                            raw_action = (
                                await self._execute_youtube(action)
                            )

                        # =================================================
                        # EVERYTHING ELSE → ANDROID
                        # =================================================

                        else:

                            print(
                                "    [ROUTER] "
                                f"{app or 'unknown'} action "
                                "→ Android"
                            )

                            syscall_type, syscall_args = (
                                self.syscall_handler.translate_intent(
                                    action
                                )
                            )

                            print(
                                f"    [SYSCALL] "
                                f"{syscall_type} "
                                f"{syscall_args}"
                            )

                            raw_action = (
                                await self.os.execute_syscall(
                                    syscall_type,
                                    syscall_args
                                )
                            )

                        print(
                            f"    [EXECUTION RESULT] "
                            f"{raw_action}"
                        )

                        action_result = (
                            self._build_action_result(
                                action,
                                raw_action
                            )
                        )

                        if action_result["status"] != "success":
                            raise RuntimeError(
                                action_result.get(
                                    "error",
                                    "Execution failed"
                                )
                            )

                        # =================================================
                        # MONITOR / VERIFY
                        # =================================================

                        is_ok, message = (
                            self.monitor.verify_step(
                                current_step,
                                action_result
                            )
                        )

                        print(
                            f"    [MONITOR] {message}"
                        )

                        if not is_ok:
                            raise RuntimeError(
                                f"Step verification failed: "
                                f"{message}"
                            )

                        # =================================================
                        # STEP SUCCESS
                        # =================================================

                        success = True

                        step_results[str(step_id)] = action_result

                        execution_results.append({
                            "step_id": step_id,
                            "description": description,
                            "status": "success",
                            "result": action_result.get("result"),
                            "action": action_result
                        })

                        self.context.update_context(
                            action_result
                        )

                        print(
                            f"    [SUCCESS] "
                            f"Step {step_id} completed."
                        )

                    except Exception as e:

                        print(
                            f"    [ERROR] "
                            f"Step {step_id}: {e}"
                        )

                        if retries < self.max_retries:

                            retries += 1

                            print(
                                f"    [RETRY] "
                                f"Retrying step {step_id}..."
                            )

                            await asyncio.sleep(1)

                        else:

                            print(
                                f"    [CRITICAL] "
                                f"Step {step_id} failed "
                                f"after {self.max_retries} retries."
                            )

                            return {
                                "status": "partial_success",
                                "completed_steps": execution_results,
                                "failed_step": current_step,
                                "error": str(e)
                            }

        finally:

            if self.youtube:
                try:
                    await self.youtube.close()
                except Exception as e:
                    print(
                        f"[YOUTUBE] Close error: {e}"
                    )

                self.youtube = None

        elapsed = round(
            time.time() - start_time,
            2
        )

        print(
            f"\n[EXECUTION MANAGER] "
            f"Task completed successfully "
            f"in {elapsed}s."
        )

        return {
            "status": "success",
            "results": execution_results,
            "step_results": step_results,
            "execution_time": elapsed
        }

    # ================================================================
    # YOUTUBE EXECUTION
    # ================================================================

    async def _execute_youtube(self, action):

        if self.youtube is None:

            print(
                "[YOUTUBE] Creating YouTube executor..."
            )

            self.youtube = YouTubeExecutor()

            await self.youtube.start()

        action_type = action.get("action")

        if action_type == "launch_app":

            await self.youtube.open_youtube()

            return {
                "status": "success",
                "result": "YouTube opened"
            }

        if action_type == "search":

            query = action.get("query")

            if not query:
                return {
                    "status": "failed",
                    "error": "YouTube search query is missing."
                }

            await self.youtube.search(query)

            return {
                "status": "success",
                "result": f"Search completed: {query}"
            }

        if action_type == "select_first_result":

            await self.youtube.open_first_result()

            return {
                "status": "success",
                "result": "First YouTube result opened"
            }

        if action_type == "open_result":

            await self.youtube.open_first_result()

            return {
                "status": "success",
                "result": "YouTube result opened"
            }

        if action_type == "get_current_url":

            url = await self.youtube.get_current_url()

            return {
                "status": "success",
                "result": url
            }

        return {
            "status": "failed",
            "error": (
                f"Unsupported YouTube action: "
                f"{action_type}"
            )
        }

    # ================================================================
    # REFERENCE RESOLUTION
    # ================================================================

    def _resolve_step_references(
        self,
        step,
        step_results
    ):

        def resolve_value(value):

            if isinstance(value, str):

                for step_id, result in step_results.items():

                    token = (
                        "{{step_"
                        + str(step_id)
                        + ".result}}"
                    )

                    if token in value:

                        replacement = result.get(
                            "result"
                        )

                        if replacement is None:
                            replacement = result.get(
                                "bridge_action"
                            )

                        if replacement is None:
                            replacement = result

                        value = value.replace(
                            token,
                            str(replacement)
                        )

                return value

            if isinstance(value, dict):

                return {
                    key: resolve_value(val)
                    for key, val in value.items()
                }

            if isinstance(value, list):

                return [
                    resolve_value(item)
                    for item in value
                ]

            return value

        return resolve_value(step)

    # ================================================================
    # RESULT NORMALIZATION
    # ================================================================

    def _build_action_result(
        self,
        action,
        raw_action
    ):

        result = {
            "status": "success",
            **action,
            "bridge_action": raw_action
        }

        if raw_action is None:

            result["status"] = "failed"

            result["error"] = (
                "Execution layer returned no result."
            )

        elif isinstance(raw_action, dict):

            if raw_action.get("status") in (
                "failed",
                "error"
            ):

                result["status"] = "failed"

                result["error"] = raw_action.get(
                    "error",
                    "Execution failed."
                )

            elif raw_action.get("success") is False:

                result["status"] = "failed"

                result["error"] = raw_action.get(
                    "error",
                    "Execution failed."
                )

            if "result" in raw_action:

                result["result"] = raw_action["result"]

        return result