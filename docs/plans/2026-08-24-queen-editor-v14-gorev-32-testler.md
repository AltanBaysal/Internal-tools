# v14 Görev 32 — Elde cevap varken gösterge yanmaz: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Sekiz test yazmak; yedisi düşecek, biri tutucu olarak yeşil doğacak. Kod bu döngüde
değişmiyor.

**Architecture:** Üç hook, üç depo, tek kural. `useProjectSettings` proje anahtarlı bir depo alır ve
testleri taze proje adlarıyla temiz başlar; `useModels` ve `useProducers` makineye ait tek yuvalı
depo alır, dolayısıyla testleri her testte modülü sıfırlar.

**Tech Stack:** Vitest + jsdom + @testing-library/react (`renderHook`).

**Spec:** [Görev 32 test spec'i](../specs/2026-08-24-queen-editor-v14-gorev-32-testler-design.md)

## Global Constraints

- **Kod değişmiyor.** `useProjectSettings.js`, `useModels.js`, `useProducers.js` bu commit'te olduğu
  gibi kalır.
- **Kırmızı bırakılır.** `skip`/`xfail` yok.
- **Mevcut testlerin cümleleri değişmiyor** — yalnız iki dosyanın kurulumu temiz modül düzenine
  geçiyor.
- **`dist` bu commit'e girmez.**
- Dil: test adları ve yorumlar **İngilizce**; commit mesajı **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Test komutu (depo kökünden, `cd` yok): `npm test --prefix queen-editor/frontend`
- `vi.resetModules()` kullanılan dosyada **hem hook hem de sahte api aynı `beforeEach` içinde
  yeniden import edilir**, ve arkasından **`vi.clearAllMocks()` gelir**. `resetModules` bir
  `vi.mock` fabrikasını yeniden koşturmuyor: sahte her testte aynı nesne kalıyor ve çağrılarını
  yanına alıp taşıyor. Yanındaki hook gerçekten yeni; temizlenmesi gereken yalnız geçmişi.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `.../features/projects/useProjectSettings.test.jsx` | kaydın hatırlanması | dört test ekle |
| `.../features/photo_generation/useModels.test.jsx` | model listesinin hatırlanması | temiz modül düzeni + iki test |
| `.../features/producers/useProducers.test.jsx` | üretici satırlarının hatırlanması | temiz modül düzeni + iki test |

---

### Task 1: Kayıt bir ziyaret boyunca hatırlanır

**Files:**
- Modify: `queen-editor/frontend/src/features/projects/useProjectSettings.test.jsx`

**Interfaces:**
- Consumes: dosyanın mevcut `settle()` yardımcısı ve `getSettings` sahtesi.
- Produces: implementasyon döngüsünün uyacağı sözleşme — aynı projeye ikinci kez bakan bir mount
  `status: "ready"` ile ve hatırlanan `settings` ile başlar; arkada yine sorar; gelen yeni cevap
  yerini alır; düşen bir tazeleme hatırlanana dokunmaz.

- [ ] **Step 1: Dört testi dosyanın `describe` bloğunun sonuna ekle**

`swallows a late answer for the previous project after a quick switch` testinden sonra:

```jsx
  it("opens ready the second time the same project is looked at", async () => {
    getSettings.mockResolvedValue({ prompts: "İLK", negative: "", variants: 2 });

    const first = renderHook(() => useProjectSettings("hatirlanan"));
    await settle();
    first.unmount();

    // Opening a frame tears this hook down and building it again is the whole of coming back.
    // There is nothing to wait for: the answer is in hand.
    const { result } = renderHook(() => useProjectSettings("hatirlanan"));
    expect(result.current.status).toBe("ready");
    expect(result.current.settings.prompts).toBe("İLK");
  });

  it("still waits for a project nothing has answered for", async () => {
    getSettings.mockResolvedValue({ prompts: "İLK", negative: "", variants: 2 });

    const first = renderHook(() => useProjectSettings("dolduran"));
    await settle();
    first.unmount();

    // What is remembered is one project's own answer, never another's.
    const { result } = renderHook(() => useProjectSettings("bos"));
    expect(result.current.status).toBe("loading");
  });

  it("refreshes what it remembered, without a wait on screen", async () => {
    getSettings.mockResolvedValue({ prompts: "ESKİ", negative: "", variants: 2 });

    const first = renderHook(() => useProjectSettings("tazelenen"));
    await settle();
    first.unmount();

    getSettings.mockResolvedValue({ prompts: "YENİ", negative: "", variants: 2 });
    const { result } = renderHook(() => useProjectSettings("tazelenen"));
    // Remembering is not believing forever: the record is asked for again, and the screen simply
    // does not go blank while the answer is on its way.
    expect(result.current.settings.prompts).toBe("ESKİ");
    await settle();

    expect(result.current.settings.prompts).toBe("YENİ");
    expect(result.current.status).toBe("ready");
  });

  it("keeps what it remembered when the refresh cannot be read", async () => {
    getSettings.mockResolvedValue({ prompts: "DURAN", negative: "", variants: 2 });

    const first = renderHook(() => useProjectSettings("duran"));
    await settle();
    first.unmount();

    getSettings.mockRejectedValue(new Error("Sunucuya ulaşılamadı."));
    const { result } = renderHook(() => useProjectSettings("duran"));
    await settle();

    // A refresh that fell over costs the user nothing, and emptying the screen over it would be
    // the opposite of quiet. The dead tunnel is the status poll's to report, and it does.
    expect(result.current.status).toBe("ready");
    expect(result.current.settings.prompts).toBe("DURAN");
  });
```

- [ ] **Step 2: Dördünün de düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `useProjectSettings.test.jsx` **3 failed**, mevcut 3 testi yeşil.

Düşen üçü aynı sebeple düşer: bugün her mount `loading` ile başlıyor ve hiçbir şey hatırlanmıyor.

**`still waits for a project nothing has answered for` düşmez, ve düşmemeli.** Bugün de doğru,
çünkü hiçbir şey hatırlanmıyorken her mount zaten bekliyor. Yazılma sebebi başka: kaydı tek yuvalı
bir depoya koyan uygulama bu testi kırar, ve bir projenin cevabını başka bir projeye göstermeyi
engelleyen tek şey o.

---

### Task 2: Model listesi bir ziyaret boyunca hatırlanır

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/useModels.test.jsx`

**Interfaces:**
- Consumes: `listModels` sahtesi.
- Produces: sözleşme — ikinci mount hatırlanan listeyle başlar; düşen bir tazeleme onu boşaltmaz.
  Depo makineye ait, yani anahtarsız.

- [ ] **Step 1: Temiz modül düzenine geç**

Dosyanın başındaki import ve kurulum bloğunun bugünkü hâli:

```jsx
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { listModels } from "../../shared/api.js";
import { useModels } from "./useModels.js";

vi.mock("../../shared/api.js", () => ({
  listModels: vi.fn(),
}));

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

beforeEach(() => {
  vi.clearAllMocks();
});
```

Yerine:

```jsx
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../../shared/api.js", () => ({
  listModels: vi.fn(),
}));

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

// What the machine last answered is remembered for the length of a visit, and that memory lives in
// the module. So each test gets the module itself fresh -- otherwise one test's answer would be
// the next test's starting point. Both are imported from the same fresh registry: taking the hook
// from the new one and the fake from the old would leave them talking to two different mocks.
let listModels;
let useModels;

beforeEach(async () => {
  vi.resetModules();
  ({ listModels } = await import("../../shared/api.js"));
  ({ useModels } = await import("./useModels.js"));
});
```

Mevcut iki testin gövdesine **dokunulmuyor.**

- [ ] **Step 2: İki testi `describe` bloğunun sonuna ekle**

```jsx
  it("opens with the list it already learned", async () => {
    listModels.mockResolvedValue(["nova.safetensors"]);

    const first = renderHook(() => useModels());
    await settle();
    first.unmount();

    // Coming back from a frame builds this hook again. The box saying yükleniyor… over a list the
    // screen already had is the flicker this removes.
    const { result } = renderHook(() => useModels());
    expect(result.current.models).toEqual(["nova.safetensors"]);
  });

  it("keeps the learned list when the next read cannot be made", async () => {
    listModels.mockResolvedValue(["nova.safetensors"]);

    const first = renderHook(() => useModels());
    await settle();
    first.unmount();

    listModels.mockRejectedValue(new Error("Sunucuya ulaşılamadı."));
    const { result } = renderHook(() => useModels());
    await settle();

    // Emptying a box over a refresh that fell over is not quiet. With nothing remembered yet the
    // answer is still the empty list -- that is the test above this one.
    expect(result.current.models).toEqual(["nova.safetensors"]);
  });
```

- [ ] **Step 3: Yalnız yeni ikisinin düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `useModels.test.jsx` **2 failed**, mevcut 2 testi yeşil. Mevcut ikisi düşerse dur: temiz
modül düzeni onların anlamını değiştirmemeli.

---

### Task 3: Üretici satırları bir ziyaret boyunca hatırlanır

**Files:**
- Modify: `queen-editor/frontend/src/features/producers/useProducers.test.jsx`

**Interfaces:**
- Consumes: `listProducers` sahtesi, `THREE` sabiti.
- Produces: sözleşme — ikinci mount hatırlanan satırlarla başlar, ve hatırlanan şey ilk cevap değil
  `install()`'ın yazdığını da taşıyan o anki hâldir.

- [ ] **Step 1: Temiz modül düzenine geç**

Bugünkü hâli:

```jsx
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { listProducers } from "../../shared/api.js";
import { COLAB_INSTALL, useProducers } from "./useProducers.js";

vi.mock("../../shared/api.js", () => ({ listProducers: vi.fn() }));

const THREE = [
  { id: "photo", name: "Fotoğraf üreticisi", installed: true },
  { id: "video", name: "Video üreticisi", installed: false },
];

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

beforeEach(() => {
  vi.clearAllMocks();
  listProducers.mockResolvedValue(THREE);
});
```

Yerine:

```jsx
import { act, renderHook } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

vi.mock("../../shared/api.js", () => ({ listProducers: vi.fn() }));

const THREE = [
  { id: "photo", name: "Fotoğraf üreticisi", installed: true },
  { id: "video", name: "Video üreticisi", installed: false },
];

async function settle() {
  await act(async () => { await Promise.resolve(); });
}

// What the machine answered is remembered for the length of a visit, and that memory lives in the
// module -- so each test gets the module itself fresh. Both are imported from the same fresh
// registry: taking the hook from the new one and the fake from the old would leave them talking to
// two different mocks.
let listProducers;
let COLAB_INSTALL;
let useProducers;

beforeEach(async () => {
  vi.resetModules();
  ({ listProducers } = await import("../../shared/api.js"));
  ({ COLAB_INSTALL, useProducers } = await import("./useProducers.js"));
  listProducers.mockResolvedValue(THREE);
});
```

Mevcut üç testin gövdesine **dokunulmuyor.**

- [ ] **Step 2: İki testi `describe` bloğunun sonuna ekle**

```jsx
  it("opens with the rows it already read", async () => {
    const first = renderHook(() => useProducers());
    await settle();
    first.unmount();

    // The panel drew neither rows nor an error while this was null, and coming back from a frame
    // put it through that again for an answer that cannot have changed.
    const { result } = renderHook(() => useProducers());
    expect(result.current.producers).toEqual(THREE);
  });

  it("remembers the rows as they stand, not as they arrived", async () => {
    const first = renderHook(() => useProducers());
    await settle();
    act(() => { first.result.current.install("video"); });
    first.unmount();

    const { result } = renderHook(() => useProducers());
    // Kur writes its sentence onto a row, so the answer on screen is no longer the answer the
    // server gave. Remembering the first one would take that sentence away on the way back.
    expect(result.current.producers[1].note).toBe(COLAB_INSTALL);
  });
```

- [ ] **Step 3: Yalnız yeni ikisinin düştüğünü gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: `useProducers.test.jsx` **2 failed**, mevcut 3 testi yeşil.

---

### Task 4: Kırmızıyı doğrula ve commit'le

- [ ] **Step 1: Toplamı gör**

Run: `npm test --prefix queen-editor/frontend`

Expected: **7 failed** — üçü `useProjectSettings.test.jsx`, ikisi `useModels.test.jsx`, ikisi
`useProducers.test.jsx`. Sekizinci yeni test tutucudur ve yeşil doğar. Başka hiçbir dosya
düşmemeli; özellikle `App.test.jsx` ve `SidePanel.test.jsx` 31'den yeşil kalmalı, ve
`useProducers`'ın `asks the server nothing` testi de yeşil kalmalı — düşerse sahte temizlenmemiş
demektir.

- [ ] **Step 2: Yalnız test dosyalarının değiştiğini doğrula**

Run: `git status --short`

Expected: üç `.test.jsx` ve `docs/superpowers`. Hook dosyalarının kendileri ve `dist` bu listede
**olmamalı.**

- [ ] **Step 3: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): red for three answers a visit should only need once

THESE TESTS FAIL ON PURPOSE. The code that answers them is the next commit.

Item 31 moved the waiting off the screen and into the one column that asked for
it. The waiting is still there: coming back from a frame asks for the project
record, the model list and the producer rows all over again, and all three pass
through not-knowing on the way. A ring in the photo panel, yukleniyor in the
model box, and producer rows blinking out -- with a good answer already in hand.

The app has done this three times already: the frame list, the pictures that
have been on screen, and the gallery's scroll place are all kept for the length
of a visit. These three complete the set. Two of them belong to the machine and
carry no project key; the record belongs to a project and carries one.

A remembered answer is never emptied by a refresh that fell over. Losing a
refresh costs the user nothing, and blanking the screen over it would be the
opposite of quiet -- and a dead tunnel is the status poll's to report, which it
already does. With nothing remembered yet, a failed first read still answers
exactly as it does today.

Two of the test files now take a fresh module per test. The memory is real
module state, so one test's answer really would become the next one's starting
point. The existing tests keep their sentences; only their start is made honest.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** B1–B4 → Task 1. B5, B6 → Task 2. B7, B8 → Task 3. Spec'te olup planda karşılığı
olmayan madde yok.

**Ad tutarlılığı:** Üç hook da bugünkü dışa açık yüzünü koruyor — `{ status, settings, error, save,
reload }`, `{ models, error, reload }`, `{ producers, error, install }`. Testler yeni bir ad
istemiyor; istedikleri tek şey bu adların ne zaman ne taşıdığı.

**Yer tutucu yok:** Her adımda gerçek kod ve gerçek komut var.

**Bilerek dışarıda:**

- **`useProjectSettings` için temiz modül düzeni.** Deposu proje anahtarlı, ve dört testin dördü de
  kendine ait bir proje adı istiyor — `REMEMBERED`'ın testlerinin çözümü, ve gereksiz yere ikinci
  bir düzen getirmemek.
- **Hatırlanan bir kaydın hatası.** Tazeleme düştüğünde `error` alanının ne taşıdığı sınanmıyor:
  ekranda görünen `status` ve `settings`, ve madde ekranda ne olduğu hakkında. Hangi metnin
  saklandığına dair bir cümle yazmak, kararı verilmemiş bir şeyi sabitlemek olurdu.
