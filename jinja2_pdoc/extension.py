import textwrap
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict

import jinja2

from jinja2_pdoc.wrapper import PdocStr, Module


class Jinja2Pdoc(jinja2.ext.Extension):
    tags = {"pdoc"}

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
