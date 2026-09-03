# Madde 156 — Kod `people`'ı türetir · **test turu**

**Tarih:** 3 Eylül 2026 · **Branch:** `feat/v6` · **Kaynak:** [v7 yol haritası, Madde
156](../plans/2026-09-03-v7-roadmap.md)

Bu belge yalnız **testlerin** ne çivileyeceğini anlatır. Kodun kendisi ikinci turun işi.

## Neyi çiviliyoruz

`build_prompts` bugün karedeki sayıyı **okuyor**: `frame.get("people", "")`. Kendi yorumu bunu itiraf
ediyor — *"the count is placed, never worked out: the code knows who entered the frame but not what
they are, and no field says so."*

Madde 154 o boşluğu kapattı: karakter girdisi artık `kind` taşıyor. Bu tur, sayının koddan çıktığını
çiviler.

## Sayının kuralı

Karedeki karakterlerin **haritadaki** girdilerine bakılır, türleri sayılır, ve sayım SDXL'in okuduğu
etikete çevrilir:

- Bir tane olan tekil: `1girl`, `1boy`. Birden fazla olan çoğul: `2girls`, `3boys`.
- **Sıra sabit: önce `boy`, sonra `girl`.** Şemanın örneği de bunu diyor *(`"1boy, 1girl"`)*, ve
  booru etiket sırası bu. Karenin kendi sırası **lideri** seçer, sayımı değil — ikisi ayrı sorular.
- **Türü olmayan karakter sayılmaz.** Düz metin girdisinin türü yoktur; `girl`/`boy` dışında bir tür
  de yoktur. İkisi de aynı kapıdan düşer, çünkü ikisi de aynı şey: kodun sayamadığı bir şey.
- Sayılacak kimse yoksa etiket **hiç yazılmaz** — boş bir alan gibi düşer, virgül bırakmaz.

## Yazılı `people` kazanır

Elde duran her dosyada bu alan yazılı, ve o dosyalar bozulmamalı. Bu yüzden okuma sırası:
**yazılıysa o, değilse sayım.**

Bunun bir yan etkisi var ve kabul ediliyor: yazılı `people` taşıyan eski bir dosyada sayım hiç
koşmaz. Doğrusu da bu — o dosyanın karakterlerinde zaten `kind` yok, sayım koşsaydı etiketi
silecekti.

## Yeni testler — `test_build_prompts.py`

Hepsi `characters` haritasına `{"kind": …, "tags": …}` girdileri koyarak koşar; dosyanın varsayılan
fikstürü düz metin taşıyor ve **öyle kalıyor** *(sayılmayan girdinin kanıtı o)*.

1. **Bir kız sayılır** — tek karakterli kare, `people` yazılmadan, `1girl` taşıyor.
2. **Bir oğlan ve bir kız** — `1boy, 1girl`. Karenin sırası `aylin, deniz` iken bile sayım
   `1boy, 1girl` diyor: sıra sabit.
3. **İki kız çoğul olur** — `2girls`.
4. **İki oğlan çoğul olur** — `2boys`. *(Çoğullaştırmanın tek harfe bakan bir kural olduğunu iki tür
   üstünde birden görmek gerekiyor.)*
5. **Sayım kalitenin hemen ardında, liderin önünde** — sıranın kendisi çivilenir.
6. **Türü olmayan karakter sayılmaz** — biri düz metin biri `kind` taşıyan iki karakterli bir kare
   `1girl` diyor, `1boy, 1girl` demiyor.
7. **Tanınmayan bir tür de sayılmaz** — `{"kind": "robot", …}` sayıma katılmıyor. Araç bunu yazamaz
   *(`KINDS` reddeder)*, ama elle düzenlenmiş bir dosya taşıyabilir ve kod düşmemeli.
8. **Kimse yoksa sayı da yok** — boş `characters`, ve promptta kalitenin ardından doğrudan mekân
   geliyor; boşluk ya da fazladan virgül yok.
9. **Yazılı `people` sayımı yener** — türleri `1boy, 1girl` diyecek bir kare, `people: "2girls"`
   yazılıysa `2girls` taşıyor.
10. **Tür prompta hiç girmez** — `kind` yalnız sayıya dönüşür; `tags` metninin dışında bir `girl`
    kelimesi prompta düşmez. *(Var olan `test_a_character_written_with_a_kind_still_builds` bunun
    yarısını zaten tutuyordu; sayı gelince o test de sayıyı bekleyecek şekilde güncellenir.)*
11. **Karakter önizlemesi sayısız kalır** — `build_character_prompts` kare görmez, sayacağı bir kare
    yoktur. Var olan `test_a_preview_reads_both_shapes_too` bunu tutuyor; yanına türlü bir girdinin
    önizlemesinde `1girl` **olmadığını** söyleyen bir test giriyor.

## Yeni testler — `test_schema.py`

Şema modelin okuduğu metin, ve artık yazamadığı bir alanı anlatıyor.

12. **Şema `"people"` alanını hiç göstermez** — alan adı olarak. *(Kelimenin kendisi metinde kalır:
    "two people dressed differently" bir kıyafet kuralı, sayıyla ilgisi yok. Bu yüzden çivi tırnaklı
    biçime vurulur, `test_the_schema_never_mentions_quality`'nin yaptığı gibi değil.)*
13. **Kitapçıkta 6. kural yoktur** — `test_the_rulebook_has_no_quality_rule`'un kardeşi. Numara boş
    bırakılır, kapatılmaz: 3 numaranın emsali bu.

## Değişen var olan testler

- `test_build_prompts.py::test_a_character_written_with_a_kind_still_builds` — türlü girdi artık
  sayı üretiyor; beklenen prompt `1girl` kazanıyor.
- `test_schema.py::test_the_schema_shows_every_field_rather_than_describing_it` — parametre
  listesinden `people` çıkıyor.
- `test_schema.py::test_the_example_shows_two_people_in_different_clothes` — çivisi
  `'"people": "1boy, 1girl"'` idi. Örneğin öğrettiği şey iki ayrı kıyafet; çivi ona kayıyor.
- `test_schema.py::test_the_rulebook_has_a_sixth_rule_about_the_count` — yerini 13. madde alıyor.

## Bu turda dokunulmayanlar

- **`tools.py` hiç değişmiyor.** `kind`'ı yazan araç 154'te geldi, ve bu madde yalnız onu okuyor.
- **Sayım `update_frame`'e ya da `write_frame_prompt`'a girmiyor.** Sayı dosyada bir alan değil,
  derleme anında çıkan bir etiket — kareye hiç yazılmıyor.
- **Eski dosyalardaki yazılı `people` silinmiyor.** Ne kod siliyor ne de bir göç adımı var.

## Nasıl kırmızı olacak

Yeni testler `1girl` bekliyor, bugünkü kod `people` alanı boş olduğu için hiçbir sayı yazmıyor —
hepsi assertion'da düşüyor. Şema testleri de bugünkü metinde duran paragraf ve kural yüzünden
düşüyor. Import hatası yok: `build_prompts` ve `schema` bugün de var, imzaları değişmiyor.
