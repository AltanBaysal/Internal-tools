"""/api/projects -- request/response translation only. No rules, no filesystem knowledge."""
from flask import Blueprint, jsonify, request

from backend.features.projects.domain.usecases.create_project import InvalidName, NameTaken


def make_projects_blueprint(list_projects, create_project):
    """Both arguments are use cases already bound to a store (see main.py)."""
    bp = Blueprint("projects", __name__)

    def payload(project):
        # The UI shows whole seconds; the float's precision means nothing to it.
        return {"name": project.name, "modifiedAt": int(project.modified_at)}

    @bp.get("/api/projects")
    def get_projects():
        try:
            projects = list_projects()
        except OSError as exc:
            # The operating system's own words -- never guess the cause (missing mount, no
            # permission and a wrong path all land here with different messages).
            return jsonify({"error": str(exc)}), 500
        return jsonify({"projects": [payload(p) for p in projects]})

    @bp.post("/api/projects")
    def post_project():
        name = (request.get_json(silent=True) or {}).get("name", "")
        try:
            project = create_project(name)
        except InvalidName as exc:
            return jsonify({"error": str(exc)}), 400
        except NameTaken as exc:
            return jsonify({"error": str(exc)}), 409
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500
        return jsonify(payload(project)), 201

    return bp
