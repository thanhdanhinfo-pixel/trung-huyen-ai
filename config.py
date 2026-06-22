import os
from typing import Dict, List

DRIVE_FOLDER_ID = os.getenv("DRIVE_FOLDER_ID", "")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "")

# TRUNG_HUYEN_AI_OS knowledge source model
# Format:
# KNOWLEDGE_SOURCES=drive:core_brain:<folder_id>,drive:group:<folder_id>,doc:master:<doc_id>
KNOWLEDGE_SOURCES = os.getenv("KNOWLEDGE_SOURCES", "")
MASTER_DOCUMENT_ID = os.getenv("MASTER_DOCUMENT_ID", "")
AI_SYSTEM_MODE = os.getenv("AI_SYSTEM_MODE", "observer")
AI_SYSTEM_VERSION = os.getenv("AI_SYSTEM_VERSION", "1.0.0")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

MAX_CONTEXT_CHARS = 12000

MCP_API_KEY = os.getenv("MCP_API_KEY", "")

CACHE_DIR = os.getenv("CACHE_DIR", "storage/cache")
INDEX_DIR = os.getenv("INDEX_DIR", "storage/index")

QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

QDRANT_COLLECTION = "trung_huyen_brain"


def parse_knowledge_sources() -> List[Dict[str, str]]:
    """
    Parse KNOWLEDGE_SOURCES into structured source definitions.

    Supported item format:
        drive:<name>:<id>
        doc:<name>:<id>

    Backward compatibility:
        If KNOWLEDGE_SOURCES is empty, DRIVE_FOLDER_ID is used as a drive source.
        If MASTER_DOCUMENT_ID is set, it is added as doc:master.
    """
    sources: List[Dict[str, str]] = []

    raw = (KNOWLEDGE_SOURCES or "").strip()
    if raw:
        for item in raw.split(","):
            item = item.strip()
            if not item:
                continue

            parts = item.split(":", 2)
            if len(parts) != 3:
                continue

            source_type, name, source_id = [part.strip() for part in parts]
            if not source_type or not name or not source_id:
                continue

            sources.append({
                "type": source_type,
                "name": name,
                "id": source_id,
            })

    if not sources and DRIVE_FOLDER_ID:
        sources.append({
            "type": "drive",
            "name": "default",
            "id": DRIVE_FOLDER_ID,
        })

    has_master_doc = any(
        source.get("type") == "doc" and source.get("name") == "master"
        for source in sources
    )
    if MASTER_DOCUMENT_ID and not has_master_doc:
        sources.append({
            "type": "doc",
            "name": "master",
            "id": MASTER_DOCUMENT_ID,
        })

    return sources


def drive_root_sources() -> List[Dict[str, str]]:
    return [source for source in parse_knowledge_sources() if source.get("type") == "drive"]


def master_document_source() -> Dict[str, str] | None:
    for source in parse_knowledge_sources():
        if source.get("type") == "doc" and source.get("name") == "master":
            return source
    return None
