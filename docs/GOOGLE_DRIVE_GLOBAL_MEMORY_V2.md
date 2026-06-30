# Google Drive Global Memory V2

## Purpose
Make Google Drive the long-term memory and knowledge source of truth for TRUNG_HUYEN_AI_OS.

## Role
Google Drive is not runtime cache. It is the Founder Knowledge Drive and Global Memory Layer.

Priority order:
1. Founder knowledge
2. Academy knowledge
3. Strategy and decisions
4. Project memory
5. Operating procedures
6. Archive

## Target Drive Structure

```text
/AI_OS
├── 00_GLOBAL_MEMORY
│   ├── identity.md
│   ├── principles.md
│   ├── decisions/
│   ├── checkpoints/
│   └── system_state/
│
├── 01_ACADEMY
│   ├── programs/
│   ├── lessons/
│   ├── frameworks/
│   └── content_assets/
│
├── 02_PROJECTS
│   ├── TRUNG_HUYEN_AI_OS/
│   ├── Digital_Twin/
│   ├── GPT_Network/
│   └── products/
│
├── 03_STRATEGY
│   ├── yearly_strategy/
│   ├── roadmaps/
│   ├── decisions/
│   └── market_notes/
│
├── 04_OPERATIONS
│   ├── SOPs/
│   ├── workflows/
│   ├── checklists/
│   └── governance/
│
└── 99_ARCHIVE
```

## Memory Types

### 1. Identity Memory
Stores who the system is, Founder authority, operating mode, source-of-truth priority.

### 2. Decision Memory
Stores major decisions, reasoning, date, owner, affected systems.

### 3. Project Memory
Stores project plans, tasks, milestones, open questions, blockers.

### 4. Academy Memory
Stores curriculum, frameworks, training content, learning paths.

### 5. Operational Memory
Stores SOPs, runbooks, incident playbooks, governance rules.

## Metadata Standard

Each important document should start with:

```yaml
---
title:
type: identity | decision | project | academy | operation | archive
owner: Founder
status: active | draft | deprecated | archived
priority: P0 | P1 | P2 | P3
created_at:
updated_at:
source_of_truth: google_drive
related_projects:
related_endpoints:
---
```

## RAG Indexing Policy

High priority:
- 00_GLOBAL_MEMORY
- 02_PROJECTS/TRUNG_HUYEN_AI_OS
- 03_STRATEGY
- 04_OPERATIONS/governance

Medium priority:
- 01_ACADEMY
- 02_PROJECTS/*

Low priority:
- 99_ARCHIVE

## Retrieval Rules

When answering Founder questions about history, strategy, Academy, decisions, or project context:
1. Prefer /system/khoi-dong for current system state.
2. Prefer Google Drive for long-term knowledge.
3. Prefer GitHub for code truth.
4. Do not rely only on conversation memory.

## Integration Endpoints

Current backend endpoints:
- /drive/files
- /drive/search
- /drive/read
- /drive/read-path
- /drive/list-path
- /drive/search-read
- /rag/search
- /rag/index
- /rag/count

## Next Implementation Steps

1. Create Drive folder map in Google Drive.
2. Create seed documents for 00_GLOBAL_MEMORY.
3. Add Drive memory manifest to repository.
4. Rebuild Drive path index.
5. Run RAG indexing for high-priority folders.
6. Validate retrieval with sample Founder questions.

## Deferred
Redis is deferred. It is runtime RAM, not long-term memory. Google Drive remains the priority memory layer.
