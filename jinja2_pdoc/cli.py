from pathlib import Path

import click

from jinja2_pdoc import PdocJinja2, jinja2


def newline(content: str, newline: str = "\n"):
    if content.endswith(newline):
        return content

    return content + newline


@click.command()
@click.argument("input", type=click.Path(exists=True))
@click.argument("output", type=click.Path(file_okay=False), default=Path.cwd())
@click.option(
    "-p",
    "--pattern",
    default="*.jinja2",
    help="template search pattern for directories",
)
@click.option("-f", "--force", is_flag=True, help="overwrite existing files")
def main(input: str, output: str = ".", pattern: str = "*.jinja2", force: bool = False):
    """
    Render jinja2 templates from a input directory or file and
    write to a output directory.

    if the `input` is a directory, all files with a matching `pattern` are renderd.

    if no `output` is given, the current working directory is used.
    """

    env = jinja2.Environment(extensions=[PdocJinja2])

    input = Path(input)
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)

    i = 0

    if input.is_dir():
        for file in input.rglob(pattern):
            code = env.from_string(file.read_text()).render()

            out = output.joinpath(file.stem)

            if force or not out.exists():
                i += 1
                out.write_text(code)
    else:
        code = env.from_string(input.read_text()).render()
        out = output.joinpath(input.stem)

        if force or not out.exists():
            i = 1
            out.write_text(code)

    click.echo(f"Rendered {i} files to {output.resolve()}")


if __name__ == "__main__":
    main()
