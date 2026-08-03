# Queen Editor — v2 (tasarım güncellemesi, şemsiye spec)

**Tarih:** 2026-08-03 · **Durum:** onay bekliyor
**Kaynak:** claude.ai/design projesi `Queen Editor` → `Queen Editor Basit v1.html` + `HANDOFF.md` (kullanıcının güncellediği hâl; brief + 19 ekran artboard'u)
**İlişki:** [2026-07-24 şemsiye spec'in](2026-07-24-queen-editor-v1-design.md) üstüne gelir — oradaki mimari kararlar (feature-first, servis sınırları, Flask, Vite+dist, Drive düzeni, node id'leri, numaralandırma, seed) **aynen geçerli**; bu spec yalnız tasarımın getirdiği davranış kararlarını ekler ve eskiyenleri düzeltir.
**Plan:** [2026-08-03-queen-editor-v2-roadmap.md](../plans/2026-08-03-queen-editor-v2-roadmap.md) (Bölüm 6-13)

## Amaç

Kullanıcı tasarım projesini elden geçirdi: iki ekranlık "mutlu yol" arayüzü, fotoğrafın
görüntülenmesini, sıralanmasını, silinmesini, dışa aktarılmasını ve üretimin duraklatılmasını
kapsayan tam bir ürüne genişledi. Bu spec o kararları repoya taşır; davranışın ayrıntılı anlatımı
tasarım projesindeki `HANDOFF.md`'dedir, çelişki olursa bu spec kazanır.

## Eski spec'te geçersizleşenler

| Eski karar | Yeni karar |
|---|---|
| Proje silme **kapsam dışı** | Kapsamda: karttaki çöp ikonu + onay; klasör içeriğiyle silinir (Bölüm 10) |
| Motor seçimi **kapsam dışı** | Kapsamda: **gerçek çoklu model** — birden fazla model kurulur, panelden seçilir, seçim projeyle kaydedilir; model listesi Bölüm 13'ün ilk kararı (kullanıcı kararı, 2026-08-03) |
| Fotoğrafa tıkla → **yeni sekmede** açılır | **Foto detay ayrı sayfası** (aşağıda) |
| Durdur → üretim **durdurulur** | **Durdur = duraklat**: Devam et / İptal et ayrımı (aşağıda) |
| Varyant 1–26 | Tasarım "üst sınır yok" diyor; harf tabanlı adlandırmayla çelişiyor — **açık soru**, Bölüm 11'de karara bağlanır |

## Ekran seti

İki değil **üç görünüm**: Projeler · Proje · **Foto detay** (projeden açılan alt sayfa — modal değil,
kendi adresi olan sayfa). Ortak app bar üçünde de aynı: solda marka, ortada bulunulan yerin adı,
sağda o ekranın aksiyonları.

## Yeni davranış kararları

### Projeler ekranı

- Kart sade kalır (ad + son değiştirilme); kapak/foto sayısı bilinçli yok.
- Her kartta sürekli görünür kırmızı çöp ikonu → onay penceresi ("içindeki tüm fotoğraflar kalıcı
  olarak silinir") → proje klasörüyle silinir.
- Boş durumda "İlk projeyi oluştur" butonu (Yeni proje ile aynı pencere).
- Yeniden adlandırma bu sürümde de yok.

### Proje ekranı — sağ panel

- **Model** açılır listesi panelin en üstünde; üretimde kullanılacak model burada seçilir.
- **Üret** → üretim başlarken tüm panel alanları (model, prompt listesi, negatif, varyant)
  **kilitlenir** ve soluk görünür; üretim bitene ya da iptal edilene kadar öyle kalır. Galeri ise
  üretim boyunca **tamamen serbest**: detay, silme, sıralama çalışır.
- Bütün üretim durumları aynı kalıbı kullanır: üstte ana buton boyutunda tek buton, altında durum
  kartı.
  - **Sürüyor:** üstte nötr/soluk **Durdur**, altta ilerleme kartı (sayaç + çubuk + "şimdi: …").
  - **Duraklatıldı** (Durdur'a basılınca): üstte mor **Devam et** (kaldığı yerden), altta nötr kart,
    en altta soluk **İptal et** — kalan kuyruk atılır, üretilenler kalır, panel hazıra döner.
  - **Durdu** (ölümcül hata / oturum ölümü): üstte **Kaldığı yerden devam et**, altta kırmızı kart +
    kısa teknik neden (ham hata metni).
  - **Bitti:** panel hazıra döner + Üret'in altında kalıcı yeşil bildirim ("✓ 48/48 üretildi");
    yeni üretim başlayınca kaybolur. Hatalı karelerle bitişte özel tasarım yok — bildirim gelir,
    kırmızı kareler tek tek Tekrar dene ile üretilir.
- **Format kontrolü Üret'e basınca:** liste okunamıyorsa üretim başlamaz — kutu çerçevesi kırmızı +
  "Format hatası" (detay verilmez); yazmaya başlayınca temizlenir. Liste boşken Üret pasif (hata
  durumu değil).
- App bar: **Export** (ikincil, her zaman aktif — üretim sürerken ve foto yokken de) + **Projeden
  çık** (nötr renk — kırmızı silmeye ayrıldı; onay sorar).

### Proje ekranı — galeri

- Her karenin sağ üst köşesinde **sıra numarası rozeti**; numara galerideki güncel konumdur.
- **Tıklama ayrımı:** tıkla → foto detay · basılı tut + sürükle → sıralama · hover'da beliren ✓ →
  seçim modu.
- **Sıralama elle değiştirilebilir** ve projeyle birlikte kalıcıdır; bu sıra aynı zamanda **export
  listesinin sırasıdır**. Yeni üretilen fotolar elle sıralanmış galerinin **en üstüne** eklenir.
- **Seçim modu:** seçili kare mor çerçeve + tik; altta yüzen bar "N seçili · Tümünü seç · Sil ·
  Vazgeç"; Sil onay ister; silme kalıcıdır (depodan da). Liste sonuna ekstra boşluk — son satır
  barın üstünde tam görünür. Esc çıkar.
- Üretim başlayınca planlanan **tüm kareler** galeriye düşer: gelmemişler kesikli "bekliyor", o an
  üretilen "yükleniyor", patlayanlar kırmızı.

### Foto detay sayfası

- Foto olabildiğince büyük, **orijinal oranında** (galeri kareleri kare kırpılır, burada kırpılmaz).
- ‹ › okları foto alanının iki ucunda **sabit** (fotonun üstünde değil); ilk fotoda sol, son fotoda
  sağ ok pasif — **başa sarmaz**. Klavye ← → gezer, Esc galeriye döner. Gezinme sırası = galeri
  sırası.
- Sağ panel: sıra ("3 / 48"), dosya adı, prompt metni — prompt kutusu **her zaman kaydırmalı**,
  "tamamını göster" mekanizması yok.
- **Sil** aynı onay penceresini kullanır; silinince **sonraki foto** açılır (son fotoysa önceki,
  hiç kalmadıysa galeri).

### Export (JSON)

Basınca anında tek JSON iner — bütün projeyi kapsar; başka bir kodun fotoları bulup
eşleştirebilmesi için:

```json
{
  "folder": "queenEditor/düğün/",
  "photos": [
    { "file": "0_a.png", "prompt": "kraliçe tahtta oturuyor, altın taç" }
  ]
}
```

- En başta projenin Drive klasör yolu, ardından dosya adı + prompt listesi.
- **Sıra = galerideki güncel sıra** (dosya adı sırası değil). Sonraki adımda video bu listeden bu
  sırayla uç uca üretilecek — video üretiminin kendisi **bu kapsamın dışında**, sınır bu dosya.

### Sağlamlık (eski spec'le aynı, tasarım doğruladı)

Tekil kare → kırmızı + Tekrar dene (aynı ad, yeni seed), üretim sürer · altyapı hatası / üst üste 3
hata → durur, Kaldığı yerden devam et yalnız eksikleri üretir · sekme/bilgisayar/Colab oturumu
kapansa bile proje açılışında yarım üretim algılanır, aynı kartla sürdürülür · hiçbir senaryoda iş
kaybı yok. Aynı projenin iki sekmede açılması v1'de yok sayılır.

## Açık sorular

- **Varyant üst sınırı** (Bölüm 11'de): tasarım sınırsız, harf tabanlı adlandırma 26 ile sınırlı.
- **Model listesi** (Bölüm 13'te): hangi modeller kurulacak, kurulum süresine etkisi.

## Kapsam dışı (v2)

Video üretimi (sınır: Export) · bağlantı durumu çubuğu · foto sayısı / kapak görseli · yeniden
adlandırma · referans görsel · iki sekme senkronu · kimlik doğrulama · çoklu kullanıcı.
