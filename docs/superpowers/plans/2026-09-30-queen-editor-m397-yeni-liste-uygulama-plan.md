# Madde 397 — Kutu QueenAgent'ın yeni listesini okur, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `51e05cae`'nin on altı kırmızı durumu yeşile, gerisi yeşil kalarak.

**Spec:** [m397 uygulama turu](../specs/2026-09-30-queen-editor-m397-yeni-liste-uygulama-design.md)

## Her yere geçerli kurallar

- Yalnız dört sunucu dosyası değişiyor: `prompt_list.py`, `start_batch.py`, `list_frames.py`,
  `regenerate.py` — hepsi `queen-editor/backend/features/photo_generation/domain/` altında. Testlere,
  ekrana ve dist'e dokunulmuyor.
- Yorum İngilizce ve yalnız bugün doğru olanı söylüyor. Cümleler aynı iki sabit.

---

## Görev 1: `domain/prompt_list.py` — iki biçim, bir ayrıştırıcı

Modül docstring'i:

```python
"""The pasted prompt list, read. Pure, and it never executes what it reads.

The text comes straight out of a notebook cell, so a leading `PROMPTS =` is stripped before
parsing and `ast.literal_eval` does the rest: it accepts literals only -- no calls, no names,
nothing executable -- so a paste can be wrong but never dangerous.

Two shapes are read (madde 397). The flat list of strings is every list written before
QueenAgent's; QueenAgent's is a record per frame -- `scene` and `photo`, each in triple quotes --
the shape its build_prompts.render_module writes.
"""
```

`parse_prompts` gidiyor; yerine iki fonksiyon:

```python
def parse_photo_list(text):
    """The photo panel's list -> [{"prompt": …}] or [{"prompt": …, "scene": …}], one per prompt.

    A record's `photo` is the prompt, and its `scene` rides with it as it was written: every frame
    the prompt opens keeps it. A flat list's entry carries no scene, so the plan line it makes is
    the line it always made.
    """
    if not text or not text.strip():
        raise InvalidPrompts(EMPTY)

    body = _ASSIGNMENT.sub("", text.strip(), count=1)
    try:
        value = ast.literal_eval(body)
    except (ValueError, SyntaxError, MemoryError, RecursionError):
        raise InvalidPrompts(UNREADABLE) from None

    # A bare string, a number, a dict, a list mixing the two shapes or holding anything else -- all
    # the same answer.
    if not isinstance(value, (list, tuple)):
        raise InvalidPrompts(UNREADABLE)
    if all(isinstance(item, str) for item in value):
        entries = [{"prompt": item.strip()} for item in value]
    elif all(isinstance(item, dict) and isinstance(item.get("scene"), str)
             and isinstance(item.get("photo"), str) for item in value):
        entries = [{"prompt": item["photo"].strip(), "scene": item["scene"]} for item in value]
    else:
        raise InvalidPrompts(UNREADABLE)

    # nova-3dcg's contract: an empty item is a deliberate "skip this line" switch, and a record with
    # no photo is the same switch.
    entries = [entry for entry in entries if entry["prompt"]]
    if not entries:
        # A list of blanks is an empty list, not a broken one.
        raise InvalidPrompts(EMPTY)
    return entries


def parse_prompts(text):
    """The flat list alone -> list[str]: what the reference pool's box reads.

    QueenAgent's list is refused here: its prompts are photo tags, and this box asks for the words a
    video is made from.
    """
    entries = parse_photo_list(text)
    if any("scene" in entry for entry in entries):
        raise InvalidPrompts(UNREADABLE)
    return [entry["prompt"] for entry in entries]
```

## Görev 2: `domain/usecases/start_batch.py` — girdi satıra yayılıyor

İçe aktarma: `from backend.features.photo_generation.domain.prompt_list import parse_photo_list`.

`plan_frames`:

```python
def plan_frames(start, entries, negative, variants, new_seed, model="", lora=""):
    """[{"id", "type", "number", "variant", "prompt", …}] photo jobs in prompt-major order.

    …(bugünkü paragraflar olduğu gibi)…

    An entry is what the list said about one prompt (prompt_list.parse_photo_list): its words, and
    the scene when QueenAgent wrote one. The scene goes on every variant's line; a flat list's entry
    has none, and its line is the one it always was.
    """
    return [{"id": frame_id(start + index, variant), "type": layers.PHOTO,
             "number": start + index, "variant": variant,
             **entry, "negative": negative, "seed": new_seed(), "model": model,
             "lora": lora}
            for index, entry in enumerate(entries)
            for variant in range(variants)]
```

`start_batch`'te `prompts = parse_prompts(text)` → `entries = parse_photo_list(text)`, ve
`plan_frames(…, prompts, …)` → `plan_frames(…, entries, …)`.

## Görev 3: `domain/usecases/list_frames.py` — her kartta `scene`

İçe aktarma: `from backend.features.photo_generation.domain.photo_name import number_of, photo_file`.

`said = record.prompts(project)`'in altına:

```python
    # What each prompt's frames were written from (madde 397), found by the prompt's number. Every
    # card holding the prompt's picture carries that number -- a video's variant, a twin, a card
    # whose photo was deleted (photo_name._parts) -- so one scene answers for the family without
    # being copied onto each of them. Every scene comes from QueenAgent's list.
    scenes = {frame["number"]: frame["scene"] for frame in planned if frame.get("scene")}
```

`card`'ın sözlüğünde `"prompts"`'un altına:

```python
                # Read-only: no request can change it. Empty is a card with none.
                "scene": scenes.get(number_of(fid), ""),
```

## Görev 4: `domain/usecases/regenerate.py` — yeni aile senaryoyu söylüyor

Plana eklenen satırda `**mark,`'ın altına:

```python
        # The scene stays with the picture (madde 397). New words start a new prompt's family, and
        # the gallery finds a scene by the family's number -- so the line that opens it says it.
        **({"scene": source["scene"]} if source["scene"] else {}),
```

## Görev 5: Koşu ve commit

- [ ] Dört satır paralel, yazıldığı gibi *(CLAUDE.md, Commands)*; iki npm satırı arka planda.
- [ ] Beklenen: dördü yeşil.
- [ ] Kod, spec ve plan tek commit'te: `feat(queen-editor): 397 -- …`.
- [ ] Denetim: `parse_prompts`'u yalnız `queue_references.py` çağırıyor *(Grep)*; FOUNDATION,
      CODE-STANDARD ve CLAUDE.md'nin Style'ı.
