"""Let a project's folder be renamed under a run, and keep the run pointing at it.

This is the port the projects feature is handed, the same way `halt` is: renaming a project is that
feature's work, and the worker that might be inside the folder belongs to this one. They meet only
in main.py.
"""


def follow_rename(runner, old, new, move):
    """Run `move` with no write able to straddle it, then let the run and its status follow."""
    answer = runner.named.moved(old, new, move)
    runner.rename(old, new)
    return answer
