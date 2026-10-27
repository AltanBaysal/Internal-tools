# Madde 385 — Edit prompts da konuşmayı sahne cümlesine yazar — uygulama

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 385 (Dalga 8).
**Testler:** [testler tasarımı](2026-09-30-queenagent-m385-edit-prompts-konusma-testler-design.md), kırmızı
commit `06ecc37b`. Kırmızı olan iki test: `test_edit_prompts_writes_wanted_speech_into_the_frames_scene_sentence`
ve `test_the_speech_sentence_is_written_once_and_both_skills_carry_it`.

**Kullanıcıdan gereken:** yok.

## Ne yazılır

Yalnız `queen-agent/backend/features/workspace/domain/prompt.py` değişir.

1. **Yeni sabit `SPEECH_IN_THE_SCENE`**, `THE_IMAGE_MODEL`'in arkasında (iki skill metninden önce
   tanımlı olmalı). Metni, bugün Start a scenario'da duran madde, harfi harfine:

   > `- If the user wants someone to speak in a frame, write their words, in quotation marks, into that
   > frame's scene sentence: the video's prompt is written from it.`

   Sondaki satır sonu sabitte değil, `THE_IMAGE_MODEL` gibi: taşıyan metin kendi satır sonunu koyar.
   Docstring'i neden bir kez yazıldığını ve iki okurunu söyler (369, 385), ve fotoğraf prompt'unun neden
   korunduğunu: kareyi yazan model sözü aksiyonun dışında bırakır.

2. **Start a scenario** `Step 4 -- the scenes`'teki maddeyi sabitle değiştirir. Metin bayt bayt aynı
   kalır; akış 1025 kelimede.

3. **Edit prompts** `Step 2 -- the fix`'in son maddesi olarak sabiti taşır, `update_frame`'li kadro
   maddesinin arkasında. Edit prompts 827'den 856 kelimeye çıkar (tavan 856, kırmızı commit'te).

Improve'a dokunulmaz. `WRITE_FRAME_SYSTEM_PROMPT`'a dokunulmaz.

## Kararlar

- **Yer.** `THE_IMAGE_MODEL`'in arkası: iki skill'in paylaştığı parçalar orada başlıyor, ve
  `THE_CHECKS` gibi skill'lerden önce tanımlanmalı.
- **Edit prompts'ta 2. adım, 4. değil.** Değişiklik 2. adımda yapılıyor; konuşma isteği bir düzeltme
  isteği gibi okunur ve o adımda karşılanır. 3. adım zaten `build_prompts`'u yeniden çağırır, sahne
  cümlesi listeye oradan girer.
- **Modül yorumları.** `prompt.py`'nin skill bölümünün başındaki yorum *"From here a sentence enters
  only by deleting one"* der; 385 tavanı test yorumunda kendi gerekçesiyle yükseltti, bu yorum
  değişmez.
