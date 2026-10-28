# Madde 331 — H3'ün video prompt yazarı `dynv2` yazmıyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Karar satırda: *"hiç yazılmasın, dynv2 talimattan tamamen çıkar,
istediğin prompt'a elle eklersin — bu olsun şimdilik"*.

## Bugün ne oluyor

Kareden'de H3 prompt'unu Grok yazıyor, `H3_VIDEO_INSTRUCTION` ile
*([xai_prompt_writer.py](../../../queen-editor/backend/features/photo_generation/data/xai_prompt_writer.py))*.
Talimatın şablonu `dynv2.` satırıyla açılıyor ve kuralı *"dynv2. is the first line. Write it for most
scenes. Leave it out only if the scene is calm or still."* *(madde 246)*. Test
`test_the_h3_instruction_opens_with_dynv2_unless_the_scene_is_calm` bu üç cümleyi çiviliyor.

Üretici *(`comfy_h3_video_generator.py`, `TRIGGER`)* `dynv2` ile başlayan bir prompt'ta kelimeyi resim
cümlesinin önüne alıyor — Motion Booster yalnız H3'ün okuduğu ilk kelime `dynv2` olunca uyanıyor.
Bunu `test_dynv2_goes_before_the_i2va_picture_sentence` ve `…fl2va…` soruyor.

## Kural

- **Talimat `dynv2`'den hiç söz etmiyor:** şablonun `dynv2.` satırı da kuralı da gidiyor. Loop kuralı
  eklendiğinde de *(madde 307)* talimatta `dynv2` yok.
- **Elle eklemek çalışmaya devam ediyor:** üretici değişmiyor; başına `dynv2.` yazılan prompt'ta
  kelime ComfyUI'ye giden metnin en başına gidiyor.
- Talimatın geri kalanı — ilk kare cümlesi, üç bölüm, kurallar — aynen kalıyor.

## Yazılacak testler

Bu turda kaynak kod değişmiyor.

### `test_video_prompt_writer.py`

1. **Değişen:** `test_the_h3_instruction_opens_with_dynv2_unless_the_scene_is_calm` →
   `test_the_h3_instruction_never_asks_for_dynv2`. `dynv2` ne düz talimatta ne loop'lu talimatta
   geçiyor — ikincisi yazıcının loop'ta gerçekten gönderdiği metinden okunuyor, sahte istemciyle.
   Bugün kırmızı: talimat `dynv2.` ile açılıyor.

## Değişen

- *(1)*: 246'da kullanıcının sözü *"most scenes"*ti; 331'de *"hiç yazılmasın"*. Test aynı soruyu —
  talimat `dynv2` hakkında ne diyor — ters cevapla soruyor.

## Bekçiler, bugün de yeşil

- `test_dynv2_goes_before_the_i2va_picture_sentence`, `test_dynv2_goes_before_the_fl2va_picture_sentence`
  — elle eklenen `dynv2` hâlâ en başa gidiyor. Bu testlerin prompt'u artık yazıcının değil, elin
  yazdığı prompt; soru aynı.
- `test_the_h3_writer_converts_the_photo_prompt_with_its_own_instruction` — sahte cevabındaki
  `dynv2` bir modelin cevabının olduğu gibi geçtiğini gösteren örnek; yazıcı cevabı süzmüyor, ve
  kullanıcı `dynv2`'yi zaten elle ekleyebiliyor. Değişmiyor.
- `test_the_h3_instruction_says_the_photo_is_the_first_frame`,
  `test_the_h3_instruction_asks_for_the_three_sections` — talimatın geri kalanı yerinde.
- Loop testleri *(307, 315)* — loop kuralı iki yazıcıya da gidiyor.

## Sorulmayan

- **Motion Booster'ın kendisi:** grafikte 0.7'de kalıyor; tetik elden geliyor.
- **Üretici yorumu** *(`TRIGGER`'ın üstündeki "the writer decides whether a scene gets it")* yanlış
  kalıyor; uygulama turu düzeltir. Testi yok — yorum.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest kırmızı — yalnız *(1)*, talimat hâlâ `dynv2.` ile
açıldığı için. Geri kalan her şey yeşil.
