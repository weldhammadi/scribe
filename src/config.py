import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

STT_MODEL = "whisper-large-v3-turbo"
#STT_LANGUAGE = "fr"

LLM_MODEL = "llama-3.3-70b-versatile"
LLM_TEMPERATURE = 0.2
LLM_MAX_TOKENS = 1024

SYSTEM_PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "system_prompt.txt"


def require_api_key() -> str:
    if not GROQ_API_KEY:
        sys.exit(
            "Clé API Groq manquante : renseignez GROQ_API_KEY dans un fichier .env "
            "(voir .env.example)."
        )
    return GROQ_API_KEY


def get_client() -> Groq:
    return Groq(api_key=require_api_key())

if __name__ == "__main__":
    print("GROQ_API_KEY:", require_api_key())