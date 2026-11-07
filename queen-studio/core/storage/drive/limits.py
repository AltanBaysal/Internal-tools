"""The Drive adapter's bounds, in one place: a test hands in small ones to reach each.

Everything read from Drive is input from outside the process (CODE-STANDARD, Cost), so each file is
bounded before it is opened, and nothing is written that this bound would refuse to read back.
"""

from dataclasses import dataclass

KIB = 1024
MIB = 1024 * KIB
GIB = 1024 * MIB
# A file's bytes are held this much at a time while they are hashed or streamed from Drive.
PIECE = MIB
# Opened JSON parsed into Python objects takes this many times its bytes (measured on records by
# the 532 review): the memory bounds below count the opened bytes, so the memory is this much more.
PARSED = 4.7


@dataclass(frozen=True)
class Limits:
    # Step 4, Bloklar: a tail goes to a block past 100 records or 256 KB.
    tail_count: int = 100
    tail_bytes: int = 256 * KIB
    # Step 4: an open block grows to 4 MB, then closes; one change may take it past, not past 8.
    block_full: int = 4 * MIB
    block_most: int = 8 * MIB
    # A 20,000-frame project's head is ~1 MB opened (step 4): sixteen times that is no project.
    head_most: int = 16 * MIB
    # A whole project opened, head and blocks: 20,000 frames are ~77 MB (step 4). At PARSED that
    # is ~600 MB in memory, within the 1 GB step 4 gives the loaded projects (Bellek ve disk).
    project_most: int = 128 * MIB
    # 1000 projects to a page (528, 5): twenty pages are far past any user's Drive.
    pages: int = 20
    # The base heads kept: the last few dozen projects used (m531, Sonraki maddeler için), and
    # never more than these bytes opened, ~150 MB in memory at PARSED.
    bases: int = 32
    bases_bytes: int = 32 * MIB
    # The longest a commit may take from its plan to its head's last write try: past it the
    # change is Rejected (retry.written). A sleeping machine's clock moves on too.
    commit_most: float = 600
    # A block no longer named is trashed this long after; a block named by no head, twice this
    # long after it was made. A commit built on a head naming it lands within commit_most of its
    # plan, and its plan came at most commit_most before the head that retired it: two
    # commit_most, a third of this, with room for the clocks.
    retire_after: float = 3600
    # Files (the m534 spec, Yükleme): up to Drive's 5 MB multipart limit in one request, read whole
    # into memory; past it a resumable upload, one chunk in memory at a time. On Drive a chunk but
    # the last is a multiple of 256 KiB; step 4 takes 16 MB.
    simple_most: int = 5 * MIB
    chunk: int = 16 * MIB
    # What a download leaves free on the machine's disk, for ComfyUI and the cache beside it.
    keep_free: int = GIB
