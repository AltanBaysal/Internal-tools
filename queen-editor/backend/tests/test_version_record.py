"""Which version queen-editor is on -- answered by the roadmap filenames themselves.

Asked on 2026-09-11, the question had two answers: the branches said v4, the roadmap filenames said
v14. A version is a branch and a branch gets one roadmap, but for eight runs a new roadmap was
opened instead of items being added to the one already running. Four branches, thirteen roadmaps,
and two different files both calling themselves v5.

There is no separate record file: the name is the record (user's decision, 11 September). That only
holds while no name can lie, which is what the assertions below are for.

Text is what can answer here, and the failure guarded is a name drifting from the branch it names
while every other test stays green.

Both tools are read, not just this one. The first pass asked only about queen-editor and that is
exactly where the second drift hid: QueenAgent's v2 and v3 both sat on fix/mira, and its v8 named no
branch at all, while every assertion here stayed green. The counters are separate; the rules over
them are not.
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

# The header field naming the run's branch. Three spellings are in use and all three count -- the
# question is which branch, not which word introduces it.
LABEL = re.compile(r"\*\*(?:Branch|Dal|Koşu dalı):\*\*")
# A branch as the headers write them: always in backticks, always under feat/ or fix/.
BRANCH = re.compile(r"`((?:feat|fix)/[^`\s]+)`")
# A branch name that ends in a version number -- feat/queen-editor-v5, feat/v6, feat/mira-v1. Not
# every branch has one: the older ones were named before the habit settled.
NUMBERED = re.compile(r"v(\d+)$")

# A markdown link to a roadmap, text and target together. The link assertions above catch only the
# target, which is how 120 texts kept naming versions that no longer exist.
LINK = re.compile(r"\[([^\]]+)\]\(([^()\s]*-roadmap\.md)\)")
# A version named inside link text.
IN_TEXT = re.compile(r"\bv(\d+)\b")
# The one place naming an old version is right: a sentence explaining the rename says "... adıyla",
# meaning "under the name of". Kept this narrow on purpose -- a wide exemption empties the assertion.
FORMER = "adıyla"

# What CLAUDE.md used to call the current version. It sent this session to v14: the highest numbered
# document is not the current version, it is only the newest thing written.
WRONG_RULE = "highest `vN` current"

# The shape every roadmap filename takes: a date, the tool it belongs to, and that tool's version.
SHAPE = re.compile(r"^\d{4}-\d{2}-\d{2}-([a-z][a-z-]*)-v(\d+)-roadmap\.md$")


def _read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _roadmaps():
    """Every roadmap, as (filename, tool, version).

    A name that does not match the shape is skipped instead of crashing here -- naming those is
    test_every_roadmap_name_says_a_date_a_tool_and_a_version's job, and one failure reads better than
    a stack trace in every other test.
    """
    found = []
    for path in sorted(glob.glob(os.path.join(ROADMAPS, "*-roadmap.md"))):
        name = os.path.basename(path)
        shaped = SHAPE.match(name)
        if shaped:
            found.append((name, shaped.group(1), int(shaped.group(2))))
    return found


def _declared_branch(text):
    """The branch a roadmap declares for its own run, or None.

    Read from the label rather than from line order, because either shortcut produces a false red.
    The FIRST label in the file is the document's own: a merged roadmap repeats the label inside
    every Koşu N section, and queen-agent v1 mentions `fix/mira` in a note four lines above its own
    header line.

    Only the first branch on that line is the document's. A second one there is either the branch the
    run was opened from (queen-agent v1) or a second branch the version spread onto (queen-agent v5,
    items 124-132) -- neither is a claim on that branch.
    """
    for line in text.splitlines():
        if LABEL.search(line):
            found = BRANCH.search(line)
            return found.group(1) if found else None
    return None


def _markdown():
    """Every markdown file that could point at a roadmap.

    Both tools' own docs, not just this one's: a roadmap renamed here can be linked from over there,
    and a link nobody resolves is how the drift started.
    """
    under_docs = glob.glob(os.path.join(DOCS, "**", "*.md"), recursive=True)
    beside_tools = glob.glob(os.path.join(REPO, "*", "*.md"))
    return under_docs + beside_tools + [CLAUDE]


def test_one_version_has_one_roadmap():
    """Two files calling themselves v5 is the state this item exists to end.

    Per tool, because the counters are separate: queen-editor v5 and queen-agent v5 are two different
    versions and always were.
    """
    claimed = {}
    for name, tool, version in _roadmaps():
        claimed.setdefault((tool, version), []).append(name)

    doubled = {key: names for key, names in claimed.items() if len(names) > 1}

    assert not doubled, f"Aynı sürümü adlayan birden çok yol haritası: {doubled}"


def test_every_roadmap_says_which_branch_it_ran_on():
    """A name cannot answer at all without a branch behind it.

    The branch is what makes a version something that happened rather than a number someone wrote. A
    document naming none leaves its own number unbacked, and nothing else in the repo can say whether
    that version ran, or where.
    """
    silent = [name for name, _, _ in _roadmaps()
              if _declared_branch(_read(os.path.join(ROADMAPS, name))) is None]

    assert not silent, "Başlığında dal adı olmayan yol haritası: " + ", ".join(silent)


def test_no_branch_is_claimed_by_two_roadmaps():
    """One branch, one roadmap -- the rule this whole item exists to restore.

    Two documents on one branch is exactly how a counter starts counting documents instead of
    versions, and it happened on both sides: nine queen-editor roadmaps on feat/queen-editor-v3, and
    QueenAgent's v2 and v3 on fix/mira.
    """
    owners = {}
    for name, _, _ in _roadmaps():
        branch = _declared_branch(_read(os.path.join(ROADMAPS, name)))
        if branch:
            owners.setdefault(branch, []).append(name)

    doubled = {branch: names for branch, names in owners.items() if len(names) > 1}

    assert not doubled, f"Aynı dalı sahiplenen birden çok yol haritası: {doubled}"


def test_a_numbered_branch_agrees_with_the_name():
    """Where the branch carries a number, the filename carries the same one.

    Not every branch does. fix/mira and feat/queenagent-colab were cut before the habit settled, and
    a branch name cannot be corrected afterwards -- so what makes them a record is not what they are
    called but that exactly one document claims each, which the assertion above is for.
    """
    parted = []
    for name, _, version in _roadmaps():
        branch = _declared_branch(_read(os.path.join(ROADMAPS, name)))
        if not branch:
            continue
        numbered = NUMBERED.search(branch)
        if numbered and int(numbered.group(1)) != version:
            parted.append(f"{name}: adı v{version}, dalı `{branch}`")

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


def test_a_links_text_names_the_version_it_goes_to():
    """A link has two halves and the rename only fixed one of them.

    Thirteen documents became five, every path was repointed, and 120 link texts went on naming v5,
    v7, v14 -- versions with no document behind them. The link resolves, so the assertion above stayed
    green while the sentence around it told the reader about something that does not exist. If the name
    is the record, then every place writing that name is the record too.

    Exempt: text that says "adıyla" (under the name of), which is a sentence deliberately naming a
    former version -- the roadmaps explaining the rename have to say the old number.
    """
    lying = []
    for path in _markdown():
        for text, target in LINK.findall(_read(path)):
            shaped = SHAPE.match(os.path.basename(target))
            if not shaped or FORMER in text:
                continue
            version = int(shaped.group(2))
            for named in IN_TEXT.findall(text):
                if int(named) != version:
                    lying.append(f"{os.path.relpath(path, REPO)}: [{text}] → v{version}")
                    break

    assert not lying, "Bağlantı metni gittiği belgeden başka bir sürümü adlıyor:\n" + "\n".join(lying)


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

    The tool is a folder at the root of the repo, with no exceptions -- and one was tried. A run
    carried out under a product's earlier name belongs to the tool that name became, not to a name
    the repo no longer has: keeping it would leave a counter nobody can find the code for.
    """
    folders = {name for name in os.listdir(REPO) if os.path.isdir(os.path.join(REPO, name))}
    allowed = folders

    wrong = []
    for path in sorted(glob.glob(os.path.join(ROADMAPS, "*.md"))):
        name = os.path.basename(path)
        shaped = SHAPE.match(name)
        if not shaped:
            wrong.append(f"{name}: tarih-tool-vN kalıbına uymuyor")
        elif shaped.group(1) not in allowed:
            wrong.append(f"{name}: '{shaped.group(1)}' diye bir tool klasörü yok")
        elif int(shaped.group(2)) < 1:
            # Every counter starts at v1, both tools alike. A version is a branch, so a run with no
            # branch of its own is not a version -- it is the first run inside the version whose
            # branch came next, and it says there that it had none. v0 was tried and folded in.
            wrong.append(f"{name}: sürüm v1'den başlar, v0 diye bir sürüm yok")

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
