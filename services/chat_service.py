from __future__ import annotations

from typing import Any, Dict

from openai import OpenAI

from config import OPENAI_API_KEY, OPENAI_MODEL
from drive import search_and_read


def openai_client() -> OpenAI:
    if not OPENAI_API_KEY:
        raise RuntimeError("Missing OPENAI_API_KEY environment variable.")
    return OpenAI(api_key=OPENAI_API_KEY)


def answer_from_drive(*, question: str, limit: int, max_chars_per_file: int) -> Dict[str, Any]:
    knowledge = search_and_read(
        q=question,
        limit=limit,
        max_chars_per_file=max_chars_per_file,
    )

    context = "\n\n---\n\n".join(
        item.get("content", "")
        for item in knowledge
        if item.get("content")
    )

    sources = [
        {
            "name": item.get("name"),
            "link": item.get("webViewLink"),
            "id": item.get("id"),
            "mimeType": item.get("mimeType"),
        }
        for item in knowledge
    ]

    if not context:
        return {
            "status": "ok",
            "answer": "Chưa tìm thấy thông tin trong Google Drive.",
            "sources": sources,
        }

    system = "Bạn là AI của Trung Huyền Academy. Chỉ dùng dữ liệu trong GOOGLE DRIVE CONTEXT."
    user = f"CÂU HỎI:\n{question}\n\nGOOGLE DRIVE CONTEXT:\n{context}"

    response = openai_client().responses.create(
        model=OPENAI_MODEL,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
    )

    return {
        "status": "ok",
        "mode": "google_drive_only",
        "answer": response.output_text,
        "sources": sources,
    }
