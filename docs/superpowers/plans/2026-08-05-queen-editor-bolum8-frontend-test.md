# Bölüm 8 — Frontend Test Altyapısı Uygulama Planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Frontend'in karar taşıyan kodu (`api.js`, `useGeneration`, `useProjectSettings`, Bölüm 7'nin bağlantı düzeltmesi) `npm test` ile kanıtlanır hâle gelir; sonraki bölümler testle yazılabilir.

**Architecture:** vitest mevcut `vite.config.js`'in içine bir `test` bloğu olarak girer — ayrı derleyici zinciri yok. Ortam `jsdom`, hook ve bileşenler `@testing-library/react` ile koşar. Test dosyaları kaynağın yanında (`src/**/<ad>.test.js(x)`) durur ve hiçbir yerden import edilmedikleri için `dist/`'e girmez. Ağ `vi.stubGlobal("fetch", …)` ile, zaman `vi.useFakeTimers()` ile sahtelenir; hiçbir test gerçek saniye beklemez.

**Tech Stack:** vitest 2.x · jsdom · @testing-library/react 16 (+ @testing-library/dom peer) · React 18 · Vite 5.4.

**Spec:** [2026-08-05-queen-editor-bolum8-frontend-test-design.md](../specs/2026-08-05-queen-editor-bolum8-frontend-test-design.md)

## Global Constraints

- **Commit yok** — hiçbir görev commit atmaz; tek commit en sonda kullanıcı onayıyla (kullanıcı kuralı).
- **Üretim kodu değişmez.** Bu bölüm mevcut davranışı dondurur. Test yazarken gerçek bir hata bulunursa düzeltilmez: teste `it.fails` yazılmaz, bulgu plana not düşülür ve ilgili bölüme taşınır. Tek istisna testin kendisinin yanlış olması.
- **Test adları ve `describe` başlıkları Türkçe**; kod yorumları İngilizce (repo sözleşmesi).
- **Yeni bağımlılıklar yalnız `devDependencies`** — Colab `npm install` çalıştırmaz, sadece `dist/`'i servis eder.
- **`waitFor` ile sahte zamanlayıcı karıştırılmaz.** @testing-library/react'in `waitFor`'u yalnız Jest'in sahte zamanlayıcısını tanır; vitest'inkiyle sonsuza dek bekler. Zamanla ilgili her bekleyiş bu plandaki `settle()` yardımcısıyla yapılır (`act` + `vi.advanceTimersByTimeAsync`).
- **jest-dom yok, snapshot yok, coverage eşiği yok** (spec §Kapsam).
- Dosyalar CRLF satır sonlarıyla kalır (repo sözleşmesi).

---

### Task 1: Test koşucusu + `api.js` testleri

**Files:**
- Modify: `queen-editor/frontend/package.json` (devDependencies + scripts)
- Modify: `queen-editor/frontend/vite.config.js` (`test` bloğu)
- Create: `queen-editor/frontend/src/test-setup.js`
- Create: `queen-editor/frontend/src/shared/api.test.js`

**Interfaces:**
- Consumes: `shared/api.js`'in dışa açık fonksiyonları (`listProjects`, `getSettings`, `listPhotos`, `getStatus`, `createProject`) ve `TIMEOUT_MS = 10_000` davranışı.
- Produces: `npm test` / `npm run test:watch` betikleri; `src/test-setup.js` her testten sonra DOM'u ve global sahtelerini temizler — sonraki bütün test dosyaları buna güvenir.

- [ ] **Step 1: Bağımlılıkları kur**

Run (`queen-editor/frontend/` içinde):

```bash
npm install -D vitest jsdom @testing-library/react @testing-library/dom
```

Beklenen: `package.json`'ın `devDependencies`'ine dört paket eklenir, `package-lock.json` güncellenir.

- [ ] **Step 2: Betikleri ekle**

`package.json`'ın `scripts` bloğu şu hâle gelir (mevcut iki satır korunur):

```json
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "test": "vitest run",
    "test:watch": "vitest"
  },
```

- [ ] **Step 3: `vite.config.js`'e test bloğunu ekle**

Dosyanın tamamı şu hâle gelir:

```js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// base "/" -> assets load from an absolute path, which is what the nested routes need. Flask
// serves dist at the root and falls back to index.html for unknown paths, so a relative
// "./assets/..." would resolve against /projects/<name>/ on a reload, hit that fallback, and load
// index.html as the module script -- a blank page. Covered by test_static.py.
export default defineConfig({
  plugins: [react()],
  base: "/",
  build: { outDir: "dist" },
  // Vitest reuses this config, so tests get the same JSX transform and module resolution as the
  // build. Test files live next to their source and are never imported, so they stay out of dist/.
  test: {
    environment: "jsdom",
    setupFiles: "./src/test-setup.js",
  },
});
```

Not: `globals` açılmaz — her test dosyası `describe/it/expect/vi`'yi açıkça import eder, böylece dosya hangi yapılandırmayla koşarsa koşsun aynı anlama gelir.

- [ ] **Step 4: `src/test-setup.js`'i yaz**

```js
import { cleanup } from "@testing-library/react";
import { afterEach, vi } from "vitest";

// One test's leftovers must never decide another test's outcome: unmount what was rendered, drop
// the fake fetch, and hand the clock back. Without globals enabled, Testing Library's own auto
// cleanup does not run, so it is done here explicitly.
afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.useRealTimers();
});
```

- [ ] **Step 5: `src/shared/api.test.js`'i yaz**

```js
import { describe, expect, it, vi } from "vitest";

import { getSettings, getStatus, listPhotos, listProjects } from "./api.js";

function okResponse(body) {
  return { ok: true, status: 200, statusText: "OK", json: async () => body };
}

describe("api.request", () => {
  it("proje adını URL'de kodlar", async () => {
    const fetchMock = vi.fn().mockResolvedValue(okResponse({ photos: [] }));
    vi.stubGlobal("fetch", fetchMock);

    await listPhotos("düğün fotoğrafları");

    const url = fetchMock.mock.calls[0][0];
    expect(url).toBe(`/api/projects/${encodeURIComponent("düğün fotoğrafları")}/photos`);
    expect(url).not.toContain("düğün");
  });

  it("sunucunun reddettiği istekte sunucunun kendi metnini fırlatır", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 404,
      statusText: "NOT FOUND",
      json: async () => ({ error: "Proje bulunamadı: düğün" }),
    }));

    await expect(getSettings("düğün")).rejects.toThrow("Proje bulunamadı: düğün");
  });

  it("JSON olmayan hata gövdesinde kodu ve durum metnini gösterir", async () => {
    vi.stubGlobal("fetch", vi.fn().mockResolvedValue({
      ok: false,
      status: 502,
      statusText: "Bad Gateway",
      json: async () => { throw new SyntaxError("Unexpected token < in JSON"); },
    }));

    await expect(getSettings("düğün")).rejects.toThrow("502 Bad Gateway");
  });

  it("ağ reddini Türkçe önekle sarar ve ham metni altında tutar", async () => {
    vi.stubGlobal("fetch", vi.fn().mockRejectedValue(new TypeError("Failed to fetch")));

    await expect(listProjects()).rejects.toThrow(
      "Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nFailed to fetch",
    );
  });

  it("10 saniye cevapsız kalan isteği iptal eder", async () => {
    vi.useFakeTimers();
    // A dead tunnel answers nothing at all: this fetch settles only if the abort signal fires.
    vi.stubGlobal("fetch", vi.fn((path, options) => new Promise((_, reject) => {
      options.signal.addEventListener("abort", () => {
        const err = new Error("The operation was aborted.");
        err.name = "AbortError";
        reject(err);
      });
    })));

    const pending = getStatus();
    const assertion = expect(pending).rejects.toThrow(
      "Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nZaman aşımı (10 sn)",
    );
    await vi.advanceTimersByTimeAsync(10_000);
    await assertion;
  });

  it("cevap gelen isteği sonradan iptal etmez", async () => {
    vi.useFakeTimers();
    let signal;
    vi.stubGlobal("fetch", vi.fn((path, options) => {
      signal = options.signal;
      return Promise.resolve(okResponse({ status: "idle" }));
    }));

    await getStatus();
    await vi.advanceTimersByTimeAsync(30_000);

    expect(signal.aborted).toBe(false);
  });
});
```

- [ ] **Step 6: Testleri koştur**

Run: `npm test` (`queen-editor/frontend/` içinde)
Expected: 6 test PASS.

- [ ] **Step 7: Kasıtlı bozma turu (kırmızıyı gör)**

`api.js`'te `const TIMEOUT_MS = 10_000;` satırını geçici olarak `const TIMEOUT_MS = 10_000_000;` yap, `npm test` koştur.
Expected: **"10 saniye cevapsız kalan isteği iptal eder"** testi FAIL (zaman aşımı gelmediği için `pending` çözülmez → test zaman aşımına uğrar). Sonra satırı **geri al** ve `npm test`'in yeniden yeşil olduğunu doğrula.

### Task 2: `useGeneration` testleri

**Files:**
- Create: `queen-editor/frontend/src/features/photo_generation/useGeneration.test.jsx`

**Interfaces:**
- Consumes: `useGeneration(project)` → `{ job, photos, error, stopping, generate, stop }`; `POLL_MS = 2000`. `shared/api.js` modülü `vi.mock` ile tamamen sahtelenir.
- Produces: `settle(ms)` deseni — `act` + `vi.advanceTimersByTimeAsync`; Task 3 aynı deseni kendi dosyasında tekrarlar (ortak yardımcı dosya kurulmaz, spec §3 YAGNI kuralı).

- [ ] **Step 1: Dosyayı yaz**

```jsx
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { generateBatch, getStatus, listPhotos, stopGeneration } from "../../shared/api.js";
import { useGeneration } from "./useGeneration.js";

vi.mock("../../shared/api.js", () => ({
  generateBatch: vi.fn(),
  getStatus: vi.fn(),
  listPhotos: vi.fn(),
  stopGeneration: vi.fn(),
}));

// Testing Library's waitFor only understands Jest's fake clock, so with vitest's it would wait
// forever. Advancing the fake clock inside act() flushes both the timers and the promises they
// unblock, which is exactly what a poll tick is.
async function settle(ms = 0) {
  await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
}

const RUNNING = { status: "running", project: "düğün", done: 1, failed: 0, total: 4 };
const DONE = { status: "done", project: "düğün", done: 4, failed: 0, total: 4 };

beforeEach(() => {
  vi.clearAllMocks();
  vi.useFakeTimers();
});

describe("useGeneration", () => {
  it("açılışta fotoğrafları bilinmez sayar ve ilk poll'da hem durumu hem fotoğrafları ister", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listPhotos.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    expect(result.current.photos).toBeNull();

    await settle();

    expect(result.current.photos).toEqual([]);
    expect(getStatus).toHaveBeenCalledTimes(1);
    expect(listPhotos).toHaveBeenCalledWith("düğün");
  });

  it("üretim sürerken 2 saniyede bir sorar, bitince zinciri durdurur", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listPhotos.mockResolvedValue([]);

    renderHook(() => useGeneration("düğün"));
    await settle();
    expect(getStatus).toHaveBeenCalledTimes(1);

    await settle(2000);
    expect(getStatus).toHaveBeenCalledTimes(2);

    getStatus.mockResolvedValue(DONE);
    await settle(2000);
    expect(getStatus).toHaveBeenCalledTimes(3);

    await settle(10_000);
    expect(getStatus).toHaveBeenCalledTimes(3);
  });

  it("poll patlarsa hatayı gösterir, denemeyi sürdürür ve bağlantı dönünce hatayı siler", async () => {
    const dead = new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nZaman aşımı (10 sn)");
    getStatus.mockRejectedValue(dead);
    listPhotos.mockRejectedValue(dead);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();
    expect(result.current.error).toContain("Sunucuya ulaşılamadı");

    await settle(2000);
    expect(getStatus).toHaveBeenCalledTimes(2);

    getStatus.mockResolvedValue({ status: "idle" });
    listPhotos.mockResolvedValue([]);
    await settle(2000);
    expect(result.current.error).toBeNull();
  });

  it("üretim biterken fotoğrafları bir kez daha ister", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listPhotos.mockResolvedValue([]);

    renderHook(() => useGeneration("düğün"));
    await settle();
    const afterFirstPoll = listPhotos.mock.calls.length;

    getStatus.mockResolvedValue(DONE);
    await settle(2000);

    // The poll's own refresh plus one extra for the frame still landing on Drive.
    expect(listPhotos.mock.calls.length).toBe(afterFirstPoll + 2);
  });

  it("ekrandan çıkıldıktan sonra yeni poll kurmaz", async () => {
    getStatus.mockRejectedValue(new Error("kopuk"));
    listPhotos.mockRejectedValue(new Error("kopuk"));

    const { unmount } = renderHook(() => useGeneration("düğün"));
    await settle();
    const callsBefore = getStatus.mock.calls.length;

    unmount();
    await settle(10_000);

    expect(getStatus.mock.calls.length).toBe(callsBefore);
  });

  it("üretim başlayınca panel beklemeden üretim durumuna geçer", async () => {
    getStatus.mockResolvedValue({ status: "idle" });
    listPhotos.mockResolvedValue([]);
    generateBatch.mockResolvedValue({ started: true });

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    await act(async () => {
      await result.current.generate({ prompts: '["a"]', negative: "", variants: 4 });
    });

    expect(result.current.job).toEqual({
      status: "running", project: "düğün", done: 0, failed: 0, total: 0,
    });
  });

  it("durdura basıldığı an butonu pasifler, sunucu cevabını beklemez", async () => {
    getStatus.mockResolvedValue(RUNNING);
    listPhotos.mockResolvedValue([]);
    let resolveStop;
    stopGeneration.mockReturnValue(new Promise((resolve) => { resolveStop = resolve; }));

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    act(() => { result.current.stop(); });
    expect(result.current.stopping).toBe(true);

    await act(async () => { resolveStop({ ...RUNNING, stopping: true }); });
    expect(result.current.stopping).toBe(true);
  });

  it("sunucunun bildirdiği durduruluyor bilgisi de butonu pasif tutar", async () => {
    getStatus.mockResolvedValue({ ...RUNNING, stopping: true });
    listPhotos.mockResolvedValue([]);

    const { result } = renderHook(() => useGeneration("düğün"));
    await settle();

    expect(result.current.stopping).toBe(true);
  });
});
```

- [ ] **Step 2: Koştur**

Run: `npm test`
Expected: 6 + 8 = 14 test PASS.

- [ ] **Step 3: Kasıtlı bozma turu**

`useGeneration.js`'in `.catch` bloğundaki `if (!alive.current) return;` satırını geçici olarak sil, `npm test` koştur.
Expected: **"ekrandan çıkıldıktan sonra yeni poll kurmaz"** FAIL. Satırı geri al, testler yine yeşil.

### Task 3: `useProjectSettings` + `GeneratePanel` testleri

**Files:**
- Create: `queen-editor/frontend/src/features/projects/useProjectSettings.test.jsx`
- Create: `queen-editor/frontend/src/features/photo_generation/GeneratePanel.test.jsx`

**Interfaces:**
- Consumes: `useProjectSettings(project)` → `{ status, settings, error, save, reload }`; `GeneratePanel` prop'ları `{ job, error, busyElsewhere, settings, project, stopping, onGenerate, onStop }`.
- Produces: —

- [ ] **Step 1: `useProjectSettings.test.jsx`'i yaz**

```jsx
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getSettings } from "../../shared/api.js";
import { useProjectSettings } from "./useProjectSettings.js";

vi.mock("../../shared/api.js", () => ({
  getSettings: vi.fn(),
  saveSettings: vi.fn(),
}));

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

beforeEach(() => {
  vi.clearAllMocks();
});

describe("useProjectSettings", () => {
  it("ayarlar gelince hazır duruma geçer", async () => {
    getSettings.mockResolvedValue({ prompts: '["a"]', negative: "kötü", variants: 4 });

    const { result } = renderHook(() => useProjectSettings("düğün"));
    expect(result.current.status).toBe("loading");

    await settle();

    expect(result.current.status).toBe("ready");
    expect(result.current.settings.negative).toBe("kötü");
  });

  it("hata durumunda sunucunun metnini taşır", async () => {
    getSettings.mockRejectedValue(new Error("Proje bulunamadı: düğün"));

    const { result } = renderHook(() => useProjectSettings("düğün"));
    await settle();

    expect(result.current.status).toBe("error");
    expect(result.current.error).toBe("Proje bulunamadı: düğün");
  });

  it("proje hızlı değişirse eski projenin geç gelen cevabını yutar", async () => {
    let resolveFirst;
    getSettings
      .mockImplementationOnce(() => new Promise((resolve) => { resolveFirst = resolve; }))
      .mockImplementationOnce(() => Promise.resolve({ prompts: "İKİNCİ", negative: "", variants: 2 }));

    const { result, rerender } = renderHook(({ project }) => useProjectSettings(project), {
      initialProps: { project: "birinci" },
    });

    rerender({ project: "ikinci" });
    await settle();
    expect(result.current.settings.prompts).toBe("İKİNCİ");

    await act(async () => {
      resolveFirst({ prompts: "BİRİNCİ", negative: "", variants: 9 });
    });

    expect(result.current.settings.prompts).toBe("İKİNCİ");
  });
});
```

- [ ] **Step 2: `GeneratePanel.test.jsx`'i yaz**

```jsx
import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import GeneratePanel from "./GeneratePanel.jsx";

const SETTINGS = { prompts: '["ilk prompt"]', negative: "", variants: 4 };
const RUNNING = { status: "running", project: "düğün", done: 7, failed: 0, total: 48 };
const DEAD = "Sunucuya ulaşılamadı — bağlantıyı kontrol et.\nZaman aşımı (10 sn)";

function renderPanel(props) {
  return render(
    <GeneratePanel
      job={RUNNING}
      error={null}
      busyElsewhere={false}
      settings={SETTINGS}
      project="düğün"
      stopping={false}
      onGenerate={() => Promise.resolve()}
      onStop={() => {}}
      {...props}
    />,
  );
}

// The progress bar is dimmed by a wrapper, so "is it dimmed" is answered by walking up from the
// counter rather than by reaching for a class name that does not exist.
function isDimmed(element) {
  for (let node = element; node; node = node.parentElement) {
    if (node.style && node.style.opacity === "0.45") return true;
  }
  return false;
}

describe("GeneratePanel — üretim sürerken bağlantı", () => {
  it("bağlantı koptuğunda son bilinen ilerlemeyi söyler ve çubuğu soluklaştırır", () => {
    renderPanel({ error: DEAD });

    expect(screen.getByText("Sunucuya ulaşılamıyor — son bilinen: 7/48")).toBeTruthy();
    expect(isDimmed(screen.getByText("7 / 48"))).toBe(true);
  });

  it("bağlantı sağlamken ne uyarı yazar ne çubuğu soluklaştırır", () => {
    renderPanel();

    expect(screen.queryByText(/son bilinen/)).toBeNull();
    expect(isDimmed(screen.getByText("7 / 48"))).toBe(false);
  });
});
```

- [ ] **Step 3: Koştur**

Run: `npm test`
Expected: 14 + 3 + 2 = 19 test PASS.

- [ ] **Step 4: Kasıtlı bozma turu**

`GeneratePanel.jsx`'te `style={errorInfo ? { opacity: 0.45 } : undefined}` ifadesini geçici olarak `style={undefined}` yap, `npm test` koştur.
Expected: **"bağlantı koptuğunda … çubuğu soluklaştırır"** FAIL. Geri al, yeşile dön.

### Task 4: Kapanış — build, backend, dokümanlar

**Files:**
- Modify: `queen-editor/CODE-STANDARD.md` (§Tests)
- Modify: `queen-editor/frontend/dist/` (yalnız gerekiyorsa; beklenti: değişmez)

**Interfaces:**
- Consumes: Task 1-3'ün çıktısı.
- Produces: —

- [ ] **Step 1: Testlerin `dist/`'e sızmadığını doğrula**

Run: `npm run build` (`queen-editor/frontend/` içinde), ardından `git status --short`.
Expected: build temiz biter; `dist/` altında **değişiklik yok** (test dosyaları hiçbir yerden import edilmiyor, bu yüzden paketlenmiyor). `dist/` değiştiyse dur ve nedenini araştır.

- [ ] **Step 2: Backend'in etkilenmediğini doğrula**

Run: `pytest` (`queen-editor/` içinde)
Expected: 181 test PASS.

- [ ] **Step 3: `CODE-STANDARD.md` §Tests'i güncelle**

Mevcut:

```markdown
## Tests
Run `pytest` from `queen-editor/`. Domain and use cases test with fake ports — no ComfyUI, no Drive.
```

Yeni:

```markdown
## Tests
Backend: run `pytest` from `queen-editor/`. Domain and use cases test with fake ports — no ComfyUI,
no Drive.

Frontend: run `npm test` from `queen-editor/frontend/` (vitest + jsdom). Test files sit next to
their source as `<name>.test.js(x)`; they are never imported, so they stay out of `dist/`. Network
and clock are faked (`vi.stubGlobal("fetch", …)`, `vi.useFakeTimers()`) — no test waits a real
second, and none of them needs a browser, a tunnel or a GPU. Testing Library's `waitFor` does not
understand vitest's fake clock: advance it inside `act()` instead.
```

- [ ] **Step 4: Commit YOK — kullanıcı onayı bekle**

Değişen/eklenen dosyalar çalışma kopyasında bırakılır. Kullanıcı "commitle" deyince tek commit:
`test(queen-editor): Bölüm 8 — frontend test altyapısı (vitest + jsdom)`.

## Bulgu defteri

Test yazarken ortaya çıkan ama bu bölümde **düzeltilmeyen** gerçek davranış sapmaları buraya yazılır
(Global Constraints: bölüm mevcut davranışı dondurur). Boşsa öyle kalır.

- **Üretim kodunda sapma bulunmadı** — üç kasıtlı bozma turunun üçü de doğru testi düşürdü, mevcut
  davranış olduğu gibi donduruldu.
- **Plandan sapma (araç sürümü):** `npm install` vitest 4'ü getirdi; vitest 4 kendi rolldown tabanlı
  Vite'ını kullanıyor ve her koşuda "esbuild yerine oxc" uyarıları basıyor — yani testler build'den
  farklı bir dönüştürücüyle koşuyordu. `vitest@^3` sabitlendi: aynı `vite.config.js`, aynı esbuild
  zinciri, uyarısız çıktı.
- **Test hatası (plan yazımında yakalanmadı, koşarken yakalandı):** ilk "unmount sonrası poll
  kurulmaz" testi boşuna geçiyordu — effect'in temizliği zaten bekleyen zamanlayıcıyı siliyor, yani
  koruma kaldırılınca bile test yeşil kalıyordu. Gerçek risk **istek uçarken** ekrandan çıkmak;
  test o senaryoya çevrildi ve koruma kaldırıldığında 1 yerine 6 poll sayarak düştü.
