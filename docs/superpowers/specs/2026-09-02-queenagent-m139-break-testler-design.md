# Madde 139 · Tur 1 (test) — Tasarım

**Kaynak:** [v6 yol haritası, Madde 139](../plans/2026-09-01-v6-roadmap.md)
**Şartı:** 138 — koşuldu, denendi, `BREAK` işe yarıyor *(kullanıcı yargısı, 1 Eylül)*.
**Dal:** `feat/v6`

## Sorun

Grafik artık `BREAK`'i tanıyor, ama promptun içine kimse yazmıyor. `build_prompts` bugün her şeyi
tek bir virgül dizisine diziyor:

```
quality, people, ANA KARAKTER + kıyafeti, mekân, action, camera, GERİ KALANLAR
```

Karakter tarifleri arasında mesafe var *(Madde 95)* ama **ayrım yok** — hepsi tek metin, tek parça
hâlinde kodlanıyor. 138'in açtığı düğüm boşta duruyor.

## İki karar, ve ikisi de bu spec'te veriliyor

Yol haritası bu maddeye iki açık soruyla geliyordu.

### 1 · `BREAK` her karakter bloğunun arasına girer

Ana karakterle geri kalanların arasına değil, **her bloğun arasına**. Üç kişilik bir karede
`… camera BREAK ikinci BREAK üçüncü` çıkar.

Sebep: mekanizma karakterleri ayırıyor, ve kuralın istisnası olmaması kuralın kendisinden daha
kolay okunuyor. Yanında bir bedel de kalkıyor — bugünkü sıra düzeltmesi *"sondaki ikisi hâlâ
birbirine bulaşabilir, bilerek kabul edildi"* diyordu
*([test_build_prompts.py](../../../queen-agent/backend/tests/test_build_prompts.py) bunu bir testle
kayda geçirmiş)*. `BREAK` o kabulü bedelsiz kaldırıyor, yani kabul de kalkıyor.

### 2 · Sıra düzeltmesi **duruyor**

Ana karakter başta, geri kalan `camera`'dan sonra — Madde 95'in koyduğu düzen aynen kalıyor.

Yol haritası bunu *"yeniden sorulacak"* diye bırakmıştı, ve kayda geçmiş bir şüphe vardı: erken
jetonlar daha ağır bastığı için ikinci karakteri sona atmak onu zayıflatabilir. Şüphe duruyor —
ama **kaldırılmıyor, çünkü kaldıracak ölçü yok.** Sıra düzeltmesini kullanıcı 27 Ağustos'ta elle
deneyip işe yaradığını görmüştü; ölçülmüş bir kazanımı ölçüsüz atmak, bu koşunun 138'de düzelttiği
hatanın aynısı olurdu.

Ayrıca bu madde **tek şeyi değiştiriyor.** Sıra da aynı anda değişseydi, çıkan farkın hangisinden
geldiği söylenemezdi.

Şüphe kendi denemesini bekliyor: aynı kare, sıra düzeltmeli ve düzeltmesiz. O deneme bu maddenin
işi değil.

## Yol

Prompt tek bir metin olmaya devam ediyor; değişen, **nasıl birleştirildiği**.

Bugün bütün parçalar tek bir `_tags` çağrısından geçiyor ve aralarına virgül giriyor. Bundan sonra
**her blok kendi `_tags`'inden geçiyor**, ve bloklar birbirine ` BREAK ` ile ekleniyor:

```
[quality, people, ana karakter + kıyafeti, mekân, action, camera]  ← kendi virgülleri
                              BREAK
[ikinci karakter + kıyafeti]                                        ← kendi virgülleri
```

**Sebep 138'in düğümünün nasıl böldüğü:** düz `text.split("BREAK")`. Yani `BREAK` bir tag gibi
virgüllerin arasına girerse parçalar `, ` ile başlayıp biter — zararsız ama gereksiz, ve promptu
okuyan insan için kirli. Blokları ayrı geçirmek `BREAK`'in virgül komşuluğuna hiç girmemesini
sağlıyor.

## Kurallar

- **Tek karakterli karede `BREAK` yok.** Ayıracak ikinci blok yok.
- **Kimsenin olmadığı karede `BREAK` yok.**
- **`build_character_prompts` değişmiyor.** Tek karakteri tek başına deneyen yol; orada da ayıracak
  bir şey yok.
- **Boş blok `BREAK` doğurmaz.** Sonu ` BREAK ` ile biten ya da iki `BREAK`'i yan yana gelen bir
  prompt çıkmamalı.
- **Bilinen sonucu:** kalite zinciri yalnız ilk blokta kalıyor, çünkü bloklar ayrı kodlanıyor.
  A1111 tarafında `BREAK`'in olağan davranışı bu, ve bilerek kabul ediliyor.

## Bu turun testleri

### Yeniden yazılan üç test

Üçü de bugünkü birleştirmeyi çiviliyor; sözleşme değiştiği için beklentileri değişiyor.

- `test_the_second_character_lands_past_the_camera` — **kırmızı**. `, {DENIZ}` yerine
  ` BREAK {DENIZ}`.
- `test_a_frame_without_a_people_tag_still_splits` — **kırmızı**. Aynı değişiklik, sayı etiketi
  olmayan eski dosyalarda.
- `test_the_second_and_third_stay_side_by_side_at_the_end` → **`…_are_cut_off_from_each_other_too`**
  — **kırmızı**. Adı da yargısı da değişiyor: kabul edilmiş bedel kalkıyor, ve testi de onunla
  birlikte. Eski hâli *"yan yana kalırlar"* diyordu; yenisi *"aralarına da `BREAK` girer"* diyor.

### Yeni bir kırmızı

- `test_break_never_touches_a_comma` — **kırmızı**. Çıktıda ne `, BREAK` var, ne `BREAK,`.
  Maddenin `_tags`'e dokunma sebebi bu tek cümlede.

### İki bekçi, bugün yeşil

- `test_a_single_character_frame_carries_no_break` — tek kişilik kare `BREAK` taşımıyor.
- `test_a_character_tried_alone_carries_no_break` — `build_character_prompts` de taşımıyor.

## Ayakta kalması gerekenler

Dosyanın kalan kırk küçük testi. Özellikle sırayı indeksle ölçenler — `test_who_leads…`,
`test_each_characters_block_stays_together`,
`test_the_outfit_of_whoever_comes_last_follows_them_past_the_camera` — bunlar birleştiricinin
karakterini değil **sırasını** ölçüyor, ve sıra değişmiyor.

Bir de `test_a_repeated_solo_tag_is_left_exactly_as_written`: iki blok ayrı geçse de tekrarlanan
etiket hâlâ olduğu gibi taşınıyor.

## Bilerek yapılmayanlar

**Kod ellenmez.** `build_prompts.py` bu turda değişmiyor.

**`skip` / `xfail` yok.**

**Sıra düzeltmesinin denenmesi.** Yukarıda 2. kararda yazılı: kendi denemesini bekliyor.

**Skill metni ve şema.** Prompt+ metni promptun neye benzediğini anlatıyor; `BREAK` oraya da
yazılmalı mı, uygulama turunun sorusu — bu tur yalnız birleştiricinin çıktısını ölçüyor.
