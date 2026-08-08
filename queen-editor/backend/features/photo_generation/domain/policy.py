"""When does the queue stop, and whose failure was it? One pure decision, in one file.

Design v2's rule (difference report 8.3): a failure the run cannot get past is tried again on the
SAME frame, up to three times, and only then does the queue stop -- so one outage costs one frame's
attempts instead of three frames. The frame writes no line while this happens: it stays owed, and
Kaldığı yerden devam et picks up exactly where the queue left off.

The old rule counted three failed frames in a row and singled out model loader failures. Both are
gone: the only split left is who failed, and that is not a guess about the cause.
"""

MAX_ATTEMPTS = 3


def is_frame_fault(exc):
    """Whose failure is this -- the frame's, or the run's?

    The frame's when the renderer answered and reported that this render failed; the run's when no
    answer came at all (unreachable server, HTTP error, timeout, an output that made no sense). The
    renderer marks its own exception; getattr rather than isinstance because the domain must not
    import the service that raises it.
    """
    return getattr(exc, "frame_level", False)


def stop_reason(attempts):
    """Failed attempts on the frame being rendered -> user-facing reason, or None to keep going."""
    if attempts >= MAX_ATTEMPTS:
        return f"Aynı kare {MAX_ATTEMPTS} kez denendi — üretim durduruldu"
    return None
