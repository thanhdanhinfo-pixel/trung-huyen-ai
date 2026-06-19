from datetime import datetime


def create_markdown(
    title: str,
    content: str,
    author: str = "Trung Huyền",
    knowledge_type: str = "principle",
    status: str = "draft",
):
    today = datetime.now().strftime("%Y-%m-%d")

    return f"""---
title: {title}
author: {author}
created: {today}
version: 1.0
status: {status}
type: {knowledge_type}

tags:
- AI Brain
---

# {title}

{content}
"""
