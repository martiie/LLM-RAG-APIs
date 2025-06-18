import os
from dotenv import load_dotenv

load_dotenv()

EMBED_MODEL_NAME = 'all-MiniLM-L6-v2'
DOCS_JSON = 'docs.json'
GENAI_MODEL = 'gemini-2.0-flash'
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
