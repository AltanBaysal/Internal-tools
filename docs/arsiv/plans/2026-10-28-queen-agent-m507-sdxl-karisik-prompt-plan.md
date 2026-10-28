# Madde 507 — SDXL prompt'ları tag'lerle cümleler karışık, plan

**Hedef:** SDXL rehberi girdileri (karakter, kıyafet, yer) ve eylemi Danbooru tag'leriyle kısa İngilizce
cümlelerin karışımı olarak yazdırıyor; negatif liste tag kalıyor.

**Spec:** [m507](../specs/2026-10-28-queen-agent-m507-sdxl-karisik-prompt-design.md)

## Kısıtlar

- Yalnız `sdxl-prompt-writing.md` değişir; SDXL'in iki skill'i ve Krea'nın her şeyi aynen kalır, geri
  almak tek commit.
- Kalite tag'i yok, "or" yok, karakterde solo yok, ayna yok, NSFW'de doğrudan sözcük, negatif liste ve
  kamera açısı kuralları yerinde kalır.
- Kod değişmez; tag biçimine dayanan bir yer bulunursa raporlanır.
- Önce test kırmızı, sonra metin.

### Görev 1: Testler kırmızı

**Dosyalar:** `queen-agent/backend/tests/test_tools.py`, `test_prompt.py`, `test_build_prompts.py`

- [x] `test_the_rules_ask_for_tags_rather_than_sentences` → `…_mixed_with_short_sentences`.
- [x] Yeni: `test_the_rules_that_name_a_tag_hold_for_a_sentence_too`, `test_the_negative_list_stays_tags`;
  `test_the_rules_forbid_an_or` cümleyi de arar; `…when_the_vocabulary_has_nothing` yeni cümleyi arar.
- [x] `test_the_sdxl_guide_says_nothing_about_krea` karışık satırı arar.
- [x] `test_a_sentence_reaches_the_prompt_as_written` (`build_prompts`; ilk koşuda yeşil, kod değişmiyor).
- [x] Üç dosya koşar: altı test kırmızı.

### Görev 2: Rehber

**Dosya:** `queen-agent/backend/features/workspace/skills/sdxl-prompt-writing.md`

- [x] `## Writing a tag` → `## Writing tags and sentences`, dokuz satır (spec'teki gibi); son ikisi,
  zamir ve cümle sonundaki nokta, ana ajanın 28 Ekim isteği, testleri önce kırmızı.
- [x] `## The image model`'in ikinci satırı tag demeden.
- [x] "or" kuralı cümleyi de kapsar.
- [x] Negatif listeye: *"Write the negative list in tags alone, never sentences."*

### Görev 3: Yorumlar

- [x] `domain/prompt.py`: SDXL rehberini anlatan yorum madde 507'yi söyler.
- [x] `domain/build_prompts.py`: `_tags`'in yorumu prompt'un tag ve cümle olduğunu söyler.

### Görev 4: Takım ve yol haritası

- [x] `python -m pytest queen-agent -q` — yeşil.
- [x] Yol haritasında 507 ✅, başlık "Bitti · 6/6 · dal `feat/queenagent-v12` · kullanıcının denemesini
  bekliyor". Commit'i ana ajan atar.
