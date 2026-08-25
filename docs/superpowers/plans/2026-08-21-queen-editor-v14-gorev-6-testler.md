# v14 Görev 6 — Tahmin ve onay metinleri moda göre değişiyor: TEST döngüsü (test planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Panelin iki cümlesini — butonun altındaki tahmin ve eklendikten sonraki yeşil onay —
seçilen moda ve kapsamdaki kopya karelere bağlayan on bir testi yazmak ve kırmızı bırakmak.

**Architecture:** Tek test dosyası. On yeni test iki yeni blokta, bir eski testin beklentisi
düzeltiliyor. Kaynak dosyaya bu turda dokunulmuyor.

**Tech Stack:** vitest, @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-6-mod-metinleri-testler-design.md)

## Global Constraints

- **Yalnız test dosyası değişiyor.** `LayerPanel.jsx` ve `production_modes.js` bu turda el
  değmeden kalıyor — kırmızının anlamı bu.
- **`skip` / `xfail` yok.** Kırmızı kırmızı commit ediliyor.
- Test adları ve yorumları **İngilizce**; ekranda aranan metinler **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komutlar dört satır, birebir, boru yok:
  ```
  python -m pytest queen-agent -q
  npm test --prefix queen-agent/frontend
  python -m pytest queen-editor -q
  npm test --prefix queen-editor/frontend
  ```
- **`dist` bu turda derlenmiyor** — ön yüz kaynağı değişmiyor.

## Beklenen cümleler

Testler bu metinleri harfi harfine arıyor; uygulama turu bunları üretmek zorunda.

| Durum | Cümle |
|---|---|
| Loop tahmini | `2 loop video üretilecek — her video kendine döner.` |
| Bağlı tahmin | `2 bağlı video üretilecek — her video sıradaki karede biter.` |
| Loop onayı | `2 loop video kuyruğa eklendi` |
| Video kopya uyarısı | `1 video üretilecek — videolu 1 kare için yeniler kopya kare olur, eskisi durur.` |
| Loop + kopya | `1 loop video üretilecek — videolu 1 kare için yeniler kopya kare olur, eskisi durur.` |
| İki karelik kopya | `2 video üretilecek — videolu 1 kare için yeniler kopya kare olur, eskisi durur.` |
| Ses kopya uyarısı | `1 ses üretilecek — sesi olan 1 kare için yeniler kopya kare olur, eskisi durur.` |

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/features/photo_generation/LayerPanel.test.jsx` | panelin nöbeti | iki blok eklenir, bir beklenti düzeltilir |

---

### Task 1: Tahmin modu söylüyor

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`

**Interfaces:**
- Consumes: dosyanın tepesindeki `FRAMES`, `renderPanel`, `variantBox`. Yeni bir yardımcı
  eklenmiyor; `modeRow` bloğun kendi içinde, öteki iki blokta olduğu gibi.

- [ ] **Step 1: Bloğu yaz**

`LayerPanel — linking wants neighbours` bloğunun altına, `LayerPanel — sound` bloğunun üstüne:

```jsx
describe("LayerPanel — the estimate speaks the mode", () => {
  const modeRow = (label) => screen.getByText(label).closest("button");

  it("says what a loop video is and what it does", () => {
    renderPanel();

    fireEvent.click(modeRow("Loop"));

    expect(screen.getByText("2 loop video üretilecek — her video kendine döner.")).toBeTruthy();
  });

  it("says what a linked video is and where it ends", () => {
    renderPanel();

    fireEvent.click(modeRow("Sonrakine bağla"));

    expect(screen.getByText("2 bağlı video üretilecek — her video sıradaki karede biter."))
      .toBeTruthy();
  });

  it("leaves no trace of the plain sentence once a mode is picked", () => {
    // The whole point of the item: three modes, three sentences, and the old single template gone
    // from all of them. Asserting the new sentence alone would pass with both on screen.
    renderPanel();

    fireEvent.click(modeRow("Loop"));

    expect(screen.queryByText(/her kare kendi videosunu alır/)).toBeNull();
  });

  it("confirms in the mode's own words", async () => {
    renderPanel({ onQueue: () => Promise.resolve({ added: 2 }) });

    fireEvent.click(modeRow("Loop"));
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(screen.getByText("2 loop video kuyruğa eklendi")).toBeTruthy();
  });

  it("keeps the words the queue was actually sent with", async () => {
    // The card stands for ten seconds and the row is one click away. Reading the live mode would
    // let it report a loop run that was never asked for.
    renderPanel({ onQueue: () => Promise.resolve({ added: 2 }) });

    fireEvent.click(modeRow("Loop"));
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });
    fireEvent.click(modeRow("Standart"));

    expect(screen.getByText("2 loop video kuyruğa eklendi")).toBeTruthy();
  });
});
```

- [ ] **Step 2: Takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: bu bloğun beşi de kırmızı. Panel bugün `2 video üretilecek — her kare kendi videosunu
alır.` ve `2 video kuyruğa eklendi` yazıyor, aranan metinlerin hiçbiri ekranda yok.

---

### Task 2: Tahmin kopyayı haber veriyor

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`

**Interfaces:**
- Consumes: `FRAMES` (`1_a` videolu tek kare), `done` yardımcısı, `renderPanel`.

- [ ] **Step 1: Bloğu yaz**

Task 1'in bloğunun hemen altına:

```jsx
describe("LayerPanel — the estimate warns about copies", () => {
  const modeRow = (label) => screen.getByText(label).closest("button");
  const COPY = "videolu 1 kare için yeniler kopya kare olur, eskisi durur.";

  it("says a frame that already has this layer will gain a twin", () => {
    // Production never writes over a layer that is there: it makes a copy frame beside it. Until
    // now nothing said so and the gallery growing by one was the first news of it.
    renderPanel({ selected: ["1_a"] });

    expect(screen.getByText(`1 video üretilecek — ${COPY}`)).toBeTruthy();
  });

  it("counts only the frames in scope that hold the layer", () => {
    // Two frames go to the queue, one of them is the copy. The two numbers in the line are
    // different numbers and a single count would read as either.
    renderPanel({ selected: ["1_a", "0_a"] });

    expect(screen.getByText(`2 video üretilecek — ${COPY}`)).toBeTruthy();
  });

  it("never warns on the scope that leaves those frames out", () => {
    // Videosu olmayanlar cannot contain a frame with a video, so the count is zero by its own
    // definition rather than by a second rule about which scope may warn.
    renderPanel();

    expect(screen.queryByText(/kopya kare olur/)).toBeNull();
  });

  it("puts the warning where the mode's own line would have been", () => {
    // The mode is still said -- it is in the head of the sentence -- so nothing is lost by giving
    // the tail to the news the user has no other way of hearing.
    renderPanel({ selected: ["1_a"] });

    fireEvent.click(modeRow("Loop"));

    expect(screen.getByText(`1 loop video üretilecek — ${COPY}`)).toBeTruthy();
    expect(screen.queryByText(/kendine döner/)).toBeNull();
  });

  it("warns in the sound panel's own words", () => {
    const held = done("2_a.png", { video: "2_a_V1_0.mp4", audio: "2_a_A1_0.wav" });

    render(
      <LayerPanel layer="audio" frames={[done("0_a.png"), held]} selected={["2_a"]} producer={null}
                  onQueue={() => Promise.resolve({ added: 1 })} onInstall={() => {}} />,
    );

    expect(screen.getByText(
      "1 ses üretilecek — sesi olan 1 kare için yeniler kopya kare olur, eskisi durur."))
      .toBeTruthy();
  });
});
```

- [ ] **Step 2: Eski testin beklentisini düzelt**

`LayerPanel — variants` bloğundaki `counts a selected frame that already has a video`, bugünden
sonra kopya cümlesini üreten durumun ta kendisi. Ölçtüğü şey değişmiyor, cümlesi değişiyor:

```jsx
  it("counts a selected frame that already has a video", () => {
    // Picking it by hand is how a second video is asked for -- it becomes a copy frame.
    renderPanel({ selected: ["1_a"] });

    expect(screen.getByText("Seçili kareler").closest("button").textContent).toContain("1");
    expect(screen.getByText(
      "1 video üretilecek — videolu 1 kare için yeniler kopya kare olur, eskisi durur."))
      .toBeTruthy();
  });
```

- [ ] **Step 3: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: iki python takımı ve QueenAgent'ın ön yüzü yeşil. queen-editor'ün ön yüzü `43 tests | 10
failed` — Task 1'in beşi, Task 2'nin dördü, ve düzeltilen eski test.

**Onuncu değil dokuzuncu:** Task 2'nin *"never warns on the scope that leaves those frames out"*
testi doğuştan yeşil. Ölçtüğü şey bir yokluk, ve o yokluk bugün de doğru — kopya cümlesi henüz
hiçbir kapsamda yok. Uygulama turundan sonra nöbeti gerçek oluyor: cümle var olduğunda yalnız doğru
kapsamda çıktığını o test tutuyor. Bir yokluk testini kırmızıya zorlamanın tek yolu onu geçici
olarak yanlış yazmak olurdu.

---

### Task 3: Kırmızıyı commit et

- [ ] **Step 1: Kırmızı sayısını oku**

Bir önceki adımın çıktısındaki `failed` sayısı 10 olmalı. Değilse durup sebebini bul: azsa bir test
yanlışlıkla bugünkü davranışı tarif ediyor, fazlaysa test dosyasında ilgisiz bir şey kırılmış.

- [ ] **Step 2: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): the panel says which mode it is about to run

The estimate under the button and the green card after it both speak one sentence
whatever was picked. These tests give each mode its own words: loop makes a video that
returns to itself, linking makes one that ends on the next frame, and the plain mode
keeps the line it has.

The mode is said in the head of the sentence -- 2 loop video uretilecek -- so the tail
is free for news the user has no other way of hearing: a frame that already carries this
layer does not get written over, it gains a twin beside it. That warning takes the tail
and the sound panel says it in its own word.

The green card now has to remember the mode it was sent with. It stands for ten seconds
and the row is one click away, so reading the live mode would let it report a run nobody
asked for.

Ten red, the source untouched. The eleventh is born green: it measures an absence, and
the sentence it forbids does not exist yet. Its watch starts once the sentence does.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in on testi Task 1'de beş, Task 2'de beş. 5. karar (`owed` olduğu gibi
kalıyor) bilerek testsiz — bir sınırın nöbeti olmaz, ve bağlı modda atlanan kareyi ölçen bir test
panele motorun kuralını kopyalatmaya zorlardı.

**Tip tutarlılığı:** `renderPanel` bugünkü imzasıyla çağrılıyor (`{ selected, onQueue, frames }`),
ses testi `render`'ı doğrudan kullanıyor — `renderSound` başka blokta ve orası `SOUND_FRAMES`'e
bağlı, oysa bu testin videolu **ve** sesli bir kareye ihtiyacı var.

**Kontrol edilen tuzak:** 3. test (`leaves no trace`) `queryByText(...).toBeNull()` diyor. Yalnız
yeni cümleyi aramak, iki cümlenin yan yana durduğu bir uygulamada da yeşil olurdu.

**Kontrol edilen tuzak 2:** 7. test iki farklı sayı taşıyor (2 ve 1). Tek sayılı bir örnek, kopya
sayısını kapsam sayısıyla karıştıran bir uygulamayı ayırt edemezdi.

**Kontrol edilen tuzak 3:** 5. test onayı bekledikten **sonra** satıra tıklıyor. Önce tıklasaydı
gönderilen mod da standart olurdu ve test hiçbir şeyi ayırt etmezdi.

**Kontrol edilen tuzak 4:** 9. test hem yeni kuyruğu arıyor hem modun kuyruğunun gitmiş olduğunu.
Yalnız birincisi, iki kuyruğu birbirine ekleyen bir uygulamada da geçerdi.

**Kırmızının dürüstlüğü:** onu da `getByText` / `queryByText` hatası olarak düşüyor, yani takım
koşuyor ve geri kalan testler ölçülüyor. Bu turda içe aktarılan yeni bir isim yok — koleksiyon
hatası doğmuyor.

**Doğuştan yeşil olan:** on bir testin biri (`never warns on the scope…`) bugün de geçiyor, çünkü
ölçtüğü şey bir yokluk. Task 2 Step 3'te yazıldı; bir yokluk testini kırmızıya zorlamak onu geçici
olarak yanlış yazmak demek olurdu ve turun tek kuralı bunun tersi.
