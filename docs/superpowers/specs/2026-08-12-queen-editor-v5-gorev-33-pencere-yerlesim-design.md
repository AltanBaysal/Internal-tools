# Görev 33 — Pencere ve yerleşim cilası

**Maddeler:** 105, 107, 108
**Roadmap:** [v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) · Blok 9
**Fark belgesi:** [v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)

## Sorun

Üç ayrı ölçü hatası, üçü de v5'in son geçişine bırakılmıştı.

- Onay pencerelerinin hepsi tek genişlikte açılıyor. Kısa metin ortada kayboluyor, uzun metin dört
  satıra bölünüyor; tasarım her pencereye kendi genişliğini veriyor.
- Uygulama açılışta yatayda kayıyor: cihaz ekranından geniş çiziliyor ve alta bir kaydırma çubuğu
  düşüyor *(kullanıcının elle bulgusu)*.
- Seçim barı ekranın en dibine yapışık duruyor; yüzmesi gerekiyor *(yine elle bulgu)*.

## Kararlar

1. **Her onay penceresi tasarımın verdiği genişlikte açılır** *(madde 105)*:

   | Pencere | Genişlik |
   |---|---|
   | Kare silme (detay ekranı ve yalnız-üretilmiş seçim) | 320 *(varsayılan)* |
   | Proje silme | 340 |
   | Kurulum ve kurulum iptali | 360 |
   | Kuyruk boşaltma | 380 |
   | Export çıkış onayı | 380 |
   | Yeni proje | 400 |
   | Bekleyen çıkarma | 400 |
   | Karışık silme | 420 |

2. **Katman silme pencereleri 400'de kalır.** Madde 105 onları saymıyor; genişlikleri madde 80'in
   kendi kararı (kalanı anlatan cümle 320'ye sığmıyor) ve o karar hâlâ geçerli.
3. **Yeni proje kutusu 380'den 400'e çıkar.** Tek listelenmemiş sapma buydu; kendi bileşeni olduğu
   için `ConfirmModal`'ın varsayılanından değil, kendi stilinden alıyor.
4. **Yatay taşma iki katmanda birden kapatılır** *(madde 107)*. Yalnız gizlemek yanlış olur:
   gizlenen içerik ulaşılamaz hâle gelir. O yüzden önce **itenler** düzeltilir — sabit genişlikli
   yan panelde ve galeri karolarında bölünemeyen uzun metinler (model dosya adları, prompt'lar,
   hata satırları, dosya adları) kutularını dışarı itmesin diye kırılır ve `min-width: 0` ile
   ızgara/esnek kutuların "içeriğim kadar geniş olurum" varsayılanı kaldırılır — sonra belge
   düzeyinde bir güvence konur: pencere yatayda kaymaz.
5. **Güvence `app.css`'e yazılır, `vendor/styles.css`'e değil.** Vendor dosyası elle
   düzenlenmiyor; düzeltmelerin yeri uygulamanın kendi sayfası.
6. **Seçim barı alt kenardan 28 piksel yukarıda yüzer** *(madde 108)*. Bugün 20; kartın gölgesiyle
   birlikte bu, ekranın dibine yapışmış gibi okunuyor. Barın kapladığı yer galeri altındaki
   boşluktan düşülmeye devam eder, böylece son sıra barın altında kalmaz.
7. **Yatay taşmanın testi yok.** jsdom yerleşim hesaplamıyor: genişlik, taşma ve kaydırma çubuğu
   orada ölçülemez. Ölçülebilen şey pencere genişlikleri ve barın konumu; taşma, kullanıcının
   Colab geçişinde görülecek. Bunu saklamak yerine yazıyoruz.

## Ne değişiyor

| Yer | Bugün | Yarın |
|---|---|---|
| Kuyruk boşaltma onayı | 320 | 380 |
| Bekleyen çıkarma onayı | 320 | 400 |
| Karışık silme onayı | 320 | 420 |
| Kurulum / iptal onayları | 320 | 360 |
| Yeni proje | 380 | 400 |
| Export çıkış onayı | 400 | 380 |
| Yan panel ve karo metinleri | uzun sözcük kutuyu iter | kırılır, kutu yerinde kalır |
| Belge | yatayda kayabilir | kaymaz |
| Seçim barı | dipten 20px | dipten 28px |

## Testler

- `QueuePanel.test.jsx`, `Gallery.test.jsx`, `ProducersPanel.test.jsx`,
  `NewProjectModal.test.jsx`, `ExportScreen.test.jsx` — her pencere kendi genişliğinde açılır.
  Ölçüm pencerenin kartından okunur (`style.width`).
- `Gallery.test.jsx` — seçim barının rayı alt kenardan 28 piksel yukarıda.
- Yatay taşma için test yok *(karar 7)*.

## Öz eleştiri

- *`overflow-x: hidden` bir maskeleme değil mi?* — Tek başına olsaydı öyle olurdu. Karar 4 önce
  iten metinleri kırıyor; güvence, gözden kaçan bir yeni bileşenin pencereyi kaydırmasını
  engelleyen ikinci sıra. İkisi ayrı ayrı değil, birlikte anlamlı.
- *28 piksel nereden geliyor?* — Tasarım bir sayı vermiyor, kullanıcı "boşlukla ayrılsın" diyor.
  20'nin yetmediği elle görüldü; 28, kartın gölgesi bittikten sonra da boşluk bırakan ilk değer.
  Sayı bir tercih ve öyle yazılıyor, ölçülmüş bir sabit gibi değil.
- *Genişlikler bileşene mi gömülmeli?* — Hayır. Genişlik pencerenin metnine ait, metin de onu açan
  ekrana; `ConfirmModal` yalnız varsayılanı (320) taşır, gerisini çağıran söyler. Aksi hâlde ortak
  bileşen sekiz ekranın metnini bilmek zorunda kalırdı.
