# Madde 93 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-m93-yonerge-sona-iner-testler-design.md](../specs/2026-08-27-queenagent-m93-yonerge-sona-iner-testler-design.md)
**Bu turda kod yazılmaz.** Beş test kırmızıya döner, biri yeniden ölçülür, üçü silinir.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Sözleşme

Yeni bir isim yok. Değişen tek şey `stream_answer`'ın motora verdiği listenin **şekli**:

```
bugün:   [... mesajlar, aralarına serpilmiş yönergeler ...]
sonra:   [... mesajlar ...] [{"role": "system", "content": güncel yönerge}]
```

`XaiEngine` bunun önüne `SYSTEM_PROMPT`'u koyuyor, bugünkü gibi. Yani modele giden tam sıra:
sabit yönerge · konuşma · güncel skill'in metni.

---

## 1. `backend/tests/test_stream_answer.py`

### 1.1 Silinen üç test

`test_the_same_skill_twice_running_says_it_once`, `test_a_reply_in_between_does_not_bring_it_back`,
`test_a_skill_left_and_taken_up_again_is_said_again`. Üçü de yönergenin **tekrarı** hakkında, ve
tekrar diye bir şey kalmıyor. Ayakta kalan iddiaları 1.3'ün içinde.

### 1.2 `test_a_skill_puts_its_instruction_right_before_the_message` yerine

```python
def test_the_instruction_is_the_last_thing_in_the_request(tmp_path):
    # Two measures point at the same place. Attention: accuracy is highest at the two ends of a
    # context and falls by more than a third in the middle. Cache: what is fixed stays at the
    # front so the prefix holds, and what changes sits at the end so only it goes stale.
    _, conversation = _said_with(tmp_path, ("write me a scenario", "create-scenario"))
    assert conversation[-1] == {
        "role": "system",
        "content": instruction_for("create-scenario"),
    }
    assert conversation[-2]["content"] == "write me a scenario"
```

### 1.3 `test_changing_the_skill_brings_the_new_one_in_once` yerine

```python
def test_only_the_current_skill_is_sent_whatever_came_before(tmp_path):
    # However many times the selection changed, one instruction goes and it is this turn's. Before
    # this item a chat that had changed skill four times carried four texts, the oldest of them
    # forty messages back -- and the model had to find the newest copy among them.
    _, conversation = _said_with(
        tmp_path,
        ("one", "create-scenario"),
        ("and again", "create-scenario"),
        ("now split it", "split-into-frames"),
    )
    assert _instructions(conversation) == [instruction_for("split-into-frames")]
```

### 1.4 Yeni: konuşmanın içinde yönerge yok

```python
def test_no_instruction_stands_among_the_messages(tmp_path):
    # The other half of the same move: the block did not just get a new place, the old places are
    # empty. Measured on the messages rather than on the whole request, because the one at the end
    # is the one that is supposed to be there.
    _, conversation = _said_with(
        tmp_path, ("one", "create-scenario"), ("now split it", "split-into-frames")
    )
    assert [piece["role"] for piece in conversation[:-1]] == ["user", "user", "user"]
```

> Üç `user`: `_seeded` sohbeti bir mesajla doğuruyor, `_said_with` iki tane daha ekliyor.

### 1.5 Yeni: her turda taşınıyor

```python
def test_the_instruction_moves_to_the_end_of_every_round(tmp_path):
    # An answer runs up to sixteen rounds and each sends its own request. Left where it was, the
    # block would sit behind the tool exchanges from the second round on -- and the reason this
    # item exists would stop holding after the first one.
    chats, files = _seeded(tmp_path)
    append_message(chats, "p1", "c1", "check the files", NOW, skill="verify-prompts")
    engine = ScriptedEngine([[{"tool_calls": [call("list_files")]}], [{"text": "clean"}]])
    list(stream_answer(chats, files, engine, "p1", "c1", NOW, NEVER))
    second = engine.seen[1]
    assert second[-1] == {"role": "system", "content": instruction_for("verify-prompts")}
    # And what it moved past: the round that asked for the tool, and the tool's answer.
    assert [piece["role"] for piece in second[-3:-1]] == ["assistant", "tool"]
```

## 2. `backend/tests/test_xai_engine.py` — bir yeni test

```python
def test_the_fixed_part_leads_and_the_last_word_stays_last():
    # Madde 93's shape, end to end: what is fixed at the front, what changes at the back. The
    # engine adds to the front and reorders nothing -- if it ever sorted or grouped by role, the
    # instruction would land in the middle again and nothing else would notice.
    client = FakeClient()
    tail = {"role": "system", "content": "the instruction"}
    XaiEngine(client).complete(CONVERSATION + [tail])
    assert client.seen[0] == {"role": "system", "content": SYSTEM_PROMPT}
    assert client.seen[-1] == tail
```

## 3. `backend/tests/test_chats_api.py` — bir ölçü

`test_a_selected_skill_reaches_the_engine_as_an_instruction` yönergeyi `seen[0]`'da arıyor; artık
`seen[-1]`'de:

```python
    assert with_skill.seen[-1] == {
        "role": "system",
        "content": instruction_for("create-scenario"),
    }
```

Yorumuna bir cümle giriyor: yer Madde 93'te değişti, iddia değişmedi.

---

## Beklenen kırmızı

**Beş test.** Sayıyı koşarak değil şuradan türetiyoruz: bugün yönerge mesajın **önüne** giriyor ve
skill her değiştiğinde bir tane daha ekleniyor — beş iddianın hiçbiri bugün doğru değil.

`test_a_chat_without_a_skill_is_told_nothing_extra`, `test_a_skill_nobody_knows_adds_nothing...` ve
`test_the_instruction_is_never_written_to_the_chat` **yeşil kalır**: hiçbiri yönergenin yerini
ölçmüyor.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `stream_answer.py`, `xai_engine.py`, `skills.py` bu turda açılmaz.
- **`Message.skill`'e dokunulmaz.**
- **Ön yüze dokunulmaz, `dist` derlenmez.**
