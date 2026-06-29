# Rules Domain

Target modules:
- engine.py
- engine_v2.py
- policy.py

Root files remain as compatibility facades until import audit is complete.

---

# RULE-019: SYSTEM_STABILITY_GATE_AND_UNIFIED_UNLOCK

Status: ACTIVE
Owner: Founder
Scope: ALL_SYSTEM
Enforcement: BLOCK_DEPLOY_AND_BLOCK_REAL_PROJECT_EXECUTION_IF_FAIL

## Core rule

Không được deploy, merge, hoặc triển khai dự án thật nếu hệ thống chưa vượt qua SYSTEM_STABILITY_GATE.

Hệ thống phải ổn định trước khi bắt đầu triển khai công việc thật.

## Mandatory stability checks

1. import app OK
2. import api.mcp OK
3. /health OK
4. /mcp/ping OK
5. /mcp/preflight OK
6. /mcp/tools OK
7. /mcp/call(system_self_test) OK
8. backend governance checks OK
9. developer runtime checks OK

## Failure behavior

Nếu bất kỳ check nào fail:

- Không deploy.
- Không merge.
- Không triển khai dự án thật.
- Phải sửa lỗi nền trước khi tiếp tục feature/project work.

## Unified unlock command

Khi Founder nói:

```text
Mở khóa đi
```

TRUNG_HUYEN_AI_OS phải hiểu là:

```text
Mở toàn bộ các lớp khóa hiện có và tương lai trong phạm vi Founder cho phép.
```

Founder không phải biết hệ thống đang có bao nhiêu lớp khóa.
Founder không phải nói riêng từng lớp như API key, Founder Grant, system_write, audit, legacy approval hoặc future lock layer.

## Mandatory unlock behavior

Một lệnh `Mở khóa đi` phải mở hoặc đồng bộ toàn bộ các lớp:

1. MCP/API access layer
2. Founder Grant layer
3. system_write authorization layer
4. audit/logging layer
5. legacy approval compatibility layer
6. any future registered lock layer

Nếu hệ thống thêm lớp khóa mới, lớp đó bắt buộc phải đăng ký vào unified unlock flow. Không được tạo lớp khóa ẩn khiến Founder phải đoán hoặc mở thủ công nhiều lần.

## Authority model

Founder Intent > Individual Lock Implementations

Founder Grant là nguồn sự thật duy nhất cho quyền ghi. Audit là lớp log/truy vết, không được chặn thao tác đã vượt qua Founder Grant.

## Runtime verification

Runtime verification: PASSED

Firestore grant verification: PASSED

## Purpose

Chặn lỗi nền lọt vào runtime, hợp nhất cơ chế mở khóa, và bảo đảm hệ thống đủ trơn tru để triển khai dự án thật.

---

# RULE-020: CAPABILITY_DENIAL_PROHIBITION

Status: ACTIVE
Owner: Founder

## Mandatory preflight

Trước khi kết luận thiếu quyền hoặc thiếu công cụ, bắt buộc:

1. getPreflight()
2. getToolHealth()
3. đọc CAPABILITY_REGISTRY
4. thử action thực tế nếu action tồn tại.

## Forbidden statements after verification

Nếu:
- github_write = available
- runtime = available
- mcp = available
- safe_mode = false

thì cấm phát biểu:
- Tôi không có công cụ.
- Tôi không có quyền GitHub.
- Tôi không thể sửa file.
- Tôi không thể deploy.

## Required behavior

Verify → Attempt → Report Failure.

Chỉ được báo không thể thực hiện sau khi execution thực tế thất bại.
