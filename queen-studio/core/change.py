"""What every changing request carries (step 6, Request headers): its key and who makes it.

Each POST, PATCH and DELETE endpoint takes `change` as a dependency, so a request without both
headers, or with one out of its rule, is refused with `invalid_request` before the endpoint runs,
and the UI's types require both. GET takes neither. A test tries every changing route without them.
`async`: it touches no store, so it needs no worker thread of its own.
"""

from dataclasses import dataclass
from typing import Annotated, Literal

from fastapi import Header

# `core` is the third actor of history, written only by the core itself (step 2).
Actor = Literal["agent", "ui"]

# The hint of a header's problem: an address's detail leaves the headers out, since the agent never
# writes them, so the rule is said here.
HEADERS_HINT = (
    "Every POST, PATCH and DELETE carries `Idempotency-Key`, 1 to 128 printable ASCII characters "
    "new for each change, and `Actor`, `agent` or `ui`; the MCP tool and the UI set both."
)


@dataclass(frozen=True)
class Change:
    # Keeping it and finding a repeat is v1-10's (step 6, The same request twice).
    key: str
    actor: Actor


async def change(
    key: Annotated[
        str,
        Header(
            alias="Idempotency-Key",
            max_length=128,
            pattern=r"^[\x20-\x7e]+$",
            description="1 to 128 printable ASCII characters, new for each change and the same "
            "when the change is sent again. The MCP tool sets it, the UI too.",
        ),
    ],
    actor: Annotated[
        Actor,
        Header(alias="Actor", description="Who makes the change; history records it."),
    ],
) -> Change:
    return Change(key=key, actor=actor)
