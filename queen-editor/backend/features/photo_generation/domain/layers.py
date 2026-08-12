"""A frame is a stack of layers: a photo, at most one video, at most one audio.

The unit is the slot, not the file. Two frames can point at one file -- a copy frame shares its
source's photo -- so "what happened to this layer" is a question about a (frame, slot) pair, and a
fold per file would answer it wrong the moment sharing starts.

Which slot may be produced into is the whole of "üret = ekle, sil = kaldır": production writes only
into a free slot, so nothing can ever be overwritten. Retry needs no rule of its own -- it writes a
"queued" line, and that frees the slot.

This is not the queue's question. Whether a slot is free says what MAY be asked for; what the queue
still owes is queue.is_open's answer and it did not change. A deleted photo frees its slot without
putting the frame back in line.
"""
from backend.features.photo_generation.domain import queue

PHOTO = "photo"
VIDEO = "video"
AUDIO = "audio"

# A slot is taken while its latest line says a layer is there -- produced or blown up. A failed
# layer counts as present deliberately: the frame stays out of the production panel's scope and is
# rescued by Tekrar dene alone, so one frame never gets two ways to be produced at once.
TAKEN = (queue.DONE, queue.FAILED)


def is_taken(status):
    """True while a layer occupies the slot."""
    return status in TAKEN


def can_produce(slots, slot):
    """slots: {slot name: status} for ONE frame. May a new layer be written into `slot`?"""
    if is_taken(slots.get(slot)):
        return False
    if slot == AUDIO:
        # Audio is mixed over a video, so a frame without one has nowhere to put it.
        return is_taken(slots.get(VIDEO))
    return True


def files_to_unlink(slots, closing):
    """Which files stop being pointed at once `closing` is closed.

    slots: {frame: {slot: {"status", "file"}}} for the whole project.
    closing: {(frame, slot)} -- the slots a deletion is about to close.

    Answered before a single line is written: the disk is touched first, so a failed unlink leaves
    the record untouched. A file another frame still holds is left where it is.
    """
    going, staying = set(), set()
    for frame, frame_slots in slots.items():
        for slot, cell in frame_slots.items():
            if not is_taken(cell["status"]):
                continue
            if (frame, slot) in closing:
                going.add(cell["file"])
            else:
                staying.add(cell["file"])
    return going - staying
