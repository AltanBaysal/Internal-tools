# Madde 471 · Başlıkta sürüm V10 yazar — tasarım

**Tarih:** 20 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
471 · v10-5 · **Dal:** `feat/queen-editor-v10` · **Önceki:** v9'da
[428](2026-10-06-queen-editor-m428-surum-v9-uygulama-design.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Ne ve neden

Kullanıcı, 20 Ekim — "v10 btin ceditorde sürüm bump etmeyide yaz sonra unutyorsun", "yad başta bump
et ui da". Koşunun ilk işi: ekrandaki sürüm `V9`'dan `V10`'a.

## Değişen

**Tek satır:** `queen-editor/frontend/src/shared/version.js`'te `VERSION = "V9"` → `"V10"`. Sayıyı
tutan tek yer o; dört ekran — proje listesi, proje ekranı, karenin sayfası, export ekranı — onu
okuyor. `dist/` ve `node_modules/` dışında `queen-editor/` altında `V9` yazan başka yer yok (tarandı).

Dosyanın yorumu değişmiyor: sayının neden elle yazıldığını ve ekranların onu çizdiğini söylüyor,
ikisi de bugün doğru.

## Testler

**Hiçbir test değişmiyor, yenisi de eklenmiyor.** `version.test.js` sayının biçimini (`/^V\d+$/`)
tutuyor, `V10` de ona uyuyor; dört ekranın testi başlığın `Queen Editor ${VERSION}` olduğunu tutuyor.
Değeri bir teste yazmak tek kararı iki yere koyardı *(248)*. Bu yüzden kırmızıya düşen bir test yok:
değişiklik bir karar, davranış değil.

## `dist/`

Defter depoyu klonluyor ve build etmiyor (FOUNDATION'ın 3. kararı); `dist/` aynı değişiklikle yeniden
build'lenir. Colab'da `V10`, o commit itildikten sonra görünür.

## Maliyet ve risk

Çalışma anında hiçbir şey değişmiyor: sabit bir dize, disk ya da ağ yok.

## Bitti sayılır

Projeler sayfasının ve proje ekranının başlığında "Queen Editor V10" yazıyor; queen-editor'ün iki
takımı yeşil.
