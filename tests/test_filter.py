import subprocess
from pathlib import Path

import pytest

from jinja2_pdoc import Environment


@pytest.fixture
def mock_shell(mocker):
    return mocker.patch(
        "subprocess.run",
        return_value=subprocess.CompletedProcess(
            args="echo testing..",
            stdout="testing..",
            stderr="",
            returncode=0,
        ),
    )


@pytest.fixture
def mock_include(mocker):
    return mocker.patch.object(Path, "read_text", return_value="testing..")


@pytest.mark.parametrize(
    "filter",
    [
        "shell",
        "include",
        "strip",
    ],
)
def test_filter(filter):

    assert filter in Environment().filters


def test_add_filter():

    env = Environment()
    env.add_filter("upper", lambda s: s.upper())
    s = env.from_string('{{ "hello world." | upper }}').render()

    assert s == "HELLO WORLD."


def test_add_filter_raises():

    with pytest.raises(TypeError):
        Environment().add_filter("none", None)


def test_render_include(mock_include):

    template = '{{ "LICENSE" | include }}'

    code = Environment().from_string(template).render()

    assert code == "testing.."


def test_render_shell(mock_shell):

    template = '{{ "echo testing.." | shell }}'

    code = Environment().from_string(template).render()

    assert code == "testing.."


def test_render_strip():

    template = '{{ "  testing..  \n" | strip }}'

    code = Environment().from_string(template).render()

    assert code == "testing.."


@pytest.mark.parametrize(
    "attr",
    [
        "stdout",
        "stderr",
        "returncode",
        "args",
    ],
)
def test_shell_result(mock_shell, attr):
    assert isinstance(Environment.shell("echo testing..", result=attr), str)


@pytest.mark.parametrize(
    "promt,expected",
    [
        (None, "testing.."),
        ("> ", "> echo testing..\n\ntesting.."),
        ("$ %s", "$ echo testing..\ntesting.."),
    ],
)
def test_shell_promt(mock_shell, promt, expected):

    stdout = Environment.shell("echo testing..", promt=promt)

    assert stdout == expected


def test_include_attr(mock_include):

    content = Environment.include("", attr="upper")

    assert content == "TESTING.."


def test_strip_chars():

    content = Environment.strip("testing..", chars=".")

    assert content == "testing"
