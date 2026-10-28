# Madde 436 — Queen Editor'ün testleri QueenAgent'ı okumaz, plan

> **Koşum:** bu oturumda, ana klasörde, satır satır. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** QueenAgent'ın `prompt.py`'sini yükleyen iki test dosyası yalnız Queen Editor'ü sınar.

**Yaklaşım:** Yeni davranış yok, kırmızı test yazılmaz. Bir test gider, ikisi sorusunu Queen Editor'ün
kendi suffix'ine çevirir; iki yorum bugünü söyler.

**Araçlar:** pytest, vitest.

**Spec:** [m436](../specs/2026-10-09-queen-editor-m436-araclar-ayri-design.md)

## Her yere geçerli kurallar

- Yorumlar ve docstring'ler **İngilizce**, ve yalnız bugün doğru olanı söyler.
- Dört satır birer birer koşulur, hiçbir zaman ikisi birlikte; `skip` / `xfail` yok.
- `queen-agent/`'a, yol haritasına ve belgelere dokunulmaz.

---

## Görev 1: `queen-editor/backend/tests/test_video_prompt_writer.py`

- [ ] `import importlib.util`, `import os`, `TOOL`, `QUEEN_AGENT_PROMPT` ve `_queen_agent_suffix`'i sil.
- [ ] `test_the_suffix_is_queen_agent_s_word_for_word`'u sil.
- [ ] `test_every_writer_s_system_prompt_ends_with_queen_agent_s_suffix` →
  `test_every_writer_s_system_prompt_ends_with_the_suffix`; `suffix = prompt_writer.SYSTEM_PROMPT_SUFFIX`.

## Görev 2: `queen-editor/backend/tests/test_agent_answer.py`

- [ ] `import importlib.util`, `import os`, `TOOL`, `QUEEN_AGENT_PROMPT` ve `_queen_agent_suffix`'i sil.
- [ ] `test_the_instruction_ends_with_queen_agent_s_suffix` →
  `test_the_instruction_ends_with_the_prompt_writers_suffix`: gönderilen talimat
  `prompt_writer.SYSTEM_PROMPT_SUFFIX` ile biter ve `prompt().SYSTEM_PROMPT_SUFFIX` ona eşit.

## Görev 3: İki yorum

- [ ] `features/photo_generation/data/prompt_writer.py` ve `features/agent/domain/prompt.py`'deki
  `SYSTEM_PROMPT_SUFFIX` yorumu: metin QueenAgent'ınkinden alındı; iki araç ayrı projeler, hiçbir test
  ikisini bağlamaz; hangi Queen Editor testi onu tutuyor.

## Görev 4: Tarama

- [ ] `queen-editor/` altında (`node_modules`, `dist` hariç) `queen-agent` / `queen_agent` ve
  `dirname(TOOL)` aranır; okuyan bir satır kalmamalı.

## Görev 5: Koş

- [ ] Dört satır, birer birer, depo kökünden. Beklenen: dördü yeşil; `queen-editor` 1555 → **1554**,
  öteki üçü değişmez.

## Görev 6: Commit — ana ajanın

- [ ] Spec, plan, iki test dosyası, iki kaynak dosyası. Mesajda çift tırnak yok.
