"""create_app -- the Flask app factory: /api blueprints + static dist serving."""
import os

from flask import Flask, jsonify, request, send_from_directory

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

    # Every disk failure, in one place (Madde 490): the screen shows the operating system's own
    # sentence -- a Drive that went away above all -- rather than Flask's HTML page, which it read as
    # "HTTP 500". 503: the request was sound and the disk could not do it now. Logged too, since
    # answering here keeps Flask from logging it, and the server's log is where a cause is looked
    # for later.
    @app.errorhandler(OSError)
    def disk_failed(error):
        app.logger.error("%s %s failed on the disk: %s", request.method, request.path, error)
        return jsonify({"error": str(error)}), 503

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
