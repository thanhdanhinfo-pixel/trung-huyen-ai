# Repository Intelligence

Run locally:

```bash
python tools/generate_all_artifacts.py
```

Generated outputs:
- artifacts/repo_snapshot.json
- artifacts/dependency_graph.json
- artifacts/root_audit.json
- artifacts/orphan_modules.json
- artifacts/REPO_TREE.txt
- artifacts/architecture_audit.json
- artifacts/move_plan.json
- artifacts/import_safety.json
- artifacts/domain_classification.json
- artifacts/root_cleanup_candidates.json

GitHub Actions workflow: `.github/workflows/repo-intelligence.yml`
