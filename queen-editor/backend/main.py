"""Composition root -- build services, wire them into features, start Flask.
Run as: python -m backend.main"""
import random
from datetime import datetime, timezone
from functools import partial

from backend import config
from backend.features.photo_generation.data.comfy_photo_generator import ComfyPhotoGenerator
from backend.features.photo_generation.data.order_store import DriveOrderStore
from backend.features.photo_generation.data.photo_record import DrivePhotoRecord
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.data.plan_store import DrivePlanStore
from backend.features.photo_generation.domain.usecases.delete_photos import delete_photos
from backend.features.photo_generation.domain.usecases.export_project import export_project
from backend.features.photo_generation.domain.usecases.cancel_generation import cancel_generation
from backend.features.photo_generation.domain.usecases.get_queue import get_queue
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.retry_frame import retry_frame
from backend.features.photo_generation.domain.usecases.resume_batch import resume_batch
from backend.features.photo_generation.domain.usecases.list_photos import list_photos
from backend.features.photo_generation.domain.usecases.save_order import save_order
from backend.features.photo_generation.domain.usecases.start_batch import start_batch
from backend.features.photo_generation.domain.usecases.stop_generation import stop_generation
from backend.features.photo_generation.presentation.routes import make_photo_generation_blueprint
from backend.features.photo_generation.runner import PhotoRunner
from backend.features.projects.data.project_store import DriveProjectStore
from backend.features.projects.data.settings_store import DriveSettingsStore
from backend.features.projects.domain.usecases.create_project import create_project
from backend.features.projects.domain.usecases.delete_project import delete_project
from backend.features.projects.domain.usecases.get_settings import get_settings
from backend.features.projects.domain.usecases.list_projects import list_projects
from backend.features.projects.domain.usecases.save_settings import save_settings
from backend.features.projects.presentation.routes import make_projects_blueprint
from backend.services.comfy.client import ComfyClient
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app

# One storage, shared by both features: they are separate features over the same Drive root.
_storage = DriveStorage(config.DRIVE_ROOT)

_project_store = DriveProjectStore(_storage)
_settings_store = DriveSettingsStore(_storage)
_projects_bp = make_projects_blueprint(
    list_projects=partial(list_projects, _project_store),
    create_project=partial(create_project, _project_store),
    delete_project=partial(delete_project, _project_store),
    get_settings=partial(get_settings, _settings_store),
    save_settings=partial(save_settings, _settings_store),
)

_photo_store = DrivePhotoStore(_storage)
_comfy_client = ComfyClient(config.COMFY_URL, poll_interval=config.POLL_INTERVAL)
_photo_generator = ComfyPhotoGenerator(_comfy_client, config.WORKFLOW_PATH, config.RENDER_TIMEOUT)
_photo_runner = PhotoRunner()
_photo_record = DrivePhotoRecord(_storage)
_plan_store = DrivePlanStore(_storage)
_order_store = DriveOrderStore(_storage)

_photo_bp = make_photo_generation_blueprint(
    start_batch=partial(start_batch, _photo_runner, _photo_store, _photo_record, _plan_store,
                        _photo_generator, lambda: random.randint(0, 2**31 - 1),
                        lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
    get_status=partial(get_status, _photo_runner),
    stop_generation=partial(stop_generation, _photo_runner, _comfy_client.interrupt),
    resume_batch=partial(resume_batch, _photo_runner, _photo_store, _photo_record, _plan_store,
                         _photo_generator,
                         lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
    cancel_generation=partial(cancel_generation, _photo_runner, _photo_store, _plan_store),
    retry_frame=partial(retry_frame, _photo_runner, _photo_store, _photo_record, _plan_store,
                        _photo_generator,
                        lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
    get_queue=partial(get_queue, _photo_record, _photo_store, _plan_store),
    list_photos=partial(list_photos, _photo_record, _photo_store, _order_store),
    save_order=partial(save_order, _photo_record, _photo_store, _order_store),
    export_project=partial(export_project, _photo_record, _photo_store, _order_store),
    delete_photos=partial(delete_photos, _photo_record, _photo_store, _order_store,
                          lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),
    photo_dir=_photo_store.photo_dir,
)

app = create_app(blueprints=[_projects_bp, _photo_bp])

if __name__ == "__main__":
    print(f"Proje kökü: {config.DRIVE_ROOT}")
    print(f"ComfyUI: {config.COMFY_URL}")
    app.run(host=config.HOST, port=config.PORT)
