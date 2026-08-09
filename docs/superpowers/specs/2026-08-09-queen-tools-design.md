# Queen Tools — Export JSON'dan videoya (tasarım)

**Tarih:** 2026-08-09 · **Durum:** onaylandı, uygulama planı bekliyor

## Amaç

Queen Editor'ün ürettiği fotoğrafları videoya çevirmek. Zincirin iki halkası (foto→video, video→ses)
zaten var; eksik olan, Queen Editor'ün **Export** dosyasını girdi olarak kabul eden bir foto→video
aracı. Export bugün üretiliyor ve onu okuyan hiçbir şey yok.

`collab-toolbox/queen-tools/` altında iki notebook ekleniyor: biri Export'taki foto prompt'larını
hareket prompt'una çevirir, diğeri sonucu okuyup videoları üretir.

## Bugünkü durum

| Araç | Ne yapıyor | Arada kalan elle iş |
|---|---|---|
| Queen Editor | `N_<harf>.png` üretir; Export → `{folder, photos:[{file, prompt}]}` | Export dosyasını kimse okumuyor |
| [wan22-arbuzai/api_from_photos.ipynb](../../../collab-toolbox/video_generator/wan22-arbuzai/api_from_photos.ipynb) | `input/N_<harf>.png` + `PROMPTS[N]` → `output/N_<harf>.mp4` | fotoğraflar elle kopyalanır, `PROMPTS` listesi elle yazılır |
| [mmaudio_generate.ipynb](../../../collab-toolbox/mmaudio_generate.ipynb) | videoya foley üretir | videolar elle kopyalanır |

İki engel var. **Birincisi:** Export'u kabul eden bir foto→video aracı yok. **İkincisi:** Export'un
verdiği `prompt` *fotoğrafı* anlatıyor ("kraliçe tahtta, altın taç"), i2v grafı ise *hareketi*
istiyor — üstelik foto prompt'ları Türkçe, video modeli İngilizce bekliyor.

## Kararlar

| Karar | Gerekçe |
|---|---|
| Ayrı klasör: `collab-toolbox/queen-tools/` | Kullanıcı kararı. Ne Queen Editor'e ne `wan22-arbuzai/`'ye karışır |
| İki notebook, tek değil | Donanım ayrı: çeviri CPU'da dakikalar, video A100 + ~36 GiB model. Tek notebook iki cümle çevirmek için A100 açtırırdı |
| Drive kökü `MyDrive/queen-tools/` | Kendi alanı. `imageToVideoV2/` ile hiçbir şey paylaşılmaz — `api_from_photos.ipynb` de `N_<harf>.mp4` yazdığı için ortak `output/` çakışma demekti |
| **İş emri yüklenen dosyadır** — iki notebook da ne yapacağını Colab'a yüklenen JSON'dan öğrenir | Kullanıcı kararı: yüklenen dosya hangisiyse o işlenir. Drive'dan seçmek "hangi projeyi açacağını" bir ayar satırına bırakırdı ve yanlış projeyi render etme riski doğardı |
| Çevirici **ilerlemeyi Drive'da tutar** | Kullanıcı kararı. Colab ölürse yarım iş kaybolmasın. Bu yukarıdaki kuralla çelişmez: Drive'daki dosya *hangi işin isteneceğini* değil, *o işin nesi bitmiş* olduğunu söyler — iş emri yine yüklenen export'tur |
| Otomatik indirme yok, **indir butonu** | Kullanıcı kararı. Dosya iş bitince, sen isteyince iner |
| **Kare başına bir istek**, cevap düz metin | Kullanıcı kararı: tek çağrıda bütün liste modelin çıktı limitine yaslanır. Kare başına istekte model JSON döndürmez — şema pazarlığı, sayım kontrolü ve "satır düşürdü mü" derdi hiç doğmaz; patlayan çağrı yalnız o kareyi etkiler |
| Çeviri sonucu **ayrı dosya** (`video.json`) | İki ayrı soru: export "bu fotoğrafı ne üretti" (kalıcı iz), video planı "bu fotoğraf nasıl hareket etsin". CODE-STANDARD'ın kuralı — başka soruya cevap veren alan başka dosya ister |
| Çeviri **Export butonuna girmez** | Export bugün anlık çalışan bir indirme bağlantısı ([Bölüm 10 spec'i](2026-08-05-queen-editor-bolum10-export-design.md)); araya ağ çağrısı koymak onu yavaş, patlayabilir ve yükleme durumu isteyen bir şeye çevirirdi. Queen Editor'ün kodunda tek satır değişmez |
| Queen Editor'ün proje klasörü **yalnız okunur** | Bağımsızlık. Fotoğraflar `folder` yolundan okunur; oraya video, JSON, geçici dosya — hiçbir şey yazılmaz |
| Notebook grafı **Drive'dan okur**; repodaki kopya kaynaktır | Colab'a repo klonlanmıyor (bu notebook'lar tek dosya olarak yükleniyor), o yüzden okuyabileceği tek kalıcı yer Drive. Graf zaten repoda commit'li: `wan22-arbuzai/workflow_api.json` — arbuzai ailesiyle paylaşılan aynı dosya, Drive'a oradan kopyalanır. Grafı değiştirmek yine `manual.ipynb` → Export (API) |
| Çıktı adı **sıra numarasıdır**: `001.mp4`, `002.mp4` | Kullanıcı kararı. Plan dosyasındaki `photos` sırası zaten videonun sırası; ad da onu taşıyınca klasörü alfabetik listeleyen her araç doğru sırayı görür. Hangi fotoğraf ve prompt olduğu `photos[n]` satırında duruyor, dosya adına ikinci kez yazılmaz. **Kabul edilen takas:** numara konumdan geldiği için, projeye foto eklenip yeniden export edilirse sonraki numaralar kayar ve "çıktı zaten var" kontrolü eski dosyaları bulamaz |
| Atlanan kare **numarasını harcar** (`001, 002, 004`) | Boşluk kaydırılırsa dosya ile plan satırı arasındaki tek eşleşme bozulur; boşluk ayrıca "orada bir şey atlandı" der |
| **Her iki sır da Colab Secrets'ta**: `XAI_API_KEY` ve `CIVITAI_COOKIE` | Kullanıcı kararı. NOTEBOOK-STANDARD §4 cookie'yi CONFIG'de tutmayı kabul ediyor, ama bu ailede anahtarın zaten Secrets'ta olması onu tutarsız bırakıyordu. `CIVITAI_COOKIE` adı Queen Editor'ünkiyle aynı — tek yapıştırma iki aracı da besler. Diğer notebook'lar değişmedi |
| `VARIANTS = 1` | Kullanıcı kararı. Ayar `api_from_photos`'tan devralınır ama 1'de kalır |
| `XAI_MODEL = "grok-4.3"` | Kullanıcı `grok-3` kullanıyordu; o model 15 Mayıs 2026'da deprecate edildi, **15 Ağustos 2026'da kapanıyor** ve istekleri zaten `grok-4.3`'e yönlendirilip o fiyattan faturalanıyor ([xAI retirement](https://docs.x.ai/developers/migration/may-15-retirement)). Yani davranış aynı, ad doğru |

## Akış

```
Queen Editor ──Export──> dugun-export.json  (bilgisayara iner)
                              │  Colab'a yükle
                   prompt_converter.ipynb  (CPU + Drive)
                              │  indir butonu
                        dugun-video.json   (elle düzeltilebilir)
                              │  Colab'a yükle
                    photo_to_video.ipynb   (A100 + Drive)
                              ↓
              MyDrive/queen-tools/dugun/001.mp4 …
```

## Drive düzeni

```
MyDrive/queen-tools/
├── workflow_api.json     ← bir kez elle konur: repodaki wan22-arbuzai/workflow_api.json'un kopyası
└── <proje>/              ← notebook açar
    ├── video.json        ← çevirici yazar (ilerleme + sonuç)
    └── 001.mp4 …         ← video notebook'u yazar
```

`<proje>` = export'taki `folder` yolunun son parçası. Kullanıcı proje adını hiçbir yere yazmaz.
Queen Editor'ün kökü (`MyDrive/queenEditor/`) ayrı durur ve yalnız okunur.

## Dosya biçimi

Çeviricinin çıktısı, export'un şeklini bozmaz — bir alan ekler:

```json
{
  "folder": "/content/drive/MyDrive/queenEditor/dugun",
  "photos": [
    { "file": "11_d.png",
      "prompt": "slow camera push in, she turns her head slightly",
      "photo_prompt": "kraliçe tahtta, altın taç" }
  ]
}
```

- `prompt` — video notebook'unun okuduğu alan. Çeviriden sonra **hareket prompt'u** burada durur.
- `photo_prompt` — orijinal foto prompt'u. Üç iş birden yapar: **çevrildi işareti** (varsa o satır
  çevrilmiştir, tekrar çevrilmez), elle düzeltirken **referans**, ve fotoğrafın izi.
- İki dosyanın şekli aynı olduğu için video notebook'u hangisini verdiğine bakmaz; çeviri istemediğin
  projede doğrudan ham export verilir. Kodda dallanma yok.
- `photos` sırası export'tan geldiği gibi korunur — çevirici sırayı değiştirmez.

**Asıl kopya Drive'dakidir.** İndirilen dosya, video notebook'una vermek için alınmış bir kopyadır.
Elle düzelttiğin prompt'un kalıcı olmasını istiyorsan düzeltmeyi `queen-tools/<proje>/video.json`
üzerinde yaparsın. Yalnız indirdiğin kopyayı düzeltirsen o koşuda istediğin gibi render edilir, ama
bir sonraki çeviri koşusu sana Drive'daki hâlini geri verir.

## 1. `queen-tools/prompt_converter.ipynb` — CPU

Model indirmez, GPU istemez. Drive'ı yalnız ilerlemeyi saklamak için mount eder (NOTEBOOK-STANDARD
§1: mount ilk hücrede).

**Girdi:** Colab'a yüklenen export dosyası.
**Çıktı:** `MyDrive/queen-tools/<proje>/video.json` + iş bitince **indir butonu**.

**Dosya doğrulaması.** `folder` ve `photos` var mı, her satırda `file` ve `prompt` var mı — yoksa
hücre neyin eksik olduğunu yazıp `RuntimeError` ile durur. Dosya elle de düzenlenebildiği için bu
kapı gerekli.

**Liste export'tan gelir.** Drive'da `video.json` varsa açılır ama **kaynak yüklenen export'tur**:
export'ta olan yeni kareler çevrilir, export'tan silinmiş kareler dosyadan düşer, `photo_prompt`'u
olan kareler (elle düzeltilmiş olanlar dahil) aynen korunur. Böylece silinmiş bir fotoğraf listede
hayalet gibi kalmaz.

**Çeviri.** Kare başına bir istek: talimat + o karenin foto prompt'u → cevap **düz metin**, hareket
prompt'u. Türkçe→İngilizce çevirisi de aynı çağrıda olur. İstekler sırayla gider. **Foto prompt'u boş
olan kare hiç gönderilmez** — tabloda "prompt boş" ile atlanır; boş metne cevap almak için para
harcanmaz.

**Devam edebilirlik.** Her başarılı çeviriden sonra `video.json` Drive'a yazılır. Colab ölse, sekme
kapansa, çağrı patlasa fark etmez: aynı export'u tekrar yüklediğinde `photo_prompt`'u olan kareler
atlanır, kalınan yerden devam eder. Ödenmiş çağrı boşa gitmez. Tek bir kareyi yeniden çevirtmek için
o satırın `photo_prompt` alanını dosyadan silmek yeter.

**Tablo.** Her kare için `dosya · eski prompt · yeni prompt` basılır; sonuç gözle geçirilir.

**Ayarlar (CONFIG).**
- Çeviri talimatı düzenlenebilir bir metindir. Wan I2V için yazılmış bir başlangıç sürümüyle gelir:
  kamerayı sabit tut, sahneyi yeniden tarif etme (model görüntüyü zaten alıyor), ana aksiyonu
  sürekli harekete çevir, ikincil hareket ekle, fiziksel olarak makul kal, tempo ve ruh hâli
  belirt. Çıktı **düz metin** istenir — kare başına tek istek gittiği için liste biçimi ayrıştırma
  derdi doğurur, karşılığında hiçbir şey vermez. **Boşaltılırsa hücre `RuntimeError` ile durur:**
  boş talimatla istek atıp para harcamaz.
- `XAI_MODEL = "grok-4.3"`, endpoint `https://api.x.ai/v1/chat/completions`,
  `Authorization: Bearer <anahtar>` (OpenAI uyumlu gövde).
- `XAI_API_KEY` **Colab Secrets'tan** okunur ve hiçbir çıktıya basılmaz. Notebook kaynağına yazılmaz.

**Hata.** Çağrı 2xx dönmezse **servisin kendi yanıtı** basılır (HTTP kodu + gövde), sebep uydurulmaz
(NOTEBOOK-STANDARD §2). Yeniden deneme yoktur: notebook'u tekrar çalıştırmak zaten kaldığı yerden
devam eder.

## 2. `queen-tools/photo_to_video.ipynb` — A100

[api_from_photos.ipynb](../../../collab-toolbox/video_generator/wan22-arbuzai/api_from_photos.ipynb)'ın
kopyası. **Değişen:** CONFIG ve plan hücresi. **Aynen kalan:** ortak yardımcılar, 16 custom node,
model indirme + doğrulama, ComfyUI'yi arka planda başlatma, render döngüsü, hata sınıflandırması
(loader hatası batch'i durdurur, tekil hata kareyi atlar, üst üste 3 hata durdurur), `VARIANTS`
adlandırması. Civitai cookie'si tek farkla taşınır: değeri CONFIG'e gömülü değil,
`CIVITAI_COOKIE` sırrından okunur (kararlar tablosu).

**Girdi:** Colab'a yüklenen `video.json`. Fotoğraflar JSON'daki `folder` yolundan **doğrudan
okunur** — kopyalama yok. Aynı Drive aynı yola mount olduğu için yol çözülür; klasör yoksa hücre
yolu basıp durur.

**Çıktı:** `MyDrive/queen-tools/<proje>/001.mp4` — ad, karenin plan dosyasındaki 1-tabanlı
konumudur (üç hane). `VARIANTS > 1` ise `001_<v>.mp4` (v 1'den). Klasörü notebook açar.

**Plan tablosu** modeller inmeden basılır: `çıktı · ÜRET/ATLA · fotoğraf · sebep`. Atlama sebepleri:
prompt boş · çıktı zaten var · **JSON'da yazan dosya `folder`'da yok** (dosya bayatlamış, uyarı
satırı). ÜRET sıfırsa `RuntimeError` — ~36 GiB boşuna inmez.

**Grafa yazılan alanlar** `api_from_photos.ipynb` ile aynı: LoadImage `287`, PromptGenerator
`233:240` (prompt + seed), Seed `210`. LoRA, çözünürlük, step, cfg graftan gelir.

**Yarıda kalırsa** notebook baştan çalıştırılır: Drive'da mp4'ü olan kareler hem planda hem döngüde
atlanır (NOTEBOOK-STANDARD §5).

## Repo işi

`CLAUDE.md`'nin notebook tablosuna iki satır eklenir (repo kuralı: yeni araç → alt klasör + tabloda
satır). Donanım sütunu: çevirici **CPU**, video **A100 (Colab Pro)**.

## Doğrulama (kullanıcı, Colab)

1. Queen Editor'de birkaç fotoğraflı bir projede **Export** → `dugun-export.json` iner.
2. `prompt_converter.ipynb` → dosyayı yükle → tabloda her kare için eski/yeni prompt görünür;
   `queen-tools/dugun/video.json` Drive'da oluşur; indir butonu dosyayı indirir.
3. Aynı export'u tekrar yükle → hepsi çevrilmiş olduğu için **tek çağrı yapılmaz**.
4. Drive'daki `video.json`'da bir satırın `photo_prompt` alanını sil, export'u tekrar yükle →
   **yalnız o kare** çevrilir.
5. Çeviri sürerken runtime'ı kapat, yeniden aç, aynı export'u yükle → kalınan yerden devam eder.
6. CONFIG'deki çeviri talimatını boşalt, çalıştır → istek atılmadan `RuntimeError`.
7. `photo_to_video.ipynb` → `video.json`'u yükle → plan tablosu **modeller inmeden** basılır, her
   satırda gerçek fotoğraf adı görünür.
8. Koşu biter → `MyDrive/queen-tools/dugun/001.mp4, 002.mp4 …` Drive'da ve dosya sırası videonun
   sırasıyla aynı; Queen Editor'ün proje klasöründe
   **yeni hiçbir dosya yok**.
9. Notebook'u tekrar çalıştır → hepsi "zaten var" ile atlanır.
10. JSON'a olmayan bir dosya adı yaz, tekrar çalıştır → o satır ATLA + "dosya yok" ile görünür, koşu
    diğerlerini üretir.
11. `queen-tools/workflow_api.json`'u geçici olarak kaldır → hücre yolu yazarak durur.

## Kapsam dışı

- **mmaudio** — zincir `queen-tools/<proje>/` klasöründe biter; oradan sonrası elle taşınır, mmaudio
  notebook'una dokunulmaz.
- **Kliplerin tek videoda birleştirilmesi** — çıktı ayrı ayrı kliplerdir (kullanıcı kararı).
- **Queen Editor'de herhangi bir değişiklik** — Export bugünkü hâliyle yeterli. Hareket prompt'unun
  kare başına Queen Editor'de tutulması ileriki bir iş.
- **Çevirinin Export butonuna gömülmesi** — kararlar tablosunda gerekçesiyle reddedildi.
- **Çeviri talimatının iyileştirilmesi** — CONFIG'de bir başlangıç sürümü var; sonuçlar görüldükçe
  orada düzeltilir, ayrı bir iş açılmaz.
- **`wan22-arbuzai/` ve `imageToVideoV2/`** — graf kopyalanması dışında dokunulmaz; iki notebook
  ailesi ayrı yaşamaya devam eder.
