# Madde 48 — Seçim menüyü kapatır · Plan (iki tur)

**Tasarım belgesi:** [2026-08-19-queenagent-m48-menu-kapanmasi-design.md](../specs/2026-08-19-queenagent-m48-menu-kapanmasi-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Tur 1 — Testler (kırmızı commit)

`App.test.jsx`, dört test:

1. `picking a model closes the menu`
2. `pressing the model already in use closes the menu and asks the server nothing`
3. `picking a skill closes the menu`
4. `in a draft, picking a model closes the menu too`

Menünün kapalı olduğu, `MODEL` başlığının kaybolmasıyla görülür — menü açıkken çizilen tek şey o.

1, 3, 4 düşer; **2 geçer** — sebebi tasarım belgesinde: o satır App'in kapatmasını hiç
tetiklemediği için yarışa girmiyor.

## Tur 2 — Uygulama (yeşil commit)

`App.jsx`: `chooseModel` ve `chooseSkill`'den `setPicker(null)` silinir; taslak hâlindeki iki satır
içi karşılığı da. Yorumla söylenir: kapatmak `Menu`'nün işi, ve iki güncelleme aynı toplu işte
birbirini bozuyordu.

---

## Kapanış denetimi

- Escape sırası ve "bir menü diğerini kapatır" testleri hâlâ yeşil: `togglePicker` değişmedi.
