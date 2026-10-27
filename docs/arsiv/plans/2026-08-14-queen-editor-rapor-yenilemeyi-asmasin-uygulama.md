# Rapor yenilemeyi aşmasın: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `e59dc4e`'deki üç kırmızı testi yeşile çevirmek.

**Architecture:** Tek dosya: kanca bir şey hatırlıyor ve döndürdüğü durumu ona göre veriyor.

**Tech Stack:** React 18, vitest, Vite build.

**Tasarım:** [implementasyon spec'i](../specs/2026-08-14-queen-editor-rapor-yenilemeyi-asmasin-uygulama-design.md)

## Global Constraints

- **Testler değişmiyor.** `e59dc4e`'deki altı test sözleşme.
- Yorum **İngilizce**; commit mesajında **çift tırnak yok**.
- **`dist/` aynı commit'te** yeniden derlenir.
- Komutlar: `npm test --prefix queen-editor/frontend` · `npm run build --prefix queen-editor/frontend`

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../photo_generation/useGeneration.js` | ekranın iş hakkında bildiği | izlenmemiş rapor gizlenir |

---

### Task 1: Rapor, izleyene ait olur

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/useGeneration.js`

- [ ] **Step 1: Rapor sayılan durumları adlandır**

`const POLL_MS = 2000;` altına:

```js
// The two statuses that are a report rather than a state: the run is over, and this is how it went.
const REPORT = ["done", "error"];
```

- [ ] **Step 2: Hatırlayacak yeri aç**

`wasRunning` ref'inin altına:

```js
  // Has this page seen the engine in anything but an outcome? The engine keeps a finished run's
  // outcome in memory and /api/status answers with it until the next run starts, so a page opened
  // afterwards would draw a previous page's news -- and did, on top of the sound the user was
  // trying to queue (2026-08-14). Seeing one status that is not an outcome, or starting a run from
  // this page, is what makes the next outcome ours to show.
  const watched = useRef(false);
```

- [ ] **Step 3: Yoklama gördüğünü işaretlesin**

`poll()` içinde `setJob(state);` satırının **üstüne**:

```js
        if (!REPORT.includes(state.status)) watched.current = true;
```

- [ ] **Step 4: Bu sayfadan başlatılan koşu da izlenmiş sayılsın**

`startPolling` içinde, `setJob({ status: "running", project });` satırının üstüne:

```js
    // Pressing the button is watching: a run that ends before the first poll would otherwise have
    // its report hidden from the very person who asked for it.
    watched.current = true;
```

- [ ] **Step 5: Döndürülen durumu türet**

`const stopping = ...` satırının üstüne:

```js
  // What the screen is told. The raw status stays as it is -- another tab may be watching the same
  // run, and the server is not wrong; only this page's reading of it changes.
  const told = !watched.current && REPORT.includes(job.status) ? { status: "idle" } : job;
```

ve dönüş nesnesinde `job` yerine:

```js
  return { job: told, known, frames, error, errorField, stopping, queue, failures,
           current, currentLayer,
```

Geri kalanı aynı kalır.

**Adı `told`, `shown` değil:** `shown` bu dosyada zaten galeri listesi (`frames || []`). Aynı adı
ikinci kez tanımlamak dosyayı hiç yüklenmez hâle getiriyor — plan ilk yazıldığında bu gözden kaçtı,
takım üç dosyanın **hiç toplanmadığını** söyleyerek yakaladı.

- [ ] **Step 6: Takım**

Run: `npm test --prefix queen-editor/frontend`
Expected: 337 geçen, 0 düşen.

---

### Task 2: Derle ve commit'le

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): let a report belong to the run its page watched

The three tests from the previous commit go green.

The engine keeps a finished run outcome in memory and the status endpoint
answers with it until the next run starts. So a green Kuyruk tamamlandi came
back on every reload and in every tab, and on 2026-08-14 it came back on top
of the sound the user was trying to queue -- reading as though the sound had
somehow finished.

The page now remembers whether it has seen the engine in anything but an
outcome, and whether it started a run itself. Until then an outcome is a
previous page news and reads as idle. Pressing the button counts as watching,
or a run that ended before the first poll would have its report hidden from
the person who asked for it.

The server keeps answering truthfully: another tab may be watching the same
run, and the resume button and the error text are read from the same status.
What changed is one page reading of it.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** işaretleme → Step 3-4 · türetme → Step 5. Eksik yok.

**Kontrol edilen ref:** `watched` bir ref, yani değişmesi yeniden çizim tetiklemiyor — ama her
zaman `setJob`'la aynı yoklamada değişiyor, ve o çizimi zaten `setJob` tetikliyor. Sıra da bu
yüzden önemli: işaretleme `setJob`'dan önce.

**Kontrol edilen kapsam:** `stopping`, `current`, `currentLayer` ham `job`'dan okunmaya devam
ediyor. Üçü de yalnız koşarken anlamlı ve koşan bir durum hiç gizlenmiyor.

**Kontrol edilen kayıp:** gizlenen durum `{status: "idle"}` — `project` de gitmiş oluyor. Bunu
kullanan tek şey `mine`, o da yalnız `waiting`/`error` dallarında iş görüyor; ikisi de bu hâlde
zaten çizilmiyor.