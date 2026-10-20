"""Project name validation -- the single source of truth for the rules.

Pure: no filesystem, no Flask, no schema knowledge. The name becomes a Drive folder name, so the
rules are the filesystem's plus a length cap. Turkish letters, spaces, dashes and underscores are
allowed on purpose ("kapak çekimi"). Messages are user-facing, so they are Turkish; the frontend
prints them verbatim and keeps no copy of the rules.
"""

MAX_LENGTH = 64
FORBIDDEN_CHARS = '/\\:*?"<>|'
# Where madde 221 moved archived projects. The name stays reserved because old installs still have
# that folder, and the list would show it as a project.
ARCHIVE_DIR = "arsiv"
# Where exports land, beside the projects (madde 473). Named here because this feature is the one
# that says which folders under the root are projects; main.py hands the same name to the photo
# store, so the folder exports use and the name kept from projects cannot drift apart.
EXPORTS_DIR = "Exportlar"
# Matched whatever the case: the app runs on Colab's Linux but the repo is developed on Windows,
# where "Arsiv" and "arsiv" are one folder.
_RESERVED = {ARCHIVE_DIR.casefold(), EXPORTS_DIR.casefold()}


def is_reserved(name):
    """Whether the name is one of the app's own folders under the root -- which is not a project,
    whatever a URL calls it."""
    return name.casefold() in _RESERVED


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
    if is_reserved(name):
        # The sentence does not say why: what a name is held back for is the app's own folder, which
        # is not the user's business, and one sentence serves both names.
        return "Bu ad ayrılmış, başka bir ad dene."
    return None


def archive_taken(name):
    """What a user is told when the name they asked for is sitting in the archive (madde 223).

    Its own sentence rather than the usual "bu ad zaten kullanılıyor": that one would send someone
    looking among their projects for a name that is not there. Both ways out are named, because both
    are real -- pick another name, or take that project out first.

    Here rather than in either use case: creating and renaming share it, and one situation gets one
    sentence whichever window the user is in.
    """
    return f"Arşivde {name} adlı bir proje var. Başka bir ad seç ya da önce onu arşivden çıkar."
