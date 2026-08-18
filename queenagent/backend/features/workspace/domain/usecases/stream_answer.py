"""Stream an answer, reaching for tools as the model asks.

The generator yields text pieces and finally the updated Chat. Telling them apart by type is
simpler than carrying a separate "this one is the last" flag.
"""
from backend.features.workspace.domain.errors import ChatNotFound, EngineFailed
from backend.features.workspace.domain.skills import instruction_for
from backend.features.workspace.domain.tools import (
    MAX_ROUNDS,
    TOOL_SPECS,
    WRITES_FILES,
    FileStarted,
    FileWritten,
    run_tool,
)
from backend.features.workspace.domain.usecases.append_message import append_message


def _conversation(chat):
    """Every message, with a skill's instruction dropped in front of the turn it governs.

    Once, not on every request: the instruction is a piece of the conversation rather than a header
    on it. Only the user's messages are watched -- an answer carries no skill, and letting one count
    would make the instruction reappear on every single turn.
    """
    active = ""
    built = []
    for message in chat.messages:
        if message.role == "user" and message.skill != active:
            active = message.skill
            # A rule fades the further back it sits, so a skill taken up again is stated again.
            instruction = instruction_for(active)
            if instruction:
                built.append({"role": "system", "content": instruction})
        built.append({"role": message.role, "content": message.text})
    return built


def stream_answer(chat_store, file_store, engine, project_id, chat_id, now):
    chat = chat_store.get(project_id, chat_id)
    if chat is None:
        raise ChatNotFound(chat_id)

    # Local to this answer and never written to the chat: tool calls, their results and a skill's
    # instruction are the model's own bookkeeping, and the design has nowhere to draw them.
    conversation = _conversation(chat)
    said = []
    born = []

    try:
        for _ in range(MAX_ROUNDS):
            spoken, calls = [], []
            # None rather than a name when the chat never chose: which model speaks for it is the
            # engine's own setting, and the domain has no business knowing what that says.
            for piece in engine.stream(conversation, tools=TOOL_SPECS, model=chat.model or None):
                if "text" in piece:
                    spoken.append(piece["text"])
                    said.append(piece["text"])
                    yield piece["text"]
                else:
                    calls.extend(piece["tool_calls"])

            if not calls:
                break

            conversation.append(
                {"role": "assistant", "content": "".join(spoken), "tool_calls": calls}
            )
            for call in calls:
                tool = call["function"]["name"]
                # The dashed card goes up before the tool runs: the name is not settled until it
                # has, and the design's card carries no name anyway.
                if tool in WRITES_FILES:
                    yield FileStarted()
                result = run_tool(file_store, project_id, tool, call["function"]["arguments"])
                # A name born twice in one turn is still one file: the card says a file exists, not
                # how many times it was written.
                if result.created and result.created not in born:
                    born.append(result.created)
                    yield FileWritten(result.created)
                conversation.append(
                    {"role": "tool", "tool_call_id": call["id"], "content": result.text}
                )
    except Exception as failure:
        # Half an answer is never kept: the design's line is that an answer either exists or does
        # not, and a file cannot be born of an unfinished thought.
        raise EngineFailed(str(failure)) from failure

    # Everything said across the rounds becomes one message: the user read one answer.
    yield append_message(
        chat_store, project_id, chat_id, "".join(said), now, role="ai", files=born
    )
