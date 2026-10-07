# Madde 403 — Prompt'lar kuyruğa eklenirken yazılıp karta eklenir, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır.

**Hedef:** Test turunun kırmızı testleri yeşil; eski testler yeşil kalıyor.

**Mimari:** Kayıt yazılmış prompt'u durum saymadan tutar; döngü her turda önce borçlu prompt'ları
yazar, sonra kendi prompt'u olmayan işi karttakiyle üretir; sayfanın notu yeni zamanı söyler.

**Spec:** [m403 uygulama turu](../specs/2026-10-01-queen-editor-m403-kuyrukta-yazilir-uygulama-design.md)

## Her yere geçerli kurallar

- Kod ve yorum İngilizce, sayfanın sözü Türkçe. Yorum NEDEN'i ve yalnız şimdi doğru olanı söyler.
- Testlere dokunulmaz; yazarların metinlerine dokunulmaz; dist kurulmaz.

---

## Görev 1: `queen-editor/backend/features/photo_generation/data/photo_record.py`

`FILE`'ın altına:

```python
# A line saying a layer's prompt was written (madde 403). Nothing became of the layer: it is exactly
# as owed as it was, so the status fold passes over the line.
WRITTEN = "written"
```

`mark`'ın altına:

```python
    def prompt_written(self, project, frame, layer, file, prompt, at):
        """Write down the prompt a model wrote for a layer still owed -- the words it will be made
        with (madde 403). `file` is the layer's own name, as on every other line about it."""
        self.append(project, {"frame": frame, "layer": layer, "file": file, "status": WRITTEN,
                              "prompt": prompt, "at": at})
```

`slots()`'un döngüsünün başına `if _status_of(row) == WRITTEN: continue` ve docstring'e neden;
`prompts()`'un docstring'i bekleyen katmanı anar; `prompts()`'un altına:

```python
    def written_prompts(self, project):
        """{frame: {layer: prompt}} -- the prompt a model wrote for a layer still owed.

        It holds until the next line about that slot: the layer landing (its own row carries the
        prompt from then on), blowing up, being pulled out, deleted, or put back in line -- a layer
        queued again is written for again.
        """
        latest = {}
        for row in self._rows(project):
            latest[(_frame_of(row), _layer_of(row))] = (
                row.get("prompt") if _status_of(row) == WRITTEN else None)
        folded = {}
        for (frame, layer), prompt in latest.items():
            if isinstance(prompt, str):
                folded.setdefault(frame, {})[layer] = prompt
        return folded
```

## Görev 2: `queen-editor/backend/features/photo_generation/domain/ports.py`

`PhotoRecord`'a, `mark`'ın ve `prompts`'un yanına:

```python
    def prompt_written(self, project: str, frame: str, layer: str, file: str, prompt: str,
                       at: str) -> None:
        """Keep the prompt a model wrote for a layer still owed, on the card, until it is made."""
        ...

    def written_prompts(self, project: str) -> dict:
        """{frame: {layer: prompt}} -- the prompts written for layers still owed. A later line about
        the layer -- produced, failed, removed, deleted or put back in line -- ends it."""
        ...
```

## Görev 3: `queen-editor/backend/features/photo_generation/domain/run_loop.py`

`_prompts_of`'un altına:

```python
def _unwritten(owed, writers, record, project):
    """The first owed job whose prompt a model still has to write, or None.

    The rule a job's turn used to apply: its type has a writer, it carries no prompt of its own,
    none has been written for it yet, and the frame has words to write from -- asking with none
    would buy an invented prompt. The record is asked only when some job could need one: a run with
    no writers never asks it about words at all.
    """
    waiting = [job for job in owed if queue.type_of(job) in writers and not job["prompt"]]
    if not waiting:
        return None
    said, written = record.prompts(project), record.written_prompts(project)
    return next((job for job in waiting
                 if queue.type_of(job) not in written.get(job["id"], {})
                 and any(said.get(job["id"], {}).values())), None)
```

`job()`'da:
- `attempts, holding, written, chosen` → `attempts, holding, chosen`; bellekte yazılmış prompt yok.
- `current = owed[0]` → `writing = _unwritten(owed, writers or {}, record, project)`,
  `current = writing or owed[0]`; bekleme ve tohum yalnız `writing is None` iken.
- Rapor: yazma turunda `{**counts, "current": None, "pending": <bütün borçlular>}`.
- Try: `under`, `ending`; `writing` varsa `words = writers[kind].write(_prompts_of(…), mode,
  source=under, end=ending, scene=…)`, yoksa `prompt = current["prompt"] or
  record.written_prompts(project).get(fid, {}).get(kind, "")` ve üretim.
- Except değişmez. Sonra, yazma turundaysa: `named.steady()` altında
  `record.prompt_written(project, fid, kind, name, words, now())`, `attempts, holding = 0, None`
  *(yazmanın denemeleri üretime geçmesin)*, `continue`.
- Modülün docstring'i, `make_job`'un `writers` paragrafı ve eski "Asked here rather than when the job
  was queued" yorumu yeni kuralı söyler.

## Görev 4: yorumlar — `queue_layer.py`, `queue_references.py`

`_job`'un ve `plan_reference_cards`'ın docstring'lerinde "when its turn comes" → kuyruğa girer girmez
yazılır ve kayda eklenir (madde 403).

## Görev 5: `queen-editor/frontend/src/features/photo_generation/PhotoDetail.jsx`

Not: `"Prompt yok — üretimden önce yazılacak."`; üstündeki yorum: kuyruk her borçlu prompt'u bir şey
yapmadan önce yazar (madde 403), not o kısa arayı ve durmuş bir koşuyu anlatır.

## Görev 6: Koşu ve commit

- [ ] Dört satır paralel, yazıldığı gibi — hepsi yeşil.
- [ ] Spec, plan ve kod tek commit'te: `feat(queen-editor): 403 -- …`. dist yok.
