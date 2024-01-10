import pytest

from jinja2_pdoc import PdocJinja2, jinja2, pdoc


@pytest.mark.parametrize(
    "arg, ret",
    [
        ("a::b", {"module": "a", "name": "b", "attr": "source"}),
        ("a::b:", {"module": "a", "name": "b", "attr": "source"}),
        ("a::b:c", {"module": "a", "name": "b", "attr": "c"}),
        ("a::b:_c_", {"module": "a", "name": "b", "attr": "c"}),
        ("a::b:c.d", {"module": "a", "name": "b", "attr": "c", "frmt": "d"}),
        ("a::b.c:d", {"module": "a", "name": "b.c", "attr": "d"}),
        ("a::b.c:d.e", {"module": "a", "name": "b.c", "attr": "d", "frmt": "e"}),
        ("a::b.c:_d_.e", {"module": "a", "name": "b.c", "attr": "d", "frmt": "e"}),
        ("a::b.c:d._e_", {"module": "a", "name": "b.c", "attr": "d", "frmt": "e"}),
        ("a::b.c:_d_._e_", {"module": "a", "name": "b.c", "attr": "d", "frmt": "e"}),
        ("a:::b", {"module": "a", "name": "", "attr": "b"}),
        ("a:::", {"module": "a", "name": "", "attr": "source"}),
        pytest.param(
            "a",
            None,
            marks=pytest.mark.xfail(
                raises=ValueError, strict=True, reason="should be fixed in future"
            ),
        ),
        pytest.param(
            "a::b:c.",
            {"module": "a", "name": "b", "attr": "c"},
            marks=pytest.mark.xfail(strict=True, reason="should be fixed in future"),
        ),
        pytest.param(
            "a:::.b",
            {"module": "a", "name": "", "attr": "source", "frmt": "b"},
            marks=pytest.mark.xfail(strict=True, reason="should be fixed in future"),
        ),
    ],
)
def test_syntax(arg, ret):
    assert PdocJinja2._pdoc_syntax(arg) == ret


def test_load():
    with pytest.raises(RuntimeError):
        PdocJinja2._pdoc_load("not_a_module")

    m = PdocJinja2._pdoc_load("pathlib")
    assert isinstance(m, pdoc.doc.Module)

    m = PdocJinja2._pdoc_load("tests/__init__.py")
    assert issubclass(type(m), pdoc.doc.Module)


def test_jinja2():
    """test_jinja2"""

    m = PdocJinja2._pdoc_jinja2("tests:::docstring")
    assert m == ""

    with pytest.raises(AttributeError):
        PdocJinja2._pdoc_jinja2("tests::test_pdoc")

    m = PdocJinja2._pdoc_jinja2("tests/test_extension.py::test_jinja2:docstring")
    assert m == "test_jinja2"


def test_extension():
    env = jinja2.Environment(extensions=[PdocJinja2])

    s = """
        {% pdoc pathlib::Path:source.upper %}
        """

    code = env.from_string(s).render()

    # check that code does not contain `{% pdoc ... %}` anymore
    assert "{% pdoc" not in code


def test_extension_syntax_error():
    env = jinja2.Environment(extensions=[PdocJinja2])

    s = """
        {% pdoc %}
        """

    with pytest.raises(jinja2.exceptions.TemplateSyntaxError):
        code = env.from_string(s).render()


def test_extension_assertion_error():
    env = jinja2.Environment(extensions=[PdocJinja2])

    s = """
        {% pdoc pathlib::not_existing %}
        """

    with pytest.raises(jinja2.exceptions.TemplateAssertionError):
        code = env.from_string(s).render()
