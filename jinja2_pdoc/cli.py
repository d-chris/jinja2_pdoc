from pathlib import Path
from typing import Tuple

import click

from jinja2_pdoc import Jinja2Pdoc, jinja2


def eof_newline(content: str, eof: str = "\n") -> str:
    """
    make sure the file content ends with a newline if specified.
    """
    if content.endswith(eof) or not eof:
        return content

    return content + eof


def search_files(file: str, pattern: str = "*.jinja2") -> Tuple[Path, Path]:
    """
    Search for files with a pattern in a directory or a single file.

    Return tuples of template file and output file name
    """
    root = Path(file)

    if root.is_file():
        if root.suffix != Path(pattern).suffix:
            raise ValueError(f"file suffix {root.suffix} does not match {pattern}")

        files = [
            root,
        ]
        root = root.parent
    else:
        files = root.rglob(pattern)

    for file in files:
        yield (file, file.relative_to(root).with_suffix(""))


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
@click.option(
    "-n",
    "--newline",
    default="\n",
    help="newline character",
)
def main(
    input: str,
    output: str = ".",
    pattern: str = "*.jinja2",
    force: bool = False,
    newline: str = "\n",
) -> None:
    """
    Render jinja2 templates from a input directory or file and
    write to a output directory.

    if the `input` is a directory, all files with a matching `pattern` are renderd.

    if no `output` is given, the current working directory is used.
    """

    env = jinja2.Environment(extensions=[Jinja2Pdoc])

    output = Path(output)

    def echo(tag, file, out):
        if isinstance(tag, BaseException):
            out = str(tag)[:48]
            tag = type(tag).__name__
            color = "red"
        else:
            out = str(out.resolve())[-48:]

            if tag == "skip":
                color = "yellow"
            else:
                color = "green"

        tag = click.style(f"{tag[:16]:<16}", fg=color)

        click.echo(f"{tag} {str(file)[-48:]:.<48}   {out}")

    for template, file in search_files(input, pattern):
        out = output.joinpath(file)

        if out.is_file() and not force:
            echo("skip", template, out)
            continue

        try:
            content = template.read_text()
            code = env.from_string(content).render()
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(eof_newline(code, newline))
        except BaseException as e:
            echo(e, template, out)
        else:
            echo("rendered", template, out)


if __name__ == "__main__":
    main()
