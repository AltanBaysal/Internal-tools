"""/api/projects/<project>/generate · /api/status · /api/stop
/api/projects/<project>/frames · /photos/<project>/<file>

Translation only: no rules here. The use case's exception messages go out verbatim, so the wording
lives in exactly one place (the domain).
"""
from flask import Blueprint, jsonify, request, send_from_directory

from backend.features.photo_generation.domain import layers, production_mode, queue
from backend.features.photo_generation.export_runner import MODES
from backend.features.photo_generation.domain.frame_list import InvalidFrames
from backend.features.photo_generation.domain.prompt_list import InvalidPrompts
from backend.features.photo_generation.domain.production_mode import InvalidMode
from backend.features.photo_generation.domain.usecases.queue_layer import InvalidScope
from backend.features.photo_generation.domain.usecases.regenerate import LayerMissing, NoNextFrame
from backend.features.photo_generation.domain.usecases.resume_batch import NothingToResume
from backend.features.photo_generation.domain.usecases.retry_frame import FrameMissing
from backend.features.photo_generation.domain.usecases.save_order import InvalidOrder
from backend.features.photo_generation.domain.usecases.start_batch import (
    Busy,
    InvalidVariants,
    ProjectMissing,
)


# The layers a job can be asked for. A photo is not among them: it is asked for with its own
# prompts, not by hanging a layer on a frame that already exists.
QUEUEABLE = (layers.VIDEO, layers.AUDIO)

# The layers that can be taken off a frame on their own. The photo is not among them either: it is
# the base layer, so removing it is removing the frame (POST …/frames/delete).
REMOVABLE = (layers.VIDEO, layers.AUDIO)


def make_photo_generation_blueprint(start_batch, get_status, stop_generation, resume_batch,
                                    cancel_generation, retry_frame, retry_failed, queue_layer,
                                    regenerate, remove_layer, list_frames, list_models, save_order,
                                    export_summary, export_state, run_export, cancel_export,
                                    remove_frames, copy_frames, photo_dir):
    """The callables are already bound to a runner/store/generator (see main.py)."""
    bp = Blueprint("photo_generation", __name__)

    @bp.post("/api/projects/<project>/generate")
    def post_generate(project):
        body = request.get_json(silent=True) or {}
        prompts = body.get("prompts")
        # A non-string body field is treated as empty text -> "Prompt listesi boş."
        prompts = prompts if isinstance(prompts, str) else ""
        negative = body.get("negative")
        # No negative is legitimate (the batch renders without one); a non-string counts as none.
        negative = negative if isinstance(negative, str) else ""
        model = body.get("model")
        # No model is legitimate too: the graph renders with its own checkpoint.
        model = model if isinstance(model, str) else ""
        try:
            added = start_batch(project, prompts, negative, body.get("variants"), model)
        # Which box was wrong travels with the message: the screen marks that field instead of
        # guessing from the wording.
        except InvalidPrompts as exc:
            return jsonify({"error": str(exc), "field": "prompts"}), 400
        except InvalidVariants as exc:
            return jsonify({"error": str(exc), "field": "variants"}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        # 202: a batch runs for minutes, so the request only reports that the work was accepted.
        # "added" is how many frames the queue took -- the panel quotes it back to the user; and
        # "frames" is the gallery they landed in, because the screen would ask for exactly that in
        # a second round-trip, and until it lands the frames it was just told about are nowhere.
        return jsonify({"job": "running", "added": added, "frames": list_frames(project)}), 202

    @bp.get("/api/models")
    def models():
        try:
            return jsonify({"models": list_models()})
        except Exception as exc:
            # Whatever the renderer said or failed to say, verbatim -- the panel prints it under
            # the model field and generating stays possible without a choice.
            return jsonify({"error": str(exc)}), 502

    @bp.get("/api/status")
    def status():
        return jsonify(get_status())

    @bp.post("/api/stop")
    def stop():
        return jsonify(stop_generation())

    @bp.post("/api/projects/<project>/resume")
    def resume(project):
        try:
            resume_batch(project)
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except (NothingToResume, Busy) as exc:
            return jsonify({"error": str(exc)}), 409
        return jsonify({"job": "running"}), 202

    @bp.post("/api/projects/<project>/cancel")
    def cancel(project):
        try:
            cancel_generation(project)
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        return "", 204

    @bp.post("/api/projects/<project>/retry")
    def retry(project):
        body = request.get_json(silent=True) or {}
        frame = body.get("frame")
        try:
            # No frame named means all of them: "retry this frame" and "retry" are the same verb
            # with and without an object.
            if frame is None:
                retry_failed(project)
            else:
                retry_frame(project, frame)
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except FrameMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        return jsonify({"job": "running"}), 202

    @bp.post("/api/projects/<project>/layers/<kind>")
    def post_layer(project, kind):
        if kind not in QUEUEABLE:
            return jsonify({"error": f"Böyle bir katman yok: {kind}"}), 404
        body = request.get_json(silent=True) or {}
        # No "files" key at all means every frame that does not hold this layer; a list means that
        # selection.
        files = body.get("files")
        try:
            # No "variants" key means one per frame, and no "mode" key means a plain video: a
            # client older than either box asks for exactly what it always asked for.
            added = queue_layer(project, kind, files=files, variants=body.get("variants", 1),
                                mode=body.get("mode", production_mode.STANDARD))
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except InvalidScope as exc:
            return jsonify({"error": str(exc), "field": "files"}), 400
        except InvalidMode as exc:
            return jsonify({"error": str(exc), "field": "mode"}), 400
        except InvalidVariants as exc:
            return jsonify({"error": str(exc), "field": "variants"}), 400
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        # The gallery comes back with the answer, the same as a photo batch: the button is the
        # same button, and one of the two waiting a round-trip longer than the other would be an
        # accident rather than a decision.
        return jsonify({"job": "running", "added": added, "frames": list_frames(project)}), 202

    @bp.post("/api/projects/<project>/layers/<kind>/delete")
    def delete_layer(project, kind):
        if kind not in REMOVABLE:
            return jsonify({"error": f"Silinebilir bir katman değil: {kind}"}), 404
        body = request.get_json(silent=True) or {}
        try:
            # What really left the disk goes back: a layer a frame did not carry costs nothing and
            # is not an error, and neither is a name the gallery no longer knows.
            return jsonify(remove_layer(project, body.get("frames"), kind))
        except InvalidFrames as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            # The operating system's own words -- never guess the cause.
            return jsonify({"error": str(exc)}), 500

    @bp.post("/api/projects/<project>/regenerate")
    def post_regenerate(project):
        body = request.get_json(silent=True) or {}
        layer = body.get("layer")
        # Every layer can be made again, the photo included: what is asked for here is one named
        # frame's own layer, not a batch.
        if layer not in queue.ORDER:
            return jsonify({"error": f"Böyle bir katman yok: {layer}"}), 404
        prompt = body.get("prompt")
        try:
            # The frame is named by its identity: a copy frame shares its source's picture, so a
            # file name would not say which of the two was asked for. A non-string prompt counts as
            # no words at all -- what goes down is exactly what the user was shown.
            frame = regenerate(project, body.get("frame"), layer,
                               prompt if isinstance(prompt, str) else "",
                               mode=body.get("mode", production_mode.STANDARD))
        except (ProjectMissing, FrameMissing) as exc:
            return jsonify({"error": str(exc)}), 404
        except LayerMissing as exc:
            return jsonify({"error": str(exc)}), 400
        except (InvalidMode, NoNextFrame) as exc:
            # The same shape the queue's own refusal takes: both say the mode is what went wrong.
            return jsonify({"error": str(exc), "field": "mode"}), 400
        except Busy as exc:
            return jsonify({"error": str(exc)}), 409
        # The new frame's name goes back: the screen has just been told that its work landed
        # somewhere else.
        return jsonify({"job": "running", "frame": frame}), 202

    @bp.get("/api/projects/<project>/frames")
    def frames(project):
        # The gallery's whole sequence in one answer -- produced, pending and failed alike.
        try:
            return jsonify({"frames": list_frames(project)})
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    @bp.put("/api/projects/<project>/order")
    def put_order(project):
        body = request.get_json(silent=True) or {}
        try:
            # The stored list goes back so the client sees what was kept, not what it guessed.
            return jsonify({"order": save_order(project, body.get("order"))})
        except InvalidOrder as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    @bp.get("/api/projects/<project>/export/status")
    def export_status(project):
        # Per mode, so a screen with one export running and one idle reads both in one answer.
        return jsonify(export_state())

    @bp.post("/api/projects/<project>/export/<mode>")
    def start_export(project, mode):
        if mode not in MODES:
            return jsonify({"error": f"Böyle bir export yok: {mode}"}), 404
        try:
            started = run_export(project, mode)
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        if not started:
            return jsonify({"error": "Bu export zaten sürüyor."}), 409
        # 202: writing the files takes minutes, and how far it has got is read from the status.
        return jsonify({"job": "running"}), 202

    @bp.post("/api/projects/<project>/export/cancel")
    def cancel_export_route(project):
        # Both modes: leaving the screen cancels whatever it started (madde 96).
        cancel_export()
        return jsonify({"job": "cancelling"}), 202

    @bp.get("/api/projects/<project>/export/summary")
    def export_summary_of(project):
        # What an export would write, for the screen that asks before it runs. Nothing is created
        # here: the folder in the answer is where a run would land.
        try:
            return jsonify(export_summary(project))
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404

    # POST, not DELETE: the request carries a list of frames, and a body on DELETE is a corner of
    # HTTP that proxies and clients disagree about.
    @bp.post("/api/projects/<project>/frames/delete")
    def remove(project):
        body = request.get_json(silent=True) or {}
        try:
            # What really happened goes back, split in two: a photo left the disk, a frame that was
            # never produced only left the queue. Frames that had already gone are not an error.
            return jsonify(remove_frames(project, body.get("frames")))
        except InvalidFrames as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            # The operating system's own words -- never guess the cause.
            return jsonify({"error": str(exc)}), 500

    # Beside the delete above, and the same shape: a list of identities in the body, because a copy
    # frame shares its source's picture and a file name would not say which of the two was asked
    # for.
    @bp.post("/api/projects/<project>/frames/copy")
    def copy(project):
        body = request.get_json(silent=True) or {}
        try:
            answer = copy_frames(project, body.get("frames"))
        except InvalidFrames as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        # The gallery comes back with the twins: the screen would ask for exactly this in a second
        # round-trip, and until it lands the copies it was just told about are nowhere.
        return jsonify({**answer, "frames": list_frames(project)})

    @bp.get("/photos/<project>/<filename>")
    def serve_photo(project, filename):
        # send_from_directory rejects paths that escape the folder.
        resp = send_from_directory(photo_dir(project), filename)
        # next_number never reuses a number, so a photo URL's bytes can never change.
        resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return resp

    return bp
