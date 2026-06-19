from datetime import datetime


def create_markdown(
    title: str,
    content: str,
    author: str = "Trung Huyền",
    knowledge_type: str = "Principle",
    status: str = "draft",
    version: str = "1.0",
    tags: list[str] | None = None,
):
    if tags is None:
        tags = ["AI Brain"]

    today = datetime.now().strftime("%Y-%m-%d")

    tag_text = "\n".join(f"- {tag}" for tag in tags)

    return f"""---
title: {title}
author: {author}
created: {today}
version: {version}
status: {status}
type: {knowledge_type}

tags:
{tag_text}
---

# {title}

{content}
"""
