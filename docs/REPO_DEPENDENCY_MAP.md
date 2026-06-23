# REPO DEPENDENCY MAP

Cập nhật: 2026-06-23

## Mục tiêu

Xác định file nào đang phục vụ vận hành, file nào là module tương lai/prototype, file nào có thể dọn khỏi root.

## Lõi đang vận hành chắc chắn KEEP

Các file/thư mục này đang là nền vận hành hiện tại:

- `app.py`
- `config.py`
- `requirements.txt`
- `Dockerfile`
- `api/`
- `services/`
- `drive.py`
- `vectordb.py`
- `rag/`
- `knowledge/`
- `static/`

## Runtime mới đã thêm và cần giữ

- `services/developer_runtime.py`
- `services/workflow_engine.py`
- `services/worker_runtime.py`
- `services/github_runtime.py`
- `services/health_runtime.py`
- `services/runtime.py`
- `services/ai_runtime.py`

## File rác chắc chắn REMOVE khỏi source

Các file này không phải source code vận hành:

- `app.cpython-313.pyc`
- `config.cpython-313.pyc`
- `drive.cpython-313.pyc`
- `RUNTIME_WRITE_TEST.md`
- `TEST_GITHUB_CONNECTOR.md`

Ghi chú: `.gitignore` đã được cập nhật để ngăn chúng quay lại. Việc xóa vật lý cần dùng Git delete/commit; nếu công cụ hiện tại không hỗ trợ delete file trực tiếp thì xử lý bằng GitHub UI hoặc bổ sung delete endpoint.

## Nhóm root cần ARCHIVE trước, chưa xóa ngay

Các file này nhiều khả năng là prototype/tương lai. Không nên để ở root, nhưng chưa xóa trước khi rà import:

### AI / Agent / Governance

- `agent_orchestrator.py`
- `ai_ceo.py`
- `ai_governance.py`
- `brain_agent.py`
- `decision_engine.py`
- `goal_manager.py`
- `learning_engine.py`
- `master_planner.py`
- `multi_agent_manager.py`
- `planner_agent.py`
- `research_agent.py`
- `task_agent.py`

Đề xuất: chuyển vào `archive/prototype/agents/` hoặc gom thành tài liệu `docs/AI_AGENT_BACKLOG.md`.

### Chat / Prompt / Response

- `chat.py`
- `chat_engine.py`
- `prompt.py`
- `prompt_manager.py`
- `response.py`
- `answer_validator.py`
- `hallucination_guard.py`
- `quality_score.py`

Đề xuất: module đang dùng nên vào `services/chat/`; prototype vào `archive/prototype/chat/`.

### Memory / Knowledge / Context

- `conversation_memory.py`
- `long_term_memory.py`
- `knowledge_evolution.py`
- `knowledge_graph.py`
- `context_builder.py`
- `context_ranker.py`
- `document_cache.py`
- `document_ranker.py`
- `metadata_engine.py`

Đề xuất: module đang dùng nên vào `services/knowledge/`; prototype vào `archive/prototype/knowledge/`.

### Ops / Runtime / Workflow root-level

- `orchestrator.py`
- `workflow_engine.py`
- `task_queue.py`
- `scheduler.py`
- `runtime_health.py`
- `sync_job.py`
- `nightly_sync.py`
- `auto_reindex.py`
- `performance_monitor.py`
- `metrics.py`
- `audit_log.py`
- `logger.py`

Đề xuất: giữ bản chuẩn trong `services/`; root-level nếu trùng thì archive hoặc xóa sau khi xác minh không import.

### Security / Tooling

- `auth.py`
- `security_layer.py`
- `tool_registry.py`
- `request_middleware.py`
- `rule_engine.py`
- `exceptions.py`

Đề xuất: module đang dùng nên vào `services/security/` hoặc `services/common/`; prototype vào archive.

## Root mục tiêu sau cleanup

Root cuối cùng nên còn:

- `.gitignore`
- `README.md`
- `Dockerfile`
- `requirements.txt`
- `app.py`
- `config.py`
- `api/`
- `services/`
- `rag/`
- `knowledge/`
- `static/`
- `docs/`
- `archive/`

## Các bước tiếp theo

1. Bổ sung endpoint delete/move vào Developer Runtime để có thể xóa hoặc di chuyển file bằng workflow thay vì thao tác thủ công.
2. Dọn 5 file REMOVE chắc chắn.
3. Rà import thực tế trong `app.py`, `api/`, `services/`.
4. Archive các file prototype khỏi root.
5. Test `/health`, `/developer/workflow/status`, `/system/runtime/status`.
