# v14 Görev 28 eki — Bekleyen karo da döner: TEST döngüsü tasarımı

**Tarih:** 2026-08-24 · **Kaynak:** Colab turu, aynı gün
**Öncesi:** [Görev 28 test spec'i](2026-08-24-queen-editor-v14-gorev-28-testler-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 28

## Neden bir karar geri alınıyor

Görev 28 karoyu dört hâle ayırdı ve bunlardan ikisinde tutucu gösteriyor: **sırada bekleyen** sade
kutu, **inen** kutu artı dönen halka. Gerekçe şuydu: tavan 1 olduğu için galeri açılır açılmaz
bütün karolar sıraya giriyor, hepsi dönerse doksan halka döner ve hangisinin gerçekten indiği
kaybolur.

Kullanıcı bunu okuyup onaylamıştı. Sonra Colab'da gördü ve kararını değiştirdi: ekranın büyük
bölümü hareketsiz duruyor, bir şey olduğunu söyleyen tek işaret gözden kaçacak kadar küçük kalıyor.

**Ekranda görmek okumaktan başka bir şey.** Bu koşunun kendi dersi: karar turdan sonra da
değişebilir.

## Değişen tek şey

| Hâl | Bugün | Yarın |
|---|---|---|
| Sırada | Kutu | **Kutu + halka** |
| İniyor | Kutu + halka | Kutu + halka |
| Geldi | Fotoğraf | Fotoğraf |
| Gelmedi | Kutu | Kutu |

Yani tutucu artık `granted` değerine bakmıyor: **beklemek, indirmekle aynı görünüyor.** Ayrımı
yapan tek şey `state` — `waiting` dönüyor, `gone` durmuş duruyor.

## Kabul edilen bedel

Galeriye bakan biri artık **hangi karenin o an indiğini göremiyor.** Kullanıcı bunu bilerek seçti:
her karonun *"benim de sıram var"* demesi, sıranın nerede olduğunu bilmekten daha değerli.

Bu, sırayı tarif eden başka hiçbir şeyi bozmuyor — indirme yine tek tek ve yine kare sırasıyla.
Değişen yalnız neyin çizildiği.

## Sabitlenecek davranış

| # | Ne | Neden |
|---|---|---|
| **B1** | Sırada bekleyen karo halka gösterir | Kararın kendisi |

Görev 28'in diğer iki tutucu testi olduğu gibi kalıyor ve ikisi de anlamını koruyor: inen karo
dönmeye devam ediyor, gelmeyen karo sessiz kutu olarak duruyor. Yeni davranışın onlarla çelişmemesi
bu ikisinin yeşil kalmasıyla görülüyor.

## Nerede duracak

`frontend/src/features/photo_generation/TileImage.test.jsx` — bugün *"shows a plain holder while it
waits its turn"* diyen test. **Yeni test eklenmiyor, o testin cümlesi değişiyor:** aynı durumu
sınıyor, cevabı değişti. İkinci bir test eklemek aynı hâl için iki çelişen cümle bırakırdı.

## Kapsam dışı

- **Kuyruk değişmiyor.** Tavan 1, sıra kare sırası, 30 saniyelik bilet — hiçbiri bu ekin konusu
  değil.
- **Yeni bir görsel yazılmıyor.** `Rendering` zaten var ve zaten kullanılıyor.
- **Kod bu döngüde değişmiyor.** Test kırmızı bırakılır.
