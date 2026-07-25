"""Ask the running batch to stop after the frame it is on."""


def stop_generation(runner):
    """Raise the flag and return the current state (idle is a no-op)."""
    runner.request_stop()
    return runner.status()
