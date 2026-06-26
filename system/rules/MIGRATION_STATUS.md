# Rules Migration Status

Pending source modules:
- system/rule_engine.py
- system/rule_engine_v2.py
- system/policy_engine.py

Migration approach:
1. Copy implementation.
2. Convert root module to compatibility shim.
3. Run import audit.
4. Remove shim in a later release.
