# v14 Görev 13 — Seçim barının görünümü: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Barın iki yeni kuralını dört testle yazmak ve kırmızı commit etmek. Kaynak kodda tek satır
değişmiyor.

**Architecture:** Tek dosya, tek blok. Üçü barın bugünkü testlerinin yanına, biri katman
düğmelerinin kendi bloğuna.

**Tech Stack:** React 18 + vitest + @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-13-secim-bari-testler-design.md)

## Global Constraints

- **Bu tur yalnız test yazar.** `frontend/src` altındaki kaynak dosyalar değişmiyor.
- Test adları ve yorumlar **İngilizce**; ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `skip` / `xfail` yok.
- **Barın konumu bu maddede değişmiyor**: `floats the selection bar clear of the bottom edge`
  testi 28px demeye devam ediyor (spec, "Fark 84 bu maddede yapılmıyor").

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/features/photo_generation/Gallery.test.jsx` | bar | 4 test |

---

### Task 1: Bekleyen kare varsa katman düğmeleri yok

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

**Interfaces:**
- Consumes: Gallery'nin bugünkü `onRemoveLayer` prop'u; yeni ad yok.

- [ ] **Step 1: İki testi yaz**

`describe("Gallery — taking a layer off many frames", …)` bloğunun sonuna, son testin altına:

```jsx
  it("draws no layer buttons while a frame that is not produced is in the selection", () => {
    // What these two take off is a finished stack, and the queue is still writing into that one.
    renderGallery({ frames: [withSound("2_a.png"), pending("1_a.png")],
                    onRemoveLayer: remover() });
    pick("2_a.png", "1_a.png");

    expect(screen.queryByText("Videoları sil")).toBeNull();
    expect(screen.queryByText("Sesleri sil")).toBeNull();
    // The frames themselves can still go, and the produced one can still be copied.
    expect(screen.getByText("Sil")).toBeTruthy();
    expect(screen.getByText("Kopyala")).toBeTruthy();
  });

  it("leaves three buttons in the bar when only frames that are not produced are selected", () => {
    renderGallery({ frames: [pending("2_a.png"), pending("1_a.png")],
                    onCopy: vi.fn(), onRemoveLayer: remover() });
    pick("2_a.png");

    const bar = screen.getByText("1 seçili").parentElement;
    const words = [...bar.querySelectorAll("button")].map((one) => one.textContent.trim());
    expect(words).toEqual(["Tümünü seç", "Sil", "Vazgeç"]);
  });
```

- [ ] **Step 2: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: ilki kırmızı; ikincisi doğuştan yeşil (spec, "Doğuştan yeşil").

---

### Task 2: Boşluk ve tek satır

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.test.jsx`

- [ ] **Step 1: İki testi yaz**

`floats the selection bar clear of the bottom edge` testinin hemen altına:

```jsx
  it("narrows the space between the bar's items", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    // Six buttons now, and 14 was a bar with three (Fark 83).
    expect(screen.getByText("1 seçili").parentElement.style.gap).toBe("10px");
  });

  it("keeps every button's words on one line", () => {
    renderGallery();
    fireEvent.click(checkOf("1_a.png"));

    // Whether the bar really fits on one line is a question jsdom cannot answer -- it computes no
    // layout. What it can hold is the rule that keeps a label from breaking in two, and that also
    // stops a flex item shrinking below its own text.
    expect(screen.getByText("1 seçili").parentElement.style.whiteSpace).toBe("nowrap");
  });
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: queen-agent'ın ikisi yeşil (384 / 474), queen-editor python yeşil (694). queen-editor
frontend'de **3 kırmızı**.

---

### Task 3: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): the selection bar shrinks to what the selection can be

Four tests for the bar's own rules. The two layer buttons are not drawn at all while a
frame that is not produced is in the selection: what they take off is a finished stack, and
the queue is still writing into that one. A selection of nothing but pending frames leaves
the three buttons every selection has. Kopyala does not take this rule -- a mixed selection
keeps it.

The space between the bar's items narrows to 10, and no button's words may break in two.
Whether the bar really fits on one line is a question jsdom cannot answer, so what the test
holds is the rule that keeps a label whole -- which is also what stops a flex item
shrinking below its own text. The other half of never wrapping, items not falling to a
second row, is flex's own default and needs no code to say so.

The bar's position is not touched. Fark 84 asks for 20 pixels, but 28 is not a drift -- it
is the answer given to the user's own finding that the bar read as stuck to the floor, and
20 is the value they said that about. The fark list's own rule has an exception for exactly
this, and it did not catch this one. The question goes to the user in plain words.

One of the four is born green: with a pending-only selection, Kopyala is already absent by
the copy rule and the layer buttons by the layer rule. It takes up its watch once the new
rule keeps the same three buttons for a different reason.

queen-agent green (384 / 474). queen-editor python green (694). Frontend: 3 red.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in dört testi Task 1 (1–2), Task 2 (3–4).

**Tip tutarlılığı:** üç test barı `screen.getByText("N seçili").parentElement` ile buluyor — bugünkü
düğme sırası testinin kullandığı yolun aynısı.

**Kontrol edilen tuzak:** 1 numaralı test seçime videolu **ve** sesli bir kare koyuyor, yani iki
düğme de bugünkü kuralla çizilirdi; yokluğu bekleyen kareden geliyor, seçimin boşluğundan değil.

**Kontrol edilen tuzak 2:** aynı test `Sil` ve `Kopyala`nın kaldığını da ölçüyor — yeni kuralın
komşularına bulaşmadığının nöbeti.

**Kontrol edilen tuzak 3:** `style.gap` ve `style.whiteSpace` satır içi biçimden okunuyor; bar
biçimini `BAR` sabitinden alıyor, yani ikisi de gerçekten orada.

**Bilerek dışarıda:** barın konumu. Bugünkü 28px testi olduğu gibi duruyor.
