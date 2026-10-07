# Bölüm 10 — Export Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** App bar'daki Export düğmesi, projenin Drive klasör yolunu ve fotoğraf–prompt listesini galeri sırasıyla taşıyan tek bir JSON dosyası indirir.

**Architecture:** Dosyayı sunucu üretir: yeni domain use case `export_project` mevcut `list_photos`'u çağırır (proje kontrolü + galeri sırası tek yerde kalsın), sonuca klasör yolunu ekler. Yeni uç `GET /api/projects/<p>/export` JSON'u `Content-Disposition: attachment` ile döner. Frontend'de Export, görünümü `Btn ghost` ile birebir aynı olan bir indirme bağlantısıdır — JavaScript'siz çalışır.

**Tech Stack:** Flask + pytest · React 18 + vitest/jsdom.

**Spec:** [2026-08-05-queen-editor-bolum10-export-design.md](../specs/2026-08-05-queen-editor-bolum10-export-design.md)

## Global Constraints

- **TDD:** önce düşen test, sonra kod; testin düştüğü görülmeden kod yazılmaz.
- **Commit:** bölüm sonunda tek commit + push; `dist/` aynı commit'te.
- **Katman kuralları:** `domain/` saf; dosya adı/şema `data/`'da; `presentation/` yalnız çeviri ve serileştirme.
- Ekran metni Türkçe, kod/veri İngilizce. Export JSON anahtarları: `folder`, `photos`, `file`, `prompt`.
- İndirilen dosya adı: `<proje>-export.json`; Türkçe karakter kodlaması Flask'ın `download_name` işlevine bırakılır, elle başlık kurulmaz.
- Export düğmesinin **pasif/yükleniyor durumu yoktur** (tasarımda yok).
- Dosyalar CRLF satır sonlarıyla kalır.

---

### Task 1: `export_project` use case

**Files:**
- Create: `queen-editor/backend/features/photo_generation/domain/usecases/export_project.py`
- Test: `queen-editor/backend/tests/test_photo_usecases.py` (ekleme)

**Interfaces:**
- Consumes: `list_photos(record, store, order_store, project)` (Bölüm 9), `PhotoStore.photo_dir`.
- Produces: `export_project(record, store, order_store, project) -> {"folder": str, "photos": [{"file", "prompt"}]}`; olmayan projede `ProjectMissing`.

- [ ] **Step 1: Testleri yaz**

Import satırına:

```python
from backend.features.photo_generation.domain.usecases.export_project import export_project
```

Testler (`test_save_order_*` bloğunun ardına):

```python
def test_export_carries_the_folder_and_the_gallery_order():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "prompt": "ilk", "seed": 7})
    record.append("düğün", {"file": "1_a.png", "prompt": "ikinci", "seed": 8})
    order = FakeOrderStore(["0_a.png", "1_a.png"])

    assert export_project(record, FakeStore(), order, "düğün") == {
        "folder": "/fake/düğün",
        "photos": [{"file": "0_a.png", "prompt": "ilk"},
                   {"file": "1_a.png", "prompt": "ikinci"}],
    }


def test_export_of_an_empty_project_still_names_the_folder():
    assert export_project(FakeRecord(), FakeStore(), FakeOrderStore(), "düğün") == {
        "folder": "/fake/düğün", "photos": []}


def test_export_rejects_a_missing_project():
    with pytest.raises(ProjectMissing):
        export_project(FakeRecord(), FakeStore(projects=()), FakeOrderStore(), "yok")
```

Not: `FakeStore.photo_dir` zaten `f"/fake/{project}"` döndürüyor (dosyanın başındaki sahte).

- [ ] **Step 2: Koştur, düştüğünü gör**

Run: `python -m pytest backend/tests/test_photo_usecases.py -q` (`queen-editor/` içinde)
Expected: FAIL — modül yok.

- [ ] **Step 3: Use case'i yaz**

```python
"""The project in one file: where its photos live, and which prompt made each one, in gallery order.

The list comes from list_photos rather than from the record directly, so "which photos exist and in
what order" keeps exactly one answer -- an export that disagreed with the gallery would be a second
truth, and the video is stitched from this order.
"""
from backend.features.photo_generation.domain.usecases.list_photos import list_photos


def export_project(record, store, order_store, project):
    rows = list_photos(record, store, order_store, project)
    return {
        "folder": store.photo_dir(project),
        # Only what the next tool needs: a name and the prompt behind it. The rest of the trace
        # (negative, seed, time) stays in the record.
        "photos": [{"file": row["file"], "prompt": row.get("prompt", "")} for row in rows],
    }
```

- [ ] **Step 4: Koştur**

Run: `python -m pytest backend/tests/test_photo_usecases.py -q`
Expected: hepsi PASS.

### Task 2: `GET /api/projects/<p>/export` ucu

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/presentation/routes.py`
- Modify: `queen-editor/backend/main.py`
- Test: `queen-editor/backend/tests/test_photo_routes.py` (ekleme)

**Interfaces:**
- Produces: blueprint'e yeni `export_project` parametresi.

- [ ] **Step 1: Testleri yaz**

`make_client` içindeki blueprint çağrısına `export_project=partial(export_project, record, store, order_store),` eklenir ve import satırına use case girer. Testler:

```python
def test_export_downloads_a_json_file_in_gallery_order(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts='["a", "b"]', variants=1)
    client.put("/api/projects/düğün/order", json={"order": ["0_a.png", "1_a.png"]})

    resp = client.get("/api/projects/düğün/export")

    assert resp.status_code == 200
    assert resp.mimetype == "application/json"
    assert "attachment" in resp.headers["Content-Disposition"]
    body = json.loads(resp.data)
    assert body["photos"] == [{"file": "0_a.png", "prompt": "a"},
                              {"file": "1_a.png", "prompt": "b"}]
    assert body["folder"].endswith("düğün")


def test_export_of_an_unknown_project_returns_404(tmp_path):
    client, _ = make_client(tmp_path)
    assert client.get("/api/projects/yok/export").status_code == 404
```

Dosyanın başına `import json` eklenir (yoksa).

- [ ] **Step 2: Koştur, düştüğünü gör**

Run: `python -m pytest backend/tests/test_photo_routes.py -q`
Expected: FAIL.

- [ ] **Step 3: Rotayı yaz**

`routes.py` başına:

```python
import io
import json

from flask import Blueprint, jsonify, request, send_file, send_from_directory
```

İmzaya `export_project` eklenir (`save_order`'dan sonra). `put_order`'ın ardına:

```python
    @bp.get("/api/projects/<project>/export")
    def export(project):
        try:
            data = export_project(project)
        except ProjectMissing as exc:
            return jsonify({"error": str(exc)}), 404
        # Written out here rather than in the domain: turning a value into bytes on the wire is
        # this layer's job. ensure_ascii=False keeps Turkish prompts readable in the file.
        payload = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
        return send_file(io.BytesIO(payload), mimetype="application/json", as_attachment=True,
                         download_name=f"{project}-export.json")
```

`main.py`: import + blueprint parametresi:

```python
from backend.features.photo_generation.domain.usecases.export_project import export_project
```

```python
    export_project=partial(export_project, _photo_record, _photo_store, _order_store),
```

- [ ] **Step 4: Koştur**

Run: `python -m pytest -q` (`queen-editor/` içinde)
Expected: hepsi PASS.

### Task 3: App bar'da Export bağlantısı

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js` (yeni `exportUrl`)
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx`
- Modify: `queen-editor/frontend/src/shared/app.css`
- Test: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.test.jsx` (yeni)

**Interfaces:**
- Produces: `exportUrl(project)` — `photoUrl` gibi düz URL üreteci, fetch değil.

- [ ] **Step 1: Testi yaz**

```jsx
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import ProjectScreen from "./ProjectScreen.jsx";

vi.mock("../../shared/api.js", () => ({
  exportUrl: (project) => `/api/projects/${encodeURIComponent(project)}/export`,
  generateBatch: vi.fn(),
  getStatus: vi.fn().mockResolvedValue({ status: "idle" }),
  listPhotos: vi.fn().mockResolvedValue([]),
  photoUrl: (project, file) => `/photos/${project}/${file}`,
  saveOrder: vi.fn(),
  stopGeneration: vi.fn(),
}));

const SETTINGS = { prompts: "", negative: "", variants: 4 };

beforeEach(() => {
  vi.clearAllMocks();
});

describe("ProjectScreen app bar", () => {
  it("Export'u indirme bağlantısı olarak sunar", () => {
    render(<ProjectScreen project="düğün" settings={SETTINGS} onSaveSettings={() => {}} />);

    const link = screen.getByText("Export").closest("a");
    expect(link.getAttribute("href")).toBe(
      `/api/projects/${encodeURIComponent("düğün")}/export`);
    expect(link.hasAttribute("download")).toBe(true);
  });

  it("Export düğmesi Projeden çık'ın solunda durur", () => {
    render(<ProjectScreen project="düğün" settings={SETTINGS} onSaveSettings={() => {}} />);

    const exportEl = screen.getByText("Export");
    const exitEl = screen.getByText("Projeden çık");
    // Node.compareDocumentPosition: bit 4 = "other node follows this one" in document order.
    expect(exportEl.compareDocumentPosition(exitEl) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });
});
```

- [ ] **Step 2: Koştur, düştüğünü gör**

Run: `npm test` (`queen-editor/frontend/` içinde)
Expected: 2 test FAIL.

- [ ] **Step 3: `exportUrl`'i ekle** (`api.js`, `photoUrl`'ün yanına)

```js
// Plain URL, not a fetch: the browser downloads it straight from the link (see ProjectScreen).
export function exportUrl(project) {
  return `/api/projects/${encodeURIComponent(project)}/export`;
}
```

- [ ] **Step 4: App bar'ı güncelle** (`ProjectScreen.jsx`)

Import satırına `exportUrl` eklenir. App bar'ın üçüncü hücresi:

```jsx
        <div style={{ display: "flex", gap: 8, justifySelf: "end" }}>
          {/* A link, not a Btn: its whole job is downloading a file, which the browser does by
              itself -- no JavaScript, and "save link as" keeps working. The look is the design's
              ghost button (see app.css for the underline reset). */}
          <a className="wf-btn wf-btn--ghost" href={exportUrl(project)} download>Export</a>
          <Btn ghost onClick={() => navigate("/")}>Projeden çık</Btn>
        </div>
```

(Eski `<Btn ghost style={{ justifySelf: "end" }}>Projeden çık</Btn>` bu grupla değiştirilir.)

- [ ] **Step 5: Alt çizgiyi kapat** (`shared/app.css` sonuna)

```css
/* A download link wearing the design's button clothes: everything else comes from .wf-btn, only
   the anchor's default underline has to go. */
a.wf-btn {
  text-decoration: none;
}
```

- [ ] **Step 6: Koştur**

Run: `npm test`
Expected: hepsi PASS.

### Task 4: Kapanış

- [ ] **Step 1: Bozma turu**

`ProjectScreen.jsx`'te `download` niteliğini geçici olarak kaldır → "Export'u indirme bağlantısı
olarak sunar" testi FAIL etmeli. Geri al.

- [ ] **Step 2: Tüm testler + build**

Run: `python -m pytest -q` (`queen-editor/`) → PASS
Run: `npm test` (`queen-editor/frontend/`) → PASS
Run: `npm run build` → temiz, `dist/` yenilenir.

- [ ] **Step 3: Commit + push**

```bash
git add -A
git commit -m "feat(queen-editor): Bölüm 10 — Export (galeri sırasında tek JSON)"
git push
```

## Bulgu defteri

- **Bölüm numarası kaymasından kalan yorum düzeltildi:** `shared/app.css` panel kilidi yorumunda
  Model bloğu için "Part 14" yazıyordu; yeni numaralamada 15. Yorum-kod tutarlılığı kuralı gereği
  düzeltildi (kod değişmedi).
- Bozma turu: `download` niteliği kaldırılınca bağlantı testi düştü, geri alındı. Başka sapma yok.
