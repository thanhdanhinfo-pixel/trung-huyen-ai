import os
import base64
import requests

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_OWNER = os.getenv("GITHUB_OWNER")
GITHUB_REPO = os.getenv("GITHUB_REPO")
GITHUB_BRANCH = os.getenv("GITHUB_BRANCH", "main")

print("===== GITHUB CONFIG =====")
print("TOKEN:", bool(GITHUB_TOKEN))
print("OWNER:", GITHUB_OWNER)
print("REPO:", GITHUB_REPO)
print("BRANCH:", GITHUB_BRANCH)
print("=========================")

BASE = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}"


def _headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
    }


def github_list_files(path=""):
    r = requests.get(
        f"{BASE}/contents/{path}",
        headers=_headers(),
        params={"ref": GITHUB_BRANCH},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()


def github_read_file(path):
    r = requests.get(
        f"{BASE}/contents/{path}",
        headers=_headers(),
        params={"ref": GITHUB_BRANCH},
        timeout=30,
    )
    r.raise_for_status()

    data = r.json()

    return {
        "path": path,
        "sha": data["sha"],
        "content": base64.b64decode(data["content"]).decode(),
    }


def github_update_file(path, content, sha, message):
    body = {
        "message": message,
        "content": base64.b64encode(content.encode()).decode(),
        "sha": sha,
        "branch": GITHUB_BRANCH,
    }

    r = requests.put(
        f"{BASE}/contents/{path}",
        headers=_headers(),
        json=body,
        timeout=30,
    )

    r.raise_for_status()

    return r.json()
