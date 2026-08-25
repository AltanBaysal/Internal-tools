"""Write the project's videos out: one file per frame, or one file for all of them -- and the
pictures they were made from, in a folder of their own.

The order is the gallery's, read from its foot up -- the same order the export summary counts and
the same one the badge counts from. Numbering follows it: 01 is the start of the sequence.

Nothing is moved. Every file written here is a copy; the project's own videos and sounds stay where
they are, which is what makes an export repeatable.

A run that fails takes its folder with it (madde 94). Half an export is worse than none: the folder
would look like a finished one, and the next run opens a new dated folder anyway.
"""
from functools import partial

from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.domain.usecases.export_summary import exportable
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing

MERGED = "merged"


def start_export(runner, store, record, plan_store, order_store, exporter, now, project, mode):
    """Claim the mode and write the export in the background; False means it is already going.

    The project is checked here rather than inside the run: the run happens in another thread, and
    an answer of "no such project" has to reach the request that asked.
    """
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    return runner.start(mode, partial(run_export, runner, store, record, plan_store, order_store,
                                      exporter, now, project, mode))


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


def run_export(runner, store, record, plan_store, order_store, exporter, now, project, mode):
    """Writes into a fresh dated folder and returns it; None when the run was cancelled."""
    frames = exportable(list_frames(record, store, plan_store, order_store, project))
    folder = store.make_export_folder(project, now())
    runner.report(mode, state="running", written=0, total=len(frames), target=folder,
                  error=None)
    pieces = []
    try:
        for index, frame in enumerate(frames, start=1):
            if runner.cancelled(mode):
                # Between pieces, never inside one: cutting ffmpeg off mid-file would leave half a
                # video, and the folder is going anyway.
                store.remove_dir(folder)
                runner.report(mode, state="idle", written=0, target=None)
                return None
            target = store.export_path(folder, f"{index:02d}.mp4")
            exporter.piece(store.file_path(project, frame["layers"][layers.VIDEO]),
                           _audio(store, project, frame), target)
            pieces.append(target)
            # The picture goes in under its video's own number, so the photos folder reads as the
            # same sequence and nothing has to be matched up by hand. A frame that somehow has no
            # picture leaves none: its video is written all the same.
            photo = frame.get("layers", {}).get(layers.PHOTO)
            if photo:
                store.copy_photo(store.file_path(project, photo), folder,
                                 f"{index:02d}{_extension(photo)}")
            runner.report(mode, written=index)
        if mode == MERGED:
            runner.report(mode, state="merging")
            exporter.merge(pieces, store.export_path(folder, f"{project}.mp4"))
    except Exception:
        store.remove_dir(folder)
        raise
    runner.report(mode, state="done")
    return folder


def _audio(store, project, frame):
    sound = _audio_of(frame)
    return store.file_path(project, sound) if sound else None
