import time

import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.data.memory_stops import MemoryStops
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
                MemoryStops(),
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


def test_search_is_gone(tmp_path):
    # The design removes search deliberately, so the endpoint is not there to answer.
    client = _client(tmp_path)
    assert client.get("/api/search?q=quantum").status_code == 404
    assert client.get("/api/search").status_code == 404


def test_a_file_cannot_be_renamed(tmp_path):
    # Renaming lives on the project alone. 405 rather than 404: GET and DELETE still answer there.
    client = _client(tmp_path)
    pid = client.post("/api/projects").get_json()["id"]
    _files(tmp_path).write(pid, "plan.md", "body")
    resp = client.patch(f"/api/projects/{pid}/files/plan.md", json={"name": "outline.md"})
    assert resp.status_code == 405
    assert client.get(f"/api/projects/{pid}/files/plan.md").get_json()["text"] == "body"


def test_the_file_rename_use_case_is_gone():
    with pytest.raises(ModuleNotFoundError):
        import backend.features.workspace.domain.usecases.rename_file  # noqa: F401


def test_the_store_offers_no_rename(tmp_path):
    # The port shrank with the use case: nothing is left that can move a file inside files/.
    assert not hasattr(_files(tmp_path), "rename")


def test_deleting_over_http_answers_with_the_trash_name(tmp_path):
    client = _client(tmp_path)
    pid = client.post("/api/projects").get_json()["id"]
    _files(tmp_path).write(pid, "plan.md", "body")
    resp = client.delete(f"/api/projects/{pid}/files/plan.md")
    assert resp.status_code == 200
    assert resp.get_json() == {"trashed": "plan.md"}
    assert client.get(f"/api/projects/{pid}/files").get_json() == []


def test_deleting_a_file_that_is_gone_is_a_404(tmp_path):
    client = _client(tmp_path)
    pid = client.post("/api/projects").get_json()["id"]
    assert client.delete(f"/api/projects/{pid}/files/ghost.md").status_code == 404


def test_there_is_no_address_that_brings_a_file_back(tmp_path):
    # Karar 16: the question is the protection now, and the trash directory is what keeps the file.
    # The rule table is what proves the offer is gone rather than merely unused.
    client = _client(tmp_path)
    addresses = [str(rule) for rule in client.application.url_map.iter_rules()]
    assert not [address for address in addresses if "restore" in address]


def test_deleting_still_says_where_the_file_went(tmp_path):
    # Nobody reads the name any more, but it is the one sentence that says what happened on disk,
    # and deleting a project answers the same way.
    client = _client(tmp_path)
    pid = client.post("/api/projects").get_json()["id"]
    _files(tmp_path).write(pid, "plan.md", "body")
    assert client.delete(f"/api/projects/{pid}/files/plan.md").get_json()["trashed"] == "plan.md"


def test_the_list_and_one_file_are_different_addresses(tmp_path):
    # Same prefix, two routes: the list must not swallow a name.
    client = _client(tmp_path)
    pid = client.post("/api/projects").get_json()["id"]
    _files(tmp_path).write(pid, "plan.md", "x")
    assert isinstance(client.get(f"/api/projects/{pid}/files").get_json(), list)
    assert isinstance(client.get(f"/api/projects/{pid}/files/plan.md").get_json(), dict)
