import time

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.file import extension_of
from backend.features.workspace.domain.usecases.list_files import list_files
from backend.features.workspace.presentation.routes import make_workspace_bp
from backend.services.store.store import Store
from backend.web.app import create_app


class FakeEngine:
    def stream(self, messages, tools=None):
        yield {"text": "Done."}


def _client(tmp_path):
    store = Store(str(tmp_path))
    app = create_app(
        dist_dir=str(tmp_path),
        blueprints=(
            make_workspace_bp(
                FileProjectStore(store),
                FileChatStore(store),
                FileFileStore(store),
                FakeEngine(),
            ),
        ),
    )
    return app.test_client()


def _files(tmp_path):
    return FileFileStore(Store(str(tmp_path)))


def test_the_chip_is_three_letters_of_the_extension():
    assert extension_of("plan.md") == "md"
    assert extension_of("notes.MARKDOWN") == "mar"
    assert extension_of("no-extension") == "no-"


def test_an_empty_project_lists_nothing(tmp_path):
    assert list_files(_files(tmp_path), "p1") == []


def test_files_come_back_newest_first(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "older.md", "a")
    # mtime resolution is coarse enough that two writes in the same instant would tie.
    time.sleep(0.01)
    files.write("p1", "newer.md", "b")
    assert [file.name for file in list_files(files, "p1")] == ["newer.md", "older.md"]


def test_the_listing_carries_the_chip_and_a_time(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "a")
    listed = list_files(files, "p1")[0]
    assert listed.ext == "md"
    assert listed.modified_at.startswith("20")


def test_the_endpoint_answers_an_empty_project_without_blowing_up(tmp_path):
    client = _client(tmp_path)
    pid = client.post("/api/projects").get_json()["id"]
    resp = client.get(f"/api/projects/{pid}/files")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_the_endpoint_lists_what_the_model_wrote(tmp_path):
    client = _client(tmp_path)
    pid = client.post("/api/projects").get_json()["id"]
    _files(tmp_path).write(pid, "plan.md", "body")
    listed = client.get(f"/api/projects/{pid}/files").get_json()
    assert listed[0]["name"] == "plan.md"
    assert listed[0]["ext"] == "md"
    assert "modifiedAt" in listed[0]


def test_one_file_comes_back_whole(tmp_path):
    client = _client(tmp_path)
    pid = client.post("/api/projects").get_json()["id"]
    _files(tmp_path).write(pid, "plan.md", "the body")
    body = client.get(f"/api/projects/{pid}/files/plan.md").get_json()
    assert body["name"] == "plan.md"
    assert body["ext"] == "md"
    assert body["size"] == 8
    assert body["text"] == "the body"
    assert "modifiedAt" in body


def test_reading_a_file_that_is_gone_is_a_404(tmp_path):
    client = _client(tmp_path)
    pid = client.post("/api/projects").get_json()["id"]
    resp = client.get(f"/api/projects/{pid}/files/ghost.md")
    assert resp.status_code == 404
    assert "not found" in resp.get_json()["error"]


def test_the_list_and_one_file_are_different_addresses(tmp_path):
    # Same prefix, two routes: the list must not swallow a name.
    client = _client(tmp_path)
    pid = client.post("/api/projects").get_json()["id"]
    _files(tmp_path).write(pid, "plan.md", "x")
    assert isinstance(client.get(f"/api/projects/{pid}/files").get_json(), list)
    assert isinstance(client.get(f"/api/projects/{pid}/files/plan.md").get_json(), dict)
