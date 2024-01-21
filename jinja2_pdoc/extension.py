from functools import lru_cache
from typing import Dict

import jinja2

from jinja2_pdoc.wrapper import Module, PdocStr


class Jinja2Pdoc(jinja2.ext.Extension):
    """
    extension to include source code directly from python modules into
    jinja2 templates with `{% pdoc module:object:pdoc_attr.str_attr %}`
    """

    tags = {"pdoc"}

    def parse(self, parser: jinja2.parser.Parser) -> jinja2.nodes.Node:
        """
        parse the arguments following the tag `pdoc` and return a node with the
        formatted source code or docstring.
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
        Parse a line of the form `module:name:__attr__` and return a dict with
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

        try:
            pdoc["module"], line = line.split(":", 1)
        except ValueError:
            pdoc["module"] = line
            pdoc["name"] = ""
            pdoc["attr"] = "source"
            return pdoc

        try:
            pdoc["name"], line = line.split(":", 1)
        except ValueError:
            pdoc["name"] = line
            pdoc["attr"] = "source"
            return pdoc

        try:
            attr, frmt = line.split(".", 1)
        except ValueError:
            pdoc["attr"] = line.strip("_") or "source"
        else:
            pdoc["attr"] = attr.strip("_") or "source"
            frmt = frmt.strip("_")
            if frmt:
                pdoc["frmt"] = frmt

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
        >>> PdocJinja2._pdoc_jinja2("pathlib:Path.open:__docstring__")
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
