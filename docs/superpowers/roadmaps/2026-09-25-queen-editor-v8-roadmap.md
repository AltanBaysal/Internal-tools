# Queen Editor — Yol Haritası v8

**Tarih:** 2026-09-25 · **Koşu dalı:** `feat/queen-editor-v8` · **Durum:** 0/3
**Öncesi:** [v7](2026-09-21-queen-editor-v7-roadmap.md) — 41/41 kapandı ve `c061908b` ile main'e
birleşti.
**Kaynak:** v8-1 ve v8-2 kullanıcının 25 Eylül'deki sözlerinden doğdu. v8-3 28 Eylül'de
[QueenAgent v9](2026-09-25-queen-agent-v9-roadmap.md)'un v9-7'sinden ayrıldı, ve QueenAgent'ın
çıkardığı listeyi okur.

---

| # | İş | Bitti sayılır |
|---|---|---|
| v8-1 | `UNALIGNED` **Ses motorunun kurulum hücresi geri bildirim verecek.** *(Kullanıcı, 25 Eylül — MMAudio kütüphanesini kuran hücre için: "burda takıldı, output'ta bir şey de yok", "bu kadar kötü olmasın, feedback versin", "bir sonraki turda çözelim".)* | *Hizalanınca yazılır.* |
| v8-2 | `UNALIGNED` **Bir üretimin ne kadar sürdüğü gösterilecek.** *(Kullanıcı, 25 Eylül — "bir üretimin ne kadar sürdüğünü gösterecek miyiz? var mı öyle bir şey, yoksa ekleyelim roadmap'e".)* | *Hizalanınca yazılır.* |
| v8-3 | `UNALIGNED` **Kutu QueenAgent'ın yeni listesini okur: H3 prompt'u video katmanına, senaryo karta.** *(Kullanıcı, 28 Eylül — "queen editorun roadmpını güncelemen lazım değil mi bu çıtkıy kabul etmesi için", "kabulu queen editore yazalım çünkü çok detalı bir günceleme". QueenAgent v9'un v9-7'sinden ayrıldı.)* **v9-7'de kullanıcıyla konuşulanlar:** listede her kare üç alanlı bir kayıt — `scene`, `photo`, `video`; H3 prompt'u kartın video katmanına girer; senaryo kartta görünür, ve yeri ile görünüşü queen-editor'ün tasarımcısından gelir; H3 prompt'u gelmeyen kartın prompt'unu bugünkü gibi grok yazar; eski düz liste bugünkü gibi açılır. **v9-7'den önce biter:** bugünkü kutu yalnız string listesi okuyor *([prompt_list.py](../../../queen-editor/backend/features/photo_generation/domain/prompt_list.py))*, ve yeni listeye "Format hatası" der. | *Hizalanınca yazılır.* |
