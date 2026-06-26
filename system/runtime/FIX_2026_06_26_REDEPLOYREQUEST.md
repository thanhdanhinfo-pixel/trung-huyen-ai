# Fix — RedeployRequest NameError

## Problem

Cloud Run revision failed startup with:

```text
NameError: name 'RedeployRequest' is not defined
```

Location:

```text
api/deployment.py
```

## Fix

Added before `/deployment/redeploy` endpoint:

```python
class RedeployRequest(BaseModel):
    approved: bool = Field(default=False)
    reason: Optional[str] = None


def _redeploy_config() -> Dict[str, Any]:
    ...
```

## Expected result

Next Cloud Run build should pass app import and container startup should progress beyond this error.

## Next verification

After deployment finishes:

```text
GET /deployment/capabilities
GET /mcp/tools
```

Expected:

```text
redeploy_endpoint: true
drive_list_children
drive_tree
drive_index
```
