# Queen Editor v5 · Görev 17 — Motor videoyu üretir · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 5, Görev 17 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
23'ün üretim yarısı, 28 · **Tür:** arka uç.

## Neden

Video işi kuyruğa giriyor (Görev 14, 15) ve prompt'u yazılıyor (Görev 16), ama onu yapacak üretici
yok: sırası gelen iş "video üreticisi bekleniyor" diyip koşuyu bekletiyor. Bu görev o üreticiyi
koyar — kare videolu hâle gelir, fotoğrafı yerinde kalır.

## Ne olacak

Sırası gelen video işi ComfyUI'ye ikinci bir grafiği çalıştırtır: karenin fotoğrafı yüklenir, video
prompt'u ve tohum yerleştirilir, çıkan mp4 karenin **video katmanı** olarak Drive'a yazılır.
Dosyanın adı katman şemasından gelir: `P11_3_V1_0.mp4`.

## Kararlar

### 1. Altyapı: aynı ComfyUI, ikinci bir grafik

Video üreticisi de ComfyUI'dir — makinede zaten ayakta, modelleri Görev 12'nin üretici kurulumuyla
iniyor ve motor "üretici" kavramını zaten tanıyor. Motor **WAN 2.2 I2V**, grafiğin kendisi
`queen-editor/workflow_video_api.json` olarak repoda taşınır — foto grafiğiyle aynı kural.

Node kimlikleri `collab-toolbox/queen-tools/photo_to_video.ipynb`'den devralınan bilgi:

| Node | Ne yapar |
|---|---|
| `287` | `LoadImage` — karenin fotoğrafı |
| `233:240` | `PromptGenerator` — video prompt'u |
| `210` | `Seed` (rgthree) — hem örnekleyicinin hem PromptGenerator'ın tohumu |

Yeni bir export bunları değiştirebilir; o zaman **tek dosya** değişir (`data/comfy_video_generator.py`).

### 2. Grafik dosyası kullanıcının dışa aktardığı bir varlıktır

`workflow_video_api.json` repoda **henüz yok** ve koddan üretilemez: ComfyUI'de "Workflow →
Export (API)" ile kaydedilip commit'lenmesi gerekir — foto grafiği de böyle geldi.

Dosya yokken video işinin sırası gelirse yükleyici kendi cümlesiyle patlar ("Video grafiği yok:
… — ComfyUI'de Export (API) ile kaydet ve commit'le") ve bu koşunun hatasıdır: bir sonraki video
işi de aynı yere düşecek. Yeni bir "kurulu değil" mekanizması açılmaz — üreticiler paneli makinedeki
**modelleri** anlatır, repodaki dosyayı değil.

### 3. Fotoğraf ComfyUI'ye yüklenir

Kare fotoğrafı Drive'da, ComfyUI ise kendi diskinde çalışıyor; ikisini bağlayan tek doğru yol
`POST /upload/image` (`overwrite=true`), sonra `LoadImage`'i dönen sunucu adına bağlamak.
Defterin yaptığı da bu.

Yükleme adı **karenin kendi foto dosyası adıdır** (`P0_1.png`): kare başına biricik, üzerine
yazıldığında da aynı kareye ait olur — sabit tek bir ad, iki kare arasında yanlış görüntüye işaret
etme riskini taşırdı.

### 4. Üretici portu bir isteğe bağlı argüman genişler

`generate(prompt, negative, seed, model="", source=None)`; `source`, `(dosya adı, bayt)` ikilisi.
Fotoğraf üreticisi onu hiç okumaz — bir foto kendinden üretilir. Motor, video işinde karenin foto
baytlarını depodan okuyup verir; bunun için depo portuna `read(project, filename)` eklenir.

Alternatif olan "yol ver" seçilmedi: yol bilgisi data katmanının işi ve domain'in `os.path`
kurcalaması bu ayrımı bozardı.

### 5. Dosya adı katman şemasından gelir

Video `video_file(kare, 1, 0)` ile adlanır: `P11_3_V1_0.mp4` — madde 97'nin örneğinin birebir
kendisi. Tur ve varyant şimdilik sabit (1, 0), çünkü bir karenin **tek** videosu olur: ikinci video
yeni bir kare doğurur (Görev 15). Turun artması yalnız "yeniden üret" ile anlamlı olur (madde 98,
Görev 25) ve o gün bu satır değişir.

Motorun bugün her katmanı `photo_file` ile adlandırması burada biter. Yan kazanç: aynı karenin foto
ve video işleri artık ayrı adlar taşıdığı için **deneme sayacı** ikisini karıştırmaz (bugün foto üç
kez patlamış bir karenin videosu ilk hatada kırmızıya düşerdi).

Galeri hâlâ kareyi **foto adıyla** işaretler (kuyruk raporundaki `pending`, `failures`): ekranın
karo kimliği fotoğrafın adıdır, katmanın değil.

### 6. Çıktı mp4'tür ve tek tanedir

ComfyUI video düğümleri çıktıyı `gifs`/`videos` altında yayımlar, foto düğümleri `images` altında;
grafikte ikisi birden olabilir. İstemci "çıktıyı getir"i bir **uzantı süzgeciyle** öğrenir: video
üreticisi yalnız `.mp4` ister, foto üreticisi bugünkü davranışta kalır.

Böylece grafiği webm yazan bir export sessizce mp4 adıyla kaydedilmez: "1 çıktı bekleniyordu, 0
geldi" der ve ham çıktıları basar.

### 7. Süre grafiğin kendi ayarıdır

Madde 28 "süre bu sürümde sabit" diyor; uygulama hiçbir uzunluk düğümüne dokunmaz. Panelin "her
video 5 saniye" cümlesi grafiğin export'una bakar — grafiği 5 saniyeye ayarlamak dışa aktaranın
işidir.

## Nasıl görülür

1. Videosuz kareye video iste → sırası gelince `P0_0_V1_0.mp4` Drive'a düşer.
2. Karenin fotoğrafı aynen durur; kayıtta ayrı bir video satırı doğar.
3. Grafik dosyası yokken koşu durur ve panel dosyanın adını söyler.

## Testler

**İstemci:** `upload_image` dosyayı `/upload/image`'e gönderir ve sunucunun verdiği adı döner ·
HTTP hatası gövdesiyle patlar · `fetch_output` uzantı süzgeciyle `gifs` altındaki mp4'ü bulur ·
süzgeç verilmeyince bugünkü davranış (yalnız `images`) sürer.

**Video üreticisi:** grafiğe fotoğrafın sunucu adı, prompt ve tohum yazılır · üretim baytları döner ·
kaynak verilmeyince kendi cümlesiyle patlar · grafik dosyası yokken/UI biçimindeyken/node eksikken
kendi cümlesiyle patlar. Bu sınıf `installed()` taşımaz: video üreticisinin kurulu olup olmadığına
model grubunun dosyaları karar veriyor (Görev 12).

**Depo:** `read` dosyanın baytlarını döner.

**Motor:** video işi karenin foto baytlarıyla üreticiye gider · çıkan dosya `P0_0_V1_0.mp4` adıyla
yazılır · kayıt satırı `layer: video` ve o adı taşır · foto işi hâlâ `.png` adıyla yazılır.

## Kapsam dışı

- **Galeride video rozeti ve oynatma** — Görev 18.
- **Katman hatası davranışı** — Görev 19.
- **Ses** — Blok 6.
- **`workflow_video_api.json`'ın kendisi** — kullanıcının export'u (karar 2).

## Riskler

- **Grafik gelene kadar video üretilemez.** Kod tamam olur, testler sahte grafikle koşar; gerçek
  video ancak dosya commit'lendikten sonra çıkar. Bunu görevin sonunda kullanıcıya söylemek şart.
- **Node kimlikleri export'a bağlı.** Farklı bir export farklı kimlikler verir; yükleyici eksik
  node'u adıyla söyler, sessizce yanlış yere yazmaz.
- **Bellekte bayt.** Foto baytları Drive'dan okunup HTTP ile yükleniyor; bir foto birkaç MB, tek
  iş sıradayken sorun değil.
- **"Üretici bekleniyor" hâli video için kapanıyor.** Motor bir türü ancak üreticisi *hiç yokken*
  bekletiyor (Görev 13); video üreticisi artık hep kayıtlı olduğu için, modelleri inmemiş bir
  makinede video işi ComfyUI'nin kendi hata cümlesiyle durur, kurulum kartıyla değil. Pratikte dar
  bir aralık: panel modeller inmeden video kuyruğa eklettirmiyor (Görev 14'ün kurulum kartı). Sesi
  bekleten hâl olduğu gibi duruyor.
