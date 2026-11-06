"""The core's identity, kept on the machine's own disk in `core.json` (step 4).

It stays the same while the machine lives, so a restarted core finds the queues whose `runner` it
is. Read once at start; health answers from the value in memory.
"""

import json
import os
import re
import secrets
import string
from pathlib import Path

_FILE = "core.json"
_LETTERS = string.ascii_lowercase + string.digits
_SHAPE = re.compile(r"[a-z0-9]{10}")


class UnreadableIdentity(Exception):
    """core.json is there but cannot be read; the start stops rather than write over it."""


def core_id(disk: Path) -> str:
    path = disk / _FILE
    try:
        found: object = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return _create(path)
    except (OSError, ValueError) as unreadable:  # JSON and UTF-8 errors are both ValueErrors
        raise UnreadableIdentity(f"{path}: {unreadable}") from unreadable
    match found:
        case {"core": str(identity)} if _SHAPE.fullmatch(identity):
            return identity
        case _:
            raise UnreadableIdentity(
                f'{path}: expected {{"core": "<10 lowercase letters or digits>"}}'
            )


def _create(path: Path) -> str:
    # Written whole beside it, then put in place: a crash mid-write leaves no half file to stop on.
    identity = "".join(secrets.choice(_LETTERS) for _ in range(10))
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(_FILE + ".tmp")
    temporary.write_text(json.dumps({"core": identity}), encoding="utf-8")
    os.replace(temporary, path)
    return identity
