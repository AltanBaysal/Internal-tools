# v14 Görev 38 — Açık sekme kareler arasında yerinde kalır: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Detay sayfasının kare değişince sekmeyi düşürdüğünü anlatan bir kırmızı test ile bir yeşil
tutucuyu yazmak — kod hiç değişmeden.

**Architecture:** Tek dosya, tek blok. `PhotoDetail.test.jsx`'in *the layer tabs* bloğuna iki test ve
dosyanın fixture'larına videosu olan bir ikinci kare giriyor. İkisi de kareyi `rerender` ile
değiştiriyor — okların yaptığı şey bu: sayfa sökülmüyor, altındaki kare değişiyor.

**Tech Stack:** React 18, Vite, Vitest + jsdom, @testing-library/react.

**Spec:** [Görev 38 test spec'i](../specs/2026-08-25-queen-editor-v14-gorev-38-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `PhotoDetail.jsx` bu döngüde hiç açılmıyor. Bir test kırmızı commit'lenir;
  `skip`/`xfail` yok.
- **Mevcut 108 testin cümlesi değişmiyor.** Yeni bir fixture ve iki test yalnız ekleniyor.
- **Katman adı sormayan kural, tek testle sınanıyor** — ses için ikinci bir test yazılmaz.
- Dil: test kodu ve yorumlar **İngilizce**; commit mesajı **İngilizce**; belgeler **Türkçe**.
- Commit mesajında **çift tırnak yok** — PowerShell here-string'i kırıyor (CLAUDE.md).
- Test komutu birebir: `npm test --prefix queen-editor/frontend`.
- **`dist` tazelenmiyor** — ön yüz kaynağı değişmiyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx` | detay sayfasının bütün testleri | bir fixture + iki test |

Tek dosya, yeni dosya yok. Anlatılan şey sekmelerin davranışı ve o dosyanın *the layer tabs* bloğu
zaten tam olarak bunu topluyor.

---

### Task 1: Videosu olan bir ikinci kare, sonra iki test

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx:87-90`
  (fixture'lar) ve `:194-201` civarı (*the layer tabs* bloğu)

**Interfaces:**
- Consumes: dosyada zaten duran `LAYERED` (üç katmanlı ilk kare), `SECOND` (videosuz ikinci kare),
  `IDLE`, `settle()`, `tab(name)`, ve sahte `listFrames`/`getStatus`.
- Produces: `SECOND_VIDEO` — videosu olan ikinci kare. Bu turdan sonra dosyada duruyor; uygulama
  döngüsü hiç açmıyor.

- [ ] **Step 1: Fixture'ı ekle**

`SECOND` sabitinin **altına**, `BROKEN`'ın **üstüne**:

```jsx
// The same second frame with a video of its own: a run of videos is what the user is stepping
// through when the open tab matters, and no fixture in this file was one before.
const SECOND_VIDEO = { id: "P1_0", file: "P1_0.png", status: "done", prompt: "mavi elbise",
                       negative: "", layers: { photo: "P1_0.png", video: "P1_0_V1_0.mp4" },
                       failed: [], owed: [],
                       prompts: { photo: "mavi elbise", video: "kadın yürüyor" } };
```

- [ ] **Step 2: İki testi yaz**

*the layer tabs* bloğunun son testinden sonra, bloğun kendi `});`'inden **önce**:

```jsx
  it("keeps the open tab when the next frame has that layer too", async () => {
    // The arrows swap the frame under a mounted page. Stepping through a run of videos should not
    // drop the user back on the photo at every step and make them pick the video again.
    listFrames.mockResolvedValue([LAYERED, SECOND_VIDEO]);
    getStatus.mockResolvedValue(IDLE);
    const { rerender } = render(<PhotoDetail project="düğün" frame="P0_0" />);
    await settle();
    fireEvent.click(tab("Video"));

    rerender(<PhotoDetail project="düğün" frame="P1_0" />);
    await settle();

    expect(tab("Video").getAttribute("aria-current")).toBe("page");
    expect(screen.getByText("P1_0.png")).toBeTruthy();     // it really is the next frame
  });

  it("falls back to the photo when the next frame has no such layer", async () => {
    listFrames.mockResolvedValue([LAYERED, SECOND]);
    getStatus.mockResolvedValue(IDLE);
    const { rerender } = render(<PhotoDetail project="düğün" frame="P0_0" />);
    await settle();
    fireEvent.click(tab("Video"));

    rerender(<PhotoDetail project="düğün" frame="P1_0" />);
    await settle();

    // This is what the reset was for, and it is the half that stays: an open tab on a layer the
    // frame never had would be a tab on nothing.
    expect(tab("Foto").getAttribute("aria-current")).toBe("page");
    expect(tab("Video").disabled).toBe(true);
  });
```

**`rerender` neden, `navigate` değil:** oklar `navigate` çağırıyor ve o bu dosyada sahte — adres
değişmiyor, sayfa yeniden çizilmiyor. Kareyi gerçekten değiştiren şey `frame` prop'u, ve dosyadaki
*forgets the editing when another frame is opened* testi tam olarak bu yolu kullanıyor.

**İkinci iddialar neden var:** birincisinde `P1_0.png` adı, geçişin gerçekten olduğunu söylüyor —
o olmadan test hiç geçmemiş bir sayfada da yeşil olurdu. İkincisinde sekmenin pasifliği, düşüşün
sebebinin "o katman yok" olduğunu söylüyor.

- [ ] **Step 3: Birinin kırmızı, birinin yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `PhotoDetail.test.jsx` **110 tests, 1 failed.** Düşen:

- *keeps the open tab when the next frame has that layer too* — `aria-current` `null`, beklenen
  `"page"`. Sekme fotoğrafa düşmüş.

Yeşil kalması gereken: *falls back to the photo when the next frame has no such layer*.

Takımın toplamı **584** (bugünkü 582 + 2), düşen **1**.

**İkisi de düşerse dur.** İkincisi bugünün davranışını anlatıyor ve bugün doğrulamalı; düşüyorsa
kurulumda hata var — büyük ihtimalle `tab("Video")` ikinci karede bulunamıyordur, ki o da sekmenin
gizlendiği anlamına gelir ve dosyadaki *leaves the tab of a layer the frame does not have disabled
rather than hidden* testiyle çelişirdi.

- [ ] **Step 4: Arka yüz takımını da koştur**

Run: `python -m pytest queen-editor -q`

Expected: **715 passed.** Bu döngü arka yüze hiç dokunmuyor; koşulma sebebi CLAUDE.md'nin iki sabit
satırı.

- [ ] **Step 5: Değişen her şeyi gör**

Run: `git status --short`

Expected: `PhotoDetail.test.jsx`, yol haritası, ve `docs/superpowers` altındaki iki yeni belge.
`PhotoDetail.jsx` ve `dist/` bu listede **olmamalı.**

Yol haritası listede çünkü 38. madde ona bu turda yazıldı — spec kaynağından türer, tersi değil.

- [ ] **Step 6: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): red for a tab that will not stay put between frames

Watching a run of videos on the detail page costs a press per frame. The arrows
swap the frame under a mounted page and the page answers by resetting the open
tab to the photo, so the next video has to be chosen again, and the one after
that.

The reset has a reason and it is written where it happens: a frame that never
had a layer must not open on that layer's tab. That reason only covers half of
what the reset does. When the frame that arrives has the layer, dropping the
tab buys nothing and costs the press.

Two tests. The red one steps to a frame that has a video of its own and expects
the tab to still be on it. The green one is the half worth keeping: a frame
with no video falls back to the photo, and its video tab is disabled, which is
what makes falling back the right answer there.

Neither test names a layer twice over. The rule is not that video stays, it is
that a tab stays while the frame has what it shows -- so the sound tab needs no
test of its own; it would be the same line asked twice.

The file gains a second frame that carries a video. Every fixture in it was
either the three layered frame or a bare photo, which is why no test in this
file could have caught this: stepping onto a frame with no video lands on the
photo tab whichever rule is in force.

The roadmap gains item 38 in this commit: a spec derives from its source, never
the other way round.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:**

| Spec'te ne diyor | Planda nerede |
|---|---|
| Katman varsa sekme yerinde | Task 1 Step 2, test 1 |
| Katman yoksa fotoğrafa düşüyor | Task 1 Step 2, test 2 |
| Videosu olan ikinci kare gerekiyor | Task 1 Step 1 |
| Ses için ikinci test yok | Global Constraints, commit mesajı |
| Bugünkü testler bunu tutmuyor | Task 1 Step 6 commit mesajı |
| Effect'in geri kalanı test edilmiyor | Bilerek dışarıda (aşağıda) |
| Kod değişmiyor | Global Constraints, Task 1 Step 5 |
| `dist` tazelenmiyor | Global Constraints, Task 1 Step 5 |

Spec'te olup planda karşılığı olmayan madde yok.

**Yer tutucu yok:** Her adımda çalıştırılacak gerçek kod ve gerçek komut var; beklenen sayılar
(108 → 110, 582 → 584, 715) ve beklenen hata değeri (`null` yerine `"page"`) yazılı.

**Ad tutarlılığı:** `SECOND_VIDEO` iki adımda aynı yazımla geçiyor; `LAYERED`, `SECOND`, `IDLE`,
`settle`, `tab`, `listFrames`, `getStatus` hepsi dosyada bugün duran adlar. `SECOND_VIDEO`'nun
`id`'si `SECOND`'ınkiyle bilerek aynı (`P1_0`): ikisi aynı karenin iki hâli, ve iki test aynı
adresle çalışıyor.

**Bilerek dışarıda:** effect'in sıfırladığı diğer dört şey — prompt kutusu, basılmış düğmeler, hata
kartı, üretim modu kutusu. Dördü de değişmiyor ve prompt kutusunun kendi testi zaten var.
