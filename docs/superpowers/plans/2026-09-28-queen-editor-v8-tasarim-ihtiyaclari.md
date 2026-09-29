# Queen Editor: bir sonraki tasarım turunun ihtiyaçları

Queen Editor tarayıcıda çalışan bir üretim aracı. Kullanıcı bir projeye prompt listesi yapıştırır,
her prompt birkaç kare açar, ve her karenin önce fotoğrafı, sonra üstüne videosu ve sesi üretilir.
Arayüz bilerek Türkçe; aşağıdaki etiketler ekranda yazdığı gibi. Prompt listesini sahibinin öteki
aracı QueenAgent yazıyor; QueenAgent'ın ihtiyaçları ayrı bir belgede.

Bu belge sahibinin bu tasarım turunda cevap istediği üç ihtiyacı anlatıyor. Çözüm değil, sorun ve
sahibinin kesinleşmiş kararları var. Burada sahibinin kararı olarak yazmayan her şey tasarımcının
kararı. Açık kalan bir şey olursa varsaymadan sahibine sorun: açık noktaları sizinle konuşmak
istiyor.

---

## Bugün: kareler nerede görünüyor

İlk iki ihtiyaç karenin kendisine dokunuyor. Karenin bugün göründüğü iki yer:

- **Galeri.** Proje ekranında beş sütunluk bir ızgara, her kare kare biçimli bir kutucuk. Kutucukta:
  - sağ üstte sıra numarası
  - sol üstte durumu, katmanın adıyla: *"foto kuyrukta"*, *"video üretiliyor"*, *"ses hata"* gibi
  - sol altta sahip olduğu katmanlar: *"video"* (loop videoysa *"loop"*) ve *"ses"*
  - sağ alt köşe, etiketler üst üste binmesin diye bilerek boş
  - kutucuğun altında dosya adı
- **Karenin sayfası.** Kutucuğa basınca açılır.
  - Ortada fotoğraf büyük, iki yanda oklar, üstte *"Foto"*, *"Video"*, *"Ses"* sekmeleri.
  - Sağda 300px'lik bir sütun. Üstte karenin bilgileri: *"Sıra"*, *"Dosya adı"*; foto sekmesinde
    *"Model"* ve *"LoRA"*, video sekmesinde *"Üretim modu"*.
  - Altında açık sekmenin prompt kutusu (*"Foto prompt'u"*, *"Video prompt'u"*, *"Ses prompt'u"*),
    foto sekmesinde bir de *"Foto negatif prompt'u"*.
  - En altta *"Yeniden üret — yeni kare"* ve silme düğmeleri.

Prompt listesi proje ekranının yan panelindeki *"Prompt listesi"* kutusuna yapıştırılır. Aynı
panelde *"Negatif prompt"* alanı ve *"Varyant"* sayısı var: her prompt o sayı kadar kare açar, yani
bir prompt'un birkaç karesi olur.

---

## 1. Karenin senaryosu

**Bugün**
- Liste yalnız prompt taşıyor. Bir karenin neyi göstermeye çalıştığı hiçbir yerde yazmıyor.
- Fotoğraf prompt'u, fotoğraf modeline giden bir etiket listesi (*"1girl, black dress, bedroom,
  from behind…"* gibi). Kullanıcı fotoğrafın istenen şeyle eşleşip eşleşmediğini bugün bu etiketleri
  okuyarak anlamaya çalışıyor.

**İhtiyaç.** QueenAgent'ın listesi bundan sonra her kare için bir senaryo da getirecek: karenin
neyi göstermeye çalıştığını anlatan sahne cümlesi. Sahibinin sözleriyle, senaryo Queen Editor'de
"bir yerde yazsın, böylece kullanıcı prompt'ların ve fotoğrafın eşleşip eşleşmediğini kolayca
görebilsin."

**Sahibinin kararları**
- Her karenin senaryosu karede görünür.
- Senaryo QueenAgent'ın listesiyle gelir.
- Senaryo yalnız okunur: kullanıcı onu Queen Editor'de değiştirmez.
- Eski biçimdeki liste de açılmaya devam eder, ve ondan açılan karelerin senaryosu yoktur.

**Tasarımcıya kalan**
- Senaryonun nerede durduğu: galerideki kutucukta, karenin sayfasında, ya da ikisinde.
- Nasıl göründüğü.

**Tasarlanması gereken durumlar**
- **Senaryosu olan kare.**
- **Aynı prompt'tan açılmış birkaç kare:** hepsi aynı senaryoyu taşır.
- **Senaryosu olmayan kare:** eski biçimdeki listeden açılmış, ya da bu değişiklikten önce üretilmiş.

---

## 2. Üretim süresi

**Bugün**
- Hiçbir katmanın ne kadar sürede üretildiği kaydedilmiyor, ve hiçbir yerde görünmüyor.
- Bir katman üretilirken galerideki kutucuğun sol üstünde *"foto üretiliyor"* ya da *"video
  üretiliyor"* yazıyor; karenin sayfasında fotoğrafın üstünde *"video üretiliyor…"* kutusu var. Ne
  kadardır sürdüğü yazmıyor.

**İhtiyaç.** Sahibinin sözleriyle: "her fotoğraf, video, ses ne kadar sürede üretildi, kaydedelim ve
gösterelim."

**Sahibinin kararları**
- Her katmanın kendi süresi var: fotoğrafın, videonun ve sesin ayrı ayrı.
- Süre yalnız üretimin kendisi, yani modelin o katmanda çalıştığı süre. Sırada beklenen süre sayılmaz.
- Süre canlı görünür: bir katman üretilirken geçen süre ilerler, ve üretim bitince katmanın süresi
  kalır.
- Bu değişiklikten önce üretilmiş karelerin süresi yok, ve onlarda süre görünmez.

**Tasarımcıya kalan**
- Sürenin nerede durduğu: galerideki kutucukta, karenin sayfasında, ya da ikisinde.
- Nasıl göründüğü, sayının biçimi dahil.

**Tasarlanması gereken durumlar**
- **Yalnız fotoğrafı olan kare:** tek süre.
- **Fotoğrafı, videosu ve sesi olan kare:** üç ayrı süre.
- **Bir katmanı üretilmekte olan kare:** o katmanın süresi canlı ilerliyor.
- **Bir katmanı kuyrukta bekleyen kare:** o katmanın süresi henüz başlamadı.
- **Eski kare:** hiç süresi yok.

---

## 3. Prompt'u yazan modelin seçimi

**Bugün**
- Kullanıcı yalnız fotoğraf prompt'larını yazıyor. Videonun ve sesin prompt'unu bir dil modeli,
  grok, kendisi yazıyor; kullanıcı modeli göremiyor ve seçemiyor.
- Video ve ses, yan paneldeki *"Video üret"* ve *"Ses üret"* panellerinden kuyruğa ekleniyor. İkisinde
  de *"Model"* başlıklı bir kutu var, ama o kutu videoyu ya da sesi üreten modeli gösteriyor, ve tek
  seçeneği var.
- Yazılan prompt karenin sayfasındaki *"Video prompt'u"* ve *"Ses prompt'u"* kutularında görünüyor.

**İhtiyaç.** Sahibinin sözleriyle: "model seçebilelim, DeepSeek yapmak istemezse diye." Prompt'ları
bundan sonra varsayılan olarak DeepSeek yazacak; açık içerikli bir kareyi reddederse kullanıcı başka
bir modele geçebilmeli.

**Sahibinin kararları**
- Uygulama açıkken, bir açılır listeden seçilir.
- Listede iki model var: *"Queen AI"* (DeepSeek) ve *"Grok"*.
- Varsayılan *"Queen AI"*.
- Tek seçim, yazılan bütün prompt'ları kapsar: videonun ve sesin prompt'ları.
- Seçim, paneldeki öteki seçimler gibi projeye kaydedilir; proje yeniden açılınca aynı model seçili.

**Tasarımcıya kalan**
- Listenin nerede durduğu, ve adı.
- Videoyu ya da sesi üreten modelin *"Model"* kutusuyla karışmaması.

**Tasarlanması gereken durumlar**
- **Queen AI seçili:** yeni projede.
- **Grok seçili.**
- **Liste açık:** iki satır.

---

## Çalışmaya devam etmesi gerekenler

- Galerideki kutucuğun bugünkü etiketleri okunur kalır: sıra numarası, durum ve sahip olunan
  katmanlar.
- Karenin sayfasındaki prompt kutuları yazılabilir kalır. Kullanıcı loop olmayan bir karenin video
  prompt'unu oradan elle düzeltiyor.
- Paneldeki *"Negatif prompt"* alanı bugünkü gibi kalır. Senaryonun negatif listesi QueenAgent'tan
  kopyalanıp buraya yapıştırılıyor.
