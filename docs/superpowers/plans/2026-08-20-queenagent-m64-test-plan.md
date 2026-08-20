# Madde 64 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-20-queenagent-m64-test-design.md](../specs/2026-08-20-queenagent-m64-test-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Değişiklik

`queen-agent/backend/tests/test_notebook.py` — iki test eklenir. Bugün `BRANCH`'in değerini tutan
hiçbir test yok; kontrol edildi.

| Test | Ne soruyor |
|---|---|
| `test_the_notebook_clones_main` | CONFIG hücresinde `BRANCH = "main"` |
| `test_the_notebook_ships_pointing_at_no_feature_branch` | Defterin hiçbir yerinde `feat/` geçmiyor |

Birincisi CONFIG hücresine, ikincisi kaynağın tamamına sorulur — çünkü unutulmuş bir dal adı en çok
bir yorumun içinde kalır, ve orada durduğu sürece bir sonraki okuyanı yanlış yere gönderir.

İkincisinin hata mesajı ne yapılacağını söyler: bir madde koşarken `BRANCH`'i kendi dalına çevirmek
doğaldır, commit'lemeden geri almak gerekir.

## Beklenen kırmızı

**İki test.** Birincisi değer `feat/queenagent-colab` olduğu için, ikincisi aynı dize dosyada
geçtiği için. İkisi de gerçekten kırmızı — hiçbiri kilit değil.

Arayüze dokunulmuyor: `npm test --prefix queen-agent/frontend` **474'te yeşil kalmalı.** Kalmazsa
kapsam sızmış demektir.

## Bu turda yapılmayan

Defter, yol haritası, hiçbir üretim kodu.
