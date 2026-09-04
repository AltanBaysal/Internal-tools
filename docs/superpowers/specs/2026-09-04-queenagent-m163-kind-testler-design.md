# Madde 163 — `kind` kalkar · **test turu**

**Tarih:** 4 Eylül 2026 · **Branch:** `feat/v7` · **Kaynak:** [v7 yol haritası, Madde
163](../plans/2026-09-03-v7-roadmap.md)

Bu belge yalnız **testlerin** ne çivileyeceğini anlatır. Kodun kendisi ikinci turun işi.

## Neyi çiviliyoruz

Madde 156 sayımı koda aldı: karakterin `kind`'ına bakıp `1girl` / `2girls` üretmek. Bu madde onu
geri veriyor — ama eski yerine değil, **karakterin kendi etiketlerine**.

Gerekçe kullanıcının kendi cümlesi *(4 Eylül)*: **istem kompleksitesini azaltmak ve
basitleştirmek.** Yani bu tur bir çıktı kalitesi turu değil; ölçüsü modelin öğrenmek zorunda olduğu
yüzeyin küçülmesi. `kind` bugün o yüzeyde üç yer tutuyor ve üçü birden gidiyor:

| Nerede | Bugün ne diyor |
|---|---|
| `set_character` imzası | `kind` diye bir alan, `enum: [girl, boy]` |
| `set_character` açıklaması | *"a new one needs both a kind and tags"* |
| `SDXL_PROMPT_RULES` | *"no count of people; code writes both"* |

Yerine tek cümle kalıyor: **karakterin etiketleri kendi sayısıyla açılır** — `1girl, long teal hair`.

## Neden bugün işe yarıyor, 156 gününde yaramazken

156'nın derdi tek kareye iki kadın girdiğinde `1girl … 1girl` basılmasıydı — **herkes tek bir
kodlama parçasındayken.** Madde 139 karakter blokları arasına `BREAK` koydu; bugün her karakter
kendi parçasında duruyor ve o parçanın kendi `1girl`'ü tam olması gereken yerde. `2girls` toplamı,
herkesin tek parçada olduğu günün ilacıydı.

## Karar: yazılan tek şekil düz metin, okunan iki şekil

`set_character` bundan sonra **düz metin yazıyor** — `{"kind": …, "tags": …}` haritası hiç
kurulmuyor. `build_prompts` ise iki şekli de **okumaya devam ediyor** *(`_identity`)*: diskteki 154
sonrası dosyalar haritayı taşıyor ve FOUNDATION 1 onları dokunulmaz sayıyor.

Bunun görünür sonucu: **haritalı bir girdiye yeni etiket yazılırsa girdi düz metne döner.** Kayıp
yok — geride kalacak tek alan `kind`, ve onu okuyan kimse kalmıyor. Kazanç, `_set_entry`'nin üç araç
için **aynı** işi yapması: karakterin ayrıcalığı kalkıyor, `_changed` diye bir yardımcıya gerek
kalmıyor.

## `frame["people"]` yerinde duruyor

Okunmaya devam ediyor, çünkü elde duran her dosya onu taşıyor. Artık ne yazan var ne türeten — yalnız
okuyan. Bugünkü `test_the_people_tag_…` üçlüsü olduğu gibi kalıyor, ve yeşil kalmaları bunun kanıtı.

## Değişen testler — `test_build_prompts.py`

1. **`test_a_character_written_with_a_kind_still_builds`** — beklenen prompt türetilmiş `1girl`'ü
   kaybediyor: `f"{QUALITY}, {AYLIN}, {BEDROOM}, …"`. Bugün kod ikisini birden basıyor *(fikstürün
   kendi `1girl`'ü + türetilen)*, yani kırmızı.
2. **`test_the_kind_itself_never_reaches_the_prompt`** — çivisi sertleşiyor. Bugün `built.count("girl")
   == 1` diyor, yani türetilmiş sayıyı sayıyor; artık `"girl" not in built` diyecek. Fikstür
   `AYLIN_TAGS` sayı taşımıyor, dolayısıyla haritadaki `kind` prompta **hiçbir biçimde** düşmemeli.
3. **Yeni: `test_the_code_never_works_a_count_out_of_the_characters`** — bu maddenin ana çivisi.
   Haritalı iki karakterli, `people` alanı olmayan bir kare: promptta ne `1girl` ne `2girls` var,
   yalnız etiketlerin kendi yazdığı. Bugün `2girls` çıkıyor.
4. **Yeni: `test_each_character_carries_its_own_count_into_its_own_block`** — sayının nereye gittiği.
   Kendi sayısıyla açılan iki düz metin karakter, `BREAK`'in iki yanında kendi sayılarıyla duruyor.
   *(Bugün de yeşil — 139'un kurduğu düzen. Silinen bir kuralın yerine geçen kural, kendi testi
   olmadan yazılı sayılmaz.)*

**Silinen testler** — konusu ortadan kalkanlar: `test_one_girl_is_counted_from_her_kind`,
`test_the_count_puts_the_boy_first_whichever_way_the_frame_leads`,
`test_two_of_a_kind_are_counted_in_the_plural`, `test_the_plural_holds_for_boys_too`,
`test_the_worked_out_count_lands_where_a_written_one_lands`,
`test_a_character_with_no_kind_is_left_out_of_the_count`,
`test_a_kind_the_code_does_not_know_is_not_counted`,
`test_a_frame_with_nobody_in_it_gets_no_count_at_all`,
`test_a_written_count_wins_over_the_one_the_code_would_work_out`, `test_a_preview_carries_no_count`.

Fikstür `_kinds` **kalıyor**: haritalı girdi diskte var olmaya devam ediyor ve 1–3 numara onu
okutuyor. Adı da kalıyor — yazdığı şekil hâlâ o.

## Değişen testler — `test_tools.py`

5. **`test_set_character_adds_a_new_one`** — `kind` argümanı gidiyor, beklenen girdi düz metin:
   `characters["lara"] == "1girl, red hair"`. Bugün harita çıkıyor.
6. **`test_set_character_changes_the_one_that_is_there`** — `characters["aylin"]["tags"]` yerine
   `characters["aylin"] == "1girl, short red"`. *(Bugün `kind` verildiği için harita kuruluyor.)*
7. **`test_a_new_character_needs_both_a_kind_and_tags`**, yerine
   **`test_a_new_character_is_born_of_its_tags_alone`** — ters çevriliyor. Yalnız `tags` ile gelen
   yeni bir ad artık **kabul ediliyor**; bugün
   *"A new character needs a kind and tags"* diye reddediliyor. Etiketsiz gelen ad ise hâlâ reddedilir
   ve o çivi `test_a_new_entry_elsewhere_needs_its_tags`'in parametre listesine `set_character`
   eklenerek oraya taşınır — üç araç tek kural.
8. **`test_only_a_character_carries_a_kind` → `test_no_tool_asks_for_a_kind`** — üç `set_` aracının
   hiçbirinin parametrelerinde `kind` yok. Bugün `set_character`'da var.
9. **`test_tags_alone_leave_the_kind_where_it_was`**, yerine
   **`test_a_map_form_character_retagged_becomes_plain_text`** — haritalı `aylin`'e yalnız `tags`
   gelince girdi düz metne dönüyor. Bugün harita kalıyor
   ve `kind` korunuyor.
10. **`test_the_prompt_rules_leave_the_count_and_the_quality_to_code` →
    `test_the_prompt_rules_leave_the_quality_to_code`** — kurallar hâlâ `quality` diyor, ama artık
    `count` demiyor: `"count" not in said`. Bugün diyor.
11. **Yeni: `test_the_character_tool_asks_for_the_count_in_the_tags`** — `set_character`'ın `tags`
    açıklaması modele sayıyı yazdırıyor: içinde `1girl` geçiyor. Bugün tam tersini söylüyor
    *("no count")*.
12. **`test_a_character_and_its_new_name_change_together`** *(1828. satır)* — yeniden adlandırmayla
    birlikte etiket de verilince girdi düz metne dönüyor: `characters["ayla"] == "bob cut"`. Bugün
    harita bekliyor.

**Silinen testler:** `test_a_kind_that_is_neither_girl_nor_boy_is_refused` *(reddedilecek bir alan
yok)*, `test_a_kind_alone_leaves_the_tags_where_they_were`,
`test_a_plain_text_character_given_a_kind_becomes_the_map_form` *(haritaya geçiren kapı kapanıyor)*.

**Dokunulmayan testler ve sebebi:** `CROWDED` fikstürü haritalı kalıyor — yalnız **okunan** bir
şeklin testlerde de durması gerekiyor. Yalnız yeniden adlandıran testler *(1697. satır)* girdiyi
açmıyor, dolayısıyla haritayı da bozmuyor; yeşil kalmaları eski dosyanın dokunulmadığının kanıtı.
`kind=` argümanı geçiren ama girdinin şekline bakmayan testler *(1170, 1180, 1198, 1804)* de öyle:
argüman artık okunmuyor, sessizce düşüyor — `run_tool` hiçbir yerde tanımadığı argümanı reddetmiyor,
ve bu maddede o kural değişmiyor.

## Bu turda dokunulmayanlar

- **`AT_ONCE`, `AT_MOST`, `_STILL`, `_NOT_AS_TEXT`** — ayrı işler, ayrı turlar.
- **Ön yüz.** Hiçbir `.tsx` açılmıyor, `dist` yeniden derlenmiyor.
- **Göç adımı yok.** Diskteki `kind` alanları silinmiyor; okuyan kalmayınca zararsız bir alan olarak
  duruyorlar.

## Nasıl kırmızı olacak

`ImportError` yok — silinen adları hiçbir test `import` etmiyor *(`KINDS` ve `COUNTED` test
dosyalarında geçmiyor)*. Kırmızıların tamamı **assertion**: ya bugünkü kodun türettiği sayı fazladan
çıkıyor, ya bugünkü aracın kurduğu harita düz metin yerine geliyor, ya da bugünkü istem metni artık
yasak olan kelimeyi taşıyor. Biri `TypeError` olacak — düz metne `["tags"]` diye erişen 6 numara — ve
o da bekleniyor.

**Koşulan sonuç: 11 kırmızı, 772 yeşil**, artı defterin bilinen 2'si — toplam 13.

Beklenenden iki test kırmızı **çıkmadı**, ve ikisi de doğru:

- **6 numara** *(`test_set_character_changes_the_one_that_is_there`)* — fikstürdeki `aylin` düz metin,
  ve çağrıdan `kind` çıkınca bugünkü kod da düz metin bırakıyor. Yani bugün de yarın da yeşil; kırmızı
  sanmamın sebebi çağrının `kind` taşıdığını unutmamdı.
- **7'nin parametre listesine giren `set_character` satırı** — etiketsiz yeni bir ad bugün de
  reddediliyor, yarın da. Testin işi zaten kuralın **üç araçta aynı** olduğunu yazmak.

Yerine sayılmayan bir kırmızı geldi: `test_set_character_says_whether_it_added_or_changed`. Çağrıdan
`kind` çıkınca bugünkü kod yeni adı reddediyor, ve *"Added"* hiç yazılmıyor — 7 numaranın aynı
kırmızısı, ikinci bir yerden.
