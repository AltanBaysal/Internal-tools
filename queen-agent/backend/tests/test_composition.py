"""What main.py wires together -- Madde 62's half of it: where the API key comes from.

Asked by reading the file rather than importing it. The composition root is the one file whose whole
content is wiring, and importing it builds a real app against the user's own data root -- a test that
does that is a test with a side effect on the machine it runs on. Reading a file to ask what it says
is not new here either: test_notebook.py is nothing else.
"""
import os

_QUEEN_AGENT = os.path.dirname(          # queen-agent
    os.path.dirname(                     # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests

MAIN = os.path.join(_QUEEN_AGENT, "main.py")
SETTINGS_FEATURE = os.path.join(_QUEEN_AGENT, "backend", "features", "settings")


def _main():
    with open(MAIN, encoding="utf-8") as handle:
        return handle.read()


def test_the_key_is_taken_from_config():
    """One road, and this is where it is chosen. Stated as what the file DOES rather than only as
    what it avoids: a rule written as an absence alone can never fail."""
    assert "config.XAI_API_KEY" in _main(), "Anahtar config'ten alınmıyor"


def test_no_settings_feature_is_wired_in():
    """The engine used to read the key out of a saved settings file. That file was served back in
    plain text over a link with no password, which is why it is gone rather than merely unused."""
    assert "features.settings" not in _main(), "Settings özelliği hâlâ bağlanıyor"


def test_the_settings_feature_is_gone_from_the_tree():
    """Not just unwired -- deleted. Left on disk it is a working HTTP surface waiting for the next
    person who wires a blueprint list without reading this."""
    assert not os.path.isdir(SETTINGS_FEATURE), f"Hâlâ duruyor: {SETTINGS_FEATURE}"
