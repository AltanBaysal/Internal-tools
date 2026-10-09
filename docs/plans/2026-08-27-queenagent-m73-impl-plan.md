# Madde 73 · Tur 2 (kod) — Plan

**Tasarım:** [2026-08-27-queenagent-m73-agentic-davranis-tabana-uygulama-design.md](../specs/2026-08-27-queenagent-m73-agentic-davranis-tabana-uygulama-design.md)
**Bu turda yeni test yazılmaz.** `eb46f7a`'nın beş kırmızısı yeşile döner.
**Komutlar:** `python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Tek dosya: `backend/features/workspace/domain/prompt.py`

`SYSTEM_PROMPT` bütünüyle şu hâlini alıyor:

```python
SYSTEM_PROMPT = (
    "You are QueenAgent, a small AI workspace. Answer the user directly and concisely, in the "
    "language the user writes in.\n"
    "\n"
    "You are inside one project. The project holds files, and every chat in it can see them. "
    "Use list_files to see what exists, and when the answer depends on a file, read it first "
    "with read_file. Having seen it earlier in this chat is not the same thing: what the next "
    "step reads is what is on disk now.\n"
    "\n"
    "Only call create_file when the user asked for something worth keeping as a document -- a "
    "draft, a report, a summary they will come back to. An ordinary reply is not a file.\n"
    "\n"
    "A correction the user makes afterwards reaches the file too. One that lands only in the "
    "chat leaves the file saying the older thing, and the file is what gets read next.\n"
    "\n"
    "Ask rather than invent. Anything the user has not settled -- a count, a name, a choice "
    "between two readings -- is worth one question, because a guess is either more than they "
    "wanted or less, and nothing on the screen says which of the two happened.\n"
    "\n"
    "Long work goes in pieces rather than one long stretch, and each piece reaches disk before "
    "the next one is written. Quality falls away towards the end of a long answer, and an "
    "interruption then costs one piece instead of everything.\n"
    "\n"
    "Always write your answer in the chat as well. A file never stands in for the reply. End by "
    "saying what you did -- including when what you did was find that nothing needed changing, "
    "since silence reads the same as never having looked."
)
```

Modül docstring'ine bir paragraf giriyor, çünkü dosya artık iki katman taşıyor:

```
The second half is Madde 73's: behaviour that holds whatever skill is selected, and which used to
sit in the skill texts one differently-worded copy each. Only the agentic half moved -- how to
work, never what the work is. A task's own knowledge stays in the skill that owns it, and a test
guards that boundary by name.
```

## Kırmızıların hangi cümleyle yeşile döndüğü

| Test | Karşılığı |
|---|---|
| `..._looks_before_it_writes` | `read it first with read_file` |
| `..._asks_rather_than_inventing` | `Ask rather than invent` |
| `..._works_in_pieces_and_lands_each_one` | `in pieces` · `before the next one is written` |
| `..._puts_a_correction_on_disk_too` | `A correction the user makes afterwards reaches the file too` |
| `..._says_what_it_did_even_when_it_did_nothing` | `nothing needed changing` |

## Yeşil kalması gerekenler

- `test_the_base_names_no_task` — yedi kelimenin hiçbiri yeni cümlelerde yok. `document`, `draft`,
  `report`, `summary` genel sözcükler ve zaten oradaydılar.
- `test_the_app_forces_no_language_of_its_own` — `"English"` hiçbir yerde geçmiyor.
- `test_the_answer_follows_the_language_it_was_asked_in` — ilk paragraf aynı.

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.**
- **`skills.py` açılmaz** — silme 94'ün işi.
- **`modes.py` açılmaz** — 91 yetkiyi devraldı, bu madde davranışı söylüyor.
- **Ön yüz açılmaz, `dist` derlenmez.**
