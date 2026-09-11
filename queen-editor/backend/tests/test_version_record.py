"""Which version queen-editor is on, and whether anything can still disagree about it.

Asked on 2026-09-11, the question had two answers: the branches say v4, the roadmap filenames say
v14. Neither is a lie -- a version is a branch and a branch gets one roadmap, but for ten runs a new
roadmap was opened instead of items being added to the one already running. Four branches, thirteen
roadmaps.

Text is what can answer here. The record is a file, the roadmaps are files, and the failure this
guards is two files drifting apart while every other test stays green -- the app would be the right
app, described by a record that stopped being true.

Its own file rather than the notebook one next door, because it asks about neither the notebook nor
the producers, and that file's name would become a promise it does not keep.
"""
import glob
import os
import re

TOOL = os.path.dirname(          # queen-editor
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
REPO = os.path.dirname(TOOL)

RECORD = os.path.join(TOOL, "SURUMLER.md")
PLANS = os.path.join(REPO, "docs", "superpowers", "plans")
CLAUDE = os.path.join(REPO, "CLAUDE.md")

# A run branch, as the roadmaps and the record both spell it.
BRANCH = re.compile(r"feat/queen-editor-v\d+")

# What CLAUDE.md used to call the current version. It sent this session to v14: the highest numbered
# document is not the current version, it is only the newest thing written.
WRONG_RULE = "highest `vN` current"


def _read(path):
    with open(path, encoding="utf-8") as handle:
        return handle.read()


def _roadmaps():
    """Every queen-editor roadmap, newest run included, by filename.

    The filename rather than the title: the record lists documents, and a document is reached by its
    name. A title can be repeated -- and here it is, nine times over.
    """
    found = glob.glob(os.path.join(PLANS, "*queen-editor-v*-roadmap.md"))
    return sorted(os.path.basename(path) for path in found)


def _branch_in_header(text):
    """The run branch a roadmap declares, or None.

    The label is not read -- older documents say **Branch:** where newer ones say **Koşu dalı:**, and
    the question is which branch, not which word introduces it. The header is the first few lines:
    a branch named further down belongs to some item's story, not to the run.
    """
    head = "\n".join(text.splitlines()[:8])
    found = BRANCH.search(head)
    return found.group(0) if found else None


def _record_line(record, roadmap):
    """The record's line about one roadmap."""
    for line in record.splitlines():
        if roadmap in line:
            return line
    return None


def test_the_record_names_one_current_version():
    """One place answers the question, and it answers with a single branch."""
    assert os.path.exists(RECORD), f"Sürüm kaydı yok: {os.path.relpath(RECORD, REPO)}"

    current = [line for line in _read(RECORD).splitlines() if "Güncel" in line]
    assert current, "Kayıtta Güncel diye işaretlenmiş bir satır yok"

    named = BRANCH.findall("\n".join(current))
    assert len(named) == 1, f"Güncel sürüm tek bir dal adlamalı, adlananlar: {named}"


def test_every_roadmap_is_written_down_in_the_record():
    """A roadmap opened and never registered is how the confusion built up in the first place."""
    assert os.path.exists(RECORD), f"Sürüm kaydı yok: {os.path.relpath(RECORD, REPO)}"

    record = _read(RECORD)
    missing = [name for name in _roadmaps() if name not in record]

    assert not missing, f"Kayda yazılmamış yol haritası: {missing}"


def test_the_record_and_each_roadmap_name_the_same_branch():
    """Where the two disagree, the question has two answers again -- which is the whole complaint."""
    assert os.path.exists(RECORD), f"Sürüm kaydı yok: {os.path.relpath(RECORD, REPO)}"

    record = _read(RECORD)
    parted = []
    for name in _roadmaps():
        declared = _branch_in_header(_read(os.path.join(PLANS, name)))
        if declared is None:
            parted.append(f"{name}: başlığında dal adı yok")
            continue

        line = _record_line(record, name)
        listed = BRANCH.search(line) if line else None
        if listed is None or listed.group(0) != declared:
            parted.append(f"{name}: başlık {declared}, kayıt {listed.group(0) if listed else 'yok'}")

    assert not parted, "Kayıt ile belge ayrışıyor:\n" + "\n".join(parted)


def test_claude_md_no_longer_calls_the_newest_document_the_current_version():
    """The sentence that produced the wrong answer. Fixing the record and leaving it standing drops
    the next reader in the same place."""
    # Whitespace collapsed first: the sentence wraps in the file, so the words are separated by a
    # newline there and by a space here.
    assert WRONG_RULE not in " ".join(_read(CLAUDE).split()), (
        "CLAUDE.md güncel sürümü hâlâ en yüksek numaralı belge diye tarif ediyor — "
        "en yüksek numaralı belge güncel sürüm değil, yalnız en son yazılan"
    )
