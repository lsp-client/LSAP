import html


def clean_hover_content(content: str) -> str:
    r"""
    Clean up hover content by unescaping HTML entities and removing unnecessary
    Markdown escapes (like \_) to ensure it is pure Markdown.
    """
    unescaped = html.unescape(content)
    # Remove unnecessary backslash escapes for underscores, as they are often
    # over-escaped by some language servers but usually not needed in code symbols.
    return unescaped.replace("\\_", "_")
