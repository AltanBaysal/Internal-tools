"""The project in one file: where its photos live, and which prompt made each one, in gallery order.

The list comes from list_photos rather than from the record directly, so "which photos exist and in
what order" keeps exactly one answer -- an export that disagreed with the gallery would be a second
truth, and the video is stitched from this order.
"""
from backend.features.photo_generation.domain.usecases.list_photos import list_photos


def export_project(record, store, order_store, project):
    rows = list_photos(record, store, order_store, project)
    return {
        "folder": store.photo_dir(project),
        # Only what the next tool needs: a name and the prompt behind it. The rest of the trace
        # (negative, seed, time) stays in the record.
        "photos": [{"file": row["file"], "prompt": row.get("prompt", "")} for row in rows],
    }
