# v14 Görev 26 — Kuyruk panelinin görsel hizalaması: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Kuyruk panelinin yedi farkını on bir testle yazmak — altısı yeni, beşi var olanın
değişmesi. Hepsi kırmızı commit ediliyor.

**Architecture:** Ön yüzde tek test dosyası. Motor açılmıyor.

**Tech Stack:** vitest, @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-26-kuyruk-hizalamasi-testler-design.md)

## Global Constraints

- **Üretim kodu bu döngüde değişmiyor.** Yeni modül yok, kabuk yok.
- **26. maddeye dokunulmuyor.** Bekleme kartının cümlesi ve kuyruğun kendiliğinden sürüp sürmeyeceği
  bu turun konusu değil; 47. fark yalnız beklerken bir düğmenin görünmesini istiyor.
- Test adları ve yorumlar **İngilizce**; ekran metni **Türkçe**.
- `skip` / `xfail` yok — kırmızı kırmızı commit edilir.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `dist` bu commit'te **derlenmiyor**.

## File Structure

| Dosya | İşlem |
|---|---|
| `.../research/2026-08-20-queen-editor-tasarim-v4-farklari.md` | 47–49. kararlar |
| `frontend/.../photo_generation/QueuePanel.test.jsx` | 6 test eklenir, 5 test değişir |

---

### Task 1: 47–49. kararlar kaynağına

**Files:**
- Modify: `docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md`

- [ ] **Step 1: Tarih notunu 27. maddeyle genişlet**

`… 24 ve 25. madde uygulanırken.` → `… 24, 25 ve 27. madde uygulanırken.`

- [ ] **Step 2: Üç satır ekle**

46. satırın altına:

```markdown
| 47 | **Fark 48 düşüyor — "kare" kalıyor.** 4. kararın kapattığı sorunun aynısı: tasarımın terminoloji kuralı içerik birimi için "kare" diyor, çizimi bazı cümlelerde "fotoğraf" diyor ve o sözcük terminoloji netleşmeden önceki dilden kalmış. 4. karar boş ekran metinleri için verilmişti; gerekçe sözcüğün kendisine ait. | 48 |
| 48 | **Fark 50 düşüyor — ham çıktı kutusu kalıyor.** İstenen tek satır zaten ilk satır: kart kuralın cümlesini üstte, servisin cevabını altındaki kutuda gösteriyor. Kalkması istenen cümle değil kanıt, ve deponun kuralı hata mesajında sebep uydurmayı yasaklıyor — uygulama tasarımın örnek cümlesindeki sentezlenmiş teşhisi üretemez, üretirse uydurur. Kutu ayrıca uzun çıktının düğmeleri panelden itmemesi için yazılmış ve kopyalanabilir olması kullanıcının hatayı taşıyabilmesinin tek yolu. | 50 |
| 49 | **Fark 59 zaten kapandı.** 25. maddede kurulum düğmesi koşu kartından tür kartına indi ve orada yalnız "Kur" yazıyor; "Video üreticisini kur" hiç kalmadı. | 59 |
```

---

### Task 2: `QueuePanel.test.jsx` — başlık, sayı, nokta, cümle

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/QueuePanel.test.jsx`

- [ ] **Step 1: İki başlık testini tireye çevir**

`draws the kind's own card and no run card of its own` içinde:
`screen.getByText("Foto · üretiliyor")` → `screen.getByText("Foto — üretiliyor")`

`puts the queue's own card beside the run's, each answering its own question` içinde:
`screen.getByText("Foto · sırada")` → `screen.getByText("Foto — sırada")`

- [ ] **Step 2: Üç yeni testi akan kuyruk bloğuna yaz**

`QueuePanel — a flowing queue` bloğunun sonuna:

```jsx
  it("colours the running kind's number as text and the waiting one's as a whisper", () => {
    renderPanel({ job: { ...RUNNING, current: { id: "P0_0", type: "photo" } },
                  queue: [{ layer: "photo", owed: 1 }, { layer: "video", owed: 3 }] });

    // Fark 42: the accent stays on the heading row, where the dot is. Three numbers in the same
    // loud colour made the panel one big counter and said nothing about which is moving.
    const number = (layer) => document.querySelector(`[data-kind="${layer}"] .wf-mono`);
    expect(number("photo").style.color).toBe("var(--ink)");
    expect(number("video").style.color).toBe("var(--ink-3)");
  });

  it("lets the dot fade while the pause is on its way", () => {
    renderPanel({ stopping: true });

    // Fark 43: still beating, because the engine is still turning -- but no longer in the colour
    // that means work is flowing.
    const dot = document.querySelector("[data-run-card] .qe-dot");
    expect(dot.className).toContain("qe-dot--alive");
    expect(dot.style.background).toBe("var(--ink-3)");
    expect(screen.getAllByText("Duraklatılıyor…")[0].style.color).toBe("var(--ink-3)");
  });
```

- [ ] **Step 3: Üreticisi eksik türün başlığını yaz**

`QueuePanel — a producer that is not on the machine` bloğunun sonuna:

```jsx
  it("reads the heading of a kind with nobody to do the work as waiting", () => {
    renderPanel({ queue: BOTH, producers: MISSING });

    // Fark 41: three states, three words. "sırada" says a turn is coming; this one's turn cannot
    // come until something lands on the machine.
    expect(card("audio").textContent).toContain("Ses — bekliyor");
    expect(card("photo").textContent).toContain("Foto — üretiliyor");
  });
```

- [ ] **Step 4: Tamamlandı kartının cümlesini yaz**

`QueuePanel — a finished queue` bloğuna:

```jsx
  it("keeps the green for the heading and says the count quietly", () => {
    renderPanel({ job: { status: "done", project: "düğün", done: 20, failed: 0, total: 20 },
                  queue: [] });

    // Fark 44: the heading carries the good news; the number under it is a fact, not a second
    // announcement.
    expect(screen.getByText("Kuyruk tamamlandı").style.color).toBe("var(--ok)");
    expect(screen.getByText("20 kare üretildi").style.color).toBe("var(--ink-3)");
  });
```

- [ ] **Step 5: Koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: FAIL — iki başlık, iki renk, bir nokta, bir cümle.

---

### Task 3: `QueuePanel.test.jsx` — hata kartı ve boşaltma

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/QueuePanel.test.jsx`

- [ ] **Step 1: Üç hata kartı testini tamamlanmış kuyruğa ve yeni yazıya çevir**

`keeps the good news to itself and gives the failures their own card` içinde:
`screen.getByText("Hepsini tekrar dene")` → `screen.getByText("Tekrar dene")`

`breaks the total down only when more than one kind failed`:

```jsx
  it("breaks the total down only when more than one kind failed", () => {
    renderPanel({ job: { status: "done", project: "düğün", done: 20, failed: 3, total: 23 },
                  queue: [], failures: [{ layer: "photo", count: 2 }, { layer: "video", count: 1 }] });

    // The dot between the kinds stays: that one is a list, not a state (fark 41).
    expect(screen.getByText("3 kare üretilemedi — 2 foto · 1 video")).toBeTruthy();
  });
```

`puts every red job back in line at once, instead of pointing at the gallery`:

```jsx
  it("puts every red job back in line at once, instead of pointing at the gallery", () => {
    const onRetryAll = vi.fn();
    renderPanel({ job: { status: "done", project: "düğün", done: 20, failed: 3, total: 23 },
                  queue: [], failures: [{ layer: "photo", count: 3 }], onRetryAll });

    fireEvent.click(screen.getByText("Tekrar dene"));

    expect(onRetryAll).toHaveBeenCalled();
    expect(screen.queryByText(/galeride göster/)).toBeNull();
  });
```

- [ ] **Step 2: Kartın ne zaman doğduğunu yaz**

`QueuePanel — the failures card` bloğuna:

```jsx
  it("waits for the queue to finish before it says anything", () => {
    const flowing = renderPanel({ failures: [{ layer: "photo", count: 3 }] });
    expect(screen.queryByText(/üretilemedi/)).toBeNull();
    flowing.unmount();

    // Fark 46: paused too. A total that is still growing is not a total, and the red frames are
    // already red in the gallery with a Tekrar dene each.
    renderPanel({ job: { status: "paused", project: "düğün", done: 7, failed: 3, total: 48 },
                  queue: [{ layer: "photo", owed: 2 }], failures: [{ layer: "photo", count: 3 }] });
    expect(screen.queryByText(/üretilemedi/)).toBeNull();
  });
```

- [ ] **Step 3: Beklerken boşaltmayı yaz**

`QueuePanel — a queue with nobody to do the work` bloğuna:

```jsx
  it("can be emptied while it waits", () => {
    const onCancel = vi.fn();
    renderPanel({ job: WAITING, queue: [{ layer: "video", owed: 5 }], onCancel });

    // Fark 47: emptying is safe exactly when nothing is being rendered, and a queue waiting for a
    // producer has nothing in hand -- so there is no reason for the way out to be missing here.
    fireEvent.click(screen.getByText("Kuyruğu boşalt"));
    fireEvent.click(screen.getByText("Boşalt"));

    expect(onCancel).toHaveBeenCalled();
  });
```

- [ ] **Step 4: Koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: FAIL — toplam 10 kırmızı. `breaks the total down…` doğuştan yeşil: kart bugün her hâlde
çiziliyor, dolayısıyla tamamlanmış kuyrukta da çiziliyor.

---

### Task 4: Dört komut ve kırmızı commit

- [ ] **Step 1: Dört komutu da koş**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: ilk üçü yeşil (384 / 474 / 709); dördüncüsü 547 testin **10'u kırmızı**.

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/specs/2026-08-21-queen-editor-v14-gorev-26-kuyruk-hizalamasi-testler-design.md docs/superpowers/plans/2026-08-21-queen-editor-v14-gorev-26-testler.md docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md queen-editor/frontend/src/features/photo_generation/QueuePanel.test.jsx
git commit -m @'
test(queen-editor): the queue panel gets its tones
'@
```

Çift tırnak yok, amend yok.
