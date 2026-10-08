"""Composition root -- build services, wire them into features, start Flask.
Run as: python -m backend.main"""
import time
from datetime import datetime, timezone
from functools import partial

from backend import config
from backend.features.agent.data.chat_record import DriveChatRecord
from backend.features.agent.domain.usecases.answer_question import answer_question
from backend.features.agent.domain.usecases.chats import (
    ask_question,
    list_chats,
    new_chat,
    open_chat,
    stop_agent,
    working_chats,
)
from backend.features.agent.presentation.routes import make_agent_blueprint, make_chats_blueprint
from backend.features.agent.runner import AgentRunner
from backend.features.photo_generation.data.comfy_photo_generator import ComfyPhotoGenerator
from backend.features.photo_generation.data.ffmpeg_audio import FfmpegAudio
from backend.features.photo_generation.data.ffmpeg_clips import FfmpegClips
from backend.features.photo_generation.data.ffmpeg_stills import FfmpegStills
from backend.features.photo_generation.data.mmaudio_generator import MMAudioGenerator
from backend.features.photo_generation.data.mmaudio_sampler import MMAudioSampler
from backend.features.photo_generation.data.comfy_h3_video_generator import ComfyH3VideoGenerator
from backend.features.photo_generation.data.prompt_writer import (
    AudioPromptWriter,
    H3VideoPromptWriter,
)
from backend.features.photo_generation.domain import layers, seed
from backend.features.photo_generation.data.order_store import DriveOrderStore
from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.features.photo_generation.data.reference_order_store import (
    DriveReferenceOrderStore,
)
from backend.features.photo_generation.data.reference_store import DriveReferenceStore
from backend.features.photo_generation.data.video_length_store import DriveVideoLengthStore
from backend.features.photo_generation.data.happy_ending_store import DriveHappyEndingStore
from backend.features.photo_generation.domain.usecases.add_references import add_references
from backend.features.photo_generation.domain.usecases.copy_frames import copy_frames
from backend.features.photo_generation.domain.usecases.list_references import list_references
from backend.features.photo_generation.domain.usecases.queue_references import queue_references
from backend.features.photo_generation.domain.usecases.reference_files import reference_files
from backend.features.photo_generation.domain.usecases.remove_reference import remove_reference
from backend.features.photo_generation.domain.usecases.save_reference_order import (
    save_reference_order,
)
from backend.features.photo_generation.domain.usecases.remove_frames import remove_frames
from backend.features.photo_generation.data.ffmpeg_video_exporter import FfmpegVideoExporter
from backend.features.photo_generation.domain.usecases.export_summary import export_summary
from backend.features.photo_generation.domain.usecases.run_export import start_export
from backend.features.photo_generation.export_runner import MODES, ExportRunner
from backend.features.photo_generation.domain.usecases.cancel_generation import cancel_generation
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.follow_rename import follow_rename
from backend.features.photo_generation.domain.usecases.halt_project import halt_project
from backend.features.photo_generation.domain.usecases.queue_layer import queue_layer
from backend.features.photo_generation.domain.usecases.regenerate import regenerate
from backend.features.photo_generation.domain.usecases.remove_layer import remove_layer
from backend.features.photo_generation.domain.usecases.retry_failed import retry_failed
from backend.features.photo_generation.domain.usecases.retry_frame import retry_frame
from backend.features.photo_generation.domain.usecases.resume_batch import resume_batch
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.list_models import list_loras, list_models
from backend.features.photo_generation.domain.usecases.save_order import save_order
from backend.features.photo_generation.domain.usecases.start_batch import start_batch
from backend.features.photo_generation.domain.usecases.stop_generation import stop_generation
from backend.features.photo_generation.domain.usecases.video_length import (
    get_video_length,
    save_video_length,
)
from backend.features.photo_generation.domain.usecases.happy_ending import (
    get_happy_ending,
    save_happy_ending,
)
from backend.features.photo_generation.presentation.reference_routes import (
    make_reference_blueprint,
)
from backend.features.photo_generation.presentation.routes import make_photo_generation_blueprint
from backend.features.photo_generation.presentation.video_length_routes import (
    make_video_length_blueprint,
)
from backend.features.photo_generation.presentation.happy_ending_routes import (
    make_happy_ending_blueprint,
)
from backend.features.photo_generation.runner import PhotoRunner
from backend.features.projects.data.project_store import DriveProjectStore
from backend.features.projects.data.reference_settings_store import DriveReferenceSettingsStore
from backend.features.projects.data.settings_store import DriveSettingsStore
from backend.features.projects.domain.usecases.archive_project import (
    archive_project,
    list_archived_projects,
    restore_project,
)
from backend.features.projects.domain.usecases.check_name import check_name
from backend.features.projects.domain.usecases.create_project import create_project
from backend.features.projects.domain.usecases.delete_project import delete_project
from backend.features.projects.domain.usecases.get_settings import get_settings
from backend.features.projects.domain.usecases.list_projects import list_projects
from backend.features.projects.domain.usecases.rename_project import rename_project
from backend.features.projects.domain.usecases.save_reference_settings import (
    save_reference_settings,
)
from backend.features.projects.domain.usecases.save_settings import save_settings
from backend.features.producers.data.comfy_models import ComfyModelFiles
from backend.features.producers.domain.model_groups import GROUPS, audio_weights
from backend.features.producers.domain.usecases.list_producers import list_producers
from backend.features.producers.presentation.routes import make_producers_blueprint
from backend.features.projects.presentation.reference_settings_routes import (
    make_reference_settings_blueprint,
)
from backend.features.projects.presentation.routes import make_projects_blueprint
from backend.services.comfy.client import ComfyClient
from backend.services.deepseek.box import Box
from backend.services.deepseek.client import DeepSeekClient
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app

# One storage, shared by every feature that keeps files: they are separate features over the same
# Drive root.
_storage = DriveStorage(config.DRIVE_ROOT)

_project_store = DriveProjectStore(_storage)
_settings_store = DriveSettingsStore(_storage)
_reference_settings_store = DriveReferenceSettingsStore(_storage)

_photo_store = DrivePhotoStore(_storage)
_comfy_client = ComfyClient(config.COMFY_URL, poll_interval=config.POLL_INTERVAL,
                            log_path=config.COMFY_LOG)
_photo_generator = ComfyPhotoGenerator(_comfy_client, config.WORKFLOW_PATH, config.RENDER_TIMEOUT)
# Queen AI writes every prompt nobody typed (madde 400, 404): a video's looking at the frame's
# photo, a sound's from its video's prompt. Every ask goes through the box, which sends a failed
# request again (madde 416).
_queen_ai = Box(DeepSeekClient(config.DEEPSEEK_API_KEY, config.DEEPSEEK_MODEL,
                               config.DEEPSEEK_URL, timeout=config.DEEPSEEK_TIMEOUT))
# H3 is the one video model (madde 435): every session renders its videos with H3's graphs, and
# Queen AI writes H3's prompt for them. A session with no video installed is wired the same way --
# the producers panel says H3's files are missing, and the video panel keeps Kuyruğa ekle closed.
_video_generator = ComfyH3VideoGenerator(_comfy_client, config.H3_VIDEO_WORKFLOW_PATH,
                                         config.H3_VIDEO_FIRST_LAST_WORKFLOW_PATH,
                                         config.VIDEO_TIMEOUT)
_video_writer = H3VideoPromptWriter(_queen_ai)
# Sound is the one producer that is not a ComfyUI graph: MMAudio runs inside this process. Where
# its weights live is the producers feature's answer, so the path is taken from the group it
# installs rather than spelled out here a second time.
_model_files = ComfyModelFiles(config.COMFY_ROOT)
_audio_generator = MMAudioGenerator(MMAudioSampler(audio_weights(_model_files)), FfmpegAudio())
# What the loop dispatches on: one producer per job type. All three are ComfyUI graphs; a type with
# nobody to do it would make the queue wait rather than skip the work.
_producers = {layers.PHOTO: _photo_generator, layers.VIDEO: _video_generator,
              layers.AUDIO: _audio_generator}
# Who writes a job's prompt when it carries none. Photo has no writer: its prompt is the user's own.
_writers = {layers.VIDEO: _video_writer, layers.AUDIO: AudioPromptWriter(_queen_ai)}
# What a card with no picture gets when its video lands (madde 296). ffmpeg is already on the
# machine -- the sound engine cuts with it, and the export joins with it.
_stills = FfmpegStills()
_photo_runner = PhotoRunner()
_photo_record = DrivePhotoRecord(_storage)
_plan_store = DrivePlanStore(_storage)
_order_store = DriveOrderStore(_storage)

_export_runner = ExportRunner()
_video_exporter = FfmpegVideoExporter(disclaimer=config.DISCLAIMER_PATH)

# The one place the two features meet: deleting a project has to stop the production that project
# owns, and the worker that owns it belongs to photo generation. The projects feature is handed the
# ability, not the worker.
_projects_bp = make_projects_blueprint(
    list_projects=partial(list_projects, _project_store),
    create_project=partial(create_project, _project_store),
    check_name=check_name,
    delete_project=partial(delete_project, _project_store,
                           partial(halt_project, _photo_runner, _comfy_client.interrupt,
                                   time.sleep)),
    # Renaming meets the worker too, but the other way round: the production is not stopped, it is
    # carried over to the folder's new name.
    rename_project=partial(rename_project, _project_store,
                           partial(follow_rename, _photo_runner)),
    get_settings=partial(get_settings, _settings_store),
    save_settings=partial(save_settings, _settings_store),
    # No halt port: archiving marks the project rather than moving it (madde 227), so a worker
    # writing into that folder is not a problem -- the project going on working is the point.
    archive_project=partial(archive_project, _project_store),
    restore_project=partial(restore_project, _project_store),
    list_archived_projects=partial(list_archived_projects, _project_store),
)

# Referanstan's boxes: the photo panel's question, in a file and at a door of their own (madde 317).
_reference_settings_bp = make_reference_settings_blueprint(
    get_reference_settings=partial(get_settings, _reference_settings_store),
    save_reference_settings=partial(save_reference_settings, _reference_settings_store),
)


_start_export = partial(
    start_export, _export_runner, _photo_store, _photo_record, _plan_store, _order_store,
    _video_exporter,
    # Local time and down to the minute: the folder's name is read by a person, and two exports of
    # the same opening are meant to land together (madde 92).
    lambda: datetime.now().strftime("%Y-%m-%d %H-%M"))


def _cancel_export():
    """Both modes: leaving the screen cancels whatever it started."""
    for mode in MODES:
        _export_runner.cancel(mode)


def _timing(line):
    """Where the loop's per-frame timing line lands: this process's own output, which in Colab is
    the cell left open on the server. flush=True because Python block-buffers a redirected stdout,
    and a line that sits in the buffer is a line the watching cell does not show."""
    print(line, flush=True)


# The project's reference pool: a folder of its own inside the project (madde 297). Defined above
# the cards' blueprint because that blueprint is handed _reference_files, and a module body runs
# top to bottom.
_clips = FfmpegClips()
_reference_store = DriveReferenceStore(_storage, _clips)
# Which slot each reference stands in: the folder cannot answer that, so it has a document of its
# own beside the gallery's order file (madde 300).
_reference_orders = DriveReferenceOrderStore(_storage)
# What a pool-made video is rendered from, asked at the job's turn (madde 304). Every door into the
# queue carries it, because any run can reach a card that was made of the pool.
_reference_files = partial(reference_files, _photo_store, _reference_store, _reference_orders)

# How long the project's videos run (madde 422): a file of its own in the project, behind a door of
# its own, which every way into the queue reads.
_video_lengths = DriveVideoLengthStore(_storage)
_video_length = partial(get_video_length, _video_lengths)
# Whether they end happily (madde 426): the length's twin, a file and a door of its own.
_happy_endings = DriveHappyEndingStore(_storage)
_happy_ending = partial(get_happy_ending, _happy_endings)

_photo_bp = make_photo_generation_blueprint(
    start_batch=partial(start_batch, _photo_runner, _photo_store, _photo_record, _plan_store,
                        _producers, seed.random_seed,
                        lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        log=_timing, order_store=_order_store, writers=_writers, stills=_stills,
                        references=_reference_files),
    get_status=partial(get_status, _photo_runner),
    stop_generation=partial(stop_generation, _photo_runner, _comfy_client.interrupt),
    resume_batch=partial(resume_batch, _photo_runner, _photo_store, _photo_record, _plan_store,
                         _producers,
                         lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                         log=_timing, order_store=_order_store, writers=_writers, stills=_stills,
                        references=_reference_files),
    cancel_generation=partial(cancel_generation, _photo_runner, _photo_store, _photo_record,
                              _plan_store,
                              lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
    retry_frame=partial(retry_frame, _photo_runner, _photo_store, _photo_record, _plan_store,
                        _producers,
                        lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        log=_timing, order_store=_order_store, writers=_writers, stills=_stills,
                        references=_reference_files, length=_video_length,
                        ending=_happy_ending),
    retry_failed=partial(retry_failed, _photo_runner, _photo_store, _photo_record, _plan_store,
                         _producers,
                         lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                         log=_timing, order_store=_order_store, writers=_writers, stills=_stills,
                        references=_reference_files, length=_video_length,
                        ending=_happy_ending),
    queue_layer=partial(queue_layer, _photo_runner, _photo_store, _photo_record, _plan_store,
                        _order_store, _producers,
                        lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        log=_timing, writers=_writers, stills=_stills,
                        references=_reference_files, length=_video_length,
                        ending=_happy_ending),
    regenerate=partial(regenerate, _photo_runner, _photo_store, _photo_record, _plan_store,
                       _order_store, _producers, seed.random_seed,
                       lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       log=_timing, writers=_writers, stills=_stills,
                       references=_reference_files, length=_video_length,
                       ending=_happy_ending),
    remove_layer=partial(remove_layer, _photo_record, _photo_store, _plan_store, _order_store,
                         lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
    list_frames=partial(list_frames, _photo_record, _photo_store, _plan_store, _order_store),
    list_models=partial(list_models, config.PHOTO_MODELS),
    list_loras=list_loras,
    save_order=partial(save_order, _photo_record, _photo_store, _plan_store, _order_store),
    # How long a video runs is on its line, its producer's answer (madde 423). A line written before
    # says nothing, and its video ran as long as the graph says -- so the producer that owns the
    # graph answers for it. That is H3's: a WAN video's line from before 423 counts at H3's four
    # seconds, as an H3 session always counted it (madde 435).
    export_summary=partial(export_summary, _photo_record, _photo_store, _plan_store, _order_store,
                           _video_generator.seconds),
    export_state=_export_runner.state,
    run_export=_start_export,
    cancel_export=_cancel_export,
    remove_frames=partial(remove_frames, _photo_record, _photo_store, _plan_store, _order_store,
                          lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
    copy_frames=partial(copy_frames, _photo_record, _photo_store, _plan_store, _order_store,
                        lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
    photo_dir=_photo_store.photo_dir,
)

# The pool's own surface, beside the cards' blueprint rather than inside it -- the two answer
# different questions.
_references_bp = make_reference_blueprint(
    add_references=partial(add_references, _photo_store, _reference_store, _reference_orders,
                           _clips),
    list_references=partial(list_references, _photo_store, _reference_store, _reference_orders),
    remove_reference=partial(remove_reference, _photo_store, _reference_store, _reference_orders),
    save_reference_order=partial(save_reference_order, _photo_store, _reference_store,
                                 _reference_orders),
    queue_references=partial(queue_references, _photo_runner, _photo_store, _photo_record,
                             _plan_store, _order_store, _reference_store, _reference_orders,
                             _producers, seed.random_seed,
                             lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                             log=_timing, writers=_writers, stills=_stills,
                             length=_video_length, ending=_happy_ending),
    reference_dir=_reference_store.dir_path,
)

# The project's video length: the panel saves and reads it here, the queue reads it above.
_video_length_bp = make_video_length_blueprint(
    get_video_length=partial(get_video_length, _video_lengths),
    save_video_length=partial(save_video_length, _video_lengths))
_happy_ending_bp = make_happy_ending_blueprint(
    get_happy_ending=_happy_ending,
    save_happy_ending=partial(save_happy_ending, _happy_endings))

# Every producer is judged by its own model group: installed means those files are on this machine.
# Nothing is installed from here -- the notebook does that before this process starts
# (FOUNDATION 9), so the panel only reads.
_producers_bp = make_producers_blueprint(
    list_producers=lambda: list_producers(GROUPS, _model_files))

# The agent's chats: one record per project, kept in the project's own folder (madde 417). One
# object for every writer -- the doors and every agent -- so its lock keeps all their lines whole
# (madde 420).
_chat_record = DriveChatRecord(_storage)
_chats_bp = make_chats_blueprint(new_chat=partial(new_chat, _chat_record),
                                 list_chats=partial(list_chats, _chat_record),
                                 open_chat=partial(open_chat, _chat_record))

# The agent (madde 420): Queen AI reading the open project through the box. It reads what the gallery
# shows -- the photo feature's own answer, handed in here because a feature never imports another --
# and a frame's photo, and nothing it is handed can write.
_agent = partial(answer_question, _queen_ai,
                 partial(list_frames, _photo_record, _photo_store, _plan_store, _order_store),
                 _photo_store.read)
# Which chats' agents are working: in this process alone, so a restart ends them all.
_agent_runner = AgentRunner(_chat_record)
_agent_bp = make_agent_blueprint(
    ask_question=partial(ask_question, _chat_record, _agent_runner, _agent,
                         lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
    stop_agent=partial(stop_agent, _chat_record, _agent_runner),
    working_chats=partial(working_chats, _chat_record, _agent_runner))

app = create_app(blueprints=[_projects_bp, _reference_settings_bp, _photo_bp, _references_bp,
                             _video_length_bp, _happy_ending_bp, _producers_bp, _chats_bp,
                             _agent_bp])

if __name__ == "__main__":
    print(f"Proje kökü: {config.DRIVE_ROOT}")
    print(f"ComfyUI: {config.COMFY_URL}")
    app.run(host=config.HOST, port=config.PORT)
