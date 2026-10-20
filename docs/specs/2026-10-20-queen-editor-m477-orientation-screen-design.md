# Madde 477 · Üretimin yönü, ekran — tasarım

**Tarih:** 20 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
477 · v10-3c · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)
· **Sunucu tarafı:** [476](2026-10-20-queen-editor-m476-orientation-design.md)

## Kullanıcıdan gereken

Hiçbir şey. Madde 20 Ekim'de hizalandı. Ana ajan 20 Ekim'de iki açık soruyu cevapladı: *Yeniden
üret*te seçenek karenin kendi yönüyle, yani ekrandaki resmin şekliyle açılır; *Referanstan*'ın yönü
kendi kaydında, `reference_settings.json`'da saklanır.

## Ne, neden

Kullanıcının sözü *(20 Ekim)*: "üretim başına negative prompt gibi 2 opsiyon olsun sadece sen
istediğin gibi ekle sonra tasarımcıdan tasarım gelince düzeltiriz". 476'dan beri sunucu her
üretimde `orientation` alıyor (`yatay` | `dikey`, verilmezse `yatay`). Bu parça ekrana seçeneği
koyar: bir fotoğraf üretiminin başladığı her formda **Yön: Yatay | Dikey**, negatif prompt'un
ayarlandığı gibi.

## Bugün — koddan okunanlar

- **Fotoğraf paneli** (`GeneratePanel`): negatif bir metin kutusu. Açılışta değeri projenin kaydından
  (`settings.json`, `GET …/settings`) ya da bu ziyaretin taslağından (`REMEMBERED`) gelir.
  *Kuyruğa ekle*'ye basılınca `ProjectScreen.handleGenerate` önce kaydı yazar (`PUT …/settings`),
  sonra `POST …/generate`'i gönderir.
- **Yeniden üret** (`PhotoDetail`, Foto sekmesi): negatif kutusu karenin kendi negatifiyle
  (`frame.negative`) açılır, değişirse onunla gider. Kayıt yok; kelimeler sayfada yaşar.
- **Referanstan** (`LayerPanel`, video, havuzdan): prompt listesi ve varyant kendi kaydında
  (`reference_settings.json`); basılınca önce kayıt, sonra `POST …/references/produce`.
- **Karenin satırı:** galeri kartı plan satırını yayar, yani 476'dan sonra planlanan bir fotoğrafın
  kartında `orientation` var. 476'dan önceki satırlarda, kopya karelerde (kartları kayıt satırından
  okunur) ve havuz kartlarının ilk-kare resminde yok.
- Ortak iki düğmeli bir segment bileşeni yok: *Video uzunluğu* ve *Mutlu son* `wf-segment`'i
  `LayerPanel`'in içinde çiziyor.

## Ne değişir

### 1. `orientation.jsx` — ekranın yön sözlüğü

`production_modes.js`'in eşi, yeni dosya:

- `LANDSCAPE = "yatay"`, `PORTRAIT = "dikey"` — sunucunun kelimeleri; burada yalnız Türkçe etiketler
  (`Yatay`, `Dikey`) yaşar.
- `FIRST_ORIENTATION = LANDSCAPE`: hiçbir şeyin bir yön söylemediği kutunun açıldığı değer. Sunucunun
  varsayılanının ekrandaki gösterimi; istek her zaman segmentin gösterdiğini taşır, ve iki kelimeye
  tutan sunucudur. `GeneratePanel`'in `FIRST_VARIANTS`'ı ve `PhotoDetail`'in `STANDARD`'ı gibi.
- `shapeOf(width, height)`: genişlik yükseklikten büyükse `yatay`, değilse `dikey` — H3
  üreticisinin bir fotoğrafı okuduğu kural (476). Ekranda yalnız bir kutunun açılış değeri için.
- `OrientationSegment({ value, onChange })`: iki düğmeli `wf-segment`, etiketsiz — her form başlığını
  kendi yüzüyle çizer. Seçili olan `is-on` sınıfını ve `aria-pressed="true"`'yu taşır.

### 2. Fotoğraf paneli — projeyle saklanır

- **Yer:** negatif prompt'un hemen altında, *Varyant*'ın üstünde, başlığı **Yön**. Neden: kullanıcı
  "negatif prompt gibi" dedi; aynı şekilde ayarlanan iki şey yan yana durur. Tasarımcının tasarımı
  gelince yeri değişebilir.
- **Açılış:** taslak varsa taslağınki; yoksa kaydın `orientation`'ı; o da boşsa `Yatay`.
- **Gönderim:** `generateBatch` gövdesine `orientation` girer. *Kuyruğa ekle* önce kaydı yazar —
  `saveSettings` gövdesine de `orientation` girer —, sonra üretimi gönderir; yani bir proje en son
  gönderdiği yönle açılır, negatifi gibi.
- Bir seçim, bir tuş vuruşu gibi önceki denemenin cevabını (alan hatası, ret) temizler.

### 3. `settings.json` ve `reference_settings.json` — bir alan daha

İki kayıt da "kutular açılınca ne göstersin" sorusunu cevaplar (CODE-STANDARD, *Separation of
concerns*); yön de o sorunun cevabı. Yeni dosya yok.

- `DriveSettingsStore` / `DriveReferenceSettingsStore`: `orientation` bir metin olarak okunur ve
  yazılır, doğrulanmaz — `model` ve `lora` gibi. Alanı olmayan eski bir kayıt ya da metin olmayan
  bir değer `""` okunur; ekran boşu `Yatay` açar. Doğrulama sunucunun üretim kapılarında (476):
  bilinmeyen bir değer orada 400 alır.
- `save_settings` / `save_reference_settings`: `orientation=""` alır ve kayda yazar.
- `PUT …/settings` / `PUT …/reference-settings`: metin olmayan değer `""` olur.

Projeler özelliği fotoğraf özelliğinin `orientation` modülünü içe aktarmaz (`feature ↛ feature`); bu
yüzden kelimeleri bilmez, yalnız saklar.

### 4. *Yeniden üret* — karenin kendi yönüyle açılır

- **Yer:** Foto sekmesinde, fotoğrafın negatif kutusunun altında, *Yeniden üret* düğmesinin üstünde;
  yalnız fotoğraf varken (`holds`). Video ve Ses sekmesinde yok: video altındaki fotoğrafın şeklini
  izler (476).
- **Açılış kuralı — kutu karenin kendi değeriyle açılır**, negatif kutusu `frame.negative`'le
  açıldığı gibi. Karenin kendi yönü, sahnenin gösterdiği resmin şeklidir: resim yüklenince
  (`onLoad`) `naturalWidth` ve `naturalHeight` `shapeOf`'tan geçer. Satırın kelimesi değil resim,
  çünkü 476'dan önceki kareler, kopya kareler ve havuz kartları satırda yön taşımaz ama resimleri
  bir şekle sahiptir. Resim gelene kadar `frame.orientation`, o da yoksa `Yatay`.
- Okunan şekil hangi dosyaya ait olduğuyla tutulur (`{ file, facing }`). Sayfanın durumu oklarla
  kareden kareye geçerken yaşar; dosya olmasa önceki karenin şekli yeni resim gelene kadar ekranda
  kalırdı, ve kare değişince sıfırlamak onu bir çizim boyunca yine gösterirdi. Dosyaya bağlı olunca
  kopya kare kaynağının şeklini hemen alır.
- **Gönderim:** yalnız Foto sekmesinden: `regenerateFrame`'e yedinci argüman olarak `orientation`.
  Video ve ses için `undefined`, gövdeye girmez.
- Kullanıcı segmente dokunursa seçimi resmin şeklinin önüne geçer; başka bir kareye geçince seçim
  düşer, mod kutusu gibi. Kayıt yok: bu sayfada hiçbir kelime saklanmaz (madde 76).

### 5. *Referanstan* — kendi kaydıyla saklanır

- **Yer:** *Prompt listesi*'nin altında, *Varyant*'ın üstünde, başlığı **Yön** (`data-label`'lı, sekme
  düzeninin bir satırı). Yalnız Referanstan sekmesinde: Kareden'de video karenin fotoğrafını izler.
- **Açılış:** bu ziyaretin taslağı (`DRAFTS`), yoksa kaydın `orientation`'ı, o da boşsa `Yatay`.
  Segmente dokunmak bir tuş vuruşu sayılır (`settled`): yolda olan kayıt artık üstüne yazmaz.
- **Gönderim:** önce `saveReferenceSettings({ prompts, variants, orientation })`, sonra
  `onQueue(null, count, "reference", prompts, orientation)` → `useGeneration.queueLayer`'ın altıncı
  argümanı → `produceFromReferences(project, prompts, variants, orientation)`.

## Maliyet

Koddan sayıldı, ölçülmedi.

| İşlem | Bugün | Sonra |
|---|---|---|
| *Kuyruğa ekle* (fotoğraf) | 1 `PUT settings` + 1 `POST generate`; Drive'da `settings.json` bir kez yazılır | aynı; gövdelerde bir alan daha |
| Proje açılışı | 1 `GET settings` | aynı |
| *Yeniden üret* sayfası | resim bir kez yüklenir | aynı; şekil yüklenmiş resmin boyutundan okunur, ek istek yok |
| *Yeniden üret* | 1 `POST regenerate` | aynı; gövdede bir alan daha |
| *Referanstan* | 1 `GET reference-settings` (ziyarette bir kez), basınca 1 `PUT` + 1 `POST produce` | aynı |

Ne Drive'a ne ağa ek bir gidiş var. Proje, kare ya da dosya sayısıyla büyüyen bir şey yok.

## Ne kaybolabilir, ne bozulabilir

- **Kayıtlar** 472'nin `Storage`'ıyla yazılır: geçici dosya, `fsync`, `os.replace`. Okunamayan bir kayıt
  bugünkü gibi boş okunur ve kutuları boş açar; bu iki dosya yalnız kutuları doldurur, üstüne yazmak
  bir şey kaybettirmez — basışla yazılan, ekrandakinin aynısıdır.
- **Eski kayıtlar** alanı olmadan okunur (`""` → `Yatay`); yeniden yazılmaz, ta ki kullanıcı bir daha
  gönderene kadar.
- **URL'den gelen değer** bu kayıtlarda yalnız metin olarak saklanır; yola, dosya adına ya da grafiğe
  girmez. Üretime giden değer 476'nın kapılarında iki kelimeyle karşılaştırılır.
- **Aynı anda iki istek**: yön her isteğin kendi gövdesinde; ortak durum yok.
- **Eski bir dikey kareyi yeniden üretmek** artık dikey açılır (resmin şekli). Kullanıcı yatayı seçerse
  yeni kare yatay çıkar; eski kareye dokunulmaz (madde 77).

## Bu maddenin kararları

1. **Ortak bir `orientation.jsx`:** kelimeler, etiketler, açılış değeri, `shapeOf` ve segment bir
   yerde; üç form onu kullanır.
2. **Fotoğraf panelinde yön negatifin altında**, projenin `settings.json`'ında saklanır.
3. **Yeniden üret karenin kendi yönüyle açılır**, karenin kendi yönü ekrandaki resmin şekli
   *(ana ajan, 20 Ekim)*.
4. **Referanstan'ın yönü `reference_settings.json`'da** *(ana ajan, 20 Ekim)*.
5. **Kayıtlar yönü doğrulamaz**, `model` / `lora` gibi; doğrulama üretim kapılarında.

## Sınırlar

- **Galeri kareleri kare kırpılmış** (kare döşeme); yatay ve dikey galeride aynı görünür. Bu parçada
  değişmez.
- **Export'un tuvali 478'de.**
- **Ayrıntılar** satırında yön yazmaz; madde istemedi.
- **Yer geçici:** tasarımcının tasarımı gelince segmentin yeri ve görünüşü düzeltilir.

## Bitti sayılır

1. Testler gösteriyor ki:
   - fotoğraf panelinde *Yön* negatifin altında, kayıt boşsa *Yatay* açılıyor, kaydın `dikey`'iyle
     *Dikey* açılıyor; dokunulmadıysa `yatay`, *Dikey* seçildiyse `dikey` gidiyor; seçim taslakla
     birlikte hatırlanıyor ve alanın hatasını temizliyor; *Kuyruğa ekle* yönü kayda ve üretime
     veriyor;
   - *Yeniden üret*te segment yalnız Foto sekmesinde; resim gelmeden satırın yönüyle ya da *Yatay*'la,
     resim gelince resmin şekliyle açılıyor; seçim resmin şeklinin önüne geçiyor ve gidiyor; başka
     kareye geçince düşüyor;
   - *Referanstan*'da segment yalnız o sekmede, kaydın yönüyle ya da *Yatay*'la açılıyor, seçim kayda
     ve üretime gidiyor, panel yeniden kurulunca taslakta kalıyor;
   - `api.js` beş isteğin gövdesinde `orientation`'ı taşıyor;
   - `settings.json` ve `reference_settings.json` `orientation`'ı yazıp okuyor; alanı olmayan ya da
     metin olmayan değer `""`.
2. Dört satır yeşil: `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend`
   (ve öteki iki suite ana ajanda).
3. `dist` yeniden kuruldu (`npm run build --prefix queen-editor/frontend`).
4. Yatay üretimin gerçek resmi 478'in sonundaki Colab denemesinde görülür *(kullanıcı)*.
