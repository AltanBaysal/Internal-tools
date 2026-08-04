# Bölüm 9 — Galeri Sıralama Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kullanıcı galeriyi sürükle-bırakla sıralar, sıra Drive'da kalıcıdır ve yeni üretilen fotoğraflar bu sıranın en üstüne düşer.

**Architecture:** Sıra proje klasöründe dördüncü bir dosyada (`order.json`) durur; `photos.jsonl` yalnız-ekleme kalır. Uzlaştırma (kayıt + sıra → galeri listesi) domain'de saf bir fonksiyondur, `list_photos` onu kullanır. Yeni uç `PUT /api/projects/<p>/order` kaydeder ve sakladığı listeyi döner. Frontend'de galeri HTML5 sürükle-bırakla sıralanır, iyimser günceller, hata olursa sunucunun gerçeğine döner.

**Tech Stack:** Flask (sync) + pytest · React 18 + vitest/jsdom · JSON dosyaları `DriveStorage` üzerinden.

**Spec:** [2026-08-05-queen-editor-bolum9-galeri-siralama-design.md](../specs/2026-08-05-queen-editor-bolum9-galeri-siralama-design.md)

## Global Constraints

- **TDD:** her davranış için önce düşen test, sonra kod. Test önce koşturulup **düştüğü görülmeden** kod yazılmaz.
- **Commit:** bölüm sonunda tek commit + push (bu koşuda kullanıcı ara test yapmıyor; Colab testi push edilmiş kod ister).
- **Katman kuralları** (CODE-STANDARD): `domain/` saf kalır — `flask`, dosya adı, JSON şeması bilmez. Dosya adını ve şemayı yalnız `data/` bilir. `presentation/` çeviri yapar, kural taşımaz.
- **Kullanıcıya görünen metin Türkçe**, kod yorumları/dokümanlar İngilizce.
- **Hata mesajı uydurulmaz:** sunucunun/işletim sisteminin kendi metni basılır.
- **Tasarım değerleri birebir** (spec §4): rozet `top:6 right:6`, `rgba(10,8,7,.75)`, `var(--ink-2)`, `Mono size={10}`, `padding:"2px 6px"`, `borderRadius:3`, `zIndex:1`; sürüklenen kare `rotate(-3deg) scale(1.04) translate(14px, -10px)` + `drop-shadow(0 12px 24px rgba(0,0,0,.55))` + `zIndex:5`; bırakma yuvası `2px dashed var(--accent)`, `borderRadius:4`, zemin `var(--bg-3)`.
- **`npm run build` bölüm sonunda koşar ve `dist/` aynı commit'e girer** (Colab derleme yapmaz).
- Dosyalar CRLF satır sonlarıyla kalır.

---

### Task 1: Uzlaştırma kuralı (domain, saf fonksiyon)

**Files:**
- Create: `queen-editor/backend/features/photo_generation/domain/gallery_order.py`
- Test: `queen-editor/backend/tests/test_gallery_order.py`

**Interfaces:**
- Produces: `apply_order(rows: list[dict], order: list[str]) -> list[dict]` — `rows` kaydın verdiği sıradadır (en yeni önce), `order` saklanan dosya adı listesidir. Task 2 ve 3 bunu kullanır.

- [ ] **Step 1: Testi yaz**

```python
from backend.features.photo_generation.domain.gallery_order import apply_order


def rows(*files):
    return [{"file": f, "prompt": "p"} for f in files]


def files(result):
    return [row["file"] for row in result]


def test_sirasiz_kayit_kendi_sirasinda_kalir():
    assert files(apply_order(rows("2_a.png", "1_a.png"), [])) == ["2_a.png", "1_a.png"]


def test_saklanan_sira_uygulanir():
    result = apply_order(rows("2_a.png", "1_a.png", "0_a.png"),
                         ["0_a.png", "2_a.png", "1_a.png"])
    assert files(result) == ["0_a.png", "2_a.png", "1_a.png"]


def test_sirada_olmayan_yeni_fotograflar_en_uste_gelir():
    # The record is newest-first, so 4_a is newer than 3_a and stays above it.
    result = apply_order(rows("4_a.png", "3_a.png", "1_a.png", "0_a.png"),
                         ["0_a.png", "1_a.png"])
    assert files(result) == ["4_a.png", "3_a.png", "0_a.png", "1_a.png"]


def test_kayitta_olmayan_ad_yok_sayilir():
    result = apply_order(rows("1_a.png"), ["silinmis.png", "1_a.png"])
    assert files(result) == ["1_a.png"]


def test_ayni_ad_iki_kez_gecerse_bir_kez_dizilir():
    result = apply_order(rows("1_a.png", "0_a.png"), ["1_a.png", "1_a.png", "0_a.png"])
    assert files(result) == ["1_a.png", "0_a.png"]


def test_bos_kayit_bos_doner():
    assert apply_order([], ["1_a.png"]) == []
```

- [ ] **Step 2: Testi koştur, düştüğünü gör**

Run: `python -m pytest backend/tests/test_gallery_order.py -q` (`queen-editor/` içinde)
Expected: FAIL — `ModuleNotFoundError: backend.features.photo_generation.domain.gallery_order`

- [ ] **Step 3: Fonksiyonu yaz**

```python
"""The gallery's order: the record says what exists, the order file says in what sequence.

Kept as a pure function so the rule is testable without Drive: it can neither invent a photo nor
hide one -- whatever the order file says, the result is always exactly the record's own set.
"""


def apply_order(rows, order):
    """rows: record rows, newest first. order: stored file names. Returns rows in gallery order."""
    by_file = {row["file"]: row for row in rows}
    ordered = []
    seen = set()
    for file in order:
        row = by_file.get(file)
        if row is not None and file not in seen:
            seen.add(file)
            ordered.append(row)
    # A photo the order file has never heard of is new: it belongs on top, and among themselves
    # those keep the record's own newest-first sequence.
    fresh = [row for row in rows if row["file"] not in seen]
    return fresh + ordered
```

- [ ] **Step 4: Testi koştur**

Run: `python -m pytest backend/tests/test_gallery_order.py -q`
Expected: 6 passed.

### Task 2: `order.json` deposu (data) + port

**Files:**
- Create: `queen-editor/backend/features/photo_generation/data/order_store.py`
- Modify: `queen-editor/backend/features/photo_generation/domain/ports.py` (yeni `OrderStore` protokolü)
- Test: `queen-editor/backend/tests/test_order_store.py`

**Interfaces:**
- Produces: `DriveOrderStore(storage)` → `read(project) -> list[str]`, `write(project, order: list[str]) -> None`. Port adı `OrderStore`. Task 3 ve 4 bunu kullanır.

- [ ] **Step 1: Testi yaz**

Mevcut `test_settings_store.py`'ın sahte depolama desenini izler (aynı dosyayı aç ve oradaki `FakeStorage`'ı örnek al; aşağıdaki sahte bu test dosyasının kendi içinde durur):

```python
import json

from backend.features.photo_generation.data.order_store import FILE, DriveOrderStore


class FakeStorage:
    def __init__(self, texts=None):
        self.texts = dict(texts or {})

    def read_text(self, subdir, name):
        return self.texts.get((subdir, name))

    def write_text(self, subdir, name, text):
        self.texts[(subdir, name)] = text


def test_dosya_yoksa_sira_bos():
    assert DriveOrderStore(FakeStorage()).read("düğün") == []


def test_yazilan_sira_geri_okunur():
    storage = FakeStorage()
    store = DriveOrderStore(storage)
    store.write("düğün", ["1_a.png", "0_a.png"])
    assert store.read("düğün") == ["1_a.png", "0_a.png"]


def test_turkce_adlar_kacissiz_yazilir():
    storage = FakeStorage()
    DriveOrderStore(storage).write("düğün", ["0_a.png"])
    assert "düğün" not in storage.texts[("düğün", FILE)]  # project name is not in the file
    assert json.loads(storage.texts[("düğün", FILE)]) == {"order": ["0_a.png"]}


def test_bozuk_json_sirasiz_sayilir():
    storage = FakeStorage({("düğün", FILE): "{yarım"})
    assert DriveOrderStore(storage).read("düğün") == []


def test_beklenmedik_bicim_sirasiz_sayilir():
    storage = FakeStorage({("düğün", FILE): json.dumps({"order": "1_a.png"})})
    assert DriveOrderStore(storage).read("düğün") == []


def test_metin_olmayan_ogeler_atilir():
    storage = FakeStorage({("düğün", FILE): json.dumps({"order": ["1_a.png", 5, None]})})
    assert DriveOrderStore(storage).read("düğün") == ["1_a.png"]
```

- [ ] **Step 2: Koştur, düştüğünü gör**

Run: `python -m pytest backend/tests/test_order_store.py -q`
Expected: FAIL — modül yok.

- [ ] **Step 3: Depoyu yaz**

`data/order_store.py`:

```python
"""OrderStore over DriveStorage -- the only place that knows the order file's name and shape.

Unreadable is not an error: a missing, half-written or hand-edited file means "no manual order",
and the gallery falls back to the record's own sequence. A project must never fail to open because
of the file that only decides sequence.
"""
import json

FILE = "order.json"


class DriveOrderStore:
    def __init__(self, storage):
        self._storage = storage

    def read(self, project):
        raw = self._storage.read_text(project, FILE)
        if raw is None:
            return []
        try:
            data = json.loads(raw)
        except ValueError:
            return []
        if not isinstance(data, dict):
            return []
        order = data.get("order")
        if not isinstance(order, list):
            return []
        return [name for name in order if isinstance(name, str)]

    def write(self, project, order):
        self._storage.write_text(
            project, FILE, json.dumps({"order": order}, ensure_ascii=False, indent=2))
```

- [ ] **Step 4: Portu ekle**

`domain/ports.py`'ın sonuna:

```python
class OrderStore(Protocol):
    def read(self, project: str) -> list:
        """The stored gallery order as file names; empty when there is none."""
        ...

    def write(self, project: str, order: list) -> None:
        """Replace the project's gallery order."""
        ...
```

- [ ] **Step 5: Koştur**

Run: `python -m pytest backend/tests/test_order_store.py -q`
Expected: 6 passed.

### Task 3: `list_photos` sıraya uyar + `save_order` use case

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/list_photos.py`
- Create: `queen-editor/backend/features/photo_generation/domain/usecases/save_order.py`
- Modify: `queen-editor/backend/backend/tests/test_photo_usecases.py` → doğrusu: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Consumes: `apply_order` (Task 1), `OrderStore` portu (Task 2).
- Produces: `list_photos(record, store, order_store, project)` — **imza değişti**, `main.py` güncellenecek (Task 5). `save_order(record, store, order_store, project, order) -> list[str]`; geçersiz gövde için `InvalidOrder` istisnası.

- [ ] **Step 1: Testleri yaz** (`test_photo_usecases.py`'ın sonuna ekle)

Dosyanın başındaki import bloğuna eklenecekler:

```python
from backend.features.photo_generation.domain.usecases.save_order import InvalidOrder, save_order
```

Mevcut `FakeRecord` sınıfının yanına yeni sahte ve testler:

```python
class FakeOrderStore:
    def __init__(self, order=()):
        self.order = list(order)

    def read(self, project):
        return list(self.order)

    def write(self, project, order):
        self.order = list(order)


def test_galeri_saklanan_siraya_uyar():
    record = FakeRecord(rows=[{"file": "2_a.png"}, {"file": "1_a.png"}, {"file": "0_a.png"}])
    order = FakeOrderStore(["0_a.png", "2_a.png", "1_a.png"])
    result = list_photos(record, FakeStore(), order, "düğün")
    assert [row["file"] for row in result] == ["0_a.png", "2_a.png", "1_a.png"]


def test_galeri_olmayan_projede_patlar():
    with pytest.raises(ProjectMissing):
        list_photos(FakeRecord(rows=[]), FakeStore(projects=()), FakeOrderStore(), "yok")


def test_sira_kaydedilir_ve_saklanan_liste_doner():
    record = FakeRecord(rows=[{"file": "1_a.png"}, {"file": "0_a.png"}])
    order = FakeOrderStore()
    saved = save_order(record, FakeStore(), order, "düğün", ["0_a.png", "1_a.png"])
    assert saved == ["0_a.png", "1_a.png"]
    assert order.order == ["0_a.png", "1_a.png"]


def test_kayitta_olmayan_ad_kaydedilmeden_suzulur():
    record = FakeRecord(rows=[{"file": "1_a.png"}])
    order = FakeOrderStore()
    saved = save_order(record, FakeStore(), order, "düğün", ["hayalet.png", "1_a.png"])
    assert saved == ["1_a.png"]
    assert order.order == ["1_a.png"]


def test_liste_olmayan_sira_reddedilir():
    with pytest.raises(InvalidOrder):
        save_order(FakeRecord(rows=[]), FakeStore(), FakeOrderStore(), "düğün", "1_a.png")


def test_metin_olmayan_oge_reddedilir():
    with pytest.raises(InvalidOrder):
        save_order(FakeRecord(rows=[]), FakeStore(), FakeOrderStore(), "düğün", ["1_a.png", 7])


def test_sira_kaydi_olmayan_projede_patlar():
    with pytest.raises(ProjectMissing):
        save_order(FakeRecord(rows=[]), FakeStore(projects=()), FakeOrderStore(), "yok", [])
```

**Not:** `FakeRecord`'un mevcut hâli bu testlerin ihtiyacını karşılamıyorsa (satır listesi
döndürmüyorsa), dosyadaki `FakeRecord`'a `rows` parametresi eklenir ve `list` metodu onu döner —
mevcut testlerin kullandığı davranış korunur.

- [ ] **Step 2: Koştur, düştüğünü gör**

Run: `python -m pytest backend/tests/test_photo_usecases.py -q`
Expected: FAIL (import hatası + imza uyuşmazlığı).

- [ ] **Step 3: `list_photos`'u güncelle**

```python
"""The gallery's list: the photos the record says exist, in the user's own order.

The folder is not scanned. A row is appended only after its photo is written, so the record is the
list -- and it carries the metadata the gallery's later features (export, detail) need, which a
directory listing cannot. The order file only sequences that list; it can neither add nor hide one.
"""
from backend.features.photo_generation.domain.gallery_order import apply_order
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


def list_photos(record, store, order_store, project):
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    return apply_order(record.list(project), order_store.read(project))
```

- [ ] **Step 4: `save_order`'ı yaz**

```python
"""Save the gallery order the user dragged into place.

The client's list is filtered against the record before it is stored: the server writes only names
it can see itself, so a stale tab cannot leave ghosts in the file. Missing names are not an error --
a photo the list forgot simply comes back on top on the next read (see gallery_order.apply_order).
"""
from backend.features.photo_generation.domain.usecases.start_batch import ProjectMissing


class InvalidOrder(Exception):
    """The body was not a list of file names."""


def save_order(record, store, order_store, project, order):
    if not isinstance(order, list) or any(not isinstance(name, str) for name in order):
        raise InvalidOrder("Sıra listesi metin dizisi olmalı.")
    if not store.project_exists(project):
        raise ProjectMissing(f"Proje yok: {project}")
    known = {row["file"] for row in record.list(project)}
    cleaned = []
    seen = set()
    for name in order:
        if name in known and name not in seen:
            seen.add(name)
            cleaned.append(name)
    order_store.write(project, cleaned)
    return cleaned
```

- [ ] **Step 5: Koştur**

Run: `python -m pytest backend/tests/test_photo_usecases.py -q`
Expected: hepsi PASS.

### Task 4: `PUT /api/projects/<p>/order` ucu

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/presentation/routes.py`
- Test: `queen-editor/backend/tests/test_photo_routes.py`

**Interfaces:**
- Consumes: `save_order` use case (Task 3).
- Produces: `make_photo_generation_blueprint(..., save_order=…)` — yeni parametre; `main.py` (Task 5) bağlar.

- [ ] **Step 1: Testleri yaz** (`test_photo_routes.py`'a ekle; dosyadaki mevcut uygulama kurma deseni aynen kullanılır)

```python
def test_sira_kaydedilir(client_with):
    client = client_with(save_order=lambda project, order: order)
    resp = client.put("/api/projects/düğün/order", json={"order": ["1_a.png", "0_a.png"]})
    assert resp.status_code == 200
    assert resp.get_json() == {"order": ["1_a.png", "0_a.png"]}


def test_gecersiz_sira_400_doner(client_with):
    def boom(project, order):
        raise InvalidOrder("Sıra listesi metin dizisi olmalı.")

    client = client_with(save_order=boom)
    resp = client.put("/api/projects/düğün/order", json={"order": "1_a.png"})
    assert resp.status_code == 400
    assert resp.get_json()["error"] == "Sıra listesi metin dizisi olmalı."


def test_olmayan_projede_sira_404_doner(client_with):
    def boom(project, order):
        raise ProjectMissing("Proje yok: yok")

    client = client_with(save_order=boom)
    resp = client.put("/api/projects/yok/order", json={"order": []})
    assert resp.status_code == 404
```

**Not:** `test_photo_routes.py`'da uygulamayı kuran mevcut yardımcı hangi biçimdeyse (fixture ya da
düz fonksiyon), bu testler onu kullanır — yukarıdaki `client_with` adı o yardımcının adıyla
değiştirilir ve `save_order` yeni parametre olarak eklenir. Yeni bir kurulum deseni icat edilmez.

- [ ] **Step 2: Koştur, düştüğünü gör**

Run: `python -m pytest backend/tests/test_photo_routes.py -q`
Expected: FAIL — `save_order` parametresi yok / 404 döner.

- [ ] **Step 3: Rotayı ekle**

`routes.py`'da import satırına:

```python
from backend.features.photo_generation.domain.usecases.save_order import InvalidOrder
```

İmza: `def make_photo_generation_blueprint(start_batch, get_status, stop_generation, list_photos, save_order, photo_dir):`

`photos` rotasının hemen altına:

```python
    @bp.put("/api/projects/<project>/order")
    def put_order(project):
        body = request.get_json(silent=True) or {}
        try:
            # The stored list goes back so the client sees what was kept, not what it guessed.
            return jsonify({"order": save_order(project, body.get("order"))})
        except InvalidOrder as exc:
            return jsonify({"error": str(exc)}), 400
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
```

- [ ] **Step 4: Koştur**

Run: `python -m pytest backend/tests/test_photo_routes.py -q`
Expected: hepsi PASS.

### Task 5: Bileşim kökü — yeni depo ve use case bağlanır

**Files:**
- Modify: `queen-editor/backend/main.py`

**Interfaces:**
- Consumes: Task 2-4'ün çıktıları.
- Produces: çalışan uygulama.

- [ ] **Step 1: `main.py`'ı güncelle**

Import bloğuna:

```python
from backend.features.photo_generation.data.order_store import DriveOrderStore
from backend.features.photo_generation.domain.usecases.save_order import save_order
```

Depo satırlarının yanına (`_plan_store` altına):

```python
_order_store = DriveOrderStore(_storage)
```

Blueprint çağrısında `list_photos` satırı değişir ve `save_order` eklenir:

```python
    list_photos=partial(list_photos, _photo_record, _photo_store, _order_store),
    save_order=partial(save_order, _photo_record, _photo_store, _order_store),
```

- [ ] **Step 2: Tüm backend paketini koştur**

Run: `python -m pytest -q` (`queen-editor/` içinde)
Expected: hepsi PASS (mevcut 181 + yeni testler). Kırmızı kalan varsa imza değişikliğinin dokunduğu yer düzeltilir.

### Task 6: Frontend — `saveOrder` istemcisi ve `useGeneration.reorder`

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js`
- Modify: `queen-editor/frontend/src/features/photo_generation/useGeneration.js`
- Test: `queen-editor/frontend/src/shared/api.test.js` (ekleme)
- Test: `queen-editor/frontend/src/features/photo_generation/useGeneration.test.jsx` (ekleme)

**Interfaces:**
- Produces: `saveOrder(project, order) -> Promise<{order: string[]}>`; `useGeneration` artık `reorder(files)` da döner (Task 7 kullanır).

- [ ] **Step 1: `api.test.js`'e testi ekle**

```js
  it("sırayı PUT ile gönderir", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ order: ["1_a.png"] }));
    vi.stubGlobal("fetch", fetchMock);

    await saveOrder("düğün", ["1_a.png"]);

    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe(`/api/projects/${encodeURIComponent("düğün")}/order`);
    expect(options.method).toBe("PUT");
    expect(JSON.parse(options.body)).toEqual({ order: ["1_a.png"] });
  });
```

Import satırına `saveOrder` eklenir.

- [ ] **Step 2: `useGeneration.test.jsx`'e testleri ekle**

`vi.mock` bloğuna `saveOrder: vi.fn(),` eklenir ve import satırına `saveOrder` girer.

```js
  it("sürükleme sonrası yeni sırayı beklemeden gösterir ve sunucuya yazar", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listPhotos.mockResolvedValue([{ file: "1_a.png" }, { file: "0_a.png" }]);
    saveOrder.mockResolvedValue({ order: ["0_a.png", "1_a.png"] });

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    await act(async () => { await result.current.reorder(["0_a.png", "1_a.png"]); });

    expect(result.current.photos.map((p) => p.file)).toEqual(["0_a.png", "1_a.png"]);
    expect(saveOrder).toHaveBeenCalledWith("düğün", ["0_a.png", "1_a.png"]);
  });

  it("sıra kaydedilemezse hatayı gösterir ve sunucunun sırasına döner", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listPhotos.mockResolvedValue([{ file: "1_a.png" }, { file: "0_a.png" }]);
    saveOrder.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nkopuk"));

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    await act(async () => { await result.current.reorder(["0_a.png", "1_a.png"]); });

    expect(result.current.error).toContain("Sıra kaydedilemedi");
    expect(result.current.photos.map((p) => p.file)).toEqual(["1_a.png", "0_a.png"]);
  });

  it("sıra kaydedilirken gelen poll cevabı sırayı geri sektirmez", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listPhotos.mockResolvedValue([{ file: "1_a.png" }, { file: "0_a.png" }]);
    let finishSave;
    saveOrder.mockReturnValue(new Promise((resolve) => { finishSave = resolve; }));

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    act(() => { result.current.reorder(["0_a.png", "1_a.png"]); });
    await settle(2000);   // a poll lands mid-save with the server's old order

    expect(result.current.photos.map((p) => p.file)).toEqual(["0_a.png", "1_a.png"]);

    await act(async () => { finishSave({ order: ["0_a.png", "1_a.png"] }); });
  });
```

- [ ] **Step 3: Koştur, düştüğünü gör**

Run: `npm test` (`queen-editor/frontend/` içinde)
Expected: 4 yeni test FAIL (`saveOrder` yok, `reorder` yok).

- [ ] **Step 4: `api.js`'e `saveOrder`'ı ekle**

`stopGeneration` ile `listPhotos` arasına:

```js
export async function saveOrder(project, order) {
  return request(`/api/projects/${encodeURIComponent(project)}/order`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ order }),
  });
}
```

- [ ] **Step 5: `useGeneration`'a `reorder`'ı ekle**

Import satırına `saveOrder` eklenir. Diğer `useRef`'lerin yanına:

```js
  // While a drag is being saved the gallery on screen is ahead of the server: a poll's older list
  // would snap the tiles back for one frame and then forward again.
  const savingOrder = useRef(false);
```

`refreshPhotos` şu hâle gelir:

```js
  const refreshPhotos = useCallback(() => {
    listPhotos(project)
      .then((data) => { if (alive.current && !savingOrder.current) setPhotos(data); })
      .catch((err) => { if (alive.current) setError(err.message); });
  }, [project]);
```

`stop`'un altına:

```js
  // Optimistic: the tiles move the moment they are dropped, because the drag already showed the
  // user where they land. If the write fails we say so and put the server's own order back --
  // the screen never keeps an order the server does not have.
  const reorder = useCallback(
    (files) => {
      savingOrder.current = true;
      setPhotos((current) => {
        if (!current) return current;
        const byFile = new Map(current.map((photo) => [photo.file, photo]));
        return files.map((file) => byFile.get(file)).filter(Boolean);
      });
      return saveOrder(project, files)
        .then(() => { savingOrder.current = false; })
        .catch((err) => {
          savingOrder.current = false;
          if (!alive.current) return;
          setError(`Sıra kaydedilemedi.\n${err.message}`);
          refreshPhotos();
        });
    },
    [project, refreshPhotos],
  );
```

Döndürülen nesne: `return { job, photos, error, stopping, generate, stop, reorder };`

- [ ] **Step 6: Koştur**

Run: `npm test`
Expected: hepsi PASS.

### Task 7: Galeri — rozet, sürükle-bırak, yuva

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`
- Test: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx` (yeni)

**Interfaces:**
- Consumes: `useGeneration`'ın `reorder`'ı (Task 6).
- Produces: `Gallery({ project, photos, current, onReorder })`.

- [ ] **Step 1: Testi yaz**

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import Gallery from "./Gallery.jsx";

const PHOTOS = [{ file: "2_a.png" }, { file: "1_a.png" }, { file: "0_a.png" }];

function dragTile(from, to) {
  // jsdom has no DataTransfer, so the component must not depend on one: it tracks the dragged
  // index in its own state, exactly as a keyboard-free HTML5 drag does.
  fireEvent.dragStart(from);
  fireEvent.dragOver(to);
  fireEvent.drop(to);
}

describe("Gallery sıralama", () => {
  it("her kareye sıra rozetini basar", () => {
    render(<Gallery project="düğün" photos={PHOTOS} current={null} onReorder={() => {}} />);

    expect(screen.getByText("1")).toBeTruthy();
    expect(screen.getByText("2")).toBeTruthy();
    expect(screen.getByText("3")).toBeTruthy();
  });

  it("kare bırakıldığında yeni sırayı bildirir", () => {
    const onReorder = vi.fn();
    render(<Gallery project="düğün" photos={PHOTOS} current={null} onReorder={onReorder} />);

    dragTile(screen.getByText("0_a.png"), screen.getByText("2_a.png"));

    expect(onReorder).toHaveBeenCalledWith(["0_a.png", "2_a.png", "1_a.png"]);
  });

  it("aynı yere bırakılan kare için sunucuya gitmez", () => {
    const onReorder = vi.fn();
    render(<Gallery project="düğün" photos={PHOTOS} current={null} onReorder={onReorder} />);

    dragTile(screen.getByText("1_a.png"), screen.getByText("1_a.png"));

    expect(onReorder).not.toHaveBeenCalled();
  });

  it("üretilen kare rozet almaz", () => {
    render(<Gallery project="düğün" photos={PHOTOS} onReorder={() => {}}
                    current={{ number: 3, letter: "a", prompt: "p" }} />);

    // Three photos, three badges -- the spinner tile is not in the record and has no place yet.
    expect(screen.queryByText("4")).toBeNull();
  });
});
```

Not: `dragStart`/`drop` olayları karenin **kendisine** değil, testte tutulan dosya adı etiketinin
üstünden bulunacak kareye gider — bileşen sürükleme işleyicilerini kare sarmalayıcısına koyar,
`fireEvent` olayı yukarı baloncuklar. Etiketten kareye çıkmak gerekiyorsa testte
`closest("[draggable]")` kullanılır.

- [ ] **Step 2: Koştur, düştüğünü gör**

Run: `npm test`
Expected: 4 test FAIL.

- [ ] **Step 3: `Gallery.jsx`'i yaz**

```jsx
import { useState } from "react";

import { photoUrl } from "../../shared/api.js";
import { ImgPH, Mono, Note } from "../../vendor/kit.jsx";

const PAD = { padding: 16 };
const GRID = { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12,
               alignItems: "start" };
const EMPTY = {
  minHeight: "60vh",
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: 8,
};
// Artboard 05: the badge sits on the photo itself, always visible, never on the caption line.
const BADGE = { position: "absolute", top: 6, right: 6, background: "rgba(10,8,7,.75)",
                color: "var(--ink-2)", padding: "2px 6px", borderRadius: 3, zIndex: 1 };
const DRAGGED = { transform: "rotate(-3deg) scale(1.04) translate(14px, -10px)",
                  filter: "drop-shadow(0 12px 24px rgba(0,0,0,.55))", zIndex: 5,
                  position: "relative" };
const SLOT = { aspectRatio: "1/1", border: "2px dashed var(--accent)", borderRadius: 4,
               background: "var(--bg-3)", boxSizing: "border-box" };

function Tile({ name, muted, badge, children }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <div style={{ position: "relative" }}>
        {children}
        {badge != null && <Mono size={10} style={BADGE}>{badge}</Mono>}
      </div>
      <Mono size={10} style={{ color: muted ? "var(--ink-4)" : "var(--ink-3)" }}>{name}</Mono>
    </div>
  );
}

// Artboard 03/04/05: five columns, the user's own order. The frame being rendered sits at the
// front as a spinner tile, so the grid shows what is happening, not just what landed.
export default function Gallery({ project, photos, current, onReorder }) {
  // Index of the tile being dragged and the slot it would land in -- drag state belongs to the
  // grid, not to the tiles: only the grid knows what "before this one" means.
  const [dragIndex, setDragIndex] = useState(null);
  const [overIndex, setOverIndex] = useState(null);

  if (photos === null) {
    // First fetch still flying: "empty" is not known yet, so spin instead of a false
    // "henüz fotoğraf yok" (spec §2.3).
    return (
      <div style={{ ...PAD, ...EMPTY }}>
        <span className="wf-spinner" />
      </div>
    );
  }
  if (!photos.length && !current) {
    return (
      <div style={{ ...PAD, ...EMPTY }}>
        <Mono size={12} style={{ color: "var(--ink-3)" }}>henüz fotoğraf yok</Mono>
        <Note size={13} style={{ color: "var(--ink-3)" }}>
          Prompt'ları yaz, Üret'e bas — fotoğraflar burada belirecek
        </Note>
      </div>
    );
  }

  function handleDrop() {
    const from = dragIndex;
    const to = overIndex;
    setDragIndex(null);
    setOverIndex(null);
    if (from === null || to === null || from === to) return;
    const next = photos.map((photo) => photo.file);
    const [moved] = next.splice(from, 1);
    next.splice(to, 0, moved);
    onReorder(next);
  }

  return (
    <div style={PAD}>
      <div style={GRID}>
        {current && (
          <Tile name={`${current.number}_${current.letter}.png`} muted>
            <ImgPH loading style={{ aspectRatio: "1/1" }} />
          </Tile>
        )}
        {photos.map((photo, index) => {
          const dragging = index === dragIndex;
          return (
            <div
              key={photo.file}
              draggable
              onDragStart={() => setDragIndex(index)}
              onDragOver={(e) => { e.preventDefault(); setOverIndex(index); }}
              onDrop={handleDrop}
              onDragEnd={() => { setDragIndex(null); setOverIndex(null); }}
              style={dragging ? DRAGGED : undefined}
            >
              {index === overIndex && dragIndex !== null && !dragging ? (
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <div style={SLOT} />
                  <Mono size={10} style={{ visibility: "hidden" }}>{photo.file}</Mono>
                </div>
              ) : (
                <Tile name={photo.file} badge={index + 1}>
                  {/* Placeholder until the detail page (Part 11): open the raw file in a new tab. */}
                  <a href={photoUrl(project, photo.file)} target="_blank" rel="noreferrer"
                     draggable={false}>
                    <img src={photoUrl(project, photo.file)} alt={photo.file}
                         loading="lazy" decoding="async" draggable={false}
                         style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover",
                                  border: "1px solid var(--border)", borderRadius: "var(--r-sm)",
                                  display: "block" }} />
                  </a>
                </Tile>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
```

- [ ] **Step 4: `ProjectScreen.jsx`'i bağla**

`useGeneration` çağrısına `reorder` eklenir ve galeriye geçirilir:

```jsx
  const { job, photos, error, stopping, generate, stop, reorder } = useGeneration(project);
```

```jsx
          <Gallery project={project} photos={photos} current={running ? job.current : null}
                   onReorder={reorder} />
```

- [ ] **Step 5: Koştur**

Run: `npm test`
Expected: hepsi PASS.

- [ ] **Step 6: Kasıtlı bozma turu**

`handleDrop`'taki `if (from === null || to === null || from === to) return;` satırından
`|| from === to` kısmını geçici olarak çıkar → **"aynı yere bırakılan kare için sunucuya gitmez"**
testi FAIL etmeli. Geri al.

### Task 8: Kapanış

**Files:**
- Modify: `queen-editor/frontend/dist/` (yeniden üretilir)
- Modify: `queen-editor/CODE-STANDARD.md` (§Separation of concerns tablosuna dördüncü satır)

- [ ] **Step 1: Dört dosya tablosunu güncelle**

`CODE-STANDARD.md`'deki üç satırlık tabloya dördüncü satır eklenir:

```markdown
| gallery order | in what order should the gallery show them | rewritten on every drop |
```

Tablonun hemen üstündeki "That is why a project folder holds three files rather than one" cümlesi
**four** olacak şekilde düzeltilir (yorum-kod tutarlılığı kuralı: doküman koddan sapamaz).

- [ ] **Step 2: Tüm testler + build**

Run: `python -m pytest -q` (`queen-editor/`) → hepsi PASS
Run: `npm test` (`queen-editor/frontend/`) → hepsi PASS
Run: `npm run build` → temiz; `dist/` yenilenir.

- [ ] **Step 3: Commit + push**

```bash
git add -A
git commit -m "feat(queen-editor): Bölüm 9 — galeri sıralama (sürükle-bırak + kalıcı sıra)"
git push
```

## Bulgu defteri

Uygulama sırasında ortaya çıkan, plandan sapan kararlar buraya yazılır.

- **Rota testleri sahte değil gerçek depolarla koştu.** `test_photo_routes.py` zaten geçici bir
  Drive kökü üzerinde gerçek `DrivePhotoStore`/`DrivePhotoRecord` kuruyor; planın sahte-use-case
  kurgusu yerine o desen izlendi. Kazanç: "üret → sırala → yeniden üret" akışı uçtan uca kanıtlı
  (`test_photos_produced_after_a_sort_land_on_top`), bozuk `order.json` senaryosu da gerçek dosyayla
  test edildi.
- **`list_photos` imza değişikliği iki mevcut testi kırdı**, ikisi de yeni `FakeOrderStore` ile
  güncellendi — davranışları değişmedi.
- Kasıtlı bozma turu: `from === to` koruması kaldırılınca "aynı yere bırakılan kare" testi düştü,
  geri alındı. Üretim kodunda başka sapma bulunmadı.
