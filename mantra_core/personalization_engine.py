class PersonalizationEngine:
    """
    Analyzes user behavior statistics to determine preferences.
    """
    def __init__(self):
        pass

    def get_preferences(self, stats):
        """
        Calculates preferred apps for specific intents.
        """
        preferences = {
            "most_used_apps": [],
            "intent_defaults": {}
        }

        # 1. Top Apps
        app_usage = stats.get("app_usage", {})
        sorted_apps = sorted(app_usage.items(), key=lambda x: x[1], reverse=True)
        preferences["most_used_apps"] = [app for app, count in sorted_apps[:3]]

        # 2. Intent Defaults (e.g., preferred music app)
        intent_patterns = stats.get("intent_patterns", {})
        for intent, counts in intent_patterns.items():
            best_app = max(counts.items(), key=lambda x: x[1])[0]
            preferences["intent_defaults"][intent] = best_app

        return preferences
