# Madde 54 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-20-queenagent-m54-impl-design.md](../specs/2026-08-20-queenagent-m54-impl-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adımlar

1. **`queen-agent/.gitignore`** — son satır çevrilir:

   ```
   # The frontend is built on the machine that runs it -- unlike queen-editor, nothing here ships
   # pre-built.
   frontend/dist/
   ```

   yerine `!frontend/dist/`, ve yanına neden: defter klonluyor, hiç derlemiyor, o yüzden bundle
   kaynağıyla birlikte yolculuk ediyor. Eski yorum **silinir**, düzeltilmez — söylediği şey artık
   yanlış.

2. **`queen-agent/frontend/dist`** eklenir. Derleme Tur 1'de yapıldı; yeniden derlenmez, çünkü
   testlerin okuduğu sayfa ile commit'lenen sayfa aynı olmalı.

3. Takım koşulur, iki kırmızının yeşile döndüğü görülür.

## Beklenen yeşil

`test_the_built_frontend_is_in_the_repo` — `index.html` artık taşınıyor.
`test_the_page_asks_for_files_that_were_committed_with_it` — sayfanın istediği iki asset de taşınıyor.

Toplam **358** (bugünkü 356 + iki yeni).

## Kapanış denetimi

- Kök `.gitignore` diff'te **yok**.
- queen-editor'ün hiçbir dosyası diff'te yok.
- Diff'te üç yeni dosya var ve üçü de `queen-agent/frontend/dist` altında; başka hiçbir bundle
  sızmamış (`node_modules` ya da `.vite` gibi).
