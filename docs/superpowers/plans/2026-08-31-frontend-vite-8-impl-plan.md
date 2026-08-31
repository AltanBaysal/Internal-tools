# Ön yüz vite 8 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-31-frontend-vite-8-uygulama-design.md](../specs/2026-08-31-frontend-vite-8-uygulama-design.md)
**Kırmızı commit:** `ea7c988`
**Bu tur test dosyalarına dokunmaz.** Altı bekçi yazıldığı gibi yeşile dönmeli; dönmüyorsa değişecek
olan `package.json`, test değil.
**Test komutları (değişmez, dördü de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. İki `package.json`'da üçer satır.

`queen-agent/frontend/package.json` ve `queen-editor/frontend/package.json`, `devDependencies`:

```
"@vitejs/plugin-react": "^4.3.1"  →  "^6.0.0"
"vite": "^5.4.0"                  →  "^8.0.0"
"vitest": "^3.2.7"                →  "^4.0.0"
```

`react`, `react-dom`, `jsdom`, `@testing-library/dom`, `@testing-library/react` ellenmiyor.

## B. `npm install`, iki ön yüzde de.

```
npm install --prefix queen-agent/frontend
npm install --prefix queen-editor/frontend
```

Ağaç baştan çözülür, `package-lock.json` yenilenir. queen-editor'e taban için kurulan vite 5'in
üstüne 8 iner.

## C. Dört test komutu.

Beklenen: **hepsi yeşil** — queen-agent 650, queen-editor 718, ön yüzler 568 ve 584.

Kırılırsa en olası iki yer, ve çareleri *(tasarımdan)*:

1. **`vite.config.js`'teki `test` bloğu vitest 4'le.** Çare tek satır, iki dosyada da:
   `import { defineConfig } from "vite"` → `from "vitest/config"`. Önden yapılmıyor.
2. **plugin-react 6'nın oxc tabanlı JSX dönüşümü.** 568 + 584 test bunu yakalar.

Başka bir şey kırılırsa tasarıma dönülür.

### Olan: ikisi de değil, üçüncü bir şey

Tahmin edilen iki yer de kırılmadı. `vite.config.js` iki araçta da hiç ellenmedi, JSX dönüşümü tek
test düşürmedi. Kırılan `App.test.jsx`'te tek testti:

> `expected "pushState" to not be called at all, but actually been called 30 times`

Otuz çağrının içinde `/p/pabc` vardı — **başka bir testin** proje kimliği. Kök neden: dosya iki ayrı
testte `vi.spyOn(window.history, "pushState")` çağırıyor *(satır 246 ve 510)* ve hiçbir yerde
casusu sökmüyor. Vitest 3'te ikinci çağrı taze bir sarmalayıcı veriyordu; vitest 4'te **aynı mock'u**
geri veriyor, yani ikinci test birincinin doğuşundan beri biriken her çağrıyı devralıyor — aradaki
testlerin kendi kurulum satırları dahil.

Yani bu vite 8'in getirdiği bir kusur değil, **vitest 3'ün örttüğü bir test hijyeni açığı**:
casuslar hiçbir zaman testler arasında sökülmüyormuş.

**Çare kökte, `queen-agent/frontend/src/test-setup.js`:** dosyanın zaten aynı işi yapan iki
kuralının yanına *(`cleanup`, `localStorage.clear`)* üçüncüsü — `afterEach(vi.restoreAllMocks)`.
Gerçek metodu geri koyuyor, ve bir sonraki `spyOn`'u yeni bir casus yapan şey bu.

**Bu bir sapma, ve kaydı burada.** Tasarım *"testler değişmez"* diyordu, ve `test-setup.js` test
altyapısı. Yapılmasının gerekçesi: hiçbir testin *iddiası* değişmiyor — her test zaten kendi
casusunun kendisine ait olduğunu varsayıyordu, ve düzeltme o varsayımı geri veriyor, gevşetmiyor.
Bir iddiayı yeşile boyamak için değil, iddianın ölçtüğü şeyi ölçmesi için.

queen-editor'ün `test-setup.js`'ine dokunulmadı: 584 testin hepsi ilk koşuda yeşildi, ve yeşil bir
takıma ihtiyaç duymadığı bir `afterEach` eklemek onu değiştirmek olurdu.

## D. `npm audit`, iki ön yüzde de.

```
npm audit --prefix queen-agent/frontend
npm audit --prefix queen-editor/frontend
```

Maddenin başladığı yer burasıydı: esbuild uyarısı gitmiş olmalı. Test değil, doğrulama — gerekçesi
tasarımda.

## E. `dist` iki araçta da derlenir.

```
npm run build --prefix queen-agent/frontend
npm run build --prefix queen-editor/frontend
```

Ve **kaynakla aynı commit'e** girer (CLAUDE.md). Vite 8 farklı dosya adları üretiyor;
`test_dist_is_committed.py` sayfanın istediği dosyaların commit'lendiğine baktığı için, derleyip
commit'lememek kırmızıya düşer. Derlemeden sonra `pytest queen-agent` bir kez daha koşulur.

## F. Koşuldu: **dördü de yeşil.**

| Komut | Sonuç |
|---|---|
| `python -m pytest queen-agent -q` | **650 yeşil** *(647 + 3 bekçi)* |
| `python -m pytest queen-editor -q` | **718 yeşil** *(715 + 3 bekçi)* |
| `npm test --prefix queen-agent/frontend` | **568 yeşil** — tabanın tamamı ayakta |
| `npm test --prefix queen-editor/frontend` | **584 yeşil** — tabanın tamamı ayakta |

`npm audit` iki ön yüzde de **`found 0 vulnerabilities`**. Maddenin başladığı yer kapandı.

Yan bulgu: ağaç küçüldü — her iki ön yüzde de 56 paket çıktı, 8 girdi. Rolldown, Rollup+esbuild
yığınının yerini alıyor. Derleme de hızlandı: 627ms ve 341ms.

## G. Gözle doğrulama — testlerin bittiği yerde.

- **queen-agent:** `python queen-agent/main.py`, `http://127.0.0.1:8100` açılır ve gezilir
- **queen-editor:** yerel koşusu yok; Colab'da **kullanıcı** doğrular

**Bu doğrulama gelmeden dal `main`'e alınmaz.** Bundler motoru değişti ve hiçbir test derlenmiş
paketi çalıştırmıyor.

## Bilerek yapılmayanlar

Test dosyaları ellenmez. React yükseltilmez. `npm audit fix` çağrılmaz — sürümler elle ve bilerek
yazılıyor. queen-editor'ün eksik `requests`'i bu turda düzeltilmez.
