import pytest
from click.testing import CliRunner

from jinja2_pdoc.cli import cli, jinja2pdoc


def test_cli_folder(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "examples/*.jinja2",
            "--output",
            str(tmp_path),
        ],
    )
    assert result.exit_code == 0
    assert "rendering" in result.output
    assert tmp_path.joinpath("example.md").is_file()


def test_cli_nofile(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        cli,
        [
            "--output",
            str(tmp_path),
        ],
    )
    assert result.exit_code == -1
    assert result.output == "No files found.\n"


def test_main(tmp_path):
    assert jinja2pdoc("./examples/*.jinja2", frontmatter=False, output=tmp_path) == 0


# Define the fixture with params
@pytest.fixture(
    params=[
        (["./examples/*.jinja2"], 0),
        (["./examples/*.jinja2", "./examples/*.j2"], 0),
        (["./examples/example.md.jinja2"], 0),
        (["./examples/*.jinja2", None], 0),
    ],
    ids=lambda x: f"{x[0]}-{x[1]}",
)
def files(request):
    return request.param


def test_jinja2pdoc(tmp_path, files):
    args, result = files
    assert jinja2pdoc(*args, frontmatter=False, output=tmp_path) == result


@pytest.mark.parametrize("failfast", [True, False])
def test_jinja2pdoc_fail(mocker, tmp_path, files, failfast):

    mocker.patch("pathlib.Path.write_text", side_effect=PermissionError)

    args, _ = files
    assert (
        jinja2pdoc(
            *args,
            frontmatter=False,
            output=tmp_path,
            fail_fast=failfast,
            rerender=True,
            silent=False,
        )
        == 1
    )
