"""The black box every request to Queen AI goes through (madde 416).

The caller asks once and always gets an Answer back, never an exception. A request that came back
with an HTTP error, a malformed or an empty answer, or no answer at all is sent again as it was, up
to five tries in all; when every try failed, the Answer is the last error's own text, marked as a
failure. It never raises because a caller that loops -- an agent -- must not be broken by the
service (v9-3): what to do with the failure is the caller's call.

What one try is lives in client.py; this file decides how many there are and what comes back.
"""
from dataclasses import dataclass

TRIES = 5


@dataclass(frozen=True)
class Answer:
    """The model's text, or -- when `failed` -- why the box gave up, in the service's own words."""

    text: str
    failed: bool = False


class Box:
    def __init__(self, client):
        self._client = client

    def ask(self, system, text="", images=()):
        """The client's question, asked until it is answered or five tries have failed.

        Every failure is tried again, a missing key included: the client refuses that one before
        anything is sent, so its tries cost nothing, and one rule is simpler than a list of the
        exceptions worth a second try.
        """
        for _ in range(TRIES):
            try:
                return Answer(self._client.complete(system, text, images))
            except Exception as exc:
                said = str(exc)
        return Answer(said, failed=True)
