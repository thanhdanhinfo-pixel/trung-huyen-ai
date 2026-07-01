import json
from pathlib import Path

p = Path("openapi-mcp-v3.json")
data = json.loads(p.read_text(encoding="utf-8"))

data["openapi"] = "3.0.3"

data.setdefault("security", [{"ApiKeyAuth": []}])
data.setdefault("components", {})
data["components"].setdefault("schemas", {})
data["components"]["securitySchemes"] = {
    "ApiKeyAuth": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-Key"
    }
}

for path, methods in data.get("paths", {}).items():
    for method, op in methods.items():
        if method not in ["get", "post", "put", "patch", "delete"]:
            continue

        op.setdefault("responses", {})

        for code, desc in {
            "400": "Bad request",
            "401": "Unauthorized",
            "404": "Not found",
            "500": "Internal server error"
        }.items():
            op["responses"].setdefault(code, {"description": desc})

        for resp in op["responses"].values():
            content = resp.get("content", {})
            app_json = content.get("application/json", {})
            schema = app_json.get("schema")
            if isinstance(schema, dict) and schema.get("required") == []:
                schema.pop("required", None)

p.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
print("fixed openapi-mcp-v3.json")
