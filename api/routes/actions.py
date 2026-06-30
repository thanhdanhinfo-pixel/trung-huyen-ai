from __future__ import annotations

from fastapi import APIRouter

SERVER_URL = "https://trung-huyen-ai-779121307308.asia-southeast1.run.app"

router = APIRouter(tags=["actions"])


@router.get("/actions.json", include_in_schema=False)
def actions_schema():
    basic_object = {
        "type": "object",
        "properties": {
            "status": {"type": "string"},
            "message": {"type": "string"},
        },
    }

    file_item = {
        "type": "object",
        "properties": {
            "id": {"type": "string"},
            "name": {"type": "string"},
            "mimeType": {"type": "string"},
            "webViewLink": {"type": "string"},
            "modifiedTime": {"type": "string"},
            "size": {"type": "string"},
        },
    }

    return {
        "openapi": "3.1.0",
        "info": {
            "title": "Trung Huyen Knowledge Action",
            "version": "1.0.0",
        },
        "servers": [{"url": SERVER_URL}],
        "paths": {
            "/drive/files": {
                "get": {
                    "operationId": "listDriveFiles",
                    "summary": "List Google Drive files",
                    "parameters": [
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 5},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Danh sách tài liệu",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "folder_limited": {"type": "boolean"},
                                            "files": {"type": "array", "items": file_item},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/drive/search": {
                "get": {
                    "operationId": "searchDriveFiles",
                    "summary": "Search Google Drive files",
                    "parameters": [
                        {
                            "name": "q",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                        },
                        {
                            "name": "limit",
                            "in": "query",
                            "required": False,
                            "schema": {"type": "integer", "default": 5},
                        },
                    ],
                    "responses": {
                        "200": {
                            "description": "Kết quả tìm kiếm",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "query": {"type": "string"},
                                            "files": {"type": "array", "items": file_item},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/drive/read": {
                "get": {
                    "operationId": "readDriveFile",
                    "summary": "Read Google Drive file content",
                    "parameters": [
                        {
                            "name": "file_id",
                            "in": "query",
                            "required": True,
                            "schema": {"type": "string"},
                        }
                    ],
                    "responses": {
                        "200": {
                            "description": "Nội dung tài liệu",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "file_id": {"type": "string"},
                                            "content_length": {"type": "integer"},
                                            "content": {"type": "string"},
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/drive/search-read": {
                "post": {
                    "operationId": "searchAndReadDrive",
                    "summary": "Search and read Google Drive documents",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["q"],
                                    "properties": {
                                        "q": {"type": "string"},
                                        "limit": {"type": "integer", "default": 5},
                                        "max_chars_per_file": {"type": "integer", "default": 6000},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Tài liệu kèm nội dung",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "query": {"type": "string"},
                                            "files": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "id": {"type": "string"},
                                                        "name": {"type": "string"},
                                                        "mimeType": {"type": "string"},
                                                        "webViewLink": {"type": "string"},
                                                        "modifiedTime": {"type": "string"},
                                                        "content": {"type": "string"},
                                                    },
                                                },
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
            "/chat": {
                "post": {
                    "operationId": "chatWithKnowledge",
                    "summary": "Ask Trung Huyen AI",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "required": ["question"],
                                    "properties": {
                                        "question": {"type": "string"},
                                        "limit": {"type": "integer", "default": 5},
                                        "max_chars_per_file": {"type": "integer", "default": 6000},
                                    },
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "AI trả lời dựa trên AI Brain",
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "status": {"type": "string"},
                                            "answer": {"type": "string"},
                                            "sources": {
                                                "type": "array",
                                                "items": {
                                                    "type": "object",
                                                    "properties": {
                                                        "name": {"type": "string"},
                                                        "link": {"type": "string"},
                                                        "score": {"type": "number"},
                                                        "chunk_index": {"type": "integer"},
                                                    },
                                                },
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
        },
    }
