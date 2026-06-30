# Technical Debt Register

## Resolved
- Unified Security Guard integrated into Action Registry.
- Emergency Mode implemented.
- Dual Approval framework implemented.
- High-Risk Audit Trail implemented.
- Startup and router modularization completed.

## Remaining Debt

### TD-001: app.py decomposition
Severity: Low
Risk: Low
Status: Planned (APP-DECOMPOSITION-V2)

Phases:
1. drive routes
2. rag routes
3. chat routes
4. system routes
5. actions routes
6. create_app() final cutover

Exit Criteria:
- app.py < 200 LOC
- zero import cycles
- smoke tests green

### TD-002: GitHub Branch Protection
Severity: Medium
Blocked By: missing infrastructure capability
Required Capability:
- github_set_branch_protection

### TD-003: IAM Least Privilege
Severity: Medium
Blocked By: missing infrastructure capability
Required Capability:
- gcp_get_iam_policy
- gcp_update_iam_binding

### TD-004: Secret Manager Hardening
Severity: Medium
Blocked By: missing infrastructure capability
Required Capability:
- secret_manager_upsert

## Policy
No critical debt may remain unresolved in production.
