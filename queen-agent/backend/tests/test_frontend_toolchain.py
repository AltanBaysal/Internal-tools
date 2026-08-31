"""The frontend's build chain is pinned here, and the pin is read off package.json.

This file sits beside the backend's tests because `pytest queen-agent` collects them from here, but
what it examines is the frontend's manifest -- the same reason test_dist_is_committed.py lives here.

Why the versions are guarded at all: the three move together or not at all. vitest carries vite as
a direct dependency rather than a peer, so a tree where they disagree does not fail to install --
it quietly runs the tests on one engine and builds on another. Nothing in npm says that is wrong,
so a test does.

The major is read rather than the whole range: the decision is "vite 8", not the string it was
first written as, and a patch bump must not have to edit a test to stay true.
"""
import json
import os

PACKAGE = os.path.join(
    os.path.dirname(          # queen-agent
        os.path.dirname(      # backend
            os.path.dirname(os.path.abspath(__file__)))),  # tests
    "frontend",
    "package.json",
)


def _declared():
    with open(PACKAGE, encoding="utf-8") as handle:
        return json.load(handle)["devDependencies"]


def _major(spec):
    """The major version a range allows: "^8.0.0" -> 8."""
    return int(spec.lstrip("^~>=< ").split(".")[0])


def test_the_frontend_builds_with_vite_eight():
    # GHSA-67mh-4wv8-2f99: vite 5 carries esbuild <=0.24.2, whose dev server answers any origin and
    # hands back source. Closed from vite 6.2 on; 8 was chosen because it costs no source change.
    assert _major(_declared()["vite"]) == 8, "vite 8 bekleniyordu -- güvenlik açığı vite 5'te"


def test_the_react_plugin_matches_that_vite():
    # @vitejs/plugin-react 6 declares vite ^8.0.0 and nothing else, so this is not a free choice.
    assert _major(_declared()["@vitejs/plugin-react"]) == 6, (
        "plugin-react 6 bekleniyordu -- 6 yalnız vite ^8 kabul ediyor"
    )


def test_the_test_runner_rides_the_same_vite():
    # vitest 3 depends on vite ^5 || ^6 || ^7 directly. Left at 3, it would install its own vite 7
    # beside the project's 8, and the suite would measure a build nobody ships.
    assert _major(_declared()["vitest"]) == 4, (
        "vitest 4 bekleniyordu -- vitest 3 kendi vite 7'sini kurar ve testler başka motorda koşar"
    )
