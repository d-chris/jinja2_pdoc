
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
- `nodoc` - removes shebang and docstring

Example:

```jinja2
{% pdoc pathlib:Path.open:code.dedent %}
```
