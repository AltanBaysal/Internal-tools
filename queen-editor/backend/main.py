"""Composition root -- start the Flask server. Run as: python -m backend.main"""
from backend.web.app import create_app
from backend import config

app = create_app()

if __name__ == "__main__":
    app.run(host=config.HOST, port=config.PORT)
