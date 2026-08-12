# Queen Editor v5 · Görev 22 — Motor sesi üretir ve videoya bindirir · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 6, Görev 22 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
30'un üretim yarısı, 58'in ses yarısı · **Tür:** arka uç + ön yüz.

## Neden

Ses işi kuyruğa giriyor (Görev 20) ve prompt'u yazılıyor (Görev 21), ama üreticisi yok: sırası
gelince motor "ses üreticisi bekleniyor" diyor. Bu görev o üreticiyi koyar ve karenin üçüncü
katmanını tamamlar.

## Ne olacak

Sırası gelen ses işi ComfyUI'nin üçüncü grafiğini çalıştırır: karenin **videosu** yüklenir, ses
prompt'u yerleştirilir, çıkan **wav** karenin ses katmanı olarak Drive'a yazılır. Adı videonun adını
büyütür: `P11_3_V1_0_S1_0.wav`. Galeride video rozetinin yanına ses rozeti gelir.

## Kararlar

### 1. Altyapı yine ComfyUI — MMAudio node'u

Üretici kurulumu (Görev 12) sesin modelini zaten ComfyUI'nin `models/mmaudio` klasörüne koyuyor;
yani "ses üreticisi ComfyUI'dir" kararı orada verilmiş. Grafik `queen-editor/workflow_audio_api.json`
olarak repoda taşınır — foto ve video grafikleriyle aynı kural, aynı "Export (API)" yolu.

`collab-toolbox/mmaudio_generate.ipynb` MMAudio'yu kendi python paketiyle koşuyor; o yol
seçilmedi: Flask sürecine torch ve bir GPU modeli sokmak, tek motor (ComfyUI) kuralını bozar ve
sunucuyu kurulumun bir parçası hâline getirir.

Node kimlikleri kendi export'umuzdan gelir ve `data/comfy_audio_generator.py`'de durur — grafik
değişirse yalnız o dosya değişir.

### 2. Kaynak videodur

Video işi fotoğrafı yüklüyordu; ses işi **videoyu** yükler (`POST /upload/image` ComfyUI'de video
dosyalarını da alır, LoadVideo onu adıyla bulur). Motorun "bir katman neyin üstüne biner"
sorusunun cevabı katmanın kendisinde: foto hiçbir şeyin, video fotonun, ses videonun.

### 3. Dosya videonun adını büyütür

Madde 97: ses dosyası `P11_3_V1_0_S1_0.wav`. Yani ad kareden değil **videodan** türer — ses bir
videonun üstüne bindiği için hangisinin üstünde olduğunu adı söyler. `layer_file` bu yüzden karenin
videosunu da bilmek zorunda.

Tur ve varyant yine sabit (1, 0): bir karenin tek sesi olur, ikincisi kopya kare doğurur.

### 4. "Bindirme" ayrı dosyadır, yeniden yazılmış video değil

Ses videoya **karıştırılmaz**: video dosyası olduğu gibi kalır, ses yanında kendi dosyası olarak
durur. Sebepler: tasarımın kendi adlandırması ses için ayrı bir dosya söylüyor (madde 97); silme
kuralları katman katman (madde 80, 101); ve videoyu yeniden yazmak "hiçbir üretim var olanı ezmez"
kuralını çiğnerdi.

Karenin sesli oynaması detay sayfasının işi (Görev 24: ses sekmesinde ses oynar), export'un işi
Blok 8.

### 5. Çıktı wav'dır ve tek tanedir

İstemci çıktıyı uzantıyla seçiyor (Görev 17). Ses için istenen uzantı `.wav`; grafiğin çıktı
düğümü wav yazacak biçimde export edilmiş olmalı, yoksa "1 çıktı bekleniyordu, 0 geldi" der ve ham
çıktıları basar. ComfyUI ses çıktısını kendi anahtarında yayımladığı için istemci, uzantı verildiğinde
çıktı sözlüğünün **bütün** listelerine bakar.

### 6. Galeride ikinci rozet

Madde 58: sesi de varsa video rozetinin yanına dalga ikonu + "ses" gelir. Rozet yalnız katman
tamamlandığında görünür — hatalı ses rozet doğurmaz, hâlini hap anlatır.

## Nasıl görülür

1. Videolu kareye ses iste → sırası gelince `P0_0_V1_0_S1_0.wav` Drive'a düşer.
2. Kayıtta ayrı bir ses satırı doğar; video dosyası değişmez.
3. Galeride sağ altta iki rozet yan yana.
4. Grafik dosyası yokken koşu durur ve panel dosyanın adını söyler.

## Testler

**İstemci:** uzantı süzgeci ses çıktısını da bulur (çıktı sözlüğünün her listesine bakılır).

**Ses üreticisi:** grafiğe videonun sunucu adı ve prompt yazılır · baytlar döner · kaynak
verilmeyince kendi cümlesiyle patlar · grafik yok/UI biçiminde/node eksik hâllerinde kendi cümlesiyle
patlar.

**Adlandırma:** `layer_file("audio", "P11_3", video="P11_3_V1_0.mp4")` → `P11_3_V1_0_S1_0.wav` ·
videosu olmayan kareye ses adı istenirse (olmaması gereken hâl) karenin kendi adına düşer.

**Motor:** ses işi karenin video baytlarıyla üreticiye gider · dosya `..._S1_0.wav` adıyla yazılır ·
kayıt satırı `layer: audio`.

**Ön yüz:** sesli karede iki rozet · sesi hatalı karede yalnız video rozeti.

## Kapsam dışı

- **Oynatma** — Görev 24.
- **Ses silme** — Görev 26.
- **`workflow_audio_api.json`'ın kendisi** — kullanıcının export'u.

## Riskler

- **Grafik gelene kadar ses üretilemez.** Video grafiğiyle aynı durum; ikisi de kullanıcının
  ComfyUI'sinden çıkacak.
- **MMAudio node'unun kendi ağırlıkları.** İlk kullanımda kendi indirmesini yapıyor; üretici
  kurulumu bunu zaten böyle söylüyor (Görev 12).
