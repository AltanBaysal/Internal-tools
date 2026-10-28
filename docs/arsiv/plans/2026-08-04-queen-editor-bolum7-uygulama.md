# Bölüm 7 — Arayüz tasarımla birebir + akıcı: Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** [Bölüm 7 spec'indeki](../specs/2026-08-04-queen-editor-bolum7-arayuz-design.md) 27 B7 bulgusunu kapatmak: vendor tazeleme, Durdur'un gerçekten durması, poll sağlamlığı, iskeletler, iki hata deseni, hız.

**Mimari:** Mevcut katmanlar korunur — `services/comfy` yalnız HTTP taşıma (`interrupt` eklenir), durdurma kuralı `start_batch`'in job'ında, görünüm kararları frontend bileşenlerinde. Yeni endpoint, yeni ekran, yeni veri dosyası yok.

**Stack:** Flask (sync) + React 18 + Vite; test pytest (yalnız backend — frontend doğrulaması Colab listesiyle elle).

## Global Kısıtlar

- **Kullanıcı "commit" demeden hiçbir commit atılmaz.** Task 8'deki commit adımı kapıdır; plandaki adımın varlığı izin sayılmaz. Commit pathspec ile (`git add <yollar>` + `git commit -- <yollar>`), asla `--amend` — paralel pencere kuralı. Commit'ten önce `git log -1 --oneline`.
- **Colab testi push ister:** notebook repoyu klonlar; commit+push, Colab doğrulamasından önce gelir (FOUNDATION).
- **Build before commit:** `frontend/src/` değiştiği için `npm run build` koşulur ve `dist/` **aynı commit'te** girer.
- **`vendor/` elle düzenlenmez** — Task 1 dosyayı bütünüyle `design/styles.css`'ten kopyalar; düzeltmeler `shared/app.css`'e.
- **Dil:** kod yorumları İngilizce, kullanıcıya görünen her metin Türkçe, hata metinlerinde sunucunun ham çıktısı basılır (sebep uydurma yok).
- Sıra önemli: Task 5, Task 3'ün `stopping` alanına; Task 6-7, Task 1'in CSS'ine ve Task 5'in hook şekline dayanır.

---

### Task 1: vendor/styles.css'i tasarımdan tazele + kilit istisnası

**Files:**
- Overwrite: `queen-editor/frontend/src/vendor/styles.css` (kaynak: `queen-editor/design/styles.css`, birebir)
- Modify: `queen-editor/frontend/src/shared/app.css`

**Interfaces:**
- Produces: `--ok`, `--ok-bg` token'ları; `.wf-panel--locked` kuralı; `.wf-scrim { z-index: 20 }` — Task 6'nın kartları ve kilidi bunlara dayanır.

- [ ] **Step 1: Dosyayı kopyala**

`design/styles.css` içeriğini olduğu gibi `frontend/src/vendor/styles.css` üzerine yaz (Read → Write; CSS'te export sınırı yok, tam verbatim).

- [ ] **Step 2: Doğrula**

Grep `frontend/src/vendor/styles.css`: `--ok:`, `--ok-bg:`, `wf-panel--locked`, `z-index: 20` → dördü de var. `git diff --stat -- queen-editor/frontend/src/vendor/styles.css` → tek dosya değişmiş.

- [ ] **Step 3: app.css'e kilit istisnasını ekle**

Tasarımın kilidi `> div:nth-child(-n+4)` ile ilk 4 bloğu soluklaştırır — tasarım panelinde 4 alan bloğu (Model + 3) vardır. Bizim panelde Model yok (Bölüm 14): 3 alan bloğu + aksiyon bloğu, yani kural aksiyon bloğunu da soluklaştırır. Düzeltme vendor'a değil app.css'e:

```css
/* The design's panel lock dims its first four blocks (Model + three fields). Our panel has no
   Model block yet (Part 14), so the fourth child here is the action block -- undim it. */
.wf-panel--locked > div:nth-child(4) {
  opacity: 1;
  pointer-events: auto;
}
```

- [ ] **Step 4: Görsel fark kontrolü**

`git diff -- queen-editor/frontend/src/vendor/styles.css` çıktısında beklenen farklar yalnız: `--ok`/`--ok-bg` eklenmesi, `.wf-panel--locked` kuralı, `.wf-scrim`'e `z-index: 20`, spinner/`wf-img--loading` gibi tasarımın yeni eklediği bloklar. Silinen kural varsa dur ve incele.

---

### Task 2: İptal hata değildir (backend, TDD)

Kullanıcının durdurmasıyla kesilen render `failed`/`consecutive` saymaz; toplu sonuç `stopped` olur. (`/interrupt` render'ı patlatınca istisna `job`'ın `except`'ine düşer — bugün bu, üst üste durdurmada "Üst üste 3 render başarısız" kartı üretebilir.)

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/start_batch.py:79`
- Test: `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Consumes: `runner.stop_requested()` (mevcut).
- Produces: `job()` sözleşmesi — durdurma sırasında patlayan kare `{"status": "stopped", ...}` döndürür, `failed` artmaz.

- [ ] **Step 1: Kırmızı testi yaz** (`test_photo_usecases.py` içine; dosyadaki mevcut fake'lerin adlarını kullan — test dosyasını açıp oradaki kurulum desenine uydur)

```python
def test_frame_killed_by_user_stop_is_not_a_failure():
    """A render that dies because the user stopped is 'stopped', never 'error'."""
    runner = SyncRunner()          # the file's existing synchronous runner fake

    class StoppingGenerator:
        def generate(self, prompt, negative, seed):
            runner.request_stop()          # the user pressed Durdur mid-render
            raise RuntimeError("interrupted")

    start_batch(runner, store, record, plan_store, StoppingGenerator(),
                new_seed=lambda: 1, now=lambda: "t",
                project="p", text='["a", "b", "c"]', negative="", variants=1)
    state = runner.status()
    assert state["status"] == "stopped"
    assert state["failed"] == 0
```

- [ ] **Step 2: Kırmızıyı gör**

Çalıştır (queen-editor/ içinden): `pytest backend/tests/test_photo_usecases.py -k user_stop -v`
Beklenen: FAIL — bugün `failed` 1 oluyor ya da durum `error`/`done` çıkıyor.

- [ ] **Step 3: Minimal uygulama** — `start_batch.py` job'ındaki `except` bloğunun başına:

```python
            except Exception as exc:
                if runner.stop_requested():
                    # The user's own stop killed this render -- that is not a failure.
                    return {"status": "stopped", "done": done, "failed": failed, "total": total}
                failed += 1
```

(Geri kalanı aynı kalır.)

- [ ] **Step 4: Yeşili gör**

`pytest backend/tests/test_photo_usecases.py -v` → yeni test PASS, eskiler PASS.

---

### Task 3: /api/stop gerçekten durdurur + "stopping" görünür (backend, TDD)

**Files:**
- Modify: `queen-editor/backend/services/comfy/client.py` (yeni `interrupt`)
- Modify: `queen-editor/backend/features/photo_generation/runner.py:24-26` (`status` stopping bayrağı)
- Modify: `queen-editor/backend/features/photo_generation/domain/usecases/stop_generation.py`
- Modify: `queen-editor/backend/main.py:53`
- Test: `queen-editor/backend/tests/test_comfy_client.py`, `queen-editor/backend/tests/test_photo_usecases.py`

**Interfaces:**
- Produces: `ComfyClient.interrupt()` — `POST {base}/interrupt`, gövdesiz; `stop_generation(runner, interrupt)` — yeni ikinci parametre; `/api/status` ve `/api/stop` yanıtında `"stopping": true` (yalnız running + bayrak kalkıkken). Task 5'in frontend'i bu alanı okur.

- [ ] **Step 1: Kırmızı testler**

`test_comfy_client.py` (dosyadaki fake-http desenini kullan):

```python
def test_interrupt_posts_to_comfy():
    http = FakeHttp()              # the file's existing fake, records calls
    client = ComfyClient("http://c", http=http)
    client.interrupt()
    assert ("POST", "http://c/interrupt") in http.calls
```

`test_photo_usecases.py`:

```python
def test_stop_generation_interrupts_and_reports_stopping():
    runner = PhotoRunner(spawn=lambda fn: None)     # claimed but never runs the job
    runner.start("p", lambda: {"status": "done"})
    calls = []
    state = stop_generation(runner, interrupt=lambda: calls.append("interrupt"))
    assert calls == ["interrupt"]
    assert state["status"] == "running" and state["stopping"] is True


def test_stop_generation_survives_interrupt_failure():
    """A dead ComfyUI must not turn Durdur into a 500 -- the flag alone already stops the batch."""
    runner = PhotoRunner(spawn=lambda fn: None)
    runner.start("p", lambda: {"status": "done"})

    def broken_interrupt():
        raise RuntimeError("connection refused")

    state = stop_generation(runner, interrupt=broken_interrupt)
    assert state["stopping"] is True
```

- [ ] **Step 2: Kırmızıyı gör**

`pytest backend/tests/test_comfy_client.py backend/tests/test_photo_usecases.py -v` → üç yeni test FAIL (interrupt yok, stopping yok, imza eski).

- [ ] **Step 3: Uygulama**

`client.py` sonuna:

```python
    def interrupt(self):
        """Cut whatever ComfyUI is rendering right now; harmless when nothing runs."""
        resp = self._http.post(f"{self.base}/interrupt", timeout=30)
        resp.raise_for_status()
```

`runner.py` `status`:

```python
    def status(self):
        with self._lock:
            state = dict(self._state)
            if state.get("status") == "running" and self._stop:
                state["stopping"] = True
            return state
```

`stop_generation.py`:

```python
"""Ask the running batch to stop and cut the render in flight."""


def stop_generation(runner, interrupt):
    """Raise the flag, interrupt ComfyUI, return the current state (idle is a no-op).

    The flag alone already ends the batch between frames; the interrupt only shortens the frame
    in flight, so a dead ComfyUI must not fail the request.
    """
    runner.request_stop()
    try:
        interrupt()
    except Exception:
        pass
    return runner.status()
```

`main.py:53`: `stop_generation=partial(stop_generation, _photo_runner, _comfy_client.interrupt),`

- [ ] **Step 4: Yeşili gör**

`pytest` (tümü, queen-editor/ içinden) → hepsi PASS.

---

### Task 4: /photos cache başlığı (backend, TDD)

**Files:**
- Modify: `queen-editor/backend/features/photo_generation/presentation/routes.py:57-60`
- Test: `queen-editor/backend/tests/test_photo_routes.py`

- [ ] **Step 1: Kırmızı test** (`test_photo_routes.py`, dosyadaki mevcut app-kurulum desenine uydur)

```python
def test_photo_response_is_immutably_cacheable(client_with_photo):
    resp = client_with_photo.get("/photos/p/0_a.png")
    assert resp.status_code == 200
    assert resp.headers["Cache-Control"] == "public, max-age=31536000, immutable"
```

- [ ] **Step 2: Kırmızıyı gör** → `pytest backend/tests/test_photo_routes.py -v` → FAIL (başlık yok).

- [ ] **Step 3: Uygulama** — `routes.py`:

```python
    @bp.get("/photos/<project>/<filename>")
    def serve_photo(project, filename):
        # send_from_directory rejects paths that escape the folder.
        resp = send_from_directory(photo_dir(project), filename)
        # next_number never reuses a number, so a photo URL's bytes can never change.
        resp.headers["Cache-Control"] = "public, max-age=31536000, immutable"
        return resp
```

- [ ] **Step 4: Yeşili gör** → `pytest` → hepsi PASS.

---

### Task 5: api.js ulaşılamama mesajı + useGeneration sağlamlığı (frontend)

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js:4-14`
- Modify: `queen-editor/frontend/src/features/photo_generation/useGeneration.js` (tamamı aşağıda)

**Interfaces:**
- Produces: `useGeneration` dönüşü `{ job, photos, error, stopping, generate, stop }` — `photos` **`null` = henüz bilinmiyor** (Task 6-7 iskelet basar), `[]` = gerçekten boş; `stopping` = kullanıcı bastı **veya** sunucu `job.stopping` diyor. Task 6-7 bu sözleşmeye göre yazılır.

- [ ] **Step 1: api.js — fetch reddi Türkçeleşir** (`request` başı):

```js
async function request(path, options) {
  let resp;
  try {
    resp = await fetch(path, options);
  } catch (err) {
    // fetch rejects with a browser-English TypeError when the tunnel is unreachable; say it in
    // Turkish and keep the raw text underneath (we never guess the cause).
    throw new Error(`Sunucuya ulaşılamadı — bağlantıyı kontrol et.\n${err.message}`);
  }
  let body = null;
  ...   // (devamı aynı)
```

- [ ] **Step 2: useGeneration.js'i şu içerikle değiştir**

```js
import { useCallback, useEffect, useRef, useState } from "react";

import { generateBatch, getStatus, listPhotos, stopGeneration } from "../../shared/api.js";

const POLL_MS = 2000;

// A batch runs for minutes, so the server answers 202 and we ask /api/status until it settles.
// The gallery refreshes on every poll: Drive is the truth about what exists.
export function useGeneration(project) {
  const [job, setJob] = useState({ status: "idle" });
  // null = not known yet (first fetch still flying), [] = the project truly has no photos.
  const [photos, setPhotos] = useState(null);
  const [error, setError] = useState(null);   // rejected request or unreachable server
  const [stopPressed, setStopPressed] = useState(false);
  const timer = useRef(null);

  const refreshPhotos = useCallback(() => {
    listPhotos(project)
      .then(setPhotos)
      .catch((err) => setError(err.message));
  }, [project]);

  const poll = useCallback(() => {
    // Photos are asked for regardless of the status call's fate -- a dead status endpoint must
    // not leave the gallery lying about what exists.
    refreshPhotos();
    getStatus()
      .then((state) => {
        setJob(state);
        setError(null);                       // a successful poll clears a stale connection error
        if (state.status !== "running") setStopPressed(false);
        if (state.status === "running") {
          timer.current = setTimeout(poll, POLL_MS);
        }
      })
      .catch((err) => {
        setError(err.message);
        // One bad poll must not kill the chain -- otherwise the bar freezes as "fake alive"
        // and the screen never notices the tunnel coming back.
        timer.current = setTimeout(poll, POLL_MS);
      });
  }, [refreshPhotos]);

  useEffect(() => {
    poll();
    return () => clearTimeout(timer.current);
  }, [poll]);

  const generate = useCallback(
    (form) => {
      setError(null);
      return generateBatch(project, form)
        .then(() => {
          setJob({ status: "running", project, done: 0, failed: 0, total: 0 });
          timer.current = setTimeout(poll, POLL_MS);
        })
        .catch((err) => setError(err.message));
    },
    [project, poll],
  );

  const stop = useCallback(() => {
    setStopPressed(true);                     // instant feedback; the server confirms via polls
    return stopGeneration().then(setJob).catch((err) => setError(err.message));
  }, []);

  // The server also reports "stopping" (survives a reload); either source disables the button.
  const stopping = stopPressed || Boolean(job.stopping);

  return { job, photos, error, stopping, generate, stop };
}
```

Not: hata dalındaki `setTimeout` boşta da tekrar dener — bu bilinçli: sunucu geri gelince ekran
kendiliğinden toparlanır ve `setError(null)` bayat hatayı siler (spec doğrulama 9).

- [ ] **Step 3: Doğrula**

`npm run build` (queen-editor/frontend/ içinden) → hatasız derlenir. (Görsel doğrulama Task 8'in Colab listesinde.)

---

### Task 6: GeneratePanel + ProgressPanel — kartlar, kilit, tek mesaj (frontend)

**Files:**
- Create: `queen-editor/frontend/src/shared/StatusErrorCard.jsx` (spec §4 "durum hatası" deseni — tek bileşen, Task 7 de kullanır)
- Modify: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.jsx` (aşağıdaki parçalar)
- Modify: `queen-editor/frontend/src/features/photo_generation/ProgressPanel.jsx` (tamamı aşağıda)
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx:56-59` (yeni prop'lar)

**Interfaces:**
- Consumes: Task 1'in CSS'i (`--ok`, `--ok-bg`, `wf-panel--locked` + app.css istisnası), Task 5'in `{ stopping }` ve `photos:null` sözleşmesi.
- Produces: `GeneratePanel({ job, error, busyElsewhere, settings, project, stopping, onGenerate, onStop })` ve `ProgressPanel({ job, stopping, onStop })` imzaları; `StatusErrorCard({ text, raw, onRetry })` — `onRetry` verilmezse buton yok.

- [ ] **Step 0: shared/StatusErrorCard.jsx** (yeni dosya):

```jsx
import { Btn, Icon, Mono, Note } from "../vendor/kit.jsx";

// Spec §4's "state error" card: danger border AND danger background, one plain sentence, the
// server's raw text as a bare mono line -- no nested box. Optional retry for screen-level
// failures; the panel's cards simply omit it.
export function StatusErrorCard({ text, raw, onRetry }) {
  return (
    <div className="wf-stroke"
         style={{ padding: "8px 10px", display: "flex", flexDirection: "column", gap: 6,
                  maxWidth: 640, borderColor: "var(--danger)", background: "var(--danger-bg)" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--danger)" }}>
        <Icon.Warn />
        <Note size={12} style={{ color: "var(--danger)", fontWeight: 500 }}>{text}</Note>
      </div>
      {raw && (
        <Mono size={10} style={{ color: "var(--ink-3)", whiteSpace: "pre-wrap",
                                 wordBreak: "break-word" }}>{raw}</Mono>
      )}
      {onRetry && (
        <Btn sm onClick={onRetry} style={{ alignSelf: "flex-start" }}>
          <Icon.Regen /> Tekrar dene
        </Btn>
      )}
    </div>
  );
}
```

- [ ] **Step 1: ProgressPanel.jsx'i şu içerikle değiştir**

```jsx
import { Btn, Mono, Note } from "../../vendor/kit.jsx";

const BOX = { padding: "8px 10px", display: "flex", flexDirection: "column", gap: 8 };
const TRACK = { height: 5, background: "var(--bg-3)", borderRadius: 3, overflow: "hidden" };

// Artboard 04: a full-width muted Durdur ABOVE the progress card -- same size as Üret, never
// accent-coloured. The card below only shows progress.
export default function ProgressPanel({ job, stopping, onStop }) {
  const { done = 0, failed = 0, total = 0, current } = job;
  const finished = done + failed;
  // total is 0 on the first poll after the 202: the server has not planned the frames yet.
  const percent = total ? Math.round((finished / total) * 100) : 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
      <Btn onClick={onStop} disabled={stopping}
           style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14,
                    color: "var(--ink-2)" }}>
        {stopping ? "Durduruluyor…" : "Durdur"}
      </Btn>

      <div className="wf-stroke" style={BOX}>
        <Mono size={13} style={{ color: "var(--accent)" }}>{finished} / {total || "…"}</Mono>
        <div style={TRACK}>
          <div style={{ width: `${percent}%`, height: "100%", background: "var(--accent)" }} />
        </div>
        {current && (
          <Note size={12} style={{ color: "var(--ink-2)", whiteSpace: "nowrap",
                                   overflow: "hidden", textOverflow: "ellipsis" }}>
            şimdi: "{current.prompt}"
          </Note>
        )}
        {failed > 0 && (
          <Note size={12} style={{ color: "var(--danger)" }}>
            {failed} fotoğraf üretilemedi — diğerleri devam ediyor
          </Note>
        )}
      </div>
    </div>
  );
}
```

- [ ] **Step 2: GeneratePanel — imza, kilit ve tek-mesaj düzeni**

Değişen parçalar (dosyanın geri kalanı — `countPrompts`, alan blokları, sabitler — aynı kalır;
`RAW_ERROR` sabiti silinir):

```jsx
export default function GeneratePanel({ job, error, busyElsewhere, settings, project, stopping,
                                        onGenerate, onStop }) {
  const [prompts, setPrompts] = useState(settings.prompts);
  const [negative, setNegative] = useState(settings.negative);
  const [variants, setVariants] = useState(
    settings.variants === null ? "4" : String(settings.variants),
  );
  const [submitting, setSubmitting] = useState(false);

  const running = job.status === "running" && !busyElsewhere;
  const locked = running || submitting;
  // Another project's finished batch must not talk into this panel (state leaks across projects
  // otherwise -- the worker is global but the words on screen are this project's).
  const mine = job.project === project;
  const count = countPrompts(prompts);
  const perPrompt = Number(variants);
  const planned = count !== null && Number.isInteger(perPrompt) && perPrompt > 0
    ? count * perPrompt
    : null;

  function handleGenerate() {
    setSubmitting(true);
    onGenerate({
      prompts,
      negative,
      variants: Number.isInteger(perPrompt) && variants.trim() !== "" ? perPrompt : null,
    }).finally(() => setSubmitting(false));
  }
```

Panel kökü ve alanlar (kilit görünümü CSS'ten, gerçek kilit `disabled`'dan):

```jsx
  return (
    <div className={locked ? "wf-panel wf-panel--locked" : "wf-panel"} style={PANEL}>
      {/* üç alan bloğu aynı; yalnız girişlere disabled={locked} eklenir: */}
      {/*   <textarea ... disabled={locked} />  <input ... disabled={locked} />  (negatif + varyant) */}
```

Alt blok — **aynı anda en fazla bir mesaj**, öncelik sırası: taze istek hatası → bu projenin
hata kartı → bu projenin bitti/durdu kartı → başka projede üretim notu:

```jsx
      {running ? (
        <ProgressPanel job={job} stopping={stopping} onStop={onStop} />
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
          <Btn hl disabled={!prompts.trim() || busyElsewhere || submitting}
               onClick={handleGenerate}
               style={{ justifyContent: "center", padding: "10px 12px", fontSize: 14 }}>
            {submitting ? "Başlatılıyor…" : <><Icon.Sparkle /> Üret</>}
          </Btn>

          {error ? (
            <StatusErrorCard text="İstek reddedildi" raw={error} />
          ) : mine && job.status === "error" ? (
            <StatusErrorCard text={`Üretim durdu — ${job.done}/${job.total} tamamlandı`}
                             raw={job.error} />
          ) : mine && job.status === "done" ? (
            <div className="wf-stroke"
                 style={{ padding: "8px 10px", display: "flex", alignItems: "center", gap: 8,
                          borderColor: "var(--ok)", background: "var(--ok-bg)" }}>
              <Mono size={13} style={{ color: "var(--ok)" }}>✓</Mono>
              <Note size={12} style={{ color: "var(--ok)" }}>
                {job.done} / {job.total} üretildi — tamamlandı
              </Note>
            </div>
          ) : mine && job.status === "stopped" ? (
            <div className="wf-stroke" style={{ padding: "8px 10px" }}>
              <Note size={12} style={{ color: "var(--ink-2)", display: "block" }}>
                Üretim durduruldu — {job.done}/{job.total} tamamlandı
              </Note>
            </div>
          ) : busyElsewhere ? (
            <Note size={12} style={{ color: "var(--ink-3)" }}>
              Üretim sürüyor: {job.project} — bitmesini bekle.
            </Note>
          ) : planned !== null ? (
            <Mono size={11} style={{ color: "var(--ink-3)", textAlign: "center" }}>
              {count} prompt × {perPrompt} varyant = <span style={{ color: "var(--accent)" }}>{planned} foto</span>
            </Mono>
          ) : null}
        </div>
      )}
    </div>
  );
```

("N × M" satırı yalnız hiçbir durum mesajı yokken görünür — "bitti kartıyla aynı anda durmaz"
kuralı bu zincirle kendiliğinden sağlanır.)

Dosyanın importlarına: `import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";`
(`RAW_ERROR` sabiti ve eski iç içe kutulu hata bloğu silinir.)

- [ ] **Step 3: ProjectScreen'den yeni prop'ları geçir** (`ProjectScreen.jsx`):

```jsx
  const { job, photos, error, stopping, generate, stop } = useGeneration(project);
  ...
        <GeneratePanel job={job} error={saveError || error} busyElsewhere={busyElsewhere}
                       settings={settings} project={project} stopping={stopping}
                       onGenerate={handleGenerate} onStop={stop} />
```

(`handleGenerate` zaten async — promise döndürüyor, `finally` çalışır.)

- [ ] **Step 4: Doğrula** → `npm run build` hatasız.

---

### Task 7: İskeletler, ProjectsScreen, NewProjectModal, Gallery, Projeden çık (frontend)

**Files:**
- Create: `queen-editor/frontend/src/features/photo_generation/ProjectSkeleton.jsx`
- Modify: `queen-editor/frontend/src/App.jsx`
- Modify: `queen-editor/frontend/src/features/projects/useProjectSettings.js` (reload eklenir)
- Modify: `queen-editor/frontend/src/features/projects/ProjectsScreen.jsx`
- Modify: `queen-editor/frontend/src/features/projects/NewProjectModal.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/Gallery.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx:48` (nötr renk)

**Interfaces:**
- Consumes: Task 5'in `photos: null` sözleşmesi.
- Produces: `useProjectSettings` dönüşüne `reload` eklenir (`{ status, settings, error, save, reload }`).

- [ ] **Step 1: ProjectSkeleton.jsx** (yeni dosya):

```jsx
import { Hand } from "../../vendor/kit.jsx";

const DASHED = { aspectRatio: "1/1" };

// The project screen's shape while settings load: same bar, empty dashed panel and grid.
// A blank white page reads as "broken"; this reads as "coming" (spec §2.2).
export default function ProjectSkeleton({ project }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={{ display: "grid", gridTemplateColumns: "1fr auto 1fr", alignItems: "center",
                    padding: "14px 32px", background: "var(--bg-2)",
                    borderBottom: "1px solid var(--border)" }}>
        <Hand size={20}><span className="wf-hl">Queen Editor</span></Hand>
        <Hand size={20}>{project}</Hand>
        <span />
      </div>
      <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
        <div style={{ flex: 1, padding: 16 }}>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12,
                        alignItems: "start" }}>
            {Array.from({ length: 10 }, (_, i) => (
              <div key={i} className="wf-stroke wf-stroke--dashed" style={DASHED} />
            ))}
          </div>
        </div>
        <div style={{ width: 320, flexShrink: 0, borderLeft: "1px solid var(--border)",
                      padding: 16, display: "flex", flexDirection: "column", gap: 14,
                      boxSizing: "border-box" }}>
          <div className="wf-stroke wf-stroke--dashed" style={{ flex: 1 }} />
          <div className="wf-stroke wf-stroke--dashed" style={{ height: 40 }} />
          <div className="wf-stroke wf-stroke--dashed" style={{ height: 40 }} />
        </div>
      </div>
    </div>
  );
}
```

- [ ] **Step 2: useProjectSettings'e reload** (etki gövdesi callback'e çıkar):

```js
export function useProjectSettings(project) {
  const [state, setState] = useState({ status: "loading", settings: null, error: null });

  const reload = useCallback(() => {
    setState({ status: "loading", settings: null, error: null });
    return getSettings(project)
      .then((settings) => setState({ status: "ready", settings, error: null }))
      .catch((err) => setState({ status: "error", settings: null, error: err.message }));
  }, [project]);

  useEffect(() => {
    reload();
  }, [reload]);

  const save = useCallback((settings) => saveSettings(project, settings), [project]);

  return { ...state, save, reload };
}
```

(Önceki `cancelled` koruması `reload` desenine geçince kalkar — `useProjects` ile aynı şekil;
proje değişince `reload` yeniden kurulur ve state'i `loading`'e çeker, bayat cevap görünmez
olur. Aynı davranış, tek desen.)

- [ ] **Step 3: App.jsx — iskelet + ayar hatasında kart + Tekrar dene**:

```jsx
import ProjectScreen from "./features/photo_generation/ProjectScreen.jsx";
import ProjectSkeleton from "./features/photo_generation/ProjectSkeleton.jsx";
import ProjectsScreen from "./features/projects/ProjectsScreen.jsx";
import { useProjectSettings } from "./features/projects/useProjectSettings.js";
import { projectFromPath, useRoute } from "./shared/router.js";
import { StatusErrorCard } from "./shared/StatusErrorCard.jsx";

function ProjectRoute({ project }) {
  const { status, settings, error, save, reload } = useProjectSettings(project);
  if (status === "loading") return <ProjectSkeleton project={project} />;
  if (status === "error") {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center",
                    justifyContent: "center", padding: 32 }}>
        <StatusErrorCard text="Proje ayarları yüklenemedi" raw={error} onRetry={reload} />
      </div>
    );
  }
  return <ProjectScreen project={project} settings={settings} onSaveSettings={save} />;
}

export default function App() {
  const project = projectFromPath(useRoute());
  return project ? <ProjectRoute project={project} /> : <ProjectsScreen />;
}
```

`ProjectScreen`'den `settingsError` prop'u ve `EMPTY_SETTINGS` kalkar (hata artık ekrana
girmeden kartla karşılanıyor; `saveError` `useState(null)` ile başlar).

(`StatusErrorCard` Task 6'da yaratıldı — burada yalnız import edilir.)

- [ ] **Step 4: ProjectsScreen — iskelet + kart hata + boş durum butonu**:

Değişen parçalar:

```jsx
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";

const CENTERED = {
  minHeight: "70vh",     // the design centres the empty state in ~70% of the body
  display: "flex",
  flexDirection: "column",
  alignItems: "center",
  justifyContent: "center",
  gap: 8,
};
```

Gövde:

```jsx
        {status === "error" ? (
          <div style={CENTERED}>
            <StatusErrorCard text="Projeler yüklenemedi" raw={error} onRetry={reload} />
          </div>
        ) : status === "loading" ? (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 16 }}>
            {Array.from({ length: 8 }, (_, i) => (
              <div key={i} className="wf-stroke wf-stroke--dashed" style={{ aspectRatio: "4/3" }} />
            ))}
          </div>
        ) : projects.length === 0 ? (
          <div style={CENTERED}>
            <Mono size={12} style={{ color: "var(--ink-3)" }}>henüz proje yok</Mono>
            <Note size={13} style={{ color: "var(--ink-3)" }}>
              İlk projeni oluştur, fotoğrafların burada toplansın
            </Note>
            <Btn hl style={{ marginTop: 8 }} onClick={() => setModalOpen(true)}>
              <Icon.Plus /> İlk projeyi oluştur
            </Btn>
          </div>
        ) : (
```

(Eski serbest hata bloğu silinir; `Mono` importu hâlâ boş durumda kullanılıyor, kalır.)

- [ ] **Step 5: NewProjectModal — uçuşta kapanmaz, hata varken Oluştur pasif**:

```jsx
  useEffect(() => {
    const onKey = (e) => {
      // While the create request is in flight the modal must not pretend to cancel -- the
      // server is still creating the project (spec §1B).
      if (e.key === "Escape" && !busy) onCancel();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onCancel, busy]);
```

```jsx
    <div className="wf-scrim" onClick={busy ? undefined : onCancel}>
```

```jsx
          <Btn hl onClick={submit} disabled={!name || busy || Boolean(error)}>
```

(Yazmaya başlayınca `setError(null)` zaten çalışıyor — buton kendiliğinden geri açılır.)

- [ ] **Step 6: Gallery — iskelet, lazy, hizalar, yorum düzeltmesi**:

```jsx
const GRID = { display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 12,
               alignItems: "start" };
```

Bileşen başı:

```jsx
export default function Gallery({ project, photos, current }) {
  if (photos === null) {
    // First fetch still flying: "empty" is not known yet, so show shape instead of a false
    // "henüz fotoğraf yok" (spec §2.3).
    return (
      <div style={PAD}>
        <div style={GRID}>
          {Array.from({ length: 10 }, (_, i) => (
            <div key={i} className="wf-stroke wf-stroke--dashed" style={{ aspectRatio: "1/1" }} />
          ))}
        </div>
      </div>
    );
  }
  if (!photos.length && !current) {
```

`<img>` satırı:

```jsx
            {/* Placeholder until the detail page (Part 10): open the raw file in a new tab. */}
            <a href={photoUrl(project, photo.file)} target="_blank" rel="noreferrer">
              <img src={photoUrl(project, photo.file)} alt={photo.file}
                   loading="lazy" decoding="async"
                   style={{ width: "100%", aspectRatio: "1/1", objectFit: "cover",
                            border: "1px solid var(--border)", borderRadius: "var(--r-sm)",
                            display: "block" }} />
            </a>
```

- [ ] **Step 7: Projeden çık nötr** (`ProjectScreen.jsx:48`):

```jsx
        <Btn ghost style={{ justifySelf: "end" }} onClick={() => navigate("/")}>Projeden çık</Btn>
```

- [ ] **Step 8: ProjectCard — buton semantiği + rozet zemini** (`ProjectCard.jsx`; Tab/Enter ile
açılabilir olur — spec §1A'nın tasarım-ötesi bilinçli iyileştirmesi; `position: relative` Bölüm
11'in çöp butonuna zemin):

```jsx
// The card opens the project screen. A real <button> so the keyboard can open it too; the
// wf-card look is kept by resetting the button's own chrome.
export default function ProjectCard({ name, modifiedAt }) {
  return (
    <button
      type="button"
      className="wf-card"
      onClick={() => navigate(`/projects/${encodeURIComponent(name)}`)}
      style={{
        aspectRatio: "4/3",
        padding: 14,
        cursor: "pointer",
        display: "flex",
        flexDirection: "column",
        justifyContent: "space-between",
        boxSizing: "border-box",
        position: "relative",
        font: "inherit",
        color: "inherit",
        textAlign: "left",
        width: "100%",
      }}
    >
      <Hand size={16} style={{ alignSelf: "flex-start" }}>{name}</Hand>
      <Mono size={11} style={{ color: "var(--ink-3)", alignSelf: "flex-end" }}>
        {formatModified(modifiedAt)}
      </Mono>
    </button>
  );
}
```

- [ ] **Step 9: Doğrula** → `npm run build` hatasız; `git status --short` beklenen dosyalar dışında bir şey göstermiyor; kart Tab ile odaklanıp Enter ile açılıyor (tarayıcı doğrulaması Colab listesinde).

---

### Task 8: pytest + build + rapor + KAPI (commit → push → Colab)

**Files:** yok (doğrulama + kapı).

- [ ] **Step 1: Testler** — queen-editor/ içinden `pytest` → **tümü PASS** (yeni 4 test dahil).

- [ ] **Step 2: Build** — queen-editor/frontend/ içinden `npm run build` → `dist/` yenilenir.

- [ ] **Step 3: Kalıntı kontrolü** — Grep `frontend/src/`: `RAW_ERROR` kalmadı; `var(--danger)` yalnız hata/silme bağlamında; `settingsError` referansı kalmadı.

- [ ] **Step 4 (KAPI): Kullanıcıya raporla, açık "commit" onayı bekle**

Rapor: değişen dosya listesi + pytest çıktısı + build çıktısı. Not: `queen-editor/design/`
klasörünün commit'e girip girmeyeceği kullanıcıya sorulur (tasarım kaynağı snapshot'ı — girerse
sonraki bölümlerde kaynak hazır olur).

- [ ] **Step 5: Commit + push** (onay sonrası; dist aynı commit'te):

```bash
git log -1 --oneline
git add queen-editor/backend queen-editor/frontend/src queen-editor/frontend/dist
git commit -m "feat(queen-editor): Bölüm 7 — arayüz tasarımla birebir + akıcılık" -- queen-editor/backend queen-editor/frontend/src queen-editor/frontend/dist
git push
```

(design/ da onaylandıysa `git add queen-editor/design` ve pathspec'e eklenir.)

- [ ] **Step 6: Colab doğrulaması (kullanıcı)** — spec'in 15 maddelik listesi tek turda:
iskeletler (4) · cache hızı (5) · kilit + pasif Üret (6) · Durduruluyor… + hızlı duruş (7) ·
yeşil kart + önizleme gizli (8) · tünel kes-aç toparlanması (9) · çapraz proje sızmıyor (10) ·
tek biçim hata + Tekrar dene (11) · modal davranışları (12) · İlk projeyi oluştur (13) ·
nötr Projeden çık (14). Kırmızı çıkan madde bu plana yeni task olarak döner.
