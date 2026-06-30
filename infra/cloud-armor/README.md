# Cloud Armor Deployment Plan

Status: READY_FOR_DEPLOY

Prerequisites:
- HTTPS Load Balancer in front of Cloud Run.
- Cloud Armor security policy attached to backend service.

Recommended rules:
- /chat: 100 req/min/IP
- /rag/*: 30 req/min/IP
- /admin/*: allowlist only
- Enable Google managed WAF rules.

Note:
Cloud Armor cannot be fully activated from application code. It requires GCP infrastructure changes.
