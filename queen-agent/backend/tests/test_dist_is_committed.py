"""The built frontend ships in the repo.

This file sits beside the backend's tests because `pytest queen-agent` collects them from here, but
what it examines is the repository rather than a subsystem: the notebook clones this repo and never
builds it, so a bundle that lives only on the developer's disk arrives as a blank page -- and a blank
page never says why.

Git is asked rather than the filesystem. The files are on disk the moment `npm run build` runs, so
`os.path.exists` would answer "yes" to a question nobody asked; the rule is about whether they were
committed, and only git knows that.

What these tests deliberately do not answer is whether the bundle is *current*. Whether it was built
from the source it sits next to cannot be asked cheaply or certainly -- the hash names the bundle's
own contents, not its source -- and a wrong "yes" would be worse than no answer at all.
"""
import os
import re
import subprocess

REPO = os.path.dirname(          # <repo>
    os.path.dirname(             # queen-agent
        os.path.dirname(         # backend
            os.path.dirname(os.path.abspath(__file__)))))  # tests
DIST = "queen-agent/frontend/dist"


def _tracked(path):
    """Is git carrying this path? --error-unmatch turns "no" into a non-zero exit rather than
    silence, so a mistyped path fails instead of quietly passing."""
    return subprocess.run(
        ["git", "ls-files", "--error-unmatch", path],
        cwd=REPO, capture_output=True, text=True,
    ).returncode == 0


def _listed(path):
    """Every path git carries under a directory."""
    listing = subprocess.run(
        ["git", "ls-files", path], cwd=REPO, capture_output=True, text=True,
    )
    return {line for line in listing.stdout.splitlines() if line}


def test_the_built_frontend_is_in_the_repo():
    assert _tracked(f"{DIST}/index.html"), (
        f"{DIST}/index.html commit'lenmemiş — defter derlemiyor, klonladığını servis ediyor. "
        f"queen-agent/.gitignore'daki frontend/dist/ satırına bak."
    )


def test_the_page_asks_for_files_that_were_committed_with_it():
    """The sly one. index.html names its bundle by a hash of that bundle's contents, so every build
    renames it -- committing the page and forgetting the new asset leaves something that loads and
    then asks for a file nobody pushed. The first test cannot see this: index.html is there."""
    with open(os.path.join(REPO, DIST, "index.html"), encoding="utf-8") as handle:
        page = handle.read()

    # Read off the page rather than hardcoded: the names change with every build, and a test that
    # named them would have to be edited each time -- which is how a test stops being read.
    asked = re.findall(r'(?:src|href)="/(assets/[^"]+)"', page)
    # An empty list must not count as "nothing missing": that would pass forever on a broken build.
    assert asked, "index.html hiçbir bundle istemiyor — derleme bozuk"

    tracked = _listed(f"{DIST}/assets")
    missing = [name for name in asked if f"{DIST}/{name}" not in tracked]
    assert missing == [], f"Sayfanın istediği bu dosyalar commit'lenmemiş: {missing}"
