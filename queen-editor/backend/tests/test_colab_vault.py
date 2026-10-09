"""The notebook's one read from Colab's vault, run rather than read (madde 438).

The read was written four times in the notebook -- try, userdata.get, strip, except -- and three of
them come here: CIVITAI_COOKIE, DEEPSEEK_API_KEY and HF_TOKEN. GITHUB_TOKEN stays in CONFIG, which
runs before the clone brings colab/. The vault is faked: a function standing in for userdata.get.
"""
import importlib

import pytest

SECRET = "sk-" + "s" * 32


class SecretNotFoundError(Exception):
    """What Colab's userdata.get raises for a secret the vault does not hold."""


@pytest.fixture
def vault():
    """The module. Imported here rather than at the top: a module that is not there yet fails each
    test on its own instead of the whole file."""
    return importlib.import_module("colab.vault")


def test_a_secret_is_read_by_its_name_and_trimmed(vault):
    """The paste is what carries the newline."""
    asked = []

    value, problem = vault.read_secret(lambda name: asked.append(name) or f" {SECRET}\n",
                                       "DEEPSEEK_API_KEY")

    assert asked == ["DEEPSEEK_API_KEY"], f"Kasadan böyle okunmadı: {asked}"
    assert (value, problem) == (SECRET, None), f"Okuma böyle döndü: {(value, problem)}"


def test_a_secret_that_cannot_be_read_says_what_the_read_raised(vault):
    """The read's own error, never a guessed cause."""
    def read(name):
        raise SecretNotFoundError(f"Secret {name} does not exist.")

    value, problem = vault.read_secret(read, "HF_TOKEN")

    assert value == "", f"Okunamayan secret bir değer verdi: {value!r}"
    assert problem == "HF_TOKEN okunamadı — SecretNotFoundError: Secret HF_TOKEN does not exist.", \
        f"Sorun böyle söylendi: {problem!r}"


@pytest.mark.parametrize("stored", ["", "  \n", None])
def test_an_empty_secret_is_said_to_be_empty(vault, stored):
    value, problem = vault.read_secret(lambda name: stored, "CIVITAI_COOKIE")

    assert (value, problem) == ("", "CIVITAI_COOKIE boş"), f"Boş secret böyle döndü: {(value, problem)}"


def test_reading_a_secret_prints_nothing(vault, capsys):
    """What is said, and whether at all, is the caller's: the cookie and the DeepSeek key are read as
    silently as ever, and the value itself is never printed."""
    vault.read_secret(lambda name: SECRET, "DEEPSEEK_API_KEY")
    vault.read_secret(lambda name: None, "CIVITAI_COOKIE")

    assert capsys.readouterr().out == "", "Kasadan okuma konsola bir şey bastı"
