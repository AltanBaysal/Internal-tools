# v14 Görev 34 — Açık panel geri dönüşte yerinde kalır: TEST döngüsü tasarımı

**Tarih:** 2026-08-25 · **Kaynak:** Colab turu, 24 Ağustos
**Öncesi:** [Görev 33 uygulama spec'i](2026-08-24-queen-editor-v14-gorev-33-uygulama-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 34

## Sorun

Sağ sütunda hangi panel açıksa — kuyruk, video, ses, agent, üreticiler — bir kareye girip dönünce
kapanıyor ve *Fotoğraf üret* paneline dönülüyor. Kuyruğu izlerken bir kareye bakmak isteyen
kullanıcı, her dönüşte paneli yeniden açmak zorunda.

Sebep 31, 32 ve 33'ünkiyle aynı: adres bir kareyi gösterdiğinde `App` başka bir bileşen döndürüyor,
React ağacı söküyor, ve artık var olmayan bir bileşenin state'ini atıyor. Yeni örnek kendi
varsayılanıyla doğuyor.

## Kararlaştırılan davranış

Hangi panelin açık olduğu, o proje içinde hatırlanır.

**Kapalı da bir cevaptır.** Kullanıcı sütunu kapatıp genişliği galeriye verdiyse, dönüşte sütun yine
kapalı gelir. Onun yerine paneli açmak, açık paneli kapatmakla aynı türden bir yanlış.

**Ömür bellek kadar.** Sayfa yenilenince sütun yine *Fotoğraf üret* ile açılır — bu koşunun diğer
altı deposu (`REMEMBERED` ×2, `shownPictures`, `KEPT`, model listesi, üretici listesi) ne kadar
yaşıyorsa o kadar. Diske hiçbir şey yazılmaz.

**Anahtar proje.** Hangi panele bakıldığı kullanıcının o projedeki işi; başka bir proje kendi
varsayılanıyla açılır.

## Neden 33'ten sonra

33, kuyruk panelinin ilk cevaptan önce *"Kuyruk boş"* demesini kapattı. Bu madde kuyruk panelini
geri dönüşte açık bırakıyor — yani o yanlış cümlenin ekrana geleceği ilk durumu bu madde yaratıyor.
Ters sırada, bir düzeltme yerine yeni bir hata görünürdü.

## Testlerin çakıştığı yer, ve neden bu bir kusur değil

Depo modül seviyesinde durduğu için `SidePanel.test.jsx`'in on dokuz testi birbirini etkiler:
sütunu kapatan bir test, bir sonrakini kapalı başlatır.

Bu, hatırlamanın kendi doğası — gerçekten kalıcı bir durum ekleniyor. Dosya, 32'de `useModels` ve
`useProducers`'ın geçtiği düzene geçiyor: **her teste taze modül.** Mevcut testlerin cümleleri
değişmiyor, yalnız başlangıçlarının gerçekten temiz olduğu garanti altına alınıyor.

Burada sahte api yok, dolayısıyla 32'nin `vi.clearAllMocks()` inceliği geçerli değil: dosya
`SidePanel`'i doğrudan içe alıyor ve `vi.resetModules()` onu gerçekten yeniden doğuruyor.

## Sabitlenecek davranış

| # | Ne | Bugün |
|---|---|---|
| **B1** | Açık panel ikinci mount'ta yerinde | kırmızı |
| **B2** | Kapalı bırakılan sütun kapalı geri gelir | kırmızı |
| **B3** | Hiçbir şey hatırlanmıyorken sütun *Fotoğraf üret* ile açılır | yeşil — tutucu |
| **B4** | Başka bir proje kendi varsayılanıyla açılır | yeşil — tutucu |

**B3 ve B4 kırmızıya düşmez, ve düşmemeleri gerekiyor.** İkisi de bugün doğru; varlık sebepleri
yanlış uygulamaları kırmak:

- **B3**, deponun ilk değerini `null` seçen bir uygulamayı kırar — sütun ilk ziyarette kapalı
  gelirdi. Sütunun fotoğraf paneliyle açılmasını koruyan tek şey bu.
- **B4**, projeyi anahtar yapmayı unutan bir uygulamayı kırar — bir projenin paneli ötekine
  taşınırdı.

B2'nin ayrıca sakladığı bir tuzak var: kapalı sütunun değeri `null`, ve depo "hatırlanmıyor"u da
`null` ile temsil ederse ikisi ayırt edilemez. Test bunu doğrudan sınamıyor ama uygulamayı buna
mecbur bırakıyor.

## Nerede duracak

`frontend/src/features/photo_generation/SidePanel.test.jsx`. Depo tamamen bu bileşenin içinde
doğuyor; dışarıdan geçirilen bir şey yok, dolayısıyla ekran seviyesinde bir teste de gerek yok —
33'ten farklı olarak burada sessizce eksik kalabilecek bir kablo yok.

## Kapsam dışı

- **Galeri seçiminin hatırlanması** — kullanıcı kararıyla 34'ten çıkarıldı; seçim modundayken bir
  kareyi açmanın yolu olmadığı için tarif edilen durum hiç oluşmuyor. Kaydı
  [backlog](../../../queen-editor/BACKLOG.md)'da.
- **Yazılmış ama gönderilmemiş metin** — 35. madde.
- **Kod bu döngüde değişmiyor.** Testler kırmızı bırakılır.
