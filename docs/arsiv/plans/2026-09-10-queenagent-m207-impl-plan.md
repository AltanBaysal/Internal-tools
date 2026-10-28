# Madde 207 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-10-queenagent-m207-plan-araci-uygulama-design.md](../specs/2026-09-10-queenagent-m207-plan-araci-uygulama-design.md)
**Test turu:** `f685721` — on bir kırmızı.

**Komutlar** *(sabit satırlar, kuyruk eklenmez)*:

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Amaç:** on bir kırmızıyı yeşile çevirmek — aracı silerek, iki ayrıcalığını kipe, kutu biçimini
akış metnine, planın adını da `mark_step_done`'ın aramasına vererek.

**Yürüten:** bu oturum, tek başına.

---

## Bağlayıcı kurallar

- **Yorum neden'i söyler, ve yalnız bugün doğru olanı.** `# OLD:` / `# NEW:` izi yasak.
- **Ölen test silinir, konusu yaşayan test taşınır.** Kırmızıyı yeşile boyamak için bir iddia
  gevşetilmez.
- **Akış metninin kelime tavanı 450**, ve testi tutuyor *(`test_the_texts_stay_short_enough_to_be_read`)*.
- **Commit mesajında çift tırnak yok**, ve **amend yok**.

---

## Değişen dosyalar

| Dosya | Ne olacak |
|---|---|
| `domain/prompt.py` | üç metin gider, taban cümlesi ve akışın 1. adımı değişir |
| `domain/tools.py` | şema, dal, `WRITES_FILES` girdisi gider; `mark_step_done` adı önce yazıldığı gibi arar |
| `domain/modes.py` | iki ayrıcalık `create_file`'a geçer |
| `tests/test_tools.py` | beş test ölür, biri kısalır, `_planned` `create_file`'a geçer |
| `tests/test_modes.py` | `WRITES` listesinden ad çıkar |
| `tests/test_xai_client.py` | kurgu adları `create_file` olur |

---

## Görev 1 · `prompt.py` — üç metin gider, iki metin değişir

- [ ] **Adım 1 — taban metnin plan cümlesi**

`prompt.py:61-63`. Eski:

```python
    "Long work goes in pieces rather than one long stretch, and each piece reaches disk before "
    "the next one is written. Quality falls away towards the end of a long answer, and an "
    "interruption then costs one piece instead of everything. A job of several steps starts "
    "with write_plan: the plan is where the work keeps its place, and a fresh chat picks it up "
    "from the step left open.\n"
```

Yeni:

```python
    "Long work goes in pieces rather than one long stretch, and each piece reaches disk before "
    "the next one is written. Quality falls away towards the end of a long answer, and an "
    "interruption then costs one piece instead of everything. A job of several steps starts "
    "with a plan file: the plan is where the work keeps its place, and a fresh chat picks it up "
    "from the step left open. create_file writes it.\n"
```

- [ ] **Adım 2 — akışın 1. adımı**

`prompt.py:211-215`. Eski:

```python
    "1. The plan. A chat's first turn opens with write_plan; later turns "
    "carry on from what the chat already knows. A "
    "plan already there when the chat opened is that memory: read it and carry on from the first "
    "step whose box is empty; with several, ask which. This step waits for no approval; the next "
    "question follows at once.\n"
```

Yeni:

```python
    "1. The plan. A chat's first turn writes one with create_file, each step a box: - [ ] 1. and "
    "one line of what that step is. Later turns "
    "carry on from what the chat already knows. A "
    "plan already there when the chat opened is that memory: read it and carry on from the first "
    "step whose box is empty; with several, ask which. This step waits for no approval; the next "
    "question follows at once.\n"
```

- [ ] **Adım 3 — üç metni sil**

`prompt.py:593-604` arası: `WRITE_PLAN`, `WRITE_PLAN_NAME`, `WRITE_PLAN_CONTENT`. `BUILD_PROMPTS`
ile `MARK_STEP_DONE` arasındaki boşluk tek satır kalır.

---

## Görev 2 · `tools.py` — araç gider, işaretleme adı öğrenir

- [ ] **Adım 1 — `WRITES_FILES` ve yorumu**

Yorumun son cümlesi aracı anlatıyor, ve araç kalkınca yanlış olur:

```python
# Which tools can bring a file into being. The chat draws a card for each, so an edit is not in
# here: the file was already there.
WRITES_FILES = {
    "create_file",
    "start_scenario",
    "build_prompts",
}
```

- [ ] **Adım 2 — şemayı sil**

`TOOL_SPECS`'te `"name": "write_plan"` taşıyan sözlük, iki parametresiyle birlikte.

- [ ] **Adım 3 — `run_tool`'un dalını sil**

`if name == "write_plan":` ile başlayan blok, `ToolResult(... "Saved" if born else "Rewritten")`
dönüşüne kadar.

- [ ] **Adım 4 — `mark_step_done` adı önce yazıldığı gibi arasın**

Eski:

```python
    if name == "mark_step_done":
        wanted = plan_name(safe_name(args.get("name")))
        content = file_store.read(project_id, wanted)
        if content is None:
            return ToolResult(f"There is no {wanted}.", None, wanted, "No plan by that name")
```

Yeni:

```python
    if name == "mark_step_done":
        wanted = safe_name(args.get("name"))
        content = file_store.read(project_id, wanted)
        if content is None:
            # Madde 207. write_plan pushed every name through plan_name, so a plan was always
            # <name>-plan.md and this tool could look straight there. create_file does not: the name
            # is the model's. So the name as written is tried first, and the old shape is what is
            # left to try -- without it a plan.md would be hunted for as plan-plan.md, and asking
            # again lands in the same place, because plan-plan already ends in -plan.
            wanted = plan_name(wanted)
            content = file_store.read(project_id, wanted)
        if content is None:
            # Named as the fallback would have it: that sentence is the only place left telling the
            # model what shape a plan's name is looked for in.
            return ToolResult(f"There is no {wanted}.", None, wanted, "No plan by that name")
```

`plan_name` **duruyor**, ve import'una dokunulmuyor — aynı dosyada tanımlı.

---

## Görev 3 · `modes.py` — iki ayrıcalık kipe geçer

- [ ] **Adım 1 — plan kipinin listesi**

Eski:

```python
    # Reading, and one way to write -- a plan. Given create_file without a question it could write
    # the plan and the deliverable in the same turn, which is doing the work instead of planning it.
    PLAN: READS + ("write_plan",),
```

Yeni:

```python
    # Reading, and one write -- the plan. Madde 207 took away the tool that used to be named here:
    # what made that call a plan was never the tool, it was this mode. The old fear -- that
    # create_file would let the plan and the deliverable be written in one turn -- is answered by
    # ends_the_turn below, where the first write is where the turn stops.
    PLAN: READS + ("create_file",),
```

- [ ] **Adım 2 — EDIT listesinin yorumu ve girdisi**

Eski:

```python
    # Everything, which is the mode's whole meaning: here the app does what it can do and stops for
    # nothing. write_plan is among them since Madde 97 -- in this mode a plan is an ordinary file,
    # which is why the flow can write one to keep its place and carry on in the same turn.
    EDIT: READS
    + (
        "create_file",
```

Yeni:

```python
    # Everything, which is the mode's whole meaning: here the app does what it can do and stops for
    # nothing. A plan is an ordinary file here and always was -- which is why the flow can write one
    # to keep its place and carry on in the same turn.
    EDIT: READS
    + (
        "create_file",
```

Ve listenin içindeki `"write_plan",` satırı silinir *(`"build_prompts",` ile `"add_scene"`in yorumu
arasında)*.

- [ ] **Adım 3 — `ends_the_turn`**

```python
def ends_the_turn(mode, tool):
    """Whether this call is where the turn stops.

    One pair rather than a count: the rule is not "write once", it is "the plan is written, so the
    next move is the user's". The same call in another mode is an ordinary write.

    Asked of the call rather than of what it returned. A create_file refused for a name already
    taken ends the turn too -- the user reads the refusal and decides what happens next, which is
    the same place the rule was taking them anyway.
    """
    return mode == PLAN and tool == "create_file"
```

---

## Görev 4 · Ölen ve taşınan testler

- [ ] **Adım 1 — `test_tools.py`, beş testi sil**

`# --- the plan tool (Madde 91) ---` bölümünün üçü:

- `test_a_plan_is_written_under_a_name_that_says_it_is_one`
- `test_writing_a_plan_again_replaces_it`
- `test_only_the_first_plan_reports_a_born_file`

ve iki tarif testi:

- `test_the_plan_tool_does_not_demand_a_read_of_what_the_turn_just_wrote`
- `test_write_plan_ends_only_the_turn_that_was_asked_to_plan`

Bölüm başlığı da onlarla gider; `test_an_unknown_tool_does_not_bring_the_loop_down` bir üst
bölümde kalır.

- [ ] **Adım 2 — `test_every_tool_is_declared_to_the_model`'i kısalt**

Kümeden `"write_plan"` ve onu anlatan iki satırlık yorum çıkar.

- [ ] **Adım 3 — `_planned` yardımcısı `create_file`'a geçsin**

```python
def _planned(tmp_path, content=PLAN):
    # Written the way the model writes one since Madde 207: an ordinary file, named so it reads as
    # a plan.
    files = _files(tmp_path)
    _call(files, "create_file", name="bar-scene-plan.md", content=content)
    return files
```

Bu yardımcıya yaslanan beş `mark_step_done` testi değişmiyor: hepsi `bar-scene` adıyla soruyor ve
yedek onları buluyor.

- [ ] **Adım 4 — `test_modes.py`'nin `WRITES` listesinden adı çıkar**

`"write_plan",` satırı silinir. Bu liste `ask` kipinin testini besliyor, ve var olmayan bir ad
orada hiçbir şey iddia etmeden yeşil geçerdi.

- [ ] **Adım 5 — `test_xai_client.py`'nin kurgu adları**

Üç testte `name="write_plan"` ve `"function": {"name": "write_plan"` geçiyor. `create_file`'a
çevrilir; iddialar değişmiyor, çünkü o testler parçaların birleşmesini ölçüyor.

---

## Görev 5 · Süit ve commit

- [ ] **Adım 1 — arka uç**

```bash
python -m pytest queen-agent -q
```

Beklenen: hepsi yeşil, toplam beş test düşmüş.

**Kelime tavanı burada görülür:** akışın 1. adımı büyüdü. `test_the_texts_stay_short_enough_to_be_read`
kırmızı verirse kesilecek yer bu adımın kendi tekrarıdır — *"later turns carry on from what the chat
already knows"* ile *"A plan already there when the chat opened is that memory"* aynı şeyin iki
söylenişi, ve 10 numaralı düzeltme zaten ikincisini koruyup birincisini kendi satırına almıştı.

- [ ] **Adım 2 — ön uç**

```bash
npm test --prefix queen-agent/frontend
```

Beklenen: 648 yeşil.

- [ ] **Adım 3 — commit**

---

## Kendi kontrolü

- **Spec'in her maddesi bir göreve düşüyor mu?** Metinler → 1; araç ve arama → 2; kip → 3; testler
  → 4. Açık kalan yok.
- **Yer tutucu var mı?** Yok.
- **İsim tutarlılığı:** `plan_name` ve `safe_name` ikisi de `tools.py`'de tanımlı, import
  gerekmiyor. `_WITHOUT_ASKING`, `READS`, `ends_the_turn` adları `modes.py`'nin bugünkü adları.
