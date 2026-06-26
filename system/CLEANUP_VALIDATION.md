# CLEANUP-4 VALIDATION

## API duplication audit

### api/repo.py
Purpose: repository refactor workflows.
Service: services.repo_refactor.
Status: KEEP.

### api/repository.py
Purpose: repository management workflows.
Service: services.repository_manager.
Status: KEEP.

Decision:
- No merge yet.
- Add documentation to distinguish responsibilities.

## Endpoint compatibility
- system_runtime.py remains compatibility layer.
- New modular routers are preferred for future development.

## Dead-code status
- No automatic deletions performed.
- Facades introduced first to avoid import breakage.

## Next cleanup wave
1. Migrate imports to facade modules.
2. Move endpoints from system_runtime.py to dedicated routers.
3. Add automated import validation tests.
4. Add endpoint duplication checks in CI.
