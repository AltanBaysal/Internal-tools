# Madde 73 · Tur 1 (testler) — Plan

**Tasarım:** [2026-08-27-queenagent-m73-agentic-davranis-tabana-testler-design.md](../specs/2026-08-27-queenagent-m73-agentic-davranis-tabana-testler-design.md)
**Bu turda kod yazılmaz.** Altı test kırmızıya döner.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Bir metni nasıl sınıyoruz

Model davranışını sınayamıyoruz; sınadığımız şey **yönergenin ne söylediği.** Var olan iki test
zaten böyle çalışıyor (`"the language the user writes in" in SYSTEM_PROMPT`), ve bu altısı da öyle.

Ölçü kelime değil **ifade**: `"read it first"` gibi bir söz öbeği, tek bir kelimeden hem daha zor
tesadüfen tutar hem de metni yeniden yazarken kastı korur. Altıncısı tersten çalışıyor — bir görev
adının **bulunmaması**.

## `backend/tests/test_prompt.py` — altı yeni test

Dosyanın sonuna:

```python
# --- the behaviour that holds whatever skill is selected (Madde 73) -------------------------------
#
# Four rules that sat in the skill texts one copy each, so a chat with no skill selected had none of
# them -- and the copies drifted. What comes here is the agentic half only: how to work, never what
# the work is.


def test_the_base_looks_before_it_writes():
    # Having read it earlier in the chat is not having read it: the file on disk is what the next
    # step reads, and it may have moved on since.
    said = SYSTEM_PROMPT.lower()
    assert "read it first" in said


def test_the_base_asks_rather_than_inventing():
    # Sat in three skill texts, each in its own words. A guess is either more than the user wanted
    # or less, and nothing on the screen says which one happened.
    said = SYSTEM_PROMPT.lower()
    assert "ask" in said
    assert "invent" in said


def test_the_base_works_in_pieces_and_lands_each_one():
    # The reason was written out three times, identically: quality falls away towards the end of a
    # long stretch. And each piece reaching disk is what makes an interruption cost one piece.
    said = SYSTEM_PROMPT.lower()
    assert "one long" in said or "in pieces" in said
    assert "before the next" in said


def test_the_base_puts_a_correction_on_disk_too():
    # A correction that only lands in the chat leaves the file saying the older thing, and the file
    # is what the next step reads.
    said = SYSTEM_PROMPT.lower()
    assert "correction" in said
    assert "chat" in said and "file" in said


def test_the_base_says_what_it_did_even_when_it_did_nothing():
    # Silence is not an answer: a turn that found nothing to change and a turn that never looked
    # read exactly the same.
    said = SYSTEM_PROMPT.lower()
    assert "nothing" in said


@pytest.mark.parametrize(
    "task",
    ["scenario", "frame", "character", "prompt", "sdxl", "outfit", "structure file"],
)
def test_the_base_names_no_task(task):
    # The item's own boundary, and the one worth guarding: what goes into the base is how to work,
    # never what the work is. A task word here would make every chat carry knowledge that belongs
    # to one skill -- and would quietly answer a question Madde 94 has not asked yet.
    assert task not in SYSTEM_PROMPT.lower()
```

`import pytest` dosyanın başına giriyor; bugün yok.

## Neden bu ifadeler

| Test | Ölçü | Neden bu |
|---|---|---|
| 1 | `read it first` | Bugünkü metin `read_file`'ı tanıtıyor ama **önce** demiyor; sıra kuralın kendisi |
| 2 | `ask` + `invent` | İkisi birlikte: yalnız `ask` bugünkü metinde de tutabilirdi |
| 3 | `one long`/`in pieces` + `before the next` | Bölmek yarısı; her parçanın inmesi öteki yarısı |
| 4 | `correction` + `chat` + `file` | Üçü birden: `chat` ve `file` bugün zaten var, ayırıcı olan `correction` |
| 5 | `nothing` | *"Değişecek bir şey yoksa da söyle"* — sessizliği kapatan tek kelime |
| 6 | yedi görev adı | Sınırın bekçisi, tersten |

## Beklenen kırmızı

**Altı test** — 6 numaralı yedi kere koşuyor, yani pytest yedi satır sayıyor; hepsi bugün **yeşil**,
çünkü tabanda o kelimelerin hiçbiri yok. Yani kırmızıya dönen **beş**, ve altıncısı doğduğu anda
yeşil bir bekçi.

Sayıyı koşarak değil şuradan türetiyoruz: bugünkü taban dört paragraf, ve içinde `read it first`,
`invent`, `before the next`, `correction`, `nothing` geçmiyor.

`test_the_app_forces_no_language_of_its_own` ve `test_the_answer_follows_the_language_it_was_asked_in`
yeşil kalır.

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## Bilerek yapılmayanlar

- **Kod yazılmaz.** `prompt.py` bu turda açılmaz.
- **`skills.py` açılmaz, `test_skills.py` açılmaz** — silme 94'ün işi.
- **Ön yüz açılmaz, `dist` derlenmez.**
