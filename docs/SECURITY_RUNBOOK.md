# SECURITY RUNBOOK — TRUNG_HUYEN_AI_OS

## Security Principles

- ONE WRITE PATH
- FAIL CLOSED
- NO BACKDOORS
- AUDIT EVERYTHING
- ARCHIVE BEFORE DELETE
- FOUNDER FINAL AUTHORITY

## Write Gates

### github_update_file

Requires:

- approved_by = Founder
- approval_id
- approved_at
- reason
- audit pass

### execute_plan

Allows one of:

1. Founder Approval
2. Emergency Override
3. Founder Unlock Mode Level 3

## Founder Approval

Required payload:

```json
{
  "approved_by": "Founder",
  "approval_id": "uuid",
  "approved_at": "ISO-8601",
  "reason": "reason"
}
