import re
import textwrap
from functools import cached_property
from pathlib import Path
from typing import Any, Union

import autopep8
import pdoc


class Function(pdoc.doc.Function):
    """
    A wrapper __class__ to cast an incance of `pdoc.doc.Function`
    to enhance it with new methods
    """

    _regex_doc = re.compile(
        r"^\s*?(?P<doc>\"{3}|\'{3}).*?(?P=doc)\s*$",
        re.MULTILINE | re.DOTALL,
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

    def get(self, name: str) -> Union[Function, None]:
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
    inhertits from `str` with a `dedent` method
    """

    _regex_doc = re.compile(
        r"^(?:#!.*?)?(?P<doc>\"{3}|\'{3}).*?(?P=doc)\s*$",
        re.MULTILINE | re.DOTALL,
    )

    def dedent(self) -> "PdocStr":
        """
        remove common whitespace from the left of every line in the string,
        see `textwrap.dedent` for more information.
        """
        s = textwrap.dedent(self)
        return self.__class__(s)

    def indent(self) -> "PdocStr":
        """
        remove leading spaces and change indent size to 2 spaces, instead of 4.
        """
        s = autopep8.fix_code(self.dedent(), options={"indent_size": 2})
        return self.__class__(s)

    def nodoc(self) -> "PdocStr":
        """
        remove shebang and docstring and from the string
        """
        s = self._regex_doc.sub("", self.dedent(), 1)

        return self.__class__(s.strip("\n"))

    def __getattribute__(self, name: str) -> Any:
        """
        get all known attributes and cast `str` to `PdocStr`
        """
        attr = super().__getattribute__(name)

        if callable(attr):

            def wrapper(*args, **kwargs):
                result = attr(*args, **kwargs)
                if isinstance(result, str):
                    cls = object.__getattribute__(self, "__class__")
                    return cls(result)
                return result

            return wrapper

        return attr
