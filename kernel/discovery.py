from __future__ import annotations

import ast
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List

from .relationship import RelationshipType, SystemRelationship
from .system_node import NodeStatus, NodeType, SystemNode


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class DiscoveryResult:
    """Result of one system discovery scan."""

    status: str
    discovered_at: str = field(default_factory=utc_now)
    nodes: List[SystemNode] = field(default_factory=list)
    relationships: List[SystemRelationship] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "discovered_at": self.discovered_at,
            "node_count": len(self.nodes),
            "relationship_count": len(self.relationships),
            "nodes": [node.to_dict() for node in self.nodes],
            "relationships": [relationship.to_dict() for relationship in self.relationships],
            "warnings": self.warnings,
        }


@dataclass
class DiscoveryEngine:
    """System discovery layer for AI Kernel.

    Discovery turns repository/runtime observations into SystemNode and
    SystemRelationship objects. It is the bridge from real system state to the
    Kernel Digital Twin.
    """

    last_result: DiscoveryResult | None = None

    def discover_from_paths(self, paths: Iterable[str]) -> DiscoveryResult:
        clean_paths = [path for path in sorted(set(paths)) if path]
        nodes = self._nodes_from_paths(clean_paths)
        relationships = self._ownership_relationships(clean_paths, nodes)
        warnings: List[Dict[str, Any]] = []

        dependency_relationships, dependency_warnings = self._discover_python_dependencies(clean_paths, nodes)
        relationships.extend(dependency_relationships)
        warnings.extend(dependency_warnings)

        result = DiscoveryResult(
            status="ok" if not warnings else "warning",
            nodes=list(nodes.values()),
            relationships=self._dedupe_relationships(relationships),
            warnings=warnings,
        )
        self.last_result = result
        return result

    def apply_to_model(self, system_model: Any, result: DiscoveryResult | None = None) -> Dict[str, Any]:
        result = result or self.last_result
        if not result:
            return {"status": "error", "message": "No discovery result available."}

        for node in result.nodes:
            system_model.add_node(node)
        for relationship in result.relationships:
            system_model.add_relationship(relationship)
            if relationship.relation == RelationshipType.DEPENDS_ON:
                node = system_model.get_node(relationship.source)
                if node:
                    node.add_dependency(relationship.target)

        return {
            "status": "ok",
            "applied_nodes": len(result.nodes),
            "applied_relationships": len(result.relationships),
            "system_summary": system_model.summary(),
        }

    def _nodes_from_paths(self, paths: Iterable[str]) -> Dict[str, SystemNode]:
        nodes: Dict[str, SystemNode] = {}
        for path in paths:
            node = self._node_from_path(path)
            nodes[node.id] = node
        return nodes

    def _ownership_relationships(self, paths: Iterable[str], nodes: Dict[str, SystemNode]) -> List[SystemRelationship]:
        relationships: List[SystemRelationship] = []
        for path in paths:
            node_id = self._path_to_node_id(path)
            if node_id not in nodes:
                continue
            owner_id = self._owner_for_path(path)
            if owner_id and owner_id != node_id:
                relationships.append(
                    SystemRelationship(
                        source=owner_id,
                        target=node_id,
                        relation=RelationshipType.OWNS,
                        description=f"{owner_id} owns discovered module {node_id}.",
                        metadata={"source": "discovery.path", "path": path},
                    )
                )
        return relationships

    def _discover_python_dependencies(
        self,
        paths: Iterable[str],
        nodes: Dict[str, SystemNode],
    ) -> tuple[List[SystemRelationship], List[Dict[str, Any]]]:
        relationships: List[SystemRelationship] = []
        warnings: List[Dict[str, Any]] = []
        module_index = self._build_module_index(paths)

        for path in paths:
            if not path.endswith(".py"):
                continue
            source_id = self._path_to_node_id(path)
            if source_id not in nodes:
                continue

            try:
                content = self._read_repository_file(path)
                imports = self._extract_imports(content, source_id)
            except Exception as exc:
                warnings.append({
                    "code": "IMPORT_DISCOVERY_FAILED",
                    "path": path,
                    "message": str(exc),
                    "type": type(exc).__name__,
                })
                continue

            for imported in imports:
                target_id = self._resolve_import(imported, source_id, module_index)
                if not target_id or target_id == source_id:
                    continue
                if target_id not in nodes:
                    continue

                nodes[source_id].add_dependency(target_id)
                relationships.append(
                    SystemRelationship(
                        source=source_id,
                        target=target_id,
                        relation=RelationshipType.DEPENDS_ON,
                        description=f"{source_id} imports {target_id}.",
                        metadata={
                            "source": "discovery.python_import",
                            "path": path,
                            "import": imported,
                        },
                    )
                )

        return relationships, warnings

    def _read_repository_file(self, path: str) -> str:
        from services.github_runtime import github_runtime

        result = github_runtime.read_file(path)
        return result.get("content", "")

    def _extract_imports(self, content: str, current_module: str) -> List[str]:
        tree = ast.parse(content or "")
        imports: List[str] = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name:
                        imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                module = self._resolve_relative_module(
                    current_module=current_module,
                    module=node.module or "",
                    level=node.level or 0,
                )
                if module:
                    imports.append(module)

        return imports

    def _resolve_relative_module(self, current_module: str, module: str, level: int) -> str:
        if level <= 0:
            return module

        parts = current_module.split(".")
        if parts and parts[-1] == "__init__":
            base_parts = parts[:-1]
        else:
            base_parts = parts[:-1]

        drop = max(level - 1, 0)
        if drop:
            base_parts = base_parts[:-drop] if drop < len(base_parts) else []

        if module:
            base_parts.extend(module.split("."))
        return ".".join(part for part in base_parts if part)

    def _build_module_index(self, paths: Iterable[str]) -> Dict[str, str]:
        index: Dict[str, str] = {}
        for path in paths:
            if not path.endswith(".py"):
                continue
            node_id = self._path_to_node_id(path)
            index[node_id] = node_id
            if node_id.endswith(".__init__"):
                index[node_id[:-9]] = node_id
        return index

    def _resolve_import(self, imported: str, source_id: str, module_index: Dict[str, str]) -> str | None:
        if imported in module_index:
            return module_index[imported]

        parts = imported.split(".")
        while len(parts) > 1:
            candidate = ".".join(parts)
            if candidate in module_index:
                return module_index[candidate]
            parts.pop()

        return None

    def _dedupe_relationships(self, relationships: Iterable[SystemRelationship]) -> List[SystemRelationship]:
        seen: set[tuple[str, str, str]] = set()
        deduped: List[SystemRelationship] = []
        for relationship in relationships:
            key = (relationship.source, relationship.target, relationship.relation.value)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(relationship)
        return deduped

    def _node_from_path(self, path: str) -> SystemNode:
        node_id = self._path_to_node_id(path)
        node_type = self._classify_path(path)
        owner = self._owner_for_path(path) or "repository"

        return SystemNode(
            id=node_id,
            name=path,
            node_type=node_type,
            role=self._role_for_path(path, node_type),
            owner=owner,
            description=f"Discovered repository artifact: {path}",
            status=NodeStatus.DISCOVERED,
            lifecycle="discovered",
            metadata={"path": path, "source": "repository"},
        )

    def _path_to_node_id(self, path: str) -> str:
        normalized = path.strip("/").replace("/", ".")
        if normalized.endswith(".py"):
            normalized = normalized[:-3]
        return normalized or "repository"

    def _classify_path(self, path: str) -> NodeType:
        if path.startswith("kernel/"):
            return NodeType.KERNEL_COMPONENT
        if path.startswith("worker/") or "agent" in path:
            return NodeType.AGENT
        if path.startswith("api/") or path.startswith("services/"):
            return NodeType.SERVICE
        if path.startswith("knowledge/") or path.endswith(".md"):
            return NodeType.KNOWLEDGE
        if path.startswith("static/") or path.startswith("docs/"):
            return NodeType.RESOURCE
        return NodeType.SERVICE if path.endswith(".py") else NodeType.RESOURCE

    def _owner_for_path(self, path: str) -> str:
        if path.startswith("kernel/"):
            return "kernel"
        if path.startswith("worker/"):
            return "kernel.runtime"
        if path.startswith("api/"):
            return "api"
        if path.startswith("services/"):
            return "service_layer"
        if path.startswith("knowledge/"):
            return "kernel.memory"
        return "repository"

    def _role_for_path(self, path: str, node_type: NodeType) -> str:
        if path.startswith("kernel/"):
            return "Kernel component discovered from repository."
        if path.startswith("api/"):
            return "HTTP API surface for AI OS."
        if path.startswith("worker/"):
            return "Worker execution runtime."
        if "planner" in path:
            return "Planning capability."
        if "execution" in path or "execute" in path:
            return "Execution capability."
        return f"Discovered {node_type.value} artifact."


def load_discovery_engine() -> DiscoveryEngine:
    return DiscoveryEngine()


discovery_engine = load_discovery_engine()
