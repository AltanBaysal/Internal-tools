# Madde 496 · Başlıkta sürüm V11 yazar — tasarım

**Tarih:** 27 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-6),
496 · v11-6 · **Dal:** `feat/queen-editor-v11` · **Önceki:** v10'da
[471](2026-10-20-queen-editor-m471-version-design.md) ·
**Kurallar:** [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Ne ve neden

Kullanıcı, 27 Ekim — "bir de her roadmapin başında şun uyapmanı istiyorum ui daki sürümü arttıralım
olur mu"; "ilk görev o olsun ynai". Koşunun ilk işi: ekrandaki sürüm `V10`'dan `V11`'e.

## Değişen

**Tek satır:** `queen-editor/frontend/src/shared/version.js`'te `VERSION = "V10"` → `"V11"`. Sayıyı
tutan tek yer o; dört ekran — proje listesi, proje ekranı, karenin sayfası, export ekranı — onu
okuyor. `dist/` ve `node_modules/` dışında `queen-editor/` altında `V10` geçen öteki yerler sürüm
değil (tarandı): bir checkpoint'in dosya adı (`novaOrangeXL_rexV10.safetensors`, backend testlerinde)
ve `glyphs.jsx`'teki bir SVG yolunun `V10` komutu (y=10'a dikey çizgi).

Dosyanın yorumu değişmiyor: sayının neden elle yazıldığını ve ekranların onu çizdiğini söylüyor,
ikisi de bugün doğru.

## Testler

**Hiçbir test değişmiyor, yenisi de eklenmiyor.** `version.test.js` sayının biçimini (`/^V\d+$/`)
tutuyor, `V11` de ona uyuyor; dört ekranın testi başlığın `Queen Editor ${VERSION}` olduğunu tutuyor.
Değeri bir teste yazmak tek kararı iki yere koyardı *(248)*. Bu yüzden kırmızıya düşen bir test yok:
değişiklik bir karar, davranış değil.

## `dist/`

Defter depoyu klonluyor ve build etmiyor (FOUNDATION'ın 3. kararı); `dist/` aynı değişiklikle yeniden
build'lenir. Colab'da `V11`, o commit itildikten sonra görünür.

## Maliyet ve risk

Çalışma anında hiçbir şey değişmiyor: sabit bir dize, disk ya da ağ yok.

## Bitti sayılır

Dört ekranın başlığında "Queen Editor V11" yazıyor; queen-editor'ün iki takımı yeşil.
