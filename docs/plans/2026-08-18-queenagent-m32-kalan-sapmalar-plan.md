# Madde 32 — Kalan sapmalar · Uygulama Planı

**Tasarım belgesi:** [2026-08-18-queenagent-m32-kalan-sapmalar-design.md](../specs/2026-08-18-queenagent-m32-kalan-sapmalar-design.md)
**Test komutu (değişmez):** `python -m pytest queenagent -q; npm test --prefix queenagent/frontend`

Yalnız ön uç: **bir tur**, önce testler (kırmızı), sonra uygulama.

---

## Adım 1 — Testler (kırmızı commit)

- `useList.test.jsx` — başarısızlıkta `error` sunucunun cümlesini taşır; `loading` biter; **eldeki
  liste silinmez**; yeni denemede hata temizlenir.
- `useFiles.test.jsx` — çekme hatası dışa verilir ve silme reddi ondan **ayrı** durur.
- `FileRail.test.jsx` — hata satırı çıkar, boş cümle çıkmaz; sınıf `.list-error` *(eski
  `.file-list__error`'ı sorgulayan test taşınır)*.
- `ProjectScreen.test.jsx` — dosya sütunu ve **sohbet sütunu** hata satırını gösterir; başarılı ve
  boş yüklemede cümle döner; yükleme sürerken ikisi de yok.
- `useFile.test.jsx` — proje değişince açık dosya **bırakılır** (dönünce kapalı); başka projenin
  dosyasını açıp o projeye gitmek **açık** bulur.
- `App.test.jsx` — hata iki ekrana da iletiliyor.
- `workspace.css.test.js` — `.list-error` mono, 11px, yıkıcı ton; `.file-list__error` **yok**.

---

## Adım 2 — Uygulama

`useList.js` · `useFiles.js` · `useChatLists.js` · `FileRail.jsx` · `ProjectScreen.jsx` ·
`App.jsx` · `useFile.js` · `workspace.css`.

---

## Adım 3 — Kayıt (sapma 85 ve 79)

Farklar belgesine iki tarihli not: 85 **eskidi** (Faz 7 `.json`/`.py` üretiyor), 79 **kapandı**
(Madde 20-22). Yol haritasının Madde 32 metni de buna göre düzeltilir.

---

## Kapanış denetimi

- `grep file-list__error` boş.
- `useList`'in `catch`'i listeyi boşaltmıyor.
- Arka uçta değişiklik yok.

## Risk

Yok denecek kadar az.
