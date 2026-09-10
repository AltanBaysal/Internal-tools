# Madde 208 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-10-queenagent-m208-tek-kare-araci-uygulama-design.md](../specs/2026-09-10-queenagent-m208-tek-kare-araci-uygulama-design.md)
**Test turu:** `4973df2` — altı kırmızı, üç bekçi yeşil.

**Komutlar** *(sabit satırlar, kuyruk eklenmez)*:

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Amaç:** altı kırmızıyı yeşile çevirmek; aracı, notu ve onlara yaslanan cümleleri kaldırmak.

**Yürüten:** bu oturum, tek başına.

---

## Bağlayıcı kurallar

- Yorum neden'i söyler, ve yalnız bugün doğru olanı. Şimdiki zamanda kalkan aracı anan her yorum
  ya düzeltilir ya geçmişe çekilir.
- Editör metninin kelime tavanı **200**, akışınki **450**; ikisi de bu turda küçülüyor.
- Ölen test silinir; iddiası yaşayan test bekçisine devredilmişti, tekrar yazılmaz.
- Commit mesajında çift tırnak yok; amend yok.

---

## Görev 1 · `prompt.py` — dört metin

- [ ] **Adım 1 — `EDIT_PROMPTS`, iki yol tek cümle**

Eski:

```python
    "One frame's action reads wrong: correct it yourself with update_frame. A line wanted afresh "
    "from the scene is write_frame_prompt again, with a note.\n"
```

Yeni:

```python
    "One frame's action reads wrong, or wants writing afresh from its scene: write it yourself "
    "with update_frame.\n"
```

- [ ] **Adım 2 — `ADD_SCENE`, ilk yazımı toplu araca gönder**

Eski son cümlesi:

```python
    "you mean next: a frame is born without its action, and write_frame_prompt is what "
    "writes one."
```

Yeni:

```python
    "you mean next: a frame is born without its action, and write_missing_actions writes "
    "every frame that is still without one."
```

- [ ] **Adım 3 — `WRITE_MISSING_ACTIONS`, kendi ayakları üstünde**

Eski:

```python
WRITE_MISSING_ACTIONS = (
    "Write the action of every frame in a structure file that is still without one, in one "
    "call. Each frame is asked of the same model write_frame_prompt asks, at the same time as "
    "the others, and each is shown only its own scene, cast and place. Frames that already "
    "have an action are left exactly as they are -- rewriting one is write_frame_prompt's job, "
    "with a note. There is no range and there is nothing to say twice: what is waiting is what "
    "is empty. One request failing does not undo the rest; the answer names the frames it wrote "
    "and, for any it could not, says why."
)
```

Yeni:

```python
WRITE_MISSING_ACTIONS = (
    "Write the action of every frame in a structure file that is still without one, in one "
    "call. Each frame is asked of a model kept for writing those and nothing else, at the same "
    "time as the others, and each is shown only its own scene, cast and place. Frames that "
    "already have an action are left exactly as they are -- a line that is there is changed "
    "with update_frame, in your own words. There is no range and there is nothing to say twice: "
    "what is waiting is what is empty. One request failing does not undo the rest; the answer "
    "names the frames it wrote and, for any it could not, says why."
)
```

- [ ] **Adım 4 — iki metni sil**

`WRITE_FRAME_PROMPT` ve `WRITE_FRAME_PROMPT_NOTE`. `REMOVE_FRAME` ile `WRITE_MISSING_ACTIONS`
arasında tek boş satır kalır.

---

## Görev 2 · `tools.py` — araç, not, ve üç yorum

- [ ] **Adım 1 — şemayı sil** *(`"name": "write_frame_prompt"` taşıyan sözlük, üç parametresiyle)*

- [ ] **Adım 2 — `run_tool`'un dalını sil**

```python
    if name == "write_frame_prompt":
        return _write_frame_prompt(file_store, project_id, args, engine)
```

- [ ] **Adım 3 — `_write_frame_prompt`'u sil** *(gövdesinin tamamı)*

- [ ] **Adım 4 — `_frame_seen`'in notunu al**

İmza `def _frame_seen(frame, structure):` olur; sondaki iki satır gider:

```python
    if note:
        # Last, where the instruction sits in every other request this app makes: what is fixed
        # leads and what changes trails (Madde 93).
        lines.append(f"Note: {note}")
```

Docstring'in ikinci paragrafı adların **neden** gösterildiğini yeniden söyler:

```python
    """What the writer is shown: this frame, and nothing else in the file (Madde 176).

    The user's decision of 5 September, and the reason this request stays cheap -- a file of forty
    frames would otherwise send forty casts to write one sentence. Names as well as tags, because
    the scene sentence calls people by name and the writer has to know whose tags are whose.

    A name the maps do not hold is shown without tags rather than refused: add_scene refuses those
    on the way in, so one here came from somebody editing the file by hand, and this tool is not
    where that is punished.
    """
```

Tek çağıranı `_write_missing_actions`; oradaki çağrı `_frame_seen(frame, structure)` olur ve
yanındaki *"Note is None"* cümlesi yorumdan düşer.

- [ ] **Adım 5 — `_update_frame`'in docstring'inin son cümlesi**

Eski: *"Correcting a line and having one written from the scene are two jobs now: this is the
first, and write_frame_prompt is still the second."*

Yeni:

```python
    Correcting a line and wanting one afresh from the scene both end here since Madde 208: the tool
    that took the second is gone, and neither job was ever worth carrying to a model that had not
    read the line.
```

- [ ] **Adım 6 — `_write_missing_actions`'ın docstring'i**

İlk cümlesi kalkan aracı adıyla ve şimdiki zamanda anıyor; geçmişe çekilir:

```python
    The single-frame tool took one frame per call, and a scenario of twenty-one cost twenty-one
    rounds of the main agent -- each of them resending the system prompt, the skill text and a
    context box holding a structure that grew with every write. The writer's own requests were
    never the expensive part.
```

Son paragrafındaki *"No note either -- this is the first writing, and a note is what a correction
carries."* → *"No note either: a line that is already there is changed with update_frame, in the
agent's own words."*

---

## Görev 3 · `modes.py`

- [ ] **Adım 1 — girdiyi ve yorumunu sil, toplu aracın yorumunu düzelt**

Eski:

```python
        # Madde 176. It writes to the file and it spends the user's money at a second provider --
        # the only tool here that does either by asking somebody else.
        "write_frame_prompt",
        # Madde 185. The same, once for every frame still waiting -- so this is the widest single
        # spend any tool here makes, and the quieter modes keep their gate in front of it.
        "write_missing_actions",
```

Yeni:

```python
        # Madde 185, and since 208 the only tool here that spends the user's money at a second
        # provider: one request for every frame still waiting, in one call. The widest single spend
        # any of these makes, and the quieter modes keep their gate in front of it.
        "write_missing_actions",
```

---

## Görev 4 · Ölen testler

- [ ] **Adım 1 — `test_tools.py`, Madde 176 bölümünün araç testleri**

Silinenler: `_wrote` yardımcısı, ve

- `test_the_writer_is_asked_with_the_second_part_on_the_end`
- `test_the_writer_is_handed_the_scene_the_cast_and_the_place`
- `test_the_writer_is_handed_the_note_when_there_is_one`
- `test_the_writer_is_handed_this_frame_and_no_other`
- `test_what_comes_back_is_written_to_the_frames_action`
- `test_an_action_that_is_already_there_is_written_over`
- `test_the_answer_is_a_receipt_rather_than_the_prompt`
- `test_the_tools_own_spending_comes_back_with_its_answer`
- `test_a_frame_with_no_scene_has_nothing_to_write_from`
- `test_writing_refuses_a_frame_that_is_not_there`
- `test_writing_without_a_model_says_so_rather_than_crashing`
- `test_a_request_that_falls_over_leaves_the_frame_as_it_was`
- `test_an_empty_answer_is_not_written_down`
- `test_the_single_frame_tool_is_still_there_for_a_correction`

**Kalanlar:** `FakeWriter` *(toplu testler kullanıyor)* ve yazarın sistem mesajı ile SDXL
kurallarını tutan bütün testler — onlar `WRITE_FRAME_SYSTEM_PROMPT`'a bakıyor, araca değil.

Bölüm başlığı da yeniden yazılır: artık tek kare aracının değil, **yazarın kendisinin** bölümü.

```python
# --- the frame's action, written by the model kept for those (Madde 176) --------------------------
#
# Two models, and the border between them. The agent building a scenario carries the file, the maps
# and the conversation; the writer is strong on one sentence and cannot carry the rest. The camera
# lives in that sentence too (the user's decision, 5 Sep): a model splitting one shot across two
# fields is a model doing bookkeeping instead of writing.
#
# Madde 208 left one road across that border -- write_missing_actions, which fills every waiting
# frame in one call. What is here is what the writer is told; what it is asked for is in that tool's
# own section below.
```

- [ ] **Adım 2 — `test_every_tool_is_declared_to_the_model`'i kısalt** *(ad ve Madde 176 yorumu
  çıkar; toplu aracın yorumundaki *"the tool above stays for the correction"* düşer)*

- [ ] **Adım 3 — `test_modes.py`'nin `WRITES` listesi** *(ad ve Madde 176 yorumu çıkar)*

- [ ] **Adım 4 — `test_skills.py`, `test_a_complaint_is_written_again_rather_than_edited`'i sil**
  *(bekçisi yerinde)*

---

## Görev 5 · Harcayan araç olarak kullanılan dört kurgu

`test_stream_answer.py`. Dördünde de çağrı şuna döner:

```python
        [{"tool_calls": [call("write_missing_actions", file="scene.json")]}],
```

- `test_a_tools_own_request_is_added_to_what_the_turn_spent`
- `test_a_tools_request_does_not_change_how_big_the_conversation_got`
- `test_the_turn_hands_its_engine_to_the_tool_that_needs_one`
- `test_a_tools_own_bill_moves_the_number_inside_the_round`

`_with_a_frame` **tek** bekleyen kare yazıyor, yani yazara tek istek gidiyor ve sayıların hepsi
aynı kalıyor. Üçüncü testin `engine.written[0][1]` iddiası da aynı sebeple duruyor.

---

## Görev 6 · Bayat yorumlar

- [ ] `test_tools.py:1033` — *"it belongs to whoever writes an action -- write_frame_prompt, in
  Madde 176"* → *"-- the writer write_missing_actions asks, since Madde 176"*
- [ ] `test_tools.py:1595` — *"the model's next move is write_frame_prompt on each of them"* →
  *"the model's next move names them"*
- [ ] `test_tools.py`, Madde 185 bölüm başlığı — *"write_frame_prompt takes one frame per call"* →
  geçmiş zaman, ve son cümlesindeki *"a note belongs to the correction, which is still the
  single-frame tool's job"* → `update_frame`

`test_tools.py:1930` ve `BACKLOG.md` **ellenmiyor**: ikisi de geçmiş zaman anlatıyor.

---

## Görev 7 · Süit ve commit

- [ ] **Adım 1 — arka uç:** `python -m pytest queen-agent -q` → hepsi yeşil, on beş test düşmüş.
- [ ] **Adım 2 — ön uç:** `npm test --prefix queen-agent/frontend` → 648 yeşil.
- [ ] **Adım 3 — commit.**

---

## Kendi kontrolü

- **Spec'in her maddesi bir göreve düşüyor mu?** Metinler → 1; araç, not, yorumlar → 2; kip → 3;
  ölen testler → 4; para kurguları → 5; bayat yorumlar → 6.
- **Yer tutucu var mı?** Yok.
- **Ad tutarlılığı:** `_frame_seen(frame, structure)` iki yerde geçiyor — tanımı ve
  `_write_missing_actions`'ın içindeki çağrı. Başka çağıranı yok.
