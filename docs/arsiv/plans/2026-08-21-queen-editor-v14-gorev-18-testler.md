# v14 Görev 18 — Fotoğraf varyant varsayılanı 4 → 2: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Üretim panelinin varsayılanını ölçen testi ve dokunulmayan iki şeyi tutan iki nöbetçiyi
yazmak; takımı kırmızı commit'lemek.

**Architecture:** İki test dosyası, üç test. Ölçülen şey tek bir başlangıç değeri.

**Tech Stack:** vitest, @testing-library/react, jsdom.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-18-varyant-varsayilani-testler-design.md)

## Global Constraints

- **Bu döngüde ürün kodu değişmiyor.**
- `skip` / `xfail` yok — kırmızı kırmızı commit ediliyor.
- Yorumlar **İngilizce**, ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/GeneratePanel.test.jsx` | varsayılan ve kayıtlı sayı | 2 yeni |
| `.../photo_generation/LayerPanel.test.jsx` | katman panelinin kendi varsayılanı | 1 yeni |

---

### Task 1: Üretim panelinin varsayılanı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.test.jsx`

- [ ] **Step 1: İki test**

`describe("GeneratePanel — the variant box")` içine, `refuses a value outside 1-26`'nın üstüne:

```jsx
  it("opens at two when the project has never saved a count", () => {
    // A project with nothing saved is what a new one looks like, and two is what the user asked
    // the box to start at (İstek 8).
    renderPanel({ settings: { ...SETTINGS, variants: null } });

    expect(variantBox().value).toBe("2");
  });

  it("opens at the saved count rather than the default", () => {
    // The default is for an empty setting, not a correction: a project saved with four keeps
    // four, whatever a new one now starts at.
    renderPanel({ settings: { ...SETTINGS, variants: 6 } });

    expect(variantBox().value).toBe("6");
  });
```

- [ ] **Step 2: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: ilki kırmızı (bugün 4), ikincisi bugün de geçiyor.

---

### Task 2: Katman panelinin kendi varsayılanı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`

- [ ] **Step 1: Nöbetçi**

`describe("LayerPanel — variants")` içine, `multiplies the estimate by the variant count`'un
üstüne:

```jsx
  it("opens at one, whatever the photo panel's default is", () => {
    // İstek 8's second sentence: the photo panel's default moved and this one did not. Two panels,
    // two decisions -- and a shared number would have made one of them follow the other.
    renderPanel();

    expect(variantBox().value).toBe("1");
  });
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: üçü yeşil (384 / 474 / 694), queen-editor frontend'de **478 testin 1'i kırmızı**.

---

### Task 3: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): the photo panel is asked what an empty count starts at

One line of the app chooses this number. The server has no default at all -- it wants an
integer between 1 and 26 and refuses anything else -- and a project that has never saved one
reads back as null, so the panel is the only place a first value comes from.

Two of the three tests are green the day they are written, and both hold something this
change must not reach. A project saved with a count of its own keeps it: the default is for
an empty setting, not a correction applied to what the user already chose. And the layer
panel still opens at one, which is the second sentence of the request itself -- two panels,
two decisions, and a number shared between them would have made one follow the other.

478 tests, 1 red.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in üç kararından ikisi test (1, 2); üçüncüsü bir yorum düzeltmesi ve
uygulama turunda.

**Tip tutarlılığı:** `variantBox()` iki dosyada da `getByRole("spinbutton")`; ikisi de dizeyle
karşılaştırıyor, çünkü kutu metin tutuyor.

**Kontrol edilen tuzak:** `SETTINGS` fixture'ı `variants: 4` taşıyor, yani varsayılan hiç devreye
girmiyor. Varsayılanı ölçen test `null` vermek zorunda — fixture'ı olduğu gibi kullanan bir test
bugünkü 4'ü ölçer ve yarın da geçerdi.

**Kontrol edilen tuzak 2:** aynı `describe` içindeki `refuses a value outside 1-26` testi 4'e geri
dönüyor ve o 4 **kayıtlı** ayardan geliyor, varsayılandan değil. Dokunulmuyor.

**Değişmeyen:** `GeneratePanel.jsx`, `LayerPanel.jsx`, `start_batch.py`.
