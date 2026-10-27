# Madde 483 · H3'ün video talimatına üç kural — tasarım

**Tarih:** 22 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
483 · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey. Madde hizalanmaz, kullanıcıyla birlikte yapıldı (22 Ekim); kuralların İngilizce metni
kullanıcıya gösterildi ve onaylandı, aşağıda olduğu gibi durur.

## Ne, neden

Kullanıcının üç isteği (22 Ekim): *"Erkek sesini azalt"*; *"karakter slime girl ise görünen penisin
tek parça olduğunu belirt, karakter transparan kadının içinde penis ayrı adamın penisi ayrı hareket
ediyor"*; *"bir slime girl ise aynı normal kadının sesi çıksın, su sesi değil"* — su sesi yasağı
*"sesi ve vücudu için"*. Kurallar DeepSeek'e, prompt'u yazana söylenir *("deepseke attığımız prompta
yazmamız lazım")*.

## Bugün — koddan okunanlar

`queen-editor/backend/features/photo_generation/data/prompt_writer.py`: Queen AI (DeepSeek) karenin
fotoğrafını görür ve H3'ün prompt'unu `H3_VIDEO_INSTRUCTION`'dan yazar; `Rules` listesinde
`overall_soundscape` için bir satır var. Mutlu son'da `HAPPY_ENDING_RULE` sesi *"the moans or groans"*
diye ister. `AUDIO_INSTRUCTION` (MMAudio) ayrı; onun silinmesi backlog'da.

## Ne değişir

1. `H3_VIDEO_INSTRUCTION`'ın `Rules` listesine, `overall_soundscape` kuralının hemen arkasına, kelimesi
   kelimesine:
   - In overall_soundscape, keep the man's sounds few and quiet: write at most his quiet breathing and
     a few soft grunts. Write the woman's breathing and moans as the main voice.
   - Look at Picture 1. If a woman is a slime girl, with a translucent body made of slime, and the
     man's penis can be seen through her body, write in [Shot 1] that it is one penis: the part seen
     inside her body and the part outside are one continuous shaft, and they move together as one
     piece with the man's hips.
   - If a woman in Picture 1 is a slime girl, write her voice in overall_soundscape as a normal
     woman's voice: her breathing and moans sound like any woman's. Never write water, liquid,
     splashing or bubbling sounds for her voice or her body.
2. `HAPPY_ENDING_RULE`'da *"the moans or groans"* → *"her moans"*.
3. Sabitlerin üstündeki yorumlara maddeyi ve kullanıcının sebebini söyleyen kısa bir "neden".

`AUDIO_INSTRUCTION`'a, `LOOP_RULE`'a, `LINKED_RULE`'a ve koda dokunulmaz. Kurallar her moda girer,
çünkü hepsi `H3_VIDEO_INSTRUCTION`'ı taşır.

## Maliyet

Disk ve ağ: değişmez. Her H3 prompt'u yine tek bir DeepSeek isteği; sistem mesajı yaklaşık 130 kelime
uzar.

## Ne bozulabilir, sınırlar

- Kurallar modele söylenir, zorlanmaz: DeepSeek'in onlara ne kadar uyduğu ve H3'ün ne çizdiği yalnız
  Colab'da görülür.
- Slime girl'ü DeepSeek fotoğraftan tanır; tanımazsa kurallar devreye girmez.

## Test

`queen-editor/backend/tests/test_video_prompt_writer.py`, dosyanın kendi kural testlerinin biçiminde:
üç kuralın her biri talimatta kelimesi kelimesine; Mutlu son *"her moans"* diyor ve *"groans"*
demiyor. Uzunluk ve dynv2 testleri yeni metni de tarar.

## Bitti sayılır

- Testler yeşil, `python -m pytest queen-editor -q` yeşil.
- Colab'da bir slime girl karesinin videosunda penis tek parça hareket ediyor, kadının sesi ve
  vücudunun sesleri su sesi değil; erkeğin sesi az ve sessiz — koşunun sonundaki denemede görülür.
