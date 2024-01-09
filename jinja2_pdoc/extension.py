import re
import textwrap
from functools import cached_property, lru_cache
from pathlib import Path
from typing import Any, Dict, Union

import jinja2
import pdoc


class Function(pdoc.doc.Function):
    """
    A wrapper __class__ to cast an incance of `pdoc.doc.Function`
    to enhance it with new methods
    """

    _regex_doc = re.compile(
        r"^\s*?(?P<doc>[\"\']{3}).*?(?P=doc)\s*$", re.MULTILINE | re.DOTALL
    )
    """regex to match a docstring"""

    _regex_def = re.compile(r"def.*?\(.*?\)(?:.*?)?:\s*$", re.MULTILINE | re.DOTALL)
    """regex to match a function definition"""

    def __new__(cls, obj: pdoc.doc.Function) -> Union["Function", None]:
        """
        create a new instance of `Function` with the wrapped object
        """
        if obj is None:
            return obj

        return super().__new__(cls)

    def __init__(self, obj: pdoc.doc.Function) -> None:
        """
        store the object to wrap
        """
        self.__obj = obj

    def __getattribute__(self, name: str) -> Any:
        """
        get all known attributes and cast `str` to `PdocStr`
        """
        attr = super().__getattribute__(name)

        if isinstance(attr, str):
            attr = PdocStr(attr)

        return attr

    def __getattr__(self, name):
        """
        get all unknown attributes from the wrapped object
        """
        attr = getattr(self.__obj, name)

        return attr

    @cached_property
    def code(self) -> "PdocStr":
        """
        returns the source without docstring and function definition
        """
        code = self._regex_def.sub("", self.source, 1)
        code = self._regex_doc.sub("", code, 1)

        return PdocStr(code.strip("\n"))


class Module(pdoc.doc.Module):
    """
    Subclass of `pdoc.doc.Module` to override the `get` method to return a instance of
    `Function` instead of `pdoc.doc.Function`
    """

    def get(self, name: str) -> Function:
        return Function(super().get(name))

    @classmethod
    def from_name(cls, name: str) -> "Module":
        """
        create a `Module` instance from a module name or a file path
        """
        try:
            return super().from_name(name)
        except RuntimeError:
            path = Path(name).with_suffix("")
            name = ".".join(path.parts)

            return super().from_name(name)


class PdocStr(str):
    """
    inhertits from `str` with a `dedent` property
    """

    def dedent(self) -> str:
        """
        dedent the common whitespace from the left of every line in the string,
        see `textwrap.dedent` for more information.
        """
        return textwrap.dedent(self)


class PdocJinja2(jinja2.ext.Extension):
    tags = {"pdoc"}

    @property
    def tag(self) -> str:
        """
        return the current tag and remove it from the list
        """
        tag, *_ = self.tags
        return tag

    def parse(self, parser: jinja2.parser.Parser) -> jinja2.nodes.Node:
        """
        replace a `{{ pdoc module::class:__attr__ }}` with the source code from a
        the python module. `__attr__` is optional and defaults to `source`, see
        `pdoc.doc.Functions` which attributes are available.
        """
        lineno = next(parser.stream).lineno

        tokens = []
        while parser.stream.current.type != "block_end":
            tokens.append(parser.stream.current.value)
            parser.stream.skip(1)

        arg = "".join(tokens)
        try:
            text = self._pdoc_jinja2(arg)
        except ValueError:
            raise jinja2.TemplateSyntaxError(f"syntax error in '{arg}'", lineno)
        except AttributeError:
            raise jinja2.TemplateAssertionError(f"could not resolve '{arg}'", lineno)

        content = jinja2.nodes.Const(text)

        return jinja2.nodes.Output([content]).set_lineno(lineno)

    @staticmethod
    def _pdoc_syntax(line: str) -> Dict[str, str]:
        """
        Parse a line of the form `module::name:__attr__` and return a dict with
        corresponding keys and values.

        - `module` is the module name or file path
        - `name` is the name of the function or class
        - `attr` is the optional attribute which will be called from the pdoc object.
        Default: `source`

        Example:
        >>> PdocJinja2._pdoc_syntax("pathlib::Path.open")
        {'module': 'pathlib', 'name': 'Path.open', 'attr': 'source'}
        """
        pdoc = {}

        parts = line.split("::")

        if len(parts) == 1:
            raise ValueError("Syntax Error: 'module::name:__attr__', attr is optional")

        module = parts[0]
        name, *code = parts[1].split(":")

        pdoc["module"] = module.strip()
        pdoc["name"] = name.strip()
        try:
            pdoc["attr"] = code[0].strip().strip("_") or "source"
        except IndexError as e:
            pdoc["attr"] = "source"

        attr, *frmt = pdoc["attr"].split(".")

        if frmt:
            pdoc["attr"] = attr.strip("_")
            pdoc["frmt"] = frmt[0].strip().strip("_")

        return pdoc

    @staticmethod
    @lru_cache
    def _pdoc_load(module: str) -> Module:
        """
        Load a module and return a subclass of `pdoc.doc.Module` instance.
        """
        return Module.from_name(module)

    @classmethod
    def _pdoc_jinja2(cls, line: str) -> PdocStr:
        """
        Return the code segment of a function or class from a module.

        Example:
        >>> PdocJinja2._pdoc_jinja2("pathlib::Path.open:__docstring__")
        Open the file pointed by this path and return a file object, as
        the built-in open() function does.
        """
        cfg = cls._pdoc_syntax(line)

        doc = cls._pdoc_load(cfg["module"])

        if cfg["name"]:
            s = getattr(doc.get(cfg["name"]), cfg["attr"])
        else:
            s = getattr(doc, cfg["attr"])

        if "frmt" in cfg.keys():
            s = getattr(PdocStr(s), cfg["frmt"])

            if callable(s):
                s = s()

        return PdocStr(s)


def main():
    env = jinja2.Environment(extensions=[PdocJinja2])

    s = """
        # jinja2-pdoc

        embedd python code directly from pathlib using a jinja2 extension based on pdoc

        ## docstring from pathlib.Path
        {% pdoc pathlib::Path:docstring.dedent -%}

        ## source from pathlib.Path.open
        ```python
        {% pdoc pathlib::Path.open:source.dedent -%}
        ```
        """

    code = env.from_string(textwrap.dedent(s)).render()

    Path("jinja2_pdoc.md").write_text(code)

    return code


if __name__ == "__main__":
    main()
