"""The black box every request of the agent's loop goes through (Madde 440, Madde 445).

The loop hands it a request -- the conversation and the tools -- and always gets an answer back: the
model's, whole and checked, or after five failed tries what the last one met. It never throws,
because a loop that broke on one bad request would lose the whole turn (the user, 5 October: the
agent has to get something back, or the loop breaks).

A whole answer in words is checked before it goes back: its text is shown to the model word for word
in a request of its own, and only an approval lets it through. A refusal sends the request again the
way an error does, out of the same five tries (Madde 445).

A rule rather than transport, so it lives in the domain: how many tries, what counts as empty or
refused, and that a stop is never tried again are what a test holds, and only the domain knows a
stop. The model service still sends one request and reads one stream.
"""
from dataclasses import dataclass

from backend.features.workspace.domain.chat import Usage
from backend.features.workspace.domain.prompt import APPROVED, CHECK

TRIES = 5
"""The user's number (v10-1). No wait between tries and no count shown: the retries never show."""

NOTHING = "The model returned nothing."
"""What five empty answers say -- an empty answer has no words of its own to repeat. The route says
the same sentence for a turn that ends with neither words nor a file."""

TECHNICAL = "technical"
"""The kind a failed answer is when its last try failed on the wire, or came back empty."""

REFUSED = "refused"
"""The kind a failed answer is when its last try was refused by the check (Madde 445)."""

REFUSED_SAID = "The model returned an error. Try asking another way."
"""What the chat says when the last try was refused -- the design's sentence (items 216 and 221),
the English of the user's "Model hata döndü, farklı şekilde dene". A technical failure is told in
its own words, because they say what went wrong; a refusal's words leave the user nothing to do but
ask another way, and they are not shown."""


@dataclass(frozen=True)
class Answer:
    text: str = ""
    calls: tuple = ()
    # None when the engine said nothing about spending, so the loop leaves its total alone.
    usage: Usage | None = None
    # "" for a real answer; otherwise the kind, and `text` holds what the chat says of it: the
    # failure's own words, or REFUSED_SAID.
    failed: str = ""


def ask(engine, messages, tools, on_open, stopped, silence_is_an_answer=False):
    """One request, sent again on an error, an empty answer or a refusal, at most TRIES times.

    A try is the request and, when it came back in words alone, their check; an error of either,
    an empty answer and a refusal each spend one. What comes back after five is the last try's
    failure, its kind and its words together: the last try decides (v10-1b).

    `stopped` is asked whenever a try fails: a connection we cut ourselves fails like any other --
    the check's too, since its way to cut goes to `on_open` as well -- and a stop is never tried
    again. On a stop the black box gives back an empty answer and nothing else: the stops registry
    is the one thing that knows a stop, and the loop asks it after every answer anyway, so a second
    flag here would only restate it.

    `silence_is_an_answer` is the caller's to say, because whether saying nothing is finished
    depends on the turn rather than the request: a turn that has already written a file and then
    says nothing is done (Madde 38, kept by the user on 9 October), so its empty answer comes back
    as it is, untried and unchecked.
    """
    for _ in range(TRIES):
        try:
            answer = _read(engine.stream(messages, tools=tools, on_open=on_open))
            # A tool call is not checked (v10-1b): it asks for something rather than answers, and
            # the words beside it are what the agent says while it asks.
            if answer.calls:
                return answer
            if not answer.text.strip():
                if silence_is_an_answer:
                    return answer
                failure = Answer(text=NOTHING, failed=TECHNICAL)
            elif _approved(engine, answer.text, on_open):
                return answer
            else:
                failure = Answer(text=REFUSED_SAID, failed=REFUSED)
        except Exception as error:
            failure = Answer(text=str(error), failed=TECHNICAL)
        if stopped():
            return Answer()
    return failure


def _approved(engine, text, on_open):
    """Whether the check let these words through.

    Only the one word does, blanks around it aside: anything else -- a refusal, an empty answer, an
    explanation -- approved nothing. The check's own cost is not added to the answer's: what the
    stamp says is what the answer's request sent.
    """
    return _read(engine.stream_alone(CHECK, text, on_open=on_open)).text.strip() == APPROVED


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
