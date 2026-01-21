from lsap.utils.markdown import clean_hover_content


def test_clean_hover_content_basic():
    assert clean_hover_content("foo") == "foo"
    assert clean_hover_content("foo\\_bar") == "foo_bar"
    assert clean_hover_content("foo\\\\bar") == "foo\\bar"


def test_clean_hover_content_html_unescape():
    assert clean_hover_content("foo &amp; bar") == "foo & bar"
    assert clean_hover_content("foo &lt; bar") == "foo < bar"


def test_clean_hover_content_multiple_escapes():
    # Test common over-escaped characters in Markdown
    content = r"func\(arg1, arg2\) \{ return \*ptr; \}"
    expected = "func(arg1, arg2) { return *ptr; }"
    assert clean_hover_content(content) == expected


def test_clean_hover_content_all_punctuation():
    # All ASCII punctuation characters: !"#$%&'()*+,-./:;<=>?@[\]^_`{|}~
    escaped = r"\!\"\#\$\%\&\'\(\)\*\+\,\-\.\/\:\;\<\=\>\?\@\[\\\]\^\_\`\{\|\}\~"
    expected = "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    assert clean_hover_content(escaped) == expected
