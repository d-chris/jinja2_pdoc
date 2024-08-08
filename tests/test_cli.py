from click.testing import CliRunner

from jinja2_pdoc.cli import main


def test_cli_folder(tmp_path):
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["examples/*.jinja2", "--output", str(tmp_path)],
    )
    assert result.exit_code == 0
    assert tmp_path.joinpath("example.md").is_file()
