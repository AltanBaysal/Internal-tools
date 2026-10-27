# Madde 299 — Havuz ekranda, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken:** yok. Panelin yeri ve davranışı 21 Eylül'de konuşuldu: *"solda cardların
olduğu yerde pencere gibi açılması mantıklı geldi bana… vs code gibi kapatılabilir de, ama card
penceresi kapatılamaz."*

## Madde ne diyor

> Kartların solunda kapanabilir panel; tipe göre sıralar; yükleme ve silme. Sıranın başlığı doluluğu
> söylüyor *("Fotoğraflar 4/9")*. Panelin açık mı kapalı mı olduğu tarayıcının bileceği şey, sunucuya
> sorulmaz.

## Nerede duruyor

Bugünkü proje ekranı iki sütun: solda galeri *(esner)*, sağda 320px kontrol paneli. Havuz **üçüncü
bir sütun olarak en sola** giriyor — galerinin solunda, kontrol panelinin karşısında. Kapanınca
yerinde onu geri açan ince bir düğme kalıyor; kart penceresi *(sağdaki)* kapanmıyor, çünkü
kullanıcının kararı buydu.

**Açık/kapalı sunucuya sorulmuyor** ve saklanmıyor: bileşenin kendi durumu. Sayfa yenilenince panel
açık gelir — havuzun kendisi diskte durduğu için kaybolan bir şey yok.

## Ne çiziyor

Üç sıra, tipe göre, her birinin başlığı **doluluğu** söylüyor: *"Fotoğraflar 4/9"*, *"Videolar 1/3"*,
*"Sesler 0/3"*. Sayılar sunucunun listesinden; sınırlar **298**'in tablosundan geliyor ve ekranda
ikinci kez yazılmıyor — ekranın kendi kopyası, sınır değiştiği gün yalan söylerdi. Bu yüzden
**liste sınırları da taşıyor**: `/api/projects/<p>/references` cevabına `limits` ekleniyor.

Her karo dosyanın adını taşıyor. Fotoğraf resmini gösteriyor *(`/references/…`)*, video sessiz bir
video öğesi, ses bir karo — ve klipler süresini yazıyor *(`4,2 sn`)*, çünkü sunucu zaten söylüyor.

**Ekle** düğmesi çoklu dosya seçtiriyor; **sil** her karonun üstünde, ve soruyor *(madde 83'ün
yıkıcı hareket kuralı)*.

Sunucunun reddi olduğu gibi yazılıyor — sınır cümlesi **298**'de, tek yerde.

## Yükleme zaman aşımı

`shared/api.js`'in her isteği **10 saniyede** kesiliyor. 15 saniyelik bir video Drive'a bu sürede
çıkmayabilir, ve kesilen yükleme kullanıcıya *"sunucuya ulaşılamadı"* diye görünür — yanlış cümle.
İstek sarmalayıcısı bir **`timeout`** seçeneği alıyor, ve yükleme uzun olanı kullanıyor.

## Yazılacak testler

### `frontend/src/shared/api.test.js`

1. **yükleme dosyaları `FormData` ile gidiyor** ve `Content-Type` elle konmuyor *(sınırı tarayıcı
   yazar)*.
2. **yüklemenin kendi zaman aşımı var** — on saniyede kesilmiyor.

### `frontend/src/features/photo_generation/ReferencePanel.test.jsx`

3. **üç sıra, doluluğuyla** — *"Fotoğraflar 1/9"*, *"Videolar 0/3"*, *"Sesler 0/3"*.
4. **fotoğraf resmini çiziyor**, kaynağı sunucunun referans adresi.
5. **klip süresini yazıyor.**
6. **Ekle seçilen dosyaları yolluyor**, ve gelen havuz ekranda.
7. **sunucunun reddi olduğu gibi görünüyor** — 298'in cümlesi.
8. **silmek önce soruyor**, sonra yolluyor.
9. **havuz boşken sıra başlıkları yine duruyor** *(0/9)*, çünkü panelin işi havuzu kurmak.

### `frontend/src/features/photo_generation/ProjectScreen.test.jsx`

10. **panel açık geliyor ve kapanıyor**; kapalıyken onu geri açan düğme var.
11. **sağdaki kart penceresi kapanmıyor** — kapatma düğmesi yok.

## Bu turda yapılmayacaklar

Sıra ve boşluk *(300)*, referans modu penceresi *(301)*, üretim *(302–305)*.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor/frontend` kırmızı. `dist` bu turda üretilmiyor — kaynak
değişmiyor.
