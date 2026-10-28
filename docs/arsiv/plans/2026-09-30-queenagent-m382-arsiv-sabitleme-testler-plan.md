# Madde 382 — Arşive giden projenin sabitlemesi kalkar · test turu planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 382'nin davranışını tutan testleri yazmak — yalnız testleri — ve süiti kırmızı commit etmek.

**Architecture:** Sunucunun kuralları `test_pin_archive.py`'de: mağaza (arşivdeki proje sabitli
okunmaz, dosya durur), kullanım durumu sahte portla (`Unarchive` sabitlemeyi bırakır, `Undo` bırakmaz),
`list_projects` sahte portla (arşivdeki proje sabitlilerin arasındaki yerinde), API gerçek diskle.
Ekranın payı `AllProjectsScreen.test.jsx`'te (`Undo` satırının bölümü ve `onRestoreProject`), gidiş
dönüş `App.test.jsx`'te, sunucunun yeni kurallarını tutan sahte sunucuyla.

**Tech Stack:** pytest; vitest + jsdom + Testing Library (React 18).

**Spec:** [2026-09-30-queenagent-m382-arsiv-sabitleme-testler-design.md](../specs/2026-09-30-queenagent-m382-arsiv-sabitleme-testler-design.md)

## Global Constraints

- Test adları ve yorumları İngilizce, yorum NEDEN'i söyler; pytest iddialarının mesajları Türkçe (dosyanın geri kalanı gibi).
- `skip`, `.todo`, `xfail` yok.
- Süit yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşulur.
- `AllProjectsScreen`'in yeni prop'u: `onRestoreProject(id, pinned)` — bir promise döndürebilir.
- `Undo`'nun gövdesi `{ archived: false, pinned: <bool> }`; `Unarchive`'ınki `{ archived: false }`.

---

### Task 1: Sunucu — `test_pin_archive.py`

**Files:** Modify `queen-agent/backend/tests/test_pin_archive.py`

- [ ] **Step 1:** `list_projects`'i içe al. `test_the_archive_leaves_the_pin_alone`'un yerine S1:

```python
def test_an_archived_project_is_not_pinned_and_its_pin_stays_on_disk(tmp_path):
    # Madde 382: the archive lets the pin go, as the design does. The file stays: its mtime is the
    # project's place among the pins, and Undo gives that place back.
    store = _born(tmp_path)
    store.set_pinned("pabc", True)
    pinned = os.path.join(str(tmp_path), "pabc", "pinned")
    os.utime(pinned, (1_000_000_000, 1_000_000_000))
    store.set_archived("pabc", True)
    assert not _reopened(tmp_path).pinned, "Arşivdeki proje hâlâ sabitli okunuyor"
    assert os.path.getmtime(pinned) == 1_000_000_000, "Arşiv sabitlemenin yerini diskten sildi"
```

- [ ] **Step 2:** `FakeProjectStore.__init__(self, **fields)` → `Project(id="pabc", name="Thesis",
  created_at=..., **fields)`. E1–E3:

```python
PINNED_AT = "2026-08-10T10:00:00.000+00:00"

def test_unarchiving_lets_the_pin_go():
    # Madde 382: Unarchive brings the project back into Recent, never into Pinned.
    store = FakeProjectStore(pinned_at=PINNED_AT, archived=True)
    edit_project(store, "pabc", archived=False)
    assert ("pinned", "pabc", False) in store.marked, "Unarchive sabitlemeyi bırakmadı"

def test_undo_asks_for_the_pin_and_keeps_it():
    # Undo sends the pin with the unarchive, and the pin file -- the project's place -- stays.
    store = FakeProjectStore(pinned_at=PINNED_AT, archived=True)
    edit_project(store, "pabc", archived=False, pinned=True)
    assert ("pinned", "pabc", False) not in store.marked, "Undo sabitlemeyi bıraktı"

def test_bringing_back_what_is_not_archived_leaves_the_pin():
    # Asking for what already stands changes nothing (Madde 339).
    store = FakeProjectStore(pinned_at=PINNED_AT)
    edit_project(store, "pabc", archived=False)
    assert ("pinned", "pabc", False) not in store.marked, (
        "Arşivde olmayan projeye gelen archived=False sabitlemeyi bıraktı"
    )
```

- [ ] **Step 3:** L1, sahte portla:

```python
class FakeListStore:
    def __init__(self, projects):
        self.projects = projects

    def list_all(self):
        return list(self.projects)

def test_an_archived_project_keeps_its_place_among_the_pins():
    # Where the Undo line stands (the design's projectsWithUndo): the screen draws no order.
    store = FakeListStore([
        Project(id="a", name="a", created_at=_day(1), pinned_at=_day(10)),
        Project(id="b", name="b", created_at=_day(2), pinned_at=_day(5), archived=True),
        Project(id="c", name="c", created_at=_day(3)),
    ])
    projects = list_projects(store)
    assert [project.id for project in projects] == ["b", "a", "c"], (
        "Arşivdeki proje sabitlilerin arasındaki yerinde değil"
    )
    assert not projects[0].pinned, "Arşivdeki proje listede sabitli"
```

`_day(n)` → `f"2026-08-{n:02d}T10:00:00.000+00:00"`.

- [ ] **Step 4:** A1 ve A2 (API):

```python
def test_archive_lets_the_pin_go_and_unarchive_does_not_bring_it_back(tmp_path):
    client = _client(tmp_path)
    pid = client.post("/api/projects", json={"name": "Thesis"}).get_json()["id"]
    client.patch(f"/api/projects/{pid}", json={"pinned": True})
    archived = client.patch(f"/api/projects/{pid}", json={"archived": True}).get_json()
    assert (archived["pinned"], archived["archived"]) == (False, True), "Arşive alınan proje sabitli kaldı"
    listed = _client(tmp_path).get("/api/projects").get_json()[0]
    assert listed["pinned"] is False, "Yeniden açılınca arşivdeki proje sabitli"
    back = client.patch(f"/api/projects/{pid}", json={"archived": False}).get_json()
    assert back["pinned"] is False, "Unarchive projeyi sabitlemesiyle geri getirdi"
    listed = _client(tmp_path).get("/api/projects").get_json()[0]
    assert (listed["pinned"], listed["archived"]) == (False, False), "..."
    assert not Store(str(tmp_path)).exists(f"{pid}/pinned"), "Unarchive'dan sonra pinned dosyası duruyor"

def test_undo_puts_a_pinned_project_back_in_its_place_among_the_pins(tmp_path):
    projects = FileProjectStore(Store(str(tmp_path)))
    for day, pid in enumerate(("pa", "pb", "pc"), start=1):
        projects.add(Project(id=pid, name=pid, created_at=f"2000-01-{day:02d}T00:00:00.000+00:00"))
    projects.set_pinned("pa", True)
    projects.set_pinned("pb", True)
    # Pinned a hundred seconds apart, pa first, so the order is the pins' and never chance's.
    pin_of_pa = os.path.join(str(tmp_path), "pa", "pinned")
    os.utime(pin_of_pa, (1_000_000_000, 1_000_000_000))
    os.utime(os.path.join(str(tmp_path), "pb", "pinned"), (1_000_000_100, 1_000_000_100))
    client = _client(tmp_path)
    client.patch("/api/projects/pa", json={"archived": True})
    rows = client.get("/api/projects").get_json()
    assert [row["id"] for row in rows] == ["pa", "pb", "pc"], "..."
    assert rows[0]["pinned"] is False, "Arşivdeki proje listede sabitli"
    back = client.patch("/api/projects/pa", json={"archived": False, "pinned": True}).get_json()
    assert (back["pinned"], back["archived"]) == (True, False), "Undo projeyi sabitli geri getirmedi"
    assert [row["id"] for row in client.get("/api/projects").get_json()] == ["pa", "pb", "pc"], (
        "Undo projeyi sabitlilerin arasındaki eski yerine koymadı"
    )
    assert os.path.getmtime(pin_of_pa) == 1_000_000_000, "Undo sabitlendiği anı kaydırdı"
```

### Task 2: Ön uç — `AllProjectsScreen.test.jsx`

**Files:** Modify `queen-agent/frontend/src/features/workspace/AllProjectsScreen.test.jsx`

- [ ] **Step 1:** U3'ün yerine: `a pinned project's Undo stands under Pinned, in its place among the
  pins` — `SECOND = { id: "p6", name: "Second pin", chats: 0, files: 0, pinned: true, lastActivity:
  ago(40) }`; `archiving([PINNED, SECOND, RECENT], "p1")`; `answer([{ ...PINNED, pinned: false,
  archived: true }, SECOND, RECENT])`; ilk bölüm `Pinned`, satırları `["Harbour at dusk archived ·
  Undo", <Second pin'i taşıyan>]`, iki satır.
- [ ] **Step 2:** U4: `onRestoreProject = vi.fn(() => new Promise((resolve) => (settle = resolve)))`,
  `Undo` → `onRestoreProject("p2", false)`; gerisi aynı.
- [ ] **Step 3:** U8 `a pinned project's Undo asks for its pin back` — `archiving([PINNED, RECENT],
  "p1", { onRestoreProject: vi.fn() })`, `answer([{ ...PINNED, pinned: false, archived: true },
  RECENT])`, `Undo` → `onRestoreProject("p1", true)`; `onArchiveProject.mock.calls` `[["p1", true]]`.

### Task 3: Ön uç — `App.test.jsx`

**Files:** Modify `queen-agent/frontend/src/App.test.jsx`

- [ ] **Step 1:** `serverForRows`: sabitleme `pin` alanında tutulur (başta `pinned` olanlara sırayla
  `++pins`); satır `pinned: pin !== null && !archived` der; sıra `pin`'i olanlar `pin`'e göre, sonra
  `pin`'i olmayanlar son kullanıma göre; PATCH: `pinned: false` → `pin = null`; `pinned: true` ve
  `pin === null` → `pin = ++pins`; arşivdeki projeye `archived: false` ve `pinned !== true` → `pin =
  null`. Başındaki yorum ve 363 bölümünün yorumu buna göre.
- [ ] **Step 2:** B2: ikinci PATCH `{ archived: false, pinned: false }`.
- [ ] **Step 3:** B3 `Undo puts a pinned project back in its place among the pins` —
  `HARBOUR = { id: "p4", name: "Harbour", chats: 0, files: 0, pinned: true, lastActivity:
  hoursAgo(40) }`; `serverForRows([PIER, HARBOUR, ...ROWS])`; önce `{ Pinned: ["Old pier",
  "Harbour"], Recent: ["Thesis", "Notes"] }`; `Old pier` arşivlenir → ilk bölümün satırları
  `["Old pier archived · Undo", <Harbour'u taşıyan>]`; `Undo` → yine `Pinned: ["Old pier",
  "Harbour"]`; PATCH'ler `[p3 {archived: true}], [p3 {archived: false, pinned: true}]`.
- [ ] **Step 4:** B7 `a pinned project archived and then unarchived comes back under Recent` —
  `serverForRows([PIER, ...ROWS])`; `Archive`, `Archived` sekmesi, `Old pier`'in `Unarchive`'ı;
  `No archived projects.`; `Projects`'te `{ Recent: ["Thesis", "Notes", "Old pier"] }`; PATCH'ler
  `[p3 {archived: true}], [p3 {archived: false}]`.

### Task 4: Koş ve commit

- [ ] **Step 1:** Dört satır paralel. Beklenen: queen-agent backend'de S1, E1, L1, A1, A2 kırmızı;
  frontend'de U3, U4, U8, B2, B3 kırmızı; queen-editor'ün iki süiti yeşil.
- [ ] **Step 2:** Spec, plan ve testler tek commit:
  `test(queen-agent): Madde 382 red -- an archive lets the pin go, Unarchive brings it back into Recent, Undo into its place among the pins`
