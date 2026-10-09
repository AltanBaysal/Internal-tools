# Madde 441 — Arşivde Undo yok, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** Archive projeyi soru sormadan, sunucuyu beklemeden Projects'ten çıkarır ve Archived'a
koyar; Undo satırı hiçbir yerde yok; odak yerine gelen satırın ⋯'sine, yoksa aramaya geçer.

**Yaklaşım:** Her görevde önce test, kırmızı görülür, sonra kod. Dosyalar Edit ve Write ile değişir.

**Spec:** [m441](../specs/2026-10-09-queen-agent-m441-arsiv-undo-yok-design.md)

## Her yere geçerli kurallar

- Kod, yorum, test adları ve ekrandaki her söz İngilizce.
- Yol haritasına ve queen-editor'e dokunulmaz. Arka uçta yalnız bir testin adı ve sözleri değişir.

---

## Görev 1: `ProjectRow.jsx` — Undo satırı gider, ⋯ kimliğini taşır

- [ ] `ProjectRow.test.jsx`: ⋯ `data-project` olarak projenin kimliğini taşır. Kırmızı.
- [ ] `ProjectRow.jsx`: `UndoRow` silinir; ⋯'ye `data-project`; üst yorum. Yeşil.

## Görev 2: `AllProjectsScreen.jsx` — satır hemen çıkar, odak geçer

- [ ] `AllProjectsScreen.test.jsx`: Undo testleri kalkar. Yerine: Archive soru sormaz; cevap
  gelmeden proje Projects'te yok, Archived'da var, sayılar değişmiş, `.all-projects__undo` yok; odak
  sonraki ⋯'de (Recent içinde, Pinned'dan Recent'e, aramanın bıraktıkları içinde) `preventScroll`'la,
  son ve tek satırda aramada, kaydırarak; son proje arşivlenince *"Every project is archived."*; ret projeyi geri getirir; arka arkaya
  iki Archive. Kırmızı.
- [ ] `AllProjectsScreen.jsx`: `undoing`, `openMenu`, `undo`, `switchTab` silinir; `leaving` (dizi),
  sunucunun listesinde onları arşivli çizen `listed`; `archive` odağı devreder, `leaving`'e ekler,
  cevabı bekler, çıkarır; aramaya ve sütuna ref. Yeşil.

## Görev 3: `App.test.jsx` — uçtan uca

- [ ] Undo'lu üç test yerine: Archive soru sormadan çıkarır, PATCH `{ archived: true }`, Archived'da
  görünür, Undo yok; reddedilen arşivde proje Projects'e döner ve sunucunun sözü görünür. Pinli projenin
  Unarchive'la Recent'e döndüğü test kalır, Unarchive'a arşivin yeniden okunan listesini bekleyip
  basar. Yeşil olmalı (Görev 2'den sonra).

## Görev 4: CSS

- [ ] `workspace.css.test.js`: Undo satırının testi çıkar; `app.css.test.js`: Undo'nun hover satırı
  çıkar. Yokluğunu bekleyen test yazılmaz.
- [ ] `workspace.css`: `.all-projects__undo` kuralları silinir.

## Görev 5: arka uç testinin adı

- [ ] `test_pin_archive.py`: `test_undo_brings_…` → `test_unarchive_brings_…`, yorum ve sözler
  Unarchive'ı söyler. Davranış aynı.

## Görev 6: derleme ve suite'ler

- [ ] `npm run build --prefix queen-agent/frontend`.
- [ ] Dört suite, sırayla: `python -m pytest queen-agent -q`, `npm test --prefix queen-agent/frontend`,
  `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
