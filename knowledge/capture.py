from knowledge.template import create_markdown
from knowledge.markdown import safe_filename


def capture(title: str, content: str):
    filename = safe_filename(title)

    markdown = create_markdown(
        title=title,
        content=content
    )

    return {
        "filename": filename + ".md",
        "markdown": markdown
    }
