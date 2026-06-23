# TRUNG_HUYEN_AI_OS v1.0

Bản upload lần đầu tiên cho GitHub và Cloud Run.

## API chính

- `GET /` kiểm tra server
- `GET /health` kiểm tra biến môi trường
- `GET /drive/files` liệt kê file Google Drive
- `GET /drive/search?q=...` tìm file theo tên
- `GET /drive/read?file_id=...` đọc nội dung file
- `POST /drive/search-read` tìm và đọc nội dung
- `POST /chat` hỏi AI dựa trên tài liệu Google Drive
- `GET /docs` Swagger UI

## Biến môi trường Cloud Run

- `GOOGLE_SERVICE_ACCOUNT_JSON`
- `DRIVE_FOLDER_ID`
- `OPENAI_API_KEY`
- `OPENAI_MODEL` mặc định `gpt-4.1-mini`
- `MAX_CONTEXT_CHARS` mặc định `30000`

## Deploy

Upload toàn bộ project này lên GitHub repository `trung-huyen-ai`, sau đó để Cloud Run build từ GitHub.

<!-- DEVELOPER GATEWAY PREVIEW TEST -->