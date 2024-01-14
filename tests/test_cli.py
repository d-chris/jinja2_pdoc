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
        root=None,
    ):
        assert "test_load_files" in content
        assert out.parent == tmp_path


def test_load_files_folder(tmp_path: Path):
    files = [
        "examples/example1.md.jinja2",
        "examples/ex2/example2.md.jinja2",
        "examples/example.md",
    ]

    for file in map(lambda x: tmp_path.joinpath(x), files):
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(file.stem)

    input = tmp_path.joinpath("examples").rglob("*.jinja2")

    for _, out in load_files(input, tmp_path, force=True, root=tmp_path):
        file = out.relative_to(tmp_path)
        assert out.is_absolute()
        assert file.as_posix() + ".jinja2" in files

    input = tmp_path.joinpath("examples").rglob("*.jinja2")

    for content, out in load_files(input, tmp_path, force=True, root=None):
        file = out.relative_to(tmp_path)
        assert out.is_absolute()
        assert file.parent == Path(".")
        assert content == file.name


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
