# v14 Görev 33 — Ekran bilmediğini söylemez: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Üç test yazmak; hepsi düşecek. Kod bu döngüde değişmiyor.

**Architecture:** Tek bir bayrak üç dosyadan geçiyor. Testler onu üç yerde sınıyor: panelin kendisi,
sütunun geçirmesi, ve ekranın kabloyu gerçekten kurması.

**Tech Stack:** Vitest + jsdom + @testing-library/react.

**Spec:** [Görev 33 test spec'i](../specs/2026-08-24-queen-editor-v14-gorev-33-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `useGeneration.js`, `ProjectScreen.jsx`, `SidePanel.jsx`, `QueuePanel.jsx` bu
  commit'te olduğu gibi kalır.
- **Kırmızı bırakılır.** `skip`/`xfail` yok.
- **Prop adı `known`** — `useGeneration`'ın bugün zaten döndürdüğü ad. Yeni bir ad uydurmak,
  bağlanmamış olanın yanına ikinci bir kavram koymak olurdu.
- **Bayrağın varsayılanı yok.** Çağıran vermek zorunda.
- **`dist` bu commit'e girmez.**
- Dil: test adları ve yorumlar **İngilizce**; commit mesajı **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Test komutu (depo kökünden, `cd` yok): `npm test --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/QueuePanel.test.jsx` | panelin ne dediği | yardımcıya bayrak + bir test |
| `.../photo_generation/SidePanel.test.jsx` | sütunun geçirdiği | bir test |
| `.../photo_generation/ProjectScreen.test.jsx` | kablonun kurulu olması | bir test |

---

### Task 1: Panel bilmeden susar

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/QueuePanel.test.jsx`

**Interfaces:**
- Consumes: dosyanın mevcut `renderPanel` yardımcısı ve `RUNNING` sabiti.
- Produces: sözleşme — `QueuePanel` `known` adında bir prop alır; `false` iken `.wf-spinner` gösterir
  ve kuyruk hakkında hiçbir cümle kurmaz.

- [ ] **Step 1: Yardımcı bayrağı bilinir olarak versin**

`renderPanel` içinde, `job={RUNNING}` satırının altına:

```jsx
      known
```

Kırk yedi testin hepsi panelin *bildiğinde* ne dediğini sınıyor; bu satır onların hepsini bugünkü
anlamlarında tutuyor.

- [ ] **Step 2: Testi dosyanın sonuna ekle**

Son `describe` bloğunun kapanışından sonra:

```jsx
describe("QueuePanel — before the server has said anything", () => {
  it("says nothing about a queue it has not been told about", () => {
    const { container } = renderPanel({ known: false, job: { status: "idle" }, queue: null });

    // idle is a placeholder, not an answer. Saying the queue is empty over it is a claim that can
    // be flatly wrong -- a run may be flowing on the other side of the first poll.
    expect(screen.queryByText("Kuyruk boş")).toBeNull();
    expect(screen.queryByText("Fotoğraf üret panelinden kare gönder.")).toBeNull();
    // Its own waiting, in its own column -- the shape the photo panel already took (madde 31).
    expect(container.querySelector(".wf-spinner")).toBeTruthy();
  });
});
```

- [ ] **Step 3: Yalnız bunun düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `QueuePanel.test.jsx` **48 tests, 1 failed** — yeni test. Mevcut 47'si yeşil kalmalı;
düşen olursa yardımcıya eklenen satır yanlış yere gitmiştir.

---

### Task 2: Sütun bayrağı geçirir

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/SidePanel.test.jsx`

**Interfaces:**
- Consumes: dosyanın `renderColumn` yardımcısı.
- Produces: sözleşme — `SidePanel` `known` alır ve `QueuePanel`'e geçirir.

- [ ] **Step 1: Testi son `describe` bloğunun sonuna ekle**

`shows an unreadable record inside the panel, with a way to ask again` testinden sonra, aynı
bloğun içinde:

```jsx
  it("does not let the queue panel speak before the server has", () => {
    renderColumn({ known: false, job: { status: "idle" }, queue: null });

    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    // The column only carries this; the sentence it prevents belongs to the panel.
    expect(screen.queryByText("Kuyruk boş")).toBeNull();
  });
```

- [ ] **Step 2: Düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `SidePanel.test.jsx` **19 tests, 1 failed**.

---

### Task 3: Ekran kabloyu kurar

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.test.jsx`

**Interfaces:**
- Consumes: dosyanın `renderScreen` yardımcısı ve `getStatus` sahtesi.
- Produces: sözleşme — `ProjectScreen`, `useGeneration`'ın `known`'ını `SidePanel`'e geçirir.

- [ ] **Step 1: Testi dosyanın sonuna ekle**

En son `describe` bloğunun kapanışından sonra:

```jsx
describe("ProjectScreen — the queue panel before the first answer", () => {
  it("keeps it quiet until the server has said something", async () => {
    // The answer never lands: what the panel says now is what it says with nothing reported.
    getStatus.mockImplementation(() => new Promise(() => {}));
    renderScreen("sessiz");
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });

    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    // useGeneration has carried this answer all along and nobody was reading it. The wire is the
    // whole of this item, and a wire that is missing fails quietly -- which is why it is tested
    // from the screen and not only from the panel.
    expect(screen.queryByText("Kuyruk boş")).toBeNull();
  });
});
```

- [ ] **Step 2: Sahte zamanlayıcı gerekiyorsa bloğa ekle**

Bu `describe` `vi.advanceTimersByTimeAsync` kullanıyor, dolayısıyla kendi sahte saatini kurmalı.
Testin üstüne, `describe`'ın içine:

```jsx
  beforeEach(() => {
    vi.useFakeTimers();
  });
  afterEach(() => vi.useRealTimers());
```

Dosya `act`, `fireEvent`, `screen`, `vi`, `beforeEach` ve `afterEach`'i zaten içe alıyor; yeni bir
import gerekmiyor.

- [ ] **Step 3: Düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `ProjectScreen.test.jsx` **21 tests, 1 failed**.

---

### Task 4: Kırmızıyı doğrula ve commit'le

- [ ] **Step 1: Toplamı gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **3 failed** — biri `QueuePanel.test.jsx`, biri `SidePanel.test.jsx`, biri
`ProjectScreen.test.jsx`. Başka hiçbir dosya düşmemeli.

- [ ] **Step 2: Yalnız test dosyalarının değiştiğini doğrula**

Run: `git status --short`

Expected: üç `.test.jsx` ve `docs/superpowers`. Kaynak dosyalar ve `dist` bu listede **olmamalı.**

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): red for a panel that will not guess at the queue

THESE TESTS FAIL ON PURPOSE. The code that answers them is the next commit.

Before the server has said anything the queue panel says the queue is empty,
and offers the sentence about sending frames from the photo panel. It says this
over a run that may well be flowing. idle is a placeholder, not an answer.

The answer has been in the code the whole time. useGeneration keeps a flag for
whether the server has reported anything on this mount, and its own comment
describes this item exactly: a screen that acts on the placeholder decides on a
state nobody reported. The flag is computed, it is returned -- and no consumer
reads it. The work is a wire, not an idea.

Three tests, because a missing wire fails silently: the panel keeps quiet and
shows its own ring, the column carries the flag to it, and the screen really
hands it over. Only the last one would have caught what is wrong today.

The panel's forty-seven existing tests are all about what it says once it knows,
and they keep their sentences; the helper simply tells them so.

This lands before the item that keeps the open panel across a step into a frame.
In the other order that wrong sentence would reach the screen for the first time.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** B1 → Task 1. B2 → Task 2. B3 → Task 3. Spec'te olup planda karşılığı olmayan madde
yok.

**Ad tutarlılığı:** Tek yeni ad `known`, ve o da yeni değil — `useGeneration` bugün onu bu adla
döndürüyor. Üç test dosyası da aynı yazımı kullanıyor.

**Bilerek dışarıda:** Panelin *bildiğinde* ne dediği yeniden sınanmıyor. Kırk yedi test zaten onu
söylüyor, ve yardımcıya bayrağı eklemek onların hepsini o soruya cevap verir hâlde tutuyor.
