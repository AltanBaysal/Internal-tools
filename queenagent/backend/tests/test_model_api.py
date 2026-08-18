from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app


class FakeEngine:
    def complete(self, messages, tools=None, model=None):
        return {"role": "assistant", "content": ""}

    def stream(self, messages, tools=None, model=None):
        yield {"text": ""}


def _client(tmp_path, default_model="grok-4.5"):
    store = Store(str(tmp_path))
    app = create_app(
        dist_dir=str(tmp_path),
        blueprints=(
            make_workspace_bp(
                FileProjectStore(store),
                FileChatStore(store),
                FileFileStore(store),
                FakeEngine(),
                default_model,
            ),
        ),
    )
    return app.test_client()


# The one thing about the menu that only the server knows. The names and the prices are text and
# stay in the interface; which model a chat that picked nothing will answer with is a setting.
def test_the_server_says_which_model_a_new_chat_starts_from(tmp_path):
    assert _client(tmp_path).get("/api/model").get_json() == {"default": "grok-4.5"}


def test_the_setting_is_what_it_reports(tmp_path):
    assert _client(tmp_path, "grok-4.6").get("/api/model").get_json()["default"] == "grok-4.6"
