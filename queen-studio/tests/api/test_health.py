import threading

from anyio import to_thread

from core.about import NAME, VERSION
from core.server import create_api
from tests.contract import checked_client


def test_health_names_the_app_the_core_and_the_version() -> None:
    response = checked_client(create_api(core_id="k3v9q2mz7a")).get("/health")

    assert response.status_code == 200
    assert response.json() == {"app": NAME, "core": "k3v9q2mz7a", "version": VERSION}


async def one_worker() -> None:
    # anyio's 40 worker threads, down to the one the test holds: as waiting requests would hold all.
    to_thread.current_default_thread_limiter().total_tokens = 1


def test_health_answers_while_every_worker_thread_is_held() -> None:
    # Waiting requests and slow Drive calls each hold a worker thread; health must need none, or
    # the agent reads a busy core as gone.
    api = create_api(core_id="k3v9q2mz7a")
    holding, release = threading.Event(), threading.Event()
    released: list[bool] = []

    @api.get("/hold", summary="Hold a worker thread")
    def hold() -> None:
        holding.set()
        # Gives up only if health could not answer first: the test fails then, not hangs.
        released.append(release.wait(5))

    with checked_client(api) as client:
        # One event loop for both requests, so they share its worker threads.
        assert client.portal is not None
        client.portal.call(one_worker)
        holder = threading.Thread(target=client.get, args=("/hold",))
        holder.start()
        assert holding.wait(5)

        answer = client.get("/health")
        release.set()
        holder.join(5)

    assert answer.json()["core"] == "k3v9q2mz7a"
    assert released == [True]


def test_the_openapi_document_carries_the_name_and_the_version() -> None:
    # The UI reads both from here, so the name stays written in one place.
    info = create_api(core_id="k3v9q2mz7a").openapi()["info"]

    assert (info["title"], info["version"]) == (NAME, VERSION)
