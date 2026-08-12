"""Ask the running install to stop.

Nothing is cleaned up here: the fetcher throws away its own half file the moment it is stopped, so
the cancel is a flag and not a second place that knows what a partial download looks like.
"""


def cancel_install(runner):
    runner.request_cancel()
