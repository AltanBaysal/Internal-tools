"""Every code cell ends with how long it took (madde 312).

The timer is the one piece of the notebook this suite runs. It has to be on before the clone -- the
Drive cell's time is one the user asked for -- so it cannot come from colab/, and it opens CONFIG,
the first code cell. Cut out from its heading to the next one, it runs here alone, with IPython's
event manager and the clock faked. The rest of this file reads the notebook, like the files next to
it.
"""
import json
import os
import sys
import time
import types

TOOL = os.path.dirname(          # queen-editor
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
NOTEBOOK = os.path.join(TOOL, "queeneditor.ipynb")
HEADING = "# === Cell timer ==="


def _code_cells():
    """Every code cell's source, in the order Run all runs them."""
    with open(NOTEBOOK, encoding="utf-8") as handle:
        doc = json.load(handle)
    return ["".join(cell.get("source", "")) for cell in doc.get("cells", [])
            if cell.get("cell_type") == "code"]


def _cell(marker):
    return next((source for source in _code_cells() if marker in source), "")


def _timer_section():
    """The timer, from its heading to the next one: the part of CONFIG that runs here."""
    config = _cell("# === CONFIG ===")
    start = config.find(HEADING)
    if start == -1:
        return ""
    end = config.find("# ===", start + len(HEADING))
    return config[start:] if end == -1 else config[start:end]


class _Events:
    """IPython's event manager, as much of it as the timer touches."""

    def __init__(self):
        self.callbacks = {"pre_run_cell": [], "post_run_cell": []}

    def register(self, event, function):
        self.callbacks[event].append(function)

    def unregister(self, event, function):
        self.callbacks[event].remove(function)

    def trigger(self, event):
        for function in list(self.callbacks[event]):
            function(None)


def _run_timer(monkeypatch, events):
    """Runs the timer the way CONFIG does, against `events`. Hands back the clock it reads and the
    names it leaves in the notebook's namespace."""
    clock = [0.0]
    monkeypatch.setattr(time, "perf_counter", lambda: clock[0])
    monkeypatch.setitem(sys.modules, "IPython",
                        types.SimpleNamespace(get_ipython=lambda: types.SimpleNamespace(events=events)))
    names = {}
    exec(_timer_section(), names)
    return clock, names


def test_every_cell_ends_with_how_long_it_took(monkeypatch, capsys):
    """Under every cell, as the user asked -- "uzun süren başka cell'ler de var galiba" (madde 312).
    IPython calls one hook as a cell starts and one after it has printed everything else, so the line
    lands last."""
    assert _timer_section(), "CONFIG'de sayaç bölümü yok"
    events = _Events()
    clock, _names = _run_timer(monkeypatch, events)
    capsys.readouterr()

    for start, end in ((100.0, 210.4), (300.0, 308.2)):
        clock[0] = start
        events.trigger("pre_run_cell")
        clock[0] = end
        events.trigger("post_run_cell")

    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 2 and all(line.startswith("⏱") for line in lines), f"Satırlar: {lines}"
    assert lines[0].endswith("Hücre 1 dk 50 sn sürdü") and lines[1].endswith("Hücre 8 sn sürdü"), \
        f"Satırlar: {lines}"


def test_running_config_again_leaves_one_timer(monkeypatch, capsys):
    """CONFIG is the cell run again after a box is changed. Each run hooks the timer in anew; without
    the old hooks taken off, every cell would print its time twice."""
    events = _Events()
    _run_timer(monkeypatch, events)
    clock, _names = _run_timer(monkeypatch, events)
    capsys.readouterr()

    events.trigger("pre_run_cell")
    clock[0] = 5.0
    events.trigger("post_run_cell")

    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 1, f"Bir hücre süresini {len(lines)} kez yazdı: {lines}"


def test_the_timer_is_the_first_thing_the_notebook_runs():
    """The Drive cell's time holds the wait for the permission window, and the clone comes before the
    notebook's own code does: only the top of the first code cell runs before both -- and CONFIG's own
    time is counted whole."""
    assert _code_cells()[0].startswith(HEADING), "Sayaç ilk kod hücresinin başında değil"


def test_a_cell_can_ask_how_long_it_has_run_so_far(monkeypatch):
    """The last cell never ends -- it follows the server's log -- so its line would never come. It
    tells its time where the link appears instead, asking the timer (madde 312)."""
    events = _Events()
    clock, names = _run_timer(monkeypatch, events)

    clock[0] = 100.0
    events.trigger("pre_run_cell")
    clock[0] = 114.3

    assert "cell_elapsed" in names, "Sayaç hücrenin o ana kadarki süresini vermiyor"
    assert names["cell_elapsed"]() == "14 sn", f"Süre böyle okunmuyor: {names['cell_elapsed']()}"


def test_the_link_says_how_long_it_took():
    """The line reads "Link 14 sn'de hazır", right above the link (madde 312)."""
    flask = _cell("# === Start Flask")
    said = next((line for line in flask.splitlines() if "cell_elapsed()" in line), "")

    assert "hazır" in said, "Link hücresi süresini söylemiyor"
    assert -1 < flask.find(said) < flask.find("🔗 Queen Editor"), "Süre linkin üstünde değil"
