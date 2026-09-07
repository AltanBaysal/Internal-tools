# Madde 172 · test turu — şema uçar, yerine `SDXL_PROMPT_RULES` gelir

**Kaynağı:** [v7 yol haritası, Madde 172](../plans/2026-09-05-queenagent-v7-roadmap.md).
Dilim 1'in son maddesi; ardından Deneme 1. Bu tur yalnız testleri yazar.

---

## Şema neden ölüyor

`read_prompt_structure_schema` modele **dosyanın şeklini** öğretiyor: JSON örneği, hangi alanın
nereye yazıldığı, haritaların biçimi. 167–171 o şekli araçların içine aldı — model artık bir JSON
yazmıyor, **fonksiyon çağırıyor.** Yani şema, modelin artık yazamayacağı bir formu öğretiyor.

Bu m127'nin `list_files` hatasının aynısı: olmayan bir yolu anlatan bir metin, ve o hata bir
denemeye mal olmuştu.

## Ama şemanın bir yarısı yaşamak zorunda

Şekil kodun oldu; **etiket metnini hâlâ model yazıyor.** Kalite zincirinin yazılmaması, sayının
nerede durduğu, kıyafetin kimin girdisinde olmadığı — bunları hiçbir imza zorlayamaz.

**Ve o yarı ikiye ayrılıyor, çünkü artık iki ayrı yazarı var:**

| Kural ailesi | Kim yazıyor | Nereye gidiyor |
|---|---|---|
| Girdi metni — karakter, kıyafet, mekân etiketleri | **Queen**, altı harita aracıyla | `SDXL_PROMPT_RULES`, bu maddede |
| Kare metni — action, çekim, donmuş an | **Grok**, `write_frame_prompt` ile | `WRITE_FRAME_SYSTEM_PROMPT`, Madde 176 |

Şemanın action ve camera kurallarını bu maddede altı harita aracına eklemek, onları **hiç
yazmayacak** araçlara taşımak olurdu. O yüzden burada yalnız girdi yarısı yazılıyor.

## `SDXL_PROMPT_RULES` — ne taşıyor

- Etiket, cümle değil; artikel yok; örnek yoğunluk ölçüdür.
- Hepsi İngilizce — okuyan bir görsel model.
- **Kişi sayısı karakterin kendi girdisinde** *(Madde 166)*. Bu, şemanın 6. kuralının **tersi**:
  eskiden karenin `people` alanına aitti, o alan kalktı.
- **`solo` karakterin girdisinde değil** — karenin sözü. Aynı karakter bir karede yalnız, ötekinde
  yanında biriyle; girdiye yazılırsa ikisinde de yanlış olur.
- Kıyafet karakterin girdisinde değil; kıyafet giysinin adını taşır, giyenin değil; **bir girdi bir
  kişiyi giydirir.**
- Mekânın içinde insan yok, sayı yok.
- Kalite etiketi hiç yazılmaz — kod ekliyor, yazılırsa iki kere basılır.
- Değerin içinde `or` yok: model tek resim çiziyor, `or` atamayacağı bir yazı tura.

**Şemadan gelmeyenler ve sebepleri:** JSON örneği *(model yazmıyor)*; `people` alanı *(kalktı)*;
`quality` alanı *(kalktı)*; hangi adın önce geldiği *(173'ün işi)*; action ve camera kuralları
*(176'nın)*; kuralların numaralı listesi *(bir kural kitabı `skills.py`'den 96'da çıkarılmıştı,
geri getirilmiyor — kural, ilgili olduğu parametrenin yanında duruyor)*.

## Skill metinlerine minimum dokunuş

`schema.py` silinince `test_skills.py` **import'ta** kırılıyor: iki test `RULEBOOK` çekiyor. Dört
test daha şema aracını çiviliyor.

Yani 172, skill metinlerinden **şema cümlelerini** çıkarmak zorunda. **Skill'lerin yeniden yazımı
178'de kalıyor** — burada yalnız ölen bir aracın adı ve onu çeken cümleler gidiyor. Aradaki
metinler eski takımı anlatmaya devam ediyor, ve Deneme 1 skill seçmeden koşuluyor.

---

## Testler

### `test_tools.py`

| Test | İddiası |
|---|---|
| `test_the_schema_tool_is_gone` | `TOOL_SPECS`'te yok, ve `run_tool` *no tool called* diyor |
| `test_the_rules_ride_with_every_tool_that_takes_tags` | Altı araç taşıyor |
| `test_the_rules_ride_with_nothing_else` | Kalan araçların hiçbiri taşımıyor |
| `test_the_rules_put_the_count_in_the_characters_own_entry` | 166'nın kararı metinde |
| `test_the_rules_keep_solo_out_of_a_character` | Karenin sözü |
| `test_the_rules_keep_clothes_out_of_a_character` | Ve kıyafeti giysinin adıyla anıyor |
| `test_the_rules_keep_people_out_of_a_location` | |
| `test_the_rules_forbid_a_quality_chain` | Kod yazıyor, iki kere basılmasın |
| `test_the_rules_forbid_an_or` | Tek resim, atılamayan yazı tura |
| `test_the_rules_ask_for_tags_rather_than_sentences` | |
| `test_the_rules_say_nothing_about_a_frames_action` | **176'nın yarısı buraya sızmasın** — altı araç action yazmıyor |

`test_every_tool_is_declared_to_the_model`'den bir ad çıkıyor,
`test_the_schema_tool_says_what_it_answered_with` ve `test_the_schema_tool_defines_the_term_it_hands_back`
ölüyor.

### `test_modes.py`

`READS` tek ada iniyor. `test_ask_mode_reads_without_asking` ve `test_no_mode_lists_a_tool_that_is_gone`
o listeyle koşuyor.

### `test_skills.py`

Şemayı çiviyen dört test ölüyor *(`RULEBOOK`'u çeken ikisi, sırayı çiviyen biri, iki *"fetches the
schema once"*)*. Yerine bir tane geliyor: **`test_no_instruction_names_a_tool_that_is_gone`** —
her skill metnindeki her araç adı `TOOL_SPECS`'te var mı. m127'nin hatasını bir daha sessizce
yaptırmayan bekçi, ve 173 ile 178'de de koşacak.

### `test_schema.py`

**Siliniyor.** Ölen bir modülün testleri onunla gider.

### Taramanın bulduğu, ilk scope'ta olmayan iki şey

**1 · Şema bağlam kabına da giriyordu.** `context_box.schema_was_read` ve `stream_answer`'ın
*"--- prompt structure schema ---"* bloğu. Madde 129 kabı **dosyalar için** kurmuştu; şema oraya
Madde 159'un ayıkladığı şekilde yanına binmişti. Aracı silmek ikisini de siliyor:
`schema_was_read`, onu çağıran satır, ve `test_context_box.py`'nin iki testi.

**2 · `test_stream_answer.py` şema aracını "herhangi bir araç" diye kullanıyor** — **on yedi
yerde**. Bir raund geçirmek isteyen testler argümansız ve dosyaya dokunmayan bir çağrıya ihtiyaç
duyuyordu, ve bu oydu. Dosyanın kendi `a_call()`'ı zaten yerini almış durumda *(olmayan bir dosyayı
okumak)*; kalan çağrılar ona çevriliyor, `ToolCall(... "Schema")` bekleyenler `A_STEP`'e.

**Ders, 171'in dersinin devamı:** bir şeyi silen madde, o şeyi **kullanan** her yeri aramak
zorunda — testlerin sahne dekoru olarak kullandığı yerler dahil.

---

## Bu turda yapılmayanlar

- **Kod açılmıyor.**
- **`WRITE_FRAME_SYSTEM_PROMPT` yazılmıyor** — 176.
- **Skill metinleri yeniden yazılmıyor** — 178. Yalnız ölen aracın adı çıkıyor.

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **Koşan kırmızı: 21 vak'a.** On bir kural testi *(altısı parametreli)*, aracın gittiğini söyleyen
   test, araç listesi, kabın yalnız dosya tuttuğu, skill'lerin şema aramadığı iki vak'a, ve kuralın
   skill metninde olmadığı.

   **Bir tanesi bilerek yeşil doğdu:** `test_no_instruction_names_a_tool_that_is_gone`. Bugün şema
   aracı hâlâ var, yani metindeki ad geçerli; kırmızıya ancak bir ad kaydığında düşer, ve bekçi
   olarak var olması yeterli.

   **Ve bir yanlışım çıktı:** `test_stream_answer.py`'ye `a_call()` ile `A_STEP`'i **tanımlıymış
   gibi** yazdım — bu daldaki dosyada yoklar, daha önceki bir grep çıktısını bu dosyaya ait
   sandım. Toplama hatası verdi ve ikisi tanımlandı; zaten gereken tanım oydu.
3. Öteki üç takım rakamlarını korur.
4. Kırmızı commit'lenir.
