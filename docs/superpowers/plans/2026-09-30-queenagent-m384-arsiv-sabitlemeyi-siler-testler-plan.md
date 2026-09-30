# Madde 384 — test turu planı

> **Ajan için:** adımlar sırayla, bu oturumda (CLAUDE.md alt ajan istemiyor). Adımlar `- [ ]` ile.

**Amaç:** 384'ün davranışını — arşiv sabitlemeyi sunucuda siler, arşivdekiler yalnız son kullanıma
göre dizilir, `Undo` yalnız arşivi geri alır — kırmızı testlerle yazmak. Kod yok.

**Mimari:** Sunucu testleri `test_pin_archive.py`'de (mağaza, sahte portla kullanım durumları, API);
tarayıcının testleri `AllProjectsScreen.test.jsx`'te (ekran tek başına) ve `App.test.jsx`'te
(`serverForRows`'un sahte sunucusuyla uçtan uca).

**Teknoloji:** pytest, vitest + Testing Library.

**Spec:** [2026-09-30-queenagent-m384-arsiv-sabitlemeyi-siler-testler-design.md](../specs/2026-09-30-queenagent-m384-arsiv-sabitlemeyi-siler-testler-design.md)

## Genel kısıtlar

- Test adları, yorumlar İngilizce; iddia mesajları Türkçe (dosyanın bugünkü biçimi).
- `skip`, `xfail`, `.skip`, `.todo` yok.
- Dört test satırı CLAUDE.md'deki gibi, paralel, borusuz, daraltmadan.
- Commit mesajında çift tırnak yok, `--amend` yok.

---

### Görev 1: Sunucunun testleri

**Dosya:** `queen-agent/backend/tests/test_pin_archive.py`

- [ ] **Adım 1: S1 — 382'nin mağaza testinin yerine**

`test_an_archived_project_is_not_pinned_and_its_pin_stays_on_disk` kalkar, yerine:

```python
def test_a_pin_left_beside_an_archived_project_does_not_read_as_pinned(tmp_path):
    # Madde 384: an archive takes the pin with it, but one made under the rule before (363, 382)
    # left the file on disk. An archived project never reads as pinned all the same.
    store = _born(tmp_path)
    store.set_pinned("pabc", True)
    store.set_archived("pabc", True)
    assert not _reopened(tmp_path).pinned, "Arşivdeki proje sabitli okunuyor"
```

- [ ] **Adım 2: E1, E2 — kullanım durumu**

`test_undo_asks_for_the_pin_and_keeps_it` kalkar. `test_unarchiving_lets_the_pin_go`'nun yorumu
değişir, ve önüne E1 gelir:

```python
def test_archiving_lets_the_pin_go():
    # Madde 384: the archive takes the pin with it, on the server -- the browser sends none.
    store = FakeProjectStore(pinned_at=_day(10))
    edit_project(store, "pabc", archived=True)
    assert ("pinned", "pabc", False) in store.marked, "Arşiv sabitlemeyi silmedi"


def test_unarchiving_lets_the_pin_go():
    # Unarchive brings the project back into Recent, never into Pinned -- also one whose pin an
    # archive made before Madde 384 left on disk.
    store = FakeProjectStore(pinned_at=_day(10), archived=True)
    edit_project(store, "pabc", archived=False)
    assert ("pinned", "pabc", False) in store.marked, "Unarchive sabitlemeyi bırakmadı"
```

`test_bringing_back_what_is_not_archived_leaves_the_pin` (E3) olduğu gibi kalır.

- [ ] **Adım 3: L1 — liste**

`test_an_archived_project_keeps_its_place_among_the_pins` kalkar, yerine:

```python
def test_the_archived_are_listed_by_last_use_alone():
    # Madde 384: nothing archived stands among the pins -- not even one whose pin an older archive
    # left on disk -- so the Archived tab, which keeps the server's order, is by last use alone.
    store = FakeListStore(
        [
            Project(id="a", name="a", created_at=_day(1), pinned_at=_day(10)),
            Project(id="b", name="b", created_at=_day(2), pinned_at=_day(5), archived=True),
            Project(id="c", name="c", created_at=_day(3)),
            Project(id="d", name="d", created_at=_day(4), archived=True),
        ]
    )
    projects = list_projects(store)
    assert [project.id for project in projects] == ["a", "d", "c", "b"], (
        "Arşivdeki projeler yalnız son kullanıma göre sıralı değil"
    )
    assert not any(project.pinned for project in projects if project.archived), (
        "Arşivdeki bir proje listede sabitli"
    )
```

- [ ] **Adım 4: A1, A2, A3 — API**

`test_archive_lets_the_pin_go_and_unarchive_does_not_bring_it_back` ve
`test_undo_puts_a_pinned_project_back_in_its_place_among_the_pins` kalkar, yerine:

```python
def test_archive_deletes_the_pin_and_unarchive_does_not_bring_it_back(tmp_path):
    # Madde 384: the archive takes the pin with it on the server, and Unarchive brings the project
    # back into Recent.
    client = _client(tmp_path)
    pid = client.post("/api/projects", json={"name": "Thesis"}).get_json()["id"]
    client.patch(f"/api/projects/{pid}", json={"pinned": True})
    archived = client.patch(f"/api/projects/{pid}", json={"archived": True}).get_json()
    assert (archived["pinned"], archived["archived"]) == (False, True), (
        "Arşive alınan proje sabitli kaldı"
    )
    assert not Store(str(tmp_path)).exists(f"{pid}/pinned"), "Arşivden sonra pinned dosyası duruyor"
    listed = _client(tmp_path).get("/api/projects").get_json()[0]
    assert listed["pinned"] is False, "Yeniden açılınca arşivdeki proje sabitli"
    back = client.patch(f"/api/projects/{pid}", json={"archived": False}).get_json()
    assert back["pinned"] is False, "Unarchive projeyi sabitlemesiyle geri getirdi"
    listed = _client(tmp_path).get("/api/projects").get_json()[0]
    assert (listed["pinned"], listed["archived"]) == (False, False), (
        "Yeniden açılınca arşivden dönen proje sabitli ya da arşivde"
    )


def test_undo_brings_a_pinned_project_back_into_recent_unpinned(tmp_path):
    # Madde 384, the owner's choice over the design's restoreProject: Undo only takes the archive
    # back. The pin went with the archive, so the project -- and its Undo line before it -- stands
    # in Recent, where its own last use puts it.
    projects = FileProjectStore(Store(str(tmp_path)))
    for day, pid in enumerate(("pa", "pb", "pc"), start=1):
        projects.add(Project(id=pid, name=pid, created_at=f"2000-01-{day:02d}T00:00:00.000+00:00"))
    projects.set_pinned("pa", True)
    projects.set_pinned("pb", True)
    client = _client(tmp_path)
    client.patch("/api/projects/pa", json={"archived": True})
    rows = client.get("/api/projects").get_json()
    assert [row["id"] for row in rows] == ["pb", "pc", "pa"], (
        "Arşivdeki proje son kullanımının yerinde değil"
    )
    assert rows[2]["pinned"] is False, "Arşivdeki proje listede sabitli"
    back = client.patch("/api/projects/pa", json={"archived": False}).get_json()
    assert (back["pinned"], back["archived"]) == (False, False), (
        "Undo projeyi sabitli ya da arşivde bıraktı"
    )
    assert [row["id"] for row in client.get("/api/projects").get_json()] == ["pb", "pc", "pa"], (
        "Undo'dan sonra proje Recent'te son kullanımının yerinde değil"
    )
    assert not Store(str(tmp_path)).exists("pa/pinned"), "Undo'dan sonra pinned dosyası duruyor"


def test_a_pin_an_older_archive_left_neither_orders_nor_survives_unarchive(tmp_path):
    # An archive made before Madde 384 left the pin file on disk. The list reads past it and
    # Unarchive clears it, so no migration is needed.
    projects = FileProjectStore(Store(str(tmp_path)))
    projects.add(Project(id="pa", name="pa", created_at="2000-01-01T00:00:00.000+00:00"))
    projects.add(Project(id="pb", name="pb", created_at="2000-01-02T00:00:00.000+00:00"))
    projects.set_pinned("pa", True)
    projects.set_archived("pa", True)
    projects.set_archived("pb", True)
    client = _client(tmp_path)
    rows = client.get("/api/projects").get_json()
    assert [(row["id"], row["pinned"]) for row in rows] == [("pb", False), ("pa", False)], (
        "Eski arşivin bıraktığı sabitleme arşivdeki projeyi öne dizdi ya da sabitli gösterdi"
    )
    back = client.patch("/api/projects/pa", json={"archived": False}).get_json()
    assert back["pinned"] is False, "Unarchive eski sabitlemeyi geri getirdi"
    assert not Store(str(tmp_path)).exists("pa/pinned"), "Unarchive eski pinned dosyasını silmedi"
```

`os` ve `list_projects` içe aktarmaları kullanılmaya devam ediyor.

### Görev 2: Ekranın testleri

**Dosya:** `queen-agent/frontend/src/features/workspace/AllProjectsScreen.test.jsx`

- [ ] **Adım 1: U3, U8, U4**

`a pinned project's Undo stands under Pinned, in its place among the pins` ve
`a pinned project's Undo asks for its pin back` kalkar; yerlerine:

```jsx
test("a pinned project's Undo stands in Recent, where its last use puts it", () => {
  // Madde 384: the server takes the pin away with the archive and lists the project by its last
  // use, so its Undo line stands in Recent; the screen draws no order of its own.
  const SECOND = { id: "p6", name: "Second pin", chats: 0, files: 0, pinned: true, lastActivity: ago(40) };
  const { container, answer } = archiving([PINNED, SECOND, RECENT], "p1");
  answer([SECOND, { ...PINNED, pinned: false, archived: true }, RECENT]);
  const [pinned, recent] = container.querySelectorAll(".all-projects__section");
  expect(names(pinned)).toEqual(["Second pin"]);
  expect(recent.querySelector(".all-projects__label").textContent).toBe("Recent");
  const rows = [...recent.querySelectorAll(".all-projects__row")].map((row) => row.textContent);
  expect(rows).toEqual(["Harbour at dusk archived · Undo", expect.stringContaining("Night market")]);
});

test("a pinned project's Undo asks only for the archive back", () => {
  // Madde 384, the owner's choice: the pin went with the archive, and Undo does not ask for it.
  const { props, answer } = archiving([PINNED, RECENT], "p1");
  answer([{ ...PINNED, pinned: false, archived: true }, RECENT]);
  fireEvent.click(screen.getByRole("button", { name: "Undo" }));
  expect(props.onArchiveProject.mock.calls).toEqual([
    ["p1", true],
    ["p1", false],
  ]);
});
```

`Undo brings it back, and its line holds until the list does`'un başı:

```jsx
  let settle;
  const onArchiveProject = vi.fn((id, archived) =>
    archived ? undefined : new Promise((resolve) => (settle = resolve)),
  );
  const { container, answer } = archiving([PINNED, RECENT, OLDER], "p2", { onArchiveProject });
  answer([PINNED, { ...RECENT, archived: true }, OLDER]);
  fireEvent.click(screen.getByRole("button", { name: "Undo" }));
  expect(onArchiveProject).toHaveBeenLastCalledWith("p2", false);
```

### Görev 3: Uygulamanın testleri

**Dosya:** `queen-agent/frontend/src/App.test.jsx`

- [ ] **Adım 1: `serverForRows` yeni kuralla**

```jsx
// A server that keeps its own order -- the pinned first, in the order they were pinned, then the
// most recently used (list_projects.py) -- so where a row stands after a pin, an unpin or an
// archive is the server's answer rather than a guess made on the screen. The archive takes the pin
// with it (Madde 384). A DELETE takes the project out of it.
function serverForRows(projects) {
  let pins = 0;
  let live = projects.map((project) => ({ ...project, pinnedAt: project.pinned ? ++pins : 0 }));
  const row = ({ pinnedAt, ...project }) => project;
  const listed = () =>
    [
      ...live.filter((project) => project.pinned).sort((a, b) => a.pinnedAt - b.pinnedAt),
      ...live
        .filter((project) => !project.pinned)
        .sort((a, b) => b.lastActivity.localeCompare(a.lastActivity)),
    ].map(row);
  const fetch = vi.fn().mockImplementation((path, options) => {
    const one = path.match(/^\/api\/projects\/(\w+)$/);
    if (one && options?.method === "DELETE") {
      live = live.filter((project) => project.id !== one[1]);
      return ok({ trashed: one[1] });
    }
    if (one && options?.method === "PATCH") {
      const changes = JSON.parse(options.body);
      live = live.map((project) => {
        if (project.id !== one[1]) return project;
        const next = { ...project, ...changes };
        // A second pin leaves the first one's moment, as the pin file's mtime does.
        if (changes.pinned && !project.pinned) next.pinnedAt = ++pins;
        if (changes.archived) next.pinned = false;
        return next;
      });
      return ok(row(live.find((project) => project.id === one[1])));
    }
    if (path === "/api/projects") return ok(listed());
    return ok([]);
  });
  vi.stubGlobal("fetch", fetch);
  return fetch;
}
```

363 bölümünün yorumu: *serverForRows keeps the mark as it keeps any other, and takes the pin away with
the archive (Madde 384).*

- [ ] **Adım 2: B2** — `Undo puts the project back where it was`'un ikinci PATCH'i
  `["/api/projects/p2", { archived: false }]`.

- [ ] **Adım 3: B3** — `Undo puts a pinned project back in its place among the pins` kalkar, yerine:

```jsx
test("a pinned project's Undo stands in Recent, and Undo brings it back unpinned", async () => {
  // Madde 384: the server takes the pin away with the archive, and Undo asks only for the archive
  // back -- the owner's choice over the design's restoreProject, which gave the pin back too.
  const HARBOUR = { id: "p4", name: "Harbour", chats: 0, files: 0, pinned: true, lastActivity: hoursAgo(40) };
  const fetch = serverForRows([PIER, HARBOUR, ...ROWS]);
  const { container } = render(<App />);
  await onAllProjects();
  expect(sections(container)).toEqual({ Pinned: ["Old pier", "Harbour"], Recent: ["Thesis", "Notes"] });
  actionsFor("Old pier");
  fireEvent.click(screen.getByRole("button", { name: "Archive" }));
  await screen.findByRole("button", { name: "Archived 1" });
  const [pinned, recent] = container.querySelectorAll(".all-projects__section");
  expect(rowsOf(pinned)).toEqual([expect.stringContaining("Harbour")]);
  expect(rowsOf(recent)).toEqual([
    expect.stringContaining("Thesis"),
    expect.stringContaining("Notes"),
    "Old pier archived · Undo",
  ]);
  fireEvent.click(screen.getByRole("button", { name: "Undo" }));
  await waitFor(() =>
    expect(sections(container)).toEqual({
      Pinned: ["Harbour"],
      Recent: ["Thesis", "Notes", "Old pier"],
    }),
  );
  expect(patches(fetch).map(([path, options]) => [path, JSON.parse(options.body)])).toEqual([
    ["/api/projects/p3", { archived: true }],
    ["/api/projects/p3", { archived: false }],
  ]);
});
```

`a pinned project archived and then unarchived comes back under Recent` (B7) kalır; yorumundaki
"Madde 382" → "Madde 384".

### Görev 4: Kırmızıyı gör ve commit'le

- [ ] **Adım 1:** Dört satır paralel (queen-agent'ın ön ucu arka planda, özeti görevin kendi çıktı
  dosyasından):
  `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend` ·
  `python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`
  Beklenen: pytest'te E1, L1, A1, A2, A3 kırmızı; vitest'te U3, U4, U8, B2, B3 kırmızı; ötekiler yeşil.
- [ ] **Adım 2:** Commit:
  `test(queen-agent): Madde 384 red -- the archive deletes the pin on the server, the archived are listed by last use, Undo only unarchives`
