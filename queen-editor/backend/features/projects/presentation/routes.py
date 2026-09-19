"""/api/projects -- request/response translation only. No rules, no filesystem knowledge."""
from flask import Blueprint, jsonify, request

from backend.features.projects.domain.usecases.create_project import InvalidName, NameTaken
from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def make_projects_blueprint(list_projects, create_project, check_name, delete_project,
                            rename_project, get_settings, save_settings,
                            archive_project, restore_project, list_archived_projects):
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

    @bp.post("/api/projects/<project>/rename")
    def post_rename_project(project):
        name = (request.get_json(silent=True) or {}).get("name", "")
        try:
            rename_project(project, name)
        except InvalidName as exc:
            return jsonify({"error": str(exc)}), 400
        except NameTaken as exc:
            return jsonify({"error": str(exc)}), 409
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500
        # The name is the whole answer: the screen re-reads the list, which is where the date and
        # the order come from.
        return jsonify({"name": name})

    # Before the <project> routes in the file only for reading: Flask prefers a literal segment to a
    # variable one whatever the order, and this path is one segment deep where those are two.
    @bp.get("/api/projects/archived")
    def get_archived_projects():
        try:
            projects = list_archived_projects()
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500
        return jsonify({"projects": [payload(p) for p in projects]})

    # No 409 on either of these: since madde 227 archiving marks a project rather than moving it, so
    # there is no name for it to land on. Catching something that cannot be raised would show a
    # later reader a road that is not there.
    @bp.post("/api/projects/<project>/archive")
    def post_archive_project(project):
        try:
            archive_project(project)
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500
        # 204, like delete: the client re-reads both lists, which is all that changed.
        return "", 204

    @bp.post("/api/projects/<project>/restore")
    def post_restore_project(project):
        try:
            restore_project(project)
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500
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
        model, lora = body.get("model"), body.get("lora")
        try:
            save_settings(
                project,
                prompts if isinstance(prompts, str) else "",
                negative if isinstance(negative, str) else "",
                # bool is an int in Python, and True would silently mean "1 variant".
                variants if isinstance(variants, int) and not isinstance(variants, bool) else None,
                model if isinstance(model, str) else "",
                lora if isinstance(lora, str) else "",
            )
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500
        # 204: the client already has what it sent; there is nothing to send back.
        return "", 204

    return bp
