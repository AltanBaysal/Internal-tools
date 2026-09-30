# Madde 396 — Tur sınırı 16'dan 32'ye — test planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Amaç:** 396'nın sayısını tutan iki testi 32'ye çekmek, sayıyı anlatan test yorumlarını bugüne
getirmek, suite'i koşup iki testin kırmızı olduğunu görmek, kırmızı commit'lemek. Kod yazılmaz.

**Mimari:** Üç test dosyası değişir. `test_tools.py` ve `test_chats_api.py` sayıyı elle tutar ve
kırmızıya döner; `test_stream_answer.py`'de yalnız iki yorum değişir, iddialar `MAX_ROUNDS`'tan okur
ve yeşil kalır. `tools.py`'ye bu turda dokunulmaz.

**Teknoloji:** pytest.

**Spec:** [2026-09-30-queenagent-m396-tur-siniri-testler-design.md](../specs/2026-09-30-queenagent-m396-tur-siniri-testler-design.md)

## Genel kısıtlar

- Sayı 32; son tur araçsız (bugünkü davranış, değişmez).
- Test isimleri ve yorumlar İngilizce; yorum neden'i ve yalnız bugün doğru olanı söyler; `skip`/`xfail`
  yok.
- Kaynak satırları 100 sütunun altında, dosyaların geri kalanı gibi.
- Ön uç testlerine dokunulmaz.
- Suite yalnız CLAUDE.md'deki dört satırla, olduğu gibi, paralel koşar.

---

### Görev 1: Testler

**Dosyalar:**
- Değişir: `queen-agent/backend/tests/test_tools.py` (`test_the_round_limit_carries_the_longest_chain`)
- Değişir: `queen-agent/backend/tests/test_chats_api.py` (`test_a_running_turn_reaches_the_browser_as_progress`)
- Değişir: `queen-agent/backend/tests/test_stream_answer.py` (iki yorum)

**Arayüzler:**
- Kullanır: `MAX_ROUNDS` (`backend.features.workspace.domain.tools`), `progress` olayının JSON'u.
- Üretir: uygulamanın sağlaması gereken — `MAX_ROUNDS == 32`, ilk `progress` `{"round": 1, "of": 32,
  "tokens": 0}`.

- [ ] **Adım 1: `test_tools.py`.** Şu:

```python
def test_the_round_limit_carries_the_longest_chain():
    # list, read, a skeleton, several batches of frames, a self-check and the build. Pinned,
    # because a limit that quietly cuts the chain short looks like a model that gave up.
    assert MAX_ROUNDS == 16
```

şu olur:

```python
def test_the_round_limit_carries_the_longest_chain():
    # Start a scenario runs from Step 5 on in one turn: the frames and the build, then four checks
    # that each read the built file and build again, then the negative list. 32 is the owner's
    # number (Madde 396). Pinned, because a limit that quietly cuts the chain short looks like a
    # model that gave up.
    assert MAX_ROUNDS == 32
```

- [ ] **Adım 2: `test_chats_api.py`.** Şu satır:

```python
    assert said == {"round": 1, "of": 16, "tokens": 0}
```

şu olur:

```python
    assert said == {"round": 1, "of": 32, "tokens": 0}
```

Testin yorumu 16'dan söz etmiyor, değişmez.

- [ ] **Adım 3: `test_stream_answer.py`'nin iki yorumu.**

`test_the_instruction_moves_to_the_end_of_every_round`'da:

```python
    # An answer runs up to sixteen rounds and each sends its own request. Left where it was, the
```

şu olur:

```python
    # An answer runs up to thirty-two rounds and each sends its own request. Left where it was, the
```

`test_the_notice_is_the_requests_last_word`'de:

```python
    # Madde 93 put the instruction at the end because what is fixed leads and what changes trails.
    # The instruction is fixed for the whole turn; this sentence shows up in one round out of
    # sixteen. The same reasoning that gave 93 the last word takes it back here -- so the order is
    # extended rather than broken, and the test names both to say which one moved.
```

şu olur:

```python
    # Madde 93 put the instruction at the end because what is fixed leads and what changes trails.
    # The instruction is fixed for the whole turn; this sentence shows up in one round out of
    # thirty-two. The same reasoning that gave 93 the last word takes it back here -- so the order
    # is extended rather than broken, and the test names both to say which one moved.
```

Madde 137'nin bölüm yorumu (*"Sixteen rounds went on tools … the sixteenth round"*) o maddenin çıktığı
koşuyu anlatır; dokunulmaz.

- [ ] **Adım 4: Suite.** Dört satır, olduğu gibi, paralel; iki `npm` satırı arka planda, özetleri kendi
  çıktı dosyalarından okunur:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent pytest'te tam iki test kırmızı — `test_the_round_limit_carries_the_longest_chain`
(`assert 16 == 32`) ve `test_a_running_turn_reaches_the_browser_as_progress` (`"of": 16` ≠ `32`).
Öteki üç suite yeşil.

- [ ] **Adım 5: Kırmızı commit** — spec, plan ve üç test dosyası:

```
test(queen-agent): Madde 396 red -- the round limit is 32, and the screen hears of 32
```
