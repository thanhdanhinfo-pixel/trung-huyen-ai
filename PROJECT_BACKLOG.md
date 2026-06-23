# PROJECT BACKLOG - TRUNG_HUYEN_AI_OS

Cập nhật: 2026-06-23

## Mục tiêu hiện tại

Hoàn thiện nền tảng 100% trước khi mở rộng tính năng mới.

Nguyên tắc:

- Khi người dùng nói `Duyệt`: được phép chốt quyết định và phân tích ngắn nếu cần.
- Khi người dùng nói `Action`: phải thực thi ngay, không bàn dài.
- Không thêm module mới nếu nền chưa ổn định.
- Không xóa/move file nếu chưa rà dependency.
- Mọi thay đổi có rủi ro phải có approval.
- GitHub là mã nguồn.
- Google Drive là bộ nhớ dài hạn.
- Runtime là bộ điều phối.

## Sprint: FOUNDATION LOCK

| ID | Hạng mục | Trạng thái | Tiến độ | Phụ thuộc | Ghi chú |
|---|---|---:|---:|---|---|
| F-001 | GitHub Runtime | DONE | 100% | - | Đọc/ghi/patch/commit đã hoạt động |
| F-002 | Developer Gateway | DONE | 100% | F-001 | `POST /developer/execute` là gateway duy nhất |
| F-003 | Developer Runtime | IN_PROGRESS | 85% | F-001 | Cần Action Registry + Repository Manager |
| F-004 | Workflow Engine | IN_PROGRESS | 70% | F-003 | Cần multi-step workflow hoàn chỉnh |
| F-005 | Worker Runtime | IN_PROGRESS | 45% | F-004 | Đã có internal worker runtime |
| F-006 | Repository Governance | IN_PROGRESS | 60% | F-003 | Đã có Cleanup Plan + Dependency Map |
| F-007 | System Registry | TODO | 10% | F-003,F-004 | Chưa có registry trung tâm |
| F-008 | Drive Runtime | TODO | 20% | F-003 | Cần write/move/rename/folder/sync |
| F-009 | Approval Engine | TODO | 15% | F-004 | AUTO / REVIEW / MANUAL |
| F-010 | Executive Dashboard | TODO | 0% | F-007 | Báo cáo tiến độ và sức khỏe hệ thống |

## Backlog ưu tiên gần

### B-001 — Action Registry

Trạng thái: TODO  
Mục tiêu: Runtime đăng ký action theo namespace, tránh if/else phân tán.

Các action mục tiêu:

- `github.status`
- `github.read`
- `github.patch`
- `github.verify`
- `github.rollback`
- `repository.scan`
- `repository.cleanup`
- `repository.archive`
- `repository.move`
- `repository.delete`
- `workflow.run`
- `workflow.status`
- `drive.sync`
- `drive.write`
- `registry.refresh`

### B-002 — Repository Manager

Trạng thái: TODO  
Mục tiêu: Cho Runtime có khả năng quản trị repo an toàn.

Cần có:

- scan
- dependency graph
- move
- archive
- delete
- verify
- rollback

### B-003 — System Registry

Trạng thái: TODO  
Mục tiêu: Sổ đăng ký trung tâm của toàn hệ thống.

Quản lý:

- modules
- APIs
- workers
- workflows
- reports
- Google Drive folders
- GitHub repository state
- decisions
- rules

### B-004 — Drive Runtime

Trạng thái: TODO  
Mục tiêu: Google Drive có đôi tay như GitHub.

Cần có:

- create folder
- write file
- append file
- rename
- move
- organize
- sync reports

### B-005 — Executive Dashboard

Trạng thái: TODO  
Mục tiêu: Người dùng hỏi tiến độ là có báo cáo thực tế.

Cần hiển thị:

- tiến độ sprint
- việc đang chạy
- việc bị chặn
- việc chờ duyệt
- sức khỏe hệ thống
- commit gần nhất

## Quy tắc cập nhật backlog

- Mỗi commit lớn phải cập nhật trạng thái backlog.
- Không mở sprint mới khi FOUNDATION LOCK chưa đạt 100%.
- Không xóa file root trước khi có dependency scan.
- File prototype phải archive trước, không xóa ngay.
