# GitHub Runtime Capability

Status: ACTIVE

Capabilities:
- list_files
- read_file
- update_file
- patch_file
- patch_batch
- move_file
- move_batch
- delete_file
- batch_commit
- cleanup_repository
- runtime_error_registry
- deployment_smoke_test
- deployment_rollback_stub
- qdrant_vector_search
- qdrant_collection_management

Governance:
- Writes require explicit approval.
- Patch preview should be preferred before commit.
- Smoke test should be run after runtime changes.
- Rollback is currently stub/not fully automated.
