import html
import re


def clean_hover_content(content: str) -> str:
    r"""
    Clean up hover content by unescaping HTML entities and removing unnecessary
    Markdown escapes to ensure it is pure Markdown.
    """
    unescaped = html.unescape(content)
    # Remove unnecessary backslash escapes for punctuation characters that are
    # often over-escaped by some language servers.
    return re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~])", r"\1", unescaped)
