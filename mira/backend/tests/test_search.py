from backend.features.workspace.data.file_chat_store import FileChatStore
from backend.features.workspace.data.file_file_store import FileFileStore
from backend.features.workspace.data.file_project_store import FileProjectStore
from backend.features.workspace.domain.usecases.create_project import create_project
from backend.features.workspace.domain.usecases.edit_project import edit_project
from backend.features.workspace.domain.usecases.search import search
from backend.features.workspace.domain.usecases.start_chat import start_chat
from backend.services.store.store import Store


class CountingFiles(FileFileStore):
    """A file store that says how often it went to the disk for a file's contents."""

    reads = 0

    def read(self, project_id, name):
        CountingFiles.reads += 1
        return super().read(project_id, name)


def _stores(tmp_path):
    store = Store(str(tmp_path))
    return FileProjectStore(store), FileChatStore(store), CountingFiles(store)


def _project(projects, name, project_id, at="2026-08-09T11:00:00.000+00:00"):
    create_project(projects, new_id=project_id, now=at)
    edit_project(projects, project_id, name=name)
    return project_id


def test_an_empty_query_finds_nothing_and_reads_nothing(tmp_path):
    projects, chats, files = _stores(tmp_path)
    _project(projects, "Thesis", "p1")
    files.write("p1", "plan.md", "anything")
    CountingFiles.reads = 0
    assert search(projects, chats, files, "   ") == []
    # Nothing was typed, so nothing is opened.
    assert CountingFiles.reads == 0


def test_a_project_is_found_by_name(tmp_path):
    projects, chats, files = _stores(tmp_path)
    _project(projects, "Thesis research", "p1")
    hits = search(projects, chats, files, "thesis")
    assert [(hit.kind, hit.label) for hit in hits] == [("project", "Thesis research")]
    assert hits[0].project_id == "p1"


def test_a_chat_is_found_by_title_and_says_where_it_lives(tmp_path):
    projects, chats, files = _stores(tmp_path)
    _project(projects, "Thesis", "p1")
    start_chat(chats, projects, "p1", "Write the intro", "c1", "2026-08-09T11:04:00.000+00:00")
    hit = search(projects, chats, files, "INTRO")[0]
    assert (hit.kind, hit.label, hit.chat_id, hit.project_name) == (
        "chat",
        "Write the intro",
        "c1",
        "Thesis",
    )


def test_a_file_is_found_by_name(tmp_path):
    projects, chats, files = _stores(tmp_path)
    _project(projects, "Thesis", "p1")
    files.write("p1", "outline.md", "nothing to see")
    hit = search(projects, chats, files, "outline")[0]
    assert (hit.kind, hit.label, hit.file_name) == ("file", "outline.md", "outline.md")


def test_a_file_is_found_by_what_is_inside_it(tmp_path):
    projects, chats, files = _stores(tmp_path)
    _project(projects, "Thesis", "p1")
    files.write("p1", "outline.md", "a word about quantum things")
    hit = search(projects, chats, files, "quantum")[0]
    # The word is nowhere in the name, so this hit can only have come from the contents.
    assert (hit.kind, hit.label) == ("file", "outline.md")


def test_a_file_that_matches_both_ways_is_listed_once(tmp_path):
    projects, chats, files = _stores(tmp_path)
    _project(projects, "Thesis", "p1")
    files.write("p1", "plan.md", "the plan itself")
    assert len(search(projects, chats, files, "plan")) == 1


def test_the_groups_come_in_order(tmp_path):
    projects, chats, files = _stores(tmp_path)
    _project(projects, "Alpha", "p1")
    start_chat(chats, projects, "p1", "alpha talk", "c1", "2026-08-09T11:04:00.000+00:00")
    files.write("p1", "alpha.md", "nothing")
    files.write("p1", "other.md", "alpha inside")
    # A name is a stronger answer than a body, and a project is a bigger thing than a file.
    assert [hit.kind for hit in search(projects, chats, files, "alpha")] == [
        "project",
        "chat",
        "file",
        "file",
    ]
    assert [hit.label for hit in search(projects, chats, files, "alpha")][2:] == [
        "alpha.md",
        "other.md",
    ]


def test_eight_is_the_most_that_comes_back(tmp_path):
    projects, chats, files = _stores(tmp_path)
    _project(projects, "Thesis", "p1")
    for number in range(12):
        files.write("p1", f"note-{number}.md", "x")
    assert len(search(projects, chats, files, "note")) == 8


def test_a_row_carries_the_address_the_browser_needs(tmp_path):
    projects, chats, files = _stores(tmp_path)
    _project(projects, "Thesis", "p1")
    start_chat(chats, projects, "p1", "needle talk", "c1", "2026-08-09T11:04:00.000+00:00")
    files.write("p1", "needle.md", "x")
    by_kind = {hit.kind: hit for hit in search(projects, chats, files, "needle")}
    assert by_kind["chat"].project_id == "p1" and by_kind["chat"].chat_id == "c1"
    assert by_kind["file"].project_id == "p1" and by_kind["file"].file_name == "needle.md"


def test_the_search_reaches_across_projects(tmp_path):
    projects, chats, files = _stores(tmp_path)
    _project(projects, "Alpha", "p1")
    _project(projects, "Beta", "p2")
    files.write("p2", "hidden.md", "a needle in here")
    hit = search(projects, chats, files, "needle")[0]
    assert (hit.project_id, hit.project_name, hit.file_name) == ("p2", "Beta", "hidden.md")
