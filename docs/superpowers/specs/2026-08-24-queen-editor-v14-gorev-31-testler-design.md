# v14 Görev 31 — Galeri gerekmeyen bir cevabı beklemez: TEST döngüsü tasarımı

**Tarih:** 2026-08-24 · **Kaynak:** Colab turu, aynı gün · kullanıcı kuralı
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 31

## Sorun

Bir kareye girip geri dönüldüğünde kartların yerinde tek bir yükleniyor işareti çıkıyor. Sebep:
adres bir kareyi gösterdiğinde proje ekranı tamamen sökülüyor, geri dönüşte sıfırdan kuruluyor, ve
kurulurken **proje kaydı** gelene kadar ekranın tamamı — galerisi, başlığı, sağdaki rayı — tek bir
dönen halkaya iniyor.

O kaydın ekrandaki tek müşterisi **fotoğraf üret paneli**: prompt listesi, negatif, varyant sayısı
ve model kutularını dolduruyor. Galeri onu almıyor bile.

Yani bir metin kutusunun içeriği için kırk sekiz fotoğraflık galeri bekletiliyor.

**Bu yalnız geri dönüşün derdi değil.** Aynı boşluk projeye ilk girişte de var; geri dönüş onu
görünür kıldı çünkü orada alınan bir şey var.

## Kullanıcının kuralı

> *"Yüklenmesi ve güncellenmesi gereken bir şey varsa yüklenebilir, sorun yok — ama her biri kendi
> parçasını güncellesin. Kartı etkileyen bir şey yoksa orası etkilenmesin."*

Bu maddenin tamamı bu cümlenin ilk yarısı. İkinci yarısı — *"zaten veri varsa sessiz yapılsın"* —
32. maddedir ve buraya karışmıyor: 31 bekleyişi **taşır**, 32 onu **kaldırır**.

## Kararlaştırılan yer

Bekleyiş, cevabı isteyen panelin kendi sütununa iner.

| Ne | Bugün | Yarın |
|---|---|---|
| Galeri, başlık, ray | Kayıt gelene kadar yok | Anında |
| Diğer beş panel | Kayıt gelene kadar açılamıyor | Anında |
| Fotoğraf üret paneli | Kayıt gelene kadar yok | Kendi sütununda yükleniyor |
| Kayıt okunamazsa | Tam ekran hata kartı | Aynı kart, o panelin içinde |

`ProjectLoading` ekranı ortadan kalkar — kimsenin çağırmadığı bir dosya kalmaz.

## Bir şey bilerek değişmiyor

Fotoğraf üret paneli kutularını **açılışında bir kez** dolduruyor ve bu, yazarken üstüne
yazılmamasının tek sebebi. Panel bundan sonra da kayıt geldikten sonra doğar — yalnız boş bir ekranın
arkasında değil, yaşayan bir ekranın içinde. Sözleşme aynı kalıyor, kimse sonradan senkron
edilmiyor.

## Sabitlenecek davranış

| # | Ne | Nerede görülür |
|---|---|---|
| **B1** | Kayıt beklenirken galeri ekranda | `App.test.jsx` |
| **B2** | Kayıt beklenirken proje başlığı ve ray ekranda — yani ekran tek bir halkaya inmiyor | `App.test.jsx` |
| **B3** | Kayıt okunamazsa hata kartı ekranı kaplamıyor, galeri yerinde duruyor | `App.test.jsx` |
| **B4** | Kayıt beklenirken fotoğraf üret paneli kendi sütununda yükleniyor diyor | `SidePanel.test.jsx` |
| **B5** | Kayıt beklenirken diğer paneller açılıp çalışıyor | `SidePanel.test.jsx` |
| **B6** | Kayıt geldiğinde form kutuları dolu geliyor | `SidePanel.test.jsx` |
| **B7** | Kayıt okunamazsa panelin içinde hata kartı ve tekrar deneme yolu var | `SidePanel.test.jsx` |

B1–B3 ekranın bölünmediğini söylüyor, B4–B7 bekleyişin nereye indiğini. İkisi ayrı dosyada çünkü
ayrı sorular: biri *"ekran bölündü mü"*, öteki *"bölünen parça ne diyor"*.

## Nerede duracak

**Yeni dosya:** `frontend/src/App.test.jsx`. Bugün yok — `App.jsx`'in hiç testi yok, ve bu maddenin
asıl davranışı orada yaşıyor. Adres bir projeyi gösterdiğinde ekranın ne olduğu başka hiçbir yerden
görülemiyor.

**Mevcut dosya:** `frontend/src/features/photo_generation/SidePanel.test.jsx`. Panelin ne çizdiği
zaten bu dosyanın konusu.

## Kapsam dışı

- **Hatırlama yok.** Kayıt her mount'ta yeniden isteniyor; onu susturmak 32. madde.
- **Kuyruk paneli düzeltilmiyor.** İlk cevap gelmeden "kuyruk boş" demesi 33. madde; bu döngüde
  olduğu gibi kalıyor ve buranın testleri ona hiç bakmıyor.
- **Açık panel ve seçim hatırlanmıyor.** 34. madde.
- **Kayıt sözleşmesi değişmiyor.** Sunucu tarafına, dosya biçimine, ne zaman yazıldığına
  dokunulmuyor.
- **Kod bu döngüde değişmiyor.** Testler kırmızı bırakılır.
