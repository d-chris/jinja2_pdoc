import inspect
from pathlib import Path
from typing import Generator, List, Set

import click

import jinja2_pdoc.meta as meta
from jinja2_pdoc.environment import Environment


def signature(wrapped):
    """
    A decorator that sets the signature of the wrapper function to the wrapped function
    and also copies the docstring.
    """

    def decorator(wrapper):
        wrapper.__doc__ += "\n\n" + wrapped.__doc__

        sig = inspect.signature(wrapped)

        param = [
            inspect.Parameter(
                name="files",
                kind=inspect.Parameter.VAR_POSITIONAL,
                annotation=str,
            ),
        ] + [p for n, p in sig.parameters.items() if n != "files"]

        wrapper.__signature__ = sig.replace(parameters=param, return_annotation=int)
        return wrapper

    return decorator


def expand(files: List[str], duplicates: bool = False) -> Generator[Path, None, None]:
    """
    yields only an existing file.

    if file.name contains a glob pattern it yields all
    matching files

    >>> list(expand("examples/*.jinja2"))
    [WindowsPath('examples/example.md.jinja2')]
    """

    def wrapper(file: str) -> Generator[Path, None, None]:

        try:
            file = Path(file)
            file.resolve(True)
        except (FileNotFoundError, TypeError):
            pass
        except OSError:
            parent, pattern = file.parent, file.name

            yield from parent.glob(pattern)
        else:
            yield file

    if not duplicates:
        seen = set()

        for file in files:
            for item in wrapper(file):
                if item not in seen:
                    seen.add(item)
                    yield item
    else:
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
        try:
            out = str(out.relative_to(Path.cwd()))[-48:]
        except ValueError:
            out = str(out)[-48:]

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
    type=click.Path(),
    help="output directory for files, if no 'filename' is provided in the frontmatter.",
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
@click.option(
    "--rerender/--no-rerender",
    default=False,
    show_default=True,
    help="Each file is rendered only once.",
)
def main(
    files: List[str],
    *,
    output: str = None,
    encoding="utf-8",
    suffixes: Set[str] = {".jinja2", ".j2"},
    fail_fast: bool = False,
    frontmatter: bool = True,
    rerender: bool = False,
) -> None:
    """
    Render jinja2 one or multiple template files, wildcards in filenames are allowed,
    e.g. `examples/*.jinja2`.

    If no 'filename' is provided in the frontmatter section of your file, e.g.
    '<!--filename: example.md-->'. All files are written to `output`
    directory and `suffixes` will be removed.

    To ignore the frontmatter section use the `--no-meta` flag.
    """

    root = Path(output) if output else Path.cwd()

    env = Environment()

    def render_file(file):
        template = file.read_text(encoding)

        content = env.from_string(template).render()

        post = meta.frontmatter(content) if frontmatter else {}

        try:
            output = root.joinpath(post["filename"]).resolve()
        except KeyError:
            output = root.joinpath(file.name)

        if output.suffix in suffixes:
            output = output.with_suffix("")

        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(content, encoding)

        return output

    result = 0

    for file in expand(files, duplicates=rerender):
        try:
            echo("rendering", file, render_file(file))
        except Exception as e:
            echo(e, file, "")

            if fail_fast:
                return 1

            result += 1

    return result


@signature(main.callback)
def jinja2pdoc(*files, **kwargs):
    """
    Wrapper function to call the `jinja2pdoc command-line-interface` directly from your
    python code.

    `output` is set on default to the current working directory.

    Returns non-zero exit code if an error occurred.
    """
    return main.callback(files, **kwargs)


if __name__ == "__main__":
    main()
