from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from core.about import NAME
from core.server import create_api, serve


@pytest.fixture
def client(tmp_path: Path) -> TestClient:
    ui = tmp_path / "dist"
    (ui / "assets").mkdir(parents=True)
    (ui / "index.html").write_text("<p>the page</p>", encoding="utf-8")
    (ui / "assets" / "app.js").write_text("run()", encoding="utf-8")
    # Beside the UI's folder, as core.json is beside nothing it serves: it must not be reachable.
    (tmp_path / "secret.txt").write_text("outside", encoding="utf-8")
    return TestClient(serve(create_api(core_id="k3v9q2mz7a"), ui))


def test_the_root_is_the_ui(client: TestClient) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert response.text == "<p>the page</p>"


def test_the_ui_files_are_served_by_name(client: TestClient) -> None:
    assert client.get("/assets/app.js").text == "run()"


def test_api_addresses_are_the_cores(client: TestClient) -> None:
    assert client.get("/api/health").json()["app"] == NAME
    assert client.get("/api/openapi.json").json()["paths"].keys() == {"/health"}


def test_an_unknown_api_address_never_falls_to_the_ui(client: TestClient) -> None:
    response = client.get("/api/nothing-here")

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"


def test_fastapis_doc_pages_are_off_and_their_address_is_the_uis(client: TestClient) -> None:
    assert client.get("/api/docs").status_code == 404
    assert client.get("/docs").status_code == 404


@pytest.mark.parametrize("path", ["/api", "/api?path=/health"])
def test_the_bare_api_address_is_the_apis_root(client: TestClient, path: str) -> None:
    # v1-5 puts the index there (`GET /api`, `GET /api?path=`); until then it is the API's 404.
    response = client.get(path)

    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"


# Encoded, so the test client does not resolve the `..` itself and the server sees it as sent.
@pytest.mark.parametrize(
    "path", ["/%2e%2e/secret.txt", "/..%2fsecret.txt", "/assets/..%2f..%2fsecret.txt"]
)
def test_no_address_reaches_outside_the_ui(client: TestClient, path: str) -> None:
    response = client.get(path)

    assert response.status_code == 404
    assert "outside" not in response.text
