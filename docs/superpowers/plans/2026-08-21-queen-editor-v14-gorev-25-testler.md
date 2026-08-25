# v14 Görev 25 — Uyarı kendi kartına geçiyor: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Üretici eksikliğinin tür kartına inmesini on testle yazmak — sekizi yeni, ikisi var olanın
değişmesi. Hepsi kırmızı commit ediliyor.

**Architecture:** Ön yüzde iki test dosyası. Motor açılmıyor: farkın motor yarısı zaten doğru
(46. karar).

**Tech Stack:** vitest, @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-25-uretici-uyarisi-testler-design.md)

## Global Constraints

- **Üretim kodu bu döngüde değişmiyor.** Yeni modül yok, dolayısıyla kabuk da yok: iki test dosyası
  da var olan bileşenleri okuyor ve ikisi de toplanabilir kalıyor.
- **Yeni prop kırmızı turda tanımlanmıyor.** `QueuePanel` bu turda `producers` diye bir şey
  bilmiyor; React tanımadığı prop'a bakmaz, dolayısıyla test dosyası toplanır ve testler *iddia
  ettikleri* yerde düşer. Blueprint imzasının aksine burada genişletilecek bir kapı yok.
- **Değişen iki test kırmızıya dönüyor, silinmiyor.** İkisi de aynı yeri ölçmeye devam ediyor.
- Test adları ve yorumlar **İngilizce**; ekran metni **Türkçe**.
- `skip` / `xfail` yok — kırmızı kırmızı commit edilir.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `dist` bu commit'te **derlenmiyor**.

## File Structure

| Dosya | İşlem |
|---|---|
| `.../research/2026-08-20-queen-editor-tasarim-v4-farklari.md` | 46. karar |
| `frontend/.../photo_generation/QueuePanel.test.jsx` | 7 test eklenir, 2 test değişir |
| `frontend/.../photo_generation/SidePanel.test.jsx` | 1 test |

---

### Task 1: 46. karar kaynağına

**Files:**
- Modify: `docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md`

- [ ] **Step 1: Tarih notunu 25. maddeyle genişlet**

`*(21 Ağustos 2026, 13, 15, 20, 21, 22, 23 ve 24. madde uygulanırken.)*` →
`*(21 Ağustos 2026, 13, 15, 20, 21, 22, 23, 24 ve 25. madde uygulanırken.)*`

- [ ] **Step 2: Bir satır ekle**

45. satırın altına:

```markdown
| 46 | **Fark 38'in motor yarısı zaten doğru; değişen yalnız panel.** `queue.ORDER` foto → video → ses ve motor bir türü bitirmeden ötekine başlamıyor: her tür kendi üreticisini yüklüyor, aralarında zıplamak her turda bir model yeniden yüklerdi, ve bir video üstüne asıldığı fotoğrafın önce var olmasını istiyor. Sırayı koruyan bir test de var. Yani "diğer türler normal akar, sıra o türe gelince motor bekler" bugün de böyle. Bu maddenin işi panelin **ne zaman ve nerede** konuştuğu: eksiklik, motor o türe gelene kadar hiç söylenmiyordu. | 38 |
```

---

### Task 2: `QueuePanel.test.jsx` — tür kartının kendi uyarısı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/QueuePanel.test.jsx`

**Interfaces:**
- Consumes: `renderPanel(props)` (dosyada var), `RUNNING`.
- Produces: `MISSING` / `HERE` üretici satırları — 9. test de onları kullanıyor.

- [ ] **Step 1: Üretici satırlarını dosyanın başına koy**

`RUNNING`'in altına:

```jsx
// The producer list as the app asks for it once at startup: what is installed cannot change while
// the process is up, because installing happens in the notebook before it starts.
const MISSING = [{ id: "photo", name: "Fotoğraf üreticisi", installed: true },
                 { id: "audio", name: "Ses üreticisi", installed: false }];
```

- [ ] **Step 2: Yedi testi kendi bloğunda yaz**

`QueuePanel — a queue with nobody to do the work` bloğunun **üstüne**:

```jsx
describe("QueuePanel — a producer that is not on the machine", () => {
  const BOTH = [{ layer: "photo", owed: 4 }, { layer: "audio", owed: 2 }];
  const card = (layer) => document.querySelector(`[data-kind="${layer}"]`);

  it("says so on the card of the kind it belongs to", () => {
    renderPanel({ queue: BOTH, producers: MISSING });

    // Fark 38: the answer has been in hand since startup, so there is no reason to keep it until
    // the engine reaches that kind.
    expect(card("audio").textContent).toContain("Üretici kurulu değil.");
    expect(card("audio").textContent).toContain("Kur");
  });

  it("asks for that kind's producer when its Kur is pressed", () => {
    const onInstall = vi.fn();
    renderPanel({ queue: BOTH, producers: MISSING, onInstall });

    fireEvent.click(card("audio").querySelector("button"));

    expect(onInstall).toHaveBeenCalledWith("audio");
  });

  it("leaves the card that has something to say readable", () => {
    renderPanel({ queue: BOTH, producers: MISSING });

    // A warning written at .55 is a warning nobody reads. Waiting its turn and having something to
    // say are two different states, and only the first one steps back.
    expect(card("audio").style.opacity).toBe("");
    expect(card("photo").style.opacity).toBe("0.55");
  });

  it("says nothing on the cards whose producers are here", () => {
    renderPanel({ queue: BOTH, producers: MISSING });

    expect(card("photo").textContent).not.toContain("Üretici kurulu değil.");
  });

  it("lets the queue go on flowing while the warning waits on its own card", () => {
    renderPanel({ job: { ...RUNNING, current: { id: "P0_0", type: "photo" } },
                  queue: BOTH, producers: MISSING });

    // The roadmap's own acceptance sentence: photos flow, and the sound producer's absence is
    // already on the sound card rather than taking the panel over.
    expect(card("photo").querySelector(".qe-dot--alive")).toBeTruthy();
    expect(card("audio").textContent).toContain("Üretici kurulu değil.");
    expect(screen.queryByText("Bekliyor — üretici kurulu değil")).toBeNull();
  });

  it("prints the answer the app has on the same card", () => {
    const noted = MISSING.map((row) => (row.id === "audio"
      ? { ...row, note: "Bu üretici Colab defterinden kurulur — app.ipynb'de kutusunu işaretleyip çalıştır." }
      : row));
    renderPanel({ queue: BOTH, producers: noted });

    // Kur installs nothing (karar 5): it writes the one sentence the app can answer with, and the
    // sentence belongs where the button is.
    expect(card("audio").textContent).toContain("Colab defterinden kurulur");
  });

  it("says nothing at all before the list of producers has landed", () => {
    renderPanel({ queue: BOTH, producers: null });

    expect(card("audio").textContent).not.toContain("Üretici kurulu değil.");
  });
});
```

- [ ] **Step 3: İki testi değiştir**

`offers the one button that would unblock it, by name`:

```jsx
  it("keeps no install button of its own: that one is on the kind's card", () => {
    renderPanel({ job: WAITING, queue: [{ layer: "video", owed: 5 }],
                  producers: [{ id: "video", name: "Video üreticisi", installed: false }] });

    // Fark 38: the run card no longer carries what belongs to one kind.
    expect(screen.queryByText("Video üreticisini kur")).toBeNull();
    expect(document.querySelector('[data-kind="video"]').textContent).toContain("Kur");
  });
```

`offers the way on only once the producer is really here`:

```jsx
  it("offers the way on only once the producer is really here", () => {
    const onResume = vi.fn();
    renderPanel({ job: WAITING, queue: [{ layer: "video", owed: 5 }], onResume,
                  producers: [{ id: "video", name: "Video üreticisi", installed: true }] });

    fireEvent.click(screen.getByText("Kaldığı yerden devam et"));

    expect(onResume).toHaveBeenCalled();
    // The panel reads the rows it already has rather than being told the answer twice.
    expect(document.querySelector('[data-kind="video"]').textContent)
      .not.toContain("Üretici kurulu değil.");
  });
```

- [ ] **Step 4: Koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: FAIL — yedi yeninin beşi ve iki değişen kırmızı; 4 ve 7 doğuştan yeşil.

---

### Task 3: `SidePanel.test.jsx` — kablolama

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/SidePanel.test.jsx`

- [ ] **Step 1: Testi `SidePanel — the icon rail` bloğunun sonuna yaz**

```jsx
  it("hands the queue panel the producer rows", () => {
    renderColumn({ queue: [{ layer: "video", owed: 3 }],
                   producers: { producers: [
                     { id: "video", name: "Video üreticisi", installed: false }], error: null } });

    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    // The wiring is the half that breaks silently: the panel can only say what it was given.
    expect(document.querySelector('[data-kind="video"]').textContent)
      .toContain("Üretici kurulu değil.");
  });
```

- [ ] **Step 2: Koş**

Run: `npm test --prefix queen-editor/frontend`
Expected: FAIL — kart uyarıyı taşımıyor.

---

### Task 4: Dört komut ve kırmızı commit

- [ ] **Step 1: Dört komutu da koş**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: ilk üçü yeşil (384 / 474 / 709); dördüncüsü 541 testin **8'i kırmızı**.

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/specs/2026-08-21-queen-editor-v14-gorev-25-uretici-uyarisi-testler-design.md docs/superpowers/plans/2026-08-21-queen-editor-v14-gorev-25-testler.md docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md queen-editor/frontend/src/features/photo_generation/QueuePanel.test.jsx queen-editor/frontend/src/features/photo_generation/SidePanel.test.jsx
git commit -m @'
test(queen-editor): a missing producer speaks from its own card
'@
```

Çift tırnak yok, amend yok.
