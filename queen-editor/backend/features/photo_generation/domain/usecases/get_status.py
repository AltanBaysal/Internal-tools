"""What the UI polls: the runner's current state, unchanged."""


def get_status(runner):
    return runner.status()
