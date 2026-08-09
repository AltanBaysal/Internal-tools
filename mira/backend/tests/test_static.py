from backend.web.app import create_app


def _dist(tmp_path):
    """A throwaway dist/ so the tests never depend on a real build."""
    (tmp_path / "index.html").write_text("<!doctype html><div id=root></div>", encoding="utf-8")
    assets = tmp_path / "assets"
    assets.mkdir()
    (assets / "app.js").write_text("console.log(1)", encoding="utf-8")
    return create_app(dist_dir=str(tmp_path)).test_client()


def test_root_serves_index(tmp_path):
    resp = _dist(tmp_path).get("/")
    assert resp.status_code == 200
    assert b"id=root" in resp.data


def test_existing_asset_is_served_as_is(tmp_path):
    resp = _dist(tmp_path).get("/assets/app.js")
    assert resp.status_code == 200
    assert b"console.log(1)" in resp.data


def test_unknown_path_falls_back_to_index(tmp_path):
    resp = _dist(tmp_path).get("/projects/anything")
    assert resp.status_code == 200
    assert b"id=root" in resp.data


def test_api_route_is_not_swallowed_by_the_spa_fallback(tmp_path):
    resp = _dist(tmp_path).get("/api/health")
    assert resp.get_json() == {"status": "ok"}
