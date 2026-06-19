from knowledge.template import create_markdown
from knowledge.markdown import safe_filename
from knowledge.drive import upload_markdown


def capture(
    title: str,
    content: str,
    knowledge_type: str = "Principle",
    author: str = "Trung Huyền",
    status: str = "draft",
):
    filename = safe_filename(title) + ".md"

    markdown = create_markdown(
        title=title,
        content=content,
        author=author,
        knowledge_type=knowledge_type,
        status=status,
    )

    drive_file = upload_markdown(
        filename=filename,
        markdown=markdown,
    )

    return {
        "filename": filename,
        "markdown": markdown,
        "file_id": drive_file["id"],
        "webViewLink": drive_file.get("webViewLink"),
    }
