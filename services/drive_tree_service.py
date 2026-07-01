from collections import Counter
from drive import list_recursive


def build_tree_summary(limit: int = 2000):
    items = list_recursive(limit=limit)
    counter = Counter()

    for item in items:
        path = item.get("path", "")
        root = path.split("/")[0] if path else "ROOT"
        counter[root] += 1

    domains = [
        {"name": name, "entries": count}
        for name, count in sorted(counter.items(), key=lambda x: x[1], reverse=True)
    ]

    return {
        "status": "ok",
        "domains": domains,
        "total_entries": len(items),
    }
