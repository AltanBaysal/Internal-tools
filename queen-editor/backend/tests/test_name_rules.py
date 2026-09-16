import pytest

from backend.features.projects.domain import name_rules

FORBIDDEN_MESSAGE = 'Proje adında şu karakterler kullanılamaz: / \\ : * ? " < > |'
RESERVED_MESSAGE = "Bu ad ayrılmış: arşivlenen projeler orada duruyor. Başka bir ad dene."


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
        # Madde 221: the archive is a folder under the same root, so its name cannot also be a
        # project's. Every case of it, because the repo runs on Windows too and "Arsiv" is the same
        # folder there.
        ("arsiv", RESERVED_MESSAGE),
        ("Arsiv", RESERVED_MESSAGE),
        ("ARSIV", RESERVED_MESSAGE),
    ],
)
def test_invalid_names_return_message(name, expected):
    assert name_rules.validate(name) == expected


def test_the_reserved_name_is_the_folder_the_archive_really_uses():
    """Written down once. A test spelling the name itself would keep passing after the folder was
    renamed, and the project it then failed to reserve would be the one that breaks the list."""
    assert name_rules.validate(name_rules.ARCHIVE_DIR) == RESERVED_MESSAGE
