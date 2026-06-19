def index_drive():
    files = list_drive_files()

    for file in files:
        text = extract_text(file)

        chunks = split_text(text)

        for chunk in chunks:
            embedding = create_embedding(chunk)
            save_to_qdrant(chunk, embedding)

    return {"status": "ok"}
