#!/usr/bin/env python3
"""Activate the Cloud Run GitHub Actions workflow using a GitHub token.

Why this exists:
The runtime token used by TRUNG_HUYEN_AI_OS may have repo contents write access
but not GitHub `workflow` permission. GitHub blocks writes to `.github/workflows/*`
without that scope. Run this script locally with a PAT that has `repo` + `workflow`.

Required env:
  GITHUB_TOKEN_WITH_WORKFLOW
  GITHUB_OWNER
  GITHUB_REPO

Optional env:
  GITHUB_BRANCH=main
"""

import base64
import os
import sys
from pathlib import Path

import requests

TOKEN = os.getenv("GITHUB_TOKEN_WITH_WORKFLOW")
OWNER = os.getenv("GITHUB_OWNER")
REPO = os.getenv("GITHUB_REPO")
BRANCH = os.getenv("GITHUB_BRANCH", "main")
SRC = Path("system/deployment/templates/deploy-cloud-run.workflow.yml")
DST = ".github/workflows/deploy-cloud-run.yml"


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    sys.exit(1)


if not TOKEN:
    fail("Missing GITHUB_TOKEN_WITH_WORKFLOW")
if not OWNER:
    fail("Missing GITHUB_OWNER")
if not REPO:
    fail("Missing GITHUB_REPO")
if not SRC.exists():
    fail(f"Template not found: {SRC}")

content = SRC.read_text(encoding="utf-8")
encoded = base64.b64encode(content.encode("utf-8")).decode("ascii")
base_url = f"https://api.github.com/repos/{OWNER}/{REPO}/contents/{DST}"
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

sha = None
get_resp = requests.get(base_url, headers=headers, params={"ref": BRANCH}, timeout=30)
if get_resp.status_code == 200:
    sha = get_resp.json().get("sha")
elif get_resp.status_code != 404:
    fail(f"Could not check existing workflow: {get_resp.status_code} {get_resp.text}")

body = {
    "message": "Activate Cloud Run deploy workflow",
    "content": encoded,
    "branch": BRANCH,
}
if sha:
    body["sha"] = sha

put_resp = requests.put(base_url, headers=headers, json=body, timeout=30)
if put_resp.status_code not in {200, 201}:
    fail(f"Could not activate workflow: {put_resp.status_code} {put_resp.text}")

print("Workflow activated:", DST)
print("Commit:", put_resp.json().get("commit", {}).get("html_url"))
print("Next: configure repository secrets GCP_PROJECT_ID and GCP_SERVICE_ACCOUNT_JSON, then run the workflow.")
