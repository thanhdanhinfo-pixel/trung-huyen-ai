import os

DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "") 
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN_SM") or os.getenv("GOOGLE_REFRESH_TOKEN", "")

AI_SYSTEM_MODE = os.getenv("AI_SYSTEM_MODE", "observer")
AI_SYSTEM_VERSION = os.getenv("AI_SYSTEM_VERSION", "1.0.0")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY_SM") or os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

MAX_CONTEXT_CHARS = 12000

MCP_API_KEY = os.getenv("MCP_API_KEY", "")

CACHE_DIR = os.getenv("CACHE_DIR", "storage/cache")
INDEX_DIR = os.getenv("INDEX_DIR", "storage/index")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY_SM") or os.getenv("QDRANT_API_KEY")

QDRANT_COLLECTION = "trung_huyen_brain"
