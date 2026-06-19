from knowledge.template import create_markdown
from knowledge.markdown import safe_filename


def capture(
    title: str,
    content: str,
    knowledge_type: str = "principle",
    author: str = "Trung Huyền",
    status: str = "draft",
):

    filename = safe_filename(title)

    markdown = create_markdown(
        title=title,
        content=content,
        author=author,
        knowledge_type=knowledge_type,
        status=status,
    )

    return {
        "filename": filename + ".md",
        "markdown": markdown,
    }
