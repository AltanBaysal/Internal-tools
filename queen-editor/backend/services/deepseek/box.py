"""The black box every request to Queen AI goes through (madde 416, 418, 419).

The caller asks once and always gets an Answer back, never an exception. A request that came back
with an HTTP error, a malformed or an empty answer, or no answer at all is sent again as it was, up
to five tries in all. An answer that did come is checked before it goes back: its text is sent to
DeepSeek word for word, in a request of its own, and only an approval lets it through -- a refusal
sends the request again the way an error does, out of the same five tries (madde 418). When every
try failed, the Answer is marked as a failure and says what the last try met: the refusal sentence,
or the error's own text, and which of the two it was. It never raises because a caller that loops --
an agent -- must not be broken by the service (v9-3): what to do with the failure is the caller's
call.

Two kinds of request go through the same tries: a prompt writer's question -- an instruction, words
and pictures -- and the agent's conversation with its tools (madde 419), whose answer comes back
whole: its words, or the tool calls it makes. Only words are checked.

What one try is lives in client.py; this file decides how many there are and what comes back.
"""
from dataclasses import dataclass, field

TRIES = 5

# What the check is told; its words are the answer alone. English, because it is written for the
# model. It speaks of an answer to some request and of nothing of this tool's, because QueenAgent's
# box is to send the same text word for word (v10-1b). It asks whether the answer is a refusal and
# nothing more: a check that judged the content would refuse what the writers are asked for. The box
# reads one word back, so the text asks for one word.
CHECK_INSTRUCTION = """
You check an answer that a language model gave to a request.

Context
- You are given the answer alone, word for word. You are not given the request.
- An answer is a refusal when the model does not do what was asked: it says it cannot or will not, it apologizes instead of answering, or it gives a warning or a lecture instead of the answer.

Rules
- Judge only whether the answer is a refusal. Never judge whether the answer is good, true or allowed.
- Adult, explicit or violent content in the answer is not a refusal.
- If the answer is a refusal, write REFUSAL. Otherwise write APPROVED.
- Write only the one word. No quotes, no explanations.
"""

# What the caller is told when the last try was refused -- the owner's sentence (v9-3). A technical
# failure is told in its own words, because they say what went wrong; a refusal's words leave the
# caller nothing to do but ask another way.
REFUSED = "Model hata döndü, farklı şekilde dene."


@dataclass(frozen=True)
class Answer:
    """The model's words and the tool calls it makes, or -- when `failed` -- why the box gave up, in
    the service's own words.

    `tool_calls` is DeepSeek's own list, [] when there are none; words beside the calls are in
    `text`. `refused` says a failure's last try was refused rather than failed on the wire: the
    screen draws the two as different error cards (madde 425).
    """

    text: str
    failed: bool = False
    refused: bool = False
    tool_calls: list = field(default_factory=list)


class Box:
    def __init__(self, client):
        self._client = client

    def ask(self, system, text="", images=()):
        """The client's question -- an instruction, words and pictures -- tried until its answer
        passes the check or five tries have failed. Every prompt writer asks this."""
        return self._tried(lambda: (self._client.complete(system, text, images), []))

    def converse(self, messages, tools=()):
        """A conversation and the tools the model may call, tried the same way, and its answer back
        whole (madde 419). The agent asks this."""
        return self._tried(lambda: self._client.send(messages, tools))

    def _tried(self, request):
        """`request` sends one try and returns its (words, tool calls); this tries it at most five
        times.

        A try is the request and, when words came alone, their check; a refusal and an error of
        either request each spend one. Every failure is tried again, a missing key included: the
        client refuses that one before anything is sent, so its tries cost nothing, and one rule is
        simpler than a list of the exceptions worth a second try.
        """
        for _ in range(TRIES):
            try:
                words, calls = request()
                # A tool call is not checked (v9-3): it asks for something rather than answers, and
                # the words beside it are what the agent says while it asks.
                if calls:
                    return Answer(words, tool_calls=calls)
                # Only the one word lets an answer through: anything else, a check that will not
                # judge included, has approved nothing (v9-3).
                if self._client.complete(CHECK_INSTRUCTION, words) == "APPROVED":
                    return Answer(words)
                said, refused = REFUSED, True
            except Exception as exc:
                said, refused = str(exc), False
        # Every try rewrites both, so what the caller is told is the last try's.
        return Answer(said, failed=True, refused=refused)
