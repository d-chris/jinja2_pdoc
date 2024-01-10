from pathlib import Path

from click.testing import CliRunner

from jinja2_pdoc.cli import eof_newline, load_files, main


def test_eof_newline():
    assert eof_newline("test") == "test\n"
    assert eof_newline("test\n") == "test\n"
    assert eof_newline("test", "") == "test"
    assert eof_newline("test", "\n") == "test\n"


def test_load_files(tmp_path: Path):
    for content, out in load_files(
        [
            Path(__file__),
        ],
        tmp_path,
        force=True,
    ):
        assert "test_load_files" in content
        assert out.parent == tmp_path


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
