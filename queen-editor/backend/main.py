"""Composition root -- build services, wire them into features, start Flask.
Run as: python -m backend.main"""
import random
from functools import partial

from backend import config
from backend.features.photo_generation.data.comfy_photo_generator import ComfyPhotoGenerator
from backend.features.photo_generation.data.photo_store import DrivePhotoStore
from backend.features.photo_generation.domain.usecases.get_status import get_status
from backend.features.photo_generation.domain.usecases.start_generation import start_generation
from backend.features.photo_generation.presentation.routes import make_photo_generation_blueprint
from backend.features.photo_generation.runner import PhotoRunner
from backend.features.projects.data.project_store import DriveProjectStore
from backend.features.projects.domain.usecases.create_project import create_project
from backend.features.projects.domain.usecases.list_projects import list_projects
from backend.features.projects.presentation.routes import make_projects_blueprint
from backend.services.comfy.client import ComfyClient
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app

# One storage, shared by both features: they are separate features over the same Drive root.
_storage = DriveStorage(config.DRIVE_ROOT)

_project_store = DriveProjectStore(_storage)
_projects_bp = make_projects_blueprint(
    list_projects=partial(list_projects, _project_store),
    create_project=partial(create_project, _project_store),
)

_photo_store = DrivePhotoStore(_storage)
_comfy_client = ComfyClient(config.COMFY_URL, poll_interval=config.POLL_INTERVAL)
_photo_generator = ComfyPhotoGenerator(_comfy_client, config.WORKFLOW_PATH, config.RENDER_TIMEOUT)
_photo_runner = PhotoRunner()

_photo_bp = make_photo_generation_blueprint(
    start_generation=partial(start_generation, _photo_runner, _photo_store, _photo_generator,
                             lambda: random.randint(0, 2**31 - 1)),
    get_status=partial(get_status, _photo_runner),
    photo_dir=_photo_store.photo_dir,
)

app = create_app(blueprints=[_projects_bp, _photo_bp])

if __name__ == "__main__":
    print(f"Proje kökü: {config.DRIVE_ROOT}")
    print(f"ComfyUI: {config.COMFY_URL}")
    app.run(host=config.HOST, port=config.PORT)
