# Madde 390 — v9'da yazılan prompt'lar öncekilerle aynı biçimde: testler

**Madde:** [v9 roadmap, Dalga 8, 390](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) —
kullanıcı, 30 Eylül: "promtplar önceki promtplarla aynı formatta yazılmış mı bu kontrol et
yazılmadıysa düzelt bir task sonra ben okuycam onları".

**Kullanıcıdan gereken:** yok. Madde yalnız biçime dokunur, anlama asla; anlamı değiştirmeden
düzeltilemeyen her fark aşağıda açık nokta olarak kullanıcıya bırakılır, ve kullanıcı metinleri
maddeden sonra okur.

## "v9'dan önce" ve "v9'da değişen"

- **Önce:** `6c283845` (v9 dalının main'den ayrıldığı commit).
- **Değişen:** `git diff 6c283845 HEAD -- queen-agent/backend` içinde modele giden her metin:
  `prompt.py`'de `THE_IMAGE_MODEL`, `SPEECH_IN_THE_SCENE`, `THE_CHECKS`, `EDIT_PROMPTS`,
  `START_A_SCENARIO`, `IMPROVE`, `WRITE_FRAME_SYSTEM_PROMPT`, `ADD_CHARACTER_TAGS` (yalnız bir cümle
  silindi), `BUILD_PROMPTS`, `WRITE_NEGATIVE`, `WRITE_NEGATIVE_TAGS`; `tools.py`'de `write_negative`
  aracının tanımı ve `_write_negative`'in modele döndürdüğü üç cevap. `SYSTEM_PROMPT`, `LAST_ROUND`,
  bağlam kutusu metinleri ve öteki araç tanımları v9'da değişmedi.

## v9'dan önceki biçim kuralları

Yalnız v9 öncesi metinlerin tutarlı biçimde tuttuğu kural sayılır; birbirini tutmayan yerde kural
yoktur.

1. **Skill metni bir persona paragrafıyla açılır** (`You are an expert ...`), ardından boş satır.
   Örnek: `"You are an expert SDXL prompt writer. The prompts you work on are already written: ..."`.
2. **Adım başlığı `Step N -- başlık`**: büyük `Step`, rakam, ` -- `, küçük harfli başlık, sonunda
   noktalama yok; önünde boş satır. Örnek: `"Step 2 -- the fix\n"`.
3. **Başlığın altındaki her talimat `- ` ile başlayan bir madde**, bir satır, bir ya da birkaç cümle.
   Başlıksız serbest paragraf yalnız metnin açılışında durur. Örnek: `"- Read the scenario file the
   request names. If more than one could be it, ask which.\n"`.
4. **Araçlar çıplak, küçük harfli snake_case adlarıyla anılır**, tırnaksız ve ters tırnaksız.
   Örnek: `"write it yourself with update_frame."`.
5. **Tire ` -- `** (iki eksi, iki yanda boşluk). Örnek: `"update_location -- one change reaches every
   frame naming it."`.
6. **Metinde bir adıma büyük harfle ve rakamla atıf yapılır.** Örnek: `"Ask Step 2's question in the
   same turn."`.
7. **Kullanıcının söylediği söz çift tırnak içinde yazılır.** Örnekler: `'- "You decide" covers that
   step only.'`, `'one \"you decide\" is not permission for the rest.'`, ve `REFUSED_WORDS`'ün
   `' They said: "{reason}"'`'i. Ad olmuş "yes" bunun dışında: `"wait for their yes"` tırnaksız.
8. **Örnekler iki noktadan sonra, tırnaksız, virgülle sıralanır.** Örnek: `"Name what is visible of
   them directly: erect penis, penis penetrating vagina, mouth on penis."`; araç parametrelerinde
   `as in` ile: `"A short file name, as in notes.md."`.
9. **Ortak bir metin boş satırdan sonra eklenir** (`"\n" + SDXL_PROMPT_RULES`), ya da cümle sonuna
   boşlukla (`f"{ADD_CHARACTER_TAGS} {AN_ENTRYS_NEW_TAGS}"`).
10. **Araç tanımı** buyruk kipinde tek bir ilk cümle, ardından `- ` maddeleri; kendinden söz ederken
    `This tool`. Parametre tanımı noktayla biten bir ifade. Örnek: `BUILD_PROMPTS`, `CREATE_FILE_NAME`.
11. **Kısaltma yok** (`Do not`, `cannot`); **İngiliz yazımı** (`colour`).
12. **Satır ve paragraf:** metin sonunda satır sonu yok; paragraflar tek boş satırla ayrılır.

Kural olmayanlar (v9 öncesi kendi içinde tutmuyor): Oxford virgülü (`"a preamble, a quotation mark,
or a comment"` ↔ `"update_character, update_outfit or update_location"`), `someone`/`somebody`
(ikisi de `WRITE_FRAME_SYSTEM_PROMPT`'ta), maddenin tam cümle mi olduğu (`"- Who is in a frame, ...:
update_frame, ..."`), sayıların yazıyla mı rakamla mı olduğu (`"five steps"` ↔ `OPENED_FILES`'ın
`{limit}`'i), parametre tanımının buyruk mu ifade mi olduğu (`ADD_CHARACTER_TAGS` ↔
`EDIT_FILE_OLD`), başlığın `the` ile mi başladığı (`"the fix"` ↔ `"what the request is about"`),
başlık biçimi (`Step N -- ...` ↔ `How a step runs:`).

## v9 parçalarının denetimi

| Parça | Sonuç |
|---|---|
| `THE_IMAGE_MODEL`, ve üç skill'de persona'dan sonra boş satırla yeri | uyuyor (9, 12) |
| `SPEECH_IN_THE_SCENE`, ve iki skill'de madde olarak yeri | uyuyor (3, 4) |
| `THE_CHECKS`: ilk dört madde | **kural 7'yi bozuyor**: `when the user says continue` |
| `THE_CHECKS`: `Check N -- ...` başlıkları ve maddeleri | uyuyor (2, 3, 4, 5, 8) |
| `THE_CHECKS`: kapanış paragrafı | kural 3'ten ayrılıyor — açık nokta, aşağıda |
| `EDIT_PROMPTS`: Step 2'ye eklenen, Step 3 ve Step 4 | uyuyor (2, 3, 6) |
| `START_A_SCENARIO`: persona, Step 4'e eklenen, Step 5, Step 6 | uyuyor (1, 3, 6) |
| `IMPROVE` | uyuyor (1, 2, 3, 4) |
| `WRITE_FRAME_SYSTEM_PROMPT`: açılış ve konuşma maddesi | uyuyor (3, 11) |
| `ADD_CHARACTER_TAGS` (silinen cümle) | uyuyor |
| `BUILD_PROMPTS`, `WRITE_NEGATIVE`, `WRITE_NEGATIVE_TAGS` | uyuyor (10) |
| `_write_negative`'in cevapları | v9 öncesi cevaplarla aynı kalıpta (`"A new {single} needs tags."`, `"Saved as {written}."`) |

## Test

Tek bir kural bozuluyor, ve mekanik olarak denetlenebilir: skill metinlerinde `the user says`'ten
sonra gelen söz çift tırnakla açılır. Üç skill de `THE_CHECKS`'i taşıdığından test üçü için
parametrelidir; önce ifadenin metinde olduğunu sorar ki boş bir metinde geçmesin.

- `test_skills.py`'ye: `test_a_word_the_user_says_is_written_in_quotation_marks[skill]` — üç skill
  için **kırmızı**.

Bozulmayan kurallar için test yazılmaz.

## Açık noktalar (kullanıcıya; düzeltilmez)

1. **`THE_CHECKS`'in kapanışı serbest bir paragraf.** v9 öncesinde başlığın altındaki her talimat
   bir madde; kapanış eskiden Step 5'in son maddesiydi. Madde yapmak ya onu Check 4'ün içine alır
   (Edit prompts Check 4'ü atlayabildiği için kapanış da atlanabilir) ya da kendi başlığını ister
   (yeni söz, ve Start a scenario 1025/1025'te).
2. **İmge modelinin adı.** v9 öncesi üç yerde `SDXL-family image model` der; `THE_IMAGE_MODEL`
   `a weak text-to-image model of the SDXL family` der. Adın kendisi 367'de kullanıcının sözü
   ("zayıf bir text-to-image modeli"); değiştirmek bir yeniden yazım olur.
3. **`Check 3 -- can it be drawn`** v9 öncesinde benzeri olmayan soru biçimli bir başlık; v9 öncesi
   başlıklar arasında kural olmadığından düzeltilmez.
