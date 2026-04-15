import json
import re

_FENCE_RE = re.compile(r"```(?:json)?\s*\n?")
_BRACKET_RE = re.compile(r"\{.*\}|\[.*\]", re.DOTALL)


def parse_json_output(raw: str) -> list | dict:
    cleaned = _FENCE_RE.sub("", raw).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        pass
    for match in _BRACKET_RE.finditer(cleaned):
        try:
            return json.loads(match.group(0))
        except (json.JSONDecodeError, ValueError):
            continue
    raise json.JSONDecodeError("No valid JSON found", cleaned, 0)
