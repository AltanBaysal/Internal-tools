# Madde 318 — Havuz ortada, kartların yerinde açılıyor, uygulama turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — takım yeşile döner.

**Testler:** [m318 test turu](2026-09-24-queen-editor-m318-havuz-ortada-testler-design.md),
`d8a1190a`.

## Değişen

**`ProjectScreen.jsx`** — `poolOpen` ve sol sütun *(panel ya da şerit)* gidiyor; yerine
`poolShown` *(başta `false`)*. Ortadaki kaydırma kutusunda havuz görünürken `ReferencePanel`
çiziliyor; `Gallery` bir kabın içinde, havuz görünürken `hidden` — sökülmüyor, çünkü seçimi
kendisinde ve sökülse kaybolurdu. `SidePanel`'e `poolShown` ve `onShowPool={setPoolShown}`.

**`SidePanel.jsx`** — ikisini `LayerPanel`'e geçiriyor, ve `LayerPanel`'e `key={open}`: video ve ses
aynı yerde çizildiği için bugün tek bir bileşen olarak yaşıyorlardı — sekme, kutular ve havuz bir
panelden ötekine taşınıyordu. `onShowPool`'un varsayılanı boş bir fonksiyon: sütun tek başına
çizildiğinde *(kendi testlerinde)* gösterecek bir ortası yok.

**`LayerPanel.jsx`** — sekme `onShowPool(sekme === Referanstan)`; `Referanslar` bloğunda tek düğme,
`poolShown`'a göre `Referansları kapat` / `Referansları aç`, `onShowPool(!poolShown)`; video paneli
sökülürken `onShowPool(false)` — havuz o panelin sekmesine ait.

**`ReferencePanel.jsx`** — sütunun kendi başlığı ve `×`'i gidiyor *(kapatmanın tek yeri düğme)*,
`onClose` prop'u da; 260 px'lik genişlik, kenar çizgisi ve kendi kaydırması gidiyor — artık ortanın
kutusunda, tasarımın `.rv` boşluğuyla *(24px 32px 48px)*. Sıraların görünüşü 319'un.

## Dist

`npm run build --prefix queen-editor/frontend`; `dist/` kodla aynı commit'te.

## Bitti sayılır

Dört test satırı yeşil; kod, dist, spec ve plan tek commit.
