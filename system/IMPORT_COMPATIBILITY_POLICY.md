# Import Compatibility Policy

Rules:
1. Never move a module without leaving a compatibility shim.
2. Public APIs keep the same symbols and names.
3. Source-of-truth YAML files remain at root.
4. Import audit must pass before removing any shim.
5. External integrations and apps must continue using legacy imports until a deprecation window closes.
