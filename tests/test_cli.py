from click.testing import CliRunner

from jinja2_pdoc.cli import jinja2pdoc, main


def test_cli_folder(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["examples/*.jinja2", "--output", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert tmp_path.joinpath("example.md").is_file()


def test_main(tmp_path):
    assert jinja2pdoc("./examples/*.jinja2", frontmatter=False, output=tmp_path) == 0
