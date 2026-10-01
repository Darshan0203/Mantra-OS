import json

def format_response(status, data=None, error=None):
    return {
        "status": status,
        "result": data,
        "error": error
    }

def log_event(event_name, details):
    print(f"[MANTRA OS] {event_name}: {json.dumps(details, indent=2)}")
