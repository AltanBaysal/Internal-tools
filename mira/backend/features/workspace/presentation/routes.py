"""Workspace HTTP routes -- request/response translation only, no business rules."""
import uuid
from datetime import datetime, timezone

from flask import Blueprint, jsonify

from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.list_projects import list_projects


def make_workspace_bp(project_store):
    workspace_bp = Blueprint("workspace", __name__)

    @workspace_bp.get("/api/projects")
    def get_projects():
        return jsonify([_as_json(project) for project in list_projects(project_store)])

    @workspace_bp.post("/api/projects")
    def post_project():
        # Creating takes no input: the design never asks for a name up front.
        project = create_project(project_store, new_id=_new_id(), now=_now())
        return jsonify(_as_json(project)), 201

    return workspace_bp


def _new_id():
    # Opaque and immutable: renaming a project must not move its directory or break a link.
    return "p" + uuid.uuid4().hex[:12]


def _now():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _as_json(project):
    return {
        "id": project.id,
        "name": project.name,
        "desc": project.desc,
        "hue": project.hue,
        "createdAt": project.created_at,
    }
