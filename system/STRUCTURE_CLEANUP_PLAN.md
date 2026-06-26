# STRUCTURE CLEANUP PLAN

## Goal
Reduce loose files in `system/` by grouping modules into domain packages while preserving backward compatibility.

## Target package layout

```text
system/
  events/
  scheduler/
  capability/
  evolution/
  governance_pkg/
  digital_twin_pkg/
  validation/
```

## Migration rule
1. Create new package file.
2. Copy implementation into package.
3. Convert old root file into compatibility shim.
4. Update preferred imports.
5. Remove shim only after validation.

## Priority order
1. events
2. scheduler
3. capability
4. evolution
5. validation
6. governance
7. digital twin

## Status
- Package skeleton: complete
- File migration: pending
- Compatibility shims: pending
