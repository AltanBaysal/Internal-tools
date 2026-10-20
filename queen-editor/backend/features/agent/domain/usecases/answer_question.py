"""Queen Editor's agent: one question about the open project, answered through the box (madde 420).

A loop like QueenAgent's: each round is one request through the box (madde 419), and the model either
calls tools or answers. At most 32 rounds -- the user's number -- and the last is told so and offered
no tools, so it answers with what it has, QueenAgent's way at its limit (Madde 137, v9-4).

The agent first looks at the project: the gallery's cards go to the model before the question, one
line each, numbered the way the gallery's badge numbers them (the user: "kart yapılı"). Then it reads
a frame, looks at its photo, checks it for mixed-up characters or fixes its photo as the model asks.
The fix is decided by the model, so its instruction carries the image model's rules and how a prompt
is fixed (madde 481).

Everything it does is a step on the chat with two sentences, and a step goes on until the next one
begins or the question ends: the model reads what a tool brought in the round after the tool ran, so
that is when the step is really going on. The record lets the answer or the failure finish the last
step, and a stop drop it (BEHAVIOUR.md, Agent panel).

A call that would change something waits for the user first (madde 480): the step before it is
finished -- the model read it to make this call -- and the run asks the user about the change. Only
on İzin ver does the call's step begin and its work run. On Reddet the model is told so and nothing
is done; a stop while the user is asked ends the question. Nothing here, and nothing the model is
told before a rejection, says that permission exists.
"""
import json

from backend.features.agent.domain import prompt
from backend.features.agent.domain.tools import TOOLS, QueenAIFailed, card, run_tool

MAX_ROUNDS = 32

LOOKING = ("Projeye bakıyor…", "Projeye baktı")
# The designer's sentence (sohbet.js, EMPTY): with no frame there is nothing to read, so nothing is
# asked.
NO_FRAMES = ("Projede henüz kare yok. Prompt'ları yazıp kuyruğa eklediğinde kareler galeride "
             "belirir; sonra sorularını kareler üzerinden cevaplayabilirim.")
# What the model is told when the user presses Reddet -- the user's "kullanıcı reddetti", in the
# English every tool answers in.
REJECTED = "The user rejected this change, so nothing was changed."


def numbered(cards):
    """{number: card}. The gallery's cards come top first, and its badge counts from the bottom: the
    oldest card is 1 (Gallery.jsx)."""
    return {len(cards) - index: frame for index, frame in enumerate(cards)}


def _conversation(cards, earlier, question):
    """The instruction, the chat so far, the project as it stands now, and the question.

    The chat so far is its questions and the answers the agent gave: a question that got none goes
    alone. Steps and what the tools said stay out, as QueenAgent leaves them out.
    """
    messages = [{"role": "system", "content": prompt.INSTRUCTION + prompt.MIXUP_RULES
                 + prompt.FIX_RULES + prompt.SYSTEM_PROMPT_SUFFIX}]
    for asked in earlier:
        messages.append({"role": "user", "content": asked["text"]})
        outcome = asked["outcome"] or {}
        if outcome.get("kind") == "answer":
            messages.append({"role": "assistant", "content": outcome["text"]})
    lines = [json.dumps(card(number, cards[number]), ensure_ascii=False) for number in sorted(cards)]
    messages.append({"role": "system", "content": "\n".join([prompt.FRAMES, *lines])})
    messages.append({"role": "user", "content": question})
    return messages


def answer_question(box, frames, picture, fix, run, project, earlier, question):
    """Answer `question` about `project`, writing every step and the outcome through `run`.

    `frames(project)` is the gallery's cards, top first; `picture(project, file)` a file's bytes or
    None; `fix(project, card, prompt, negative)` the photo feature's fix of one frame (madde 481),
    run only once the user allows it; `earlier` the chat's questions before this one. Neither reader
    writes, and none of the three is asked about any project but this one.
    """
    run.add_step(*LOOKING)
    cards = numbered(frames(project))
    if not cards:
        run.answer(NO_FRAMES)
        return
    messages = _conversation(cards, earlier, question)

    for index in range(MAX_ROUNDS):
        # Asked before each request: the runner drops whatever a stopped run writes, but another
        # request would still be sent and paid for.
        if run.stopped():
            return
        last = index == MAX_ROUNDS - 1
        if last:
            said = box.converse(messages + [{"role": "system", "content": prompt.LAST_ROUND}])
        else:
            said = box.converse(messages, TOOLS)
        if said.failed:
            run.fail(said.text)
            return
        # The last round's words are the answer whatever came with them: no round is left to run a
        # tool for.
        if last or not said.tool_calls:
            run.answer(said.text)
            return

        messages.append({"role": "assistant", "content": said.text,
                         "tool_calls": said.tool_calls})
        shown = []
        for call in said.tool_calls:
            # Asked before each call too: a check is a paid request of its own (madde 479), and one
            # round can hold a call for every frame.
            if run.stopped():
                return
            step, work, change = run_tool(box.ask, cards, picture, fix, project, call)
            # The look at the project is always the first step, so there is always one going on to
            # finish. After a rejection the next call finishes it again, which changes nothing.
            if step or change is not None:
                run.finish_step()
            if change is not None and not run.permit(change):
                if run.stopped():
                    return
                messages.append({"role": "tool", "tool_call_id": call["id"], "content": REJECTED})
                continue
            if step:
                # Before the work, so the chat says what goes on while it does.
                run.add_step(*step)
            # Asked once more: a stop that lands after İzin ver, before the work begins, leaves the
            # change undone -- and a stopped run does no more work of any kind.
            if run.stopped():
                return
            try:
                told, parts = work()
            except QueenAIFailed as exc:
                # The service failed, the way a failed round does: every later check would too.
                run.fail(str(exc))
                return
            messages.append({"role": "tool", "tool_call_id": call["id"], "content": told})
            shown += parts or []
        if shown:
            messages.append({"role": "user", "content": shown})
