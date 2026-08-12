# Queen Editor v5 · Görev 23 — Sekme şeridi ve katman sütunu · Uygulama planı

> Tasarım: [Görev 23 spec](../specs/2026-08-12-queen-editor-v5-gorev-23-detay-sekmeleri-design.md).
> Önce kırmızı test, sonra en küçük kod.

**Hedef:** detayda Foto | Video | Ses şeridi ve açık sekmeye göre büyüyen sağ sütun.

## Genel kısıtlar

- Kod/yorum/test **İngilizce**, arayüz metni **Türkçe**.
- Katman sırası foto → video → ses.
- Test komutları (birebir): `python -m pytest queen-editor -q` ·
  `npm test --prefix queen-editor/frontend -- --run` · `npm run build --prefix queen-editor/frontend`

---

## Görev 1 — Satır katman prompt'larını taşır

**Dosyalar:** `domain/usecases/list_frames.py`, `domain/usecases/queue_layer.py`,
test: `tests/test_photo_usecases.py`

- [ ] **Adım 1 — kırmızı test:**

```python
def test_a_frame_carries_the_prompt_of_every_layer_it_holds():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done",
                            "prompt": "kırmızı elbise"})
    record.append("düğün", {"file": "0_a_V1_0.mp4", "frame": "0_a", "layer": "video",
                            "status": "done", "prompt": "kadın dönüyor"})
    plan_store = FakePlanStore(frames=[frame(0)])

    rows = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert rows[0]["prompts"] == {"photo": "kırmızı elbise", "video": "kadın dönüyor"}


def test_a_frame_whose_record_kept_no_prompt_falls_back_to_the_plans():
    record = FakeRecord()
    record.append("düğün", {"file": "0_a.png", "frame": "0_a", "layer": "photo", "status": "done"})
    plan_store = FakePlanStore(frames=[frame(0)])

    rows = list_frames(record, FakeStore(), plan_store, FakeOrderStore(), "düğün")

    assert rows[0]["prompts"] == {"photo": "p"}
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3 — `list_frames.py`:** `said = record.prompts(project)` bir kez okunur; iki satır
oluşumuna eklenir:

```python
                       "prompts": _words(said.get(fid, {}), frame.get("prompt")),
```

```python
def _words(said, planned):
    """What each layer was made from. The record answers for every layer; the photo's own prompt
    can also come from the plan, which is where a frame planned before the record carried prompts
    still keeps it."""
    words = dict(said)
    if planned and not words.get(layers.PHOTO):
        words[layers.PHOTO] = planned
    return words
```

> Kaydın kendi döngüsünde `row.get("prompt")` yedeği kullanılır.

- [ ] **Adım 4 — `queue_layer.py`:** `said = record.prompts(project)` ve `words = {...}` satırları
kalkar; yerine `words = frame.get("prompts", {})`.

- [ ] **Adım 5:** `python -m pytest queen-editor -q` → yeşil.

---

## Görev 2 — Sekme şeridi

**Dosyalar:** `PhotoDetail.jsx`, test: `PhotoDetail.test.jsx`

- [ ] **Adım 1 — kırmızı testler:**

```jsx
const LAYERED = {
  id: "P0_0", file: "P0_0.png", status: "done", prompt: "kırmızı elbise",
  layers: { photo: "P0_0.png", video: "P0_0_V1_0.mp4", audio: "P0_0_V1_0_S1_0.wav" },
  failed: [], owed: [],
  prompts: { photo: "kırmızı elbise", video: "kadın dönüyor", audio: "kumaş hışırtısı" },
};

describe("PhotoDetail — the layer tabs", () => {
  it("opens on the photo and offers a tab per layer", async () => {
    await showDetail({ frames: [LAYERED] });

    expect(screen.getByRole("button", { name: "Foto" }).getAttribute("aria-current")).toBe("page");
    expect(screen.getByRole("button", { name: "Video" }).disabled).toBe(false);
    expect(screen.getByRole("button", { name: "Ses" }).disabled).toBe(false);
  });

  it("leaves the tab of a layer the frame does not have disabled rather than hidden", async () => {
    await showDetail({ frames: [{ ...LAYERED, layers: { photo: "P0_0.png" },
                                  prompts: { photo: "kırmızı elbise" } }] });

    expect(screen.getByRole("button", { name: "Video" }).disabled).toBe(true);
    expect(screen.getByRole("button", { name: "Ses" }).disabled).toBe(true);
  });

  it("does not open a tab for a layer that blew up", async () => {
    await showDetail({ frames: [{ ...LAYERED, failed: ["audio"] }] });

    expect(screen.getByRole("button", { name: "Ses" }).disabled).toBe(true);
  });

  it("shows the open layer's own prompt and the ones under it, read-only", async () => {
    await showDetail({ frames: [LAYERED] });

    fireEvent.click(screen.getByRole("button", { name: "Video" }));

    expect(screen.getByText("kadın dönüyor")).toBeTruthy();
    expect(screen.getByText("kırmızı elbise")).toBeTruthy();
    expect(screen.getByText("P0_0_V1_0.mp4")).toBeTruthy();
    // The negative belongs to the photo alone: video and sound jobs carry none.
    expect(screen.queryByText("Negatif")).toBeNull();
  });

  it("repeats the skeleton for sound", async () => {
    await showDetail({ frames: [LAYERED] });

    fireEvent.click(screen.getByRole("button", { name: "Ses" }));

    expect(screen.getByText("kumaş hışırtısı")).toBeTruthy();
    expect(screen.getByText("P0_0_V1_0_S1_0.wav")).toBeTruthy();
  });
});
```

> `showDetail` yardımcısı dosyada nasıl kuruluyorsa aynısını kullan (api mock'u + render).

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3 — `PhotoDetail.jsx`:** şerit ve sütun.

```jsx
// Madde 73's strip: three joined buttons over the stage. A layer the frame does not have stays
// disabled rather than hidden -- the user sees what a frame could still become.
const TABS = [
  { id: "photo", label: "Foto" },
  { id: "video", label: "Video", Glyph: PlayGlyph },
  { id: "audio", label: "Ses", Glyph: SoundGlyph },
];

const STRIP = { position: "absolute", top: 16, left: "50%", transform: "translateX(-50%)",
                display: "flex", zIndex: 2 };
```

```jsx
function LayerTabs({ open, has, onOpen }) {
  return (
    <div style={STRIP}>
      {TABS.map(({ id, label, Glyph }, index) => (
        <button key={id} type="button" disabled={!has[id]}
                aria-current={open === id ? "page" : undefined}
                onClick={() => onOpen(id)}
                className="wf-stroke"
                style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 10px",
                         background: "var(--bg-2)", cursor: has[id] ? "pointer" : "default",
                         opacity: has[id] ? 1 : 0.35,
                         color: open === id ? "var(--accent)" : "var(--ink-3)",
                         borderColor: open === id ? "var(--accent)" : "var(--border)",
                         // Joined, not three separate pills: one control, three states.
                         marginLeft: index ? -1 : 0 }}>
          {Glyph && <Glyph size={10} />}
          <Mono size={10}>{label}</Mono>
        </button>
      ))}
    </div>
  );
}
```

Sütun, açık sekmeye göre:

```jsx
  // What the column shows: every layer up to the open one, its own prompt first and the ones under
  // it below (madde 75).
  const shown = LAYER_ORDER.slice(0, LAYER_ORDER.indexOf(open) + 1);
```

Dosya adı satırları `shown` üzerinden, prompt kutuları `[...shown].reverse()` üzerinden çizilir;
`Negatif` yalnız `open === "photo"` iken.

- [ ] **Adım 4:** yeşil.

---

## Görev 3 — Bekleyen karenin alanı (madde 82)

**Dosyalar:** `PhotoDetail.jsx`, test: `PhotoDetail.test.jsx`

- [ ] **Adım 1 — kırmızı test:**

```jsx
  it("draws a waiting frame's two lines faintly", async () => {
    await showDetail({ frames: [{ id: "P0_0", file: "P0_0.png", status: "pending",
                                  layers: {}, failed: [], owed: ["photo"], prompts: {} }] });

    expect(screen.getByText("bekliyor").closest("[data-holder]").style.opacity).toBe("0.45");
  });
```

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3:** bekleyen tutucuya `data-holder` ve `opacity: 0.45` (bugünkü `0.5` yerine
tasarımın kendi sayısı); iki satır tutucunun içinde kalır.

- [ ] **Adım 4:** yeşil.

---

## Görev 4 — Tam takım, build, commit

- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] `dist/` ile tek commit:

```
feat(queen-editor): the detail page opens a tab per layer
```
