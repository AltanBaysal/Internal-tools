# Madde 148 · Tur 2 (uygulama) — Uygulama Planı

**Goal:** `12ff460`'ın 3 kırmızısını yeşile çevirmek, tek dosyaya dokunarak.

**Spec:** [Tur 2 tasarımı](../specs/2026-09-02-queenagent-m148-arac-cagrisi-uygulama-design.md)

## Global Constraints

- Yalnız `queen-agent/backend/services/xai/client.py`. Başka bir dosya değişirse düzeltme yanlış
  katmandadır.
- Kırmızı commit'in testleri değişmez.
- Defterin `BRANCH` kırmızısı bu turun işi değil ve staged edilmez.

### Task 1: `_spoken`'ı ikiye ayır

- [ ] `_said(frame)` — yalnız `delta.content`, `{"text": ...}` ya da `None`.
- [ ] `_fragments(frame)` — yalnız `delta.tool_calls`, liste ya da `None`.
- [ ] `_spoken` kalkar.

### Task 2: `_Calls` toplayıcısı

- [ ] `add(pieces)`: her parça için `index` *(yoksa `0`)*; yeni indeks sıraya eklenir.
      `function.arguments` **eklenir**, diğer her alan **yazılır**. `index` kayda girmez.
- [ ] `whole()`: ilk görülme sırasına göre liste.

### Task 3: Akış döngüsü

- [ ] `_DONE`'da `return` yerine `break` — sondaki `yield`'in koşabilmesi için.
- [ ] Sıra kare içinde: önce `_said`, sonra parçalar toplanır, sonra `_spent`. Bugünkü
      "önce kelimeler, sonra sayılar" kuralı korunur.
- [ ] Döngüden sonra, **yalnız doluysa**, `{"tool_calls": whole}`.

### Task 4: Doğrulama

- [ ] `python -m pytest queen-agent -q` → yalnız defterin 2 kırmızısı kalmalı
- [ ] `npm test --prefix queen-agent/frontend`
- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend`
- [ ] Commit: yalnız `client.py` + belgeler.
