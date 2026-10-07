# Madde 396 — Tur sınırı 16'dan 32'ye — uygulama planı

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Amaç:** Kırmızı iki testi (`9095d2b1`) `MAX_ROUNDS`'u 32 yaparak yeşile getirmek; sayının yorumunu ve
`_asked`'in docstring'ini bugüne getirmek.

**Mimari:** Bir sabit ve iki metin. `stream_answer` döngüyü, son turu ve `of`'u `MAX_ROUNDS`'tan okuduğu
için başka kod değişmez.

**Teknoloji:** Python, pytest.

**Spec:** [2026-09-30-queenagent-m396-tur-siniri-uygulama-design.md](../specs/2026-09-30-queenagent-m396-tur-siniri-uygulama-design.md)

## Genel kısıtlar

- Sayı 32; son tur araçsız kalır.
- Yorum neden'i ve yalnız bugün doğru olanı söyler; eski sayıdan söz etmez, kullanıcının söylemediği bir
  neden yazmaz.
- Kaynak satırları 100 sütunun altında.
- Testlere, ön uca ve `dist`'e dokunulmaz.
- Suite yalnız CLAUDE.md'deki dört satırla, olduğu gibi, paralel koşar.

---

### Görev 1: Sayı, yorumu ve docstring

**Dosyalar:**
- Değişir: `queen-agent/backend/features/workspace/domain/tools.py` (`MAX_ROUNDS` ve üstündeki yorum)
- Değişir: `queen-agent/backend/features/workspace/domain/usecases/stream_answer.py` (`_asked`'in docstring'i)
- Test: `queen-agent/backend/tests/test_tools.py`, `queen-agent/backend/tests/test_chats_api.py` (commit'li,
  dokunulmaz)

**Arayüzler:**
- Üretir: `MAX_ROUNDS == 32`; ilk `progress` `{"round": 1, "of": 32, "tokens": 0}` — testlerin istediği.

- [ ] **Adım 1: `tools.py`.** Şu:

```python
# The longest sensible chain is the structured prompt run: read the pair, open the scenario, fill
# the three maps, add the scenes, build. Fifteen rounds carry it and the sixteenth closes the
# turn (Madde 137); an unbounded loop would burn both money and time. Reaching the limit is a stop,
# not a failure -- which is why the number has to be generous: a chain cut short looks exactly like
# a model that gave up.
MAX_ROUNDS = 16
```

şu olur:

```python
# The longest chain is Start a scenario from Step 5 on, which runs in one turn: the frames and the
# build, then four checks that each read the built file and build again, then the negative list.
# 32 rounds is the owner's number (Madde 396), and the last of them closes the turn (Madde 137); an
# unbounded loop would burn both money and time. Reaching the limit is a stop, not a failure --
# which is why the number has to be generous: a chain cut short looks exactly like a model that
# gave up.
MAX_ROUNDS = 32
```

- [ ] **Adım 2: `stream_answer.py`, `_asked`'in docstring'i.** Şu:

```
    settled before the first round and holds for the whole turn, while this shows up in one round
    out of sixteen. The order is extended rather than broken.
```

şu olur:

```
    settled before the first round and holds for the whole turn, while this shows up in one round
    out of thirty-two. The order is extended rather than broken.
```

- [ ] **Adım 3: Suite.** Dört satır, olduğu gibi, paralel; iki `npm` satırı arka planda, özetleri kendi
  çıktı dosyalarından okunur:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

Beklenen: queen-agent pytest 972 geçti, 0 kırmızı; öteki üç suite yeşil (836, 1160, 749).

- [ ] **Adım 4: Commit** — uygulama spec'i, plan, `tools.py` ve `stream_answer.py`:

```
feat(queen-agent): 396 -- a turn reaches the model up to 32 times, and the last still has no tools
```
