# Queen Editor — Colab doğrulama listesi (Bölüm 7-14)

**Tarih:** 2026-08-05 · **Branch:** `feat/queen-editor-v1` · **Son commit:** `22e8af1`
**Kapsam:** Bölüm 7 (arayüz + bağlantı), 9 (sıralama), 10 (Export), 11 (foto detay + tek silme),
12 (seçim modu, toplu silme, proje silme, çıkış onayı), 13 (duraklat/devam/iptal, bekliyor kareleri,
format hatası), 14 (tekrar dene + kaldığı yerden devam).
Bölüm 8 (test altyapısı) Colab'a dokunmaz — doğrulaması `npm test`'tir.

**Önce:** Colab runtime'ını yeniden başlat ki repo bu commit'i klonlasın (notebook her açılışta
klonlar; eski oturum eski `dist/`'i servis eder).

Maddeler sırayla gitmek üzere dizildi: üsttekiler alttakilerin ön şartını hazırlıyor. Bir madde
kırmızıysa **not düş ve devam et** — hepsi tek fix dalgasında kapatılacak.

**Güncelleme (2026-08-08):** canlı kuyruk kararıyla ([v3 yol haritası](2026-08-08-queen-editor-v3-roadmap.md))
**F2-F5 geçersizleşti** (Durdur / Devam et / İptal et kalkıyor) ve **G1-G2 ertelendi** (elle "Kaldığı
yerden devam et"in yerini otomatik devam alacak). Kalan test işi **G3, G4, H1, H2** ve bunlar v3'ün
**son maddesinde**, canlı kuyruğun kendi listesiyle aynı dalgada denenecek.

---

## A · Sıralama (Bölüm 9)

- [x] **A1** Bir kareyi başka bir karenin yerine sürükle → kare oraya yerleşir, **rozet numaraları**
      yeniden dizilir.
- [x] **A2** Sayfayı yenile → **aynı sıra** duruyor.
- [x] **A3** Üret (2-3 kare yeter) → yeni fotoğraflar **en üste** düşüyor, elle kurduğun sıra
      altında bozulmadan duruyor.
- [x] **A4** Sürüklerken hedef hücrede **kesikli mor yuva** görünüyor, sürüklenen kare hafif eğik
      ve gölgeli.

## B · Export (Bölüm 10)

- [x] **B1** App bar'daki **Export** → `<proje>-export.json` iniyor (sayfa değişmiyor).
- [x] **B2** Dosyanın başında projenin **Drive klasör yolu**; ardından fotoğraf–prompt listesi
      **galerideki sırayla**.
- [x] **B3** Hiç fotoğrafı olmayan bir projede Export → dosya yine iniyor, `photos` boş.

## C · Foto detay (Bölüm 11)

- [x] **C1** Bir fotoğrafa tıkla → **ayrı sayfa** açılıyor, adres `/projects/…/photos/…` oluyor.
- [x] **C2** Sayfayı yenile → aynı fotoğrafta kalıyor; tarayıcı geri tuşu → galeriye dönüyor.
- [x] **C3** Dikey / yatay / kare fotoğraflarda görsel **kırpılmıyor**, oranı bozulmuyor.
- [x] **C4** ‹ › okları ve klavye ← → ile geziliyor; **ilk** fotoğrafta sol ok, **son** fotoğrafta
      sağ ok soluk ve tıklanamaz (başa sarmıyor).
- [x] **C5** `Esc` galeriye dönüyor.
- [x] **C6** Sağ sütunda **sıra (3 / 48)**, **dosya adı** ve **prompt** doğru; prompt kutusu uzun
      metinde kaydırılabiliyor.

## D · Silme (Bölüm 11 + 12)

- [x] **D1** Detay sayfasında **Sil** → "Bu fotoğraf silinsin mi?" onayı → onayla → fotoğraf gidiyor
      ve **sonraki** fotoğraf açılıyor (sonuncuysa önceki, hiç kalmadıysa galeri).
- [x] **D2** Galeride bir kareye hover → **sol üstte halka** beliriyor; tıkla → **seçim modu**
      açılıyor ve o kare seçili (mor çerçeve + örtü + ✓).
- [x] **D3** Modda başka karelere tıkla → seçim büyüyor, çubukta sayı güncelleniyor; aynı kareye
      tekrar tıkla → seçimden çıkıyor. Modda tıklamak **detay sayfasını açmıyor**.
- [x] **D4** **Tümünü seç** hepsini seçiyor; ikinci basış seçimi temizliyor (Sil pasifleşiyor).
- [x] **D5** **Sil** → "N fotoğraf silinsin mi?" → onayla → hepsi galeriden ve Drive'dan gidiyor,
      mod kapanıyor.
- [x] **D6** `Esc` ve **Vazgeç** modu kapatıyor.
- [x] **D7** Silmelerden sonra **Üret** → yeni fotoğraflar silinen numaraları **geri kullanmıyor**
      (ör. `3_a.png` silindiyse yeni kare `3_a.png` olmuyor).

## E · Proje silme ve çıkış onayı (Bölüm 12)

- [x] **E1** Proje kartının sağ üstündeki **çöp** → onay kutusu; çöpe basmak projeyi **açmıyor**.
- [x] **E2** Onayla → kart listeden gidiyor, Drive'daki klasör içeriğiyle siliniyor.
- [x] **E3** **Projeden çık** → önce soruyor; Vazgeç ekranda tutuyor, **Çık** projeler ekranına
      döndürüyor.

## F · Üretim akışı (Bölüm 13)

- [x] **F1** Üret → galerinin **başında** kesikli soluk **"bekliyor"** kareleri, önlerinde
      spinner'lı **"Çalışıyor"** karesi; üretildikçe bekleyenler azalıyor.
- [x] **F2** **Durdur** → panel **Devam et / durum kartı / İptal et** görünümüne geçiyor; kuyruk
      duruyor, bekleyen kareler ekranda kalıyor.
- [x] **F3** **Devam et** → kaldığı yerden sürüyor; daha önce üretilenler **tekrar üretilmiyor**.
- [x] **F4** Durakladığın anda render edilen kare, devam edince **aynı numarayla** yeniden üretiliyor
      (yarım dosya kalmıyor).
- [x] **F5** **İptal et** → bekleyen kareler kayboluyor, panel **Üret**'e dönüyor, üretilenler
      duruyor.
- [x] **F6** Duraklatılmışken galeride **sıralama ve silme** çalışıyor; bekleyen kareler
      sürüklenmiyor/seçilmiyor.
- [x] **F7** Bozuk prompt listesi (ör. `["a",` ) → Üret → kutu **kızarıyor**, altında sunucunun
      cümlesi; bir harf yaz → uyarı **temizleniyor**. Liste boşken Üret pasif.

## G · Sağlamlık (Bölüm 14)

- [ ] **G1** Üretim sürerken sekmeyi kapat, projeyi yeniden aç → **"Üretim yarım kaldı — X/Y
      tamamlandı"** kartı + **Kaldığı yerden devam et**; bekleyen kareler galeride.
- [ ] **G2** Devam et → yalnız eksikler üretiliyor.
- [ ] **G3** ComfyUI'ı öldür (veya modeli boz) → üst üste hata → kırmızı **"Üretim durdu — X/Y"**
      kartı, altında **sunucunun kendi teknik satırı**.
- [ ] **G4** Tek bir kare patlarsa galeride **kırmızı kare + Tekrar dene**; üretim durmadan sürüyor;
      Tekrar dene → yalnız o kare üretilip yerine geçiyor.
- [ ] **G5** Yarım işi olmayan projede bu kartların **hiçbiri** görünmüyor, panel normal Üret'i
      gösteriyor.

## H · Bağlantı (Bölüm 7'den kalan tek madde)

- [ ] **H1** Üretim sürerken **runtime'ı tamamen kapat** → en geç ~12 sn içinde ilerleme çubuğu
      **soluklaşıyor** ve kırmızı **"Sunucuya ulaşılamıyor — son bilinen: X/Y"** kartı geliyor
      (donuk çubuk kalmıyor).
- [ ] **H2** Runtime geri gelirse (aynı tünel) ekran kendini toparlıyor, kart kayboluyor.

## I · Genel görünüm (Bölüm 7)

- [x] **I1** Projeler ekranı ve proje ekranı açılırken **ortalanmış dönen gösterge** (kesikli boş
      kutular değil).
- [x] **I2** Üretim sürerken panel alanları **kilitli ve soluk**, galeri serbest.
- [x] **I3** Üretim bitince yeşil **"✓ N / M üretildi — tamamlandı"** kartı.

---

## Bulunan hatalar

Madde numarasıyla yaz (ör. "D3 — modda tıklayınca detay açılıyor"); ekran görüntüsü gerekmiyor,
ne beklediğin ve ne olduğu yeter.

- 
