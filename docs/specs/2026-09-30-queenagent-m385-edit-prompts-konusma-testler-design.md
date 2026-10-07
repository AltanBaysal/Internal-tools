# Madde 385 — Edit prompts da konuşmayı sahne cümlesine yazar — testler

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 385 (Dalga 8). *Dayandığı
madde: 369 · v9-11.* Kullanıcının 369 için sözü (29 Eylül): *"ekstra queen agetn konuşam vs varsa
sceneroyunun içinde yazması lazım ki queen editordeki deepsek görük eklesin"*. 385 için (30 Eylül):
*"olur eklensin"*. Satır: Edit prompts'ta bir karede konuşma istenince söz o karenin sahne cümlesine
tırnak içinde yazılıyor, fotoğraf prompt'una girmiyor.

**Kullanıcıdan gereken:** yok. Karar, dosya ya da ölçüm beklenmiyor. Aşağıdaki kararlar subagent'ın.

## Bugün ne var

- Start a scenario'nun `Step 4 -- the scenes` adımında 369'un maddesi: *"- If the user wants someone to
  speak in a frame, write their words, in quotation marks, into that frame's scene sentence: the
  video's prompt is written from it."*
- Kareyi yazan model (`WRITE_FRAME_SYSTEM_PROMPT`) sözü aksiyon satırının dışında bırakır; fotoğraf
  prompt'u aksiyon ve girdilerden kurulur, sahne cümlesinden değil. `build_prompts` sahne cümlesini
  prompt'un yanında listeye yazar, liste queen-editor'e gider.
- Edit prompts konuşmayı hiç anmaz; 369'un testi bunu bir yokluk olarak tutuyor
  (`assert "speak" not in _edit().lower()`).

## Ne değişiyor

1. **Aynı cümle, bir kez yazılır.** 369'un maddesi `prompt.py`'de bir sabite çıkar
   (`SPEECH_IN_THE_SCENE`), ve iki skill onu taşır: Start a scenario `Step 4 -- the scenes`'te, bugün
   durduğu yerde; Edit prompts `Step 2 -- the fix`'te, değişikliği yaptığı adımda. Cümle iki metinde de
   doğru okunuyor: "o karenin sahne cümlesine yaz" Edit prompts'ta `update_frame`'in sahne alanı
   demek (`UPDATE_FRAME_SCENE`: *"Replaces the sentence there"*), ve gerekçe — video prompt'u ondan
   yazılır — aynı.
2. **Start a scenario'nun metni kelimesi kelimesine aynı kalır.** Cümle değişmez, yalnız nereden
   geldiği değişir; akış 1025 tavanında kalır.
3. **Improve konuşmayı anmaz.** Kullanıcının isteğiyle sahne yazmaz; yalnız kontrolleri koşar.
4. **Tavan.** Edit prompts bugün 827 kelime (elle sayım, 374'ün tasarımındaki ~825–830 ile uyuşuyor);
   cümle 29 kelime ekler, 856 olur. Tavan 830'dan 856'ya çıkar, gerekçesi 367, 370, 373 ve 374'ün
   yazdığı yorumda.

## Kararlar (subagent'ın, kullanıcısız)

1. **Neden paylaşılan sabit, ayrı bir madde değil.** Aynı kuralı iki metne iki kez yazmak, `prompt.py`'nin
   kaçındığı şey (`THE_IMAGE_MODEL`, `THE_CHECKS`): biri değişince öteki eskir. Cümle iki skill'de
   değişmeden doğru okunduğu için paylaşmak Start a scenario'nun metnine dokunmuyor.
2. **Edit prompts'ta araç adı yazılmaz.** Cümle sahne cümlesini söyler; onu değiştiren tek araç
   `update_frame`, ve aracın kendi açıklaması bunu söylüyor. Araç adı eklemek ayrı bir cümle demek.
3. **Fotoğraf prompt'u için ek cümle yok.** Söz sahne cümlesine gider; fotoğraf prompt'u sahne
   cümlesinden kurulmaz, ve sahneden aksiyon yazan model sözü dışarıda bırakıyor (369). Edit prompts'un
   kendi yazdığı aksiyon için ayrı bir yasak eklenmez: cümle sözün nereye gittiğini zaten söylüyor.
4. **Mevcut bir test değişir:** `test_the_scenes_step_writes_wanted_speech_into_the_frames_scene_sentence`
   Edit prompts'ta konuşmanın olmadığını soruyordu; madde tam bunu değiştiriyor. O satır kalkar, akışla
   ilgili kısmı aynen kalır.
5. **Testler olguları tutar**, 369–374'teki gibi. Edit prompts'un 2. adımı başlığından 3. adımın
   başlığına kadar kesilir.

## Testler

`queen-agent/backend/tests/test_skills.py`, Madde 374'ün bölümünün arkasında yeni bölüm *(Madde 385)*:

- `test_edit_prompts_writes_wanted_speech_into_the_frames_scene_sentence` — Edit prompts'un
  `Step 2 -- the fix` adımında `speak`, `quotation marks`, `that frame's scene sentence` var; adımın
  dışında Edit prompts'ta `speak` yok — **kırmızı**.
- `test_the_speech_sentence_is_written_once_and_both_skills_carry_it` — `SPEECH_IN_THE_SCENE` içinde
  `speak` ve `that frame's scene sentence`; akış onu `Step 4 -- the scenes`'te bir kez, Edit prompts
  `Step 2 -- the fix`'te bir kez taşır; Improve'da `speak` yok — **kırmızı** (sabit yok).

Değişen mevcut testler:

- `test_the_scenes_step_writes_wanted_speech_into_the_frames_scene_sentence` — Edit prompts'la ilgili
  yokluk satırı kalkar — yeşil kalır.
- `test_the_texts_stay_short_enough_to_be_read` — Edit prompts'un tavanı 856, gerekçesiyle — yeşil
  kalır.
