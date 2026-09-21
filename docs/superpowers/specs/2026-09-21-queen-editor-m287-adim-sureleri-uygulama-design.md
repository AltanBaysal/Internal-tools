# Madde 287 · Ekran her adımı adıyla ve süresiyle söyleyecek — uygulama turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m287-adim-sureleri-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey.

## Çivilenmiş olguların istediği kod

### `export_runner.py` — saati tutan yer

- **`clock` enjekte ediliyor**, varsayılanı `time.monotonic`.
- **`IDLE`'a `steps` giriyor**, boş bir **demet** olarak. Demet, çünkü `state()` sığ kopya veriyor:
  paylaşılan bir liste okuyanın elinde değişebilirdi, demet değişemez.
- **`report` durum değişimini görüyor.** Yeni durum eskisinden farklıysa: yeni durum `idle` ise
  `steps` sıfırlanıyor, değilse **biten adım** — dinlenme durumlarından biri değilse — kendi
  süresiyle `steps`'e ekleniyor. Her iki durumda da adımın başlangıcı yeniden işaretleniyor.
- **`start` sorusunu tersine çeviriyor:** meşgul = `idle`, `done`, `error` dışında bir şey.
  Adım eklendikçe büyümesi gereken bir liste yerine, hiç büyümeyen tamamlayanı.

**Dinlenme durumları tek yerde:** `RESTING = ("idle", "done", "error")` — hem meşgul sorusunu hem
*"bu adım ölçülür mü"* sorusunu aynı üçlü cevaplıyor, ve ikisi zaten aynı soru.

### `run_export.py` — iki satır

- Fotoğraf döngüsünden önce: `runner.report(mode, state="photos")` — **iki modda da**.
- Birleşik modda `store.copy_export` çağrısından önce: `runner.report(mode, state="saving")`.

Başka hiçbir şey değişmiyor; ölçüm bu dosyanın işi değil.

### `ExportScreen.jsx` — cümleler ve biçim

- **`RUNNING` listesi `RESTING` listesine dönüyor**, arka uçtaki soruyla aynı biçimde: meşgul olmak
  dinlenmemek. Hem düğmenin kapalı olması hem yoklamanın sürmesi buna bakıyor.
- **Durum → cümle** tablosu: `photos` → *"Fotoğraflar ekleniyor…"*, `saving` → *"Drive'a
  kopyalanıyor…"*, `merging` → *"Disclaimer ekleniyor…"* *(255)*, gerisi sayaç.
- **Durum → ad** tablosu, biten adımların listesi için: *Videolar*, *Fotoğraflar*, *Disclaimer*,
  *Drive'a kopyalama*.
- **Saniye biçimi:** bir ondalık, ve ayıraç **virgül** — okuyan kişi Türkçe okuyor.
- **Liste nerede duruyor:** düğmelerin hemen altında, `steps` boş olmayan her mod için. Koşu
  sürerken biten adımlar birikiyor, koşu bitince aynı liste yerinde kalıyor — tek blok, iki
  durum.

**Ekran hiçbir süre hesaplamıyor** *(FOUNDATION 4)*: saniyeyi arka uç veriyor, ekran yalnız
biçimlendiriyor ve adlandırıyor.

### `dist/`

Ön yüz kaynağı değiştiği için `npm run build` koşuyor ve `dist/` **aynı commit'e** giriyor
*(FOUNDATION 3)*. Defter build etmiyor.

## Değişmeyen

- **255 ve 261.** `merging` yine *"Disclaimer ekleniyor…"*, ve tekli export'ta o cümle hiç
  çıkmıyor.
- **Yüzde yok, ffmpeg çıktısı ayrıştırılmıyor.** Ölçüm adımların etrafındaki saat.
- **`written` / `total` sayacı.** Videoların adımı hâlâ onu gösteriyor.
- **İki modun yan yana koşabilmesi** *(93)*: meşgulluk mod başına sorulıyor.

## Bunun getirdiği

**Kullanıcı koşu bittiğinde hangi adımın pahalı olduğunu görüyor** — ve **281 o sayıyı bekliyordu.**
Bu madde onu kronometre tutmadan veriyor.

**Bedeli, açıkça:** durum başına bir saat okuması ve durum sözlüğünde bir alan. Ölçüm ffmpeg'i
beklemenin biçimine dokunmuyor.

## Bu turda değişen

- `features/photo_generation/export_runner.py`: saat, `steps`, meşgulluk sorusu.
- `domain/usecases/run_export.py`: iki `report` satırı.
- `frontend/src/features/photo_generation/ExportScreen.jsx`: cümleler, adlar, adım listesi.
- `frontend/dist/`: yeniden build.
