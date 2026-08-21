# v14 Görev 21 — Sağ panelin düzeni: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sağ sütunun dört farkını on testle yazmak — etiketler, sabit yükseklikler, kopyala ikonu,
iki grup ve tek ritim. On ikisi kırmızı commit ediliyor.

**Architecture:** Tek test dosyası, bir yeni `describe` bloğu ve üç düzeltilen test. Üretim kodu bu
döngüde değişmiyor.

**Tech Stack:** vitest, @testing-library/react, jsdom.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-21-panel-duzeni-testler-design.md)

## Global Constraints

- **Üretim kodu bu döngüde değişmiyor.** `data-side`, `data-group`, `data-box` ve ikonun
  `aria-label`'ı uygulama turunda geliyor.
- Test adları **İngilizce**, yorumlar **İngilizce**; ekran metni **Türkçe**.
- `skip` / `xfail` yok — kırmızı kırmızı commit edilir.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `dist` bu commit'te **derlenmiyor** — ön yüz kaynağı değişmiyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../research/2026-08-20-queen-editor-tasarim-v4-farklari.md` | kararların kaynağı | 33, 34, 35 eklenir |
| `.../photo_generation/PhotoDetail.test.jsx` | detay sayfasının testleri | 10 yeni, 3 düzeltilen |

---

### Task 1: 33, 34 ve 35. kararlar kaynağına yazılıyor

**Files:**
- Modify: `docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md`

- [ ] **Step 1: Tarih notu**

`*(21 Ağustos 2026, 13, 15 ve 20. madde uygulanırken.)*` →
`*(21 Ağustos 2026, 13, 15, 20 ve 21. madde uygulanırken.)*`

- [ ] **Step 2: Tabloya üç satır**

```markdown
| 33 | **Kopya ikonu cevabını kendi adında verir.** Tasarım yalnız "basınca metin panoya alınır" diyor; basıştan sonrasını söylemiyor. Sessizlik cevap değil, ve reddedilen bir pano sessizce geçerse kullanıcı metni aldığını sanır. İkon 2,5 saniye boyunca **Kopyalandı** / **Kopyalanamadı** adını alıyor ve vurgu ya da tehlike rengine dönüyor — `RawOutput`'un kelimeleri ve süresi. Panele satır eklemiyor: başlığın yanında beliren bir kelime altındaki kutuyu aşağı iterdi, ki fark 89'un derdi tam olarak buydu. | 90 |
| 34 | **Kutu boşken ikon basılamaz.** Boş bir kutuyu kopyalayıp "Kopyalandı" demek yalan olurdu. İkonu gizlemek de bir cevap ama kullanıcı yazıp sildikçe başlık seğirir. İkon yerinde duruyor ve pasif kalıyor — evin pasif düğme dili. | 90 |
| 35 | **Panel kendi içinde kayar.** Kutular sabit yüksekliğe geçince sütunun toplam boyu da sabitleniyor. Tasarım "panel uzayıp altındaki butonları aşağı itmez" diyor ama panelden kısa bir pencerede ne olacağını söylemiyor. Sütun kendi içinde kayıyor; yoksa silme düğmesi ekranın altında, ulaşılamayacak bir yerde kalırdı. | 89 |
```

---

### Task 2: Pano taklidi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

**Interfaces:**
- Produces: `stubClipboard(answer)` — 5, 6 ve 7. testlerin kullandığı yardımcı.

- [ ] **Step 1: `tab` tanımının hemen altına**

`RawOutput.test.jsx`'in aynı yardımcısı; oradan olduğu gibi alınıyor, çünkü ölçtüğü şey aynı.

```jsx
// jsdom ships no clipboard, so the test supplies one and watches what it is handed.
function stubClipboard(answer) {
  const writeText = vi.fn(() => answer);
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
  return writeText;
}
```

---

### Task 3: On test

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

**Interfaces:**
- Consumes: `tab`, `open`, `settle`, `LAYERED`, `QUEUED_COPY`, `stubClipboard`.
- Consumes: `data-side`, `data-group`, `data-box`, ikonun `aria-label`'ı — **uygulama turunda doğar**.

- [ ] **Step 1: Yeni blok, `the negative prompt` bloğunun hemen üstüne**

```jsx
describe("PhotoDetail — the right column", () => {
  it("names the layer every prompt heading belongs to", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 88: all three tabs drew the same two words, so the heading said nothing about which
    // layer was under it. The words come off the tabs, so a layer cannot end up with two names.
    expect(screen.getByText("Foto prompt'u")).toBeTruthy();
    expect(screen.getByText("Foto negatif prompt'u")).toBeTruthy();

    fireEvent.click(tab("Video"));
    expect(screen.getByText("Video prompt'u")).toBeTruthy();

    fireEvent.click(tab("Ses"));
    expect(screen.getByText("Ses prompt'u")).toBeTruthy();
  });

  it("gives the photo tab's two boxes their own heights", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 89: the two boxes used to share whatever the window left over, so a short window
    // squeezed both of them. Their own measure now, and a long text folds inside it.
    const [prompt, negative] = [...document.querySelectorAll("[data-box]")];
    expect([prompt.style.height, negative.style.height]).toEqual(["162px", "96px"]);
    expect([prompt.style.overflowY, negative.style.overflowY]).toEqual(["auto", "auto"]);
  });

  it("gives the video and sound boxes the same measure", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    expect(document.querySelector("[data-box]").style.height).toBe("150px");

    fireEvent.click(tab("Ses"));
    expect(document.querySelector("[data-box]").style.height).toBe("150px");
  });

  it("puts a copy icon beside every prompt heading", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 90. The negative is a prompt box too, so it carries one as well.
    expect(screen.getByLabelText("Foto prompt'u — kopyala")).toBeTruthy();
    expect(screen.getByLabelText("Foto negatif prompt'u — kopyala")).toBeTruthy();

    fireEvent.click(tab("Video"));
    expect(screen.getByLabelText("Video prompt'u — kopyala")).toBeTruthy();
  });

  it("copies the box's own text and says so", async () => {
    const writeText = stubClipboard(Promise.resolve());
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByLabelText("Video prompt'u — kopyala"));
    await settle();

    // The open layer's words, not the photo's -- there are three boxes on this page across the
    // three tabs and each icon belongs to the one beside it.
    expect(writeText).toHaveBeenCalledWith("kadın dönüyor");
    expect(screen.getByLabelText("Kopyalandı")).toBeTruthy();
  });

  it("says so when the clipboard refuses", async () => {
    stubClipboard(Promise.reject(new Error("denied")));
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));
    fireEvent.click(screen.getByLabelText("Video prompt'u — kopyala"));
    await settle();

    // Silence would leave the user believing they had the text, and the box is still selectable
    // by hand -- saying it failed is also saying take it yourself (karar 33).
    expect(screen.getByLabelText("Kopyalanamadı")).toBeTruthy();
  });

  it("leaves the icon unpressable when the box is empty", async () => {
    await open("P0_1", { frames: [QUEUED_COPY] });

    fireEvent.click(tab("Video"));

    // A copy button that copies nothing is a lie; one that comes and goes as the user types makes
    // the heading twitch. It stays and it dims (karar 34).
    expect(screen.getByLabelText("Video prompt'u — kopyala").disabled).toBe(true);
  });

  it("splits the column into two groups with nothing between them", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 91: what the frame is, then what can be made of it. No group heading and no rule
    // between them -- the split is where the eye rests, not a line it reads.
    const side = document.querySelector("[data-side]");
    expect([...side.children].map((one) => one.getAttribute("data-group")))
      .toEqual(["info", "production"]);
  });

  it("keeps one vertical rhythm down the column", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Fark 91: three measures became two -- 16 between blocks, 6 between a label and what it
    // labels. The information group wraps on a 300px panel, so its own rows answer to the 16 too.
    const side = document.querySelector("[data-side]");
    expect(side.style.gap).toBe("16px");
    expect(side.children[0].style.rowGap).toBe("16px");
    expect(side.children[1].style.gap).toBe("16px");
    expect(document.querySelector("[data-field]").parentElement.style.gap).toBe("6px");
  });

  it("lets the panel scroll rather than clip its own buttons", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // With every box at a fixed height the column has a fixed total, and a window shorter than
    // that would put the delete button somewhere nobody can reach (karar 35).
    expect(document.querySelector("[data-side]").style.overflowY).toBe("auto");
  });
});
```

- [ ] **Step 2: Üç testin aradığı kelime**

`shows the open layer's own prompt and nothing under it` (video sekmesi):

```jsx
    expect(screen.queryByText("Foto negatif prompt'u")).toBeNull();
```

`shows the negative next to the prompt` ve `draws the box even when there is no negative, rather
than hiding it`:

```jsx
    expect(screen.getByText("Foto negatif prompt'u")).toBeTruthy();
```

- [ ] **Step 3: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: ilk üçü yeşil (384 / 474 / 694), dördüncüsü **494 testin 12'si kırmızı**:

| Test | Neden kırmızı |
|---|---|
| `names the layer every prompt heading belongs to` | başlıklar "Prompt" ve "Negatif" |
| `gives the photo tab's two boxes their own heights` | `[data-box]` yok |
| `gives the video and sound boxes the same measure` | `[data-box]` yok |
| `puts a copy icon beside every prompt heading` | ikon yok |
| `copies the box's own text and says so` | ikon yok |
| `says so when the clipboard refuses` | ikon yok |
| `leaves the icon unpressable when the box is empty` | ikon yok |
| `splits the column into two groups with nothing between them` | `[data-side]` yok |
| `keeps one vertical rhythm down the column` | `[data-side]` yok |
| `lets the panel scroll rather than clip its own buttons` | `[data-side]` yok |
| `shows the negative next to the prompt` | başlık "Negatif" |
| `draws the box even when there is no negative...` | başlık "Negatif" |

`shows the open layer's own prompt and nothing under it` **yeşil kalır** — video sekmesinde o
kelime ne bugün var ne yarın olacak.

---

### Task 4: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): the right column takes its own measure

Four differences meet in one column, so they are written as one item. The headings say
Prompt and Negatif on every tab, telling nobody which layer is under them. The boxes carry
flex, so they share whatever the window leaves and a short window squeezes both. There is
no way to put a prompt on the clipboard. And the column runs three vertical measures where
the design keeps one.

Ten red tests, and two more that were looking for the word Negatif. A third looked for its
absence on the video tab and only changes the word it looks for -- absent before, absent
after, green on both sides. A test that measures an absence has to name something that
could have been there.

The headings read their words off the tabs rather than keeping a second list, so a layer
cannot be called one thing on its tab and another over its box.

Three decisions the design leaves open are written down first, in the source: what the icon
says after a press, what it does over an empty box, and what a window shorter than the
panel does now that the panel has a fixed height.

Frontend source untouched, so no dist in this commit.

Four suites run; 12 red in queen-editor frontend.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in sekiz kararı Task 3'ün on testi (1→1, 2→2 ve 3, 3→4, 4→5 ve 6, 5→7,
6→8, 7→9, 8→10). 33–35. kararlar Task 1.

**Tip tutarlılığı:** `data-side`, `data-group`, `data-box` ve `aria-label` biçimi
(`<başlık> — kopyala`) uygulama turunun planında birebir aynı yazılıyor.

**Kontrol edilen tuzak:** kutunun `flex`'i ölçülmüyor. `flex` bir kısayol ve cssstyle onu geri
vermeyebilir — ölçülen şey `height`, ki "esnemiyor" cümlesinin karşılığı zaten o.

**Kontrol edilen tuzak 2:** ritim testi `rowGap` okuyor, `gap` kısayolunu değil. Bilgi grubunun iki
ölçüsü farklı (dikey 16, yatay 24) ve kısayolun geri okunacağının garantisi yok.

**Kontrol edilen tuzak 3:** `settle()` sahte saati ilerletip söz zincirini de boşaltıyor — pano
cevabı bir `Promise`, ve `fireEvent` tek başına onu beklemez.

**Kontrol edilen tuzak 4:** 7. test kuyrukta bekleyen kopya kareyi açıyor; o karenin video
prompt'u yok (`prompts` yalnız fotoyu taşıyor), yani kutuda kopyalanacak metin gerçekten yok.
Kutudaki ipucu cümlesi metin değil, bir bildirim — ve ikon onu kopyalamıyor.

**Değişmeyen:** öteki üç takım, `dist`, üretim kodu.
