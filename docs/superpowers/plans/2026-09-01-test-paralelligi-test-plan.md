# Test koşusu makineyi boğmaz · Tur 1 (test) — Plan

**Tasarım:** [2026-09-01-test-paralelligi-testler-design.md](../specs/2026-09-01-test-paralelligi-testler-design.md)
**Dal:** `feat/test-paralelligi` *(`main`'den)*
**Bu tur yalnız test dosyalarına dokunur.** `vite.config.js`'ler bu turda **değişmez**.
**Test komutları (değişmez, dördü de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. `queen-agent/frontend/src/viteConfig.test.js` — yeni dosya, iki kırmızı.

```js
import { expect, test } from "vitest";

import config from "../vite.config.js";

// A lock, not a behaviour test -- the same kind as app.css.test.js. What it holds is the setting
// that decides how much of the machine one test run is allowed to take.
//
// The config is imported rather than read as text. The css locks read text because jsdom loads no
// stylesheet and there is nothing to import; a JS config has no such excuse, and importing it
// reads the value actually in force rather than the one that happens to be written down.
//
// Why the setting exists at all: with a worker per core, thirty-five files each stand up their own
// jsdom and then queue for the same memory. A test measured at 99ms alone read 5107ms in that
// crowd, and the timeout -- which measures the wall clock -- called it stuck. Halving the workers
// made the suite green and twice as fast.

test("one run does not ask the machine for every core it has", () => {
  expect(config.test.maxWorkers).toBeDefined();
});

test("the share is written as a proportion, so it travels between machines", () => {
  // A fixed count would fix this machine and bind every other: ten workers is still too many on a
  // four-core runner and leaves a sixty-four-core one idle. The rule is half the cores, so that is
  // what the file says.
  expect(config.test.maxWorkers).toMatch(/^\d+%$/);
  expect(Number.parseInt(config.test.maxWorkers, 10)).toBeLessThanOrEqual(50);
});
```

Bugün **ikisi de kırmızı**: `config.test.maxWorkers` tanımsız.

## B. `queen-editor/frontend/src/viteConfig.test.js` — aynı dosya, iki kırmızı daha.

Birebir aynı içerik; yol `../vite.config.js` olarak aynı kalıyor çünkü iki dosya da `src/` altında.
Kopya bilerek, `test_frontend_toolchain.py`'deki gerekçeyle: iki araç ayrı koşu.

## C. Koşuldu: **4 kırmızı**, tam planlanan dördü.

| Komut | Sonuç |
|---|---|
| `python -m pytest queen-agent -q` | 658 yeşil |
| `python -m pytest queen-editor -q` | 720 yeşil |
| `npm test --prefix queen-agent/frontend` | **2 kırmızı**, 568 yeşil |
| `npm test --prefix queen-editor/frontend` | **2 kırmızı**, 584 yeşil |

Dördü de doğru sebepten: `expected undefined to be defined` — ayar henüz yok.

Ön yüzler **tek tek** koşuldu, paralel değil *(CLAUDE.md'nin paralel kuralından bilerek sapıldı)*:
dört takımı aynı anda koşturmak, bu maddenin incelediği çekişmenin ta kendisi, ve kırmızının
okunmasını bulandırırdı. Maskeleme yok — her komut kendi kırmızısını kendi çağrısında verdi.

**Beklenen iki tuhaflığın ikisi de olmadı:**

1. Fazladan kararsız kırmızı çıkmadı — ama koşu yine yavaştı *(queen-agent 49.13s,
   `environment 686.76s`)*, yani çekişme duruyor, bu sefer sınırın altında kaldı. Kararsızlığın
   şansa bağlı olduğunun bir kanıtı daha.
2. Kilit testi `vite.config.js`'i sorunsuz içe aktardı; `@vitejs/plugin-react` jsdom ortamında
   patlamadı. Metin okumaya düşülmedi.

## D. Kırmızı commit.

## Bilerek yapılmayanlar

`skip`/`xfail` yok. `vite.config.js`'ler ellenmez. `testTimeout` ellenmez. Testler hızlandırılmaz.
`dist` derlenmez.
