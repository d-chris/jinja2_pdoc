import pytest

from jinja2_pdoc.wrapper import Function, Module, PdocStr


@pytest.fixture
def module() -> Module:
    return Module.from_name("pathlib")


@pytest.fixture
def function(module: Module) -> Function:
    return module.get("Path.open")


@pytest.fixture
def pdocstr() -> PdocStr:
    return PdocStr("\n".join(["    def dummy():", "        pass"]))


@pytest.fixture(params=["indent", "dedent", "nodoc", "lower", "upper"])
def pdocstr_attr(request):
    return request.param


@pytest.fixture(params=["source", "code", "docstring"])
def function_prop(request):
    return request.param


def test_module():
    m = Module.from_name("pathlib")

    assert isinstance(m, Module)


def test_module_raises():
    with pytest.raises(RuntimeError):
        Module.from_name("not_a_module")


@pytest.mark.parametrize(
    "name, returntype",
    [
        ("Path", Function),
        ("Path.open", Function),
        ("NotAClass", type(None)),
        ("Path.notafunction", type(None)),
    ],
)
def test_module_returntype(module: Module, name: str, returntype: type):
    obj = module.get(name)
    assert isinstance(obj, returntype)


def test_pdocstr_attributes(pdocstr_attr: str, pdocstr: PdocStr):

    assert hasattr(pdocstr, pdocstr_attr)


def test_pdocstr_returntypes(pdocstr_attr, pdocstr: PdocStr):
    method = getattr(pdocstr, pdocstr_attr)

    assert isinstance(method(), PdocStr)


def test_pdocstr_callable(pdocstr_attr, pdocstr: PdocStr):
    method = getattr(pdocstr, pdocstr_attr)

    assert callable(method)


def test_pdocstr_nodoc():
    text = [
        "",
        '"""docstring"""',
        "",
        "def dummy():",  # 3
        "    pass",
        "",
    ]

    funcstr = PdocStr("\n".join(text))

    assert funcstr.nodoc() == "\n".join(text[3:5])


def test_pdocstr_shebang():
    text = [
        "#! python3",
        "",
        '"""docstring"""',
        "",
        "def dummy():",  # 4
        "    pass",
        "",
    ]

    funcstr = PdocStr("\n".join(text))

    assert funcstr.nodoc() == "\n".join(text[4:6])


def test_pdocstr_indent(pdocstr: PdocStr):
    s = pdocstr.indent()

    assert s.startswith("def dummy():\n  pass")


def test_pdocstr_dedent(pdocstr: PdocStr):
    s = pdocstr.dedent()

    assert s.startswith("def dummy():\n    pass")


def test_function_attributes(function_prop, function):
    assert hasattr(function, function_prop)


def test_function_returntypes(function_prop, function):
    prop = getattr(function, function_prop)

    assert isinstance(prop, PdocStr)


def test_function_property(function_prop, function):
    prop = getattr(function, function_prop)

    assert not callable(prop)


def test_function_code(function):
    doc = function.docstring

    assert doc, "testing function should have a docstring"
    assert doc not in function.code
