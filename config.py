import os

DRIVE_FOLDER_ID=os.getenv("DRIVE_FOLDER_ID","")
GOOGLE_SERVICE_ACCOUNT_JSON=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON","")
OPENAI_API_KEY=os.getenv("OPENAI_API_KEY","")
OPENAI_MODEL=os.getenv("OPENAI_MODEL","gpt-4.1-mini")

MAX_CONTEXT_CHARS=int(os.getenv("MAX_CONTEXT_CHARS","30000"))
CACHE_DIR="storage/cache"
INDEX_DIR="storage/index"
MCP_API_KEY = os.getenv("MCP_API_KEY", "")
