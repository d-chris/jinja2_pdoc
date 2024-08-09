import pytest

from jinja2_pdoc.meta import frontmatter


@pytest.mark.parametrize(
    "content, expected",
    [
        ("# Title", {}),
        ("<!--filename: test.md-->", {"filename": "test.md"}),
        ("\n  \n<!--filename: test.md-->", {"filename": "test.md"}),
        ("# Title\n<!--filename: test.md-->", {}),
        ("---\nfilename: test.md\n\n---", {"filename": "test.md"}),
        (
            "---\nfilename: test.md\nauthor: cd\n---",
            {"filename": "test.md", "author": "cd"},
        ),
        ("<!--fubar-->", {}),
        ("---\n- file\n- author\n---", {}),
    ],
    ids=lambda x: f"'{x}'",
)
def test_frontmatter(content, expected):
    assert frontmatter(content) == expected
