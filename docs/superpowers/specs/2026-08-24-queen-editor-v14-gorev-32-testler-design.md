# v14 Görev 32 — Elde cevap varken gösterge yanmaz: TEST döngüsü tasarımı

**Tarih:** 2026-08-24 · **Kaynak:** kullanıcı kuralı, Colab turu
**Öncesi:** [Görev 31 uygulama spec'i](2026-08-24-queen-editor-v14-gorev-31-uygulama-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 32

## Sorun

31 bekleyişi tüm ekrandan tek bir sütuna indirdi. Ama bekleyiş hâlâ orada: bir kareden her
dönüşte proje kaydı, model listesi ve üretici listesi yeniden isteniyor, ve üçü de "henüz
bilmiyorum" hâlinden geçiyor. Ekranda görünen:

- fotoğraf panelinde bir halka,
- model kutusunda `yükleniyor…`,
- üretici satırlarının ve kurulum notlarının bir an yok olması.

Elde geçerli cevap varken.

## Kullanıcının kuralı

> *"Kartlarda güncelleme lazımsa ve zaten veri varsa sessiz yapılsın, çünkü aktif kartları
> göremiyoruz."*

## Zaten üç kez yapılmış

Bu fikir uygulamada yeni değil, eksik: kare listesi (`REMEMBERED`), ekrana gelmiş fotoğraflar
(`shownPictures`) ve galeri kaydırması (`KEPT`) bir ziyaret boyunca hatırlanıyor. Üç yeni depo aynı
kalıbı tamamlıyor.

**Ziyaret boyunca, koşu boyunca değil.** Hepsi bellekte durur; sayfa yenilenince her şey ilk günkü
gibi sorulur. Depoların ikisi makineye ait olduğu için proje anahtarı taşımaz; kayıt projeye ait
olduğu için taşır.

## Kural: hatırlanan bir cevap boşaltılmaz

Elde bir cevap varken tazeleme başarısız olursa **ekranda hiçbir şey değişmez.** Sebep: tazelemenin
düşmesi kullanıcının bir kaybı değil, ve ekranı boşaltmak sessizliğin tam tersi olurdu.

Bu, bağlantı koptuğunda kimsenin haberi olmaması demek değil: tünel öldüğünde durum yoklaması
zaten hata veriyor ve panel onu kendi kartında söylüyor. İki ayrı kanal aynı şeyi iki kez
söylemiyor.

**İlk cevap bu kuralın dışında.** Hiçbir şey hatırlanmıyorken bir istek düşerse bugünkü davranış
aynen sürer — model listesi boşa düşer ve sebebini yazar, üretici listesi hata kartını gösterir,
kayıt panelinde hata kartı çıkar.

## Testlerin çakıştığı yer, ve neden bu bir kusur değil

`useModels.test.jsx` ve `useProducers.test.jsx`'in "istek düştü" testleri bugün **hiçbir şey
hatırlanmadığı** varsayımıyla yazılmış. Depo modül seviyesinde durduğu için aynı dosyadaki önceki
bir test onu doldurabiliyor, ve o testler sonraki testin başlangıcını değiştiriyor.

Bu, hatırlamanın kendi doğası: **gerçekten kalıcı bir durum eklendi.** İki dosya her testine temiz
bir modül vererek bunu kabul ediyor — testin bağımsızlığı, davranışı test için eğmeden korunuyor.

`useProjectSettings` bu ceremonyaya girmiyor: onun deposu proje anahtarlı, ve `REMEMBERED`'ın
testlerinin yaptığı gibi her test kendine ait bir proje adı isteyerek temiz başlıyor.

## Sabitlenecek davranış

| # | Ne | Nerede |
|---|---|---|
| **B1** | Aynı projeye ikinci kez bakan biri kaydı beklemeden hazır bulur | `useProjectSettings.test.jsx` |
| **B2** | Başka bir proje hâlâ beklemekle başlar — hatırlanan, o projenin kendi cevabı | `useProjectSettings.test.jsx` *(tutucu)* |
| **B3** | Hatırlanan kayıt arkada tazelenir; yeni cevap gelince yerini alır | `useProjectSettings.test.jsx` |
| **B4** | Tazeleme düşerse hatırlanan kayıt ekranda kalır | `useProjectSettings.test.jsx` |
| **B5** | İkinci mount model listesini beklemeden bulur | `useModels.test.jsx` |
| **B6** | Tazeleme düşerse hatırlanan model listesi durur | `useModels.test.jsx` |
| **B7** | İkinci mount üretici satırlarını beklemeden bulur | `useProducers.test.jsx` |
| **B8** | Hatırlanan satırlar `install()`'ın yazdığı notu da taşır | `useProducers.test.jsx` |

B8 kolay kaçırılan yarısı: `install()` satırların üstüne yazıyor, dolayısıyla hatırlanan şey ilk
cevap değil **o anki hâl** olmalı. `REMEMBERED` bunu state'i izleyen bir effect ile çözüyor; buradaki
iki depo da öyle çözmeli, yoksa hatırlanan liste kullanıcının bir saniye önce gördüğünden eski olur.

**B2 bugün de yeşil, ve öyle kalmalı.** Kırmızıya düşmüyor çünkü bugün hiçbir şey hatırlanmadığı için
her mount zaten beklemekle başlıyor. Yazılma sebebi başka: kaydı **tek yuvalı** bir depoya koyan
uygulama — makinenin listeleri gibi — bu testi kırar. Bir projenin cevabını başka bir projeye
göstermeyi engelleyen tek şey o.

## Nerede duracak

Üç mevcut hook test dosyası. Yeni dosya yok — üç deponun her biri zaten testi olan bir hook'un
içinde doğuyor.

`useModels.test.jsx` ve `useProducers.test.jsx` ayrıca temiz modül düzenine geçiyor: `vi.resetModules()`
ve her testin başında dinamik `import`. Mevcut testlerin **cümleleri değişmiyor**, yalnız
başlangıçlarının gerçekten temiz olduğu garanti altına alınıyor.

## Kapsam dışı

- **Kuyruk paneli** — 33. madde.
- **Açık panel ve seçim** — 34. madde.
- **Ekranın bölünmemesi** — 31'de bitti, buradaki testler ona hiç bakmıyor.
- **Sunucu tarafı** hiç açılmıyor; ne sıklıkta sorulduğu da değişmiyor. Değişen tek şey, cevap
  beklenirken ekranda ne olduğu.
- **Kod bu döngüde değişmiyor.** Testler kırmızı bırakılır.
