import json

class MultiModalProcessor:
    """
    Unified entry point for various input modalities (Text, Voice, etc.)
    Normalizes inputs into a standard 'Command' object with metadata.
    """
    def __init__(self):
        pass

    def process_input(self, raw_input, modality="text"):
        """
        Normalizes raw input based on its modality.
        """
        modality = modality.lower()
        
        if modality == "voice":
            # In a real system, this might involve cleanup of ASR transcripts
            normalized_text = raw_input.strip().lower()
        elif modality == "text":
            normalized_text = raw_input.strip()
        else:
            normalized_text = str(raw_input)

        return {
            "text": normalized_text,
            "modality": modality,
            "metadata": {
                "timestamp": json.dumps(json.dumps(None)) # Placeholder for actual time if needed
            }
        }
