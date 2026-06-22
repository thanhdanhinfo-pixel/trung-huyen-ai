FROM python:3.12-slim

WORKDIR /app 

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

ENV PORT=8080

CMD ["sh", "-c", "uvicorn app:app --host 0.0.0.0 --port ${PORT:-8080}"]
