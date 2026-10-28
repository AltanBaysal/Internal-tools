import pytest

from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.data.live_turns import LiveTurns
from backend.features.workspace.presentation.routes import (
    NOT_ARCHIVED,
    NOT_IDS,
    PROJECTS_BUSY,
    make_workspace_bp,
)
from backend.services.store.store import Store
from backend.web.app import create_app


class FakeEngine:
    def stream(self, messages, tools=None, on_open=None):
        yield {"text": "Done."}


def _wired(tmp_path, turns=None):
    store = Store(str(tmp_path))
    projects = FileProjectStore(store)
    app = create_app(
        dist_dir=str(tmp_path),
        blueprints=(
            make_workspace_bp(
                projects,
                FileChatStore(store, projects),
                FileFileStore(store, projects, {}, ""),
                FakeEngine(),
                turns or LiveTurns(),
            ),
        ),
    )
    return app.test_client(), projects


def _client(tmp_path):
    return _wired(tmp_path)[0]


def _create(client, name="Thesis"):
    # Madde 361: a project is born with the name the naming screen asked for.
    return client.post("/api/projects", json={"name": name})


def test_empty_root_returns_an_empty_list(tmp_path):
    resp = _client(tmp_path).get("/api/projects")
    assert resp.status_code == 200
    assert resp.get_json() == []


def test_a_stray_file_beside_the_projects_is_not_one(tmp_path):
    # The list is projects.json and nothing else under the root. The root is on the user's own
    # Drive or disk, so a file nobody planned for -- or a project folder an older version left (no
    # migration, Madde 447) -- can sit there at any time, and it must not become a row.
    (tmp_path / "notes.json").write_text('{"anything": "at all"}', encoding="utf-8")
    (tmp_path / "pold").mkdir()
    (tmp_path / "pold" / "project.json").write_text(
        '{"name": "Old", "createdAt": "2026-08-09T10:00:00+00:00"}', encoding="utf-8"
    )
    assert _client(tmp_path).get("/api/projects").get_json() == []


def test_created_project_appears_in_the_list(tmp_path):
    client = _client(tmp_path)
    created = _create(client, "Harbour")
    assert created.status_code == 201
    body = created.get_json()
    # One request, and the name the user typed: no project is ever left under a name nobody chose.
    assert body["name"] == "Harbour"
    assert body["id"].startswith("p")
    assert client.get("/api/projects").get_json() == [body]


def test_a_project_needs_a_name_to_be_born(tmp_path):
    # The same words a rename to nothing gets: it is one rule about what a project's name may be.
    client = _client(tmp_path)
    for asked in (
        client.post("/api/projects"),
        client.post("/api/projects", json={}),
        client.post("/api/projects", json={"name": "  "}),
    ):
        assert asked.status_code == 400
        assert asked.get_json() == {"error": "a project needs a name"}
    assert client.get("/api/projects").get_json() == []


def test_projects_survive_a_fresh_app(tmp_path):
    client, projects = _wired(tmp_path)
    _create(client)
    projects.flush()
    assert len(_client(tmp_path).get("/api/projects").get_json()) == 1


def test_project_payload_carries_zero_counts_before_anything_exists(tmp_path):
    body = _create(_client(tmp_path)).get_json()
    assert body["chats"] == 0
    assert body["files"] == 0


def test_two_projects_get_different_ids(tmp_path):
    # The id is all that tells them apart when two are given the same name.
    client = _client(tmp_path)
    first = _create(client).get_json()
    second = _create(client).get_json()
    assert first["id"] != second["id"]


def test_patch_renames_a_project(tmp_path):
    client = _client(tmp_path)
    created = _create(client).get_json()
    resp = client.patch(f"/api/projects/{created['id']}", json={"name": "Harbour"})
    assert resp.status_code == 200
    assert resp.get_json()["name"] == "Harbour"
    assert client.get("/api/projects").get_json()[0]["name"] == "Harbour"


def test_patch_rejects_an_empty_name(tmp_path):
    client = _client(tmp_path)
    created = _create(client).get_json()
    assert client.patch(f"/api/projects/{created['id']}", json={"name": "  "}).status_code == 400


def test_patch_on_an_unknown_project_is_404(tmp_path):
    assert _client(tmp_path).patch("/api/projects/nope", json={"name": "x"}).status_code == 404


def test_patch_keeps_the_counts_in_the_answer(tmp_path):
    client = _client(tmp_path)
    created = _create(client).get_json()
    body = client.patch(f"/api/projects/{created['id']}", json={"name": "Harbour"}).get_json()
    assert body["chats"] == 0
    assert body["files"] == 0


def test_a_description_in_the_body_is_simply_not_a_field(tmp_path):
    # PATCH sends what changed; a key the project has no room for is not an error, it is nothing.
    client = _client(tmp_path)
    created = _create(client).get_json()
    resp = client.patch(f"/api/projects/{created['id']}", json={"desc": "Notes."})
    assert resp.status_code == 200
    assert "desc" not in resp.get_json()


def test_the_answer_carries_neither_a_description_nor_a_colour(tmp_path):
    created = _create(_client(tmp_path)).get_json()
    # Madde 339 added the pin and the archive, and 346 the last use; neither a description nor a
    # colour came back with them.
    assert set(created) == {
        "id", "name", "createdAt", "chats", "files", "pinned", "archived", "lastActivity",
    }


def test_a_project_can_be_deleted(tmp_path):
    client = _client(tmp_path)
    created = _create(client).get_json()
    resp = client.delete(f"/api/projects/{created['id']}")
    assert resp.status_code == 200
    assert resp.get_json()["trashed"] == created["id"]
    assert client.get("/api/projects").get_json() == []


def test_deleting_a_project_that_is_not_there_says_so(tmp_path):
    resp = _client(tmp_path).delete("/api/projects/nope")
    assert resp.status_code == 404
    assert "not found" in resp.get_json()["error"]


# ---- Several at once (Madde 506): one request, and its answer is the list ----


def _three(client):
    return [_create(client, name).get_json()["id"] for name in ("A", "B", "C")]


def test_several_projects_are_archived_in_one_request_answered_with_the_list(tmp_path):
    client = _client(tmp_path)
    first, second, third = _three(client)
    client.patch(f"/api/projects/{first}", json={"pinned": True})
    answer = client.patch("/api/projects", json={"ids": [first, third], "archived": True})
    assert answer.status_code == 200
    # The list as GET answers it: the browser draws it and asks for no second one.
    assert answer.get_json() == client.get("/api/projects").get_json()
    rows = {row["id"]: (row["archived"], row["pinned"]) for row in answer.get_json()}
    assert rows == {first: (True, False), second: (False, False), third: (True, False)}, (
        "Toplu arşiv seçilenleri arşive almadı ya da sabitlemeyi bırakmadı"
    )
    back = client.patch("/api/projects", json={"ids": [first, third], "archived": False})
    assert not any(row["archived"] for row in back.get_json()), "Toplu arşivden çıkarma çalışmadı"


def test_several_projects_are_deleted_in_one_request_answered_with_the_list(tmp_path):
    client = _client(tmp_path)
    first, second, third = _three(client)
    answer = client.post("/api/projects/delete", json={"ids": [first, "pgone", third]})
    assert answer.status_code == 200
    assert [row["id"] for row in answer.get_json()] == [second], (
        "Toplu silme seçilenleri silmedi ya da listeyi dönmedi"
    )
    assert client.get("/api/projects").get_json() == answer.get_json()


def test_a_bulk_delete_with_a_turn_running_moves_nothing(tmp_path):
    turns = LiveTurns()
    client = _wired(tmp_path, turns)[0]
    first, second, _ = _three(client)
    turns.reserve(second, "c1")
    refused = client.post("/api/projects/delete", json={"ids": [first, second]})
    assert (refused.status_code, refused.get_json()) == (409, {"error": PROJECTS_BUSY})
    assert len(client.get("/api/projects").get_json()) == 3, "Reddedilen toplu silme bir proje sildi"


@pytest.mark.parametrize(
    "body",
    [
        None,
        {},
        {"ids": []},
        {"ids": "pabc"},
        {"ids": ["pabc", 3]},
        ["pabc"],
    ],
)
def test_a_bulk_request_needs_a_list_of_ids(tmp_path, body):
    client = _client(tmp_path)
    archive = {**body, "archived": True} if isinstance(body, dict) else body
    for asked in (
        client.patch("/api/projects", json=archive),
        client.post("/api/projects/delete", json=body),
    ):
        assert (asked.status_code, asked.get_json()) == (400, {"error": NOT_IDS})


@pytest.mark.parametrize("archived", [None, "yes", 1])
def test_a_bulk_archive_needs_to_say_which_way(tmp_path, archived):
    client = _client(tmp_path)
    pid = _create(client).get_json()["id"]
    body = {"ids": [pid]} if archived is None else {"ids": [pid], "archived": archived}
    asked = client.patch("/api/projects", json=body)
    assert (asked.status_code, asked.get_json()) == (400, {"error": NOT_ARCHIVED})
    assert client.get("/api/projects").get_json()[0]["archived"] is False


def test_there_is_no_way_to_bring_a_project_back(tmp_path):
    # Undo is gone (karar 16): the confirmation is what protects the user, and the disk keeps the
    # directory. The rule table is what proves no such address exists. The file's own restore is
    # still here -- that one goes in Madde 19.
    client = _client(tmp_path)
    addresses = [str(rule) for rule in client.application.url_map.iter_rules()]
    assert "/api/projects/<project_id>/restore" not in addresses
    assert not [address for address in addresses if address.startswith("/api/trash")]
