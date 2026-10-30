"""Let a project's folder be renamed under a run, and keep the run pointing at it.

This is the port the projects feature is handed, the same way `halt` is: renaming a project is that
feature's work, and the worker that might be inside the folder belongs to this one. They meet only
in main.py.
"""


def follow_rename(runner, plan_store, old, new, move):
    """Run `move` with no write able to straddle it, then let the run and its status follow.

    Under the project's write gate (madde 522): every door that queues work writes its job and
    claims or joins the worker under that gate, so a press falls wholly before the move -- its job,
    its claim and the holder's name all in the old folder, carried to the new one by what follows
    -- or wholly after it, and finds no project. Taken without, a press could write into the old
    folder and claim after the move, and its run read a folder that was no longer there.
    """
    with plan_store.held(old):
        answer = runner.named.moved(old, new, move)
        runner.rename(old, new)
    return answer
