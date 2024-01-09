import pytest

from jinja2_pdoc import PdocJinja2, pdoc


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
            "a", None, marks=pytest.mark.xfail(raises=ValueError, strict=True)
        ),
        pytest.param(
            "a::b:c.",
            {"module": "a", "name": "b", "attr": "c"},
            marks=pytest.mark.xfail(strict=True),
        ),
    ],
)
def test_syntax(arg, ret):
    assert PdocJinja2._pdoc_syntax(arg) == ret


def test_load():
    with pytest.raises(RuntimeError):
        PdocJinja2._pdoc_load("fubar")

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
