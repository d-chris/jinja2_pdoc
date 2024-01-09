import pytest

from jinja2_pdoc.wrapper import Function, Module, PdocStr


@pytest.fixture
def doc() -> Module:
    return Module.from_name("pathlib")


@pytest.fixture
def open(doc: Module) -> Function:
    return doc.get("Path.open")


def test_module(doc: Module):
    assert isinstance(doc, Module)


def test_class(doc: Module):
    cls = doc.get("Path")

    assert cls.name == "Path"
    assert isinstance(cls, Function)

    cls = doc.get("NotAClass")
    assert cls is None

    func = doc.get("Path.notafunction")
    assert func is None


def test_func(open: Function):
    assert open.name == "open"
    assert isinstance(open, Function)
    assert hasattr(open, "code")


def test_str(open: Function):
    sourcecode = open.code

    assert isinstance(sourcecode, PdocStr)
    assert hasattr(sourcecode, "dedent")

    assert isinstance(open.docstring, PdocStr)


def test_module_raises():
    with pytest.raises(RuntimeError):
        Module.from_name("not_a_module")
