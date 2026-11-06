from core.about import NAME, VERSION
from core.server import create_api
from tests.contract import checked_client


def test_health_names_the_app_the_core_and_the_version() -> None:
    response = checked_client(create_api(core_id="k3v9q2mz7a")).get("/health")

    assert response.status_code == 200
    assert response.json() == {"app": NAME, "core": "k3v9q2mz7a", "version": VERSION}


def test_the_openapi_document_carries_the_name_and_the_version() -> None:
    # The UI reads both from here, so the name stays written in one place.
    info = create_api(core_id="k3v9q2mz7a").openapi()["info"]

    assert (info["title"], info["version"]) == (NAME, VERSION)
