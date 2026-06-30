# System Connection Graph

## Control Plane

Founder
-> TRUNG_HUYEN_AI_OS
-> Action Registry
-> Security Guard
-> Execution Layer

## Knowledge Plane

Google Drive -> Retrieval -> Chat/RAG
GitHub -> Code Truth -> Runtime
Qdrant -> Vector Memory -> Search

## Infrastructure Plane

Cloud Build -> Artifact Registry -> Cloud Run
Cloud Run -> OpenAI API
Cloud Run -> Qdrant
Cloud Run -> Google Drive

## Security Boundaries

Security Guard
├── Emergency Mode
├── Dual Approval
└── High-Risk Audit

All high-risk actions must traverse this layer.
