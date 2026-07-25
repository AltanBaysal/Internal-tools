from backend.web.app import create_app


def test_index_served_from_dist(tmp_path):
    (tmp_path / "index.html").write_text("<!doctype html><title>QE</title>", encoding="utf-8")
    client = create_app(dist_dir=str(tmp_path)).test_client()
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"QE" in resp.data


def test_unknown_path_falls_back_to_index(tmp_path):
    (tmp_path / "index.html").write_text("<!doctype html><title>QE</title>", encoding="utf-8")
    client = create_app(dist_dir=str(tmp_path)).test_client()
    resp = client.get("/projects/anything")
    assert resp.status_code == 200
    assert b"QE" in resp.data


def test_health_still_works_with_static(tmp_path):
    (tmp_path / "index.html").write_text("x", encoding="utf-8")
    client = create_app(dist_dir=str(tmp_path)).test_client()
    assert client.get("/api/health").get_json() == {"status": "ok"}
