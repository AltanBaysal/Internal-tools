# Queen Editor v5 · Görev 25 — Prompt düzenleme ve Yeniden üret · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 7, Görev 25 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
76, 77, 78, 98, 99 · **Tür:** arka uç + ön yüz.

## Neden

Detay sayfası katmanları gösteriyor (Görev 23, 24) ama hiçbirine dokunulamıyor: beğenilmeyen bir
kare ancak silinip panelden yeni parti gönderilerek yenileniyor. Tasarımın cevabı, prompt'u yerinde
düzenleyip **yeni bir kare** olarak yeniden üretmek.

## Ne olacak

Detaydaki prompt kutuları yazılabilir olur; değişen kutunun çerçevesi morlaşır ve değişiklik
**kaydedilmez** — yalnız "Yeniden üret — yeni kare" butonuna basılınca işe dönüşür. Buton onay
sormaz: iş kuyruğun sonuna girer, kaynak kare ve dosyası aynen kalır, sonuç kaynağın yanına yeni
kare olarak girer.

## Kararlar

### 1. Yeniden üretim, kopya karenin ta kendisidir

Görev 15 ve 20'de kurulan yol: yeni kare doğar, üretilecek katmanın **altındaki** katmanları
kaynaktan paylaşır, sıraya kaynağın yanına girer. Yeniden üret bunun tek farkla aynısı — prompt
kullanıcıdan gelir, dil modelinden değil.

Bu yüzden ortak parça (`copy_frame`) kimlik + yerleşim + alt katmanları taşıma sorularının hepsini
cevaplar ve iki use case de oradan okur.

### 2. Numara prompt'un değişip değişmediğine bakar (madde 99)

- **Prompt aynıysa** yeni kare aynı ailenin sıradaki varyantıdır: `P11_2` → `P11_4`.
- **Prompt değiştiyse** sıradaki **prompt numarasını** alır: `P15_0`.

Sebep tasarımın kendi cümlesi: aynı prompt'un ikinci denemesi o prompt'un bir varyantıdır, değişmiş
prompt ise yeni bir iştir. Karşılığında prompt numaraları galeri sırasıyla birebir gitmez — tasarım
bunu yan etki olarak kabul etmiş.

Karşılaştırma kırpılmış metin üzerinden yapılır: baştaki/sondaki boşluk bir değişiklik değildir.

### 3. Tur numarası artmaz — ikinci tur zaten yeni karedir (madde 98)

Madde 98 "yeniden üretim ad içinde tur numarasını artıracak" diyor, madde 77 ise sonucun **yeni bir
kare** olduğunu söylüyor ve kullanıcı 77'yi bilinçli olarak seçti. Yeni karede birinci tur zaten
boştur: dosyalar `P11_4.png`, `P11_4_V1_0.mp4` olur.

Yani turun artması gereken yer kalmıyor: ikinci tur, yeni karenin kendisi. Tur çifti şemada duruyor
ve bir gün aynı kareye ikinci bir dosya yazma kararı verilirse anlamını orada bulur.

### 4. Düzenleme geçicidir, sunucuya hiç uğramaz

Kutular ekranın kendi durumudur; sunucuya yalnız butona basılınca ve yalnız **o katmanın** prompt'u
gider. Kaydetme yok: yazdığı metni bir yere kaydetmek, kullanıcının hiç istemediği bir "taslak"
kavramı doğururdu.

Kareler arasında ok tuşlarıyla gezilince kutular yeni karenin metnine döner — düzenleme o kareye
aitti.

### 5. Buton her zaman vurgulu, iş varken pasif (madde 78)

Buton prompt değişsin değişmesin mor durur — "değişiklik yoksa soluk" kuralı v2'den kalkıyor.
Pasifleştiği tek yer: bu karenin o katmanı zaten kuyruktaysa ya da üretiliyorsa, ve basıldıktan
sonra ("Kuyruğa eklendi").

Basılınca fotoğrafın sol üstünde canlı **"yeniden üretilecek — kuyrukta"** rozeti belirir: iş
kuyruğa gitti, sonucu başka bir kare olarak gelecek.

### 6. Hangi katman yeniden üretilir: açık olan

Sekme neyi açtıysa o. Foto sekmesinde foto (yeni tohumla), video sekmesinde video, ses sekmesinde
ses. Alt katmanlar kaynaktan paylaşılır; üsttekiler gelmez (madde 102).

## Nasıl görülür

1. Prompt kutusuna yazınca çerçevesi morlaşıyor; sayfadan çıkıp dönünce yazdığı gitmiş oluyor.
2. "Yeniden üret — yeni kare"ye basınca onay penceresi çıkmıyor, buton "Kuyruğa eklendi" olup
   pasifleşiyor ve fotoğrafın sol üstünde canlı rozet beliriyor.
3. Kaynak kare ve dosyası yerinde; galeride kaynağın yanında yeni kare var.
4. Prompt'a dokunulmadıysa yeni karenin adı aynı ailenin sıradaki varyantı; değiştiyse yeni prompt
   numarası.

## Testler

**Arka uç:** aynı prompt aynı ailenin sıradaki varyantını verir · değişmiş prompt sıradaki prompt
numarasını ve varyant 0'ı verir · yeni kare kaynağın yanına yerleşir · foto yeniden üretiminde yeni
tohum çekilir · video yeniden üretiminde yeni kare kaynağın fotoğrafını paylaşır · ses yeniden
üretiminde foto ve videoyu paylaşır · kaynağın kendi katmanlarına dokunulmaz · bilinmeyen dosya 404
· kaynağın taşımadığı katman istenirse 400.

**Ön yüz:** kutu düzenlenebilir · değişince çerçeve morlaşır · kare değişince kutu sıfırlanır ·
buton her hâlde vurgulu · basınca `onRegenerate` açık katman ve kutudaki metinle çağrılıyor ·
basınca buton "Kuyruğa eklendi" ve pasif · basınca rozet beliriyor · katmanı kuyruktaysa buton
pasif.

## Kapsam dışı

- **Sekme başına yıkıcı eylem** — Görev 26 (bu görevde alttaki Sil bugünkü hâlinde).
- **Hata detayı ve kopya kare detayı** — Görev 27.
- **Negatif prompt'un düzenlenmesi** — tasarım yalnız prompt kutularını söylüyor; negatif salt
  okunur kalır.

## Riskler

- **Numara sıçraması.** Prompt değişince yeni numara alınıyor; galeri sırası ile numaralar
  ayrışıyor. Tasarım bunu kabul etmiş (madde 99).
- **İki kaynak, tek metin.** Ekrandaki kutu ile sunucudaki kayıt ayrışabilir (başka bir sekme aynı
  kareyi yeniden üretirse). Zararsız: gönderilen metin kullanıcının o an gördüğü metindir.
