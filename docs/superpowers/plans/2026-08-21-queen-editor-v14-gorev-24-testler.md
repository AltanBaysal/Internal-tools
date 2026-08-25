# v14 Görev 24 — Proje ekranının hizalaması: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Proje ekranının dört farkını dokuz testle yazmak — çöpün yıkıcı standarda geçmesi,
pencerenin tek ölçüye inmesi, listenin kendi kutusunda kayması ve onayın söz sırası. Altısı yeni,
üçü var olan testin değişmesi. Hepsi kırmızı commit ediliyor.

**Architecture:** Ön yüzde iki test dosyası. Motor tarafı hiç açılmıyor. Üretim kodu bu döngüde
değişmiyor — yeni modül de yok, dolayısıyla kabuk da yok.

**Tech Stack:** vitest, @testing-library/react.

**Spec:** [test turu spec'i](../specs/2026-08-21-queen-editor-v14-gorev-24-proje-ekrani-testler-design.md)

## Global Constraints

- **Üretim kodu bu döngüde değişmiyor.** Bu maddede yeni modül doğmuyor; her iki test dosyası da
  zaten var olan bileşenleri okuyor, yani hiçbir dosya *toplanamaz* hâle gelmiyor. Kabuk yazmaya
  gerek yok.
- **Değişen üç test kırmızıya dönüyor, silinmiyor.** Üçü de aynı yeri ölçmeye devam ediyor; ölçtüğü
  değer değişiyor. Bir testi silip yerine yenisini yazmak, o testin neyi koruduğunun kaydını da
  siler.
- **`data-*` kancaları ekrandaki iddianın kendisi.** Liste kutusu `data-list`, soluklaşma bandı
  `data-fade` alıyor — evin diğer maddelerdeki kancaları gibi.
- Test adları ve yorumlar **İngilizce**; ekran metni **Türkçe**.
- `skip` / `xfail` yok — kırmızı kırmızı commit edilir.
- Commit mesajında **çift tırnak yok**, ve **amend yok**.
- Komut: dört satır, birebir, boru yok.
- `dist` bu commit'te **derlenmiyor**.

## File Structure

| Dosya | İşlem |
|---|---|
| `.../research/2026-08-20-queen-editor-tasarim-v4-farklari.md` | 43–45. kararlar |
| `frontend/.../projects/ProjectsScreen.test.jsx` | 6 test eklenir, 2 test değişir |
| `frontend/.../projects/NameModal.test.jsx` | 1 test değişir |

---

### Task 1: 43–45. kararlar kaynağına

**Files:**
- Modify: `docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md`

Kararlar spec'te gerekçeleriyle duruyor; fark listesi bir satırla kaydı alıyor. Kaynak belge kendi
kararlarını taşır, spec ondan türer.

- [ ] **Step 1: Tarih notunu 24. maddeyle genişlet**

`*(21 Ağustos 2026, 13, 15, 20, 21, 22 ve 23. madde uygulanırken.)*` →
`*(21 Ağustos 2026, 13, 15, 20, 21, 22, 23 ve 24. madde uygulanırken.)*`

- [ ] **Step 2: Üç satır ekle**

42. satırın altına, aynı tabloya:

```markdown
| 43 | **Karttaki kalem çerçevesiz kalıyor.** 1. karar çöpü yıkıcı eylem standardına soktu; standart yıkıcı bir düğmenin neye benzediğini söylüyor ve kalem yıkıcı değil (fark 3). İkisini düzen adına benzetmek standardın var olma sebebini silerdi: kırmızı çerçeve, yanındaki çıplak ikondan ayrıldığı için işaret. Kalem `ghost` varyantını alıyor — çizgisiz, ama aynı kutu; `border: none` kutuyu her kenardan bir piksel küçültüp düğmeleri kaydırıyordu. | 5 |
| 44 | **Liste kendi içinde kayıyor; 9 Ağustos 2026'nın N3 kararı geri alınıyor.** O karar tasarım v2'ye karşı verildi ve v2'de çizilmiş bir tutamak yoktu — ortada seçenek değil "bugünkü hâl yeter mi" sorusu vardı. v4 hem tutamağı hem bandı çiziyor ve ikisi ancak kırpılmış bir kutuda var olabilir: sayfa kayıyorsa tarayıcının kendi çubuğu zaten var ve altı soluklaşacak bir liste alanı yok. Uygulamanın diğer dört ekranı zaten `height: 100vh` + içeride kayan gövde. | 8 |
| 45 | **Bant sayıya bakıyor, taşmaya değil.** Tasarımın ölçüsü bir sayı: "liste sekizi geçince" — dört sütunun iki satırı. Taşmayı ölçmek uygulanabilir değil: `scrollHeight > clientHeight` jsdom'da iki sıfırı karşılaştırır ve o kuralı doğrulayan test yerleşimi taklit etmek zorunda kalır. Tutamak bu ayrımdan etkilenmiyor — kutu `overflow-y: auto` ve tarayıcı kayacak bir şey yoksa tutamağı çizmiyor. | 8 |
```

---

### Task 2: `ProjectsScreen.test.jsx` — çöp, kalem ve pencere ölçüsü

**Files:**
- Modify: `queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx`

**Interfaces:**
- Consumes: `openScreen()` yardımcısı (dosyada var), `screen.getByLabelText`.
- Produces: sonraki task'ın kullandığı `openWith(count)` yardımcısı.

- [ ] **Step 1: Çöpün testini yıkıcı standarda çevir**

`draws the bin as a red icon and nothing else: no box of its own` testinin gövdesi gidiyor, adı ve
yeri kalıyor:

```jsx
  it("draws the bin in the clothes every destructive button in the app wears", async () => {
    await openScreen();

    // Fark 5, karar 1: the design's own texts disagreed -- the rules document counts project
    // delete among the destructive standard's examples, the card drawing shows a bare icon. The
    // rules document won. Unfilled, red border, red icon.
    const bin = screen.getByLabelText("Projeyi sil");
    expect(bin.style.borderColor).toBe("var(--danger)");
    expect(bin.style.color).toBe("var(--danger)");
    expect(bin.style.background).toBe("none");
    expect(bin.querySelector("svg")).toBeTruthy();
  });
```

- [ ] **Step 2: Kalemin çizgisizliğini yaz**

Bir öncekinin altına:

```jsx
  it("leaves the pencil beside it without a line of its own", async () => {
    await openScreen();

    // Karar 43: the red frame is a mark, and a mark only marks while the thing next to it has
    // none. Ghost draws nothing but keeps the box, so the two sit level.
    const pencil = screen.getByLabelText("Projeyi yeniden adlandır");
    expect(pencil.className).toContain("wf-btn--ghost");
    expect(pencil.style.color).not.toBe("var(--danger)");
    expect(pencil.style.borderColor).not.toBe("var(--danger)");
  });
```

- [ ] **Step 3: Yeni proje penceresinin ölçüsünü yaz**

`ProjectsScreen renaming a project` bloğunun sonuna, `draws the window at the measure...` testinin
ikizi olarak — ama yeni proje tarafında. Bloğun adı yeniden adlandırma diyor, o yüzden test
`ProjectsScreen with nothing in it yet` bloğunun altına, kendi bloğunda:

```jsx
describe("ProjectsScreen opening a new project", () => {
  it("opens the window at the one measure both windows share", async () => {
    await openScreen();

    fireEvent.click(screen.getByText("Yeni proje"));

    // Fark 6: 400 was the wider of two measures; there is only one now, and it belongs to the
    // window rather than to whoever opens it.
    const title = screen.getByText("Yeni proje", { selector: ".wf-hand" });
    expect(title.closest(".wf-card").style.width).toBe("380px");
  });
});
```

- [ ] **Step 4: Koş ve üçünün de kırmızı olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: FAIL — çöp `borderColor` boş, kalemde `wf-btn--ghost` yok, pencere `400px`.

---

### Task 3: `ProjectsScreen.test.jsx` — liste kutusu ve bant

**Files:**
- Modify: `queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx`

- [ ] **Step 1: Sayılı liste açan yardımcı**

Dosyanın yardımcılarının yanına, `openScreen`'in altına:

```jsx
// The list at a given length. The names only have to be different from each other; what the test
// is looking at is the box they sit in.
async function openWith(count) {
  listProjects.mockResolvedValue(
    Array.from({ length: count }, (_, i) => ({ name: `p${i + 1}`, modifiedAt: 1754300000 })),
  );
  render(<ProjectsScreen />);
  await settle();
}
```

- [ ] **Step 2: Dört testi kendi bloğunda yaz**

`ProjectsScreen deleting a project` bloğunun altına:

```jsx
describe("ProjectsScreen with a long list", () => {
  it("scrolls the list in its own box rather than the page", async () => {
    await openWith(12);

    // Fark 8, karar 44: the header stays put and the projects move under it -- the way the app's
    // other four screens are built. The 2026-08-09 decision that the page scrolls was given
    // against a design that drew no handle at all.
    expect(document.querySelector("[data-list]").style.overflowY).toBe("auto");
  });

  it("gives the list a handle of its own, a thin one", async () => {
    await openWith(12);

    // The rule is in app.css because it is a scrollbar pseudo-element; what the screen owes is
    // the class. Nothing is drawn while there is nothing to scroll, so the handle needs no
    // condition of its own (karar 45).
    expect(document.querySelector("[data-list]").className).toContain("qe-thin-scroll");
  });

  it("fades the foot of the list once it has passed eight", async () => {
    await openWith(9);

    // Karar 45: eight is two rows of four, and it is a count because the design gives a count --
    // measuring the overflow would mean a test that fakes layout.
    const fade = document.querySelector("[data-fade]");
    expect(fade).toBeTruthy();
    // A band nobody can see must not swallow the click meant for the card under it.
    expect(fade.style.pointerEvents).toBe("none");
  });

  it("fades nothing while eight still fit", async () => {
    await openWith(8);

    expect(document.querySelector("[data-fade]")).toBeNull();
  });
});
```

- [ ] **Step 3: Koş ve dördünün de kırmızı olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: FAIL — `[data-list]` yok (üç test `null` üzerinde patlıyor), `[data-fade]` yok.

`fades nothing while eight still fit` bugün de yeşil: bant hiç yokken sekizde de yok. Doğuştan
yeşil bir test — koruduğu şey bir **yasak** (sekizde bant çizilmeyecek) ve yasağın kaldırılacak bir
karşılığı yok. Kırmızıya zorlanmıyor; kırmızı turda yeşil durduğu buraya yazılıyor.

---

### Task 4: `NameModal.test.jsx` — pencere kendi ölçüsünde

**Files:**
- Modify: `queen-editor/frontend/src/features/projects/NameModal.test.jsx`

- [ ] **Step 1: `open()` yardımcısından genişliği çıkar**

```jsx
function open(onSubmit = () => Promise.resolve()) {
  return render(<NameModal title="Yeni proje" submitLabel="Oluştur" busyLabel="Oluşturuluyor…"
                           onCancel={() => {}} onSubmit={onSubmit} />);
}
```

- [ ] **Step 2: Ölçü testini pencerenin kendi ölçüsüne çevir**

```jsx
  it("opens at its own measure: the caller does not give one", () => {
    open();

    // Fark 6: two windows, one form, one measure. It stopped being the caller's the moment the
    // second window turned out to want the same number.
    expect(createButton().closest(".wf-card").style.width).toBe("380px");
  });
```

- [ ] **Step 3: Koş ve kırmızıyı gör**

Run: `npm test --prefix queen-editor/frontend`
Expected: FAIL — `400px`, çünkü `NameModal`'ın varsayılanı hâlâ 400.

---

### Task 5: Dört komut ve kırmızı commit

- [ ] **Step 1: Dört komutu da koş**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Expected: ilk üçü yeşil (384 / 474 / 709); dördüncüsü 533 testin **8'i kırmızı** — altı yeninin
beşi ve iki değişen — artı `NameModal`'ın değişen testi, toplam 9 kırmızı. `fades nothing while
eight still fit` doğuştan yeşil.

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/specs/2026-08-21-queen-editor-v14-gorev-24-proje-ekrani-testler-design.md docs/superpowers/plans/2026-08-21-queen-editor-v14-gorev-24-testler.md docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md queen-editor/frontend/src/features/projects/ProjectsScreen.test.jsx queen-editor/frontend/src/features/projects/NameModal.test.jsx
git commit -m @'
test(queen-editor): the projects screen gets its measures
'@
```

Çift tırnak yok, amend yok.
