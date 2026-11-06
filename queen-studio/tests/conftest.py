import logging
from collections.abc import Iterator

import pytest


@pytest.fixture
def restore_root_logger() -> Iterator[None]:
    """For a test that starts the log: the root logger is the process's, and pytest's own."""
    root = logging.getLogger()
    handlers, level = root.handlers[:], root.level
    yield
    for handler in root.handlers:
        if handler not in handlers:
            handler.close()
    root.handlers[:], root.level = handlers, level
