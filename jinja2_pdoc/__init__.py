"""
.. include:: ../README.md
"""

import jinja2
import pdoc

from jinja2_pdoc.cli import jinja2pdoc
from jinja2_pdoc.environment import Environment
from jinja2_pdoc.extension import Jinja2Pdoc

__all__ = [
    "Jinja2Pdoc",
    "jinja2",
    "pdoc",
    "Environment",
    "jinja2pdoc",
]
