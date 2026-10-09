# Bölüm 11 — Foto Detay Sayfası Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fotoğrafa tıklayınca kendi adresi olan bir detay sayfası açılır: fotoğraf orijinal oranında, ‹ › ve klavyeyle gezinti, sağda sıra/dosya adı/prompt, Sil → onay → sonraki fotoğraf.

**Architecture:** Silme, kaydı yeniden yazmadan **silme satırı** ekler; okuma kaydı bir günlük gibi katlar. Numaralandırma artık kaydı da dinler, böylece silinen numara geri kullanılmaz. Yeni uç `DELETE /api/projects/<p>/photos/<dosya>`. Frontend'de yol çözümlemesi `{project, photo}` döndürür; detay sayfası kendi küçük hook'uyla (`usePhotos`) listeyi okur ve siler.

**Tech Stack:** Flask + pytest · React 18 + vitest/jsdom.

**Spec:** [2026-08-05-queen-editor-bolum11-foto-detay-design.md](../specs/2026-08-05-queen-editor-bolum11-foto-detay-design.md)

## Global Constraints

- **TDD:** önce düşen test, sonra kod.
- **Commit:** bölüm sonunda tek commit + push; `dist/` aynı commit'te.
- **Katmanlar:** dosya adı şeması artık `domain/photo_name.py`'de tek yerde; `data/` onu kullanır.
- **`photos.jsonl` asla baştan yazılmaz** — silme bir satır eklemektir.
- **Yorum koddan sapamaz:** `next_number`'ın "kayda bakmaya gerek yok" diyen dokümantasyonu bu bölümde geçersizleşiyor, aynı commit'te düzeltilir.
- Tasarım değerleri birebir (spec §2): ok `fontSize:44`, `fontWeight:300`, `left/right:20`, `top:50%`, `textShadow:"0 0 4px rgba(0,0,0,.9), 0 2px 8px rgba(0,0,0,.7)"`; bilgi sütunu `width:300`, `padding:16`, `gap:14`; etiketler `Mono size={10}` `var(--ink-3)` `letterSpacing:".08em"` uppercase; değerler `Mono size={13}` `var(--ink)`; prompt kutusu `wf-stroke` + `overflowY:"auto"` + `padding:10`, içi `Note size={12}` `var(--ink-2)` `lineHeight:1.6`; Sil `Btn sm` + `color/borderColor: var(--danger)`; onay kutusu `width:320`, `padding:18`, `gap:10`, onay düğmesi dolu kırmızı (`background/borderColor: var(--danger)`, `color:"#fff"`).
- Pasif ok `opacity:.25`, tıklanamaz; liste başa sarmaz.
- Ekran metni Türkçe, kod/yorum İngilizce. CRLF korunur.

---

### Task 1: Dosya adı kuralı tek yere + kayıt günlüğe dönüşür

**Files:**
- Create: `queen-editor/backend/features/photo_generation/domain/photo_name.py`
- Modify: `queen-editor/backend/features/photo_generation/data/photo_store.py`
- Modify: `queen-editor/backend/features/photo_generation/data/photo_record.py`
- Modify: `queen-editor/backend/features/photo_generation/domain/ports.py`
- Test: `queen-editor/backend/tests/test_photo_record.py`, `queen-editor/backend/tests/test_photo_name.py` (yeni)

**Interfaces:**
- Produces: `number_of(filename) -> int | None`; `PhotoRecord.mark_deleted(project, file, at)`, `PhotoRecord.max_number(project) -> int | None`; `PhotoRecord.list` artık silinenleri elemektedir.

- [ ] **Step 1: Testleri yaz**

`test_photo_name.py`:

```python
from backend.features.photo_generation.domain.photo_name import number_of


def test_number_comes_from_the_name():
    assert number_of("12_a.png") == 12


def test_a_name_outside_the_scheme_has_no_number():
    assert number_of("notlar.txt") is None
    assert number_of("photos.jsonl") is None
    assert number_of("12.png") is None
    assert number_of("12_ab.png") is None
    assert number_of("x_a.png") is None
```

`test_photo_record.py` sonuna:

```python
def test_a_deleted_photo_leaves_the_list_but_not_the_file(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("0_a.png"))
    record.append("düğün", entry("0_b.png"))

    record.mark_deleted("düğün", "0_a.png", "2026-08-05T10:00:00+00:00")

    assert [row["file"] for row in record.list("düğün")] == ["0_b.png"]
    # The log is only ever appended to: the original row is still in the file.
    lines = (tmp_path / "düğün" / "photos.jsonl").read_text(encoding="utf-8").splitlines()
    assert len(lines) == 3


def test_the_record_remembers_the_numbers_of_deleted_photos(tmp_path):
    record = record_at(tmp_path)
    record.append("düğün", entry("7_a.png"))
    record.mark_deleted("düğün", "7_a.png", "2026-08-05T10:00:00+00:00")

    assert record.max_number("düğün") == 7


def test_an_empty_record_claims_no_number(tmp_path):
    assert record_at(tmp_path).max_number("düğün") is None
```

- [ ] **Step 2: Koştur, düştüğünü gör**

Run: `python -m pytest backend/tests/test_photo_name.py backend/tests/test_photo_record.py -q`
Expected: FAIL.

- [ ] **Step 3: `photo_name.py`'ı yaz**

```python
"""How a photo file is named: "<number>_<letter>.png" -- number = prompt, letter = variant.

Both the store (which files are on disk) and the record (which files ever existed) have to read a
number out of a name, and two copies of that rule would be two chances to disagree.
"""


def number_of(filename):
    """"12_a.png" -> 12; anything that does not fit the scheme -> None."""
    if not filename.endswith(".png"):
        return None
    number, _, letter = filename[: -len(".png")].partition("_")
    if not number.isdigit() or len(letter) != 1 or not letter.isalpha():
        return None
    return int(number)
```

- [ ] **Step 4: `photo_store.py`'ı sadeleştir**

Dosyanın başındaki `_number_of` fonksiyonu silinir, yerine import:

```python
from backend.features.photo_generation.domain.photo_name import number_of
```

`next_number` içindeki `_number_of` çağrısı `number_of` olur. Modül docstring'indeki
"the only place that knows photos are named …" cümlesi şuna düzeltilir (yorum koddan sapamaz):

```
"""PhotoStore over DriveStorage -- photos live in the project folder, named by domain/photo_name.py.
```

- [ ] **Step 5: `photo_record.py`'ı günlüğe çevir**

```python
"""PhotoRecord over DriveStorage -- the only place that knows the record file's name and shape.

This is the gallery's log: one JSON object per line, appended right after the photo itself is
written, never rewritten. Append-only is the point -- a session that dies mid-write loses at most
the line it was adding, where rewriting the whole file could lose every earlier one. Deleting a
photo therefore appends a deletion row instead of removing anything, and reading folds the log.
"""
import json

from backend.features.photo_generation.domain.photo_name import number_of

FILE = "photos.jsonl"


class DrivePhotoRecord:
    def __init__(self, storage):
        self._storage = storage

    def append(self, project, entry):
        """entry: {"file", "prompt", "negative", "seed", "createdAt"}."""
        self._storage.append_line(project, FILE, json.dumps(entry, ensure_ascii=False))

    def mark_deleted(self, project, file, at):
        """Write down that a photo is gone, without touching the rows already there."""
        self.append(project, {"file": file, "deletedAt": at})

    def _rows(self, project):
        """Every readable row, in the order it was written.

        A line that will not parse is skipped rather than raised on: the last one can be
        half-written after a session death, and one bad line must not hide the photos before it.
        """
        rows = []
        for line in self._storage.read_lines(project, FILE):
            try:
                row = json.loads(line)
            except ValueError:
                continue
            if isinstance(row, dict) and isinstance(row.get("file"), str):
                rows.append(row)
        return rows

    def list(self, project):
        """Every photo that still exists, newest first."""
        live = {}
        for row in self._rows(project):
            if row.get("deletedAt"):
                live.pop(row["file"], None)
            else:
                live[row["file"]] = row
        return list(reversed(list(live.values())))

    def max_number(self, project):
        """Highest number the record has ever seen, deleted photos included; None when empty.

        Deleted rows still count: their number has to stay claimed, or a new photo would take the
        name of a deleted one -- same name, a different prompt, and browsers still holding the old
        bytes under an immutable cache header.
        """
        numbers = [n for n in (number_of(row["file"]) for row in self._rows(project))
                   if n is not None]
        return max(numbers) if numbers else None
```

- [ ] **Step 6: Portu güncelle** (`ports.py`, `PhotoRecord` protokolüne)

```python
    def mark_deleted(self, project: str, file: str, at: str) -> None:
        """Append the row that says this photo is gone."""
        ...

    def max_number(self, project: str) -> int | None:
        """Highest number the record has ever seen, deleted photos included."""
        ...
```

- [ ] **Step 7: Koştur**

Run: `python -m pytest backend/tests/test_photo_name.py backend/tests/test_photo_record.py -q`
Expected: PASS.

### Task 2: Diskten silme (storage + store)

**Files:**
- Modify: `queen-editor/backend/services/drive/storage.py`
- Modify: `queen-editor/backend/features/photo_generation/data/photo_store.py`
- Modify: `queen-editor/backend/features/photo_generation/domain/ports.py`
- Test: `queen-editor/backend/tests/test_drive_storage.py`, `queen-editor/backend/tests/test_photo_store.py`

**Interfaces:**
- Produces: `DriveStorage.delete_file(subdir, name)`, `PhotoStore.delete(project, filename)`.

- [ ] **Step 1: Testleri yaz**

`test_drive_storage.py` sonuna (dosyadaki mevcut yardımcıyla aynı biçimde):

```python
def test_deleting_a_file_removes_it(tmp_path):
    storage = DriveStorage(str(tmp_path))
    storage.write_bytes("düğün", "0_a.png", b"PNG")
    storage.delete_file("düğün", "0_a.png")
    assert storage.list_files("düğün") == []


def test_deleting_a_file_that_is_already_gone_is_not_an_error(tmp_path):
    DriveStorage(str(tmp_path)).delete_file("düğün", "yok.png")
```

`test_photo_store.py` sonuna:

```python
def test_delete_removes_the_photo_from_the_project_folder(tmp_path):
    storage = DriveStorage(str(tmp_path))
    store = DrivePhotoStore(storage)
    store.save("düğün", 0, "a", b"PNG")

    store.delete("düğün", "0_a.png")

    assert storage.list_files("düğün") == []
```

(Import satırları dosyanın mevcut hâline göre tamamlanır.)

- [ ] **Step 2: Koştur, düştüğünü gör** → FAIL.

- [ ] **Step 3: Kodu yaz**

`storage.py`'a:

```python
    def delete_file(self, subdir, name):
        """Remove root/subdir/name. A file that is already gone is not an error: deleting twice has
        to end where deleting once ends, so a retried request is safe."""
        try:
            os.remove(os.path.join(self.root, subdir, name))
        except FileNotFoundError:
            pass
```

`photo_store.py`'a:

```python
    def delete(self, project, filename):
        self._storage.delete_file(project, filename)
```

`ports.py` `PhotoStore` protokolüne:

```python
    def delete(self, project: str, filename: str) -> None:
        """Remove the photo from the project folder; a missing file is not an error."""
        ...
```

- [ ] **Step 4: Koştur** → PASS.

### Task 3: `next_number` kaydı dinler + `delete_photo` use case

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/start_batch.py`
- Create: `queen-editor/backend/features/photo_generation/domain/usecases/delete_photo.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Produces: `next_number(store, plan_store, record, project)` — **imza değişti**; `delete_photo(record, store, order_store, now, project, file)`; `PhotoMissing`.

- [ ] **Step 1: Testleri yaz**

Import satırına:

```python
from backend.features.photo_generation.domain.usecases.delete_photo import PhotoMissing, delete_photo
```

`FakeStore`'a silme desteği (dosyadaki sahtenin içine):

```python
    def delete(self, project, filename):
        self.deleted.append(filename)
```

ve `__init__`'ine `self.deleted = []`. `FakeRecord`'a:

```python
    def mark_deleted(self, project, file, at):
        self.rows.append({"file": file, "deletedAt": at})

    def max_number(self, project):
        numbers = [int(row["file"].split("_")[0]) for row in self.rows
                   if row["file"].split("_")[0].isdigit()]
        return max(numbers) if numbers else None
```

ve `FakeRecord.list` silinenleri elemeli (gerçek kaydın davranışını taklit eder):

```python
    def list(self, project):
        live = {}
        for row in self.rows:
            if row.get("deletedAt"):
                live.pop(row["file"], None)
            else:
                live[row["file"]] = row
        return list(reversed(list(live.values())))
```

Testler:

```python
def test_a_deleted_number_is_never_used_again():
    store, record, plan_store = FakeStore(next_no=0), FakeRecord(), FakePlanStore()
    record.append("düğün", {"file": "0_a.png"})
    record.mark_deleted("düğün", "0_a.png", "2026-08-05T10:00:00+00:00")

    assert next_number(store, plan_store, record, "düğün") == 1


def test_delete_removes_the_file_records_it_and_prunes_the_order():
    store, record = FakeStore(), FakeRecord()
    record.append("düğün", {"file": "0_a.png"})
    record.append("düğün", {"file": "1_a.png"})
    order = FakeOrderStore(["0_a.png", "1_a.png"])

    delete_photo(record, store, order, lambda: "2026-08-05T10:00:00+00:00", "düğün", "0_a.png")

    assert store.deleted == ["0_a.png"]
    assert [row["file"] for row in record.list("düğün")] == ["1_a.png"]
    assert order.order == ["1_a.png"]


def test_deleting_an_unknown_photo_is_rejected():
    with pytest.raises(PhotoMissing):
        delete_photo(FakeRecord(), FakeStore(), FakeOrderStore(), lambda: "t", "düğün", "yok.png")


def test_deleting_in_a_missing_project_is_rejected():
    with pytest.raises(ProjectMissing):
        delete_photo(FakeRecord(), FakeStore(projects=()), FakeOrderStore(), lambda: "t",
                     "yok", "0_a.png")
```

`next_number` import'u dosyada yoksa eklenir.

- [ ] **Step 2: Koştur, düştüğünü gör** → FAIL.

- [ ] **Step 3: `next_number`'ı güncelle** (`start_batch.py`)

```python
def next_number(store, plan_store, record, project):
    """The first number a new run may use.

    Three things can claim a number: a file already on disk, a frame an earlier plan reserved but
    never produced, and a photo that has since been deleted -- the record remembers those. All are
    honoured: reusing a number would bind one file name to two prompts, and a browser holding the
    deleted photo under an immutable cache header would keep showing the old image.
    """
    claims = [store.next_number(project)]
    reserved = plan_store.max_number(project)
    if reserved is not None:
        claims.append(reserved + 1)
    seen = record.max_number(project)
    if seen is not None:
        claims.append(seen + 1)
    return max(claims)
```

`start_batch` içindeki çağrı `next_number(store, plan_store, record, project)` olur.

- [ ] **Step 4: `delete_photo.py`'ı yaz**

```python
"""Delete one photo: from Drive, from the record, and from the gallery order.

Order matters. The file goes first: if that fails nothing has changed yet and the error is the whole
truth. The record is then appended to (never rewritten -- see data/photo_record.py), and the order
file drops the name so it carries no dead entries.
"""
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class PhotoMissing(Exception):
    """No such photo in this project's record."""


def delete_photo(record, store, order_store, now, project, file):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    if file not in {row["file"] for row in record.list(project)}:
        raise PhotoMissing(f"Fotoğraf yok: {file}")
    store.delete(project, file)
    record.mark_deleted(project, file, now())
    order_store.write(project, [name for name in order_store.read(project) if name != file])
```

- [ ] **Step 5: Koştur** → `python -m pytest backend/tests/test_photo_usecases.py -q` PASS.

### Task 4: `DELETE /api/projects/<p>/photos/<dosya>` ucu

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/presentation/routes.py`
- Modify: `queen-editor/backend/main.py`
- Test: `queen-editor/backend/tests/test_photo_routes.py`

- [ ] **Step 1: Testleri yaz**

`make_client`'ın blueprint çağrısına:

```python
        delete_photo=partial(delete_photo, record, store, order_store,
                             lambda: "2026-08-05T10:00:00+00:00"),
```

Testler:

```python
def test_deleting_a_photo_removes_it_from_the_gallery_and_the_folder(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)

    resp = client.delete("/api/projects/düğün/photos/0_a.png")

    assert resp.status_code == 204
    assert files_of(client) == ["1_a.png"]
    assert not (drive / "düğün" / "0_a.png").exists()


def test_a_photo_produced_after_a_delete_does_not_reuse_the_number(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)
    client.delete("/api/projects/düğün/photos/0_a.png")

    generate(client, prompts='["b"]', variants=1)

    assert files_of(client) == ["1_a.png"]


def test_deleting_an_unknown_photo_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.delete("/api/projects/düğün/photos/yok.png").status_code == 404
```

- [ ] **Step 2: Koştur, düştüğünü gör** → FAIL.

- [ ] **Step 3: Rotayı yaz**

Import: `from backend.features.photo_generation.domain.usecases.delete_photo import PhotoMissing`
İmzaya `delete_photo` eklenir (`export_project`'ten sonra). `export` rotasının ardına:

```python
    @bp.delete("/api/projects/<project>/photos/<filename>")
    def remove_photo(project, filename):
        try:
            delete_photo(project, filename)
        except (ProjectMissing, PhotoMissing) as exc:
            return jsonify({"error": str(exc)}), 404
        except OSError as exc:
            # The operating system's own words -- never guess the cause.
            return jsonify({"error": str(exc)}), 500
        # 204: the client already knows the gallery order, so it opens the next photo itself.
        return "", 204
```

`main.py`: import + `delete_photo=partial(delete_photo, _photo_record, _photo_store, _order_store, lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")),`

- [ ] **Step 4: Tüm backend** → `python -m pytest -q` PASS.

### Task 5: Yol çözümlemesi `{project, photo}`

**Files:**
- Modify: `queen-editor/frontend/src/shared/router.js`
- Modify: `queen-editor/frontend/src/App.jsx`
- Test: `queen-editor/frontend/src/shared/router.test.js` (yeni)

**Interfaces:**
- Produces: `routeFromPath(path) -> {project, photo}`, `photoPath(project, file)`, `projectPath(project)`. `projectFromPath` kaldırılır (tek kullanıcısı `App.jsx`).

- [ ] **Step 1: Testi yaz**

```js
import { describe, expect, it } from "vitest";

import { photoPath, projectPath, routeFromPath } from "./router.js";

describe("routeFromPath", () => {
  it("kök yolda ne proje ne fotoğraf vardır", () => {
    expect(routeFromPath("/")).toEqual({ project: null, photo: null });
  });

  it("proje yolunu çözer", () => {
    expect(routeFromPath(`/projects/${encodeURIComponent("düğün 2")}`))
      .toEqual({ project: "düğün 2", photo: null });
  });

  it("fotoğraf yolunu proje adı sanmaz", () => {
    expect(routeFromPath(`/projects/${encodeURIComponent("düğün")}/photos/0_a.png`))
      .toEqual({ project: "düğün", photo: "0_a.png" });
  });

  it("yol üreteçleri kodlar", () => {
    expect(projectPath("düğün")).toBe(`/projects/${encodeURIComponent("düğün")}`);
    expect(photoPath("düğün", "0_a.png"))
      .toBe(`/projects/${encodeURIComponent("düğün")}/photos/0_a.png`);
  });
});
```

- [ ] **Step 2: Koştur, düştüğünü gör** → FAIL.

- [ ] **Step 3: `router.js`'i güncelle**

`projectFromPath` yerine:

```js
// Three screens, so three shapes of path -- a router library would still be more code than this.
// Project names carry spaces and Turkish letters, so every segment is encoded.
export function routeFromPath(path) {
  const photo = path.match(/^\/projects\/([^/]+)\/photos\/([^/]+)$/);
  if (photo) {
    return { project: decodeURIComponent(photo[1]), photo: decodeURIComponent(photo[2]) };
  }
  const project = path.match(/^\/projects\/([^/]+)$/);
  return { project: project ? decodeURIComponent(project[1]) : null, photo: null };
}

export function projectPath(project) {
  return `/projects/${encodeURIComponent(project)}`;
}

export function photoPath(project, file) {
  return `${projectPath(project)}/photos/${encodeURIComponent(file)}`;
}
```

- [ ] **Step 4: `App.jsx`'i güncelle**

```jsx
export default function App() {
  const { project, photo } = routeFromPath(useRoute());
  if (!project) return <ProjectsScreen />;
  if (photo) return <PhotoDetailRoute project={project} file={photo} />;
  return <ProjectRoute project={project} />;
}
```

`PhotoDetailRoute` Task 7'de yazılır; bu adımda `App.jsx` yalnız `routeFromPath`'e geçer ve
`photo` dalı Task 7 gelene kadar eklenmez (derleme kırılmasın).

- [ ] **Step 5: Koştur** → PASS.

### Task 6: `deletePhoto` istemcisi + `usePhotos` hook'u

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js`
- Create: `queen-editor/frontend/src/features/photo_generation/usePhotos.js`
- Test: `queen-editor/frontend/src/features/photo_generation/usePhotos.test.jsx` (yeni)

**Interfaces:**
- Produces: `deletePhoto(project, file)`; `usePhotos(project) -> { photos, error, remove, reload }`.

- [ ] **Step 1: Testi yaz**

```jsx
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { deletePhoto, listPhotos } from "../../shared/api.js";
import { usePhotos } from "./usePhotos.js";

vi.mock("../../shared/api.js", () => ({
  deletePhoto: vi.fn(),
  listPhotos: vi.fn(),
}));

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("usePhotos", () => {
  it("listeyi galeri sırasıyla okur", async () => {
    listPhotos.mockResolvedValue([{ file: "1_a.png" }, { file: "0_a.png" }]);

    const { result } = renderHook(() => usePhotos("düğün"));
    expect(result.current.photos).toBeNull();
    await settle();

    expect(result.current.photos.map((p) => p.file)).toEqual(["1_a.png", "0_a.png"]);
  });

  it("silinen fotoğrafı listeden çıkarır", async () => {
    listPhotos.mockResolvedValue([{ file: "1_a.png" }, { file: "0_a.png" }]);
    deletePhoto.mockResolvedValue(null);

    const { result } = renderHook(() => usePhotos("düğün"));
    await settle();
    await act(async () => { await result.current.remove("1_a.png"); });

    expect(deletePhoto).toHaveBeenCalledWith("düğün", "1_a.png");
    expect(result.current.photos.map((p) => p.file)).toEqual(["0_a.png"]);
  });

  it("silme başarısızsa listeyi olduğu gibi bırakır ve hatayı söyler", async () => {
    listPhotos.mockResolvedValue([{ file: "0_a.png" }]);
    deletePhoto.mockRejectedValue(new Error("Fotoğraf yok: 0_a.png"));

    const { result } = renderHook(() => usePhotos("düğün"));
    await settle();
    await act(async () => { await result.current.remove("0_a.png"); });

    expect(result.current.error).toContain("Fotoğraf yok");
    expect(result.current.photos.map((p) => p.file)).toEqual(["0_a.png"]);
  });
});
```

- [ ] **Step 2: Koştur, düştüğünü gör** → FAIL.

- [ ] **Step 3: `api.js`'e ekle**

```js
export async function deletePhoto(project, file) {
  return request(`/api/projects/${encodeURIComponent(project)}/photos/${encodeURIComponent(file)}`,
                 { method: "DELETE" });
}
```

**Not:** 204 gövdesizdir; `request` gövdeyi okuyamayınca `null` döner (mevcut davranış) — bu
beklenen sonuçtur, ek kod gerekmez.

- [ ] **Step 4: `usePhotos.js`'i yaz**

```js
import { useCallback, useEffect, useRef, useState } from "react";

import { deletePhoto, listPhotos } from "../../shared/api.js";

// The detail page's own view of the gallery: the same list, in the same order, without the polling
// the project screen needs. Deleting is the only thing that changes it, so there is nothing to
// refresh on a timer.
export function usePhotos(project) {
  // null = not known yet (first fetch still flying), [] = the project truly has no photos.
  const [photos, setPhotos] = useState(null);
  const [error, setError] = useState(null);
  const alive = useRef(true);

  const reload = useCallback(() => (
    listPhotos(project)
      .then((data) => { if (alive.current) { setPhotos(data); setError(null); } })
      .catch((err) => { if (alive.current) setError(err.message); })
  ), [project]);

  useEffect(() => {
    alive.current = true;
    reload();
    return () => { alive.current = false; };
  }, [reload]);

  // The server answers 204 and says nothing else, so the list is trimmed here rather than re-read:
  // one photo left the set, and the order of the rest cannot have changed.
  const remove = useCallback((file) => (
    deletePhoto(project, file)
      .then(() => {
        if (!alive.current) return;
        setPhotos((current) => (current ? current.filter((photo) => photo.file !== file) : current));
      })
      .catch((err) => { if (alive.current) setError(err.message); })
  ), [project]);

  return { photos, error, remove, reload };
}
```

- [ ] **Step 5: Koştur** → PASS.

### Task 7: Detay sayfası, onay kutusu ve galeriden geçiş

**Files:**
- Create: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`
- Create: `queen-editor/frontend/src/features/photo_generation/PhotoDeleteModal.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`
- Modify: `queen-editor/frontend/src/App.jsx`
- Test: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx` (yeni), `Gallery.test.jsx` (ekleme)

- [ ] **Step 1: Testleri yaz**

`PhotoDetail.test.jsx`:

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { act } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { deletePhoto, listPhotos } from "../../shared/api.js";
import { navigate } from "../../shared/router.js";
import PhotoDetail from "./PhotoDetail.jsx";

vi.mock("../../shared/api.js", () => ({
  deletePhoto: vi.fn(),
  listPhotos: vi.fn(),
  photoUrl: (project, file) => `/photos/${project}/${file}`,
}));
vi.mock("../../shared/router.js", () => ({
  navigate: vi.fn(),
  photoPath: (project, file) => `/projects/${project}/photos/${file}`,
  projectPath: (project) => `/projects/${project}`,
}));

const PHOTOS = [{ file: "2_a.png", prompt: "üçüncü" },
                { file: "1_a.png", prompt: "ikinci" },
                { file: "0_a.png", prompt: "ilk" }];

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

async function open(file) {
  listPhotos.mockResolvedValue(PHOTOS);
  render(<PhotoDetail project="düğün" file={file} />);
  await settle();
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("PhotoDetail", () => {
  it("sırayı, dosya adını ve prompt'u gösterir", async () => {
    await open("1_a.png");

    expect(screen.getByText("2 / 3")).toBeTruthy();
    expect(screen.getByText("1_a.png")).toBeTruthy();
    expect(screen.getByText(/ikinci/)).toBeTruthy();
  });

  it("ok ile sonraki fotoğrafa geçer", async () => {
    await open("1_a.png");

    fireEvent.click(screen.getByText("›"));

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/0_a.png");
  });

  it("ilk fotoğrafta geri oku çalışmaz", async () => {
    await open("2_a.png");

    fireEvent.click(screen.getByText("‹"));

    expect(navigate).not.toHaveBeenCalled();
  });

  it("klavye okları ve Esc çalışır", async () => {
    await open("1_a.png");

    fireEvent.keyDown(window, { key: "ArrowLeft" });
    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/2_a.png");

    fireEvent.keyDown(window, { key: "Escape" });
    expect(navigate).toHaveBeenCalledWith("/projects/düğün");
  });

  it("silme önce onay ister, sonra sonraki fotoğrafı açar", async () => {
    deletePhoto.mockResolvedValue(null);
    await open("1_a.png");

    fireEvent.click(screen.getByText("Sil"));
    expect(screen.getByText("Bu fotoğraf silinsin mi?")).toBeTruthy();
    expect(deletePhoto).not.toHaveBeenCalled();

    // The modal's own Sil is the second one on screen (the panel's is the first).
    const confirm = screen.getAllByText("Sil").at(-1);
    await act(async () => { fireEvent.click(confirm); });

    expect(deletePhoto).toHaveBeenCalledWith("düğün", "1_a.png");
    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/0_a.png");
  });

  it("son fotoğraf silinince öncekine döner", async () => {
    deletePhoto.mockResolvedValue(null);
    await open("0_a.png");

    fireEvent.click(screen.getByText("Sil"));
    await act(async () => { fireEvent.click(screen.getAllByText("Sil").at(-1)); });

    expect(navigate).toHaveBeenCalledWith("/projects/düğün/photos/1_a.png");
  });

  it("listede olmayan dosya için hata kartı gösterir", async () => {
    await open("yok.png");

    expect(screen.getByText("Fotoğraf bulunamadı")).toBeTruthy();
  });
});
```

`Gallery.test.jsx`'e:

```jsx
  it("kareye tıklayınca detay sayfasına gider", () => {
    render(<Gallery project="düğün" photos={PHOTOS} current={null} onReorder={() => {}} />);

    const link = screen.getByText("2_a.png").closest("[draggable]").querySelector("a");
    expect(link.getAttribute("href")).toBe(
      `/projects/${encodeURIComponent("düğün")}/photos/2_a.png`);
  });
```

- [ ] **Step 2: Koştur, düştüğünü gör** → FAIL.

- [ ] **Step 3: `PhotoDeleteModal.jsx`'i yaz**

```jsx
import { useEffect } from "react";

import { Btn, Note } from "../../vendor/kit.jsx";

// Artboard: the design's delete confirm, worded for one photo. Written once for this screen --
// Part 12 brings three more confirms, and that is when a shared component earns its place.
export default function PhotoDeleteModal({ onCancel, onConfirm, busy }) {
  useEffect(() => {
    const onKey = (e) => { if (e.key === "Escape" && !busy) onCancel(); };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel, busy]);

  return (
    <div className="wf-scrim" onClick={busy ? undefined : onCancel}>
      <div className="wf-card wf-card--shadow" onClick={(e) => e.stopPropagation()}
           style={{ width: 320, padding: 18, display: "flex", flexDirection: "column", gap: 10 }}>
        <Note size={14}>Bu fotoğraf silinsin mi?</Note>
        <Note size={12} style={{ color: "var(--ink-2)" }}>Bu işlem geri alınamaz.</Note>
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 4 }}>
          <Btn sm ghost onClick={onCancel} disabled={busy}>Vazgeç</Btn>
          <Btn sm onClick={onConfirm} disabled={busy}
               style={{ background: "var(--danger)", borderColor: "var(--danger)", color: "#fff" }}>
            {busy ? "Siliniyor…" : "Sil"}
          </Btn>
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 4: `PhotoDetail.jsx`'i yaz**

```jsx
import { useEffect, useState } from "react";

import { photoUrl } from "../../shared/api.js";
import { navigate, photoPath, projectPath } from "../../shared/router.js";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Btn, Hand, Icon, Mono, Note } from "../../vendor/kit.jsx";
import PhotoDeleteModal from "./PhotoDeleteModal.jsx";
import { usePhotos } from "./usePhotos.js";

const HEADER = {
  display: "grid", gridTemplateColumns: "1fr auto 1fr", alignItems: "center",
  padding: "14px 32px", background: "var(--bg-2)", borderBottom: "1px solid var(--border)",
};
const STAGE = {
  flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: 24,
  position: "relative", background: "var(--bg)",
};
// The design's arrows: plain glyphs at the two ends of the photo area, glowing enough to stay
// legible over any photo.
const ARROW = {
  position: "absolute", top: "50%", transform: "translateY(-50%)", color: "#fff", fontSize: 44,
  lineHeight: 1, fontWeight: 300, textShadow: "0 0 4px rgba(0,0,0,.9), 0 2px 8px rgba(0,0,0,.7)",
  userSelect: "none",
};
const SIDE = {
  width: 300, flexShrink: 0, borderLeft: "1px solid var(--border)", padding: 16,
  display: "flex", flexDirection: "column", gap: 14, boxSizing: "border-box", minHeight: 0,
};
const LABEL = { color: "var(--ink-3)", letterSpacing: ".08em", textTransform: "uppercase" };

function Arrow({ glyph, side, onClick }) {
  const enabled = Boolean(onClick);
  return (
    <div role="button" onClick={onClick}
         style={{ ...ARROW, [side]: 20, cursor: enabled ? "pointer" : "default",
                  opacity: enabled ? 1 : 0.25 }}>
      {glyph}
    </div>
  );
}

// Artboard 10: the photo as large as it fits, at its own aspect ratio, between two arrows; the
// 300px column on the right says where it sits, what it is called and what made it.
export default function PhotoDetail({ project, file }) {
  const { photos, error, remove } = usePhotos(project);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);

  const index = photos ? photos.findIndex((photo) => photo.file === file) : -1;
  const current = index >= 0 ? photos[index] : null;
  const previous = index > 0 ? photos[index - 1] : null;
  const next = photos && index >= 0 && index < photos.length - 1 ? photos[index + 1] : null;

  useEffect(() => {
    const onKey = (e) => {
      if (confirming) return;                       // the modal owns the keyboard while it is open
      if (e.key === "Escape") navigate(projectPath(project));
      if (e.key === "ArrowLeft" && previous) navigate(photoPath(project, previous.file));
      if (e.key === "ArrowRight" && next) navigate(photoPath(project, next.file));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [project, previous, next, confirming]);

  function handleDelete() {
    setBusy(true);
    // Where to go afterwards is decided from the list we already have: the next photo, or the one
    // before it when this was the last, or back to the gallery when nothing is left.
    const after = next || previous;
    remove(file).then(() => {
      setBusy(false);
      setConfirming(false);
      navigate(after ? photoPath(project, after.file) : projectPath(project));
    });
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={HEADER}>
        <Hand size={20}><span className="wf-hl">Queen Editor</span></Hand>
        <Hand size={20}>{project}</Hand>
        <Btn ghost style={{ justifySelf: "end" }} onClick={() => navigate(projectPath(project))}>
          <Icon.Left /> Galeriye dön
        </Btn>
      </div>

      {photos === null ? (
        <div style={{ ...STAGE }}><span className="wf-spinner" /></div>
      ) : !current ? (
        <div style={{ ...STAGE, flexDirection: "column", gap: 12 }}>
          <StatusErrorCard text="Fotoğraf bulunamadı" raw={error || file} />
        </div>
      ) : (
        <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
          <div style={STAGE}>
            <Arrow glyph="‹" side="left"
                   onClick={previous ? () => navigate(photoPath(project, previous.file)) : undefined} />
            <Arrow glyph="›" side="right"
                   onClick={next ? () => navigate(photoPath(project, next.file)) : undefined} />
            {/* contain, not a fixed ratio: the server does not know the photo's shape, and the
                design's rule is that it is never cropped. 120px is the design's own arrow gutter. */}
            <img src={photoUrl(project, current.file)} alt={current.file}
                 style={{ maxWidth: "calc(100% - 120px)", maxHeight: "100%", width: "auto",
                          height: "auto", objectFit: "contain", display: "block" }} />
          </div>

          <div style={SIDE}>
            <div style={{ display: "flex", gap: 24 }}>
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                <Mono size={10} style={LABEL}>Sıra</Mono>
                <Mono size={13} style={{ color: "var(--ink)" }}>{index + 1} / {photos.length}</Mono>
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                <Mono size={10} style={LABEL}>Dosya adı</Mono>
                <Mono size={13} style={{ color: "var(--ink)" }}>{current.file}</Mono>
              </div>
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1, minHeight: 0 }}>
              <Mono size={10} style={LABEL}>Prompt</Mono>
              <div className="wf-stroke"
                   style={{ flex: 1, minHeight: 0, overflowY: "auto", padding: 10 }}>
                <Note size={12} style={{ color: "var(--ink-2)", display: "block",
                                         lineHeight: 1.6 }}>
                  {current.prompt}
                </Note>
              </div>
            </div>

            {error && <StatusErrorCard text="Fotoğraf silinemedi" raw={error} />}

            <Btn sm onClick={() => setConfirming(true)}
                 style={{ color: "var(--danger)", borderColor: "var(--danger)",
                          justifyContent: "center" }}>
              <Icon.Trash /> Sil
            </Btn>
          </div>
        </div>
      )}

      {confirming && (
        <PhotoDeleteModal busy={busy} onCancel={() => setConfirming(false)}
                          onConfirm={handleDelete} />
      )}
    </div>
  );
}
```

- [ ] **Step 5: Galeriyi bağla** (`Gallery.jsx`)

`photoUrl` bağlantısı detay sayfasına çevrilir; import satırına `navigate, photoPath` eklenir:

```jsx
                  {/* A real link so middle-click opens a tab, but a normal click stays in the app
                      instead of reloading the whole page. A drag never produces a click. */}
                  <a href={photoPath(project, photo.file)}
                     onClick={(e) => { e.preventDefault(); navigate(photoPath(project, photo.file)); }}
                     draggable={false}>
```

- [ ] **Step 6: `App.jsx`'e detay dalını ekle**

```jsx
import PhotoDetail from "./features/photo_generation/PhotoDetail.jsx";
```

```jsx
  if (photo) return <PhotoDetail project={project} file={photo} />;
```

- [ ] **Step 7: Koştur** → `npm test` PASS.

### Task 8: Kapanış

- [ ] **Step 1: Bozma turu**

`PhotoDetail.jsx`'te `Arrow`'un `onClick` koşulunu (`previous ? … : undefined`) geçici olarak
koşulsuz yap → **"ilk fotoğrafta geri oku çalışmaz"** testi FAIL etmeli. Geri al.

- [ ] **Step 2: Tüm testler + build**

Run: `python -m pytest -q` (`queen-editor/`) → PASS
Run: `npm test` (`queen-editor/frontend/`) → PASS
Run: `npm run build` → temiz.

- [ ] **Step 3: Commit + push**

Mesaj dosyadan verilir (PowerShell `<` karakterini yönlendirme sanıyor):
`feat(queen-editor): Bölüm 11 — foto detay sayfası + tek foto silme`

## Bulgu defteri

- **Planın öngördüğü kural gerçekten gerekliydi:** `next_number`'ın eski dokümantasyonu "kayda
  bakmaya gerek yok" diyordu; silme bu varsayımı bozuyor. Kural üç kaynağa çıkarıldı ve
  dokümantasyon aynı commit'te düzeltildi. Rota testi bunu uçtan uca kanıtlıyor
  (`test_a_photo_produced_after_a_delete_does_not_reuse_the_number`).
- **Task 4'ün testleri kodla birlikte yazıldı** (rota + test aynı turda), TDD'nin kırmızı adımı
  yalnız use case seviyesinde görüldü. Kapanış bozma turu bu boşluğu kapattı: pasif ok koruması
  kaldırılınca ilgili test düştü, geri alındı.
- Backend 227, frontend 44 test yeşil; `dist/` yenilendi.
