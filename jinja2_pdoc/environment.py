import subprocess
from pathlib import Path
from typing import Callable

import jinja2

from jinja2_pdoc.extension import Jinja2Pdoc


class Environment(jinja2.Environment):
    """
    `jinja2.Environment` with the `Jinja2Pdoc` extension already loaded.

    Example:
    >>> import jinja2_pdoc
    >>> env = jinja2_pdoc.Environment()
    >>> template = '{% pdoc jinja2_pdoc:Jinja2Pdoc:docstring.dedent -%}'
    >>> env.from_string(template).render()
    'extension to include source code directly from python modules into
    jinja2 templates with `{% pdoc module:object:pdoc_attr.str_attr %}`'
    """

    def __init__(self, *args, **kwargs):
        """
        Create a new `Environment` with the preloaded `Jinja2Pdoc` extension.
        """
        super().__init__(*args, **kwargs)
        self.add_extension(Jinja2Pdoc)

        self.add_filter("shell", self.shell)
        self.add_filter("include", self.include)
        self.add_filter("strip", self.strip)

    def add_filter(self, name: str, func: Callable) -> None:
        """
        Add a new filter to the environment.

        Args:
            name (str): The name of the filter.
            func (Callable): The filter function.

        Example:
            >>> env = jinja2_pdoc.Environment()
            >>> env.add_filter('upper', lambda s: s.upper())
            >>> env.from_string('{{ "hello world." | upper }}').render()
            'HELLO WORLD.'
        """
        if not callable(func):
            raise TypeError(f"{func=} is not a callable")

        self.filters[name] = func

    @staticmethod
    def shell(
        cmd: str,
        result: str = "stdout",
        *,
        promt: str = None,
    ) -> str:
        """
        Filter to run a shell command and return the output.

        Args:
            cmd (str): The command to run with `subprocess.run`.
            result (str, optional): The attribute to return from the
                `subprocess.CompletedProcess` instance. Defaults to "stdout".
            promt (str, optional): Format string to include the command before the
                output, e.g. `">>> %s \\n"`. Defaults to None.

        Returns:
            str: The result of the command.

        Example:
            ```jinja2
            {{ "python --version" | shell(promt="$ ") }}
            ```
        """

        process = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
        )

        output = str(getattr(process, result))

        if promt is not None:
            try:
                prefix = promt % cmd
            except TypeError:
                prefix = f"{promt}{cmd}\n"

            output = f"{prefix}\n{output}"

        return Environment.strip(output)

    @staticmethod
    def include(
        file: str,
        enc=None,
        *,
        attr: str = None,
    ) -> str:
        """
        Filter for jinja2 Template to include the content of a file.

        Args:
            file (str): The file to include.
            enc (str, optional): The encoding to use with `pathlib.Path.read_text()`.
            attr (str, optional): The string method to call on the file
                content, e.g. `include(attr="upper")`.

        Returns:
            str: The content of the file.

        Example:
            ```jinja2
            {{ ".pre-commit-hool.yaml" | include }}
            ```
        """

        content = Path(file).read_text(encoding=enc)

        if attr is not None:
            content = getattr(content, attr)()

        return Environment.strip(content)

    @staticmethod
    def strip(text: str, chars: str = "\n ") -> str:
        """
        Strips the specified characters from the beginning and end of the given text.

        Args:
            text (str): The text to be stripped.
            chars (str, optional): The characters to be stripped from the text.
            Defaults to `"\\n "`.

        Returns:
            str: The stripped text.

        Example:
            ```jinja2
            {{ "  hello world.  \\n" | strip }}
            ```
        """
        return text.strip(chars)
