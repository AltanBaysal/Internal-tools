# v14 Görev 20 — Sekmelerin ayrılması: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sekme şeridinin geometrisini üç testle yazmak — araya 8 piksel, komşunun üstüne çekilme
yok, açık sekme yalnız renkten belli. İkisi kırmızı commit ediliyor.

**Architecture:** Tek test dosyası, tek `describe` bloğu. Üretim kodu bu döngüde değişmiyor.

**Tech Stack:** vitest, @testing-library/react, jsdom.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-20-sekme-ayrimi-testler-design.md)

## Global Constraints

- **Üretim kodu bu döngüde değişmiyor.** `data-strip` uygulama turunda geliyor.
- Test adları **İngilizce**, yorumlar **İngilizce**; ekran metni **Türkçe**.
- `skip` / `xfail` yok — kırmızı kırmızı commit edilir.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `dist` bu commit'te **derlenmiyor** — ön yüz kaynağı değişmiyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../research/2026-08-20-queen-editor-tasarim-v4-farklari.md` | kararların kaynağı | 32. karar eklenir |
| `.../photo_generation/PhotoDetail.test.jsx` | detay sayfasının testleri | 3 test eklenir |

---

### Task 1: 32. karar kaynağına yazılıyor

**Files:**
- Modify: `docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md`

Spec 32. karara dayanıyor; bir spec kaynağından türer, tersi olmaz — karar önce kaynakta durur.

- [ ] **Step 1: Tarih notu**

`*(21 Ağustos 2026, 13. ve 15. madde uygulanırken.)*` →
`*(21 Ağustos 2026, 13, 15 ve 20. madde uygulanırken.)*`

- [ ] **Step 2: Tabloya satır**

```markdown
| 32 | **Açık sekmenin çerçevesi vurgu rengini korur.** Tasarım "yalnız rengiyle belli olur, ek işaret yoktur" diyor; bugün açık sekmede yazı da çerçeve de vurgu rengine dönüyor ve ikisi de renk. İşaret, tasarımın sözlüğünde *eklenen* bir şey — alt çizgi, nokta, ok. Her sekmenin zaten sahip olduğu çerçevenin açık olanda renk değiştirmesi, sekmenin renklenmesidir. Bitişikken o çerçeve sürekli bir şeridin içinde açık parçayı kutulama işini de görüyordu; ayrılınca o işi bırakıyor, rengini değil. Madde geometriden ibaret kalıyor. | 85 |
```

---

### Task 2: Üç test

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.test.jsx`

**Interfaces:**
- Consumes: `tab(name)` (satır 103), `open(fid, {frames})` (satır 68), `LAYERED` (satır 80).
- Consumes: `data-strip` — şeridin tutamağı, **uygulama turunda doğuyor**.

- [ ] **Step 1: Testler `the layer tabs` bloğuna, pasif sekme testinden hemen sonra**

```jsx
  it("sets eight pixels between the three tabs", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // The strip's own measure, not the buttons': three buttons have two gaps between them, and a
    // margin would write the number three times to get two of them (Fark 85).
    expect(document.querySelector("[data-strip]").style.gap).toBe("8px");
  });

  it("pulls no tab onto the one before it", async () => {
    await open("P0_0", { frames: [LAYERED] });

    // Each tab already owns a corner radius -- the stroke class draws it. What hid the radius was
    // the overlap: two rounded corners meeting on the same pixel read as a pinch, not a corner.
    expect([tab("Foto"), tab("Video"), tab("Ses")].map((one) => one.style.marginLeft))
      .toEqual(["", "", ""]);
  });

  it("tells the open tab by its colour and adds nothing else to it", async () => {
    await open("P0_0", { frames: [LAYERED] });

    const shut = { held: tab("Video").childElementCount, said: tab("Video").textContent };
    expect(tab("Video").style.color).toBe("var(--ink-3)");

    fireEvent.click(tab("Video"));

    expect(tab("Video").style.color).toBe("var(--accent)");
    expect(tab("Foto").style.color).toBe("var(--ink-3)");
    // No underline, no dot, no caret: opening a tab changes what colour it is and nothing about
    // what it holds. Separating the three is what makes that temptation appear (Fark 85).
    expect(tab("Video").childElementCount).toBe(shut.held);
    expect(tab("Video").textContent).toBe(shut.said);
  });
```

- [ ] **Step 2: Dört komutu koştur**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: ilk üçü yeşil (384 / 474 / 694), dördüncüsü **484 testin 2'si kırmızı**:

| Test | Neden kırmızı |
|---|---|
| `sets eight pixels between the three tabs` | `document.querySelector("[data-strip]")` bugün `null` |
| `pulls no tab onto the one before it` | Video ve Ses `-1px` taşıyor |

`tells the open tab by its colour...` **yeşil geçer** — spec'in söylediği gibi.

---

### Task 3: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): the three layer tabs stand apart

The tabs over the stage are butted together by a negative margin that pulls each one's
outline onto its neighbour's, and the comment beside it says why: three states of a single
control. That decision was withdrawn -- the change log lists the joined tab among the
things tried and dropped, and only a log entry's last shape counts.

Two red tests. Eight pixels between them, and no tab reaching onto the one before it. The
corner radius needs nothing added: the stroke class has always drawn it, and what hid it
was two rounded corners meeting on the same pixel.

A third test is green from birth and stays. The design says the open tab is told by colour
alone, with no extra mark, and there is no extra mark to remove -- so the test is what keeps
one from arriving once the three stand apart. It watches the whole crossing: colour before,
colour after, and the same contents on both sides.

Frontend source untouched, so no dist in this commit.

Four suites run; 2 red in queen-editor frontend.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in üç kararı Task 2'nin üç testi; 32. karar Task 1.

**Tip tutarlılığı:** `data-strip` yalnız bir yerde okunuyor ve uygulama turunun planı aynı adı
yazıyor.

**Kontrol edilen tuzak:** `style.gap` ve `style.color` jsdom'da `var()` ve `px` değerlerini geri
veriyor — evde zaten böyle okunuyor (`Gallery.test.jsx:250`, `Gallery.test.jsx:1154`). `border`
kısayolunun okunamama sorunu buraya değmiyor, çünkü hiçbiri kısayol değil.

**Kontrol edilen tuzak 2:** üçüncü test `Foto`'nun rengini de ölçüyor — yalnız açılanı ölçseydi üç
sekmenin birden vurguya dönmesini yakalayamazdı.

**Kontrol edilen tuzak 3:** ikinci test marjı `""` bekliyor, `"0px"` değil. Marj satırı silinince
React hiçbir şey yazmaz, sıfır yazmaz.

**Değişmeyen:** üretim kodu, öteki üç takım, `dist`.
