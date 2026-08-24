# v14 Görev 38 — Açık sekme kareler arasında yerinde kalır: UYGULAMA döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Önceki commit'in kırmızı testini yeşile döndürmek, tutucuyu yeşil bırakarak.

**Architecture:** Tek dosya, tek satır. Kare değişiminde koşan effect sekmeyi koşulsuz sıfırlamak
yerine soruyor: gelen karede bu katman var mı? Effect'in sıfırladığı diğer beş şey olduğu gibi
kalıyor.

**Tech Stack:** React 18, Vite, Vitest + jsdom.

**Spec:** [Görev 38 uygulama spec'i](../specs/2026-08-25-queen-editor-v14-gorev-38-uygulama-design.md)

## Global Constraints

- **Test dosyası değişmiyor.** `PhotoDetail.test.jsx` bir önceki commit'te ne yazıldıysa o kalır.
- **Effect'in bağımlılığı `[fid]` kalır.** `has` eklenirse her poll'de koşar ve kullanıcının açtığı
  sekmeyi altından çeker.
- **Fonksiyonel güncelleme** — `setOpen((shown) => …)`, `setOpen(has[open] ? …)` değil.
- **`handleDeleteLayer`'ın kendi `setOpen("photo")`'su değişmiyor** — ayrı bir yol, orada katman
  gerçekten gitti.
- Dil: kod ve yorumlar **İngilizce**; commit mesajı **İngilizce**; belgeler **Türkçe**.
- Commit mesajında **çift tırnak yok** — PowerShell here-string'i kırıyor (CLAUDE.md).
- Test: `npm test --prefix queen-editor/frontend` · Derleme:
  `npm run build --prefix queen-editor/frontend` · **`dist` aynı commit'e girer.**

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx` | detay sayfası ve açık sekme | effect'in bir satırı ve üstündeki yorum |

Tek dosya, tek satır. Sekmenin hangi karede ne olacağı bu bileşenin kendi işi; başka hiçbir yer
`open`'ı görmüyor.

---

### Task 1: Sekme yalnız gidecek yeri yoksa düşsün

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx:353-360`

**Interfaces:**
- Consumes: aynı bileşende zaten hesaplanan `has` — `{ photo: bool, video: bool, audio: bool }`,
  `stateOf(layer) !== null` demek, yani "bu karede bu katmandan bir şey var mı".
- Produces: dışarıya bir şey değil. `PhotoDetail`'in prop listesi ve `LayerTabs`'a verdikleri aynı.

- [ ] **Step 1: Yorumu ve satırı değiştir**

353–360. satırlar bugün:

```jsx
  // The arrows swap the frame under a page that stays mounted, so anything said about the old one
  // has to go with it -- a refusal card from the previous frame would read as this one's, and a
  // tab it does not have would be open on a frame that never had that layer.
  useEffect(() => {
    setRefused(false);
    setAsking(null);
    setBusy(false);
    setOpen("photo");
```

Yerine:

```jsx
  // The arrows swap the frame under a page that stays mounted, so anything said about the old one
  // has to go with it -- a refusal card from the previous frame would read as this one's.
  //
  // The open tab is the one thing that stays. Stepping through a run of videos used to cost a press
  // per frame, and dropping a tab the frame that arrived does have buys nothing (madde 38). It only
  // falls back when there is nowhere to fall back from: a tab on a layer the frame never had would
  // be a tab on nothing. Not by layer name -- the sound tab keeps its place by the same line.
  //
  // Asked of React rather than read from `open`, because this effect sets other state around it and
  // a value read from the closure would depend on where in the list it sits. `has` is the arriving
  // frame's: it is worked out during the render that fid changed, and this runs after it. `has` is
  // deliberately not a dependency -- the tab is a question for a new frame, not for every poll.
  useEffect(() => {
    setRefused(false);
    setAsking(null);
    setBusy(false);
    setOpen((shown) => (has[shown] ? shown : "photo"));
```

Effect'in geri kalanı (`setWords({})`, `setSent([])`, `setRefusedAct(null)`, `setNewMode(null)` ve
kendi yorumları) ve `}, [fid]);` satırı **değişmiyor.**

- [ ] **Step 2: Takımın tamamen yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **0 failed**, 584 tests. Özellikle:

- `PhotoDetail.test.jsx` **110 tests, 0 failed** — kırmızı yeşile döndü, tutucu yeşil kaldı.

*falls back to the photo when the next frame has no such layer* düşerse dur: `has` yanlış karenin
olabilir, ya da fonksiyonel güncelleme yerine `open` doğrudan okunmuştur.

*forgets the editing when another frame is opened* düşerse dur: effect'in geri kalanına dokunulmuş
demektir.

- [ ] **Step 3: Ön yüzü derle**

Run: `npm run build --prefix queen-editor/frontend`

Expected: hatasız biter ve `queen-editor/frontend/dist/` tazelenir.

- [ ] **Step 4: Arka yüz takımının da yeşil olduğunu gör**

Run: `python -m pytest queen-editor -q`

Expected: **715 passed.** Bu döngü arka yüze hiç dokunmuyor; koşulma sebebi CLAUDE.md'nin iki sabit
satırı.

- [ ] **Step 5: Yol haritasını işaretle**

Modify: `docs/superpowers/plans/2026-08-20-queen-editor-v14-roadmap.md`

38. maddenin satırındaki iş adının başına `✅ ` ekle — 35, 36 ve 37'nin satırlarındaki biçimin
aynısı:

```
| 38 | ✅ **Açık sekme kareler arasında yerinde kalır.** …
```

Aynı belgenin başlığındaki ilerleme sayısını da bir artır: `35/37` yazan yer `36/37` olur.

- [ ] **Step 6: Colab turu listesine satır ekle**

Modify: `docs/superpowers/plans/2026-08-24-queen-editor-v14-colab-turu.md`

`## 6 · Detay sayfası` bölümünün **sonuna**, *Detayın görseli* satırının altına:

```markdown
- [ ] **Sekme kareler arasında yerinde** (38). Videosu olan iki kare arasında oklarla gezilir: video
      sekmesi açık kalmalı, her karede yeniden seçilmemeli. Videosu olmayan bir kareye gelince
      fotoğrafa dönmeli. Oynatıcı duraklamış başlar — o bilerek öyle.
```

- [ ] **Step 7: Değişen her şeyi gör**

Run: `git status --short`

Expected: `PhotoDetail.jsx`, `dist/` altındakiler, `docs/superpowers` altındaki iki yeni belge ve
iki değişen belge. `PhotoDetail.test.jsx` bu listede **olmamalı.**

- [ ] **Step 8: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): the open tab stays put between frames

Watching a run of videos cost a press per frame. The arrows swap the frame under
a page that stays mounted, and the page answered by putting the tab back on the
photo whatever had been open -- so the next video had to be chosen again, and
the one after that.

The reset had a reason, and it is still here: a frame that never had a layer
must not open on that layer's tab. It only ever covered half of what the reset
did. When the frame that arrives does have the layer, dropping the tab buys
nothing at all.

So the tab now falls back rather than resetting, and only when there is nowhere
to fall back from. Not by layer name either -- the sound tab keeps its place by
the same line, and a fourth layer would too.

Everything else the frame owns still goes with it: the refusal card, the open
window, the editing, the presses, and the box that says what to make the video
in next.

Asked of React rather than read from the value in hand, because the effect sets
other state around it and a value from the closure would depend on where in the
list it sits. The layers it reads are the arriving frame's -- they are worked
out during the render the address changed on, and the effect runs after it. They
are deliberately not a dependency: which tab is open is a question for a new
frame, not for every poll, and asking it on every poll would pull a tab out from
under the user.

A video that is still queued keeps its tab too. The page then says what it is
doing there, which is the honest answer to why it cannot be played yet.

The player still starts paused, which is a separate question and the user's to
put.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:**

| Spec'te ne diyor | Planda nerede |
|---|---|
| Koşulsuz sıfırlama → koşullu düşüş | Task 1 Step 1 |
| Kural katman adı sormuyor | Task 1 Step 1'in yorumu, commit mesajı |
| `has` gelen karenin | Task 1 Step 1'in yorumu |
| Bağımlılık `[fid]` kalıyor | Global Constraints, Task 1 Step 1'in yorumu |
| Fonksiyonel güncelleme | Global Constraints, Task 1 Step 1 |
| Bekleyen katman sekmesini koruyor | Commit mesajı |
| Yorum düzeltiliyor | Task 1 Step 1 |
| Effect'in geri kalanı değişmiyor | Task 1 Step 1'in kapanış notu |
| `handleDeleteLayer` değişmiyor | Global Constraints |
| Test dosyası değişmiyor | Global Constraints, Task 1 Step 7 |
| Derlenmiş çıktı aynı commit'te | Task 1 Step 3 ve Step 8 |

Spec'te olup planda karşılığı olmayan madde yok. Yol haritası ve Colab turu adımları spec'te değil,
CLAUDE.md'nin numaralandırma ve tur kuralından geliyor.

**Yer tutucu yok:** Tek kod adımında gerçek kod, diğerlerinde gerçek komut var; beklenen sayılar
(110, 584, 715) yazılı.

**Ad tutarlılığı:** `has`, `setOpen`, `shown`, `fid` — hepsi dosyada bugün duran adlar. `shown`
parametre adı olarak `SidePanel`'in aynı kalıptaki `toggle`'ıyla bilerek aynı: iki yerde aynı soruyu
soran iki fonksiyon aynı kelimeyi taşıyor.

**Bilerek dışarıda:** oynatıcının duraklamış başlaması, ve `LayerTabs`'ın kendisi — sekme şeridi
`open`'ı yalnız çiziyor, nereden geldiğini bilmiyor.
