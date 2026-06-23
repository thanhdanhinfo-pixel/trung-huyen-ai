# REPO CLEANUP PLAN

Cập nhật: 2026-06-23

## Mục tiêu

Repo phải tinh gọn, dễ vận hành, dễ mở rộng. Không để hàng trăm file prototype nằm ở root làm nhiễu hệ thống.

## Nguyên tắc xử lý

Không xóa file nghiệp vụ nếu chưa xác minh dependency.

Mỗi file được phân loại:

- KEEP: đang cần cho vận hành hiện tại.
- MOVE: cần giữ nhưng phải chuyển đúng thư mục.
- FUTURE: ý tưởng/tương lai, chưa dùng trong runtime hiện tại.
- REMOVE: rác hoặc test tạm, có thể loại bỏ.
- REVIEW: cần kiểm tra import trước khi quyết định.

## KEEP hiện tại

Các thành phần lõi đang vận hành:

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

## REMOVE chắc chắn

Các file này không nên nằm trong repository source code:

- `app.cpython-313.pyc`
- `config.cpython-313.pyc`
- `drive.cpython-313.pyc`
- `RUNTIME_WRITE_TEST.md`
- `TEST_GITHUB_CONNECTOR.md`

Lý do:

- `.pyc` là file biên dịch runtime, không phải source.
- File test tạm đã hoàn thành nhiệm vụ kiểm tra kết nối GitHub.

## REVIEW / FUTURE ở root

Nhóm AI / Agent / Governance:

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

Nhóm Chat / Prompt / Response:

- `chat.py`
- `chat_engine.py`
- `prompt.py`
- `prompt_manager.py`
- `response.py`
- `answer_validator.py`
- `hallucination_guard.py`
- `quality_score.py`

Nhóm Memory / Knowledge / Context:

- `conversation_memory.py`
- `long_term_memory.py`
- `knowledge_evolution.py`
- `knowledge_graph.py`
- `context_builder.py`
- `context_ranker.py`
- `document_cache.py`
- `document_ranker.py`
- `metadata_engine.py`

Nhóm Ops / Runtime / Workflow:

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

Nhóm Security / Tooling:

- `auth.py`
- `security_layer.py`
- `tool_registry.py`
- `request_middleware.py`
- `rule_engine.py`
- `exceptions.py`

## Quyết định chuẩn hóa

### Giai đoạn 1: Dọn rác chắc chắn

Xóa `.pyc` và file test tạm.

### Giai đoạn 2: Không để prototype nằm ở root

Các file FUTURE không xóa ngay. Chuyển vào:

- `archive/future_modules/`

hoặc gom vào tài liệu:

- `ARCHITECTURE_BACKLOG.md`

### Giai đoạn 3: Giữ root tối thiểu

Root cuối cùng chỉ nên còn:

- `app.py`
- `config.py`
- `requirements.txt`
- `Dockerfile`
- `.gitignore`
- `README.md`
- `api/`
- `services/`
- `rag/`
- `knowledge/`
- `static/`

## Việc tiếp theo

1. Xóa REMOVE chắc chắn.
2. Kiểm tra import từ `app.py`, `api/`, `services/` vào các file root.
3. File không được import nhưng có giá trị ý tưởng thì chuyển sang archive.
4. File không có giá trị thì xóa.
