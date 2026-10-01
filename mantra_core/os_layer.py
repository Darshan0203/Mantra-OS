from enum import Enum
from typing import Dict, Any, List
import subprocess


class SysCallType(Enum):
    LAUNCH_APP = "SYSCALL_LAUNCH_APP"
    UI_CLICK = "SYSCALL_UI_CLICK"
    UI_INPUT = "SYSCALL_UI_INPUT"
    UI_SCROLL = "SYSCALL_UI_SCROLL"

    SEARCH = "SYSCALL_SEARCH"
    SELECT_FIRST_RESULT = "SYSCALL_SELECT_FIRST_RESULT"
    OPEN_RESULT = "SYSCALL_OPEN_RESULT"
    GET_CURRENT_URL = "SYSCALL_GET_CURRENT_URL"
    OPEN_CONTACT = "SYSCALL_OPEN_CONTACT"

    FETCH_DATA = "SYSCALL_FETCH_DATA"
    NOTIFY_USER = "SYSCALL_NOTIFY_USER"


class OSLayer:
    """
    MANTRA OS Kernel.
    Routes system calls to Android through ADB.
    """

    APP_PACKAGES = {
        "whatsapp": "com.whatsapp",
        "chrome": "com.android.chrome",
        "instagram": "com.instagram.android",
        "settings": "com.android.settings",
    }

    def __init__(self):
        self.call_history: List[Dict[str, Any]] = []

    def _adb(self, *args):
        command = ["adb", *args]

        print("[ADB]", " ".join(command))

        result = subprocess.run(
            command,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"ADB command failed:\n{result.stderr.strip()}"
            )

        return result.stdout.strip()

    async def execute_syscall(
        self,
        call_type: SysCallType,
        arguments: Dict[str, Any]
    ):
        print(
            f"[KERNEL] Executing "
            f"{call_type.value} "
            f"with args: {arguments}"
        )

        self.call_history.append({
            "type": call_type.value,
            "args": arguments
        })

        if call_type == SysCallType.LAUNCH_APP:
            app = arguments.get("app")

            package_name = self.APP_PACKAGES.get(
                str(app).lower()
            )

            if not package_name:
                return {
                    "status": "failed",
                    "error": f"Unknown Android app: {app}"
                }

            self._adb(
                "shell",
                "am",
                "force-stop",
                package_name
            )

            self._adb(
                "shell",
                "monkey",
                "-p",
                package_name,
                "1"
            )

            return {
                "status": "success",
                "action": "launch_app",
                "app_name": app,
                "package": package_name
            }

        if call_type == SysCallType.SEARCH:
            return {
                "status": "success",
                "action": "search",
                "app": arguments.get("app"),
                "query": arguments.get("query")
            }

        if call_type == SysCallType.SELECT_FIRST_RESULT:
            return {
                "status": "success",
                "action": "select_first_result",
                "app": arguments.get("app")
            }

        if call_type == SysCallType.OPEN_RESULT:
            return {
                "status": "success",
                "action": "open_result",
                "app": arguments.get("app")
            }

        if call_type == SysCallType.GET_CURRENT_URL:
            return {
                "status": "success",
                "action": "get_current_url",
                "app": arguments.get("app")
            }

        if call_type == SysCallType.OPEN_CONTACT:
            return {
                "status": "success",
                "action": "open_contact",
                "app": arguments.get("app"),
                "contact": arguments.get("contact")
            }

        if call_type == SysCallType.UI_CLICK:
            return {
                "status": "success",
                "action": "perform_action",
                "type": "click",
                "target": arguments.get("target")
            }

        if call_type == SysCallType.UI_INPUT:
            return {
                "status": "success",
                "action": "perform_action",
                "type": "input",
                "target": arguments.get("target"),
                "text": arguments.get("text")
            }

        if call_type == SysCallType.UI_SCROLL:
            return {
                "status": "success",
                "action": "perform_action",
                "type": "scroll",
                "direction": arguments.get(
                    "direction",
                    "down"
                )
            }

        if call_type == SysCallType.NOTIFY_USER:
            return {
                "status": "success",
                "action": "speak",
                "text": arguments.get("message")
            }

        return {
            "status": "failed",
            "error": f"Unsupported system call: {call_type}"
        }

    def get_audit_log(self):
        return self.call_history