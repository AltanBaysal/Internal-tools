"""The notebook installs what the panel counts.

The app reads a producer's group off the disk and the notebook is what puts it there
(FOUNDATION 9). Nothing connects the two lists at runtime, so a file added to the group and
forgotten in the notebook would leave the panel saying "kurulu değil" for good, with nobody able to
see why. This test is that connection.
"""
import os

from backend.features.producers.domain.model_groups import GROUPS

NOTEBOOK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "app.ipynb")


def _notebook():
    with open(NOTEBOOK, encoding="utf-8") as handle:
        return handle.read()


def test_every_photo_file_the_panel_counts_is_fetched_by_the_notebook():
    text = _notebook()

    missing = [row["name"] for row in GROUPS["photo"] if row["name"] not in text]

    assert missing == [], f"Defter bu dosyaları indirmiyor: {missing}"


def test_the_gated_files_are_fetched_the_way_that_works():
    """curl, not aria2c: Civitai redirects to its store, which answers 403 if the login cookie
    travels with the request. aria2c forwards it; curl drops it when the host changes."""
    text = _notebook()

    assert "civitai_probe" in text, "Ağır indirmeden önce kapılı erişim yoklanmalı"
    assert "civitai.red/api/download/models" in text
