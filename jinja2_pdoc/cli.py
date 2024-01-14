from pathlib import Path
from typing import Generator, Iterable, Tuple

import click

from jinja2_pdoc import Jinja2Pdoc, jinja2


def eof_newline(content: str, eof: str = "\n") -> str:
    """
    make sure the file content ends with a newline if specified.
    """
    if content.endswith(eof) or not eof:
        return content

    return content + eof


def load_files(
    files: Iterable[Path], out_dir: Path, force: bool, root: Path = None
) -> Generator[Tuple[str, Path], None, None]:
    """
    iterates over files and yield `(content,  out_file)` if its not existing.

    if `force` is True, all files are proessed.
    """
    for file in files:
        if not root:
            out = out_dir.joinpath(file.name)
        else:
            out = out_dir.joinpath(file.relative_to(root))

        if not out.is_file() or force:
            yield (file.read_text(), out.with_suffix(""))
            click.echo(f"rendering.. {out}")
        else:
            click.echo(f"skip....... {out}")
    else:
        click.echo("\n......done")


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

    input = Path(input).resolve()
    output = Path(output).resolve()

    if input.is_file():
        files = [
            input,
        ]
        root = None
    else:
        files = input.rglob(pattern)
        root = input

    for content, file in load_files(files, output, force, root):
        code = env.from_string(content).render()
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(eof_newline(code, newline))


if __name__ == "__main__":
    main()
