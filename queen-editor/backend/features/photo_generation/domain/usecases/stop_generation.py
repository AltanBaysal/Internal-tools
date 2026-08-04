"""Ask the running batch to stop and cut the render in flight."""


def stop_generation(runner, interrupt):
    """Raise the flag, interrupt ComfyUI, return the current state (idle is a no-op).

    The flag alone already ends the batch between frames; the interrupt only shortens the frame
    in flight, so a dead ComfyUI must not fail the request.
    """
    runner.request_stop()
    try:
        interrupt()
    except Exception:
        pass
    return runner.status()
