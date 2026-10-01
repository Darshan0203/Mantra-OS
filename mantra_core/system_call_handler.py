from mantra_core.os_layer import SysCallType


class SystemCallHandler:
    """
    Translates ExecutionAgent actions into MANTRA OS system calls.
    """

    def __init__(self):
        pass

    def translate_intent(self, action_obj: dict):

        action = action_obj.get("action")

        if action == "launch_app":
            return (
                SysCallType.LAUNCH_APP,
                {
                    "app": action_obj.get("app")
                }
            )

        elif action == "search":
            return (
                SysCallType.SEARCH,
                {
                    "app": action_obj.get("app"),
                    "query": action_obj.get("query")
                }
            )

        elif action == "select_first_result":
            return (
                SysCallType.SELECT_FIRST_RESULT,
                {
                    "app": action_obj.get("app")
                }
            )

        elif action == "open_result":
            return (
                SysCallType.OPEN_RESULT,
                {
                    "app": action_obj.get("app")
                }
            )

        elif action == "get_current_url":
            return (
                SysCallType.GET_CURRENT_URL,
                {
                    "app": action_obj.get("app")
                }
            )

        elif action == "open_contact":
            return (
                SysCallType.OPEN_CONTACT,
                {
                    "app": action_obj.get("app"),
                    "contact": action_obj.get("contact")
                }
            )

        elif action == "send_message":
            return (
                SysCallType.UI_INPUT,
                {
                    "target": action_obj.get("contact"),
                    "text": action_obj.get("message")
                }
            )

        elif action == "play_music":
            return (
                SysCallType.LAUNCH_APP,
                {
                    "app": action_obj.get("app")
                }
            )

        elif action == "perform_action":

            sub_type = action_obj.get("type")

            if sub_type == "click":
                return (
                    SysCallType.UI_CLICK,
                    {
                        "target": action_obj.get("target")
                    }
                )

            elif sub_type == "input":
                return (
                    SysCallType.UI_INPUT,
                    {
                        "target": action_obj.get("target"),
                        "text": action_obj.get("text")
                    }
                )

            elif sub_type == "scroll":
                return (
                    SysCallType.UI_SCROLL,
                    {
                        "direction": action_obj.get(
                            "direction",
                            "down"
                        )
                    }
                )

        elif action == "speak":
            return (
                SysCallType.NOTIFY_USER,
                {
                    "message": action_obj.get("text")
                }
            )

        return (
            SysCallType.FETCH_DATA,
            {
                "raw": action_obj
            }
        )