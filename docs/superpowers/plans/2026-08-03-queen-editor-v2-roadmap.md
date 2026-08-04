# Queen Editor — Yol Haritası v2 (tasarım güncellemesi)

**Tarih:** 2026-08-03 · **Durum:** Bölüm 6 tamam · sırada Bölüm 7
**Tasarım kaynağı:** claude.ai/design projesi `Queen Editor` → `Queen Editor Basit v1.html` + `HANDOFF.md` (kullanıcının güncellediği hâli — davranış kararlarının tamamı orada). Proje linki: <https://claude.ai/design/p/efad1f83-69d3-4e07-89fa-3783839c81c3> — dosyalar repo'ya kopyalanmaz, her ihtiyaçta buradan taze çekilir (DesignSync `get_file`, proje kimliğiyle).
**Şemsiye tasarım:** [2026-08-03-queen-editor-v2-design.md](../specs/2026-08-03-queen-editor-v2-design.md) (davranış kararları) · [2026-07-24-queen-editor-v1-design.md](../specs/2026-07-24-queen-editor-v1-design.md) (mimari kararlar)
**Yerini aldığı doküman:** [2026-07-24-queen-editor-roadmap.md](2026-07-24-queen-editor-roadmap.md) — oradaki Bölüm 6 buradaki Bölüm 6'ya, Bölüm 7 buradaki Bölüm 12+13'e eridi.

**Revizyon (2026-08-03):** Bölüm 7 olarak "Arayüz: tasarımla birebir + akıcı" eklendi, eski 7-13 birer kaydı. Gerekçe: Bölüm 6 Colab'da doğrulanırken arayüzün üç ayrı yerde tasarımdan saptığı ve hiçbir beklemenin ekranda karşılığı olmadığı görüldü. Buraya taşınanlar: panel kilidi (eski 11), boş projeler ekranındaki "İlk projeyi oluştur" ve "Projeden çık"ın nötr rengi (eski 10 — onay sorma orada kaldı).

Tek kaynak: bütün bölümlerin dökümü burada. İlke aynı — **önce çalıştır, sonra sağlamlaştır**; her bölüm bir öncekinin üstüne birikir, hiçbirinin çıktısı çöpe gitmez. Her bölüm çıktı odaklı (**ne çalışır** + **nasıl görülür**) ve Colab'da tek başına "evet oldu" denerek kapanır. Sırası gelen bölümün detaylı planı ve o bölümü ilgilendiren kararlar o an netleşir.

**Kapsam sınırı:** Video üretiminin kendisi bu yol haritasının dışında — sınır Export dosyası (Bölüm 8). Tasarımın kapsam dışı listesi aynen geçerli: bağlantı çubuğu · foto sayısı / kapak · yeniden adlandırma · referans görsel.

---

## Tamamlanan bölümler (1-6)

Her biri Colab'da doğrulandı:

| Bölüm | Görülür çıktı |
|---|---|
| 1 · Repo çekimi | Private repo token'la Colab'a klonlanır |
| 2 · Bağlantı | Sunucu + tünel; sayfa açılır, "sunucuya bağlı ✓" |
| 3 · Proje | Proje oluşturma; Drive'da klasör; kart listesi |
| 4 · Tek foto | ComfyUI ile tek prompt → tek foto |
| 5 · Çoklu foto | Prompt listesi × varyant → galeri; Durdur; numaralar kaldığı yerden |
| 6 · Kalıcılık + iz | Yenileyince kutular dolu; her fotonun prompt/negatif/seed izi Drive'da |

---

## Bölüm 7 — Arayüz: tasarımla birebir + akıcı

Tasarımın kâğıt üstünde kalmış kısmı ekrana iner; her bekleme ekranda karşılık bulur. Yeni özellik yok — var olan her şey tasarımdaki hâline çekilir.

- **Ne çalışır:**
  - **Eleman denetimi:** beş ekranın (projeler · boş projeler · proje + panel · galeri · yeni proje kutusu) her elemanı tasarımla tek tek karşılaştırılır, sapan eleman tasarıma çekilir. Envanter spec'te tablo hâlinde durur; uygulama o tabloyu satır satır kapatır. Bilinen sapmalar: panel hiç kilitlenmiyor, "Projeden çık" kırmızı (tasarımda nötr), boş projeler ekranında "İlk projeyi oluştur" butonu yok, Durdur küçük buton (tasarımda kartın üstünde tam genişlik), bitiş için yeşil "✓ tamamlandı" kartı yok.
  - **Geri bildirim:** projeler ve fotoğraflar gelirken ekran boş kalmaz; basılan her buton anında durum değiştirir; üretim sürerken panel alanları kilitli ve soluk (`wf-panel--locked`), galeri serbest kalır.
  - **Durdur anında durur:** basıldığı an panel tepki verir **ve** süren kare ComfyUI'da kesilir — yarım kare kaydedilmez, numarası planda ayrılmış kalır. (Duraklat / Devam et / İptal et ayrımı Bölüm 12'de gelir; burada Durdur hâlâ "bitir".)
  - **Hata gösterimi tek desen:** alan hatası (kırmızı çerçeve + altında tek satır) ve durum hatası (kırmızı çerçeveli-zeminli kart + uyarı ikonu + tek cümle + küçük teknik satır). Her hata bu ikisinden biri; şu an üç ekranda üç ayrı biçim var.
- **Nasıl görülür:** projeye gir → fotoğraflar gelene kadar ekran dolu; Üret → panel kilitlenir; Durdur → saniyeler içinde durur, dakikalarca değil; sunucuyu kapat → hata her ekranda aynı biçimde çıkar.
- **Yok:** küçük resim (thumbnail) üretimi; yeni ekran; Bölüm 12'nin duraklat/devam akışı.

## Bölüm 8 — Galeri sıralama

Export sırasının temeli: kullanıcının elle kurduğu sıra.

- **Ne çalışır:** her karede sıra numarası rozeti; basılı tut + sürükle → kare taşınır, numaralar güncellenir; sıra kalıcı; yeni üretilen fotolar elle sıralanmış galerinin en üstüne düşer.
- **Nasıl görülür:** sırala → sayfayı yenile → sıra durur; tekrar Üret → yeniler en üstte, eski sıra bozulmaz.
- **Yok:** export (Bölüm 9), silmede numara davranışı (Bölüm 11).

## Bölüm 9 — Export

Video hattını açan çıktı: bütün projeyi anlatan tek dosya.

- **Ne çalışır:** app bar'daki **Export** → tek JSON iner: en başta projenin Drive klasör yolu, ardından tüm fotoların dosya adı + prompt listesi, **galerideki güncel sırayla**. Export her zaman aktif — üretim sürerken ve hiç foto yokken de basılabilir.
- **Nasıl görülür:** dosyayı indir, aç → sıra galeriyle birebir; video bu sırayla uç uca eklenecek şekilde beslenebilir.
- **Yok:** video üretimi (kapsam dışı, başka araç).

## Bölüm 10 — Foto detay sayfası

Fotoyu gerçekten görmenin yolu; ham dosya sekmesinin yerini alır.

- **Ne çalışır:** fotoya tıkla → ayrı sayfa: foto olabildiğince büyük, **orijinal oranında** (dikey/yatay/kare, kırpılmaz); ‹ › okları foto alanının iki ucunda sabit, ilk/son fotoda pasif, başa sarmaz; klavye ← → gezer, Esc galeriye döner; sağda sıra ("3 / 48"), dosya adı ve prompt metni (kutu her zaman kaydırmalı); **Sil** → onay → sonraki foto açılır (son fotoysa önceki, hiç kalmadıysa galeri).
- **Nasıl görülür:** farklı oranlı fotolar arasında gez, birini sil, galeriye dön.
- **Yok:** toplu silme (Bölüm 11).

## Bölüm 11 — Silme + onaylar

Yıkıcı işlemlerin tamamı, hepsi onaylı.

- **Ne çalışır:** seçim modu — hover'da beliren ✓ ile açılır, seçili kare mor çerçeveli, altta yüzen bar ("3 seçili · Tümünü seç · Sil · Vazgeç"), Sil onay ister, silme kalıcıdır (Drive'dan da gider); proje silme — karttaki kırmızı çöp + onay, klasör içeriğiyle silinir; **Projeden çık** onay sorar (rengi Bölüm 7'de nötre çekildi).
- **Nasıl görülür:** 3 foto seç-sil → galeriden ve Drive'dan gider, sıra numaraları güncellenir; proje sil → kart ve klasör gider.

## Bölüm 12 — Üretim akışı

Üretim deneyimi tasarımdaki son hâline gelir; yeni ekran yok.

- **Ne çalışır:** **Durdur = duraklat** — üstte Devam et (kaldığı yerden), altta İptal et (kalan kuyruk atılır, üretilenler kalır); üretim başlayınca galeriye planlanan tüm kareler düşer — gelmemişler kesikli "bekliyor", o an üretilen "yükleniyor"; format kontrolü Üret'e basınca — bozuk listede kırmızı çerçeve + "Format hatası", yazmaya başlayınca temizlenir, boş listede Üret pasif.
- **Nasıl görülür:** Durdur → Devam et → kaldığı yerden sürer; İptal → üretilenler durur, panel hazıra döner; bozuk liste yapıştır → kırmızı uyarı, üretim başlamaz.
- **Karar (2026-08-04, Bölüm 7 denetiminde bağlandı):** varyant üst sınırı 26 kalır — harf tabanlı adlandırma backend gerçeği; kutu `max=26` ile sınırlar, HANDOFF'un "sınır yok" cümlesinden bilinçli sapma.
- **Yok:** panel kilidi, anında Durdur ve bitiş kartı (Bölüm 7); tekil kare hatası ve ölümcül durma (Bölüm 13).

## Bölüm 13 — Sağlamlık

v1 davranışlarının tam hâli: hiçbir senaryoda iş kaybı yok.

- **Ne çalışır:** tekil kare patlarsa kırmızı kare + **Tekrar dene** (sadece o kareyi üretir), üretim sıradakiyle sürer, ilerleme kartında "N fotoğraf üretilemedi" satırı; bağlantı kopması / servis ölümü / üst üste hatalar → kırmızı "Üretim durdu" kartı + kısa teknik neden + **Kaldığı yerden devam et** (yalnız eksikler üretilir); sekme kapansa, bilgisayar kapansa, Colab oturumu ölse bile proje yeniden açılınca aynı kart görünür ve tek tıkla sürer.
- **Nasıl görülür:** ComfyUI'ı öldür → hata kartı; runtime'ı yeniden başlat → devam kartı, yalnız eksikler üretilir.

## Bölüm 14 — Çoklu model

Bağımsız en büyük iş; hiçbir bölüm buna bağımlı değil, istenirse öne çekilebilir.

- **Ne çalışır:** paneldeki **Model** dropdown'ı gerçek seçim yapar — birden fazla model kurulur, seçilen modelle üretilir; seçim projeyle kaydedilir. Hangi modellerin ekleneceği bu bölümün ilk kararı.
- **Nasıl görülür:** modeli değiştir, üret → görünür şekilde farklı sonuç; projeyi yeniden aç → seçim durur.

---

## Sıra özeti

| Bölüm | Görülür çıktı | Yeni kazanım |
|---|---|---|
| 7 · Arayüz: birebir + akıcı | Kilitli panel, anında Durdur, tek tip hata | ekran tasarımla aynı, bekleme görünür |
| 8 · Galeri sıralama | Sürükle-bırak, kalıcı sıra | export sırasının temeli |
| 9 · Export | Tek JSON, galeri sırasında | video hattı beslenebilir |
| 10 · Foto detay | Ayrı sayfa, oklar, prompt | fotoyu gerçekten görme |
| 11 · Silme + onaylar | Toplu foto + proje silme | temizlik, yanlışlıkla kayıp yok |
| 12 · Üretim akışı | Duraklat/devam/iptal, bekliyor kareleri | üretim deneyimi tam |
| 13 · Sağlamlık | Tekrar dene + kaldığı yerden devam | iş kaybı imkânsız |
| 14 · Çoklu model | Model seçimi | içerik çeşitliliği |

## Neden bu sıra

- **Önce zemin:** arayüz denetimi (7) sıranın başında, çünkü sonraki her bölüm (rozet, seçim çubuğu, detay sayfası) bu zeminin üstüne eleman ekliyor — zemin sapmışken eklenen her eleman sapmayı büyütür ve iki kere düzeltilir.
- **Önce temel:** kalıcılık + iz (6) detay sayfasının (10) ve export'un (9) ön şartı; sıralama (8) export sırasını tanımlar.
- **Değer erken:** Bölüm 9'da video hattı beslenebilir hâle gelir — tasarımın asıl hedefi.
- **Yıkıcı işler görüntülemeden sonra:** silme (11), detay sayfası (10) ile fotoyu görebilir olduktan sonra gelir.
- **Sağlamlık mutlu yoldan sonra:** duraklat/devam (12) oturmuş akışın üstüne, hata/devam (13) en sona yakın — eski yol haritasıyla aynı ilke.
- **Çoklu model (14) en sonda:** bağımsız ve en büyük iş; sıra onu beklemez, istenirse öne alınır.

## Açık sorular (ilgili bölümün planında karara bağlanır)

- **Model listesi** (Bölüm 14): hangi modeller kurulacak.
- ~~Varyant üst sınırı~~ — 2026-08-04'te karara bağlandı: 26 kalır (Bölüm 12'deki karar notu).

## Sıradaki adım

**Bölüm 7** (arayüz: tasarımla birebir + akıcı) için spec yazılır. Spec'in gövdesi eleman envanteri: ekran · eleman · tasarımdaki hâli · bizdeki hâli · fark. Envanter tasarım kaynağı (`Queen Editor Basit v1.html`) tek tek okunarak çıkarılır.
