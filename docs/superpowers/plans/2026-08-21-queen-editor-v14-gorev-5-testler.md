# v14 Görev 5 — Sonrakine bağla ardışık seçim istiyor: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Dağınık seçimde bağlama seçeneğinin kapanmasını, sebebin tek satır görünmesini, bitişik
seçimde geri açılmasını ve kapanan seçeneğin seçili kalamamasını sınayan altı testi yazmak; takımı
kırmızı commit'lemek.

**Architecture:** Tek dosya, tek yeni öbek. Panelin dışarıdan gördüğü iki şey var — `frames`
(galerinin tamamı) ve `selected` (kimlikler) — ve bütün kural o ikisinin ilişkisi, yani testler
prop değiştirerek yazılıyor. Modun düşmesini görmek için `rerender` gerekiyor: seçim galeride
değişiyor, panelde değil.

**Tech Stack:** React 18, vitest, jsdom, @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-5-ardisik-secim-testler-design.md)

## Global Constraints

- **Bu döngüde kod yazılmıyor.** `frontend/src` altındaki kaynak dosyaları değişmiyor.
- Test adları ve yorumları **İngilizce**; aranan ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `dist/` **derlenmiyor**.
- Commit **kırmızı gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/features/photo_generation/LayerPanel.test.jsx` | ardışıklık kuralı | 1 öbek, 6 test |

---

### Task 1: Ardışıklık öbeği

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/LayerPanel.test.jsx`

**Interfaces:**
- Consumes: `LayerPanel`'in `frames` ve `selected` prop'ları; dosyanın var olan `FRAMES` sabiti ve
  `renderPanel` yardımcısı.

- [ ] **Step 1: Öbeği yaz**

`describe("LayerPanel — the production mode", ...)` öbeğinin **hemen altına**:

```jsx
describe("LayerPanel — linking wants neighbours", () => {
  const modeRow = (label) => screen.getByText(label).closest("button");
  // 2_a and 0_a sit either side of 1_a in the gallery, so picking the two of them leaves a hole.
  const SCATTERED = ["2_a", "0_a"];
  const NEIGHBOURS = ["2_a", "1_a"];
  const WHY = "Zincir ancak bitişik karelerde kapanır — arada seçilmemiş kare var.";

  it("closes the option when the chosen frames are not neighbours", () => {
    renderPanel({ selected: SCATTERED });

    expect(modeRow("Sonrakine bağla").disabled).toBe(true);
  });

  it("says why, in one line, under the option it closed", () => {
    renderPanel({ selected: SCATTERED });

    expect(screen.getByText(WHY)).toBeTruthy();
  });

  it("opens the option again when the hole is closed", () => {
    renderPanel({ selected: NEIGHBOURS });

    expect(modeRow("Sonrakine bağla").disabled).toBe(false);
    expect(screen.queryByText(WHY)).toBeNull();
  });

  it("leaves the option open when the scope is every frame with no video", () => {
    // That set is scattered by its nature -- the frames between its members are the ones that
    // already have a video -- and each of its frames still has a next one to end on.
    renderPanel();

    expect(modeRow("Sonrakine bağla").disabled).toBe(false);
    expect(screen.queryByText(WHY)).toBeNull();
  });

  it("counts one frame as neighbours of itself", () => {
    renderPanel({ selected: ["1_a"] });

    expect(modeRow("Sonrakine bağla").disabled).toBe(false);
  });

  it("drops back to the plain mode when the selection breaks apart under it", async () => {
    // Otherwise a row nobody can click keeps going to the queue: the gallery is where the
    // selection changes, and the panel never hears a second click to correct itself.
    const onQueue = vi.fn().mockResolvedValue({ added: 1 });
    const { rerender } = renderPanel({ selected: NEIGHBOURS, onQueue });
    fireEvent.click(modeRow("Sonrakine bağla"));

    rerender(
      <LayerPanel layer="video" frames={FRAMES} selected={SCATTERED} producer={null}
                  onQueue={onQueue} onInstall={() => {}} />,
    );
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(["2_a.png", "0_a.png"], 1, "standard");
  });
});
```

Son test `rerender`'ı elden çağırıyor: `renderPanel` sabit prop'larla kuruyor, ve burada değişmesi
gereken tam olarak `selected`. Galerinin seçimi değiştirmesi böyle görünüyor.

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: `queen-editor`'ın ön yüzünde üç test düşüyor — 1., 2. ve 6. Kalan üçü (3, 4, 5) **yeşil
doğuyor**: satır bugün her koşulda açık, ve o üç test tam olarak "açık kalmalı" diyor. Kalan üç
takım yeşil.

---

### Task 2: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): linking asks for neighbouring frames

Red on purpose: the option is open whatever is selected, and there is no line saying
why it would ever not be. Three of the six tests are born green -- they say where the
rule must not reach, and a rule's edge does not have to fail first to be worth writing
down.

Linking means a chain: each video ends on the next frame picture, and that frame video
ends on its own next. The chain only closes if the chosen frames sit together in the
gallery; with a hole in the middle it is two pieces, each ending on a frame nobody
picked.

The rule follows the scope, not the selection. On the scope that is every frame with no
video the option stays open: that set is scattered by nature -- what sits between its
members already has a video -- and each of its frames still has a real next.

A closed option cannot stay picked, so the mode falls back to plain when the selection
breaks apart. The gallery is where a selection changes and the panel never hears a
second click to correct itself.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in altı testinin altısı planda kodlu, tek Task'ta. Spec'in 6. kararındaki
metin testin `WHY` sabitiyle birebir aynı.

**Tip tutarlılığı:** `onQueue(files, variants, mode)` son testte de 4. maddedeki sırayla.
`SCATTERED` kimlik listesi, `["2_a.png", "0_a.png"]` dosya adı listesi — panel kimlikle eşleştirip
dosya adıyla gönderiyor, ve test ikisini bir arada gösteriyor.

**Kontrol edilen tuzak:** `FRAMES`'te 1_a'nın videosu var, yani "Videosu olmayanlar" kapsamı
{2_a, 0_a} — kendisi dağınık. 4. test tam olarak bunun üstünde duruyor: aynı iki kare seçimle
kapatıyor, kapsamla açık bırakıyor. Kuralın kapsama bağlı olduğunu bundan başka gösterecek bir
kurulum yok.

**Kontrol edilen tuzak 2:** son test `onQueue`'nun **üç** argümanına birden bakıyor. Yalnız moda
bakan bir test, seçimi de sıfırlayan bir uygulamayla yeşil kalırdı — mod düşerken kapsamın yerinde
kaldığını söyleyen tek yer burası.

**Kontrol edilen tuzak 3:** 3, 4 ve 5 yeşil doğuyor ve bu planda yazılı. Kırmızı sanılıp
kovalanmaları, bu döngüde kaybedilecek en kolay yarım saat.
