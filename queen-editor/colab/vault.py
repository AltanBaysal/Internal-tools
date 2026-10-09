"""The notebook's reads from Colab's vault -- its Secrets panel.

GITHUB_TOKEN is read in CONFIG instead: the clone needs it, and this module comes with the clone.
"""


def read_secret(read, name):
    """(value, problem): the secret read with `read` -- the notebook's userdata.get -- and trimmed, as
    the paste carries the newline, with problem None; or "" and the sentence saying why there is none,
    the read's own error included. Nothing is printed: whether a missing secret is worth a line is the
    caller's to say."""
    try:
        value = (read(name) or "").strip()
    except Exception as e:
        return "", f"{name} okunamadı — {type(e).__name__}: {e}"
    if not value:
        return "", f"{name} boş"
    return value, None
