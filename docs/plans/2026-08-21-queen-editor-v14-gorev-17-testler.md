# v14 Görev 17 — Panelin görsel hizalaması: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kapsam satırının adını, seçim dairesini, model kutusunu ve kalkan Süre bloğunu ölçen
testleri yazmak; takımı kırmızı commit'lemek.

**Architecture:** Tek test dosyası. Yeni bir blok video tarafının altı ölçüsünü, mevcut `sound`
bloğu ses tarafının üçünü alıyor.

**Tech Stack:** vitest, @testing-library/react, jsdom.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-17-panel-hizalamasi-testler-design.md)

## Global Constraints

- **Bu döngüde ürün kodu değişmiyor.**
- `skip` / `xfail` yok — kırmızı kırmızı commit ediliyor.
- Yorumlar **İngilizce**, ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- DOM işaretleri: satırın dairesi `data-dot`, blok başlığı `data-label`.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/LayerPanel.test.jsx` | ad, daire, kutu, kalkan blok | 9 yeni, 1 silinen, 2 düzeltilen |

---

### Task 1: Kısa adı arayan iki testi düzelt, Süre testini sil

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`

- [ ] **Step 1: İki arama**

`counts the frames a video can still be hung on` içinde:

```jsx
    expect(screen.getByText("Videosu olmayan kareler").closest("button").textContent)
      .toContain("2");
```

`clears the reason when another scope is picked` içinde:

```jsx
    fireEvent.click(screen.getByText("Videosu olmayan kareler").closest("button"));
```

- [ ] **Step 2: Süre testini sil**

```jsx
  it("says the length is not a choice in this version", () => {
    renderPanel();

    expect(screen.getByText("Her video 5 saniye — bu sürümde sabit.")).toBeTruthy();
  });
```

Bloğu 33. fark kaldırıyor; yerine 5 ve 9 geliyor.

---

### Task 2: Panelin şekli — video tarafı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`

**Interfaces:**
- Consumes: `data-dot` (satırın dairesi), `data-label` (blok başlığı), `getByRole("combobox")`.

- [ ] **Step 1: Yeni blok ve adın tam yazılması**

`describe("LayerPanel — why the press was refused")`'ın altına:

```jsx
describe("LayerPanel — the panel's own shape", () => {
  const rowOf = (label) => screen.getByText(label).closest("button");
  const blocks = () => [...document.querySelectorAll("[data-label]")].map((one) => one.textContent);

  it("names the scope in full, the way its sound twin is named", () => {
    // A slip rather than a choice: the app's own description wrote this row out in full, and only
    // the video side got shortened.
    renderPanel();

    expect(screen.getByText("Videosu olmayan kareler")).toBeTruthy();
    expect(screen.queryByText("Videosu olmayanlar")).toBeNull();
  });
```

- [ ] **Step 2: Daire ve ölçü**

```jsx
  it("puts a circle at the head of each scope row, bright on the chosen one", () => {
    renderPanel();

    const chosen = rowOf("Videosu olmayan kareler").querySelector("[data-dot]");
    const other = rowOf("Seçili kareler").querySelector("[data-dot]");
    expect(chosen.style.borderWidth).toBe("2px");
    expect(chosen.style.borderColor).toBe("var(--accent)");
    expect(other.style.borderWidth).toBe("1px");
    expect(other.style.borderColor).toBe("var(--ink-3)");
  });

  it("draws its rows with more room, the scope rows and the mode rows alike", () => {
    // One look for both families: the mode row is drawn the way a scope row is drawn, and giving
    // the measure to only one of them would leave 8px rows sitting under 10px rows.
    renderPanel();

    expect(rowOf("Videosu olmayan kareler").style.padding).toBe("10px 12px");
    expect(rowOf("Loop").style.padding).toBe("10px 12px");
  });
```

- [ ] **Step 3: Model kutusu ve kalkan blok**

```jsx
  it("offers the model in the same box the photo panel uses", () => {
    // One option, because there is one model per layer -- a box that opens and shows the only
    // thing there is. The frame and the arrow are the design's; the choice is not invented.
    renderPanel();

    expect(screen.getByRole("combobox").className).toContain("wf-input");
    expect([...screen.getByRole("combobox").options].map((one) => one.textContent))
      .toEqual(["WAN 2.2 I2V"]);
  });

  it("has no block of its own for the length", () => {
    renderPanel();

    expect(screen.queryByText("Süre")).toBeNull();
    expect(screen.queryByText(/5 saniye/)).toBeNull();
  });

  it("keeps only the blocks the design leaves standing", () => {
    renderPanel();

    expect(blocks()).toEqual(["Model", "Kapsam", "Üretim modu", "Varyant"]);
  });
});
```

- [ ] **Step 4: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: altısı da kırmızı.

---

### Task 3: Panelin şekli — ses tarafı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`

- [ ] **Step 1: Üç test**

`describe("LayerPanel — sound")` içine, `says what it would make, in its own words`'ün altına:

```jsx
  it("already names its own scope in full", () => {
    // The anchor the video row is being matched to: this side was written out from the start, and
    // this test is what keeps it from drifting the other way.
    renderSound();

    expect(screen.getByText("Videosu olup sesi olmayan kareler")).toBeTruthy();
  });

  it("shows its own model in that same box", () => {
    renderSound();

    expect([...screen.getByRole("combobox").options].map((one) => one.textContent))
      .toEqual(["MMAudio v2"]);
  });

  it("has no length block either", () => {
    renderSound();

    expect(screen.queryByText("Süre")).toBeNull();
    expect(screen.queryByText("Ses videonun süresince üretilir.")).toBeNull();
  });
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: üçü yeşil (384 / 474 / 694), queen-editor frontend'de **475 testin 10'u kırmızı** —
sekiz yeni, ve kısa adı arayan iki düzeltilmiş test.

---

### Task 4: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): the layer panel is measured, not read

Four differences, none of them behaviour. The scope row is asked for its full name -- the
app's own description wrote it out and only the video side was shortened, which is why the
sound side gets a test of its own here: it is the anchor, and it must not drift the other
way to meet the short one.

Each scope row is asked for a circle at its head, thick and accent-coloured on the chosen
one and thin and faint on the other. Both row families are asked for the roomier measure,
because the mode row is drawn the way a scope row is drawn and giving the measure to one of
them would leave two heights in one panel.

The model is asked to be the box the photo panel already uses, holding the one option there
is -- there is one model per layer, and the queue's job carries no model at all.

The length block is asked to be gone, and one test reads the panel's remaining blocks as a
list: Model, Kapsam, Üretim modu, Varyant. That list is the item's own definition of done.

One test is green the day it is written, and that is the point of it: the sound scope was
always named in full. The two tests that looked the video row up by its short name are red
along with the eight, which is the same statement read from the other end.

475 tests, 10 red.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in dört kararı Task 2 (1, 2, 3, 4) ve Task 3 (ses yüzleri). Yorum
düzeltmeleri uygulama turunda — bu turda ürün kodu değişmiyor.

**Tip tutarlılığı:** `data-dot` ve `data-label` yalnız bu testlerde okunuyor; `getByRole("combobox")`
fotoğraf panelinin kendi âdeti.

**Kontrol edilen tuzak:** `getByText` bir `option`'ı buluyor ama sarmalayan `select`'i bulmuyor —
testing-library metni yalnız **doğrudan metin çocuklarından** okuyor. Fotoğraf panelinin
`model bulunamadı` testi bunu bugün zaten kullanıyor, yani idiom kanıtlı.

**Kontrol edilen tuzak 2:** `queryByText("Videosu olmayanlar")` tam eşleşme arıyor; uzun ad
yerindeyken null döndürüyor. Kısa adın gerçekten gittiğini söyleyen şey bu.

**Kontrol edilen tuzak 3:** daire `border` kısayoluyla değil, üç uzun özellikle yazılıyor —
`var()` içeren bir kısayolu jsdom geri okuyamıyor.

**Değişmeyen:** `LayerPanel.jsx`, `queue_layer.py`. Bu döngüde ürün kodu yok.
