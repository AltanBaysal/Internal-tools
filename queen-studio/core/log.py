"""Where the core's log goes: a file on the machine's own disk, and the console.

Every logger reaches the root, Uvicorn's too once it is told to set up none of its own, so this
one setting covers the whole process. Showing the file in the notebook and sending it to Drive
every five minutes is v1-25's.
"""

import logging
import time
from pathlib import Path


def start_log(file: Path) -> None:
    file.parent.mkdir(parents=True, exist_ok=True)
    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s %(name)s: %(message)s", datefmt="%Y-%m-%dT%H:%M:%SZ"
    )
    formatter.converter = time.gmtime  # UTC, as every time the core gives (step 6)
    handlers: list[logging.Handler] = [
        logging.FileHandler(file, encoding="utf-8"),
        logging.StreamHandler(),
    ]
    for handler in handlers:
        handler.setFormatter(formatter)
    # force: a second start replaces the handlers rather than writing every line twice.
    logging.basicConfig(level=logging.INFO, handlers=handlers, force=True)
