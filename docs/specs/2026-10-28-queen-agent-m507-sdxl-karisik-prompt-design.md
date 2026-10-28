# Madde 507 · SDXL prompt'ları tag'lerle cümleler karışık — tasarım

**Tarih:** 28 Ekim 2026 · **Madde:** [v12 yol haritası](../roadmaps/2026-10-24-queen-agent-v12-roadmap.md#v12-6),
507 · v12-6 · **Dal:** `feat/queenagent-v12` · **Önceki:** v11'de
[492](../arsiv/specs/2026-10-22-queen-agent-m492-krea-prompts-design.md) (iki rehber, dört skill) ve
[495](../arsiv/specs/2026-10-23-queen-agent-m495-skill-md-design.md) (skill'ler `.md`) ·
**Kurallar:** [FOUNDATION](../../queen-agent/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-agent/CODE-STANDARD.md)

## Ne ve neden

Kullanıcı, 28 Ekim, 501'in denemesinde: Nova'da şu prompt *"oldukça iyi çalışıyor"* —
*"witchnight. 1girl, flaccid futa, flaccid penis, futanari, slime girl with blue skin getting fucked in
the full nelson position, anal, she is grabbing his arms. she is wearing revealing nude style armor that
barely covers her intimate areas, …"*. Bilinen tag'ler cümlelerin arasında kalıyor, cümleler ilişkiyi
ve ayrıntıyı taşıyor. Kararı *"2 yi yapalım"*: *"Her şey senin örneğindeki gibi karışık olur.
Karakterler de cümleyle anlatılır, ör. "she is wearing revealing armor that barely covers…". Daha esnek
olur, ama aynı karakter karelerde farklı anlatılabilir."* Yalnız SDXL; Krea'nın skill'leri değişmez.

Bir deneme: kullanıcı Nova'da deniyor, daha iyi çizerse kalır, değilse geri alınır. O yüzden değişiklik
tek bir metinde toplanıyor.

## Bir karenin prompt'u nasıl kuruluyor

- Senaryo dosyası (`.sdxl.json`) dört harita tutar: `characters`, `outfits`, `locations` (her biri
  ad → metin) ve `frames`. Bir kare `characters` (ad → giydiği kıyafet adları), `location`, `scene` ve
  `action` taşır. Metinleri model araçlarla yazar (`sdxl_set_character`, `…_outfit`, `…_location`,
  `sdxl_update_frame`'in `action`'ı).
- `domain/build_prompts.py` bunları sabit sırayla birleştirir: kalite zinciri ve ilk karakterin bloğu
  (karakter, sonra kıyafetleri), her sonraki karakter kendi bloğunda, sonra eylem ve yer. Bloklar
  ` BREAK ` ile ayrılır; Queen Editor'ün `CLIPTextEncodeBREAK` düğümü bu dizgide böler.
- Blok içi birleştirme `_tags`: her parçayı virgülde böler, boşlukları kırpar, boşları atar, `", "`
  ile yeniden birleştirir.
- Metinlerin nasıl yazılacağını model, SDXL'in iki skill'inin ilk satırının okuttuğu
  `skills/sdxl-prompt-writing.md` rehberinden öğrenir. *"Write tags, never sentences"* orada; iki SDXL
  skill'inde tag'i cümleye yasaklayan bir satır yok (Step 5'teki *"never as tags"* sahne içindir).

## Değişen kural

Yalnız rehber değişiyor. `## Writing a tag` bölümü `## Writing tags and sentences` oluyor:

> - Write each entry and each frame's action as Danbooru tags mixed with short English sentences, with commas between them. A character, an outfit and a place are written this way too.
> - Where the Danbooru vocabulary has a tag for a thing, use the tag rather than a description of the same thing. The model has seen a real tag many times, and has never seen a paraphrase of it.
> - Write the tags in English, with spaces where the site writes underscores.
> - Put one thing in each tag, split the way the vocabulary splits it. Do not join two tags into one longer tag.
> - Write a short sentence for what a tag cannot say: who does what to whom, and how a body or a piece of clothing looks. Write a short sentence too when the vocabulary has no tag for it.
> - Keep each sentence short and plain, about one thing, as in she is grabbing his arms.
> - Name a character in a sentence by what tells the character apart, as in the slime girl or the man, whenever she or he could point at more than one person in the frame. A pronoun can carry an action onto the wrong person.
> - End a sentence without a full stop: commas separate the parts, and the code joins the parts with commas.
> - Every rule about tags holds for the sentences too: the image model draws every sentence, as it draws every tag.

Ve üç küçük düzeltme:

- `## The image model`: *"reads the tags of every entry and of every frame's action"* →
  *"reads every entry and every frame's action"*.
- `## What is left out`: *"Never write the word or inside a tag."* → *"… inside a tag or a sentence."*
- `## The negative list`: yeni son satır *"Write the negative list in tags alone, never sentences."*

Neden böyle:

- **Karakterler de:** kullanıcının seçtiği 2. yol bu. İlk satır karakteri, kıyafeti, yeri ve eylemi
  tek tek sayıyor; zayıf model "entry" sözünü karakter için ayrıca okumayabilir.
- **Bilinen tag kalıyor:** madde 200'ün gerekçesi (modeller Danbooru tag'leriyle eğitildi) hâlâ doğru;
  kullanıcının örneği de `1girl`, `futanari`, `full nelson`'ı tag olarak tutuyor. Cümle yalnız tag'in
  söyleyemediği için: ilişki (*kim kime ne yapıyor*) ve ayrıntı.
- **Örnek kısa ve kullanıcının kendi prompt'undan:** düzeltme 30'un dersi, uzun bir örneğin olduğu gibi
  kopyalanması. *"she is grabbing his arms"* biçimi gösteriyor, kopyalanacak bir karakter taşımıyor.
- **"Every rule about tags holds for the sentences too":** kamera açısı kuralları (Rule 1–3: *"every
  tag of the entry is meant to be in the photo"*), Step 8–10'un kontrolleri ve Step 11 "tag" diyor.
  Hepsini yeniden yazmak yerine tek satır onları cümlelere taşıyor; skill'ler hiç değişmiyor, geri
  almak tek dosya.
- **Negatif liste tag kalıyor:** negatif bütün fotoğrafa işler; bir cümle bir karakterin bütün
  tarifini herkesten silerdi. Step 11 zaten *"Write only the tags into the file"* diyor; rehberin yeni
  satırı genelleme satırının bunu cümleye açmasını kapatıyor.
- **Zamir yerine ayırt eden ad** *(ana ajan, 28 Ekim)*: karakterlerin karışması rehberin saydığı en
  büyük sorun; iki kadınlı bir karede *she* eylemi yanlış kişiye taşıyabilir.
- **Cümle sonunda nokta yok** *(ana ajan, 28 Ekim)*: parçaları virgül ayırıyor ve `_tags` onları
  `", "` ile birleştiriyor; noktayla biten cümle `"arms., next"` bırakıyordu. Kod değil kural değişiyor.
- **"An article is not a tag either" gidiyor:** cümlenin artikeli olur; tag'in tek-şey kuralı yerinde.

Değişmeyenler: kalite tag'i yok, "or" yok, karakterde solo yok, ayna yok, NSFW'de doğrudan sözcük
(Rule 6), negatif listenin kuralları, kamera açısı kuralları, sahne kuralları. SDXL'in iki skill'i ve
Krea'nın her şeyi aynen kalıyor.

## Tag biçimine dayanan kod

Okunan yerler ve sonuç:

- **`build_prompts._tags` (QueenAgent):** virgülde bölüp `", "` ile birleştiriyor. Cümle bozulmuyor:
  içindeki virgül aynı virgül olarak geri geliyor, nokta dokunulmadan kalıyor. Tek iz: bir girdi ya da
  eylem noktayla biterse arkasındaki parçayla `"arms., next"` olur. Kod değişmiyor; rehberin
  *"End a sentence without a full stop"* kuralı bunu önlüyor (ana ajanın kararı). Yorumu bugün doğru olanı söylesin diye güncelleniyor, ve bir test cümlenin
  olduğu gibi geçtiğini tutuyor.
- **BREAK:** yalnız bloklar arasında, kodun koyduğu dizgi. Cümle onu etkilemiyor.
- **Tekilleştirme yok:** ne QueenAgent'ta ne Queen Editor'de prompt üzerinde bir tekilleştirme var
  (`test_a_repeated_solo_tag_is_left_exactly_as_written` bunu zaten tutuyor).
- **Queen Editor `prompt_list.parse_photo_list`:** `photo` dizgisini bütün olarak alıyor, içine
  bakmıyor. `parse_prompts` QueenAgent listesini biçiminden (kayıt) reddediyor, içeriğinden değil.
  `render_module` üçlü tırnağı ve tırnakla biten metni zaten kaçırıyor (Krea cümleleri için, madde 492).
- **Queen Editor `comfy_photo_generator`:** metni olduğu gibi `wildcard_text` / `populated_text`'e
  yazıyor; `catalog.with_trigger` önüne LoRA kelimesini ve virgül koyuyor. Cümle bunlara dokunmuyor.
  Impact wildcard sözdizimi (`{a|b}`, `__x__`) cümlede çıkmaz.
- **Queen Editor agent'ının metinleri** (`MIXUP_RULES`, `FIX_RULES`): "remove the tag that caused the
  mix-up" diyor; kod değil model metni, karışık bir prompt'ta da okunur. Değiştirilmiyor, raporlanıyor.

## Testler

- **`test_tools.py`:** `test_the_rules_ask_for_tags_rather_than_sentences` →
  `test_the_rules_ask_for_tags_mixed_with_short_sentences` (karışık satır, karakterler de, cümlenin ne
  için olduğu; yazım bölümünde *"never sentences"* ve *"article"* yok). Yeni:
  `test_the_rules_that_name_a_tag_hold_for_a_sentence_too`, `test_the_negative_list_stays_tags`,
  `test_a_sentence_names_a_character_when_a_pronoun_could_mean_two`,
  `test_a_sentence_ends_without_a_full_stop`. `…when_the_vocabulary_has_nothing` yeni cümleyi tutuyor.
- **`test_prompt.py`:** `test_the_sdxl_guide_says_nothing_about_krea` artık eski *"Write tags, never
  sentences."* yerine karışık satırı arıyor.
- **`test_build_prompts.py`:** yeni `test_a_sentence_reaches_the_prompt_as_written` — virgüllü ve
  noktalı bir cümle girdiden ve eylemden prompt'a bütün geçiyor. Kod değişmediği için ilk koşuda yeşil;
  kodun tag biçimine dayanmadığının kanıtı.
- Kelime sınırları skill'ler içindir; skill'ler değişmediği için sınır değişmiyor.

## Maliyet ve risk

Çalışma anında değişen bir şey yok: rehber import anında bir kez okunuyor, ajan onu bir `read_file`
ile okuyor (bugünkü gibi); rehber 890 kelimeden 1047'ye uzuyor. Disk ya da ağ çağrısı eklenmiyor.

Risk, kullanıcının kendi saydığı: aynı karakter karelerde farklı anlatılabilir. Girdiler haritada bir
kez yazılıp her kareye aynen kopyalandığı için bu yalnız eylem cümlelerinde olur. İki aynı
cinsiyetten karakterli bir karede zamirin belirsizliği zamir kuralıyla karşılanıyor; tutup tutmadığını
deneme gösterecek.

Geri almak: bu maddenin commit'ini geri almak; rehber, iki yorum ve testler tek commit'te.

## Bitti sayılır

- Rehber yukarıdaki gibi; `python -m pytest queen-agent -q` yeşil.
- Kabul (kullanıcının, Nova'da): SDXL start ve edit'le yazılan karelerin prompt'ları tag'lerle kısa
  İngilizce cümlelerin karışımı; öncekinden iyi çizerse kalır. Ekranda denenmez.
