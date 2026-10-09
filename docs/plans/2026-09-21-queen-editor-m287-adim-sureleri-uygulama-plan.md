# Madde 287 · Ekran her adımı adıyla ve süresiyle söyleyecek — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-21-queen-editor-m287-adim-sureleri-uygulama-design.md) ·
**Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md)

## Adımlar

**1 · `export_runner.py`.** `RESTING` üçlüsü, `clock` enjeksiyonu, `IDLE`'a boş `steps` demeti,
`report`'un durum değişiminde adımı kapatması, `start`'ın meşgulluğu dinlenmemek diye sorması.

**2 · `run_export.py`.** Fotoğraf döngüsünden önce `state="photos"`; birleşik modda Drive'a
kopyalamadan önce `state="saving"`.

**3 · `ExportScreen.jsx`.** `RESTING`, durum → cümle, durum → ad, saniye biçimi, ve düğmelerin
altındaki adım listesi.

**4 · `npm run build --prefix queen-editor/frontend`.** `dist/` aynı commit'e girecek.

**5 · Takım:** dört satır paralel. Sekiz kırmızının yeşile dönmesi beklenir.

**6 · Commit** (yeşil), kaynak ve `dist` birlikte.
