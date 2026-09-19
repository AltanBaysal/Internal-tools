# Madde 237 · Model ve LoRA ayrı iki kutu — test turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Kullanıcıdan gereken

Hiçbir şey. Beş karar da 18 Eylül'de alındı ve maddenin satırında duruyor.

## Bugün ne oluyor

Model kutusundaki bir satır bir **tarif**: bir kimlik, bir checkpoint ve bir LoRA dizilimi
*(`domain/recipes.py`)*. `nova3dcg` Nova'nın checkpoint'i + USNR 0.8; `slime` aynı checkpoint +
translucent 0.9 + prompt'un başına giren tetik kelime. Kare, seçileni `recipe:<id>` biçiminde tek
bir değer olarak taşıyor; render eden yer öneki görüp tarifi çözüyor
*(`comfy_photo_generator._recipe`)*.

Defter de aynı ikiliği taşıyor: CONFIG'de tarif kutuları, `PHOTO_RECIPES` listesi, ve uygulamaya
`QE_PHOTO_RECIPES` ile geçen kimlikler.

## Ne olacak

**Katalog ikiye ayrılıyor.**

- **Model** bir checkpoint'tir: kimlik, ad, dosya, ve **kendi standart LoRA dizilimi**. Nova 3DCG'nin
  standardı USNR 0.8; DaSiWa'nınki boş.
- **LoRA** bir dosyadır: kimlik, ad, dosya, güç, ve varsa tetik kelime. Bugün tek satır: Slime
  *(translucent 0.9, tetik `translucent penetration`)*.

**Kare iki değer taşıyor:** `model` ve `lora`. `lora` boşsa modelin standardı kullanılır — bugünkü
çıktı birebir korunur. `lora` doluysa yükleyicinin yuvaları **yalnız** o LoRA ile doldurulur, ve
tetik kelimesi prompt'un başına geçer; bu, bugünkü Slime'ın ta kendisi.

**Eski değerler okunur, göç yazılmaz:** `recipe:slime` modeli `nova3dcg`, LoRA'sı `slime` sayılır;
`recipe:nova3dcg` yalnız modeldir. Bilinmeyen bir tarif bugünkü gibi render'ı durdurur.

**Defter** seçilen modelleri veriyor, `QE_PHOTO_MODELS` ile. DaSiWa kendi kutusuyla geliyor;
işaretli değilse inmiyor ve listede görünmüyor. **LoRA'nın defterde kutusu yok:** iki LoRA dosyası
bugün de her fotoğraf kurulumunda iniyor *(birlikte 1,1 GiB'ın altında)* ve Üreticiler paneli ikisini
de sayıyor. Bir LoRA kutusu diske hiçbir şey söylemezdi, yalnız bir satırı saklardı. Slime'ın eski
tarif kutusu bu yüzden gidiyor, ve LoRA listesi her zaman `Standart` + katalogdaki LoRA'lar.

**Panel** Model kutusunun altına LoRA kutusunu koyuyor. İlk satırı `Standart`, değeri boş. Liste
gelmeden kutu yalnız `Standart` gösteriyor. İki kutu aynı cevapla geliyor: `/api/models` artık
`{models, loras}` döndürüyor.

**LoRA seçimi projenin ayarlarına yazılmıyor.** Model yazılıyor, çünkü proje açılınca hangi
checkpoint'le çalışıldığı hatırlanmalı. LoRA ise kullanıcının sözüyle **varsayılanı Standart olan**
bir kutu: ziyaret boyunca taslakla birlikte hatırlanıyor, proje yeniden açılınca Standart'a dönüyor.

## Çivilenecek olgular

| # | Ne diyor | Bugün |
|---|---|---|
| 1 | Model listesi işaretlenen checkpoint'leri veriyor, değerlerinde `recipe:` yok | **kırmızı** |
| 2 | LoRA listesi `Standart` ile başlıyor ve işaretlenen LoRA'ları sıralıyor | **kırmızı** |
| 3 | LoRA seçilmemiş bir kare modelin standart dizilimiyle render ediliyor *(Nova → USNR 0.8)* | **kırmızı** |
| 4 | LoRA seçilmiş bir kare yalnız o LoRA'yı yüklüyor ve tetiği prompt'un başına koyuyor | **kırmızı** |
| 5 | DaSiWa seçilen bir kare kendi checkpoint'iyle, LoRA'sız render ediliyor | **kırmızı** |
| 6 | `recipe:slime` yazan eski bir kare Nova + Slime olarak render ediliyor | **kırmızı** |
| 7 | Tanınmayan bir model render'ı kendi cümlesiyle durduruyor | yeşil *(bekçi)* |
| 8 | Kuyruğa giren kare LoRA seçimini plana yazıyor, ve üretim onu okuyor | **kırmızı** |
| 9 | Panelde Model kutusunun altında LoRA kutusu var, `Standart` ile açılıyor | **kırmızı** |
| 10 | Panel seçilen LoRA'yı kuyruk isteğiyle gönderiyor | **kırmızı** |
| 11 | Kare detayı hangi model ve hangi LoRA ile üretildiğini yazıyor | **kırmızı** |
| 12 | Defterin her fotoğraf kutusu bir model, ve kutular uygulamanın model kimlikleriyle eşleşiyor | **kırmızı** |
| 13 | Defter DaSiWa'nın checkpoint'ini yalnız kutusu işaretliyken indiriyor | **kırmızı** |
| 14 | Defter seçilen modelleri `QE_PHOTO_MODELS` ile veriyor, `QE_PHOTO_RECIPES` kalmıyor | **kırmızı** |
| 15 | Plan LoRA'yı okuyup yazıyor; eski bir planın karesi Standart okunuyor | **kırmızı** |
| 16 | Yeniden üretilen fotoğraf karesinin modelini ve LoRA'sını koruyor | **kırmızı** |

## Bu turda değişen

Yalnız testler: `test_photo_usecases.py`, `test_comfy_photo_generator.py`, `test_photo_routes.py`,
`test_plan_store.py`, `test_notebook_installs_the_producer_groups.py`, `GeneratePanel.test.jsx`,
`PhotoDetail.test.jsx`, `useModels.test.jsx`, ve cevabın şeklini taklit eden
`ProjectScreen.test.jsx` ile `App.test.jsx`.

Üreticinin çağrı şekline `lora=""` ekleniyor *(model'in hemen ardına)*, yani testlerdeki her sahte
üretici bu parametreyi alıyor. Video ve ses üreticileri onu almak zorunda ama kullanmıyor —
`source` ve `end` için zaten böyle.
