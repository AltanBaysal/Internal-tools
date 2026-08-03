# Queen Editor — Yol Haritası v2 (tasarım güncellemesi)

**Tarih:** 2026-08-03 · **Durum:** onay bekliyor · sırada Bölüm 6
**Tasarım kaynağı:** claude.ai/design projesi `Queen Editor` → `Queen Editor Basit v1.html` + `HANDOFF.md` (kullanıcının güncellediği hâli — davranış kararlarının tamamı orada)
**Şemsiye tasarım:** [2026-08-03-queen-editor-v2-design.md](../specs/2026-08-03-queen-editor-v2-design.md) (davranış kararları) · [2026-07-24-queen-editor-v1-design.md](../specs/2026-07-24-queen-editor-v1-design.md) (mimari kararlar)
**Yerini aldığı doküman:** [2026-07-24-queen-editor-roadmap.md](2026-07-24-queen-editor-roadmap.md) — oradaki Bölüm 6 buradaki Bölüm 6'ya, Bölüm 7 buradaki Bölüm 11+12'ye eridi.

Tek kaynak: bütün bölümlerin dökümü burada. İlke aynı — **önce çalıştır, sonra sağlamlaştır**; her bölüm bir öncekinin üstüne birikir, hiçbirinin çıktısı çöpe gitmez. Her bölüm çıktı odaklı (**ne çalışır** + **nasıl görülür**) ve Colab'da tek başına "evet oldu" denerek kapanır. Sırası gelen bölümün detaylı planı ve o bölümü ilgilendiren kararlar o an netleşir.

**Kapsam sınırı:** Video üretiminin kendisi bu yol haritasının dışında — sınır Export dosyası (Bölüm 8). Tasarımın kapsam dışı listesi aynen geçerli: bağlantı çubuğu · foto sayısı / kapak · yeniden adlandırma · referans görsel.

---

## Tamamlanan bölümler (1-5)

Eski yol haritasından, her biri Colab'da doğrulandı:

| Bölüm | Görülür çıktı |
|---|---|
| 1 · Repo çekimi | Private repo token'la Colab'a klonlanır |
| 2 · Bağlantı | Sunucu + tünel; sayfa açılır, "sunucuya bağlı ✓" |
| 3 · Proje | Proje oluşturma; Drive'da klasör; kart listesi |
| 4 · Tek foto | ComfyUI ile tek prompt → tek foto |
| 5 · Çoklu foto | Prompt listesi × varyant → galeri; Durdur; numaralar kaldığı yerden |

---

## Bölüm 6 — Kalıcılık + iz

Neredeyse her yeni özelliğin ön şartı: ayarlar projeyle yaşar, her fotonun kaynağı bilinir.

- **Ne çalışır:** prompt listesi, negatif ve varyant projeyle birlikte kaydedilir; her fotonun hangi prompt'tan üretildiğinin izi tutulur.
- **Nasıl görülür:** sayfayı yenile ya da projeyi başka cihazda aç → kutular dolu gelir; bir fotonun hangi prompt'tan geldiği bulunabilir.
- **Yok:** izi gösteren ekran (detay sayfası, Bölüm 9), export (Bölüm 8).

## Bölüm 7 — Galeri sıralama

Export sırasının temeli: kullanıcının elle kurduğu sıra.

- **Ne çalışır:** her karede sıra numarası rozeti; basılı tut + sürükle → kare taşınır, numaralar güncellenir; sıra kalıcı; yeni üretilen fotolar elle sıralanmış galerinin en üstüne düşer.
- **Nasıl görülür:** sırala → sayfayı yenile → sıra durur; tekrar Üret → yeniler en üstte, eski sıra bozulmaz.
- **Yok:** export (Bölüm 8), silmede numara davranışı (Bölüm 10).

## Bölüm 8 — Export

Video hattını açan çıktı: bütün projeyi anlatan tek dosya.

- **Ne çalışır:** app bar'daki **Export** → tek JSON iner: en başta projenin Drive klasör yolu, ardından tüm fotoların dosya adı + prompt listesi, **galerideki güncel sırayla**. Export her zaman aktif — üretim sürerken ve hiç foto yokken de basılabilir.
- **Nasıl görülür:** dosyayı indir, aç → sıra galeriyle birebir; video bu sırayla uç uca eklenecek şekilde beslenebilir.
- **Yok:** video üretimi (kapsam dışı, başka araç).

## Bölüm 9 — Foto detay sayfası

Fotoyu gerçekten görmenin yolu; ham dosya sekmesinin yerini alır.

- **Ne çalışır:** fotoya tıkla → ayrı sayfa: foto olabildiğince büyük, **orijinal oranında** (dikey/yatay/kare, kırpılmaz); ‹ › okları foto alanının iki ucunda sabit, ilk/son fotoda pasif, başa sarmaz; klavye ← → gezer, Esc galeriye döner; sağda sıra ("3 / 48"), dosya adı ve prompt metni (kutu her zaman kaydırmalı); **Sil** → onay → sonraki foto açılır (son fotoysa önceki, hiç kalmadıysa galeri).
- **Nasıl görülür:** farklı oranlı fotolar arasında gez, birini sil, galeriye dön.
- **Yok:** toplu silme (Bölüm 10).

## Bölüm 10 — Silme + onaylar

Yıkıcı işlemlerin tamamı, hepsi onaylı.

- **Ne çalışır:** seçim modu — hover'da beliren ✓ ile açılır, seçili kare mor çerçeveli, altta yüzen bar ("3 seçili · Tümünü seç · Sil · Vazgeç"), Sil onay ister, silme kalıcıdır (Drive'dan da gider); proje silme — karttaki kırmızı çöp + onay, klasör içeriğiyle silinir; **Projeden çık** nötr renge döner + onay sorar; boş projeler ekranına "İlk projeyi oluştur" butonu.
- **Nasıl görülür:** 3 foto seç-sil → galeriden ve Drive'dan gider, sıra numaraları güncellenir; proje sil → kart ve klasör gider.

## Bölüm 11 — Üretim akışı

Üretim deneyimi tasarımdaki son hâline gelir; yeni ekran yok.

- **Ne çalışır:** **Durdur = duraklat** — üstte Devam et (kaldığı yerden), altta İptal et (kalan kuyruk atılır, üretilenler kalır); üretim sürerken panel alanları kilitli ve soluk, galeri tamamen serbest (detay + silme + sıralama); üretim başlayınca galeriye planlanan tüm kareler düşer — gelmemişler kesikli "bekliyor", o an üretilen "yükleniyor"; bitince yeşil "✓ 48/48 üretildi" bildirimi (yeni Üret'e kadar kalır); format kontrolü Üret'e basınca — bozuk listede kırmızı çerçeve + "Format hatası", yazmaya başlayınca temizlenir, boş listede Üret pasif.
- **Nasıl görülür:** Durdur → Devam et → kaldığı yerden sürer; İptal → üretilenler durur, panel hazıra döner; bozuk liste yapıştır → kırmızı uyarı, üretim başlamaz.
- **Açık soru (bu bölümde karara bağlanır):** varyant üst sınırı — tasarım "sınır yok" diyor, harf tabanlı adlandırma 26'da tıkanıyor.
- **Yok:** tekil kare hatası ve ölümcül durma (Bölüm 12).

## Bölüm 12 — Sağlamlık

v1 davranışlarının tam hâli: hiçbir senaryoda iş kaybı yok.

- **Ne çalışır:** tekil kare patlarsa kırmızı kare + **Tekrar dene** (sadece o kareyi üretir), üretim sıradakiyle sürer, ilerleme kartında "N fotoğraf üretilemedi" satırı; bağlantı kopması / servis ölümü / üst üste hatalar → kırmızı "Üretim durdu" kartı + kısa teknik neden + **Kaldığı yerden devam et** (yalnız eksikler üretilir); sekme kapansa, bilgisayar kapansa, Colab oturumu ölse bile proje yeniden açılınca aynı kart görünür ve tek tıkla sürer.
- **Nasıl görülür:** ComfyUI'ı öldür → hata kartı; runtime'ı yeniden başlat → devam kartı, yalnız eksikler üretilir.

## Bölüm 13 — Çoklu model

Bağımsız en büyük iş; hiçbir bölüm buna bağımlı değil, istenirse öne çekilebilir.

- **Ne çalışır:** paneldeki **Model** dropdown'ı gerçek seçim yapar — birden fazla model kurulur, seçilen modelle üretilir; seçim projeyle kaydedilir. Hangi modellerin ekleneceği bu bölümün ilk kararı.
- **Nasıl görülür:** modeli değiştir, üret → görünür şekilde farklı sonuç; projeyi yeniden aç → seçim durur.

---

## Sıra özeti

| Bölüm | Görülür çıktı | Yeni kazanım |
|---|---|---|
| 6 · Kalıcılık + iz | Yenileyince kutular dolu | ayarlar + foto↔prompt izi |
| 7 · Galeri sıralama | Sürükle-bırak, kalıcı sıra | export sırasının temeli |
| 8 · Export | Tek JSON, galeri sırasında | video hattı beslenebilir |
| 9 · Foto detay | Ayrı sayfa, oklar, prompt | fotoyu gerçekten görme |
| 10 · Silme + onaylar | Toplu foto + proje silme | temizlik, yanlışlıkla kayıp yok |
| 11 · Üretim akışı | Duraklat/devam/iptal, bekliyor kareleri | üretim deneyimi tam |
| 12 · Sağlamlık | Tekrar dene + kaldığı yerden devam | iş kaybı imkânsız |
| 13 · Çoklu model | Model seçimi | içerik çeşitliliği |

## Neden bu sıra

- **Önce temel:** kalıcılık + iz (6) detay sayfasının (9) ve export'un (8) ön şartı; sıralama (7) export sırasını tanımlar.
- **Değer erken:** Bölüm 8'de video hattı beslenebilir hâle gelir — tasarımın asıl hedefi.
- **Yıkıcı işler onaylardan sonra değil, görüntülemeden sonra:** silme (10), detay sayfası (9) ile fotoyu görebilir olduktan sonra gelir.
- **Sağlamlık mutlu yoldan sonra:** duraklat/devam (11) oturmuş akışın üstüne, hata/devam (12) en sona yakın — eski yol haritasıyla aynı ilke.
- **Çoklu model (13) en sonda:** bağımsız ve en büyük iş; sıra onu beklemez, istenirse öne alınır.

## Açık sorular (ilgili bölümün planında karara bağlanır)

- **Varyant üst sınırı** (Bölüm 11): tasarım sınırsız diyor, harf tabanlı adlandırma 26'yla sınırlı.
- **Model listesi** (Bölüm 13): hangi modeller kurulacak.

## Sıradaki adım

Yol haritası onaylanınca **Bölüm 6** (kalıcılık + iz) için detaylı plan yazılıp başlanır.
