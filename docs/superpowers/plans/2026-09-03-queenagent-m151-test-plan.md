# Madde 151 — Test turu planı

**Kaynak:** [tasarım](../specs/2026-09-03-queenagent-m151-kapi-testler-design.md) ·
**Tur:** test *(kırmızı commit'lenir)*

Yalnız testler. `tools.py`'ye bu turda dokunulmuyor.

Hepsi `test_tools.py`'ye giriyor — dosyanın kendi yardımcılarıyla *(`_call`, `_outcome`, `_with`,
`_files`)*, çünkü ölçülen şey aracın cevabı ve diskte kalan.

---

## 1. `create_file` reddi — dört test

- **`test_create_file_refuses_a_structure_file`** — `.json` adına yazılmıyor; cevapta ret var.
- **`test_create_file_writes_nothing_when_it_refuses`** — ret sonrası dosya **diskte yok**. Ayrı
  test, çünkü *"hayır dedi"* ile *"yazmadı"* iki ayrı şey ve ikincisi asıl olan.
- **`test_create_file_refuses_a_structure_file_before_looking_at_the_name`** — ad zaten doluyken de
  cevap ret; *"already there"* değil. Model yoksa boş bir adla girebileceğini öğrenir.
- **`test_the_door_does_not_care_about_letter_case`** — `SCENE.JSON` da reddediliyor.

## 2. `edit_file` reddi — iki test

- **`test_edit_file_refuses_a_structure_file`** — okunabilir bir yapı dosyasında ret.
- **`test_edit_file_leaves_the_structure_untouched_when_it_refuses`** — dosyanın içeriği aynı.
- **`test_a_refused_structure_write_says_refused`** — kartın üstündeki kelime `Refused`.

## 3. Kapının fazla geniş olmadığı — iki test

Bunlar bugün de yeşil; kapının yalnız bir dosya türüne kapandığını tutuyorlar.

- **`test_read_file_still_opens_a_structure_file`** — okumak kapatılmıyor.
- **`test_the_door_is_not_in_front_of_the_structural_tools`** — `add_frames` yapı dosyasını yazmaya
  devam ediyor.

**`.md` için ayrı test yazılmıyor:** yazarken görüldü ki dosyada zaten var —
`test_reading_gives_the_contents` `create_file` ile `.md` yazıyor,
`test_editing_changes_the_one_match_and_leaves_the_rest` `.md` düzenliyor. Kapı onları düşürürse
ikisi de kırmızıya döner, yani koruma zaten yerinde. İkinci bir kopya yazmak, aynı şeyi iki yerden
söylemek olurdu.

## 4. Tamir yolu — bir test

- **`test_edit_file_still_repairs_a_broken_structure_file`** — içeriği JSON olarak okunamayan bir
  `.json` düzenlenebiliyor. Bu turda **yeşil** *(kod henüz reddetmiyor)*; kırmızıya uygulama turunda
  da düşmemesi gereken tek testtir, ve orada kapının fazla kapanmadığının kanıtı olur.

## 5. Koş ve kırmızıyı gör

```
python -m pytest queen-agent -q
```

Kırmızı: 1. ve 2. adımdaki altı test. 3. ve 4. adımdakiler yeşil.

Diğer üç satır ardışık koşulur — dördü aynı anda koşturulunca queen-agent frontend'i `test-setup.js`
üstünde toptan düşüyor *(kaynak çekişmesi, 3 Eylül'de görüldü)*.

## 6. Kırmızı commit'lenir

`test(m151): …`
