# Görev 1 — Üretim sözleşmesi tek olsun

**Roadmap:** [v7](../plans/2026-08-13-queen-editor-v7-roadmap.md) · Blok 1

## Sorun

Uygulama Colab'da hiçbir şey üretemiyor, ama test takımı yeşil.

- **Foto:** `ComfyPhotoGenerator.generate()` `source` diye bir argüman tanımıyor; döngü her çağrıda
  geçiyor. Her kare üç kez deneniyor ve üretim duruyor.
- **Ses:** `MMAudioGenerator.generate()` `(ad, bayt)` döndürüyor; döngü cevabı bayt sanıp dosyaya
  yazıyor. Üstelik ürettiği ad domainin şemasına da uymuyor — döngü o dosyaya
  `P0_0_V1_0_S1_0.wav` diyor, üretici `P0_0_V1_0.wav`.
- **Yazılı sözleşme üç yerde üç türlü:** port `source`'u hiç anmıyor, v6 Görev 5 spec'i cevabı
  `(ad, bayt)` diye yazıyor, video üreticisi baytla cevap veriyor.

Takımın bunu yakalamamasının sebebi tek: **hiçbir test bir üreticiyi kuyrukla birlikte
koşmuyor.** Her üretici kendi testinde tek başına çağrılıyor, kuyruk testleri de sahte
üreticilerle koşuyor. İki taraf da kendi içinde tutarlı; aralarındaki sözleşme kimsenin testi
değil.

## Kararlar

1. **Sözleşme:** `generate(prompt, negative, seed, model="", source=None) -> bytes`. Dosyayı
   **döngü adlandırır**. Neden bayt: ad domainin işi (`photo_name.layer_file`), ve üretici adı
   ikinci kez bilirse iki ad birbirinden ayrılır — bugün zaten ayrılmış durumda.
2. **Üç üretici de aynı imzayı taşır**, kaynağa ihtiyacı olmayan da. Foto `source` alır ve
   kullanmaz; sebebini kendi dosyasında yazar: bir fotoğraf hiçbir şeyin üstüne binmez.
   Alternatif — döngünün `source`'u yalnız gerektiğinde geçmesi — tek çağrı yerine iki çağrı şekli
   demek olurdu, ve hangi şeklin geçerli olduğunu döngüyle üretici ayrı ayrı bilmek zorunda
   kalırdı.
3. **Port, yazılı sözleşmenin tek sahibidir.** `ports.PhotoGenerator.generate` hem `source`'u hem
   cevabın ne olduğunu yazar. Bugün ikisini de yazmıyor; sözleşmenin nerede yazdığı belirsiz
   olduğu için üç kopya birbirinden ayrıldı.
4. **Ses üreticisi ad döndürmeyi bırakır.** Döndürdüğü ad zaten yanlış; silmek bir davranış kaybı
   değil, bir yalanın kalkması.
5. **Sözleşmeyi koruyan test kuyrukla birlikte koşar.** Yeni bir test dosyası üç **gerçek** üretici
   sınıfını **gerçek** döngünün (`make_job`) altında koşturur: ComfyUI istemcisi ve MMAudio
   örnekleyicisi sahte, üretici sınıfları gerçek. İddiası: iş uçtan uca geçiyor, dosya domainin
   verdiği adla kaydediliyor, içinde üreticinin baytları var.
   İmza kontrolü (`inspect.signature`) bunun yerine geçmez: bugünkü ses hatası imzada değil,
   cevapta. Bir sonraki hata da orada olabilir.
   **Grafikler de gerçek olanı**, uydurma değil: kendi grafiğini yamalayamayan bir üretici
   sözleşmeyi pratikte karşılamıyordur. Sahte olan yalnız test makinesinde bulunamayacak şeyler —
   ComfyUI sunucusu, torch ve ffmpeg.
6. **`test_the_answer_is_a_wav_named_after_the_video` değişir, silinmez.** Sorduğu soru hâlâ
   geçerli — "cevap nedir" — değişen cevabı. Adı da yeni cevabına göre yazılır.
7. **v6 Görev 5 spec'i düzeltilmez.** Yanlış sözleşme oradan geldi, ama spec'ler o gün verilen
   kararın tarihi kaydıdır; geriye dönük düzenlemek kararın ne zaman değiştiğini okunamaz yapar.
   Düzeltme bu spec'te duruyor. (Yaşayan belgeler — FOUNDATION, CODE-STANDARD — bu görevde
   değişmiyor: sözleşme ikisinde de yazmıyor.)

## Testler

Yeni, sözleşmeyi koruyan dosya:

- Foto işi gerçek `ComfyPhotoGenerator` ile kuyruktan uçtan uca geçer; `P0_0.png` kaydedilir ve
  içinde istemcinin verdiği baytlar vardır.
- Video işi gerçek `ComfyVideoGenerator` ile geçer; `P0_0_V1_0.mp4` kaydedilir ve üreticiye kaynak
  olarak karenin fotoğrafı ulaşır.
- Ses işi gerçek `MMAudioGenerator` ile geçer; `P0_0_V1_0_S1_0.wav` kaydedilir ve içinde
  örnekleyicinin baytları vardır.

Değişen test:

- `MMAudioGenerator.generate` tek başına çağrıldığında **yalnız bayt** döner.

Değişmeyen:

- Mevcut takım yeşil kalır. Kuyruk, katman ve yeniden üretme tarafında tek satır kullanım durumu
  değişmemeli — değişiyorsa ya port bozulmuştur ya kapsam kaymıştır.

## Öz eleştiri

- *Foto neden kullanmadığı bir argümanı alıyor?* — Çünkü sözleşmeyi çağıran taraf tek: kuyruk.
  Kuyruğun her iş türü için ayrı bir çağrı şekli tutması, bugün düzelttiğimiz hatanın daha
  büyüğünü davet eder. Kullanılmayan argüman görünür ve açıklanmış bir maliyettir; iki çağrı şekli
  görünmez bir maliyet.
- *Üç üreticiyi gerçek koşturan test yavaş olmaz mı?* — Olmaz. Ağır olan her şey (ComfyUI
  istemcisi, torch, ffmpeg) zaten dışarıdan veriliyor; testte sahtesi geçiyor. Diske dokunan tek
  şey ses üreticisinin geçici klasörü, o da `tmp_path`.
- *Sahte istemciyle koşan bir test üretimi gerçekten kanıtlar mı?* — Kanıtlamaz, iddiası da o
  değil. İddiası: **döngüyle üretici birbirini anlıyor.** Bugün kırılan tam olarak buydu.
  ComfyUI'nin gerçekten cevap verdiği ancak Colab turunda görülür.
- *Sözleşmeyi porta yazmak yetmez mi, test şart mı?* — Yetmez. Port bir `Protocol`; kimse ona
  uymaya zorlanmıyor, çalışma zamanında da kontrol edilmiyor. Bugünkü üç kopya tam da bu yüzden
  ayrıldı.
