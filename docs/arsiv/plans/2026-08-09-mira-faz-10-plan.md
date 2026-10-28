# Mira Faz 10 (Okuma) — Uygulama Planı

**Hedef:** Dosyayı okuma paneli — sohbette ray 320 → 560px (Madde 22), proje ekranında sağdan 560px
panel (Madde 23), **Download** (Madde 24).

**Mimari:** Tek uç nokta bir dosyanın hem künyesini hem metnini verir; boyut metinden türer. Tek
panel bileşeni iki kapta yaşar: sohbette rayın içi, proje ekranında bir `aside`. Açık dosya `App`'te
bir addır.

**Kaynak spec:** [Faz 10](../specs/2026-08-09-mira-faz-10-okuma-design.md)

## Global Kısıtlar

- Boyut diske sorulmaz, metinden türer: `len(text.encode("utf-8"))`.
- Metin düz çizilir; markdown render edilmez.
- Download sunucudan yeniden okur; ekrandaki kopyayı kaydetmez.
- Test komutları: `python -m pytest d:\code\github\internal-tools\mira -q` ·
  `npm --prefix d:\code\github\internal-tools\mira\frontend test`.
- Commit: `git add <yollar>` → `git commit -m <mesaj> -- <aynı yollar>`.

---

### Task 1: Dosyayı okumak (arka uç)

**Dosyalar:** Değiştir `domain/file.py`, `domain/errors.py`, `domain/ports.py`,
`data/file_file_store.py`, `presentation/routes.py` · Oluştur `domain/usecases/read_file.py` · Test
`backend/tests/test_files_api.py`, `backend/tests/test_read_file.py`

**Arayüzler:**
- Üretir: `FileBody(file: File, text: str)` — `size` özelliği UTF-8 bayt sayısı ·
  `read_file(file_store, project_id, name) -> FileBody` · `FileStore.read_body(project_id, name)`
- Tüketir: Faz 9'un `File`, `extension_of`, `FileFileStore._iso` parçaları.

- [ ] **Adım 1: Testleri yaz**

```python
def test_reading_gives_the_text_with_its_chip_and_time(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "plan.md", "the body")
    body = read_file(files, "p1", "plan.md")
    assert (body.file.name, body.file.ext, body.text) == ("plan.md", "md", "the body")
    assert body.file.modified_at.endswith("+00:00")


def test_size_counts_bytes_not_characters(tmp_path):
    files = _files(tmp_path)
    files.write("p1", "not.md", "ü")
    # The browser cannot count this itself: one character, two bytes.
    assert read_file(files, "p1", "not.md").size == 2


def test_a_file_that_is_not_there_is_reported(tmp_path):
    with pytest.raises(FileNotFound):
        read_file(_files(tmp_path), "p1", "ghost.md")
```

API tarafı (`test_files_api.py`):

```python
def test_reading_a_file_over_http(client):
    ...
    body = client.get(f"/api/projects/{pid}/files/plan.md").get_json()
    assert body == {"name": "plan.md", "ext": "md", "modifiedAt": ANY, "size": 8, "text": "the body"}


def test_reading_a_file_that_is_gone_is_a_404(client):
    assert client.get("/api/projects/p1/files/ghost.md").status_code == 404
```

- [ ] **Adım 2: Kırmızı olduğunu gör** — `python -m pytest d:\code\github\internal-tools\mira -q`
- [ ] **Adım 3: Yaz**

```python
# domain/file.py
@dataclass(frozen=True)
class FileBody:
    file: File
    text: str

    @property
    def size(self):
        # Bytes as they sit on disk; the browser counts characters and would disagree.
        return len(self.text.encode("utf-8"))
```

```python
# data/file_file_store.py
def read_body(self, project_id, name):
    path = f"{project_id}/{FILES_DIR}/{name}"
    if not self._store.exists(path):
        return None
    return FileBody(
        File(name=name, ext=extension_of(name), modified_at=_iso(self._store.mtime(path))),
        self._store.read_text(path),
    )
```

```python
# domain/usecases/read_file.py
def read_file(file_store, project_id, name):
    body = file_store.read_body(project_id, name)
    if body is None:
        raise FileNotFound(name)
    return body
```

Rota:

```python
@workspace_bp.get("/api/projects/<project_id>/files/<name>")
def get_file(project_id, name):
    try:
        body = read_file(file_store, project_id, name)
    except FileNotFound:
        return jsonify({"error": "file not found"}), 404
    return jsonify(
        {
            "name": body.file.name,
            "ext": body.file.ext,
            "modifiedAt": body.file.modified_at,
            "size": body.size,
            "text": body.text,
        }
    )
```

- [ ] **Adım 4: Yeşil olduğunu gör** · **Adım 5: Commit**

---

### Task 2: Panel (ön yüz)

**Dosyalar:** Oluştur `features/workspace/useFile.js`, `features/workspace/FilePanel.jsx` · Değiştir
`FileRail.jsx`, `FileRow.jsx`, `ChatScreen.jsx`, `ProjectScreen.jsx`, `App.jsx`, `workspace.css` ·
Test `FilePanel.test.jsx`, `FileRail.test.jsx`, `ProjectScreen.test.jsx`, `App.test.jsx`

**Arayüzler:**
- Üretir: `useFile(projectId, name) -> {file, error}` · `<FilePanel file error onClose />`
- Tüketir: Faz 9'un `FileRow`, `FileRail`, `useFiles`.

`FileRow` bir `onOpen` alır ve satır tıklanabilir olur. `FileRail` açık dosya varken listeyi değil
paneli çizer ve `rail--open` sınıfını alır. `ProjectScreen` paneli ızgaranın yanına koyar ve
ızgaraya `project-grid--reading` sınıfını verir. Açık ad `App`'te durur; proje değişince silinir.

- [ ] **Adım 1: Testleri yaz**

```jsx
test("the panel names the file and shows its text", () => {
  render(<FilePanel file={{ name: "plan.md", ext: "md", size: 1434, text: "the body", modifiedAt: NOW }} />);
  expect(screen.getByText("plan.md")).toBeTruthy();
  expect(screen.getByText("the body")).toBeTruthy();
});

test("the meta line carries the chip, the size and the time", () => {
  render(<FilePanel file={{ ..., size: 1434, modifiedAt: TWO_HOURS_AGO }} />);
  expect(screen.getByTestId("file-meta").textContent).toBe("md · 1.4 KB · 2h ago");
});

test("Escape closes the panel", () => {
  const onClose = vi.fn();
  render(<FilePanel file={FILE} onClose={onClose} />);
  fireEvent.keyDown(window, { key: "Escape" });
  expect(onClose).toHaveBeenCalled();
});
```

- [ ] **Adım 2: Kırmızı** · **Adım 3: Yaz** · **Adım 4: Yeşil** · **Adım 5: Commit**

---

### Task 3: Download

**Dosyalar:** Değiştir `FilePanel.jsx`, `shared/api.js` (gerekirse), `workspace.css` · Test
`FilePanel.test.jsx`

- [ ] **Adım 1: Testleri yaz**

```jsx
test("Download reads the file again rather than saving what is on screen", async () => {
  const fetch = vi.fn().mockResolvedValue({ ok: true, status: 200, json: async () => FILE });
  vi.stubGlobal("fetch", fetch);
  render(<FilePanel projectId="p1" file={FILE} />);
  fireEvent.click(screen.getByRole("button", { name: "Download" }));
  await waitFor(() => expect(fetch).toHaveBeenCalled());
});

test("while it downloads the button says preparing", async () => { ... });
```

`URL.createObjectURL` jsdom'da yok — testte `vi.stubGlobal("URL", {...})` ile konur.

- [ ] **Adım 2: Kırmızı** · **Adım 3: Yaz** · **Adım 4: Yeşil** · **Adım 5: Commit**

---

## Öz-denetim

**Spec kapsaması.** §1 Task 1 · §2-3 Task 2 · §4 Task 3 · §6'daki on testin hepsi bir task'a düşüyor
(1-4 Task 1, 5-8 Task 2, 9-10 Task 3).

**Ad tutarlılığı.** `read_body` portta, veri katmanında ve use case'te aynı; HTTP'de `modifiedAt` ve
`size`, ön yüzde `file.modifiedAt` / `file.size`. `FileBody.size` bir özellik, alan değil — JSON'a
rota koyar.

**Risk.** `GET …/files/<name>` rotası `GET …/files` ile aynı önekte; Flask ikisini ayırır ama ad
eğik çizgi içeremez — `<string>` dönüştürücüsünün varsayılanı bu, ve `store`'un kökü ikinci kilit.
