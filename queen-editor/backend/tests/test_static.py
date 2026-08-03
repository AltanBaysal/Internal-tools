import os
import re
from urllib.parse import urljoin

from backend import config
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


def _local_assets(html):
    """Asset URLs the page asks the browser to fetch from us (fonts and other hosts excluded)."""
    urls = re.findall(r'<(?:script|link)[^>]*?(?:src|href)="([^"]+)"', html)
    return [url for url in urls if not url.startswith(("http://", "https://", "//"))]


def test_a_reload_inside_a_project_loads_the_real_assets():
    """The committed build has to work at a nested path, not only at "/".

    A reload at /projects/<name> gets index.html from the SPA fallback, and the browser then
    resolves that page's asset URLs against /projects/. Relative URLs resolve to
    /projects/assets/..., which is not a file, so the fallback answers with index.html again and
    the browser receives HTML where it expected a module script -- a blank page. Only a Colab run
    would surface that, so it is asserted here against the real dist instead.
    """
    client = create_app().test_client()          # the committed frontend/dist, not a fixture
    resp = client.get("/projects/deneme")
    assert resp.status_code == 200

    assets = _local_assets(resp.get_data(as_text=True))
    assert assets, "the built page requests no local asset -- dist looks broken"
    for url in assets:
        resolved = urljoin("/projects/deneme", url).lstrip("/")
        assert os.path.isfile(os.path.join(config.DIST_DIR, resolved)), (
            f"{url} resolves to /{resolved}, which is not in dist: reloading inside a project "
            f"would hand the browser HTML instead of the asset"
        )
