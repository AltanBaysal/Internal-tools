# Madde 17 — Onay kutusu bileşeni · Uygulama Planı

**Tasarım belgesi:** [2026-08-17-queenagent-m17-onay-design.md](../specs/2026-08-17-queenagent-m17-onay-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

İki commit: **önce yalnız testler** (kırmızı gider), sonra bileşen. Arka uç değişmiyor.

---

## Adım 1 — Testler (kırmızı commit)

**Yeni `ConfirmDialog.test.jsx`**
- başlık, cümle ve iki düğme çizilir; onay düğmesinin adı çağırandan gelir.
- "Cancel" `onCancel`, onay `onConfirm` çağırır.
- karartıya tıklamak iptal; kartın içine tıklamak değil.
- açılınca odak "Cancel"da.
- bileşen `keydown` dinleyicisi kurmaz — klavye App'in tek dinleyicisinin işi.

**`workspace.css.test.js`** — onay düğmesi `--destructive` dolu, hover `--destructive-hover`;
karartı ekranı kaplar (`position: fixed`, `inset: 0`).

**Ölçülen kırmızı:** bileşen dosyası yok, `ConfirmDialog.test.jsx` hiç yüklenmiyor; artı 2 CSS testi.

---

## Adım 2 — Uygulama

1. `features/workspace/ConfirmDialog.jsx`.
2. `workspace.css` — `.dialog`, `.dialog__card`, `.dialog__title`, `.dialog__body`,
   `.dialog__actions`, `.dialog__confirm`.

### Kapanış denetimi

- `grep addEventListener` `ConfirmDialog.jsx`'te boş.
- Yeni keyframe eklenmedi.

---

## Risk

Kutu bu maddede hiçbir yerden açılmıyor; asıl sınama Madde 18 ve 19.
