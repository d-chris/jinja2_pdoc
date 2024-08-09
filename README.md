# jinja2-pdoc

[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/jinja2_pdoc)](https://pypi.org/project/jinja2_pdoc/)
[![PyPI - jinja2_pdoc](https://img.shields.io/pypi/v/jinja2_pdoc)](https://pypi.org/project/jinja2_pdoc/)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/jinja2_pdoc)](https://pypi.org/project/jinja2_pdoc/)
[![PyPI - License](https://img.shields.io/pypi/l/jinja2_pdoc)](https://raw.githubusercontent.com/d-chris/jinja2_pdoc/main/LICENSE)
[![GitHub - pytest](https://img.shields.io/github/actions/workflow/status/d-chris/jinja2_pdoc/pytest.yml?logo=github&label=pytest)](https://github.com/d-chris/jinja2_pdoc/actions/workflows/pytest.yml)
[![GitHub - Page](https://img.shields.io/website?url=https%3A%2F%2Fd-chris.github.io%2Fjinja2_pdoc%2F&up_message=pdoc&logo=github&label=documentation)](https://d-chris.github.io/jinja2_pdoc)
[![GitHub tag (with filter)](https://img.shields.io/github/v/tag/d-chris/jinja2_pdoc?logo=github&label=github)](https://github.com/d-chris/jinja2_pdoc)
[![codecov](https://codecov.io/gh/d-chris/jinja2_pdoc/graph/badge.svg?token=19YB50ZL63)](https://codecov.io/gh/d-chris/jinja2_pdoc)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://github.com/pre-commit/pre-commit)

---

[`jinja2`](https://www.pypi.org/project/jinja2) extension based on [`pdoc`](https://pypi.org/project/pdoc/) to embedd python code directly from modules or files into your `jinja` template.

Lazy loading of `docstrings`, `code` and `functions` directly from python modules into your `jinja2 template`.

## Installation

```cmd
pip install jinja2_pdoc
```

## Example

Create a markdown file with `docstrings` and `source code` from `pathlib.Path` using `jinja2` with `jinja2_pdoc` extension.

### Python

````python
from jinja2_pdoc import jinja2, Jinja2Pdoc

env = jinja2.Environment(extensions=[Jinja2Pdoc])

s = """
    # jinja2-pdoc

    embedd python code directly from pathlib using a jinja2 extension based on pdoc

    ## docstring from pathlib.Path

    {% pdoc pathlib:Path:docstring %}

    ## source from pathlib.Path.open

    ```python
    {% pdoc pathlib:Path.open:source.indent -%}
    ```
    """

code = env.from_string(textwrap.dedent(s)).render()

Path("example.md").write_text(code)
````

### Markdown

output of the [python code](#python) above.

````markdown

# jinja2-pdoc

embedd python code directly from pathlib using a jinja2 extension based on pdoc

## docstring from pathlib.Path

PurePath subclass that can make system calls.

Path represents a filesystem path but unlike PurePath, also offers
methods to do system calls on path objects. Depending on your system,
instantiating a Path will return either a PosixPath or a WindowsPath
object. You can also instantiate a PosixPath or WindowsPath directly,
but cannot instantiate a WindowsPath on a POSIX system or vice versa.

## source from pathlib.Path.open

```python
def open(self, mode='r', buffering=-1, encoding=None,
         errors=None, newline=None):
  """
  Open the file pointed by this path and return a file object, as
  the built-in open() function does.
  """
  if "b" not in mode:
    encoding = io.text_encoding(encoding)
  return io.open(self, mode, buffering, encoding, errors, newline)
```
````

## Syntax

`{% pdoc`[`<module>`](#module)`:`[`<object>`](#object)`:`[`<pdoc_attr[.str_attr]>`](#pdoc_attr)`%}`

### `<module>`

module name or path to python file, e.g.:

- `pathlib`
- `examples/example.py`

Example:

```jinja2
{% pdoc pathlib %}
```

### `<object>`

class and/or function names, eg. from `pathlib`:

- `Path`
- `Path.open`

Example:

```jinja2
{% pdoc pathlib:Path %}
```

### `<pdoc_attr>`

`pdoc` attributes:

- `docstring` - docstring of the object
- `source` - source code of the object
- `code` - plane code from functions, without def and docstring

Example:

```jinja2
{% pdoc pathlib:Path:docstring %}
```

### `[.str_attr]`

optional `str` functions can be added to `<pdoc_attr>` with a dot

- `dedent` - removes common leading whitespace, see `textwrap.dedent`
- `indent` - format code with 2 spaces for indentation, see `autopep8.fix_code`
- `upper` - converts to upper case
- `lower` - converts to lower case

Example:

```jinja2
{% pdoc pathlib:Path.open:code.dedent %}
```

## Command Line Interface

```console
>>> jinja2pdoc --help

Usage: jinja2pdoc [OPTIONS] [FILES]...

  Render jinja2 one or multiple template files, wildcards in filenames are
  allowed, e.g. `examples/*.jinja2`.

  If no 'filename' is provided in the frontmatter section of your file, e.g.
  '<!--filename: example.md-->'. All files are written to `output` directory
  and `suffixes` will be removed.

  To ignore the frontmatter section use the `--no-meta` flag.

Options:
  -o, --output PATH           output directory for files, if no 'filename' is
                              provided in the frontmatter.  [default: cwd]
  -e, --encoding TEXT         encoding of the files  [default: utf-8]
  -s, --suffixes TEXT         suffixes which will be removed from templates,
                              if no 'filename' is provided in the frontmatter
                              [default: .jinja2, .j2]
  --fail-fast                 exit on first error when rendering multiple file
  --meta / --no-meta          parse frontmatter from the template, to search
                              for 'filename'  [default: meta]
  --rerender / --no-rerender  Each file is rendered only once.  [default: no-
                              rerender]
  --silent                    suppress console output
  --help                      Show this message and exit.
```

```console
>>> jinja2pdoc .\examples\*.jinja2
rendered         examples\example.md.jinja2......................   .\example.md
```

## pre-commit hook

**Per default the hook is not registered to any `type` or `files`!**

To render all template files from `docs` using `.pre-commit-config.yaml` add the following.

You may add a `frontmatter` section at the beginning of in your templates to specify output directory and filename, e.g. `<!--filename: example.md-->`. If no metadata are at the beginning of the  template, the rendered file is written to the `output` directory which is default the current working direktory.

```yaml
repos:
  - repo: https://github.com/d-chris/jinja2_pdoc/
    rev: v1.0.0
    hooks:
      - id: jinja2pdoc
        files: docs/.*\.jinja2$
```

## Dependencies

[![PyPI - autopep8](https://img.shields.io/pypi/v/autopep8?logo=pypi&logoColor=white&label=autopep8)](https://pypi.org/project/autopep8/)
[![PyPI - click](https://img.shields.io/pypi/v/click?logo=pypi&logoColor=white&label=click)](https://pypi.org/project/click/)
[![PyPI - jinja2](https://img.shields.io/pypi/v/jinja2?logo=jinja&logoColor=white&label=jinja2)](https://pypi.org/project/jinja2/)
[![PyPI - pdoc](https://img.shields.io/pypi/v/pdoc?logo=pypi&logoColor=white&label=pdoc)](https://pypi.org/project/pdoc/)
[![Pypi - PyYAML](https://img.shields.io/pypi/v/PyYAML?logo=pypi&logoColor=white&label=PyYAML)](https://pypi.org/project/PyYAML/)

---
