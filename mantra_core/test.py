import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv(
    "D:/MantraOS/mantra_core/.env",
    override=True
)

key = os.getenv("GROQ_API_KEY")

print("Key found:", key is not None)
print("Prefix:", key[:4] if key else "NONE")
print("Length:", len(key) if key else 0)

client = Groq(api_key=key)

models = client.models.list()

print("GROQ CONNECTION OK")
print("Models:", len(models.data))