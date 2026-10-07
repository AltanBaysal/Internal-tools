# v14 Görev 28 eki — Bekleyen karo da döner: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bir testin cümlesini değiştirmek; o test düşecek. Kod bu döngüde değişmiyor.

**Architecture:** Tek dosya, tek test. Yeni yardımcı, yeni test, yeni dosya yok.

**Spec:** [Görev 28 eki test spec'i](../specs/2026-08-24-queen-editor-v14-gorev-28-halka-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `TileImage.jsx` bu commit'te olduğu gibi kalır.
- **Kırmızı bırakılır.** `skip`/`xfail` yok.
- **İkinci bir test eklenmiyor** — aynı hâl için iki cümle çelişki olurdu.
- Dil: test adı ve yorumlar **İngilizce**; commit mesajı **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Test komutu (depo kökünden, `cd` yok): `npm test --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/features/photo_generation/TileImage.test.jsx` | karonun ne gösterdiği | tek testin adı, gövdesi ve yorumu |

---

### Task 1: Bekleyen karonun testi halkayı ister

**Files:**
- Test: `queen-editor/frontend/src/features/photo_generation/TileImage.test.jsx`

**Interfaces:**
- Consumes: dosyanın mevcut `holder` ve `turning` yardımcıları.
- Produces: implementasyon döngüsünün uyacağı sözleşme — izin almamış karo da `.wf-spinner`
  gösteriyor.

- [ ] **Step 1: `what the tile shows` bölümünün ilk testini değiştir**

Bugünkü hâli:

```jsx
  it("shows a plain holder while it waits its turn", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    // Every tile is in the queue from the moment it is built, so a ring on each of them would be
    // ninety rings turning at once. That is not information.
    expect(holder()).toBeTruthy();
    expect(turning()).toBeNull();
  });
```

Yerine:

```jsx
  it("turns while it waits its turn, the same as while it downloads", () => {
    render(<TileImage project="düğün" file="1_a.png" />);

    // Waiting and downloading look alike on purpose. Seen on a screen rather than read in a
    // design: with one slot almost every tile is waiting, and a gallery that sits still says
    // nothing is happening. Which tile holds the slot is what this gives up, and it was the
    // cheaper of the two.
    expect(holder()).toBeTruthy();
    expect(turning()).toBeTruthy();
  });
```

Bölümün diğer dört testine **dokunulmuyor** — *inen karo döner*, *fotoğraf gelene kadar gizli*,
*gelince kutu gider*, *gelmezse sessiz kutu*. Sonuncusu bu değişiklikten sonra da anlamını koruyor:
dönen halka artık *"bekliyor ya da iniyor"* demek, ve gelmeyen karo hâlâ ikisi de değil.

- [ ] **Step 2: Yalnız o testin düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: **1 failed** — *turns while it waits its turn, the same as while it downloads*,
`turning()` `null` döndüğü için. Kalan 552 yeşil.

Düşen başka test varsa dur: bu değişikliğin başka hiçbir davranışa dokunmaması gerekiyor.

---

### Task 2: Kırmızıyı doğrula ve commit'le

- [ ] **Step 1: Yalnız test dosyasının değiştiğini doğrula**

Run: `git status --short`
Expected: `TileImage.test.jsx` ve `docs/superpowers`. `TileImage.jsx` ve `dist` bu listede
**olmamalı.**

- [ ] **Step 2: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): red for a tile that turns while it waits

THIS TEST FAILS ON PURPOSE. The line that answers it is the next commit.

The gallery gave the ring to the one tile holding the slot and left every
other tile a still box, so that a person could see which picture was actually
coming. Read in a design that was the careful choice. Seen in Colab it was the
wrong one: with a single slot nearly every tile is waiting, so nearly the
whole screen sat still and the one ring was too small to read as progress.

Waiting and downloading look alike from now on. What that gives up is knowing
which tile holds the slot -- the cheaper of the two, and a deliberate trade.
The tile that will never get its picture still shows the quiet box, so the
ring keeps a meaning: something is still coming.

No second test for the new answer. It is the same state as before with a
different verdict, and two tests about one state would only contradict each
other.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** B1 → Task 1. Spec'te olup planda karşılığı olmayan madde yok.

**Ad tutarlılığı:** Test `turning()` yardımcısını kullanıyor, o da `.wf-spinner` arıyor —
implementasyon döngüsünün uyacağı ad bu, ve `Rendering` zaten onu getiriyor.

**Bilerek dışarıda:** *gelmeyen karo* testinin gözden geçirilmesi. Anlamı değişmedi — halka artık
daha geniş bir şeyi anlatıyor ama o hâl hâlâ halkasız, dolayısıyla test hâlâ doğru şeyi söylüyor.
Değişmemiş bir testi değiştirmek, kaydı bulandırmak olurdu.
