# Madde 427 — Bir satırı sürüklemek öteki satırların sırasını silmesin, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Adımlar `- [ ]` ile işaretlenir. Testler `8fcfb1e5`'te
> kırmızı; bu tur yalnız onların söylediği kodu yazar.

**Hedef:** Sürükleme sıra belgesini okusun ve yalnız gönderilen satırları değiştirsin; öteki satırlar
kayıtlı sıralarında kalsın.

**Yaklaşım:** Tek dosya, tek use case: `save_reference_order` belgeyi `orders.read` ile okur,
gönderilen satırları bugünkü süzgeçten geçirip üstüne yazar, ve bütün belgeyi yazar. Ekran, kapı,
`placed` ve sıra deposu değişmez.

**Araçlar:** Python, pytest.

**Spec:** [m427 uygulama turu](../specs/2026-10-06-queen-editor-m427-surukleme-sirasi-uygulama-design.md)

## Her yere geçerli kurallar

- Kod, docstring ve yorumlar **İngilizce**; yorum *neden*i ve yalnız bugün doğru olanı söyler.
- Testler yalnız CLAUDE.md'nin dört satırıyla, olduğu gibi, paralel koşulur; `skip` / `xfail` yok.
- Testlere dokunulmaz: bu turda kırmızı testler kodla yeşile döner.

**Arayüz:** `save_reference_order(store, pool, orders, project, order)` — imza ve dönüş aynı: havuzun
yuvalı satırları.

---

## Görev 1: `domain/usecases/save_reference_order.py`

**Dosya:** Değiştir:
`queen-editor/backend/features/photo_generation/domain/usecases/save_reference_order.py`

- [ ] **Adım 1: modülün belgesine madde 427'nin kuralı ve sebebi.**

```python
"""Save the order the user dragged the reference pool into. Returns the pool as it now stands.

The sequence is filtered against what the pool really holds before it is stored, the way the
gallery's own order is (save_order): the server writes only names it can see itself, so a stale tab
cannot leave ghosts in the file -- names that stand in no slot (madde 321).

Only the rows that were sent change, and every other row keeps the order it was saved in
(madde 427). The screen sends the dragged row alone: a file written from the body alone would lose
every other row, and the pool would then place those by name (references.placed).
"""
```

- [ ] **Adım 2: yazma, belgeyi okuyup yalnız gönderilen satırları değiştirir.**

```python
    known = {row["name"] for row in list_references(store, pool, orders, project)}
    order_now = orders.read(project)
    # dict.fromkeys keeps the first of any repeated name, and the order they came in.
    order_now.update({kind: [name for name in dict.fromkeys(names) if name in known]
                      for kind, names in order.items()})
    orders.write(project, order_now)
    return list_references(store, pool, orders, project)
```

## Görev 2: Koş, yeşili oku, commit'le

- [ ] **Adım 1: dört satır, paralel, olduğu gibi.**

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: dördü de yeşil; `queen-editor` pytest'inde test turunun iki kırmızısı yeşile döndü.

- [ ] **Adım 2: commit** — kod, spec ve plan.

```powershell
git add queen-editor/backend/features/photo_generation/domain/usecases/save_reference_order.py docs/superpowers/specs/2026-10-06-queen-editor-m427-surukleme-sirasi-uygulama-design.md docs/superpowers/plans/2026-10-06-queen-editor-m427-surukleme-sirasi-uygulama-plan.md
git commit -m @'
fix(queen-editor): 427 -- a drag in the reference pool changes only the row it sends and every other row keeps its saved order; before, the order file was rewritten from the sent rows alone, so dragging the videos dropped the pictures order and they fell back to name order

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
'@
```
