"""create_app -- the Flask app factory: /api blueprints + static dist serving."""
import os

from flask import Flask, send_from_directory

from backend import config
from backend.web.health import health_bp


def create_app(dist_dir=config.DIST_DIR, blueprints=()):
    app = Flask(__name__, static_folder=None)  # dist is served by our own routes
    app.config["DIST_DIR"] = dist_dir
    app.register_blueprint(health_bp)
    # Features are injected by the composition root: this infrastructure layer must not import any
    # feature (CODE-STANDARD.md).
    for blueprint in blueprints:
        app.register_blueprint(blueprint)

    @app.get("/")
    def index():
        return send_from_directory(app.config["DIST_DIR"], "index.html")

    # Any other path: serve the file if it exists, else fall back to index.html (SPA). /api/* is
    # matched by the more specific blueprint rules first, so it never reaches here.
    @app.get("/<path:path>")
    def static_or_spa(path):
        full = os.path.join(app.config["DIST_DIR"], path)
        if os.path.isfile(full):
            return send_from_directory(app.config["DIST_DIR"], path)
        return send_from_directory(app.config["DIST_DIR"], "index.html")

    return app
