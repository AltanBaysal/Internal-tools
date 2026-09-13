"""Which version queen-editor is on -- answered by the roadmap filenames themselves.

Asked on 2026-09-11, the question had two answers: the branches said v4, the roadmap filenames said
v14. A version is a branch and a branch gets one roadmap, but for eight runs a new roadmap was
opened instead of items being added to the one already running. Four branches, thirteen roadmaps,
and two different files both calling themselves v5.

There is no separate record file: the name is the record (user's decision, 11 September). That only
holds while no name can lie, which is what the assertions below are for.

Text is what can answer here, and the failure guarded is a name drifting from the branch it names
while every other test stays green.
"""
import glob
import os
import re

TOOL = os.path.dirname(          # queen-editor
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
REPO = os.path.dirname(TOOL)

ROADMAPS = os.path.join(REPO, "docs", "superpowers", "roadmaps")
PLANS = os.path.join(REPO, "docs", "superpowers", "plans")
DOCS = os.path.join(REPO, "docs")
CLAUDE = os.path.join(REPO, "CLAUDE.md")

# A run branch, as every roadmap spells it in its own header.
BRANCH = re.compile(r"feat/queen-editor-v(\d+)")
# The version a roadmap's filename claims.
NAMED = re.compile(r"queen-editor-v(\d+)-roadmap\.md")

# What CLAUDE.md used to call the current version. It sent this session to v14: the highest numbered
# document is not the current version, it is only the newest thing written.
WRONG_RULE = "highest `vN` current"

# The shape every roadmap filename takes: a date, the tool it belongs to, and that tool's version.
SHAPE = re.compile(r"^\d{4}-\d{2}-\d{2}-([a-z][a-z-]*)-v\d+-roadmap\.md$")
# A product whose code never landed in main -- no folder to check it against, and the roadmap stays
# as the record of what was built. Written down rather than inferred, so nobody renames it on a hunch.
RETIRED = {"mira"}


def _read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _roadmaps():
    """Every queen-editor roadmap, by filename."""
    found = glob.glob(os.path.join(ROADMAPS, "*queen-editor-v*-roadmap.md"))
    return sorted(os.path.basename(path) for path in found)


def _branch_in_header(text):
    """The run branch a roadmap declares, or None.

    The label is not read -- older documents say **Branch:** where newer ones say **Koşu dalı:**, and
    the question is which branch, not which word introduces it. The header is the first few lines: a
    branch named further down belongs to some item's story, not to the run.
    """
    head = "\n".join(text.splitlines()[:8])
    found = BRANCH.search(head)
    return found.group(1) if found else None


def _markdown():
    """Every markdown file that could point at a roadmap.

    Both tools' own docs, not just this one's: a roadmap renamed here can be linked from over there,
    and a link nobody resolves is how the drift started.
    """
    under_docs = glob.glob(os.path.join(DOCS, "**", "*.md"), recursive=True)
    beside_tools = glob.glob(os.path.join(REPO, "*", "*.md"))
    return under_docs + beside_tools + [CLAUDE]


def test_one_version_has_one_roadmap():
    """Two files calling themselves v5 is the state this item exists to end."""
    claimed = {}
    for name in _roadmaps():
        version = NAMED.search(name).group(1)
        claimed.setdefault(version, []).append(name)

    doubled = {version: names for version, names in claimed.items() if len(names) > 1}

    assert not doubled, f"Aynı sürümü adlayan birden çok yol haritası: {doubled}"


def test_the_name_says_the_branch_the_roadmap_ran_on():
    """A name is only a record while it cannot lie, and the branch is what it must not lie about.

    v0 is the one exemption and it is not a gap: that run closed before feat/queen-editor-v1 was cut,
    so there is no branch to name. The number says exactly that -- before the first branch -- and the
    document says it too. Any other roadmap with a silent header is the drift starting again.
    """
    parted = []
    for name in _roadmaps():
        declared = _branch_in_header(_read(os.path.join(ROADMAPS, name)))
        named = NAMED.search(name).group(1)
        # v0 has no branch by definition, and its header says so by naming the branch that came
        # after it -- which is why the exemption is the whole version and not just a silent header.
        if named == "0":
            continue
        if declared != named:
            parted.append(f"{name}: adı v{named}, başlığı {'v' + declared if declared else 'hiçbir dal'}")

    assert not parted, "Ad ile dal ayrışıyor:\n" + "\n".join(parted)


def test_every_link_to_a_roadmap_resolves_from_where_it_is_written():
    """Two costs, one assertion.

    Merging thirteen documents into five deletes eight names; moving the rest into roadmaps/ keeps
    every name and changes every path. An assertion that only asked whether a NAME matched some file
    would have seen the first and slept through the second -- so the link is resolved the way a reader
    follows it: relative to the file it is written in.
    """
    dangling = {}
    for path in _markdown():
        here = os.path.dirname(path)
        for link in set(re.findall(r"\(([^()\s]*[\w\-.]*-roadmap\.md)\)", _read(path))):
            if not os.path.exists(os.path.normpath(os.path.join(here, link))):
                dangling.setdefault(os.path.relpath(path, REPO), set()).add(link)

    assert not dangling, f"Çözülemeyen yol haritası bağlantısı: {dangling}"


def test_a_roadmap_can_still_reach_everything_it_links_to():
    """The move changes what a roadmap's own links mean, not just the links pointing at it.

    A roadmap sitting in plans/ reached its task plans by bare filename; from roadmaps/ that same
    name resolves to nothing. Links outward (../specs/, ../../../queen-editor/) kept working because
    the depth did not change -- which is exactly why this direction is easy to forget.
    """
    dangling = {}
    for path in glob.glob(os.path.join(ROADMAPS, "*.md")):
        for link in set(re.findall(r"\(([^()\s#]+\.md)(?:#[^()\s]*)?\)", _read(path))):
            if not os.path.exists(os.path.normpath(os.path.join(ROADMAPS, link))):
                dangling.setdefault(os.path.basename(path), set()).add(link)

    assert not dangling, f"Yol haritasından çıkan kırık bağlantı: {dangling}"


def test_every_roadmap_name_says_a_date_a_tool_and_a_version():
    """The record is the name, so the name has a shape rather than a habit.

    Three parts, none optional: when the run opened, whose run it was, and which version. Missing any
    one of them, the name stops answering on its own -- and one with no version cannot say where it
    sits in the series.

    **A version belongs to exactly one tool's counter**, even when the run reached into the other one.
    There is no shared counter: a name like ortak-v6 would claim a series whose v1 to v5 never
    existed, while that 6 is only the sixth of queen-agent's. A run that crosses tools says so in its
    own header, where the items can be named.

    The tool is checked against the repo itself: a folder at the root, or the one written-down
    exception. That way adding a tool needs no edit here, and renaming a retired one needs a decision.
    """
    folders = {name for name in os.listdir(REPO) if os.path.isdir(os.path.join(REPO, name))}
    allowed = folders | RETIRED

    wrong = []
    for path in sorted(glob.glob(os.path.join(ROADMAPS, "*.md"))):
        name = os.path.basename(path)
        shaped = SHAPE.match(name)
        if not shaped:
            wrong.append(f"{name}: tarih-tool-vN kalıbına uymuyor")
        elif shaped.group(1) not in allowed:
            wrong.append(f"{name}: '{shaped.group(1)}' ne bir klasör ne de {sorted(RETIRED)}")

    assert not wrong, "Yol haritası adı standarda uymuyor:\n" + "\n".join(wrong)


def test_roadmaps_live_in_their_own_folder():
    """One roadmap left behind in plans/ is a second rule, and a second rule leaves the next run
    guessing where its own document goes."""
    left = sorted(os.path.basename(p) for p in glob.glob(os.path.join(PLANS, "*-roadmap*.md")))

    assert not left, f"plans/ altında kalan yol haritası: {left}"
    assert os.path.isdir(ROADMAPS), "docs/superpowers/roadmaps/ yok"


def test_claude_md_no_longer_calls_the_newest_document_the_current_version():
    """The sentence that produced the wrong answer. Fixing the names and leaving it standing drops
    the next reader in the same place."""
    # Whitespace collapsed first: the sentence wraps in the file, so the words are separated by a
    # newline there and by a space here.
    assert WRONG_RULE not in " ".join(_read(CLAUDE).split()), (
        "CLAUDE.md güncel sürümü hâlâ en yüksek numaralı belge diye tarif ediyor — "
        "en yüksek numaralı belge güncel sürüm değil, yalnız en son yazılan"
    )
