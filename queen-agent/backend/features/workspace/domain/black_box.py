"""The black box every request of the agent's loop goes through (Madde 440).

The loop hands it a request -- the conversation and the tools -- and always gets an answer back: the
model's, whole, or after five failed tries the last failure's own words. It never throws, because a
loop that broke on one bad request would lose the whole turn (the user, 5 October: the agent has to
get something back, or the loop breaks).

A rule rather than transport, so it lives in the domain: how many tries, what counts as empty, and
that a stop is never tried again are what a test holds, and only the domain knows a stop. The model
service still sends one request and reads one stream.
"""
from dataclasses import dataclass

from backend.features.workspace.domain.chat import Usage

TRIES = 5
"""The user's number (v10-1). No wait between tries and no count shown: the retries never show."""

NOTHING = "The model returned nothing."
"""What five empty answers say -- an empty answer has no words of its own to repeat. The route says
the same sentence for a turn that ends with neither words nor a file."""

TECHNICAL = "technical"
"""The kind a failed answer is when the model failed technically. Madde 445 adds the refusal."""


@dataclass(frozen=True)
class Answer:
    text: str = ""
    calls: tuple = ()
    # None when the engine said nothing about spending, so the loop leaves its total alone.
    usage: Usage | None = None
    # "" for a real answer; otherwise the kind, and `text` holds the failure's own words.
    failed: str = ""


def ask(engine, messages, tools, on_open, stopped, silence_is_an_answer=False):
    """One request, sent again on an error or an empty answer, at most TRIES times.

    `stopped` is asked whenever a try fails: a connection we cut ourselves fails like any other, and
    a stop is never tried again. On a stop the black box gives back an empty answer and nothing
    else: the stops registry is the one thing that knows a stop, and the loop asks it after every
    answer anyway, so a second flag here would only restate it.

    `silence_is_an_answer` is the caller's to say, because whether saying nothing is finished
    depends on the turn rather than the request: a turn that has already written a file and then
    says nothing is done (Madde 38, kept by the user on 9 October), so its empty answer comes back
    as it is, untried.
    """
    failure = NOTHING
    for _ in range(TRIES):
        try:
            answer = _read(engine.stream(messages, tools=tools, on_open=on_open))
        except Exception as error:
            if stopped():
                return Answer()
            failure = str(error)
            continue
        if answer.text.strip() or answer.calls or silence_is_an_answer:
            # Madde 445's check goes here: a whole answer in words is shown to the model in a
            # request of its own, and a refusal counts as one more failed try.
            return answer
        if stopped():
            return Answer()
        failure = NOTHING
    return Answer(text=failure, failed=TECHNICAL)


def _read(pieces):
    """The stream read to its end: the words joined, the calls collected, the last reading kept.

    A reading replaces the one before it: inside one stream the figure is a total for the call, and
    adding them up would multiply the bill by the number of frames.
    """
    words, calls, usage = [], [], None
    for piece in pieces:
        if "text" in piece:
            words.append(piece["text"])
        elif "usage" in piece:
            spent = piece["usage"]
            usage = Usage(spent["sent"], spent["cached"], spent["answered"])
        else:
            calls.extend(piece["tool_calls"])
    return Answer(text="".join(words), calls=tuple(calls), usage=usage)
