# Madde 157 — test turu planı

**Spec:** [m157 silme testler design](../specs/2026-09-03-queenagent-m157-silme-testler-design.md)

Bu tur yalnız test yazar.

## 1. `test_tools.py`'nin fikstürü okunur

`STRUCTURE` sabiti neyi taşıyor: kaç kare, hangi karakter, hangi kıyafet, hangi mekân. Silme
testleri **kullanılan** ve **kullanılmayan** ad ayrımına dayanıyor, yani ikisinin de fikstürde
bulunması gerekiyor — yoksa test kendi verisini kurar.

## 2. Harita silme testleri yazılır

Spec'in 1–11'i. Üç kaynakta da aynı davranışı çiviyen testler `pytest.mark.parametrize` ile tek
gövdede toplanır *(araç adı, harita adı, silinecek ad)*; kaynağa özgü olan tek şey ret cümlesindeki
fiil, ve o kendi testinde durur.

## 3. `remove_frame` testleri yazılır

Spec'in 12–19'u. `0` ve negatif ayrı bir test: Python'da `frames[-1]` sessizce sondakini siler, ve
bir testin var olma sebebi tam olarak böyle bir sessizlik.

## 4. Kayıt testleri

- Roster testine dört ad eklenir *(13 → 17)*.
- `test_modes.py`'ye dördünün `edit`'te izinsiz koştuğu, `ask` ve `plan`'da sorduğu eklenir.
- `WRITES_FILES`'ta olmadıkları çivilenir.

## 5. Koşulur ve kırmızı görülür

CLAUDE.md'nin dört satırı, **sırayla**:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: `queen-agent` kırmızı *(yeni silme testleri + notebook'un bilinen iki kırmızısı)*, diğer
üç satır yeşil.

## 6. Kırmızı commit'lenir

`test(m157): …` — mesajda çift tırnak yok.
