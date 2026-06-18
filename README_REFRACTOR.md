TRUNG_HUYEN_AI_OS refactor package

Files included:
- app.py
- drive.py
- config.py
- requirements.txt
- Dockerfile
- api/__init__.py
- api/mcp.py
- static/index.html

Deploy notes:
1. Replace current repo files with these files.
2. IMPORTANT: rename any existing "drive (1).py" to "drive.py".
3. Ensure Cloud Run env vars:
   - DRIVE_FOLDER_ID
   - GOOGLE_SERVICE_ACCOUNT_JSON
   - OPENAI_API_KEY
   - OPENAI_MODEL
   - MCP_API_KEY
4. Cloud Run command remains:
   uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}
5. GPT Actions import:
   https://trung-huyen-ai-779121307308.asia-southeast1.run.app/openapi.json
6. GPT Actions auth:
   API key header name: x-api-key
