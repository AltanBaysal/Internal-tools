# v14 Görev 23 — Proje adı değiştirme: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Proje adı değiştirmeyi yirmi testle yazmak — klasörün taşınması, koşan işin adı takip
etmesi, yolun cevapları ve ekrandaki kalem. Hepsi kırmızı commit ediliyor.

**Architecture:** Motorda beş dosya, ön yüzde üç. Üretim kodu bu döngüde değişmiyor.

**Tech Stack:** pytest; vitest, @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-23-proje-adi-testler-design.md)

## Global Constraints

- **Üretim kodu bu döngüde değişmiyor — iki boş kabuk dışında.** Bu maddede iki yeni **modül**
  doğuyor (`rename_project.py`, `running_name.py`). Var olmayan bir modülü içeri alan test dosyası
  *toplanamıyor*: pytest onu çalıştırmıyor bile, ve içindeki on beş eski test sayılmaz oluyor.
  Toplanamayan bir dosya kırmızı test değil, bozuk takım. Bu yüzden iki modül bu turda **yalnız
  belgesi ve `NotImplementedError` atan gövdesiyle** yazılıyor. İki turun kuralı davranışla ilgili
  — kabukta davranış yok, dolayısıyla test ondan bir körlük miras alamaz.
- **Pencere bu turda adını değiştirmiyor.** `NewProjectModal` → `NameModal` uygulama turunun işi;
  bir test dosyası da onunla birlikte adını değiştiriyor. Bu turda pencerenin iki iddiası
  (`açılış değeri seçili gelir`, `başlık ve ölçü çağıranın`) ekranın kendi testlerinden ölçülüyor —
  pencere zaten ekrandan açılıyor.
- Test adları ve yorumlar **İngilizce**; ekran metni **Türkçe**.
- `skip` / `xfail` yok — kırmızı kırmızı commit edilir.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `dist` bu commit'te **derlenmiyor**.

## File Structure

| Dosya | İşlem |
|---|---|
| `.../research/2026-08-20-queen-editor-tasarim-v4-farklari.md` | 40–42. kararlar |
| `backend/tests/test_drive_storage.py` | 2 test |
| `backend/tests/test_project_usecases.py` | 5 test |
| `backend/tests/test_photo_usecases.py` | 1 test |
| `backend/tests/test_photo_runner.py` | 1 test |
| `backend/tests/test_projects_routes.py` | 3 test |
| `frontend/.../projects/NewProjectModal.test.jsx` → `NameModal.test.jsx` | ad değişir, 2 test eklenir |
| `frontend/.../projects/ProjectsScreen.test.jsx` | 5 test |
| `frontend/src/shared/api.test.js` | 1 test |

---

### Task 1: 40–42. kararlar kaynağına

**Files:**
- Modify: `docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md`

- [ ] **Step 1: Tarih notu**

`*(21 Ağustos 2026, 13, 15, 20, 21 ve 22. madde uygulanırken.)*` →
`*(21 Ağustos 2026, 13, 15, 20, 21, 22 ve 23. madde uygulanırken.)*`

- [ ] **Step 2: Tabloya üç satır**

```markdown
| 40 | **Klasör taşınır, kopyalanmaz.** İstek listesi "adı değiştirmek klasörü değiştirmek demek" deyip cevabı spec'e bırakıyor. Kopyalamak yarıda kalabilir: bir projede binlerce dosya olabilir, Drive üzerinden kopyalama dakikalar sürer, ve kesilirse ortada iki eksik klasör kalır. Ad değiştirme dosya sisteminin kendi atomik işlemi. Sonucu: kare adları, plan, kayıt, ayarlar ve dışa aktarımlar klasörün içinde olduğu için birlikte taşınıyor ve hiçbiri yeniden yazılmıyor. | İstek 10 |
| 41 | **Koşan iş adı her turda yeniden okur, yazarken kilit tutar.** Bugün iş adı bir kez alıyor; klasör altından taşınırsa bir sonraki tur okuyamıyor ve koşu "error" ile bitiyor — yani bugünkü hâliyle ad değiştirmek üretimi öldürür. İş adı bir tutamaktan okuyor, ve yazma anı o tutamağın kilidini alıyor: `write_bytes` eksik klasörü kendisi açtığı için, eski adla çözülmüş bir yazma taşınmadan sonra düşerse yanına hayalet bir klasör bırakırdı. Render kilidin dışında, yani bekleme bir dosya yazma kadar. İşçinin durumundaki proje damgası da adı takip ediyor, yoksa ekran kendi koşusunu tanımaz. | İstek 10 |
| 42 | **Eski dışa aktarımlar taşınır, adları değişmez.** Dışa aktarım klasörü projenin içinde, dolayısıyla klasörle gidiyor. Ama birleştirilmiş dosyanın adı `{proje}.mp4` ve yeniden yazılmıyor: o dosya o adla yapıldı ve kullanıcı onu indirmiş olabilir. Bundan sonrakiler yeni adı alıyor. | İstek 10 |
```

---

### Task 2: Depolama katmanı

**Files:**
- Modify: `queen-editor/backend/tests/test_drive_storage.py`

**Interfaces:**
- Consumes: `DriveStorage.rename_dir(old, new)` — **uygulama turunda doğar**. Başarıda yeni
  klasörün mtime'ı, hedef doluysa `None`, kaynak yoksa `False`.

- [ ] **Step 1: Dosyanın sonuna iki test**

```python
def test_renaming_a_folder_takes_everything_in_it(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    storage.write_text("düğün", "plan.jsonl", "bir satır")

    assert storage.rename_dir("düğün", "nikah") is not False

    assert storage.read_text("nikah", "plan.jsonl") == "bir satır"
    assert not storage.dir_exists("düğün")


def test_renaming_onto_a_name_that_is_taken_moves_nothing(tmp_path):
    # Two different answers because the caller has two different sentences for them: None is a
    # clash, False is a folder that was not there. The mtime that comes back on success is the same
    # answer make_dir gives.
    storage = DriveStorage(str(tmp_path))
    storage.make_dir("düğün")
    storage.make_dir("nikah")

    assert storage.rename_dir("düğün", "nikah") is None
    assert storage.rename_dir("yok", "başka") is False

    assert storage.dir_exists("düğün")
    assert storage.dir_exists("nikah")
```

---

### Task 3: Kural

**Files:**
- Modify: `queen-editor/backend/tests/test_project_usecases.py`

**Interfaces:**
- Consumes: `rename_project(store, move, old, new)` — **uygulama turunda doğar**.
  `move(old, new, do)` çağrılıyor ve `do()`'nun cevabı geri veriliyor.

- [ ] **Step 1: `FakeStore`'a rename**

```python
    def rename(self, old, new):
        """The renamed project, None when the new name is taken, False when the old one is gone."""
        if any(p.name == new for p in self.projects):
            return None
        found = next((p for p in self.projects if p.name == old), None)
        if found is None:
            return False
        self.projects = [Project(new, p.modified_at) if p.name == old else p
                         for p in self.projects]
        return next(p for p in self.projects if p.name == new)
```

- [ ] **Step 2: `test_create_project_raises_when_name_taken`'in altına beş test**

```python
# The port the projects feature knows nothing behind: production follows the folder there
# (photo_generation's own use case). Here it only has to run what it was handed.
def straight(old, new, do):
    return do()


def test_rename_moves_the_project_and_leaves_the_rest_alone():
    store = FakeStore([Project("düğün", 100.0), Project("nikah", 200.0)])

    rename_project(store, straight, "düğün", "kına")

    assert sorted(p.name for p in store.list()) == ["kına", "nikah"]


def test_rename_rejects_a_name_that_breaks_a_rule_without_touching_the_store():
    store = FakeStore([Project("düğün", 100.0)])
    with pytest.raises(InvalidName) as exc:
        rename_project(store, straight, "düğün", "foto/deneme")
    assert "kullanılamaz" in str(exc.value)
    assert [p.name for p in store.list()] == ["düğün"]


def test_rename_says_the_same_sentence_creating_says_when_the_name_is_taken():
    # One sentence for one situation: the user meets the same words whichever window they are in.
    store = FakeStore([Project("düğün", 100.0), Project("nikah", 200.0)])
    with pytest.raises(NameTaken) as exc:
        rename_project(store, straight, "düğün", "nikah")
    assert str(exc.value) == "Bu ad zaten kullanılıyor. Başka bir ad dene."


def test_saving_a_project_under_its_own_name_is_not_a_clash():
    # The design says so outright: the window closes and nothing moves.
    store = FakeStore([Project("düğün", 100.0)])

    rename_project(store, straight, "düğün", "düğün")

    assert [p.name for p in store.list()] == ["düğün"]


def test_renaming_a_project_that_is_not_there_says_so():
    with pytest.raises(ProjectMissing) as exc:
        rename_project(FakeStore(), straight, "yok", "başka")
    assert str(exc.value) == "Proje yok: yok"
```

`import`'lara `rename_project` ekleniyor.

---

### Task 4: Koşan iş adı takip ediyor

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_usecases.py`
- Modify: `queen-editor/backend/tests/test_photo_runner.py`

**Interfaces:**
- Consumes: `RunningName` ve `make_job(..., named=...)` — **uygulama turunda doğar**.
- Consumes: `PhotoRunner.rename(old, new)` — **uygulama turunda doğar**.

- [ ] **Step 1: `test_photo_usecases.py`'ye bir test**

`test_regenerating_with_the_same_prompt_stays_in_the_family`'nin hemen üstüne:

```python
def test_a_run_reads_the_project_name_again_every_turn():
    """A rename moves the folder under a run, and the run has to follow it: the name is read from a
    holder rather than captured once, so the turn after the move works in the new folder."""
    store, record, plan_store = video_project((0, "a"))
    named = RunningName("düğün")

    job = make_job(sync_runner(), store, record, plan_store,
                   {layers.PHOTO: FakeGenerator()}, lambda: "t", "düğün", named=named)
    named.moved("düğün", "başka", lambda: None)

    # The plan is read off the name the holder carries now, so a run on a project that is not there
    # any more says the folder is missing rather than quietly draining the old one.
    assert plan_store.read_for is None or plan_store.read_for == "düğün"
    job()
    assert plan_store.read_for == "başka"
```

> **Not:** `FakePlanStore`'a `read_for` alanı eklenecek — son okunan proje adı. Kırmızı turda test
> dosyasında, çünkü `FakePlanStore` orada yaşıyor.

- [ ] **Step 2: `test_photo_runner.py`'ye bir test**

```python
def test_the_runner_follows_a_project_that_was_renamed_under_it():
    # The screen compares the status's project with its own, so a stale stamp would hide a run from
    # the very page watching it.
    runner = PhotoRunner(spawn=lambda fn: None)
    runner.start("düğün", lambda: {"status": "done"})

    runner.rename("düğün", "nikah")

    assert runner.status()["project"] == "nikah"
```

---

### Task 5: Yol

**Files:**
- Modify: `queen-editor/backend/tests/test_projects_routes.py`

- [ ] **Step 1: `client_for`'a yeni bağlama**

```python
        rename_project=partial(rename_project, store, lambda old, new, do: do()),
```

- [ ] **Step 2: Silme testinin altına üç test**

```python
def test_renaming_a_project_moves_its_folder(tmp_path):
    client, drive = make_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})
    (drive / "düğün" / "0_a.png").write_bytes(b"PNG")

    resp = client.post("/api/projects/düğün/rename", json={"name": "nikah"})

    assert resp.status_code == 200
    assert resp.get_json()["name"] == "nikah"
    # The photo came with the folder: nothing inside a project is rewritten by a rename.
    assert (drive / "nikah" / "0_a.png").read_bytes() == b"PNG"
    assert not (drive / "düğün").exists()


def test_renaming_onto_a_name_that_is_taken_is_refused_with_the_reason(tmp_path):
    client, _ = make_client(tmp_path)
    client.post("/api/projects", json={"name": "düğün"})
    client.post("/api/projects", json={"name": "nikah"})

    resp = client.post("/api/projects/düğün/rename", json={"name": "nikah"})

    assert resp.status_code == 409
    assert resp.get_json()["error"] == "Bu ad zaten kullanılıyor. Başka bir ad dene."


def test_renaming_a_project_that_is_not_there_answers_404(tmp_path):
    client, _ = make_client(tmp_path)

    resp = client.post("/api/projects/yok/rename", json={"name": "başka"})

    assert resp.status_code == 404
```

---

### Task 6: İki boş kabuk

**Files:**
- Create: `queen-editor/backend/features/projects/domain/usecases/rename_project.py`
- Create: `queen-editor/backend/features/photo_generation/domain/running_name.py`

Yalnız belge ve imza; gövde yok. Sebebi Global Constraints'te.

- [ ] **Step 1: `rename_project.py`**

```python
"""Give one project a new name -- written in the tour after this one."""


def rename_project(store, move, old, new):
    raise NotImplementedError
```

- [ ] **Step 2: `running_name.py`**

```python
"""Which folder the worker is writing into -- written in the tour after this one."""


class RunningName:
    def __init__(self, name=None):
        raise NotImplementedError
```

- [ ] **Step 3: Yolun imzası**

Aynı sebep: `client_for` bilinmeyen bir argüman verirse Flask'ın planı hiç kurulmuyor ve dosyadaki
yirmi dört eski test de kırmızıya dönüyor. İmza parametreyi alıyor, yol henüz yok.

```python
def make_projects_blueprint(list_projects, create_project, check_name, delete_project, get_settings,
                            save_settings, rename_project=None):
```

Varsayılan `None`: `main.py` bu turda bağlamıyor ve kurulum onsuz da ayakta kalmalı. Uygulama
turunda parametre `delete_project`'in yanına taşınıyor ve varsayılanı kalkıyor.

---

### Task 7: Ekran

**Files:**
- Modify: `queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx`
- Modify: `queen-editor/frontend/src/shared/api.test.js`

- [ ] **Step 1: `api.js` taklidine `renameProject`**

```js
  renameProject: vi.fn(),
```

ve import satırına `renameProject` ekleniyor.

- [ ] **Step 2: Yeni blok, silme bloğunun altına**

```jsx
describe("ProjectsScreen renaming a project", () => {
  it("offers a pencil beside the bin", async () => {
    await openScreen();

    // Fark 1: the only way in. Neutral, not red -- renaming takes nothing away.
    const pencil = screen.getByLabelText("Projeyi yeniden adlandır");
    expect(pencil.style.color).not.toBe("var(--danger)");
  });

  it("opens the window on the name that is there", async () => {
    await openScreen();

    fireEvent.click(screen.getByLabelText("Projeyi yeniden adlandır"));

    expect(screen.getByText("Projeyi yeniden adlandır")).toBeTruthy();
    expect(screen.getByDisplayValue("düğün")).toBeTruthy();
    expect(navigate).not.toHaveBeenCalled();
  });

  it("asks nothing before renaming: it takes nothing away", async () => {
    await openScreen();

    fireEvent.click(screen.getByLabelText("Projeyi yeniden adlandır"));

    // Fark 3: no confirm window, no red button, no bin. The window opens straight onto the name.
    expect(screen.queryByText("Sil")).toBeNull();
    expect(screen.getByText("Kaydet")).toBeTruthy();
  });

  it("renames the project and reads the list again", async () => {
    await openScreen();
    renameProject.mockResolvedValue({ name: "nikah" });
    listProjects.mockResolvedValue([{ name: "nikah", modifiedAt: 1754300000 }]);

    fireEvent.click(screen.getByLabelText("Projeyi yeniden adlandır"));
    fireEvent.change(screen.getByDisplayValue("düğün"), { target: { value: "nikah" } });
    await act(async () => { fireEvent.click(screen.getByText("Kaydet")); });

    // Drive is the single source of truth here too: re-read rather than guess which card moved.
    expect(renameProject).toHaveBeenCalledWith("düğün", "nikah");
    expect(screen.getByText("nikah")).toBeTruthy();
  });

  it("says under the box when the name is already somebody's", async () => {
    await openScreen();
    renameProject.mockRejectedValue(new Error("Bu ad zaten kullanılıyor. Başka bir ad dene."));

    fireEvent.click(screen.getByLabelText("Projeyi yeniden adlandır"));
    fireEvent.change(screen.getByDisplayValue("düğün"), { target: { value: "nikah" } });
    await act(async () => { fireEvent.click(screen.getByText("Kaydet")); });

    // Fark 2: the field reddens and the sentence stands under it; typing takes it away again.
    expect(screen.getByText("Bu ad zaten kullanılıyor. Başka bir ad dene.")).toBeTruthy();
    expect(screen.getByDisplayValue("nikah").style.borderColor).toBe("var(--danger)");
  });
});
```

- [ ] **Step 3: `api.test.js`'e bir test**

```js
  it("renames a project at the address it has now", async () => {
    fetch.mockResolvedValue(answer({ name: "nikah" }));

    await renameProject("düğün", "nikah");

    // The address is the old name and the body is the new one: a project IS its folder, so the
    // folder it is in today is where the request has to go.
    expect(fetch).toHaveBeenCalledWith("/api/projects/d%C3%BC%C4%9F%C3%BCn/rename",
                                       expect.objectContaining({ method: "POST" }));
    expect(JSON.parse(fetch.mock.calls[0][1].body)).toEqual({ name: "nikah" });
  });
```

> **Not:** `api.test.js`'in kendi yardımcılarının adları farklıysa (`answer`, `fetch` taklidi) test
> o dosyanın kalıbına uydurulur — ölçtüğü şey değişmez.

- [ ] **Step 4: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: ilk ikisi yeşil (384 / 474). queen-editor Python **709 testin 12'si kırmızı**, frontend
**527 testin 8'i kırmızı**.

---

### Task 8: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): a project can be given another name

A project is a folder and its name is the address of everything in it, so the request
handed two questions to the spec: what happens to a running production, and what happens to
work already exported. Both are answered in the source before a line of test is written.

The folder is moved, not copied. A project can hold thousands of files and a copy over
Drive can be interrupted, which would leave two half projects and nobody able to say which
one is real; a rename is the filesystem's own atomic move. Everything a project knows lives
inside the folder -- the plan, the record, the settings, the exports -- so all of it travels
and none of it is rewritten. Frame names were never the project's name and are untouched.

A run has to follow the folder. Today the job takes the name once and keeps the string, so
a rename under a run would leave the next turn reading a folder that is not there and the
run would end in error -- renaming would kill production. The name comes from a holder read
again every turn, and the writes take that holder's lock, because a write creates the folder
it is missing and one resolved under the old name would leave a ghost beside the real thing.
The render stays outside the lock, so the wait is one file write.

Exports move with the folder but keep the name they were made under: that file was written
with that name in it and the user may already have it.

Twenty red tests. Twelve on the engine -- the folder move and its two ways to fail, the rule
and its four refusals, the run following the name, the worker's own stamp following it, and
the route's three answers. Eight on the screen -- the pencil beside the bin, the window
opening on the name it is about to change with the whole of it selected, the rename and the
reload, and the taken name said under the field.

The window is not written twice. The one that asks for a new project's name is the one that
asks for another, so it becomes a window that asks for a project name and takes its title,
its words and its measure from whoever opened it.

Frontend source untouched, so no dist in this commit.

Four suites run; 12 red in queen-editor python and 8 in its frontend.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in üç kararı Task 1; 20 testi Task 2 (1–2), Task 3 (3–7), Task 4 (8–9),
Task 5 (10–12), Task 7 (13–17), Task 6 (18–19), Task 7 Step 3 (20).

**Tip tutarlılığı:** `rename_dir` üç değer döndürüyor (mtime / `None` / `False`) ve `store.rename`
bunu `Project` / `None` / `False`'a çeviriyor; kural katmanı ikisini iki ayrı cümleye çeviriyor.
`move(old, new, do)` üç parametre alıyor ve `do()`'nun cevabını geri veriyor — testlerdeki
`straight` de öyle.

**Kontrol edilen tuzak:** `is False` ve `is None` ile kontrol ediliyor, `if not` ile değil: bir
mtime `0.0` olabilir ve o da yanlış olurdu.

**Kontrol edilen tuzak 2:** kural katmanı adı **taşımadan önce** doğruluyor, bugünkü
`create_project` gibi — kural kıran bir ad depoya hiç ulaşmıyor.

**Kontrol edilen tuzak 3:** 4. testte `named.moved` çağrılıp *sonra* `job()` koşuluyor. Sıra
önemli: `make_job` adı kapanışa almış olsaydı test yeşil geçerdi.

**Değişmeyen:** queen-agent'ın iki takımı, `dist`, üretim kodu.
