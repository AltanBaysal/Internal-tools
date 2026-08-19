"""HTTP for the settings: read them, change them. No business logic lives here."""
from flask import Blueprint, jsonify, request

from backend.features.settings.domain.usecases.read_settings import read_settings
from backend.features.settings.domain.usecases.save_settings import save_settings


def make_settings_bp(settings_store):
    settings_bp = Blueprint("settings", __name__)

    @settings_bp.get("/api/settings")
    def get_settings():
        return jsonify(_json(read_settings(settings_store)))

    @settings_bp.patch("/api/settings")
    def patch_settings():
        payload = request.get_json(silent=True) or {}
        # What the settings hold is decided here rather than by whatever the browser sends.
        if "apiKey" not in payload:
            return jsonify({"error": "settings only carry an apiKey"}), 400
        return jsonify(_json(save_settings(settings_store, payload["apiKey"])))

    return settings_bp


def _json(settings):
    # Plain text, deliberately: this is the user's own machine and their own key, and a masked one
    # they cannot read back would be a worse answer than the key itself.
    return {"apiKey": settings.api_key}
