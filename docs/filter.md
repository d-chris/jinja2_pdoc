Filter to use in `jinja2` template.

### include

`Environment.include` - returns the content of the file.

```jinja
{{ "path/to/file" | include(enc="utf-8") }}
```

### shell

`Environment.shell` - run shell command and return the selected result from `subprocess.CompletedProcess`.

```jinja
{{ "python --version" | shell(promt=">>> %s\n") }}
```

### strip

`Environment.strip` - remove leading and trailing whitespace and newlines from a string.

```jinja
{{ "path/to/file" | include | strip }}
```
