# Startup Failure Debug 

Cloud Run deploy reached Step #2 and failed with:

```text
The user-provided container failed to start and listen on PORT=8080
```

This means Docker build completed but the container process crashed or failed to bind to port 8080.

A build-time smoke check was added to Dockerfile:

```dockerfile
RUN python -c "import app; print('APP_IMPORT_OK')"
```

Purpose:

- If FastAPI app import is broken, Cloud Build will now fail earlier.
- The real Python traceback will appear directly in build logs.
- This makes startup errors easier to diagnose from mobile.

Next action:

Redeploy once more and inspect the new build logs.

Expected success signal:

```text
APP_IMPORT_OK
```

If it fails, copy the Python traceback shown immediately before the failure.
