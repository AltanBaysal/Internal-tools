"""Composition root -- build services, wire them into features, start Flask.
Run as: python -m backend.main"""
from functools import partial

from backend import config
from backend.features.projects.data.project_store import DriveProjectStore
from backend.features.projects.domain.usecases.create_project import create_project
from backend.features.projects.domain.usecases.list_projects import list_projects
from backend.features.projects.presentation.routes import make_projects_blueprint
from backend.services.drive.storage import DriveStorage
from backend.web.app import create_app

_project_store = DriveProjectStore(DriveStorage(config.DRIVE_ROOT))
_projects_bp = make_projects_blueprint(
    list_projects=partial(list_projects, _project_store),
    create_project=partial(create_project, _project_store),
)

app = create_app(blueprints=[_projects_bp])

if __name__ == "__main__":
    print(f"Proje kökü: {config.DRIVE_ROOT}")
    app.run(host=config.HOST, port=config.PORT)
