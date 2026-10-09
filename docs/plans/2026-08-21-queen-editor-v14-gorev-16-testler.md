# v14 Görev 16 — Panel hata dili: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Katman panelinin dört sebebini, kırmızı kartını, kırmızı varyant kutusunu ve kilidini
kalkmış butonunu ölçen testleri yazmak; takımı kırmızı commit'lemek.

**Architecture:** Tek test dosyası. Yeni bir blok video tarafının on iki cevabını, mevcut `sound`
bloğu ses tarafının üçünü alıyor.

**Tech Stack:** vitest, @testing-library/react, jsdom.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-16-panel-hata-dili-testler-design.md)

## Global Constraints

- **Bu döngüde ürün kodu değişmiyor.**
- `skip` / `xfail` yok — kırmızı kırmızı commit ediliyor.
- Yorumlar **İngilizce**, ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- Cümlelerin sonunda `— üretilecek bir şey yok` **yok**; testler cümleleri birebir yazıyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/LayerPanel.test.jsx` | reddin sebebi, kırmızı kart, kutu, kilit | 15 yeni, 2 silinen |

---

### Task 1: Bugünkü iki boş-kapsam testini sil

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`

- [ ] **Step 1: Video tarafı**

`describe("LayerPanel — the scope")` içinden şu test siliniyor:

```jsx
  it("says there is nothing to do rather than treating it as a fault", () => {
    renderPanel({ frames: [done("1_a.png", { video: "1_a_V1_0.mp4" })] });

    expect(screen.getByText("Tüm karelerin videosu var — üretilecek bir şey yok.")).toBeTruthy();
    expect(screen.getByText("Kuyruğa ekle").closest("button").disabled).toBe(true);
  });
```

- [ ] **Step 2: Ses tarafı**

`describe("LayerPanel — sound")` içinden:

```jsx
  it("says there is nothing to do in its own words", () => {
    renderSound({ frames: [done("0_a.png")] });

    expect(screen.getByText("Videosu olup sesi olmayan kare yok — üretilecek bir şey yok."))
      .toBeTruthy();
  });
```

İkisi de bugünkü tek cümleyi ve basılmadan gelen kilidi ölçüyor; ikisi de 27 ve 28 ile düşüyor.

---

### Task 2: Reddin sebebi — video tarafı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`

**Interfaces:**
- Consumes: kırmızı kartın kutusu `.wf-stroke`, yeşil kartla aynı sınıf.

- [ ] **Step 1: Yeni blok ve yardımcıları**

`describe("LayerPanel — variants")`'ın altına:

```jsx
describe("LayerPanel — why the press was refused", () => {
  const addButton = () => screen.getByText("Kuyruğa ekle").closest("button");
  const press = () => fireEvent.click(addButton());
  // Every frame already carries the layer: the scope is empty and nothing is wrong.
  const ALL_HELD = [done("1_a.png", { video: "1_a_V1_0.mp4" })];
  // Nothing is a photo yet, so there is nothing to hang a video on at all.
  const NONE_MADE = [{ id: "3_a", file: "3_a.png", status: "pending", layers: {}, failed: [] }];
```

- [ ] **Step 2: Sakin panel ve dört sebep**

```jsx
  it("stays pressable with nothing to do, and says nothing until it is pressed", () => {
    renderPanel({ frames: ALL_HELD });

    expect(addButton().disabled).toBe(false);
    expect(screen.queryByText(/Tüm karelerin/)).toBeNull();
    expect(screen.queryByText(/üretilecek bir şey yok/)).toBeNull();
  });

  it("says all the frames already have one", () => {
    renderPanel({ frames: ALL_HELD });

    press();

    expect(screen.getByText("Tüm karelerin videosu var.")).toBeTruthy();
  });

  it("does not send a request it refused", () => {
    const onQueue = vi.fn();
    renderPanel({ frames: ALL_HELD, onQueue });

    press();

    expect(onQueue).not.toHaveBeenCalled();
  });

  it("says the project has nothing produced yet", () => {
    renderPanel({ frames: NONE_MADE });

    press();

    expect(screen.getByText("Henüz üretilmiş kare yok.")).toBeTruthy();
  });

  it("says the chosen frames are not photos yet", () => {
    // İstek 4.3, word for word: the frames the user picked have no picture, and the panel used to
    // blame them for already having videos.
    renderPanel({ selected: ["3_a"] });

    press();

    expect(screen.getByText("Seçili karelerin fotoğrafı henüz üretilmedi.")).toBeTruthy();
  });

  it("says the variant box is empty", () => {
    renderPanel();

    fireEvent.change(variantBox(), { target: { value: "" } });
    press();

    expect(screen.getByText("Varyant sayısı girilmedi — en az 1 yaz.")).toBeTruthy();
  });
```

- [ ] **Step 3: Kutu, silinme ve kılık**

```jsx
  it("turns the variant box red while it is empty", () => {
    renderPanel();
    expect(variantBox().style.borderColor).toBe("");

    fireEvent.change(variantBox(), { target: { value: "" } });

    expect(variantBox().style.borderColor).toBe("var(--danger)");
  });

  it("clears the reason as soon as the count is typed", () => {
    // Both halves, because the second one alone is true of a panel that never answers at all.
    renderPanel();
    fireEvent.change(variantBox(), { target: { value: "" } });
    press();
    expect(screen.getByText("Varyant sayısı girilmedi — en az 1 yaz.")).toBeTruthy();

    fireEvent.change(variantBox(), { target: { value: "2" } });

    expect(screen.queryByText("Varyant sayısı girilmedi — en az 1 yaz.")).toBeNull();
  });

  it("clears the reason when another scope is picked", () => {
    // The reason belongs to the press that made it -- the scope it named and the frames it
    // counted. Moving either one turns it into a stale answer under a button about to be pressed
    // again.
    renderPanel({ selected: ["3_a"] });
    press();
    expect(screen.getByText("Seçili karelerin fotoğrafı henüz üretilmedi.")).toBeTruthy();

    fireEvent.click(screen.getByText("Videosu olmayanlar").closest("button"));

    expect(screen.queryByText("Seçili karelerin fotoğrafı henüz üretilmedi.")).toBeNull();
  });

  it("dresses the reason as the green card's red twin", () => {
    renderPanel({ frames: ALL_HELD });

    press();

    const card = screen.getByText("Tüm karelerin videosu var.").closest(".wf-stroke");
    expect(card.style.borderColor).toBe("var(--danger)");
    expect(card.style.background).toBe("var(--danger-bg)");
  });
```

- [ ] **Step 4: Butonun iki hâli**

```jsx
  it("keeps the button pressable while the reason stands", () => {
    renderPanel({ frames: ALL_HELD });

    press();

    expect(screen.getByText("Tüm karelerin videosu var.")).toBeTruthy();
    expect(addButton().disabled).toBe(false);
  });

  it("locks the button only while the request is in flight", async () => {
    // The other half of the rule: nothing before the press locks it, and the one thing that does
    // lets go again.
    let land;
    renderPanel({ onQueue: () => new Promise((resolve) => { land = resolve; }) });
    expect(addButton().disabled).toBe(false);

    await act(async () => { press(); });

    expect(screen.getByText("Ekleniyor…").closest("button").disabled).toBe(true);
    await act(async () => { land({ added: 2 }); });
    expect(addButton().disabled).toBe(false);
  });
});
```

- [ ] **Step 5: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: on ikinin onu kırmızı; `does not send a request it refused` ve `locks the button only
while the request is in flight` bugün de geçiyor.

---

### Task 3: Reddin sebebi — ses tarafı

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`

- [ ] **Step 1: Üç test**

`describe("LayerPanel — sound")` içine, silinen testin yerine:

```jsx
  it("says all the frames already have a sound", () => {
    renderSound({ frames: [
      done("1_a.png", { video: "1_a_V1_0.mp4", audio: "1_a_V1_0_S1_0.wav" })] });

    fireEvent.click(screen.getByText("Kuyruğa ekle").closest("button"));

    expect(screen.getByText("Tüm karelerin sesi var.")).toBeTruthy();
  });

  it("says nothing has a video to lay a sound over", () => {
    // Not the video panel's sentence: what is missing under a sound is a video, not a photo. An
    // empty project reads this too, and it is the nearer thing that is missing.
    renderSound({ frames: [done("0_a.png")] });

    fireEvent.click(screen.getByText("Kuyruğa ekle").closest("button"));

    expect(screen.getByText("Videosu olan kare yok.")).toBeTruthy();
  });

  it("says the chosen frames have no video yet", () => {
    renderSound({ selected: ["0_a"] });

    fireEvent.click(screen.getByText("Kuyruğa ekle").closest("button"));

    expect(screen.getByText("Seçili karelerin videosu henüz üretilmedi.")).toBeTruthy();
  });
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: üçü yeşil (384 / 474 / 694), queen-editor frontend'de **467 testin 13'ü kırmızı**.

---

### Task 4: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): the layer panel is asked why, four ways

The complaint was one sentence: with unproduced frames selected the video panel said all the
frames already had videos. It said that because it only had one thing to say -- an empty
scope, whatever emptied it, printed the layer's single line and locked the button before
anyone had pressed it.

These tests give it four answers. Nothing produced yet, the chosen frames are not photos
yet, they all have one already, and the count box is empty. The sound panel answers in its
own terms: what is missing under a sound is a video, not a photo, so an empty project there
reads that no frame has a video rather than that none is produced.

The button is measured twice: pressable with nothing to do, and locked only while a request
is actually in flight. The reason arrives as the green card's red twin, in the same box in
the same place, and leaves as soon as the panel is touched again -- a reason is an answer to
one press, and the scope it named can move under it.

Two of the tests are green the day they are written. One says a refused press does not reach
the server, which is true today for a different reason -- the button is locked, so the click
does nothing at all. The other holds the one lock that stays. Neither is forced red.

The two tests measuring the old single sentence are gone.

467 tests, 13 red.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in dört kararı Task 2 (1, 2, 3, 4) ve Task 3 (2'nin ses yüzü).

**Tip tutarlılığı:** cümleler tek yerde, birebir yazılıyor; hiçbir test kalıp kurmuyor.

**Kontrol edilen tuzak:** `getByText("Kuyruğa ekle")` butonun kendisini döndürüyor — içindeki ikon
metin taşımıyor, ve `closest("button")` zaten kendisini veriyor. Aynı âdet dosyada zaten var.

**Kontrol edilen tuzak 2:** 15. testin kurgusu. `SOUND_FRAMES`'in ilki videosuz, ikincisi videolu;
seçim videosuzu gösteriyor, dolayısıyla kapsam boş ama `can` dolu — sebep "seçili karelerin
videosu yok" olmalı, "videosu olan kare yok" değil.

**Kontrol edilen tuzak 3:** `card.style.background` — kırmızı kart `var(--danger-bg)` değişkenini
satır içi yazıyor, tarayıcı onu olduğu gibi saklıyor. Rakam yok, normalleştirme yok.

**Koşuda çıkan tuzak 4:** iki "sebep siliniyor" testi ilk yazıldığında yeşil doğdu. Yokluğu ölçen
bir cümle, o şey hiç doğmuyorken de doğru — panel hiç cevap vermeseydi ikisi de geçerdi. İkisine de
**önce belirdiğini** söyleyen bir satır eklendi; şimdi yayın tamamını ölçüyorlar ve ikisi de
kırmızı.

**Değişmeyen:** `LayerPanel.jsx`, `GeneratePanel.jsx`. Bu döngüde ürün kodu yok.
