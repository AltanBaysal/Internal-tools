"""create_app -- the Flask app factory: /api blueprints + static dist serving."""
import os

from flask import Flask, jsonify, send_from_directory

from backend.services.storage.storage import NameRefused
from backend.web.health import health_bp
from backend import config


def create_app(dist_dir=config.DIST_DIR, blueprints=()):
    app = Flask(__name__, static_folder=None)  # dist is served by our own routes
    app.config["DIST_DIR"] = dist_dir
    app.register_blueprint(health_bp)
    # Features are injected by the composition root: this infrastructure layer must not import
    # any feature (CODE-STANDARD.md).
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    # Every OSError a route lets through, in one place: the sentence it carries goes to the screen,
    # which prints body.error. Without it a route that caught nothing answered with Flask's HTML
    # page, and the screen said "HTTP 500". That is Drive's failures -- a dropped mount, a file that
    # could not be read -- and every other OSError too: a socket that timed out on ComfyUI, and
    # requests' errors, which are IOErrors, from DeepSeek. 503 because what failed is a service
    # behind the request, not the request.
    @app.errorhandler(OSError)
    def service_failed(exc):
        return jsonify({"error": str(exc)}), 503

    # A name the storage door turned away is the asker's error. Flask answers an exception with the
    # handler of its nearest class, so this one wins over the OSError one above.
    @app.errorhandler(NameRefused)
    def name_refused(exc):
        return jsonify({"error": str(exc)}), 400

    @app.get("/")
    def index():
        return send_from_directory(app.config["DIST_DIR"], "index.html")

    # Any other path: serve the file if it exists, else fall back to index.html (SPA).
    # /api/* is matched by the more specific health rule first, so it never reaches here.
    @app.get("/<path:path>")
    def static_or_spa(path):
        full = os.path.join(app.config["DIST_DIR"], path)
        if os.path.isfile(full):
            return send_from_directory(app.config["DIST_DIR"], path)
        return send_from_directory(app.config["DIST_DIR"], "index.html")

    return app
