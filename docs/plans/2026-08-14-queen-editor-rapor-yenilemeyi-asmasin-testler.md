# Rapor yenilemeyi aşmasın: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Raporun yalnız o sayfanın izlediği koşuya ait olduğunu sınayan testleri yazmak, takımı
kırmızı commit'lemek.

**Architecture:** İki dosya — kararın yaşadığı kanca, ve ekranda görüneni okuyan ekran testi.

**Tech Stack:** React 18, vitest, jsdom.

**Tasarım:** [test spec'i](../specs/2026-08-14-queen-editor-rapor-yenilemeyi-asmasin-testler-design.md)

## Global Constraints

- **Bu döngüde üretim kodu değişmiyor.**
- Test adları ve yorumlar **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Komut: `npm test --prefix queen-editor/frontend`
- `dist/` **derlenmiyor**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/useGeneration.test.jsx` | ekranın işi hakkında bildiği | 5 test |
| `.../photo_generation/ProjectScreen.test.jsx` | ekranda görünen | 1 test |

---

### Task 1: Kancanın testleri

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/useGeneration.test.jsx`

- [ ] **Step 1: Dosyanın sonuna yeni bir blok ekle**

```jsx
// The engine keeps a finished run's outcome in memory and /api/status answers with it until the
// next run starts -- so a green Kuyruk tamamlandı came back on every reload, in every tab. On
// 2026-08-14 it came back in place of the sound the user was trying to queue. A report belongs to
// the run this page watched; anything already over when the page opened is a previous page's news.
describe("useGeneration — whose report is this", () => {
  const STOPPED = { status: "error", project: "düğün", error: "xAI HTTP 400" };

  it("says nothing about a run that was already over when the page opened", async () => {
    getStatus.mockResolvedValue(DONE);
    listFrames.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.job.status).toBe("idle");
  });

  it("says nothing about a run that had already stopped when the page opened", async () => {
    getStatus.mockResolvedValue(STOPPED);
    listFrames.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.job.status).toBe("idle");
    expect(result.current.job.error).toBeUndefined();
  });

  it("reports a run that ended while the page was watching", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listFrames.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();
    getStatus.mockResolvedValue(DONE);
    await settle(2000);

    expect(result.current.job.status).toBe("done");
    expect(result.current.job.done).toBe(4);
  });

  it("keeps the reason of a run that stopped while the page was watching", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listFrames.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();
    getStatus.mockResolvedValue(STOPPED);
    await settle(2000);

    expect(result.current.job.status).toBe("error");
    expect(result.current.job.error).toBe("xAI HTTP 400");
  });

  it("takes nothing but the report away", async () => {
    // The guard. What is owed is read off the gallery, not off the run, and it is true whoever
    // watched it -- hiding the report must not hide the work.
    getStatus.mockResolvedValue(DONE);
    listFrames.mockResolvedValue([
      { id: "P0_0", file: "P0_0.png", status: "done", owed: ["video"], failed: [] }]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.queue).toEqual([{ layer: "video", owed: 1 }]);
  });
});
```

- [ ] **Step 2: Koş**

Run: `npm test --prefix queen-editor/frontend -- src/features/photo_generation/useGeneration.test.jsx`
Expected: 2 düşen (ilk ikisi), üçü geçiyor.

---

### Task 2: Ekranın testi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.test.jsx`

- [ ] **Step 1: Dosyanın sonuna ekle**

```jsx
// What the user actually saw on 2026-08-14: a green report from a batch of photos, on a page they
// had just opened to queue sound.
describe("ProjectScreen — a report nobody on this page watched", () => {
  beforeEach(() => { vi.useFakeTimers(); });
  afterEach(() => vi.useRealTimers();

  it("opens on a finished run without repeating its good news", async () => {
    listFrames.mockResolvedValue([]);
    getStatus.mockResolvedValue({ status: "done", project: "eski", done: 20, failed: 0,
                                  total: 20 });

    renderScreen("eski");
    await act(async () => { await vi.advanceTimersByTimeAsync(0); });
    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    expect(screen.queryByText("Kuyruk tamamlandı")).toBeNull();
    expect(screen.getByText("Kuyruk boş")).toBeTruthy();
  });
});
```

- [ ] **Step 2: Koş**

Run: `npm test --prefix queen-editor/frontend -- src/features/photo_generation/ProjectScreen.test.jsx`
Expected: 1 düşen.

---

### Task 3: Takım ve kırmızı commit

- [ ] **Step 1: Tam takım**

Run: `npm test --prefix queen-editor/frontend`
Expected: 3 düşen, geri kalan yeşil.

- [ ] **Step 2: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): ask whose report the panel is showing

Red on purpose -- the implementation cycle turns these green.

The engine keeps a finished run outcome in memory and the status endpoint
answers with it until the next run starts, so a green Kuyruk tamamlandi came
back on every reload and in every tab. On 2026-08-14 it came back in place of
the sound the user was trying to queue, which is how it was found.

Three failures. Two open a page on a run that was already over -- one finished,
one stopped -- and ask to be told nothing about it. The third reads the screen
and asks that a page opened on a finished batch not repeat its good news.

Three stay green. A run that ends while the page is watching is still reported,
with its count and with its reason, and what is owed is still counted whoever
watched it. Hiding the report must not hide the work, and those three are what
say so.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** 1–5 → Task 1 · 6 → Task 2. Eksik yok.

**Kontrol edilen tuzak:** üçüncü ve dördüncü test ikinci yoklamayı `settle(2000)` ile alıyor, çünkü
zincir yalnız `running` iken kendini yeniden kuruyor — ilk durum `running` olmasaydı ikinci yoklama
hiç gelmezdi.

**Kontrol edilen bekçi:** beşinci test `queue`'ya bakıyor, `job`'a değil — borç galeriden okunuyor
ve düzeltmenin ona dokunmaması gerekiyor.
