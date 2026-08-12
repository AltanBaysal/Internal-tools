"""Composition root -- build services, wire them into features, start Flask.
Run as: python -m backend.main"""
import random
import time
from datetime import datetime, timezone
from functools import partial

from backend import config
from backend.features.photo_generation.data.comfy_photo_generator import ComfyPhotoGenerator
from backend.features.photo_generation.data.ffmpeg_audio import FfmpegAudio
from backend.features.photo_generation.data.mmaudio_generator import MMAudioGenerator
from backend.features.photo_generation.data.mmaudio_sampler import MMAudioSampler
from backend.features.photo_generation.data.comfy_video_generator import ComfyVideoGenerator
from backend.features.photo_generation.data.xai_prompt_writer import (
    AudioPromptWriter,
    VideoPromptWriter,
)
from backend.features.photo_generation.domain import layers
from backend.features.photo_generation.data.order_store import DriveOrderStore
from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.features.photo_generation.domain.usecases.remove_frames import remove_frames
from backend.features.photo_generation.data.ffmpeg_video_exporter import FfmpegVideoExporter
from backend.features.photo_generation.domain.usecases.export_summary import export_summary
from backend.features.photo_generation.domain.usecases.run_export import start_export
from backend.features.photo_generation.export_runner import MODES, ExportRunner
from backend.features.photo_generation.domain.usecases.cancel_generation import cancel_generation
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.halt_project import halt_project
from backend.features.photo_generation.domain.usecases.queue_layer import queue_layer
from backend.features.photo_generation.domain.usecases.regenerate import regenerate
from backend.features.photo_generation.domain.usecases.remove_layer import remove_layer
from backend.features.photo_generation.domain.usecases.retry_failed import retry_failed
from backend.features.photo_generation.domain.usecases.retry_frame import retry_frame
from backend.features.photo_generation.domain.usecases.resume_batch import resume_batch
from backend.features.photo_generation.domain.usecases.list_frames import list_frames
from backend.features.photo_generation.domain.usecases.list_models import list_models
from backend.features.photo_generation.domain.usecases.save_order import save_order
from backend.features.photo_generation.domain.usecases.start_batch import start_batch
from backend.features.photo_generation.domain.usecases.stop_generation import stop_generation
from backend.features.photo_generation.presentation.routes import make_photo_generation_blueprint
from backend.features.photo_generation.runner import PhotoRunner
from backend.features.projects.data.project_store import DriveProjectStore
from backend.features.projects.data.settings_store import DriveSettingsStore
from backend.features.projects.domain.usecases.check_name import check_name
from backend.features.projects.domain.usecases.create_project import create_project
from backend.features.projects.domain.usecases.delete_project import delete_project
from backend.features.projects.domain.usecases.get_settings import get_settings
from backend.features.projects.domain.usecases.list_projects import list_projects
from backend.features.projects.domain.usecases.save_settings import save_settings
from backend.features.producers.data.comfy_models import ComfyModelFiles
from backend.features.producers.domain.model_groups import (
    CIVITAI,
    GROUPS,
    audio_weights,
    civitai_headers,
)
from backend.features.producers.domain.usecases.cancel_install import cancel_install
from backend.features.producers.domain.usecases.install_producer import install_producer
from backend.features.producers.domain.usecases.list_producers import list_producers
from backend.features.producers.presentation.routes import make_producers_blueprint
from backend.features.producers.runner import InstallRunner
from backend.features.projects.presentation.routes import make_projects_blueprint
from backend.services.comfy.client import ComfyClient
from backend.services.download.fetcher import HttpFetcher
from backend.services.drive.storage import DriveStorage
from backend.services.xai.client import XaiClient
from backend.web.app import create_app

# One storage, shared by both features: they are separate features over the same Drive root.
_storage = DriveStorage(config.DRIVE_ROOT)

_project_store = DriveProjectStore(_storage)
_settings_store = DriveSettingsStore(_storage)

_photo_store = DrivePhotoStore(_storage)
_comfy_client = ComfyClient(config.COMFY_URL, poll_interval=config.POLL_INTERVAL)
_photo_generator = ComfyPhotoGenerator(_comfy_client, config.WORKFLOW_PATH, config.RENDER_TIMEOUT)
_video_generator = ComfyVideoGenerator(_comfy_client, config.VIDEO_WORKFLOW_PATH,
                                       config.VIDEO_TIMEOUT)
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
_xai = XaiClient(config.XAI_API_KEY, config.XAI_MODEL, config.XAI_URL, timeout=config.XAI_TIMEOUT)
_writers = {layers.VIDEO: VideoPromptWriter(_xai), layers.AUDIO: AudioPromptWriter(_xai)}
_photo_runner = PhotoRunner()
_photo_record = DrivePhotoRecord(_storage)
_plan_store = DrivePlanStore(_storage)
_order_store = DriveOrderStore(_storage)

_export_runner = ExportRunner()
_video_exporter = FfmpegVideoExporter()

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
    get_settings=partial(get_settings, _settings_store),
    save_settings=partial(save_settings, _settings_store),
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


_photo_bp = make_photo_generation_blueprint(
    start_batch=partial(start_batch, _photo_runner, _photo_store, _photo_record, _plan_store,
                        _producers, lambda: random.randint(0, 2**31 - 1),
                        lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        log=_timing, order_store=_order_store, writers=_writers),
    get_status=partial(get_status, _photo_runner),
    stop_generation=partial(stop_generation, _photo_runner, _comfy_client.interrupt),
    resume_batch=partial(resume_batch, _photo_runner, _photo_store, _photo_record, _plan_store,
                         _producers,
                         lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                         log=_timing, order_store=_order_store, writers=_writers),
    cancel_generation=partial(cancel_generation, _photo_runner, _photo_store, _photo_record,
                              _plan_store,
                              lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
    retry_frame=partial(retry_frame, _photo_runner, _photo_store, _photo_record, _plan_store,
                        _producers,
                        lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        log=_timing, order_store=_order_store, writers=_writers),
    retry_failed=partial(retry_failed, _photo_runner, _photo_store, _photo_record, _plan_store,
                         _producers,
                         lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                         log=_timing, order_store=_order_store, writers=_writers),
    queue_layer=partial(queue_layer, _photo_runner, _photo_store, _photo_record, _plan_store,
                        _order_store, _producers,
                        lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                        log=_timing, writers=_writers),
    regenerate=partial(regenerate, _photo_runner, _photo_store, _photo_record, _plan_store,
                       _order_store, _producers, lambda: random.randint(0, 2**31 - 1),
                       lambda: datetime.now(timezone.utc).isoformat(timespec="seconds"),
                       log=_timing, writers=_writers),
    remove_layer=partial(remove_layer, _photo_record, _photo_store, _plan_store, _order_store,
                         lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
    list_frames=partial(list_frames, _photo_record, _photo_store, _plan_store, _order_store),
    list_models=partial(list_models, _photo_generator),
    save_order=partial(save_order, _photo_record, _photo_store, _plan_store, _order_store),
    export_summary=partial(export_summary, _photo_record, _photo_store, _plan_store, _order_store),
    export_state=_export_runner.state,
    run_export=_start_export,
    cancel_export=_cancel_export,
    remove_frames=partial(remove_frames, _photo_record, _photo_store, _plan_store, _order_store,
                          lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
    photo_dir=_photo_store.photo_dir,
)

# Every producer is judged by its own model group: installed means those files are on this machine.
_fetcher = HttpFetcher()
_install_runner = InstallRunner()
# The keys the installer may need, by source. Built here because a secret belongs in no other
# layer; an empty map is a real answer -- the install then stops at a gated row and says so.
_auth = {CIVITAI: civitai_headers(config.CIVITAI_COOKIE)} if config.CIVITAI_COOKIE else {}
_producers_bp = make_producers_blueprint(
    list_producers=lambda: list_producers(GROUPS, _model_files,
                                          running=_install_runner.status()),
    install_producer=partial(install_producer, GROUPS, _model_files, _fetcher, _install_runner,
                             _auth),
    cancel_install=partial(cancel_install, _install_runner),
)

app = create_app(blueprints=[_projects_bp, _photo_bp, _producers_bp])

if __name__ == "__main__":
    print(f"Proje kökü: {config.DRIVE_ROOT}")
    print(f"ComfyUI: {config.COMFY_URL}")
    app.run(host=config.HOST, port=config.PORT)
