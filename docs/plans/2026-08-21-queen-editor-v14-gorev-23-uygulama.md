# v14 Görev 23 — Proje adı değiştirme: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test döngüsünün bıraktığı 12 + 8 kırmızıyı yeşile döndürmek.

**Architecture:** Motorda yedi dosya, ön yüzde dört. Tutamak `PhotoRunner`'ın üstünde duruyor, bu
yüzden `run_queue`'ya giden altı kullanım ve `main.py`'deki altı bağlama hiç değişmiyor.

**Tech Stack:** Python 3, Flask; React 18, vite.

**Spec:** [uygulama turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-23-proje-adi-uygulama-design.md)

## Global Constraints

- **Test dosyaları bu döngüde değişmiyor — bir dosya adı dışında.** `NewProjectModal.test.jsx`
  bileşenle birlikte `NameModal.test.jsx` oluyor; içeriği bileşenin adı ve prop'ları dışında aynı.
- Yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- **`dist` bu commit'te derleniyor.**
- Commit **yeşil gider**.

## File Structure

| Dosya | İşlem |
|---|---|
| `backend/services/drive/storage.py` | `rename_dir` |
| `backend/.../projects/data/project_store.py` | `rename` |
| `backend/.../projects/domain/usecases/rename_project.py` | kabuk doluyor |
| `backend/.../photo_generation/domain/running_name.py` | kabuk doluyor |
| `backend/.../photo_generation/domain/usecases/follow_rename.py` | yeni |
| `backend/.../photo_generation/runner.py` | tutamak ve `rename` |
| `backend/.../photo_generation/domain/run_loop.py` | adı her turda okuma, yazarken kilit |
| `backend/.../projects/presentation/routes.py` | yol |
| `backend/main.py` | bağlama |
| `frontend/src/shared/api.js` | `renameProject` |
| `frontend/.../projects/NewProjectModal.jsx` → `NameModal.jsx` | genelleşiyor |
| `frontend/.../projects/ProjectCard.jsx` | kalem |
| `frontend/.../projects/ProjectsScreen.jsx` | pencere ve istek |
| `frontend/dist/` | derlenir |

---

### Task 1: Klasörü taşımak

**Files:**
- Modify: `queen-editor/backend/services/drive/storage.py`
- Modify: `queen-editor/backend/features/projects/data/project_store.py`

- [ ] **Step 1: `delete_dir`'in altına**

```python
    def rename_dir(self, old, new):
        """Move root/old to root/new -- the folder itself, with everything in it.

        Renamed and never copied: a project can hold thousands of files and a copy over Drive can be
        interrupted, which leaves two half folders and nobody able to say which is real. A rename is
        one operation that either happened or did not.

        Two ways to fail and the caller has a different sentence for each, so they come back apart:
        False when there was nothing to move, None when the new name is already something. The mtime
        comes back on success, the same answer make_dir gives.
        """
        source = os.path.join(self.root, old)
        target = os.path.join(self.root, new)
        if not os.path.isdir(source):
            return False
        if os.path.exists(target):
            return None
        os.rename(source, target)
        return os.stat(target).st_mtime
```

- [ ] **Step 2: `DriveProjectStore.delete`'in altına**

```python
    def rename(self, old, new):
        """The renamed project, None when the new name is taken, False when the old one is gone."""
        moved = self.storage.rename_dir(old, new)
        # `is` and not truthiness: an mtime can be 0.0 and that is a success.
        if moved is None or moved is False:
            return moved
        return Project(new, moved)
```

---

### Task 2: Tutamak

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/running_name.py`

- [ ] **Step 1: Kabuğun yerine**

```python
"""Which folder the worker is writing into, and the gate a rename passes through.

A project IS a folder and its name is the address of everything inside it, so renaming one moves the
ground under a run. The run reads the name again every turn, which is what lets the turn after a
move simply work in the new folder.

What must not happen is a write that resolved the old name and lands after the move: the storage
layer creates a folder it is missing, so such a write would leave a ghost beside the real project
with one file in it. The writes take this lock and the rename takes it too, so no write can fall on
both sides of a move. The render is outside the lock -- the wait is one file write, not one frame.
"""
import threading
from contextlib import contextmanager


class RunningName:
    def __init__(self, name=None):
        # Re-entrant: a write asks for the name it is about to use while already inside the gate.
        self._lock = threading.RLock()
        self._name = name

    def took(self, name):
        """A run has started on this project."""
        with self._lock:
            self._name = name

    def now(self):
        """The name as it stands. Read at the top of every turn."""
        with self._lock:
            return self._name

    @contextmanager
    def steady(self):
        """The name, held still for as long as the caller writes with it."""
        with self._lock:
            yield self._name

    def moved(self, old, new, do):
        """Run `do` with no write able to straddle it, and follow the folder. Returns `do`'s answer.

        The name is followed only when it was this one: renaming a project nobody is producing must
        not point the worker somewhere else.
        """
        with self._lock:
            answer = do()
            if self._name == old:
                self._name = new
            return answer
```

---

### Task 3: İşçi

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/runner.py`
- Create: `queen-editor/backend/features/photo_generation/domain/usecases/follow_rename.py`

- [ ] **Step 1: `runner.py`**

`import threading`'in altına:

```python
from backend.features.photo_generation.domain.running_name import RunningName
```

`__init__`'e:

```python
        # Which folder the job is writing into. Held here because the runner is the one object every
        # way into the queue already carries, so nothing else has to be threaded a holder.
        self.named = RunningName()
```

`start`'ın içinde, `self._spawn(...)`'dan hemen önce:

```python
        self.named.took(project)
```

`reset`'in altına:

```python
    def rename(self, old, new):
        """Follow a project that was renamed under the worker.

        Only the stamp: the folder and the job's own name are the holder's business. The screen
        compares the status's project with its own, so a stale stamp would hide a run from the very
        page watching it.
        """
        with self._lock:
            if self._state.get("project") == old:
                self._state = {**self._state, "project": new}
```

- [ ] **Step 2: `follow_rename.py`**

```python
"""Let a project's folder be renamed under a run, and keep the run pointing at it.

This is the port the projects feature is handed, the same way `halt` is: renaming a project is that
feature's work, and the worker that might be inside the folder belongs to this one. They meet only
in main.py.
"""


def follow_rename(runner, old, new, move):
    """Run `move` with no write able to straddle it, then let the run and its status follow."""
    answer = runner.named.moved(old, new, move)
    runner.rename(old, new)
    return answer
```

---

### Task 4: Döngü adı takip ediyor

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/run_loop.py`

- [ ] **Step 1: İmza ve belge**

```python
def make_job(runner, store, record, plan_store, producers, now, project,
             clock=time.monotonic, log=None, order_store=None, writers=None,
             new_seed=seed.random_seed, named=None):
```

Belgeye bir paragraf:

```
    `named` is where the project's name is read from, turn by turn: a project IS a folder and it can
    be renamed under a run, so a name captured once would leave the next turn reading a folder that
    is not there. It defaults to the runner's own holder -- the runner is what every way into the
    queue already carries. A caller that hands its own is a test watching the run follow a move.
```

- [ ] **Step 2: Gövdenin başı**

```python
    named = named or runner.named
    named.took(project)

    def snapshot():
        project = named.now()
        return (plan_store.read(project)["frames"], record.slots(project),
                order_store.read(project) if order_store else ())
```

`summary` değişmiyor: `snapshot`'ı çağırıyor ve adı hiç kullanmıyor.

- [ ] **Step 3: Turun başı**

```python
            jobs, slots, order = snapshot()
```
satırının hemen üstüne:

```python
            # Read again every turn: a rename moves the folder under the run and this is what lets
            # the next turn simply work in the new one.
            project = named.now()
```

- [ ] **Step 4: Yazma bloğu kilit altında**

`store.save` ve `record.append` çağrılarını saran satır:

```python
            # Together and under the gate: the storage layer creates a folder it is missing, so a
            # save that resolved the old name after a rename would leave a ghost project beside the
            # real one with this single file in it.
            with named.steady() as project:
                filename = store.save(project, name, data)
                record.append(project, {...})
```

Hata yolundaki `record.mark(project, fid, kind, name, queue.FAILED, ...)` de aynı biçimde
sarılıyor.

---

### Task 5: Kural, yol ve bağlama

**Files:**
- Modify: `queen-editor/backend/features/projects/domain/usecases/rename_project.py`
- Modify: `queen-editor/backend/features/projects/presentation/routes.py`
- Modify: `queen-editor/backend/main.py`

- [ ] **Step 1: `rename_project.py`**

```python
"""Give one project a new name -- the folder's own name, because that is what a project is.

Everything a project knows lives inside its folder: the plan, the record, the settings, the exports.
All of it travels with the move and none of it is rewritten, and frame names were never the
project's name to begin with.

`move` is where a running production is carried over (photo_generation's own use case). What is
behind it is not this feature's business, the same way `halt` is not.

Both exception messages are user-facing Turkish and they are the ones creating a project already
uses: one situation, one sentence, whichever window the user is in.
"""
from backend.features.projects.domain import name_rules
from backend.features.projects.domain.usecases.create_project import InvalidName, NameTaken
from backend.features.projects.domain.usecases.get_settings import ProjectMissing


def rename_project(store, move, old, new):
    error = name_rules.validate(new)
    if error:
        raise InvalidName(error)
    # A project saved under the name it already has is not a mistake, and there is nothing to move.
    if new == old:
        return
    answer = move(old, new, lambda: store.rename(old, new))
    # `is` and not truthiness: the two failures are two different sentences and neither is falsy by
    # accident.
    if answer is None:
        raise NameTaken("Bu ad zaten kullanılıyor. Başka bir ad dene.")
    if answer is False:
        raise ProjectMissing(f"Proje yok: {old}")
```

- [ ] **Step 2: Yol**

İmza:

```python
def make_projects_blueprint(list_projects, create_project, check_name, delete_project,
                            rename_project, get_settings, save_settings):
```

`delete_one_project`'in altına:

```python
    @bp.post("/api/projects/<project>/rename")
    def post_rename_project(project):
        name = (request.get_json(silent=True) or {}).get("name", "")
        try:
            rename_project(project, name)
        except InvalidName as exc:
            return jsonify({"error": str(exc)}), 400
        except NameTaken as exc:
            return jsonify({"error": str(exc)}), 409
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            return jsonify({"error": str(exc)}), 500
        # The name is the whole answer: the screen re-reads the list, which is where the date and
        # the order come from.
        return jsonify({"name": name})
```

`InvalidName` ve `NameTaken` zaten içeri alınmış.

- [ ] **Step 3: `main.py`**

```python
from backend.features.photo_generation.domain.usecases.follow_rename import follow_rename
from backend.features.projects.domain.usecases.rename_project import rename_project
```

ve blueprint'e:

```python
    rename_project=partial(rename_project, _project_store,
                           partial(follow_rename, _photo_runner)),
```

---

### Task 6: İstek

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js`

- [ ] **Step 1: `deleteProject`'in yanına**

```js
// The address is the name the project has today and the body is the one it is getting: a project IS
// its folder, so the folder it is in now is where the request has to go.
export async function renameProject(project, name) {
  return request(`/api/projects/${encodeURIComponent(project)}/rename`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
}
```

---

### Task 7: Pencere

**Files:**
- Rename: `.../projects/NewProjectModal.jsx` → `NameModal.jsx`
- Rename: `.../projects/NewProjectModal.test.jsx` → `NameModal.test.jsx`

- [ ] **Step 1: Bileşen**

Belge:

```jsx
// A window that asks for a project name -- to open one with, or to give one another. Both are the
// same window, so it is written once and its heading, its opening value, its words and its measure
// come from whoever opened it.
//
// The server owns the name rules; this modal never keeps a copy. It warns as the name is typed by
// asking the server whether the name would be accepted and printing whatever sentence comes back.
// A name already taken is not a broken rule and the check knows nothing about the disk, so a clash
// only appears once the button is pressed and the server refuses.
export default function NameModal({ title, value = "", submitLabel, busyLabel, width = 400,
                                   onCancel, onSubmit }) {
  const [name, setName] = useState(value);
  ...
  const box = useRef(null);
```

Alanın seçilmesi:

```jsx
  // Opened on a name that is already there: the whole of it is selected, so one keystroke replaces
  // it and nobody has to clear the box by hand.
  useEffect(() => { if (value) box.current?.select(); }, [value]);
```

`submit` içindeki `onCreate(name)` → `onSubmit(name)`. Kartın genişliği `width`, başlık `title`,
düğme `busy ? busyLabel : submitLabel`.

`<input ref={box} ... />`.

400'ün gerekçe yorumu bileşenden çağırana taşınıyor.

- [ ] **Step 2: Test dosyası**

Adı `NameModal.test.jsx`; `NewProjectModal` geçen her yer `NameModal`, `onCreate` prop'u `onSubmit`,
ve her `render` çağrısı pencerenin sözlerini veriyor:

```jsx
const openIt = (props = {}) => render(
  <NameModal title="Yeni proje" submitLabel="Oluştur" busyLabel="Oluşturuluyor…"
             onCancel={() => {}} onSubmit={() => Promise.resolve()} {...props} />,
);
```

Testlerin gövdeleri değişmiyor.

---

### Task 8: Kart ve ekran

**Files:**
- Modify: `queen-editor/frontend/src/features/projects/ProjectCard.jsx`
- Modify: `queen-editor/frontend/src/features/projects/ProjectsScreen.jsx`

- [ ] **Step 1: `ProjectCard`**

```jsx
export default function ProjectCard({ name, modifiedAt, onDelete, onRename }) {
```

Çöp düğmesi ikisini tutan bir satıra giriyor:

```jsx
      {/* Two icon buttons, 4px apart (Fark 5). Neither carries a box: the card's own line is
          already there and a second one around an icon reads as a button sitting on a button
          (madde 3). The pencil is neutral -- renaming takes nothing away (Fark 3) -- and the label
          the destructive standard asks for lives on the delete confirm instead (madde 9). */}
      <div style={{ position: "absolute", top: 10, right: 10, display: "flex", gap: 4 }}>
        <Btn sm aria-label="Projeyi yeniden adlandır" onClick={onRename}
             style={{ border: "none", background: "none", padding: "4px 8px" }}>
          <Icon.Pencil />
        </Btn>
        <Btn sm aria-label="Projeyi sil" onClick={onDelete}
             style={{ color: "var(--danger)", border: "none", background: "none",
                      padding: "4px 8px" }}>
          <Icon.Trash />
        </Btn>
      </div>
```

- [ ] **Step 2: `ProjectsScreen`**

```js
import { createProject, deleteProject, renameProject } from "../../shared/api.js";
import NameModal from "./NameModal.jsx";
```

```jsx
  // The name being renamed, or null -- the twin of deletingName. It is what the window opens on and
  // what the request is addressed to.
  const [renamingName, setRenamingName] = useState(null);
```

```jsx
  // Drive is the single source of truth here too: re-read the list rather than guess which card
  // moved and what its date became.
  async function handleRename(name) {
    await renameProject(renamingName, name);
    setRenamingName(null);
    await reload();
  }
```

Kart:

```jsx
              <ProjectCard key={p.name} name={p.name} modifiedAt={p.modifiedAt}
                           onDelete={() => setDeletingName(p.name)}
                           onRename={() => setRenamingName(p.name)} />
```

İki pencere:

```jsx
      {modalOpen && (
        // 400: the widest of the plain windows, because the name box carries a rule line under it
        // and a warning that must not wrap mid-word (madde 105).
        <NameModal title="Yeni proje" submitLabel="Oluştur" busyLabel="Oluşturuluyor…" width={400}
                   onCancel={() => setModalOpen(false)} onSubmit={handleCreate} />
      )}

      {renamingName && (
        // Renaming takes nothing away, so there is no confirm and no red: the window opens straight
        // onto the name (Fark 3), at the measure the design gives it (Fark 4).
        <NameModal title="Projeyi yeniden adlandır" value={renamingName}
                   submitLabel="Kaydet" busyLabel="Kaydediliyor…" width={380}
                   onCancel={() => setRenamingName(null)} onSubmit={handleRename} />
      )}
```

- [ ] **Step 3: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: dördü de yeşil — 384 / 474 / 709 / 527.

---

### Task 9: Derlenmiş çıktı ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Yol haritasını işaretle**

23. maddenin **İş** hücresi ✅ ile başlar, sayaç `22/31` → `23/31`.

- [ ] **Step 3: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): a project can be given another name

The folder is moved, with everything in it and nothing rewritten.

Where the holder lives is the decision that kept this small. Every way into the queue --
starting a batch, hanging a layer, making one again, retrying, resuming -- ends at run_queue,
and each of them is bound separately in main.py, so handing the name down as an argument
would have been six signatures and six bindings. But the runner is the one object all of
them already carry, and which folder the worker is writing into is the worker's own business.
The holder sits on the runner, the loop reads it, and nothing else moved.

The loop reads the name again at the top of every turn, so the turn after a move simply
works in the new folder. The writes -- the file and the line about it -- happen inside the
holder's gate, and the rename takes the same gate: the storage layer creates a folder it is
missing, so a save that resolved the old name and landed after the move would leave a ghost
project beside the real one with that single file in it. The render stays outside, so the
wait is one file write and not one frame.

The worker's own stamp follows too. The screen decides whether a run is its own by comparing
the status's project with the page's, so a stale stamp would hide a run from the very page
watching it.

On the screen the card grows a pencil beside its bin, and the window that asks for a new
project's name becomes a window that asks for a project name: same window, opened with a
different heading, a different button and a different measure. Opened on a name that is
already there it selects the whole of it, so one keystroke replaces it.

Nothing about it is destructive: no confirm, no red, and it works while production is
running.

dist built in this commit.

Four suites green.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in sekiz bölümü Task 3 (1), Task 2 (2), Task 4 (3), Task 3 Step 2 (4),
Task 5 Step 1 + Task 1 (5), Task 5 Step 2 (6), Task 7 (7), Task 8 (8).

**Tip tutarlılığı:** `moved(old, new, do)` üç parametre alıyor ve `do()`'nun cevabını geri
veriyor — `follow_rename` ve testlerdeki `straight` aynı biçimde çağrılıyor. `named` protokolü
`now()` / `steady()` / `took()` / `moved()`; testin sahtesi ilk ikisini karşılıyor, ki `make_job`'ın
kullandığı da o ikisi artı `took`.

**Kontrol edilen tuzak:** `make_job` sahte tutamağa `took()` çağırıyor — testin `MovingName`'inde
öyle bir metot yok. `took` yalnız `named` verilmediğinde çağrılıyor: verilmişse adı zaten çağıran
belirlemiş.

**Kontrol edilen tuzak 2:** `RLock`, `Lock` değil — yazma bloğunun içinde ad bir kez daha sorulursa
kendi kendini kilitlemesin.

**Kontrol edilen tuzak 3:** `moved` adı yalnız eşleşince takip ediyor; kimsenin üretmediği bir
projeyi yeniden adlandırmak işçiyi başka yere bakar hâle getirmiyor.

**Kontrol edilen tuzak 4:** `Icon.Pencil` kitte zaten var — yeni bir çizim gerekmiyor.

**Koşuda çıkan tuzak 5:** `test_producer_contract.py`'nin kendi sahte `Runner`'ı düştü — döngü
artık işçiden bir tutamak istiyor ve o sahte yalnız iki metot taşıyordu. Bir işbirlikçinin arayüzü
genişleyince onun sahtesi de genişler; kırmızı tur bunu listelemeliydi, 22. maddedeki imza tuzağının
aynısı. Sahteye tutamak eklendi, ölçtüğü şey değişmedi.

**Değişmeyen:** çöpün rengi ve yıkıcı standart (fark 5, 24. madde), yeni proje penceresinin 400
genişliği (fark 6, 24. madde), `run_queue` ve ona giden altı kullanım.
