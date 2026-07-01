# ARCHITECTURE REPORT - CLEAN CORE 

Cập nhật: 2026-06-23

## Mục tiêu

Tinh gọn, trôi êm, ổn định và mạnh. Không mở rộng tính năng cho đến khi nền tảng sạch hơn.

## Kết quả rà soát ban đầu

### 1. Vấn đề rõ ràng cần xử lý

- Có file biên dịch Python trong repository:
  - `app.cpython-313.pyc`
  - `config.cpython-313.pyc`
  - `drive.cpython-313.pyc`
- Có file test tạm còn nằm ở root:
  - `RUNTIME_WRITE_TEST.md`
  - `TEST_GITHUB_CONNECTOR.md`
- `app.py` đang quá lớn và chứa nhiều trách nhiệm.
- Có nhiều module gốc nhỏ, rời rạc, có nguy cơ là prototype hoặc code chết.
- Đã có thư mục `api/` và `services/`, nhưng root vẫn còn nhiều service/module rải rác.

### 2. Nguyên tắc xử lý

Không xóa ngay nếu chưa xác minh dependency.

Mỗi file được phân loại theo 4 nhãn:

- KEEP: giữ.
- MERGE: gộp vào module đúng trách nhiệm.
- REMOVE: loại bỏ sau khi xác minh không dùng.
- REFACTOR: chuẩn hóa lại.

## Phân loại bước 1

### REMOVE CANDIDATE

Các file này nên loại bỏ khỏi repo sau khi xác nhận không được import:

- `app.cpython-313.pyc`
- `config.cpython-313.pyc`
- `drive.cpython-313.pyc`
- `RUNTIME_WRITE_TEST.md`
- `TEST_GITHUB_CONNECTOR.md`

Lý do:

- `.pyc` không nên commit vào source code.
- File test tạm làm repo nhiễu và giảm độ chuyên nghiệp.

### REFACTOR CANDIDATE

- `app.py`
- `drive.py`
- `mcp.py`
- `workflow_engine.py`
- `orchestrator.py`
- `task_queue.py`
- `scheduler.py`
- `runtime_health.py`

Lý do:

- Các trách nhiệm còn phân tán.
- Cần gom về Runtime Core hoặc adapter rõ ràng.

### KEEP CANDIDATE

- `config.py`
- `requirements.txt`
- `Dockerfile`
- `README.md`
- `api/`
- `services/`
- `static/`
- `knowledge/`
- `rag/`

Lý do:

- Đây là lõi đang phục vụ vận hành hiện tại.

## Điểm nghẽn thực tế

1. `app.py` chưa phải bootstrap thuần.
2. Runtime chưa có Workflow Runner đủ mạnh.
3. Memory/Executive State chưa có một nơi duy nhất để tra cứu.
4. Google Drive chưa được dùng làm OS_DATA vận hành.
5. Repo có nhiều file root nhỏ làm tăng độ nhiễu kiến trúc.

## Hành động tiếp theo

### Bước A - Dọn rác an toàn

- Thêm `.gitignore` để chặn `.pyc`, `__pycache__`, file tạm.
- Loại bỏ các file test tạm và `.pyc` sau khi xác nhận không cần.

### Bước B - Lập dependency report

- Rà soát import giữa các file root.
- Xác định file nào thực sự được app sử dụng.

### Bước C - Thu gọn `app.py`

- Không big-bang rewrite.
- Tách router đã ổn định trước.
- Chỉ xóa logic khỏi `app.py` khi router mới đã pass test.

### Bước D - Runtime Core

- Gộp Task Queue, Scheduler, Workflow Runner vào một Runtime Core thống nhất.

## Trạng thái mục tiêu

CLEAN CORE chưa hoàn thành.

Mốc hiện tại:

- Kiểm kê root repo: hoàn thành bước đầu.
- Danh sách REMOVE CANDIDATE: đã có.
- Danh sách REFACTOR CANDIDATE: đã có.
- Cần tiếp tục: rà soát `api/` và `services/` chi tiết.
