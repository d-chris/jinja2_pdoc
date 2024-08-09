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
