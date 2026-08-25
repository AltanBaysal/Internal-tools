# v14 Görev 4 — Video panelinde Üretim modu seçicisi: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Panelde mod satırının doğmasını, açılıştaki değerini, ses panelinde hiç görünmemesini ve
seçilen modun panelden uca kadar taşınmasını sınayan on iki testi yazmak; takımı kırmızı
commit'lemek.

**Architecture:** Üç var olan test dosyası genişliyor, yeni dosya yok. `LayerPanel.test.jsx` panelin
kendi davranışı (vitest + jsdom, `onQueue` bir casus). `api.test.js` isteğin gövdesi (`fetch`
sahtelenmiş). `test_photo_routes.py` ucun gövdeyi okuyup plana indirmesi.

**Tech Stack:** React 18, vitest, jsdom, @testing-library/react; Python 3, pytest, Flask test client.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-4-mod-secicisi-testler-design.md)

## Global Constraints

- **Bu döngüde kod yazılmıyor.** `frontend/src` altındaki kaynak dosyaları ve `backend/features`
  altındaki hiçbir şey değişmiyor; `production_modes.js` bu turda doğmuyor.
- Test adları ve yorumları **İngilizce**; testlerin aradığı ekran metni **Türkçe**, çünkü kullanıcı
  onu okuyor.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `dist/` **derlenmiyor** — çalışan ön yüz davranışı bu turda değişmiyor.
- Commit **kırmızı gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/features/photo_generation/LayerPanel.test.jsx` | panelin mod satırı | 7 test eklenir, 3 test güncellenir |
| `frontend/src/shared/api.test.js` | isteğin gövdesi | 1 test eklenir |
| `backend/tests/test_photo_routes.py` | ucun modu plana indirmesi | 4 test eklenir |

---

### Task 1: Panelin mod satırı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`

**Interfaces:**
- Consumes: `LayerPanel`'in `onQueue(files, variants, mode)` çağrısı — **üçüncü argüman henüz yok**.

- [ ] **Step 1: Video panelinin öbeğini yaz**

`describe("LayerPanel — sound", ...)`'ın **üstüne**:

```jsx
describe("LayerPanel — the production mode", () => {
  const modeRow = (label) => screen.getByText(label).closest("button");

  it("offers the three ways a video can be made", () => {
    renderPanel();

    expect(screen.getByText("Üretim modu")).toBeTruthy();
    expect(modeRow("Standart")).toBeTruthy();
    expect(modeRow("Loop")).toBeTruthy();
    expect(modeRow("Sonrakine bağla")).toBeTruthy();
  });

  it("opens on the plain one", () => {
    renderPanel();

    expect(modeRow("Standart").style.borderColor).toBe("var(--accent)");
    expect(modeRow("Loop").style.borderColor).toBe("var(--border)");
    expect(modeRow("Sonrakine bağla").style.borderColor).toBe("var(--border)");
  });

  it("stands between the scope and the variant count", () => {
    // The design's order, and the reason it is that order: the mode is part of deciding what to
    // make, so it belongs on the scope's side of the panel rather than after the count.
    const { container } = renderPanel();

    const text = container.textContent;
    expect(text.indexOf("Üretim modu")).toBeGreaterThan(text.indexOf("Kapsam"));
    expect(text.indexOf("Üretim modu")).toBeLessThan(text.indexOf("Varyant"));
  });

  it("sends the mode that was picked", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 2 });
    renderPanel({ onQueue });

    fireEvent.click(modeRow("Loop"));
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null, 1, "loop");
  });

  it("sends the plain mode when nobody touched the row", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 2 });
    renderPanel({ onQueue });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null, 1, "standard");
  });
});
```

Sıra testi `container.textContent` üstünde indeks karşılaştırıyor: bileşenlerin DOM sırası budur ve
etiketleri tek tek sorgulamak, sıranın kendisini değil varlığını sınardı.

- [ ] **Step 2: Ses panelinin iki testini yaz**

`describe("LayerPanel — sound", ...)` içine, `does not explain who writes the prompt either`'ın
üstüne:

```jsx
  it("never offers a mode -- a sound ends nowhere", () => {
    // Loop and "Sonrakine bağla" are both about the picture a video ends on. A sound is laid over
    // the whole of one video and arrives nowhere, so there is nothing here to choose between.
    renderSound();

    expect(screen.queryByText("Üretim modu")).toBeNull();
    expect(screen.queryByText("Loop")).toBeNull();
  });

  it("still sends the plain mode, so the server reads one call shape", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 1 });
    renderSound({ onQueue });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null, 1, "standard");
  });
```

- [ ] **Step 3: Var olan üç gönderme testini yeni çağrı biçimine getir**

`describe("LayerPanel — sending", ...)` içinde:

```jsx
    expect(onQueue).toHaveBeenCalledWith(null, 1, "standard");
```

```jsx
    expect(onQueue).toHaveBeenCalledWith(["0_a.png"], 1, "standard");
```

```jsx
    expect(onQueue).toHaveBeenCalledWith(null, 2, "standard");
```

Çağrı biçimi değişiyor. Eski hâllerini bırakmak, biçimin tek olmadığını söylemek olurdu.

- [ ] **Step 4: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: on test düşüyor. Beşi "Üretim modu" metnini bulamıyor, ikisi ses panelinde
`onQueue`'nun üçüncü argümanını `undefined` buluyor, üçü de aynı sebeple.

---

### Task 2: İsteğin gövdesi

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.test.js`

**Interfaces:**
- Consumes: `queueLayer(project, kind, files, variants, mode)` — **beşinci argüman henüz yok**.

- [ ] **Step 1: Import'a ekle**

```js
import {
  createProject,
  getSettings,
  getStatus,
  listFrames,
  listProjects,
  queueLayer,
  saveOrder,
} from "./api.js";
```

- [ ] **Step 2: Testi yaz**

`does not abort a request after its answer has arrived`'ın üstüne:

```js
  it("carries the production mode into the queue request", async () => {
    // The panel is where the mode is chosen and the plan is where it lands; this line is the only
    // thing between them, and a body that quietly drops the key would leave every video standard
    // with nothing on screen to say so.
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ added: 1 }));
    vi.stubGlobal("fetch", fetchMock);

    await queueLayer("düğün", "video", ["0_a.png"], 2, "loop");

    const [url, options] = fetchMock.mock.calls[0];
    expect(url).toBe(`/api/projects/${encodeURIComponent("düğün")}/layers/video`);
    expect(JSON.parse(options.body)).toEqual({ files: ["0_a.png"], variants: 2, mode: "loop" });
  });
```

- [ ] **Step 3: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: on bir test düşüyor. Yenisi `mode` anahtarını gövdede bulamıyor.

---

### Task 3: Ucun okuduğu mod

**Files:**
- Modify: `queen-editor/backend/tests/test_photo_routes.py`

**Interfaces:**
- Consumes: `POST /api/projects/<p>/layers/<kind>` gövdesindeki `mode` — **uç henüz okumuyor**.
- Produces: `video_jobs(drive, project="düğün")` yardımcısı.

- [ ] **Step 1: Testleri yaz**

`test_an_unknown_layer_is_not_a_place_to_queue_anything`'in üstüne:

```python
def video_jobs(drive, project="düğün"):
    plan = json.loads((drive / project / "plan.json").read_text(encoding="utf-8"))
    return [frame for frame in plan["frames"] if frame["type"] == "video"]


def test_the_videos_endpoint_carries_the_production_mode(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    resp = client.post("/api/projects/düğün/layers/video", json={"mode": "loop"})

    assert resp.status_code == 202
    # The plan line is where the mode has to land: the renderer reads it hours later, long after
    # the panel that chose it is gone.
    assert [job["mode"] for job in video_jobs(drive)] == ["loop"]


def test_a_layer_queued_with_no_mode_is_a_plain_one(tmp_path):
    # A client older than the row asks for exactly what it always asked for -- the same reading the
    # variant count already gets.
    client, drive = make_client(tmp_path)
    generate(client, prompts='["a"]', variants=1)

    client.post("/api/projects/düğün/layers/video", json={})

    assert [job["mode"] for job in video_jobs(drive)] == ["standard"]


def test_the_videos_endpoint_refuses_a_mode_nobody_knows(tmp_path):
    client, _ = make_client(tmp_path)

    resp = client.post("/api/projects/düğün/layers/video", json={"mode": "kelebek"})

    assert resp.status_code == 400
    assert resp.get_json()["field"] == "mode"


def test_a_sound_cannot_be_asked_to_end_anywhere(tmp_path):
    # Only a video ends on a picture. Letting the word through would hide the mistake behind a
    # sound that came out fine.
    client, _ = make_client(tmp_path)

    resp = client.post("/api/projects/düğün/layers/audio", json={"mode": "loop"})

    assert resp.status_code == 400
    assert resp.get_json()["field"] == "mode"
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: `queen-editor`'ın iki takımı kırmızı, `queen-agent`'ın ikisi yeşil.

Uç tarafında üç test düşüyor: mod plan satırına `standard` olarak yazılı (2. madde oraya yazıyor),
yani "loop bekleniyordu, standard geldi"; ve iki geçersiz mod 400 yerine 202 alıyor, çünkü uç
gövdedeki anahtarı hiç okumuyor. **`test_a_layer_queued_with_no_mode_is_a_plain_one` yeşil doğuyor**
— `queue_layer`'ın varsayılanı bugün de `standard`. Kırmızı olmaması sorun değil: bu madde
varsayılanı seçilebilir yapıyor, ve varsayılanın kaybolmaması da maddenin işi.

---

### Task 4: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor/frontend/src queen-editor/backend/tests docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): the production mode can be picked from the panel

Red on purpose: the panel has no mode row, api.queueLayer sends no mode key, and the
endpoint never reads one. The engine side has carried a mode since madde 2; nothing
could give it one but a test.

The three modes are drawn the way the scope rows are, with no count cell: a mode has
nothing to count, and saying so with a missing argument would leave the reader deciding
what an absent number means. The sound panel grows no row at all -- a sound is laid over
the whole of a video and arrives nowhere -- but it still sends the plain mode, so the
server never has to ask where a request came from.

Three existing send tests move to the new call shape. Leaving the old ones would say the
shape is not one shape.

A layer queued with no mode key reading as plain is true today, so that test is born
green. This madde makes the default pickable, and keeping the default is part of it.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in on iki testinin on ikisi planda kodlu. 1-5 → Task 1 Step 1; 6-7 → Task 1
Step 2; 8 → Task 2; 9-12 → Task 3. Spec'in "var olan üç gönderme testi" notu → Task 1 Step 3.

**Tip tutarlılığı:** `onQueue(files, variants, mode)` beş test yerinde de aynı sırada.
`queueLayer(project, kind, files, variants, mode)` Task 2'de bir kez, ve panelin çağrısıyla aynı
sırayı taşıyor.

**Kontrol edilen tuzak:** sıra testi `container.textContent`'in indekslerine bakıyor, `getAllByText`
sonuçlarına değil. İkincisi belgedeki sırayı değil sorgunun sırasını verirdi.

**Kontrol edilen tuzak 2:** ses panelinin "Loop" aramasında `queryByText` var, `getByText` değil.
`getByText` bulamadığında atar; test "yok" demek istiyor, "patlamadı" değil.

**Kontrol edilen tuzak 3:** açılış testi üç satırın da kenar rengine bakıyor, yalnız seçili olanın
değil. Yalnız birine bakan bir test, üçü birden seçili çizen bir uygulamayla da yeşil kalırdı.
