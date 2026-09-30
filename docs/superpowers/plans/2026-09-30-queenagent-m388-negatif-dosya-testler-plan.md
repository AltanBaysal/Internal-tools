# Madde 388 — Edit prompts olmayan negatif dosyayı söylemez — test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Amaç:** 388'in davranışını tutan testi yazmak, suite'i koşup yeni testin kırmızı olduğunu görmek,
kırmızı commit'lemek. Kod yazılmaz.

**Mimari:** Yalnız `queen-agent/backend/tests/test_skills.py` değişir. Yeni test Edit prompts'un kendi
Step 4 parçasını (`_edits_checks_step()`) ve paylaşılan `THE_CHECKS`'i sorar; tavan testi Edit
prompts'a 870 verir.

**Teknoloji:** pytest.

**Spec:** [2026-09-30-queenagent-m388-negatif-dosya-testler-design.md](../specs/2026-09-30-queenagent-m388-negatif-dosya-testler-design.md)

## Genel kısıtlar

- Tavanlar: akış 1025, Edit prompts 870 (856'dan), Improve 700.
- Test isimleri ve yorumlar İngilizce; `skip`/`xfail` yok.
- Suite yalnız CLAUDE.md'deki dört satırla, olduğu gibi, paralel koşar.

---

### Görev 1: Testler

**Dosyalar:**
- Değişir: `queen-agent/backend/tests/test_skills.py`

**Arayüzler:**
- Kullanır: `_edits_checks_step()`, `_checks()` (dosyada var).
- Üretir: uygulamanın yazması gereken ifadeler — Edit prompts'un Step 4'ünde, `Otherwise skip it`'ten
  sonra `no negative file` ve `the prompt file alone`.

- [ ] **Adım 1: Yeni test**, `test_after_an_edit_the_negative_is_written_again_only_if_the_cast_changed`'in
  hemen arkasına:

```python
def test_after_an_edit_the_closing_names_the_negative_file_only_if_there_is_one():
    # Madde 388 (30 Sep, the user: "bunlarıda düzelt"). The closing names both files, and Check 4
    # writes the negative one -- but after an edit that left the cast alone Check 4 is skipped, and a
    # scenario written before 373 has no negative file at all. The case is born only there, so the
    # editor says it beside the skip, and the shared closing stays true for the flow and Improve.
    step = _edits_checks_step()
    assert "no negative file" in step
    assert "the prompt file alone" in step
    assert step.index("Otherwise skip it") < step.index("no negative file")
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    assert "no negative file" not in _checks()
```

- [ ] **Adım 2: Tavan.** `test_the_texts_stay_short_enough_to_be_read` yorumunun sonuna 388'in
  gerekçesi, Edit prompts'un satırı `<= 870`:

```python
    # Madde 385 raises the editor's to 856. Its fix step carries 369's sentence about speech, the one
    # the flow's scenes step carries, written once for both; the flow's own count does not move.
    #
    # Madde 388 raises the editor's to 870. Its checks step says what the closing names when Check 4
    # was skipped and the scenario has no negative file -- a case the flow and Improve never meet,
    # since they always write the list, so the sentence is the editor's and the flow's count stays.
    assert len(_flow().split()) <= 1025
    assert len(_edit().split()) <= 870
    assert len(_improve().split()) <= 700
```

- [ ] **Adım 3: Suite.** Dört satır, olduğu gibi, paralel:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent pytest'te yalnız yeni test kırmızı, `"no negative file" in step` satırında.
Öteki üç suite yeşil.

- [ ] **Adım 4: Kırmızı commit** — spec, plan ve test dosyası:

```
test(queen-agent): Madde 388 red -- Edit prompts names the negative file only when there is one
```
