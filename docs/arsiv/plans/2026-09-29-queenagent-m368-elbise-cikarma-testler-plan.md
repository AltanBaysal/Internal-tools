# Madde 368 — Elbise çıkarma sahnesi senaryoya, aksi söylenmedikçe eklenmez: test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Hedef:** Start a scenario'nun sahneler adımının, kıyafetin sahneden sahneye değişebildiğini ve
çıkarıldığı ya da değiştirildiği anın kullanıcı istemedikçe yazılmadığını söylediğini isteyen tek test.
Yalnız test, metin yok.

**Mimari:** Test, `START_A_SCENARIO`'yu `instruction_for("start-a-scenario")` üstünden okur ve
`STEPS[3]` ile `STEPS[4]` başlıkları arasından keser; kural o dilimde aranır, dışında ve Edit prompts'ta
aranmaz.

**Teknoloji:** pytest.

**Spec:** [2026-09-29-queenagent-m368-elbise-cikarma-testler-design.md](../specs/2026-09-29-queenagent-m368-elbise-cikarma-testler-design.md)

## Genel kısıtlar

- Testler İngilizce; yorum NEDEN'i söyler.
- `skip`/`xfail` yok.
- Suite yalnız CLAUDE.md'deki dört satırla, paralel, olduğu gibi koşar.
- Commit mesajında çift tırnak yok, amend yok.

---

### Görev 1: `test_skills.py`

**Dosyalar:** Değişir: `queen-agent/backend/tests/test_skills.py`

**Arayüzler:** Kullanır: `_flow()`, `_edit()`, `STEPS` (aynı dosyada; `STEPS` modül seviyesinde,
test çalışırken tanımlı).

- [ ] **Adım 1: Yeni bölüm**, `test_every_skill_knows_a_frame_is_one_moment_and_a_4_second_video`'nun
  altına:

```python
# --- what the scenes step leaves out (Madde 368) --------------------------------------------------
#
# 29 Sep, the user: when the outfit changes between two scenes, the flow writes the frames in between
# -- the garment coming off -- and the weak model cannot draw them. A dress in one scene and another
# in the next it draws fine. The rule belongs to the scenes step alone (the user: in the scenario is
# enough), which is where it is read while the scenes are being written.


def test_the_scenes_step_writes_no_frame_of_clothes_coming_off_unless_asked():
    said = _flow()
    start, end = said.index(STEPS[3]), said.index(STEPS[4])
    step = said[start:end].lower()
    assert "from one scene to the next" in step
    assert "taken off" in step
    assert "unless the user asks" in step
    # Asked after the presence above, so the absence cannot pass on a text nobody wrote.
    assert "taken off" not in (said[:start] + said[end:]).lower()
    assert "taken off" not in _edit().lower()
```

### Görev 2: Kırmızı

- [ ] Dört satır, paralel, olduğu gibi. Beklenen kırmızı yalnız
  `test_the_scenes_step_writes_no_frame_of_clothes_coming_off_unless_asked` — bir. Geri kalan her şey
  yeşil; queen-editor ve frontend'ler değişmez.
- [ ] Commit: `test(queen-agent): Madde 368 red -- the scenes step writes no frame of clothes coming off unless asked`
