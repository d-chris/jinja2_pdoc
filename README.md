# jinja2-pdoc

---

[`jinja2`](https://www.pypi.org/project/jinja2) extension based on [`pdoc`](https://pypi.org/project/pdoc/) to embedd python code directly from modules or files into your `jinja` template.

## Installation

```cmd
pip install jinja2_pdoc
```

##  Usage

- [CLI](#command-line)
- [Library](#library)

## Syntax

```jinja2
{% pdoc <module>::<object>:<pdoc_attr[.str_attr]> %}
```

### `<module>`

module name or path to python file

- `pathlib`
- `examples/example.py`

Example:

```jinja2
{% pdoc pathlib %}
```

### `<object>`

class and/or function names, eg. from `pathlib`

- `Path`
- `Path.open`

Example:

```jinja2
{% pdoc pathlib::Path %}
```

### `<pdoc_attr>`

`pdoc` attributes

- `docstring` - docstring of the object
- `source` - source code of the object
- `code` - plane code from functions, without def and docstring

Example:

```jinja2
{% pdoc pathlib::Path:docstring %}
```

### `str_attr`

optional `str` functions can be added to `<pdoc_attr>` with a dot

- `dedent` - removes common leading whitespace, see `textwrap.dedent`
- `upper` - converts to upper case
- `lower` - converts to lower case
- ...

Example:

```jinja2
{% pdoc pathlib::Path.open:code.dedent %}
```

## Examples

### Command Line

```cmd
>>> jinja2pdoc --help

Usage: jinja2pdoc [OPTIONS] INPUT [OUTPUT]

  Render jinja2 templates from a input directory or file and write to a output
  directory.

  if the `input` is a directory, all files with a matching `pattern` are
  renderd.

  if no `output` is given, the current working directory is used.

Options:
  -p, --pattern TEXT  template search pattern for directories
  -f, --force         overwrite existing files
  --help              Show this message and exit.
```

### Library

python code to render a template directly from a string

```python
from jinja2_pdoc import jinja2, PdocJinja2

env = jinja2.Environment(extensions=[PdocJinja2])

s = """
    # jinja2-pdoc

    embedd python code directly from pathlib using a jinja2 extension based on pdoc

    ## docstring from pathlib.Path

    {% pdoc pathlib::Path:docstring %}

    ## source from pathlib.Path.open

    ```python
    {% pdoc pathlib::Path.open:source.dedent -%}
    ```
    """

code = env.from_string(textwrap.dedent(s)).render()

Path("example.md").write_text(code)

```

### Result

output of the [code](#library) above

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
