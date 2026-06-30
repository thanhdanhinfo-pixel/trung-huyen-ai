# Trust Boundaries

## Zone A - Trusted Core
- Action Registry
- Security Guard
- System Security Modules
- Capability Registry

Requirements:
- Audit enabled
- Founder authorization
- Dual approval for high-risk actions

## Zone B - Internal Services
- Cloud Run runtime
- Qdrant
- Google Drive integration
- Bootstrap services

Requirements:
- Least privilege IAM
- Secret Manager only

## Zone C - External Providers
- OpenAI API
- GitHub API
- Google APIs

Requirements:
- Timeouts
- Retries
- Audit correlation IDs

## Failure Propagation
GitHub outage -> write operations degraded only.
Qdrant outage -> semantic search degraded only.
OpenAI outage -> chat completion degraded only.
Drive outage -> knowledge retrieval degraded only.

Core control plane must remain operational.
