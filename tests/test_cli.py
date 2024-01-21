from pathlib import Path

from click.testing import CliRunner

from jinja2_pdoc.cli import eof_newline, main, search_files


def test_eof_newline():
    assert eof_newline("test") == "test\n"
    assert eof_newline("test\n") == "test\n"
    assert eof_newline("test", "") == "test"
    assert eof_newline("test", "\n") == "test\n"


def test_cli_folder(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["examples", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert tmp_path.joinpath("example.md").is_file()

    result = runner.invoke(
        main,
        ["examples/example.md.jinja2", str(tmp_path)],
    )
    assert result.exit_code == 0
