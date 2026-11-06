import logging
import re
from pathlib import Path

import pytest

from core.log import start_log

pytestmark = pytest.mark.usefixtures("restore_root_logger")


def test_a_line_reaches_the_file_with_its_utc_time(tmp_path: Path) -> None:
    file = tmp_path / "core.log"
    start_log(file)

    logging.getLogger("core.jobs").info("job 4401 done in 12.5 s")

    line = file.read_text(encoding="utf-8")
    assert re.fullmatch(
        r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ INFO core\.jobs: job 4401 done in 12\.5 s\n", line
    )


def test_the_folder_is_made_when_missing(tmp_path: Path) -> None:
    file = tmp_path / "disk" / "core.log"
    start_log(file)

    logging.getLogger("core").warning("x")

    assert file.exists()


def test_a_restart_appends_to_what_is_there(tmp_path: Path) -> None:
    file = tmp_path / "core.log"
    file.write_text("before\n", encoding="utf-8")
    start_log(file)

    logging.getLogger("core").info("after")

    assert file.read_text(encoding="utf-8").startswith("before\n")
    assert file.read_text(encoding="utf-8").endswith("core: after\n")


def test_starting_twice_writes_each_line_once(tmp_path: Path) -> None:
    file = tmp_path / "core.log"
    start_log(file)
    start_log(file)

    logging.getLogger("core").info("once")

    assert file.read_text(encoding="utf-8").count("once") == 1


def test_the_console_gets_the_same_lines(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    start_log(tmp_path / "core.log")

    logging.getLogger("core").info("seen")

    assert "core: seen" in capsys.readouterr().err
