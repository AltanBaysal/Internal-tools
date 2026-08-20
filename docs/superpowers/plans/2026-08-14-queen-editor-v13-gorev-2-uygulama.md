# v13 Görev 2 — Hatanın kanıtı: İMPLEMENTASYON döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Yedi kırmızı testi yeşile çevirmek: kanıtı doğurmak, birleştirmek ve panele taşımak.

**Architecture:** Gövde metin olarak okunur ve ayrıştırma onun üstünde denenir; her iki hata dalı da
aynı yardımcıdan doğar; hook'lar mesaj yerine birleştirilmiş metni saklar.

**Tech Stack:** React 18, vitest, jsdom, Vite.

**Tasarım:** [uygulama spec'i](../specs/2026-08-14-queen-editor-v13-gorev-2-uygulama-design.md)

## Global Constraints

- Testler **değişmiyor**.
- Yorumlar **İngilizce**, yalnız NEDEN'i söylüyor.
- Commit mesajında **çift tırnak yok**.
- Komut: `npm test --prefix queen-editor/frontend`
- `dist/` **aynı commit'te** yeniden derlenir.
- Commit **yeşil** gider.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/shared/api.js` | kanıtın doğuşu | `request()` değişir |
| `frontend/src/shared/failure_text.js` | birleştirme | iskelet dolar |
| `.../photo_generation/useGeneration.js` | kanıtı saklamak | çağrı yerleri değişir |
| `.../photo_generation/useModels.js` | aynı | tek satır |
| `.../producers/useProducers.js` | aynı | tek satır |

---

### Task 1: Kanıtı doğur

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.js:9-36`

**Interfaces:**
- Produces: `request()`in fırlattığı her hata `err.evidence` taşır — `"<METOT> <yol>"` ilk satır,
  sonra ya tarayıcının metni/zaman aşımı notu, ya da `"<kod> <statusText>"` ve ham gövde.
  `err.field` bugünkü gibi duruyor.

- [ ] **Step 1: `request()` ve yanına bir yardımcı**

`api.js`'te `const TIMEOUT_MS` satırından sonra, `request()`'in yerine:

```js
// The sentence a panel shows, and beside it what a developer needs to act: which request, what came
// back, and the body verbatim. Never a guessed cause -- every line is either what we did or what
// the service said.
function failure(said, evidence) {
  const err = new Error(said);
  err.evidence = evidence;
  return err;
}

async function request(path, options) {
  const method = options?.method || "GET";
  let resp;
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    resp = await fetch(path, { ...options, signal: controller.signal });
  } catch (err) {
    // fetch rejects with a browser-English TypeError (or AbortError on timeout) when the tunnel is
    // unreachable. AbortError's own text names our own abort rather than the server, so what goes
    // down is what we can honestly say: which request, and that we cut it after ten seconds.
    const detail = err.name === "AbortError" ? `Zaman aşımı (${TIMEOUT_MS / 1000} sn)` : err.message;
    throw failure("Sunucuya ulaşılamadı — bağlantıyı kontrol et.", `${method} ${path}\n${detail}`);
  } finally {
    clearTimeout(timer);
  }
  // Bytes first, parsing after. A body is read once and only once, so parsing straight into JSON
  // threw away every answer that was not JSON -- which is exactly what a tunnel's error page is.
  const raw = await resp.text();
  let body = null;
  try {
    body = JSON.parse(raw);
  } catch {
    body = null; // empty or non-JSON body (e.g. a tunnel error page)
  }
  if (!resp.ok) {
    // The server's sentence is an answer, not a diagnosis: the same words come back with a 400 and
    // with a 500, so the code goes into the evidence even when there is a sentence to show.
    const err = failure(body?.error || `${resp.status} ${resp.statusText}`,
                        `${method} ${path}\n${resp.status} ${resp.statusText}\n${raw}`);
    // Which input the server blamed, when it says so -- the panel marks that box (spec §4).
    if (body?.field) err.field = body.field;
    throw err;
  }
  return body;
}
```

Dosyanın başındaki yorum bloğunun ikinci cümlesi de gerçeği söyleyecek şekilde kalır: mesaj
sunucunun kendi metni, kanıt onun yanında.

- [ ] **Step 2: Koştur**

Run: `npm test --prefix queen-editor/frontend -- api`
Expected: hepsi yeşil.

---

### Task 2: Birleştir ve taşı

**Files:**
- Modify: `queen-editor/frontend/src/shared/failure_text.js`
- Modify: `queen-editor/frontend/src/features/photo_generation/useGeneration.js`
- Modify: `queen-editor/frontend/src/features/photo_generation/useModels.js`
- Modify: `queen-editor/frontend/src/features/producers/useProducers.js`

- [ ] **Step 1: İskeleti doldur**

```js
// The sentence a panel draws and the proof its copy button hands over travel as one string: line
// one is read, the rest is evidence. QueuePanel splits them at that first newline, so a failure
// that carries no proof must not gain an empty line here.
export function failureText(err) {
  return err.evidence ? `${err.message}\n${err.evidence}` : err.message;
}
```

- [ ] **Step 2: `useGeneration.js`**

Import eklenir (`shared/api.js` import'unun ardına, alfabetik):

```js
import { failureText } from "../../shared/failure_text.js";
```

`setError(err.message)` geçen her yer `setError(failureText(err))` olur. Sıra kaydının kendi cümlesi
olan satır da sarmalı alır:

```js
          setError(`Sıra kaydedilemedi.\n${failureText(err)}`);
```

- [ ] **Step 3: `useModels.js` ve `useProducers.js`**

İkisinde de aynı import, ve `setError(err.message)` → `setError(failureText(err))`.

- [ ] **Step 4: Bütün takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: 360 geçen, 0 düşen.

---

### Task 3: Derle ve yeşil commit

- [ ] **Step 1: Derle**

Run: `npm run build --prefix queen-editor/frontend`

- [ ] **Step 2: Commit**

```bash
git add queen-editor/frontend/src queen-editor/frontend/dist docs/superpowers
git commit -F - <<'EOF'
feat(queen-editor): let an error carry the request it came from

The screen said a request went unanswered without saying which one. Now every
failure carries its own proof beside its sentence: the method and path, what
came back, and the body as it arrived.

The body is read as bytes and parsed afterwards. It used to go straight to
JSON, so anything that would not parse became null -- which is exactly what a
tunnel error page is, and exactly the line worth having.

The network branch drops its second line: the browser text moved into the
evidence rather than living in two places. An abort keeps naming what we did,
not a cause we would have to invent for it.

Panels with a raw box join the two into one string and the copy button hands it
over. Forms keep reading the sentence alone, since a proof block under a name
field would be noise where a single line belongs.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** "Ne geliyor"un dört paragrafı → Task 1 (metin-önce okuma, iki alanlı hata, ağ
dalının tek satırı), Task 2 (birleştirme ve üç hook). "Değişen yerler" tablosunun altı satırı →
Task 1, 2 ve Task 3 Step 1.

**Tip tutarlılığı:** `evidence` her yerde `\n` ile ayrılmış bir string; `failureText` aynı ayraçla
ekliyor; `describeError` ilk `\n`'den bölüyor.

**Kontrol edilen tuzak:** `JSON.parse("")` fırlatır, yani gövdesiz bir 204 `body = null` olur —
bugünkü davranışın aynısı. `resp.json()` da boş gövdede fırlatıyordu; değişen sıra, sonuç değil.

**Kontrol edilen tuzak 2:** `options?.method` — `request(path)` tek argümanla da çağrılıyor
(`listProjects`, `getStatus`), ve `options.method` orada `TypeError` olurdu. GET varsayılanı da
sabit değil, yokluğun karşılığı.

**Kontrol edilen kapsam:** `useProjects`, `useProjectSettings`, `NewProjectModal` ve `ExportScreen`
`err.message` okumaya devam ediyor. İlk üçü tasarım gereği (kanıt kutusu yok); `ExportScreen` bu
görevin listesinde yok ve kendi kartı geldiğinde kendi kararını ister.
