"""Project name validation -- the single source of truth for the rules.

Pure: no filesystem, no Flask, no schema knowledge. The name becomes a Drive folder name, so the
rules are the filesystem's plus a length cap. Turkish letters, spaces, dashes and underscores are
allowed on purpose ("kapak çekimi"). Messages are user-facing, so they are Turkish; the frontend
prints them verbatim and keeps no copy of the rules.
"""

MAX_LENGTH = 64
FORBIDDEN_CHARS = '/\\:*?"<>|'


def validate(name):
    """Return a Turkish error message, or None when the name is usable."""
    if not isinstance(name, str) or not name.strip():
        return "Proje adı boş olamaz."
    if name != name.strip():
        return "Proje adı boşlukla başlayamaz veya bitemez."
    if len(name) > MAX_LENGTH:
        return f"Proje adı en fazla {MAX_LENGTH} karakter olabilir."
    # Control characters break folder names as badly as the reserved punctuation does.
    if any(ch in FORBIDDEN_CHARS or ord(ch) < 32 for ch in name):
        return 'Proje adında şu karakterler kullanılamaz: / \\ : * ? " < > |'
    if name.startswith(".") or name.endswith("."):
        return "Proje adı nokta ile başlayamaz veya bitemez."
    return None
