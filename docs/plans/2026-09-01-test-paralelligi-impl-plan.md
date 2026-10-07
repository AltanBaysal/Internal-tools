# Test koşusu makineyi boğmaz · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-01-test-paralelligi-uygulama-design.md](../specs/2026-09-01-test-paralelligi-uygulama-design.md)
**Kırmızı commit:** `fa0de30`
**Bu tur test dosyalarına dokunmaz.**
**Test komutları (değişmez, dördü de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. `queen-agent/frontend/vite.config.js` — `test` bloğuna bir alan.

```js
  test: {
    environment: "jsdom",
    setupFiles: "./src/test-setup.js",
    // A worker carries a jsdom of its own, so a worker per core leaves thirty-five environments
    // queuing for one machine's memory. A test that reads 99ms alone read 5107ms in that crowd,
    // and the timeout measures the wall clock, so it called a finished test stuck. Measured on 1
    // September: every core 18-22s and red, two workers 20.6s and green, half 8.3s and green --
    // fewer workers is both steadier and faster. A proportion rather than a count, because a
    // number that fits this machine would bind every other one.
    maxWorkers: "50%",
  },
```

## B. `queen-editor/frontend/vite.config.js` — aynı alan, aynı yorum.

Yorumun son cümlesi bu tarafta bir şey daha söyler: burada kırmızı görülmedi, ama yapılandırma,
dosya sayısı ve makine aynı, ve iki araç sebepsiz farklı kural taşımaz.

## C. Koşuldu: **dördü de yeşil.**

| Komut | Sonuç |
|---|---|
| `python -m pytest queen-agent -q` | **658 yeşil** |
| `python -m pytest queen-editor -q` | **720 yeşil** |
| `npm test --prefix queen-agent/frontend` | **570 yeşil** *(568 + 2 kilit)* |
| `npm test --prefix queen-editor/frontend` | **586 yeşil** *(584 + 2 kilit)* |

## D. Tekrar koşuldu, ve maddenin asıl kanıtı burada.

queen-agent'ın ön yüzü arka arkaya üç kez:

| Koşu | Süre | Sonuç |
|---|---|---|
| 1 | 9.25s | 570 yeşil |
| 2 | 10.25s | 570 yeşil |
| 3 | 10.59s | 570 yeşil |

Üç yeşil, ve süreler birbirine yakın — kararsızlığın ikinci yüzü sürelerin savrulmasıydı
*(18s ile 49s arası)*, o da gitti.

**Karşılaştırma, aynı kod, aynı makine:**

| | Önce | Sonra |
|---|---|---|
| Sonuç | 6 koşunun 3'ü kırmızı | 3 koşunun 3'ü yeşil |
| Süre | 18–49s | 9–11s |
| `import` | 38–58s | 4.6–5.1s |

**Beklenmedik bir stres kanıtı:** üçüncü koşu, queen-editor'ün takımıyla **aynı anda** koştu — yani
düzeltmeden önce iki kırmızı üretmiş olan koşulda. Yine 570 yeşil. Ayar yalnız boş bir makinede
değil, yüklü bir makinede de tutuyor.

## E. Yeşil commit.

## Bilerek yapılmayanlar

`testTimeout` ellenmez. Test dosyaları ellenmez. `dist` derlenmez — ayar üretilen paketi değil,
yalnız koşuyu ilgilendiriyor. Oran ölçülmeden değiştirilmez.
