# TRUNG HUYEN AI SERVER

Server nền tảng để kết nối Google Drive, đọc tài liệu, lập chỉ mục sơ bộ và chuẩn bị cho AI Trung Huyền.

## Chức năng v1.0

- Kiểm tra server sống: `/`
- Kiểm tra cấu hình: `/health`
- Liệt kê file Google Drive: `/drive/files`
- Tìm file theo tên: `/drive/search?q=...`

## Biến môi trường cần có trên Render

### Bắt buộc
`GOOGLE_SERVICE_ACCOUNT_JSON`

Dán toàn bộ nội dung file JSON key Google Service Account vào biến này.

### Tùy chọn
`DRIVE_FOLDER_ID`

ID thư mục Google Drive muốn AI đọc. Nếu để trống, server sẽ tìm trong tất cả file mà Service Account được chia sẻ.

`OPENAI_API_KEY`

Chưa bắt buộc ở v1.0. Sẽ dùng ở bản v2 để hỏi đáp với kho tri thức.

## Render

Build Command:

```bash
pip install -r requirements.txt
```

Start Command:

```bash
uvicorn app:app --host 0.0.0.0 --port $PORT
```
