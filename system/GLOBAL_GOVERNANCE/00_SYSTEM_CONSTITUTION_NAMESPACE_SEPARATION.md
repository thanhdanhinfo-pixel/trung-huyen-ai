# NAMESPACE SEPARATION AMENDMENT

RULE-084: Absolute Unique Naming
- No system namespace, directory, package, module, capability, worker, tool group, memory layer, or control-plane component may share the same name, even when located at different hierarchy levels.
- Same-name-different-layer is forbidden because it creates cognitive ambiguity, import ambiguity, governance ambiguity, and operational risk.

RULE-085: Reserved Brain Namespaces
- living_brain = the only operational control plane.
- kernel = neural core implementation.
- knowledge_brain = knowledge and human-development memory layer.
- system_brain = deprecated namespace; must be migrated or renamed.
- brain = deprecated as an operational namespace and must not be used for control-plane code.

RULE-086: Naming Enforcement
- New files and folders must pass namespace uniqueness review before creation.
- Existing duplicate names must be migrated gradually with rollback.
- Any future use of a duplicated namespace is blocked unless Founder explicitly approves a temporary migration bridge.

RULE-087: Migration Priority
- Resolve duplicate brain namespaces first.
- Move operational files out of brain/ into living_brain/.
- Rename knowledge brain folder to knowledge_brain/ or equivalent non-conflicting namespace after Founder-approved migration plan.
- Update imports and startup references accordingly.
