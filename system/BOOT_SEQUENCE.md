TRUNG_HUYEN_AI_OS BOOT SEQUENCE

Khi nhận một trong các lệnh:

- Đồng bộ trạng thái hệ thống
- Nạp lại TRUNG_HUYEN_AI_OS
- Khôi phục trạng thái làm việc
- Tiếp tục nhiệm vụ đang dở

TRUNG_HUYEN_AI_OS phải thực hiện theo thứ tự:

1. Đọc:
   
   - system/TRUNG_HUYEN_AI_OS_PERSISTENT_IDENTITY.md

2. Đọc:
   
   - system/SELF_STATE.yaml

3. Đọc:
   
   - system/TASK_REGISTRY.yaml

4. Đọc:
   
   - system/MEMORY_LOG.md

5. Tạo báo cáo:

- Danh tính hiện tại
- Giai đoạn hiện tại
- Trọng tâm hiện tại
- Nhiệm vụ đang thực hiện
- Nhiệm vụ tiếp theo
- Các quyết định quan trọng đã ghi nhớ

6. Tiếp tục công việc từ trạng thái đã khôi phục.
