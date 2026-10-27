# v14 Görev 31 — Galeri gerekmeyen bir cevabı beklemez: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Yedi test yazmak; hepsi düşecek. Kod bu döngüde değişmiyor.

**Architecture:** İki dosya, iki soru. Yeni `App.test.jsx` *"adres bir projeyi gösterdiğinde ekran
bölünüyor mu"* diye soruyor; mevcut `SidePanel.test.jsx` *"bekleyen parça ne diyor"* diye. Bekleyişin
ineceği yer fotoğraf üret panelinin kendi sütunu, ve testler o sözleşmeyi adıyla sabitliyor.

**Tech Stack:** Vitest + jsdom + @testing-library/react. `globals` kapalı — `describe`/`it`/`expect`
her dosyada `vitest`'ten adıyla alınır.

**Spec:** [Görev 31 test spec'i](../specs/2026-08-24-queen-editor-v14-gorev-31-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `App.jsx`, `ProjectScreen.jsx`, `SidePanel.jsx`, `GeneratePanel.jsx`,
  `useProjectSettings.js` bu commit'te olduğu gibi kalır. `ProjectLoading.jsx` de silinmez.
- **Kırmızı bırakılır.** `skip`/`xfail` yok.
- **`dist` bu commit'e girmez** — ön yüz kaynağı değişmiyor, yalnız testler.
- Dil: test adları ve yorumlar **İngilizce**; commit mesajı **İngilizce**; belgeler **Türkçe**.
- Commit mesajında **çift tırnak yok**.
- Test komutu (depo kökünden, `cd` yok): `npm test --prefix queen-editor/frontend`
- `vi.clearAllMocks()` kullanılır, **`resetAllMocks` kullanılmaz**: fabrikada verilen
  `mockResolvedValue` varsayılanları silinirse `getStatus()` `undefined` döner ve `.then` çağrısı
  patlar.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `queen-editor/frontend/src/App.test.jsx` | adres bir projeyi gösterdiğinde ekranda ne var | **oluştur** |
| `queen-editor/frontend/src/features/photo_generation/SidePanel.test.jsx` | sağ sütunun ne çizdiği | dört test ekle, yardımcıyı ikiye ayır |

---

### Task 1: Ekranın bölünmediğini söyleyen dosya

**Files:**
- Create: `queen-editor/frontend/src/App.test.jsx`

**Interfaces:**
- Consumes: `App.jsx`'in bugünkü dışa açık yüzü — parametresiz, adresi `window.location.pathname`
  üzerinden okuyan tek bileşen.
- Produces: implementasyon döngüsünün uyacağı sözleşme — adres bir projeyi gösterdiğinde proje
  kaydının durumu ne olursa olsun `ProjectScreen` çizilir. Kayıt beklerken de, okunamamışken de
  galeri, proje adı, `Export` düğmesi ve ray ekranda olur.

- [ ] **Step 1: Dosyayı oluştur**

`queen-editor/frontend/src/App.test.jsx`:

```jsx
import { render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getSettings, listFrames } from "./shared/api.js";
import App from "./App.jsx";

// Every export the tree imports has to be here: imports are hoisted, so App pulling in the
// projects, export and detail screens evaluates their api imports whether or not they render.
vi.mock("./shared/api.js", () => ({
  cancelExport: vi.fn(),
  cancelGeneration: vi.fn(),
  checkProjectName: vi.fn(),
  copyFrames: vi.fn(),
  createProject: vi.fn(),
  deleteProject: vi.fn(),
  fileUrl: (project, file) => `/photos/${project}/${file}`,
  generateBatch: vi.fn(),
  getExportState: vi.fn(),
  getExportSummary: vi.fn(),
  getSettings: vi.fn(),
  getStatus: vi.fn().mockResolvedValue({ status: "idle" }),
  listFrames: vi.fn().mockResolvedValue([]),
  listModels: vi.fn().mockResolvedValue([]),
  listProducers: vi.fn().mockResolvedValue([]),
  listProjects: vi.fn().mockResolvedValue([]),
  queueLayer: vi.fn(),
  regenerateFrame: vi.fn(),
  removeFrames: vi.fn(),
  removeLayer: vi.fn(),
  renameProject: vi.fn(),
  resumeBatch: vi.fn(),
  retryFailed: vi.fn(),
  retryFrame: vi.fn(),
  saveOrder: vi.fn(),
  saveSettings: vi.fn(),
  startExport: vi.fn(),
  stopGeneration: vi.fn(),
}));

const FRAME = { id: "1_a", file: "1_a.png", status: "done" };

// The gallery a project last answered with is remembered across mounts, so every test here asks
// for a project name no other test has filled.
function openProject(project) {
  window.history.pushState({}, "", `/projects/${encodeURIComponent(project)}`);
  return render(<App />);
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("App — the project screen while its record is on its way", () => {
  it("draws the gallery without waiting for the record", async () => {
    // The record never lands: what stays on screen is what the screen can do without it.
    getSettings.mockImplementation(() => new Promise(() => {}));
    listFrames.mockResolvedValue([FRAME]);

    openProject("bekleyen");

    // The tile's caption -- the gallery really drew a frame, not a holder over an empty grid.
    expect(await screen.findByText("1_a.png")).toBeTruthy();
  });

  it("keeps the bar and the rail instead of collapsing to one spinner", async () => {
    getSettings.mockImplementation(() => new Promise(() => {}));
    listFrames.mockResolvedValue([FRAME]);

    openProject("baslikli");
    await screen.findByText("1_a.png");

    // The loading screen borrowed the bar but had no Export and no rail. These three say the
    // project screen itself is up.
    expect(screen.getByText("baslikli")).toBeTruthy();
    expect(screen.getByText("Export")).toBeTruthy();
    expect(screen.getByLabelText("Kuyruğu takip et")).toBeTruthy();
  });

  it("keeps the screen when the record cannot be read", async () => {
    getSettings.mockRejectedValue(new Error("Proje bulunamadı: hatali"));
    listFrames.mockResolvedValue([FRAME]);

    openProject("hatali");
    await screen.findByText("Proje ayarları yüklenemedi");

    // The card used to stand alone in the middle of an otherwise empty page. One panel's answer
    // is not the screen's answer.
    expect(screen.getByText("1_a.png")).toBeTruthy();
    expect(screen.getByText("Export")).toBeTruthy();
  });
});
```

- [ ] **Step 2: Yalnız bu üçünün düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `App.test.jsx`'ten **3 failed**.

- *draws the gallery without waiting for the record* — `1_a.png` bulunamıyor, ekranda
  `ProjectLoading` var.
- *keeps the bar and the rail instead of collapsing to one spinner* — aynı sebep.
- *keeps the screen when the record cannot be read* — başlık cümlesi ekranda ama `1_a.png` ve
  `Export` yok.

Başka dosyadan düşen test varsa dur: bu dosya hiçbir mevcut davranışa dokunmuyor.

---

### Task 2: Bekleyişin nereye indiğini söyleyen testler

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/SidePanel.test.jsx`

**Interfaces:**
- Consumes: dosyanın mevcut `SETTINGS`, `RUNNING`, `PROMPT_BOX` sabitleri.
- Produces: implementasyon döngüsünün uyacağı üç prop adı — `settings` (nesne **ya da `null`**),
  `settingsError` (sunucunun cümlesi ya da `null`), `onRetrySettings` (yeniden sormanın yolu).
  `settings` `null` iken fotoğraf üret paneli `.wf-spinner` gösterir ve prompt kutusunu çizmez;
  `settingsError` doluyken aynı sütunda `Proje ayarları yüklenemedi` kartı ve `Tekrar dene`
  düğmesi durur. Ray ve diğer beş panel her iki hâlde de çalışır.

- [ ] **Step 1: `vi`'yi içe al**

Dosyanın ikinci satırı bugün:

```jsx
import { describe, expect, it } from "vitest";
```

Yerine:

```jsx
import { describe, expect, it, vi } from "vitest";
```

- [ ] **Step 2: Yardımcıyı ikiye ayır**

Yeni testlerden biri aynı sütunu iki kez, iki farklı prop'la çizmek zorunda — `rerender` aynı
elementi istiyor, dolayısıyla elementi kuran adım `render`'dan ayrılıyor. Mevcut testlerin
hiçbirinin çağrısı değişmiyor.

Bugünkü hâli:

```jsx
function renderColumn(props) {
  return render(
    <SidePanel
      job={{ status: "idle" }}
      error={null}
      busyElsewhere={false}
      settings={SETTINGS}
      project="düğün"
      stopping={false}
      queue={[]}
      onGenerate={() => Promise.resolve()}
      onStop={() => {}}
      onResume={() => {}}
      onCancel={() => {}}
      onClearError={() => {}}
      {...props}
    />,
  );
}
```

Yerine:

```jsx
// The element apart from the render: one test draws the same column twice, before and after the
// project record lands, and rerender has to be handed the same element.
function column(props) {
  return (
    <SidePanel
      job={{ status: "idle" }}
      error={null}
      busyElsewhere={false}
      settings={SETTINGS}
      project="düğün"
      stopping={false}
      queue={[]}
      onGenerate={() => Promise.resolve()}
      onStop={() => {}}
      onResume={() => {}}
      onCancel={() => {}}
      onClearError={() => {}}
      {...props}
    />
  );
}

function renderColumn(props) {
  return render(column(props));
}
```

- [ ] **Step 3: Dört testi dosyanın sonuna ekle**

En son `describe` bloğunun kapanışından sonra:

```jsx
describe("SidePanel — while the project record is still missing", () => {
  it("waits inside its own column", () => {
    const { container } = renderColumn({ settings: null });

    // The waiting belongs to the panel that asked for the record, not to the screen: the boxes
    // are not there yet and the ring stands where they will be.
    expect(container.querySelector(".wf-spinner")).toBeTruthy();
    expect(screen.queryByPlaceholderText(PROMPT_BOX)).toBeNull();
    // The rail is untouched, so every other panel is still one press away.
    expect(screen.getByLabelText("Kuyruğu takip et")).toBeTruthy();
  });

  it("opens the panels that never needed the record", () => {
    renderColumn({ settings: null, job: RUNNING, queue: [{ layer: "photo", owed: 2 }] });

    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    // The queue reads the server's own status, not the project's record. It had no reason to wait
    // and now it does not.
    expect(screen.getByText("Foto — üretiliyor")).toBeTruthy();
  });

  it("fills the boxes once the record lands", () => {
    const { rerender } = render(column({ settings: null }));

    rerender(column({ settings: SETTINGS }));

    // The form is still seeded once, at its own mount -- it simply mounts inside a live screen
    // now. Nothing is synced afterwards, so nothing can be typed over.
    expect(screen.getByPlaceholderText(PROMPT_BOX).value).toBe('["ilk prompt"]');
  });

  it("shows an unreadable record inside the panel, with a way to ask again", () => {
    const asked = vi.fn();

    renderColumn({ settings: null, settingsError: "Proje bulunamadı: düğün",
                   onRetrySettings: asked });

    expect(screen.getByText("Proje ayarları yüklenemedi")).toBeTruthy();
    // The gallery behind it is untouched, so the way back belongs to this column too.
    fireEvent.click(screen.getByText("Tekrar dene"));
    expect(asked).toHaveBeenCalled();
  });
});
```

- [ ] **Step 4: Yalnız bu dördünün düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `SidePanel.test.jsx`'ten **4 failed**. Dördü de aynı sebeple: `settings` `null` gelince
`GeneratePanel` açılışta `settings.prompts` okuyor ve orada patlıyor.

Bu dosyanın mevcut testlerinden düşen olmamalı — hepsi `settings` veriyor ve yardımcının ayrılması
çağrılarını değiştirmiyor.

---

### Task 3: Kırmızıyı doğrula ve commit'le

- [ ] **Step 1: Toplamı gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **7 failed** — üçü `App.test.jsx`, dördü `SidePanel.test.jsx`. Kalan her şey yeşil.

Yedi dışında bir sayı görürsen dur ve sebebini bul: bu döngünün kodu hiç değiştirmemesi gerekiyor.

- [ ] **Step 2: Yalnız beklenen dosyaların değiştiğini doğrula**

Run: `git status --short`

Expected: `App.test.jsx` (yeni), `SidePanel.test.jsx`, `docs/superpowers`. Bu listede
`App.jsx`, `SidePanel.jsx`, `GeneratePanel.jsx`, `ProjectScreen.jsx`, `ProjectLoading.jsx`,
`useProjectSettings.js` ve `dist` **olmamalı**.

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): red for a gallery that does not wait for the panel

THESE TESTS FAIL ON PURPOSE. The code that answers them is the next commit.

Opening a frame replaces the project screen, so coming back builds it again --
and while it is being built the whole page collapses to one ring: gallery, bar
and rail together. What it is waiting for is the project record, and the only
thing on screen that reads that record is the photo panel: the prompt list, the
negative, the variant count and the model box. The gallery is not even handed
it.

So a textarea's contents hold up a gallery of forty-eight pictures. The same
gap is there on the first visit; coming back is only where it shows, because
that is where something is taken away.

The waiting moves into the column that asked for it. Three tests say the screen
no longer splits -- gallery, project name, Export and rail all stand while the
record is in flight and when it cannot be read at all. Four say what the
waiting part shows: a ring in its own column, the other five panels still one
press away, the boxes filled once the record lands, and an unreadable record
answered where it was asked rather than across the whole page.

The form is still seeded once at its own mount, so nothing is synced afterwards
and typing still cannot be written over.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** B1 → Task 1 test 1. B2 → Task 1 test 2. B3 → Task 1 test 3. B4 → Task 2 test 1.
B5 → Task 2 test 2. B6 → Task 2 test 3. B7 → Task 2 test 4. Spec'te olup planda karşılığı olmayan
madde yok.

**Ad tutarlılığı:** Üç yeni prop tek yerde tanımlandı ve tek yerde kullanıldı — `settings` (nullable),
`settingsError`, `onRetrySettings`. `App.test.jsx` bu adları hiç anmıyor; o dosya yalnız ekranda ne
göründüğüne bakıyor, dolayısıyla iki dosya aynı adı iki türlü yazamaz.

**Yer tutucu yok:** Her adımda çalıştırılacak gerçek kod ve gerçek komut var.

**Bilerek dışarıda:**

- **Kuyruk panelinin ilk cevaptan önce ne dediği.** Task 2'nin ikinci testi kuyruk panelini
  `RUNNING` job'la açıyor, yani "kuyruk boş" hâline hiç girmiyor. O hâl 33. maddenin konusu; buradan
  ona bakmak, henüz kararı verilmemiş bir cümleyi bu maddenin testine yazmak olurdu.
- **`ProjectLoading.jsx` için test yok.** Dosya implementasyon döngüsünde siliniyor; silinen bir
  dosyanın testi olmaz, ve onun yerine ne geldiğini Task 1'in üç testi zaten söylüyor.
- **Hatırlama denenmiyor.** Bu döngüde kayıt her mount'ta yeniden isteniyor ve testler bunu
  değiştirmiyor. Sessizlik 32. maddenin işi.
