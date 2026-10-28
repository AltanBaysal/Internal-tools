# v14 Görev 35 — Yazılmış ama gönderilmemiş metin geri dönüşte duruyor: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Fotoğraf üret panelinin sökülüp yeniden kurulduğunda yazılmış metni kaybettiğini anlatan
iki kırmızı test ile iki yeşil tutucuyu yazmak — kod hiç değişmeden.

**Architecture:** Tek dosya, iki değişiklik. Önce dosya test başına taze modül düzenine geçiyor
(uygulama döngüsünde doğacak depo modül seviyesinde duracağı için, bu düzen olmadan bir testin
yazdığı bir sonrakinin başlangıcı olurdu). Sonra dört testlik yeni bir `describe` bloğu ekleniyor.

**Tech Stack:** React 18, Vite, Vitest + jsdom, @testing-library/react.

**Spec:** [Görev 35 test spec'i](../specs/2026-08-25-queen-editor-v14-gorev-35-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `GeneratePanel.jsx` bu döngüde hiç açılmıyor. Testlerin ikisi kırmızı
  commit'lenir; `skip`/`xfail` yok.
- **Mevcut 29 testin cümlesi değişmiyor.** Yalnız modülün nereden geldiği ve yardımcının varsayılan
  prop listesi değişiyor.
- **Dil:** test kodu ve yorumlar **İngilizce**; commit mesajı **İngilizce**; belgeler **Türkçe**.
- **Commit mesajında çift tırnak yok** — PowerShell here-string'i kırıyor (CLAUDE.md).
- **Test komutu birebir:** `npm test --prefix queen-editor/frontend`. Boru yok, yönlendirme yok.
- **`dist` tazelenmiyor** — ön yüz kaynağı değişmiyor.
- Panelin bugünkü imzası: `{ job, error, errorField, busyElsewhere, settings, models, modelsError,
  producer, onGenerate, onClearError, onInstall }`. `project` yok — bu döngüde testler onu
  geçirmeye başlıyor, panel henüz okumuyor.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/features/photo_generation/GeneratePanel.test.jsx` | fotoğraf üret panelinin bütün testleri | taze modül düzeni + dört yeni test |

Tek dosya. Yeni test dosyası açılmıyor: anlatılan şey panelin kendi davranışı ve bu dosya zaten
panelin beş yönünü beş `describe` bloğunda topluyor — altıncısı yanlarına ait.

---

### Task 1: Test dosyasını taze modül düzenine geçir

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.test.jsx:1-29`

**Interfaces:**
- Consumes: `vitest`'in `vi.resetModules()`'ü ve dinamik `import()`. Bu dosyada `vi.mock` yok,
  dolayısıyla `vi.clearAllMocks()` **gerekmiyor** — `useModels.test.jsx`/`useProducers.test.jsx`'in
  ona ihtiyaç duymasının sebebi oradaki sahte `api.js`, burada öyle bir şey yok.
- Produces: `GeneratePanel` artık dosya kapsamında `let` ile duruyor ve her testten önce yeniden
  yükleniyor. `renderPanel(props)` imzası aynı kalıyor; varsayılanlarına `project="düğün"` giriyor.

- [ ] **Step 1: İçe aktarmayı taze modüle çevir**

Dosyanın 1–4. satırları bugün:

```jsx
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import GeneratePanel from "./GeneratePanel.jsx";
```

Yerine:

```jsx
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// What was typed and not yet sent is remembered for the length of a visit, and that memory lives in
// the module. So each test gets the module itself fresh -- otherwise a test that types into a box
// would be deciding what the next one opens with. Nothing is mocked in this file, so resetModules
// really does rebuild it.
let GeneratePanel;

beforeEach(async () => {
  vi.resetModules();
  ({ default: GeneratePanel } = await import("./GeneratePanel.jsx"));
});
```

`beforeEach` zaten 2. satırdaki `vitest` içe aktarmasında var; yeni bir ad eklenmiyor.

**Neden en dışta:** *the confirmation* bloğunun kendi `beforeEach`'i (`vi.useFakeTimers`) var.
Vitest dıştaki `beforeEach`'i içtekinden **önce** koşturur, yani modül sahte saatler kurulmadan
yükleniyor. Sıra doğru; bir şey değiştirmek gerekmiyor.

- [ ] **Step 2: Yardımcıya projeyi ekle**

`renderPanel` bugün:

```jsx
function renderPanel(props) {
  return render(
    <GeneratePanel
      job={{ status: "idle" }}
      error={null}
      busyElsewhere={false}
      settings={SETTINGS}
      models={MODELS}
      modelsError={null}
      onGenerate={() => Promise.resolve({ added: 4 })}
      onClearError={() => {}}
      {...props}
    />,
  );
}
```

Yerine — tek fark `project`:

```jsx
function renderPanel(props) {
  return render(
    <GeneratePanel
      job={{ status: "idle" }}
      error={null}
      busyElsewhere={false}
      settings={SETTINGS}
      project="düğün"
      models={MODELS}
      modelsError={null}
      onGenerate={() => Promise.resolve({ added: 4 })}
      onClearError={() => {}}
      {...props}
    />,
  );
}
```

Panel bugün bu prop'u okumuyor; React onu bilmediği için de bir şey yapmıyor. Buraya şimdi
konmasının sebebi, dördüncü testin *başka* bir proje adı verebilmesi ve bunun bir sapma değil
varsayılanın üzerine yazılan bir değer gibi okunması.

- [ ] **Step 3: Takımın hâlâ yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **0 failed.** `GeneratePanel.test.jsx` **29 tests, 0 failed.**

Bu adım bir düzen değişikliğinin hiçbir cümleyi bozmadığını doğruluyor. Düşen olursa dur: taze
modül düzeninin kendisi bir testi bozuyorsa, o test modül seviyesinde bir şeye yaslanıyor demektir
ve bunu bilmek yeni testleri yazmadan önce gerekiyor.

- [ ] **Step 4: Commit yok**

Bu görev tek başına commit edilmiyor — anlattığı bir şey yok, Task 2'nin kurulumu. İkisi tek
commit'e girer.

---

### Task 2: Dört testi yaz, ikisini kırmızı gör, commit'le

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.test.jsx` (dosyanın
  sonuna yeni bir `describe` bloğu)

**Interfaces:**
- Consumes: Task 1'in taze modül düzeni ve `renderPanel`'in `project="düğün"` varsayılanı. Ayrıca
  dosyada zaten duran yardımcılar: `promptBox()`, `variantBox()`, `modelBox()`, ve sabitler
  `SETTINGS` (`{ prompts: '["ilk prompt"]', negative: "", variants: 4, model: "" }`) ile
  `MODELS` (`["nova.safetensors", "başka.safetensors"]`).
- Produces: dışarıya bir şey değil. Bu bloğun iki kırmızısı, uygulama döngüsünün yeşile döndüreceği
  tam liste.

- [ ] **Step 1: Yeni describe bloğunu dosyanın sonuna ekle**

Dosyanın en sonuna — *a format error* bloğunun kapanışından sonra:

```jsx
describe("GeneratePanel — coming back to the form", () => {
  it("keeps a prompt that was typed but never sent", () => {
    const first = renderPanel();

    fireEvent.change(promptBox(), { target: { value: '["yazdım ama göndermedim"]' } });
    first.unmount();

    // Opening a frame tears the whole project screen down, this panel with it. What was typed
    // reached no disk -- only pressing the button does that -- so React dropping the state is the
    // whole of the loss.
    renderPanel();

    expect(promptBox().value).toBe('["yazdım ama göndermedim"]');
  });

  it("keeps the negative, the model and the variant count too", () => {
    const first = renderPanel();

    fireEvent.change(screen.getByDisplayValue(""), { target: { value: "bulanık" } });
    fireEvent.change(modelBox(), { target: { value: "başka.safetensors" } });
    fireEvent.change(variantBox(), { target: { value: "9" } });
    first.unmount();

    // One form, one loss: remembering the prompt and forgetting the three boxes under it would be
    // remembering half of an unfinished piece of work.
    renderPanel();

    expect(screen.getByDisplayValue("bulanık")).toBeTruthy();
    expect(modelBox().value).toBe("başka.safetensors");
    expect(variantBox().value).toBe("9");
  });

  it("fills the boxes from the record when nothing has been typed yet", () => {
    renderPanel({ settings: { ...SETTINGS, prompts: '["kayıttaki"]', variants: 6 } });

    // The first visit of a session has nothing to go on, and the project's own record is where the
    // boxes come from. Losing this would mean showing someone else's text to a user who typed none.
    expect(promptBox().value).toBe('["kayıttaki"]');
    expect(variantBox().value).toBe("6");
  });

  it("does not carry one project's draft into another", () => {
    const first = renderPanel();

    fireEvent.change(promptBox(), { target: { value: '["düğünün prompt listesi"]' } });
    first.unmount();

    renderPanel({ project: "balo" });

    // What is half-written is the user's work in one project, never a fact about the app.
    expect(promptBox().value).toBe('["ilk prompt"]');
  });
});
```

**Negatif kutusunun neden `getByDisplayValue("")` ile bulunduğu:** o `<input>`'un yer tutucusu ve
erişilebilir adı yok, ve `SETTINGS.negative` boş dize. Dosyada onu adlandıran bir yardımcı da yok.
Boş görünen tek alan o: prompt kutusunda `'["ilk prompt"]'`, varyantta `"4"`, modelde
`"nova.safetensors"` yazıyor. Aynı sorgu ikinci testte yazılan metni geri okumak için de kullanılıyor
(`getByDisplayValue("bulanık")`).

**Varyantın neden 9 olduğu:** kutu 1–26 arasını alıyor (`acceptsVariants`), 9 aralığın içinde ve
`SETTINGS.variants`in 4'ünden de yeni bir projenin varsayılanı 2'den de farklı — yani kutuda 9
görmek yalnız hatırlandığı için mümkün.

**Dördüncü testin neden `'["ilk prompt"]'` beklediği:** `renderPanel({ project: "balo" })` yardımcının
`settings={SETTINGS}` varsayılanını koruyor, `SETTINGS.prompts` da o. Yani beklenen değer "kayıttan
gelen", ve testin söylediği şey "düğünün taslağı değil".

- [ ] **Step 2: İkisinin kırmızı, ikisinin yeşil olduğunu gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `GeneratePanel.test.jsx` **33 tests, 2 failed.** Düşenler:

- *keeps a prompt that was typed but never sent* — beklenen
  `'["yazdım ama göndermedim"]'`, gelen `'["ilk prompt"]'`.
- *keeps the negative, the model and the variant count too* — `getByDisplayValue("bulanık")` hiçbir
  şey bulamıyor ve atıyor.

Yeşil kalması gerekenler: *fills the boxes from the record when nothing has been typed yet* ve
*does not carry one project's draft into another*.

Dosyanın toplamı **33**, takımın toplamı **579** (bugünkü 575 + 4).

**Dört değil iki düşerse dur.** Üçüncü ya da dördüncü test bugün düşüyorsa yazılışında bir hata var
— ikisi de bugünün davranışını anlatıyor ve bugün doğrular.

- [ ] **Step 3: Arka yüz takımını da koştur**

Run: `python -m pytest queen-editor -q`

Expected: **711 passed.** Bu döngü arka yüze hiç dokunmuyor; koşulma sebebi CLAUDE.md'nin iki sabit
satırı.

- [ ] **Step 4: Değişen her şeyi gör**

Run: `git status --short`

Expected: yalnız `GeneratePanel.test.jsx` ve `docs/superpowers` altındaki iki yeni belge.
`GeneratePanel.jsx` ve `dist/` bu listede **olmamalı.**

- [ ] **Step 5: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): red for text that was typed and never sent

Typing into the photo form and then looking at a frame costs the text. The
boxes are seeded from the project record at mount and reach disk only when the
queue button is pressed; the address swaps the whole screen, React drops the
state of a component that no longer exists, and the new instance opens on what
was last sent.

Four tests, two of them red: the prompt survives the round trip, and so do the
negative, the model and the variant count. One form, one loss -- remembering
half of an unfinished piece of work would be its own kind of wrong.

The two green ones are holders. A first visit still fills the boxes from the
record, and one project's half-written prompt never appears in another.

The file moves to a fresh module per test in the same commit. The store the
next tour writes will live at module level, and without this a test that types
into a box would be deciding what the next one opens with -- the count that
starts at two for a project with nothing saved is the one that would have gone
first. No mocks in this file, so resetModules alone rebuilds it.

The panel does not read a project yet. The tests pass one from today so the
fourth can name another, and so that reads as a value over a default rather
than a stray.

No dist in this commit: the front end source is untouched.

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:**

| Spec'te ne diyor | Planda nerede |
|---|---|
| Dört kutunun dördü birden | Task 2 Step 1, testler 1 ve 2 |
| Panel sökülüp kurulunca metin duruyor | Task 2 Step 1, test 1 |
| Test başına taze modül | Task 1 Step 1 |
| `vi.clearAllMocks()` gerekmiyor | Task 1 **Interfaces** |
| Mevcut 29 testin cümlesi değişmiyor | Global Constraints, Task 1 Step 3 |
| Yeni prop `project` | Task 1 Step 2, Task 2 Step 1 testi 4 |
| İki kırmızı, iki yeşil tutucu | Task 2 Step 2 |
| Kod değişmiyor | Global Constraints, Task 2 Step 4 |
| `dist` tazelenmiyor | Global Constraints, Task 2 Step 4 ve commit mesajı |

Spec'te olup planda karşılığı olmayan madde yok.

**Yer tutucu yok:** Her adımda çalıştırılacak gerçek kod ve gerçek komut var; beklenen sayılar
(29 → 33, 575 → 579, 711) yazılı.

**Ad tutarlılığı:** `renderPanel`, `promptBox`, `variantBox`, `modelBox`, `SETTINGS`, `MODELS` —
hepsi dosyada bugün duran adlar ve iki görevde de aynı yazımla kullanılıyor. `project` prop'unun adı
`SidePanel`'in `QueuePanel`'e verdiğiyle aynı.

**Bilerek dışarıda:** `LayerPanel` ve detay sayfasının prompt kutuları — gerekçeleri spec'te.
