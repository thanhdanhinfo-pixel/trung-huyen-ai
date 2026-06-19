from datetime import datetime


def build_markdown(item):

    today = datetime.now().strftime("%Y-%m-%d")

    return f"""---
title: {item.title}

author: {item.author}

created: {today}

version: {item.version}

type: {item.type}

tags:
{chr(10).join("- "+t for t in item.tags)}

---

# {item.title}

{item.content}
"""
