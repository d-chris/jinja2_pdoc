import pytest

from jinja2_pdoc import Jinja2Pdoc, jinja2, pdoc


@pytest.mark.parametrize(
    "arg, ret",
    [
        ("a:b", {"module": "a", "name": "b", "attr": "source"}),
        ("a:b:", {"module": "a", "name": "b", "attr": "source"}),
        ("a:b:c", {"module": "a", "name": "b", "attr": "c"}),
        ("a:b:_c_", {"module": "a", "name": "b", "attr": "c"}),
        ("a:b:c.d", {"module": "a", "name": "b", "attr": "c", "frmt": "d"}),
        ("a:b.c:d", {"module": "a", "name": "b.c", "attr": "d"}),
        ("a:b.c:d.e", {"module": "a", "name": "b.c", "attr": "d", "frmt": "e"}),
        ("a:b.c:_d_.e", {"module": "a", "name": "b.c", "attr": "d", "frmt": "e"}),
        ("a:b.c:d._e_", {"module": "a", "name": "b.c", "attr": "d", "frmt": "e"}),
        ("a:b.c:_d_._e_", {"module": "a", "name": "b.c", "attr": "d", "frmt": "e"}),
        ("a::b", {"module": "a", "name": "", "attr": "b"}),
        ("a::", {"module": "a", "name": "", "attr": "source"}),
        ("a", {"module": "a", "name": "", "attr": "source"}),
        ("a:b:c.", {"module": "a", "name": "b", "attr": "c"}),
        ("a::.b", {"module": "a", "name": "", "attr": "source", "frmt": "b"}),
    ],
)
def test_syntax(arg, ret):
    assert Jinja2Pdoc._pdoc_syntax(arg) == ret


def test_load():
    with pytest.raises(RuntimeError):
        Jinja2Pdoc._pdoc_load("not_a_module")

    m = Jinja2Pdoc._pdoc_load("pathlib")
    assert isinstance(m, pdoc.doc.Module)

    m = Jinja2Pdoc._pdoc_load("tests/__init__.py")
    assert issubclass(type(m), pdoc.doc.Module)


def test_jinja2():
    """test_jinja2"""

    m = Jinja2Pdoc._pdoc_jinja2("tests:::docstring")
    assert m == ""

    with pytest.raises(AttributeError):
        Jinja2Pdoc._pdoc_jinja2("tests::test_pdoc")

    m = Jinja2Pdoc._pdoc_jinja2("tests/test_extension.py::test_jinja2:docstring")
    assert m == "test_jinja2"


def test_extension():
    env = jinja2.Environment(extensions=[Jinja2Pdoc])

    s = """
        {% pdoc pathlib::Path:source.upper %}
        """

    code = env.from_string(s).render()

    # check that code does not contain `{% pdoc ... %}` anymore
    assert "{% pdoc" not in code


def test_extension_syntax_error():
    env = jinja2.Environment(extensions=[Jinja2Pdoc])

    s = """
        {% pdoc %}
        """

    with pytest.raises(jinja2.exceptions.TemplateSyntaxError):
        code = env.from_string(s).render()


def test_extension_assertion_error():
    env = jinja2.Environment(extensions=[Jinja2Pdoc])

    s = """
        {% pdoc pathlib::not_existing %}
        """

    with pytest.raises(jinja2.exceptions.TemplateAssertionError):
        code = env.from_string(s).render()
