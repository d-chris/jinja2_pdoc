from pathlib import Path
from typing import Generator, List, Set

import click

import jinja2_pdoc.meta as meta
from jinja2_pdoc import Environment


def expand(files: List[str]) -> Generator[Path, None, None]:
    """
    yields only an existing file.

    if file.name contains a glob pattern it yields all
    matching files

    >>> list(expand("examples/*.jinja2"))
    [WindowsPath('examples/example.md.jinja2')]
    """

    def wrapper(file: str) -> Generator[Path, None, None]:
        file = Path(file)
        try:
            file.resolve(True)
        except FileNotFoundError:
            pass
        except OSError:
            parent, pattern = file.parent, file.name

            yield from parent.glob(pattern)
        else:
            yield file

    for file in files:
        yield from wrapper(file)


def echo(tag, file, out):
    """
    print a message to the console
    """
    if isinstance(tag, Exception):
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


@click.command()
@click.argument(
    "files",
    nargs=-1,
)
@click.option(
    "-o",
    "--output",
    default=Path.cwd(),
    show_default=True,
    help="output directory for files, if no 'filename' is provided in the frontmatter",
)
@click.option(
    "-e",
    "--encoding",
    default="utf-8",
    show_default=True,
    help="encoding of the files",
)
@click.option(
    "-s",
    "--suffixes",
    multiple=True,
    default=[".jinja2", ".j2"],
    show_default=True,
    help=(
        "suffixes which will be removed from templates, "
        "if no 'filename' is provided in the frontmatter"
    ),
)
@click.option(
    "--fail-fast",
    is_flag=True,
    default=False,
    show_default=True,
    help="exit on first error when rendering multiple file",
)
@click.option(
    "--meta/--no-meta",
    "frontmatter",
    default=True,
    show_default=True,
    help="parse frontmatter from the template, to search for 'filename'",
)
def main(
    files: List[str],
    output: str = Path.cwd(),
    encoding="utf-8",
    suffixes: Set[str] = {".jinja2", ".j2"},
    fail_fast: bool = False,
    frontmatter: bool = True,
) -> None:
    """
    Render jinja2 one or multiple template files, wildcards in filenames are allowed,
    e.g. `examples/*.jinja2`.

    If no 'filename' is provided in the frontmatter section, e.g.
    '<!--filename: example.md-->'. All files are written to `output`
    directory and `suffixes` will be removed.

    To ignore the frontmatter section use the `--no-meta` flag.
    """

    root = Path(output)

    env = Environment()

    def render_file(file):
        template = file.read_text(encoding)

        content = env.from_string(template).render()

        if not content.endswith("\n"):
            content += "\n"

        post = meta.frontmatter(content) if frontmatter else {}

        try:
            output = Path(post["filename"])
        except KeyError:
            output = root.joinpath(file.name)

            if output.suffix in suffixes:
                output = output.with_suffix("")

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding)

        return output

    result = 0

    for file in expand(files):
        try:
            echo("rendering", file, render_file(file))
        except Exception as e:
            echo(e, file, "")

            if fail_fast:
                return 1

            result += 1

    return result


if __name__ == "__main__":
    SystemExit(main())
