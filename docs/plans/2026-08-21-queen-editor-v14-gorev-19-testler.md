# v14 Görev 19 — Her sekme yalnız kendi katmanını gösterir: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sağ sütunun sadeleşmesini ölçen testleri yazmak; takımı kırmızı commit'lemek.

**Architecture:** Tek test dosyası. Üç yeni test üst grubu ve bekleyen kutuyu ölçüyor; üç mevcut
test alt katmanları beklemeyi bırakıyor.

**Tech Stack:** vitest, @testing-library/react, jsdom.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-19-sekme-kendi-katmani-testler-design.md)

## Global Constraints

- **Bu döngüde ürün kodu değişmiyor.**
- `skip` / `xfail` yok — kırmızı kırmızı commit ediliyor.
- Yorumlar **İngilizce**, ekran metni **Türkçe**.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- DOM işareti: üst grubun satır başlığı `data-field`.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/PhotoDetail.test.jsx` | üst grup, prompt kutusu, bekleyen kutu | 3 yeni, 3 düzeltilen |

---

### Task 1: Alt katmanları bekleyen iki testi çevir

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

- [ ] **Step 1: Video sekmesi**

`shows the open layer's own prompt and the ones under it` bütünüyle şununla değişiyor:

```jsx
  it("shows the open layer's own prompt and nothing under it", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));

    // Its own words are the editable box; what it was made from is not this page's to show any
    // more -- the decision that put it here was taken back (madde 87).
    expect(screen.getByDisplayValue("kadın dönüyor")).toBeTruthy();
    expect(screen.queryByText("kırmızı elbise")).toBeNull();
    expect(screen.queryByText("P0_0_V1_0.mp4")).toBeNull();
    // The negative belongs to the photo alone: video and sound jobs carry none.
    expect(screen.queryByText("Negatif")).toBeNull();
  });
```

- [ ] **Step 2: Ses sekmesi**

```jsx
  it("repeats the skeleton for sound", async () => {
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Ses"));

    expect(screen.getByDisplayValue("kumaş hışırtısı")).toBeTruthy();
    expect(screen.queryByText("kadın dönüyor")).toBeNull();
    expect(screen.queryByText("P0_0_V1_0_S1_0.wav")).toBeNull();
  });
```

- [ ] **Step 3: Bekleyen kutunun cümlesi**

`opens the tab of the layer it is waiting for, with an empty box` içindeki satır:

```jsx
    expect(screen.getByText("Prompt yok — üretim sırası geldiğinde eklenecek.")).toBeTruthy();
```

---

### Task 2: Üst grup ve bekleyen kutu

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

**Interfaces:**
- Consumes: `data-field` — üst gruptaki bir satırın başlığı.

- [ ] **Step 1: Üç test**

`repeats the skeleton for sound`'un altına:

```jsx
  it("keeps the frame's own name and its place on every tab", async () => {
    // The page's own header carries the project's name, not the frame's -- so if this row went,
    // the identity would be nowhere on screen (karar 23).
    await open("P0_0", { frames: [LAYERED] });
    expect(screen.getByText("Dosya adı")).toBeTruthy();

    fireEvent.click(tab("Video"));
    expect(screen.getByText("Dosya adı")).toBeTruthy();
    expect(screen.getByText("P0_0.png")).toBeTruthy();
    expect(screen.getByText("1 / 1")).toBeTruthy();

    fireEvent.click(tab("Ses"));
    expect(screen.getByText("Dosya adı")).toBeTruthy();
  });

  it("keeps nothing else in the top group", async () => {
    // Read as a list rather than one row at a time: naming the rows that went says nothing about
    // the rows that stayed, and what this item promises is the whole group.
    await open("P0_0", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));

    expect([...document.querySelectorAll("[data-field]")].map((one) => one.textContent))
      .toEqual(["Sıra", "Dosya adı"]);
  });

  it("centres the one line a waiting box holds", async () => {
    // The box is never left blank -- an empty one reads as a prompt someone deleted (karar 24).
    await open("P0_1", { frames: [QUEUED_COPY] });

    fireEvent.click(tab("Video"));

    expect(screen.getByText("Prompt yok — üretim sırası geldiğinde eklenecek.").style.textAlign)
      .toBe("center");
  });
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: üçü yeşil (384 / 474 / 694), queen-editor frontend'de **481 testin 6'sı kırmızı**.

---

### Task 3: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): a tab is asked to show its own layer and no other

The video tab draws the photo's file name and its prompt underneath its own, and the sound
tab draws both of the layers below it. That was a decision -- let the user see what a layer
was made from -- and it has been taken back. These tests say so from the other side: on the
video tab the photo's words are gone, on the sound tab the video's are.

The frame's own name stays, which is the part of the design that was overruled. The page's
header carries the project's name and not the frame's, so this row is the only place the
identity appears at all; it now reads the same on all three tabs instead of changing its
label when a second row stood beside it.

The top group is measured as a list. Naming the rows that went says nothing about the rows
that stayed, and the whole group is what this item promises.

A box waiting for its layer keeps its one line, centred, and the line stops naming who will
write it. What the user needs there is that nothing was deleted.

481 tests, 6 red.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in üç kararı Task 1 (2, 3) ve Task 2 (1, 3).

**Tip tutarlılığı:** `data-field` yalnız üst grubun başlıklarında; prompt kutularının başlığı ayrı
bir şey ve bu listeye girmiyor.

**Kontrol edilen tuzak:** `getByText("P0_0.png")` video sekmesinde yalnız üst gruptaki satırı
buluyor — foto sekmesindeki resmin `alt` metni ayrı bir sorguyla (`getByAltText`) okunuyor ve video
sekmesinde o resim zaten yok.

**Kontrol edilen tuzak 2:** üst grubu etiket metniyle aramak olmazdı — "Video" ve "Ses" aynı
zamanda sekmelerin adı. Liste bu yüzden `data-field` üstünden okunuyor.

**Kontrol edilen tuzak 3:** `LAYERED`'ın `modes` alanı yok, dolayısıyla video sekmesinde "Üretim
modu" satırı doğmuyor ve beklenen liste iki satır. Modlu bir kare olsaydı üç olurdu.

**Değişmeyen:** `PhotoDetail.jsx`. Bu döngüde ürün kodu yok.
