import pytest

from backend.features.projects.domain import name_rules

FORBIDDEN_MESSAGE = 'Proje adında şu karakterler kullanılamaz: / \\ : * ? " < > |'


@pytest.mark.parametrize(
    "name",
    ["düğün", "kapak çekimi", "lookbook-mayıs", "test_2", "a", "ü" * 64],
)
def test_valid_names_return_none(name):
    assert name_rules.validate(name) is None


@pytest.mark.parametrize(
    "name, expected",
    [
        ("", "Proje adı boş olamaz."),
        ("   ", "Proje adı boş olamaz."),
        (" düğün", "Proje adı boşlukla başlayamaz veya bitemez."),
        ("düğün ", "Proje adı boşlukla başlayamaz veya bitemez."),
        ("ü" * 65, "Proje adı en fazla 64 karakter olabilir."),
        ("foto/deneme", FORBIDDEN_MESSAGE),
        ("C:\\yol", FORBIDDEN_MESSAGE),
        ("a\tb", FORBIDDEN_MESSAGE),
        (".gizli", "Proje adı nokta ile başlayamaz veya bitemez."),
        ("düğün.", "Proje adı nokta ile başlayamaz veya bitemez."),
        ("..", "Proje adı nokta ile başlayamaz veya bitemez."),
    ],
)
def test_invalid_names_return_message(name, expected):
    assert name_rules.validate(name) == expected
