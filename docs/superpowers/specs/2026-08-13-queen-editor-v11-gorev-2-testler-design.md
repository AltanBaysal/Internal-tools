# v11 Görev 2 — seçili kare sayısı: TEST döngüsü (tasarım)

**Tarih:** 2026-08-13 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v11](../plans/2026-08-13-queen-editor-v11-roadmap.md) · **Döngü:** 1/2 (testler)

Bu spec **yalnız testleri** tanımlıyor. Kod bu döngüde değişmiyor; sonunda takım kırmızı olacak.

## Hangi davranış sınanıyor

Galeride kare seçiliyor, video panelindeki "Seçili kareler" sayısı sıfırda kalıyor ve satır tıklanmaz
duruyor. Sebep bulundu: galeri seçimi **karenin kimliğini** tutuyor
([Gallery.jsx:331](../../../queen-editor/frontend/src/features/photo_generation/Gallery.jsx)),
panel ise **dosya adıyla** karşılaştırıyor
([LayerPanel.jsx:101](../../../queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx)).
İkisi hiçbir zaman eşleşmiyor.

Sınanacak davranış: **panel seçimi kimlikle eşler, kuyruğa dosya adı gönderir.** İki ayrı şey, ve
ikisi de yazılı olmalı — biri düzeltilip öteki bozulabilir.

## Neden mevcut testler bunu kaçırdı

`LayerPanel.test.jsx` panele seçimi **dosya adı olarak** veriyor (`selected: ["0_a.png"]`). Yani
testler, kodun yanlış varsayımını doğru sanıp çivilemiş: panel dosya adı bekliyor, test dosya adı
veriyor, ikisi anlaşıyor ve gerçek ekranda hiçbir şey çalışmıyor. Test ile kod aynı nefeste
yazıldığında olan tam olarak bu.

Bu yüzden bu döngü **üç mevcut testi de düzeltiyor.** Onlar bugünkü kodla kırmızıya dönecek — ve
dönmeleri gerekiyor. Implementasyon döngüsünde düzeltilmeleri, düzeltmenin kanıtı olurdu; şimdi
düzeltilmeleri, sözleşmenin ne olduğunun ilanı.

## Test zemini

Roadmap "ekranı gerçek gibi kuran zemin" diyordu; bakıldığında **zemin zaten var**:
`ProjectScreen.test.jsx` `shared/api.js` ile `shared/router.js`'i mock'layıp ekranın tamamını
kuruyor. Eksik olan zemin değil, onu seçimle sürüklemek — bugüne kadar o dosyada "seçim" kelimesi
hiç geçmiyor. Yani bu döngü yeni bir altyapı kurmuyor, var olanı ilk kez dikişin üstünde kullanıyor.

## Vakalar

Hepsi çalıştırılabilir testler; hiçbiri metin okumuyor.

### A · Panel — kimlikle eşler, dosya adı gönderir (`LayerPanel.test.jsx`)

| # | Vaka | Beklenen |
|---|---|---|
| A1 | Seçim bir karenin **kimliğini** taşıyor | "Seçili kareler" 1 diyor, satır etkin, tahmin "1 video üretilecek" |
| A2 | Seçilen karenin zaten videosu var | Yine sayılıyor — elle seçmek "bir tane daha" demenin yolu |
| A3 | Kimlikle seçilen kare kuyruğa ekleniyor | Sunucuya giden şey **dosya adı** (`["0_a.png"]`), kimlik değil |
| A4 | İki kare aynı fotoğrafı gösteriyor, biri seçili | Yalnız seçilen sayılıyor |

A4 bu ayrımın var olma sebebi: bir kareye ikinci video istendiğinde kopya kare doğuyor ve iki kare
tek dosyayı gösterebiliyor — galerinin kendi yorumunun söylediği şey bu. A4 olmadan biri hatayı
"panel dosya adıyla eşlesin" diye ters yönden kapatabilir ve öteki üç test buna izin verir.

### B · Ekran — dikişin kendisi (`ProjectScreen.test.jsx`)

| # | Vaka | Beklenen |
|---|---|---|
| B1 | Galeride bir kare seçilir, sonra seçim kaldırılır | Seçilince video panelindeki sayı 1 olur, kaldırılınca 0'a döner |

Tek test, iki iddia: "0'a döner" tek başına bugün de geçerdi (sayı hep 0), o yüzden önündeki "1
olur" iddiası olmadan hiçbir şey söylemiyor.

## Kapsam dışı

- **Halkaların seçim kalkınca kalması** — Görev 4. Buradaki B1 sayıyı okuyor, halkayı değil.
- **Ses panelinin aynı davranışı.** İki panel tek bileşen; kimlik eşleşmesi ikisi için de aynı satır.
  Ayrı test yazmak aynı satırı iki kez sınamak olurdu.
- Sunucunun dosya adıyla ne yaptığı: değişmiyor.

## Kırmızı commit

İki yeni test (A4, B1) ve düzeltilmiş üç test (A1, A2, A3) — beşi de düşer. Commit mesajı bunu
söyler; `xfail`/`skip` yok.

## Bitti sayılır

`npm test --prefix queen-editor/frontend` beş düşen test gösteriyor ve düşme sebepleri yukarıdaki
tablonun beklediği sebepler — hiçbiri eksik yardımcıdan ya da yazım hatasından düşmüyor.
