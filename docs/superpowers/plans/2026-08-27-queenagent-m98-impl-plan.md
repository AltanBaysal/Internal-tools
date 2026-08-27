# Madde 98 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-27-queenagent-m98-karakter-denemesi-uygulama-design.md](../specs/2026-08-27-queenagent-m98-karakter-denemesi-uygulama-design.md)
**Tur 1:** on dört kırmızı commit'lendi *(`cea56ca`)*. Bu turda test yazılmaz.
**Komut:** `python -m pytest queen-agent -q`

---

## 1 · `domain/naming.py` — ad katlama

```python
def folded(raw):
    """A name from the model, folded into another name: aylin, or yan-karakter.

    Sibling of tools.safe_name rather than the same rule: that one cleans a file name and keeps the
    dot, because the extension lives there. This one is going inside a file name, so the dot goes
    the way every other separator does.
    """
    import re

    return re.sub(r"[^A-Za-z0-9-]+", "-", str(raw or "")).strip("-").lower()
```

`import re` dosyanın başına çıkıyor, gövdeye değil.

## 2 · `domain/build_prompts.py` — kurucu ve adı

`from backend.features.workspace.domain.naming import folded` en başa.

`prompts_name`'in altına:

```python
def character_prompts_name(source, character):
    """The try is named after both, so two characters can be looked at side by side and neither
    lands in the scene's own list."""
    stem, dot, _ = source.rpartition(".")
    return f"{stem if dot else source}-{folded(character)}.py"
```

`build_prompts`'un altına:

```python
def build_character_prompts(structure, character):
    """One character on their own, once for every outfit the file names.

    The same joining a frame goes through, so what is seen here is what a frame will show. No count:
    how many people are in a picture is a frame's own field, and there is no frame here.
    """
    if not isinstance(structure, dict):
        raise BadStructure(
            "A structure file is a JSON object with characters, locations and frames."
        )

    characters = structure.get("characters") or {}
    if character not in characters:
        # The sentence a frame gets, without the frame number: there is no frame to name.
        raise BadStructure(
            f"{character} is not in characters; known: {', '.join(sorted(characters)) or 'nothing'}"
        )

    quality = structure.get("quality", "")
    identity = characters[character]
    outfits = structure.get("outfits") or {}
    if not outfits:
        return [_tags([quality, identity])]
    return [_tags([quality, identity, worn]) for worn in outfits.values()]
```

## 3 · `domain/tools.py` — sekizinci araç

Import satırı:

```python
from backend.features.workspace.domain.build_prompts import (
    build_character_prompts,
    build_prompts,
    character_prompts_name,
    prompts_name,
    render_module,
)
```

`WRITES_FILES` sekizinciyi alıyor:

```python
WRITES_FILES = {"create_file", "build_prompts", "build_character_prompts", "write_plan"}
```

`TOOL_SPECS`'te `build_prompts`'un ardına:

```python
    {
        "type": "function",
        "function": {
            "name": "build_character_prompts",
            "description": (
                "Build a try list for one character: the same joining a frame gets, once for every "
                "outfit the structure names. Writes a Python file named after the structure and "
                "the character, replacing what it wrote last time."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "The structure file's name."},
                    "character": {"type": "string", "description": "Which character to try."},
                },
                "required": ["name", "character"],
            },
        },
    },
```

`run_tool`'da, `build_prompts` dalının ardına:

```python
    if name == "build_character_prompts":
        return _try_character(file_store, project_id, args)
```

Ve `_build`'in altına:

```python
def _try_character(file_store, project_id, args):
    """One character, looked at before it enters a frame. The reading is _build's, the building is
    the other constructor's."""
    source = safe_name(args.get("name"))
    content = file_store.read(project_id, source)
    if content is None:
        return ToolResult("There is no file by that name.", None, source, "No file by that name")

    try:
        structure = json.loads(content)
    except json.JSONDecodeError as broken:
        return ToolResult(f"{source} is not valid JSON: {broken}", None, source, "Not valid JSON")

    character = str(args.get("character") or "")
    try:
        prompts = build_character_prompts(structure, character)
    except BadStructure as refused:
        return ToolResult(str(refused), None, source, "Refused")

    target = character_prompts_name(source, character)
    written = file_store.write(project_id, target, render_module(prompts))
    return ToolResult(
        f"Wrote {len(prompts)} prompts to {written}.",
        written,
        source,
        counted(len(prompts), "prompt"),
    )
```

## 4 · `domain/modes.py`

```python
    EDIT: READS
    + ("create_file", "edit_file", "build_prompts", "build_character_prompts", "write_plan"),
```

## 5 · Koş

```
python -m pytest queen-agent -q
```

Beklenen: on dört kırmızı yeşil. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

## 6 · Commit

```
feat(queen-agent): a character can be looked at before it enters a frame
```
