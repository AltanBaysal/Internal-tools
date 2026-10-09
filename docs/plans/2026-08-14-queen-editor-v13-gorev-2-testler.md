# v13 Görev 2 — Hatanın kanıtı: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Bir hatanın hangi istekten geldiğini, sunucunun kodunu ve ham gövdesini taşımasını sınayan
testleri yazmak, ve takımı kırmızı commit'lemek.

**Architecture:** Kanıt `api.js`'te doğar (`err.evidence`), `failure_text.js` onu cümlenin altına
koyar, hook metni saklar, panel ilk satır sonundan bölüp ham kutuya verir. Bu döngüde yalnız
`failure_text.js` imzasıyla açılıyor.

**Tech Stack:** React 18, vitest, jsdom.

**Tasarım:** [test spec'i](../specs/2026-08-14-queen-editor-v13-gorev-2-testler-design.md)

## Global Constraints

- **Bu döngüde mantık yazılmıyor.** Tek yeni kaynak dosyası imzasıyla açılır; `api.js` ve hook'lar
  değişmiyor.
- Test adları ve yorumlar **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Komut: `npm test --prefix queen-editor/frontend`
- `dist/` **derlenmiyor** — çalışan davranış değişmedi.
- Commit **kırmızı gider**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `frontend/src/shared/failure_text.js` | cümle + kanıt birleşimi | yaratılır (iskelet) |
| `frontend/src/shared/failure_text.test.js` | birleşimin kuralı | yaratılır |
| `frontend/src/shared/api.test.js` | kanıtın doğuşu | fixture'lar genişler, 3 yeni + 2 değişen test |
| `.../photo_generation/useGeneration.test.jsx` | kanıtın taşınması | 1 yeni test |
| `.../photo_generation/QueuePanel.test.jsx` | kanıtın kutuya düşmesi | 1 yeni test (bekçi) |

---

### Task 1: Birleştiricinin iskeleti ve testleri

**Files:**
- Create: `queen-editor/frontend/src/shared/failure_text.js`
- Create: `queen-editor/frontend/src/shared/failure_text.test.js`

**Interfaces:**
- Produces: `failureText(err)` → string. Kanıtı olan hatada `"<message>\n<evidence>"`, olmayanda
  `message`. Hook'lar bunu çağıracak.

- [ ] **Step 1: İskeleti yaz**

`queen-editor/frontend/src/shared/failure_text.js`:

```js
// Skeleton only -- the rule lands in the implementation cycle.
export function failureText(err) {
  return err.message;
}
```

- [ ] **Step 2: Testleri yaz**

`queen-editor/frontend/src/shared/failure_text.test.js`:

```js
import { describe, expect, it } from "vitest";

import { failureText } from "./failure_text.js";

describe("failureText", () => {
  it("puts the evidence under the sentence", () => {
    const err = new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et.");
    err.evidence = "GET /api/status\nZaman aşımı (10 sn)";

    // One string, two jobs: the first line is read on the panel, the rest is what the copy button
    // hands over. The panel splits them at this newline.
    expect(failureText(err)).toBe(
      "Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nGET /api/status\nZaman aşımı (10 sn)");
  });

  it("says just the sentence when there is no evidence", () => {
    // Not every failure comes through the fetch wrapper. An empty line under one of those would
    // read as proof that went missing.
    expect(failureText(new Error("Sıra kaydedilemedi."))).toBe("Sıra kaydedilemedi.");
  });
});
```

- [ ] **Step 3: Koştur**

Run: `npm test --prefix queen-editor/frontend -- failure_text`
Expected: 2 test, 1 düşüyor (`puts the evidence under the sentence`), 1 geçiyor.

---

### Task 2: Kanıtın doğuşu — `api.test.js`

**Files:**
- Modify: `queen-editor/frontend/src/shared/api.test.js`

- [ ] **Step 1: Fixture'ları genişlet**

Sahte cevaplar yalnız `json()` veriyor; ham metni saklamak `text()` gerektiriyor. Dosyanın
başındaki yardımcı ikisini de verir, ve bir de hata cevabı için eşi eklenir:

```js
function okResponse(body) {
  const text = JSON.stringify(body);
  return { ok: true, status: 200, statusText: "OK", text: async () => text, json: async () => body };
}

// A failed response the way a tunnel really answers: a body of bytes, which may or may not be
// JSON. json() throwing on a page of HTML is exactly what the real one does.
function errorResponse(status, statusText, text) {
  return { ok: false, status, statusText,
           text: async () => text, json: async () => JSON.parse(text) };
}
```

`throws the server's own text…` (bugün satır 21) ve `shows the status and its text…` (satır 32)
testlerinin satır içi sahte cevapları `errorResponse` ile değişir:

```js
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
      errorResponse(404, "NOT FOUND", JSON.stringify({ error: "Proje bulunamadı: düğün" }))));
```

```js
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
      errorResponse(502, "Bad Gateway", "<html><body>error code: 1033</body></html>")));
```

İkisi de yeşil kalır: `request()` hâlâ `json()` çağırıyor ve fixture onu vermeye devam ediyor.

- [ ] **Step 2: `createProject` import'a eklenir**

```js
import { createProject, getSettings, getStatus, listFrames, listProjects, saveOrder } from "./api.js";
```

- [ ] **Step 3: Üç yeni test ekle**

`describe("api.request")` bloğunun sonuna:

```js
  it("names the request that failed", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
      errorResponse(400, "BAD REQUEST", JSON.stringify({ error: "Bu ad zaten var." }))));

    const failure = await createProject("düğün").catch((err) => err);

    // Read from the request, never assumed: a hardcoded GET would name the wrong call for every
    // POST in this file, and naming the wrong request is worse than naming none.
    expect(failure.evidence.split("\n")[0]).toBe("POST /api/projects");
  });

  it("keeps the body a tunnel sent instead of JSON", async () => {
    const page = "<html><body>error code: 1033</body></html>";
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(errorResponse(502, "Bad Gateway", page)));

    const failure = await listProjects().catch((err) => err);

    // What used to disappear: the body was dropped the moment it would not parse, taking the one
    // line that says which tunnel refused and why.
    expect(failure.evidence).toContain(page);
  });

  it("keeps the status even when the body carried a sentence", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue(
      errorResponse(400, "BAD REQUEST", JSON.stringify({ error: "Bu ad zaten var." }))));

    const failure = await createProject("düğün").catch((err) => err);

    // A server sentence is an answer, not a diagnosis: the same words come back with a 400 and
    // with a 500, and only the code tells them apart.
    expect(failure.message).toBe("Bu ad zaten var.");
    expect(failure.evidence).toContain("400 BAD REQUEST");
  });
```

- [ ] **Step 4: İki mevcut testi değiştir**

`wraps a network refusal in a Turkish prefix and keeps the raw text under it` tümüyle şununla
değişir:

```js
  it("names the request that never answered", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    const failure = await listProjects().catch((err) => err);

    // The sentence is what is read, the proof is what is copied. The browser's own text living in
    // both would be one fact kept in two places.
    expect(failure.message).toBe("Sunucuya ulaşılamadı — bağlantıyı kontrol et.");
    expect(failure.evidence).toBe("GET /api/projects\nFailed to fetch");
  });
```

`aborts a request that goes 10 seconds without an answer` gövdesi şununla değişir (adı ve sahte
zamanlayıcısı kalır — sınadığı şey hâlâ kesme):

```js
    const pending = getStatus().catch((err) => err);
    await vi.advanceTimersByTimeAsync(10_000);
    const failure = await pending;

    expect(failure.message).toBe("Sunucuya ulaşılamadı — bağlantıyı kontrol et.");
    // AbortError's own text names our abort, not the server: it would be evidence of nothing.
    // What we can honestly say is which request we cut, and after how long.
    expect(failure.evidence).toBe("GET /api/status\nZaman aşımı (10 sn)");
```

- [ ] **Step 5: Koştur**

Run: `npm test --prefix queen-editor/frontend -- api`
Expected: 5 düşen (3 yeni + 2 değişen), geri kalanı yeşil.

---

### Task 3: Kanıtın taşınması ve kutuya düşmesi

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/useGeneration.test.jsx`
- Modify: `queen-editor/frontend/src/features/photo_generation/QueuePanel.test.jsx`

- [ ] **Step 1: `useGeneration.test.jsx`'e bir test ekle**

`shows the error when a poll fails…` testinin hemen ardına:

```js
  it("keeps the evidence of a failed poll", async () => {
    const dead = new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et.");
    dead.evidence = "GET /api/status\nZaman aşımı (10 sn)";
    getStatus.mockRejectedValue(dead);
    listFrames.mockRejectedValue(dead);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    // Storing the message alone threw the proof away at the last step of the road it travelled.
    expect(result.current.error).toContain("GET /api/status");
  });
```

- [ ] **Step 2: `QueuePanel.test.jsx`'e bir bekçi ekle**

Hata kartını çizen `describe` bloğunun sonuna:

```js
  it("hands the evidence to the copy button", () => {
    const evidence = [
      "GET /api/projects/d%C3%BC%C4%9F%C3%BCn/frames",
      "502 Bad Gateway",
      "<html><body>error code: 1033</body></html>",
    ].join("\n");

    renderPanel({ error: `Sunucuya ulaşılamadı — bağlantıyı kontrol et.\n${evidence}` });

    // Green today: describeError already splits at the first newline. It is written because
    // nothing else says the proof can reach the clipboard, and that split is now load-bearing.
    expect(document.querySelector("[data-raw]").textContent).toBe(evidence);
  });
```

- [ ] **Step 3: Bütün takımı koştur**

Run: `npm test --prefix queen-editor/frontend`
Expected: 7 düşen (1 failure_text + 5 api + 1 useGeneration). QueuePanel bekçisi geçiyor.

---

### Task 4: Kırmızı commit

- [ ] **Step 1: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): ask an error which request it came from

Red on purpose -- the implementation cycle turns these green.

The screen said a request went unanswered without saying which one, because
the wrapper throws a bare string and drops three things on the way: the method
and path are never written down, a body that will not parse becomes null and
takes the tunnel error page with it, and the status disappears whenever the
body carried a sentence of its own.

The tests name the contract: the message is one sentence, the proof rides
beside it, and every line of that proof is either what we did or what the
service said. Nothing is inferred.

Fixtures grow a text method next to json, since keeping a raw body means
reading one. The growth is backward compatible, so no existing test turns red
from it -- the five that do are the two whose contract moved and the three
that ask for evidence nobody produces yet.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** spec'in 9 testi → Task 1 (6, 7), Task 2 (1-5), Task 3 (8, 9). Fixture genişlemesi
→ Task 2 Step 1. İskelet → Task 1 Step 1.

**Tip tutarlılığı:** `err.evidence` bir string, satırları `\n` ile ayrılıyor; `failureText` onu
mesajın altına aynı ayraçla koyuyor; `describeError` ilk `\n`'den bölüyor. Üç yer aynı ayracı
kullanıyor ve testler üçünü de aynı örnekle sınıyor.

**Kontrol edilen tuzak:** `errorResponse`'un `json()`'ı JSON olmayan gövdede fırlatıyor — bu kasıtlı,
gerçek `Response.json()` de öyle yapıyor. Fixture'ı "hep JSON dönsün" diye yazmak, bu görevin
düzelttiği hatayı testin göremeyeceği hâle getirirdi.

**Kontrol edilen tuzak 2:** `await createProject(...).catch((err) => err)` — `rejects.toThrow`
mesajı sınar ama hatanın **kendisini** vermez, ve sınanan şey mesajın yanındaki alan. Hatayı
yakalayıp nesne olarak okumak tek yol.

**Kontrol edilen kapsam:** `NewProjectModal.test.jsx` ve proje listesi testleri değişmiyor —
`err.message` sözleşmesi onlar için aynı kaldı, ve zaten tek satırlık sunucu cümlesi okuyorlar.
