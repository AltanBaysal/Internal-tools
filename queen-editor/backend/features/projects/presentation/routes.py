"""/api/projects -- request/response translation only. No rules, no filesystem knowledge."""
from flask import Blueprint, jsonify, request

from backend.features.projects.domain.usecases.create_project import InvalidName, NameTaken
from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def make_projects_blueprint(list_projects, create_project, check_name, delete_project, get_settings,
                            save_settings):
    """Every argument is a use case already bound to a store (see main.py)."""
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

    # A GET because it changes nothing: the modal asks it while the name is being typed, and the
    # answer is the rules' own sentence rather than a code the frontend would have to translate.
    @bp.get("/api/projects/name-check")
    def get_name_check():
        return jsonify({"error": check_name(request.args.get("name", ""))})

    @bp.delete("/api/projects/<project>")
    def delete_one_project(project):
        try:
            delete_project(project)
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500
        # 204: the client reloads the list, which is the only thing that changed.
        return "", 204

    @bp.get("/api/projects/<project>/settings")
    def get_project_settings(project):
        try:
            return jsonify(get_settings(project))
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500

    @bp.put("/api/projects/<project>/settings")
    def put_project_settings(project):
        body = request.get_json(silent=True) or {}
        prompts, negative, variants = (body.get("prompts"), body.get("negative"),
                                       body.get("variants"))
        model = body.get("model")
        try:
            save_settings(
                project,
                prompts if isinstance(prompts, str) else "",
                negative if isinstance(negative, str) else "",
                # bool is an int in Python, and True would silently mean "1 variant".
                variants if isinstance(variants, int) and not isinstance(variants, bool) else None,
                model if isinstance(model, str) else "",
            )
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500
        # 204: the client already has what it sent; there is nothing to send back.
        return "", 204

    return bp
