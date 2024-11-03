from jinja2_pdoc import Environment

env = Environment()

template = """\
# jinja2-pdoc

embedd python code directly from pathlib using a jinja2 extension based on pdoc

## docstring from pathlib.Path

{% pdoc pathlib:Path:docstring %}

## source from pathlib.Path.open

```python
{% pdoc pathlib:Path.open:source.indent -%}
```
"""

code = env.from_string(template).render()

print(code)
