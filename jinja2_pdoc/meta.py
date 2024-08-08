import re
from typing import Any, Dict

import yaml


def frontmatter(content: str) -> Dict[str, Any]:
    match = re.search(
        r"^(.*?)(?:<!|-)--(.*?)--(?:>|-)",
        content,
        re.MULTILINE | re.DOTALL,
    )

    try:
        if any(line.strip() for line in match.group(1).split("\n")):
            return {}

        meta = yaml.safe_load(match.group(2))

        if not isinstance(meta, dict):
            return {}
    except AttributeError:
        return {}

    return meta
