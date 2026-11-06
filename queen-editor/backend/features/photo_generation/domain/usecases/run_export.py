"""Write the project's videos out: one file per frame, or one file for all of them -- and the
pictures they were made from, in a folder of their own.

The order is the gallery's, read from its foot up -- the same order the export summary counts and
the same one the badge counts from. Numbering follows it: 01 is the start of the sequence.

Nothing is moved. Every file written here is a copy; the project's own videos and sounds stay where
they are, which is what makes an export repeatable.

A run that fails takes back what it wrote (madde 94). Half an export is worse than none: the folder
would look like a finished one, and the next run opens a new dated folder anyway. What it wrote, and
not the folder: the two modes share the minute's folder, and the other's files are not this run's
to take (madde 474).
"""
from functools import partial

from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.usecases.export_summary import exportable
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing

MERGED = "merged"

# What a merged export's join is cut as on the machine, beside its pieces. Pieces are named by their
# two-digit place (01.mp4 …) and the merger writes NN-sound.mp4 there too, so a join named after
# the project could be one of them -- a project named 01 had ffmpeg write over its own first piece
# (madde 474). Drive still gets the project's name.
JOINED = "birlesik.mp4"


def start_export(runner, store, record, plan_store, order_store, exporter, now, project, mode, *,
                 mutes):
    """Claim the mode and write the export in the background; False means it is already going.

    The project is checked here rather than inside the run: the run happens in another thread, and
    an answer of "no such project" has to reach the request that asked.

    `mutes` is the store of the frames whose sound is turned off (madde 510). Required, so a wiring
    that forgot it fails rather than letting every turned-off sound back in.
    """
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    return runner.start(mode, partial(run_export, runner, store, record, plan_store, order_store,
                                      exporter, now, project, mode, mutes=mutes))


def _extension(filename):
    """The picture's own suffix, dot included, or nothing at all.

    The number belongs to the export and the suffix to the file: writing .png into the code would
    name the first jpg wrongly, and nothing on screen would say so.

    Read from the name rather than from the path -- a file's name is what this layer has, and where
    it sits on disk is the store's business.
    """
    head, dot, tail = filename.rpartition(".")
    return f".{tail}" if dot and head else ""


def _audio_of(frame):
    """The sound laid over this frame's video, or None -- a failed one is not there."""
    if layers.AUDIO in frame.get("failed", []):
        return None
    return frame.get("layers", {}).get(layers.AUDIO)


def run_export(runner, store, record, plan_store, order_store, exporter, now, project, mode, *,
               mutes):
    """Writes into a fresh dated folder and returns where it is; None when the run was cancelled."""
    frames = exportable(list_frames(record, store, plan_store, order_store, project))
    # Once, and before anything is opened: a list that cannot be read stops the run with nothing to
    # take back, and is never read as nothing turned off.
    muted = mutes.read(project)
    stamp = now()
    # Before the pieces folder: a mount that refuses here leaves nothing to clean up on either disk.
    folder = store.open_export(project, stamp)
    # Where the pieces are cut, in both modes: on the machine's own disk. A merged export's are
    # scaffolding for the join -- Drive is slow, and the set would be written there twice over
    # (madde 235). A separate export's ARE the export, and each is carried to Drive whole the moment
    # it is cut: ffmpeg writing onto Drive's mount a piece at a time was both the slowness madde 282
    # took away from the join and a write past the storage door (madde 472).
    pieces_dir = store.make_pieces_dir()
    runner.report(mode, state="running", written=0, total=len(frames), target=folder,
                  error=None)
    own = []                           # the videos this run has put on Drive, what it takes back
    try:
        finished = _write(runner, store, exporter, frames, muted, project, stamp, pieces_dir, mode,
                          own)
    except Exception as failure:
        # The run's own reason is what the user is told first. A cleanup that fails too -- the
        # mount dropped, most likely, which is often why the run failed -- leaves a half export on
        # Drive, and the screen has to say so (madde 94): the runner shows one sentence, so both go
        # into it, the run's error kept as the cause.
        try:
            _clean(runner, store, project, stamp, pieces_dir, mode, folder, own)
        except OSError as cleanup:
            raise RuntimeError(f"{failure} — Yarım export silinemedi: {cleanup}") from failure
        raise
    if not finished:
        # Taken down here, once, outside the work: a cleanup that fails is the run's error then.
        _clean(runner, store, project, stamp, pieces_dir, mode, folder, own)
        runner.report(mode, state="idle", written=0, target=None)
        return None
    # The export is on Drive; the pieces on the machine have nothing left to say. The videos a
    # separate export carried to Drive are what the user asked for, and stay (madde 283).
    store.remove_pieces(pieces_dir)
    runner.report(mode, state="done")
    return folder


def _write(runner, store, exporter, frames, muted, project, stamp, pieces_dir, mode, own):
    """The export's work; False when it was cancelled. Each video it puts on Drive is added to
    `own` once its save has returned -- a save is whole or absent, so nothing half written is
    listed. The names are this run's, not necessarily the files': a run of the same mode finished
    earlier in the same minute wrote the same names into the same folder, this run wrote over
    them, and its cleanup takes those too.

    The cancel is asked between work units, never inside one: cutting ffmpeg off mid-file would
    leave half a video, and a copy stopped halfway leaves half a picture.
    """
    pieces = []                        # what the join reads, in order: a merged export's alone
    written = set()                    # the picture files already in the export's photos folder
    # The videos first, all of them, and the pictures after -- the user asked for the two steps
    # apart, and it is what lets them be timed apart: while they were one loop, a slow counter did
    # not say whether the time went on reading a video off Drive or writing a picture back to it
    # (madde 289). Both walk the same list in the same order, which is what keeps the numbering one
    # sequence: the number is the frame's place, not the loop's.
    for index, frame in enumerate(frames, start=1):
        if runner.cancelled(mode):
            return False
        name = f"{index:02d}.mp4"
        piece = store.piece_path(pieces_dir, name)
        video = store.file_path(project, frame["layers"][layers.VIDEO])
        # Every frame here has a video that landed, which is all a mark asks for (madde 515).
        if frame["id"] in muted:
            # No sound at all, the video's own included: an H3 video carries one, and a plain copy
            # would keep it (madde 510). A merged export writes silence into it like any other
            # soundless piece.
            exporter.silent(video, piece)
        else:
            exporter.piece(video, _audio(store, project, frame), piece)
        if mode == MERGED:
            pieces.append(piece)
        else:
            # So the counter below counts what Drive holds, not what the machine cut.
            store.copy_video(project, stamp, piece, name)
            own.append(name)
        runner.report(mode, written=index)
    # Its own step, in both modes: the counter has finished counting and the work has not, so a
    # screen still reading N/N would be naming the wrong one (madde 287).
    runner.report(mode, state="photos")
    for index, frame in enumerate(frames, start=1):
        if runner.cancelled(mode):
            return False
        # The picture goes in under its video's own number, so the photos folder reads as the same
        # sequence and nothing has to be matched up by hand. A frame that somehow has no picture
        # leaves none: its video is written all the same.
        #
        # And each picture goes in once. A copy frame produces no picture of its own -- it holds
        # the source's file -- so a photo with three videos used to be written three times, and the
        # folder read as the same image over and over (madde 236). The number stays the first
        # frame's, gaps and all: it is what says which video the picture belongs to.
        photo = frame.get("layers", {}).get(layers.PHOTO)
        if photo and photo not in written:
            written.add(photo)
            store.copy_photo(project, photo, stamp, f"{index:02d}{_extension(photo)}")
    if mode == MERGED:
        runner.report(mode, state="merging")
        # The join is written on the machine's own disk and copied to Drive once it is whole.
        # ffmpeg used to write the encoded stream onto the Drive mount a piece at a time, which is a
        # known Colab slowness (madde 282); and while it runs, the Drive folder holds nothing, so a
        # half written mp4 is never there to be seen (madde 94).
        joined = store.piece_path(pieces_dir, JOINED)
        exporter.merge(pieces, joined)
        # The trip to Drive is its own step: it used to run under the disclaimer's name, which is
        # the step the user wonders about most (madde 287). It is the run's last step and one
        # save, so a merged run that fails has no file of its own on Drive to take back.
        runner.report(mode, state="saving")
        store.copy_export(project, stamp, joined, f"{project}.mp4")
    return True


def _clean(runner, store, project, stamp, pieces_dir, mode, folder, own):
    """A run that did not finish takes back what it wrote: half an export looks like a finished one
    (madde 94), and pieces nobody carried to Drive are so much scaffolding. The machine's own
    pieces go first: nothing stops their going, and a Drive that refuses must not keep them.

    On Drive it takes its own videos, and the photos only if no other export needs them: the two
    modes share the folder and its photos (madde 474). Whether the other mode is writing here now
    only the runner knows; whether one left its output here, the store sees on disk.
    """
    store.remove_pieces(pieces_dir)
    store.remove_export(project, stamp, own, in_use=runner.others_writing(mode, folder))


def _audio(store, project, frame):
    sound = _audio_of(frame)
    return store.file_path(project, sound) if sound else None
