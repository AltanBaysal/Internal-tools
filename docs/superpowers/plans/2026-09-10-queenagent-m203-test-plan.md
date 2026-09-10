# Madde 203 · Tur 1 (testler) — Plan

**Tasarım:** [2026-09-10-queenagent-m203-adim-araci-testler-design.md](../specs/2026-09-10-queenagent-m203-adim-araci-testler-design.md)
**Kaynak:** [yol haritasının Madde 203'ü](2026-09-06-queenagent-v8-roadmap.md), ve
[düzeltme log'unun 11 numarası](../../2026-09-09-queenagent-metin-duzeltmeleri.md).

**Bu turda kod yazılmaz.** Altı test kırmızıya döner; yedi test ile iki yardımcı silinir.

**Komutlar** *(sabit satırlar, kuyruk eklenmez)*:

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Yürüten:** bu oturum, tek başına.

---

## Bağlayıcı kurallar

- **Kalkan şeyin davranış testi gider** — yol haritasının kendi cümlesi: *"`_ticked` ve testleri
  gider."* Konusu olmayan bir test hiçbir şey tutmaz. Bu, 190'ın *"hiçbir test silinmiyor"*
  kuralıyla çelişmiyor: o kural bir metnin **yeniden yazılması** içindi, bu bir **kaldırma**.
- **Yokluk `_WITHOUT_ASKING`'ten okunur, `needs_permission`'dan değil.** Tanımadığı araca `False`
  diyor: kalkmış bir ad üstünde dönen döngü hiçbir şey iddia etmeden yeşil geçer. Bu koşu bu tuzağı
  iki kez kaydetti *(205, 206)*.
- **Ders taşınır, atılmaz.** Silinen iki testin yorumu, iddiasının gittiği testin yorumuna geçer.
- **Kod bu turda açılmaz.**
- Commit mesajında çift tırnak yok; amend yok.

## Değişen dosyalar

| Dosya | Ne oluyor |
|---|---|
| `queen-agent/backend/tests/test_tools.py` | envanter kümesi daralır, üç yokluk testi doğar, yedi davranış testi ile iki yardımcı gider |
| `queen-agent/backend/tests/test_modes.py` | `WRITES` adı bırakır, bir yokluk testi doğar |
| `queen-agent/backend/tests/test_skills.py` | üç test bire iner |

---

## Görev A · `test_tools.py`

- [ ] **A1 — envanter kümesi**

`test_every_tool_is_declared_to_the_model`, `mark_step_done` satırını ve yorumunu bırakır. Küme
eşitliği olduğu için bugün **kırmızı** verir.

```python
        # Madde 185, and since 208 the only tool that answers out of a model rather than out of the
        # file store: the border between the agent that builds a scenario and the model that writes
        # its sentences, crossed once for every frame still waiting, in one round.
        "write_missing_actions",
    }
```

*(Yani `"mark_step_done",` satırı ile üstündeki iki satırlık 198 yorumu gider; `write_missing_actions`
kümenin son adı olur.)*

- [ ] **A2 — araç yok, ve adı çağrılırsa cevap var**

`test_the_listing_tool_is_gone` ile `test_the_listing_tool_is_unknown_to_the_runner`'ın ikili
kalıbı, 205–208'in yazdığı gibi tek testte:

```python
def test_the_step_ticking_tool_is_gone(tmp_path):
    # Madde 203. What Madde 198 fixed was the box format -- once a plan is written as - [ ] 1., what
    # a ticked step looks like stopped being the model's to invent -- and the tool was the other
    # half of that turn. Correction 11 took the half away: where the work stopped is read off the
    # project's files now, and the plan's boxes are only a note. A tool that fills a note was paid
    # for on every request, in its description and two parameters.
    assert "mark_step_done" not in {spec["function"]["name"] for spec in TOOL_SPECS}
    # And a record written before this madde can still carry the name: the turn that replays it
    # gets an answer rather than a crash, the road every deleted tool here has taken.
    said = run_tool(_files(tmp_path), "p1", "mark_step_done", json.dumps({"name": "p", "step": 1}))
    assert "no tool called" in said.text
```

- [ ] **A3 — metinleri yok**

```python
def test_the_step_ticking_texts_are_gone():
    # What the madde actually buys back. The tool ran when a step closed; these three went out on
    # every request whether or not a plan existed.
    from backend.features.workspace.domain import prompt

    assert not hasattr(prompt, "MARK_STEP_DONE")
    assert not hasattr(prompt, "MARK_STEP_DONE_NAME")
    assert not hasattr(prompt, "MARK_STEP_DONE_STEP")
```

- [ ] **A4 — kaldırma kuyruğu: `plan_name`**

```python
def test_no_name_is_bent_into_a_plans_shape_any_more():
    # The tail this removal leaves. plan_name had one caller left after Madde 207 -- the fallback
    # inside the ticking tool, which looked for <name>-plan.md when the name as written was not
    # there. With the tool gone nothing calls it, and a function nobody calls is a shape rule the
    # next reader would take for law: a plan is named by the model now, like any other file.
    from backend.features.workspace.domain import tools

    assert not hasattr(tools, "plan_name")
```

- [ ] **A5 — yedi davranış testi ve iki yardımcı gider**

`# --- ticking a step off the plan (Madde 198) ---` başlığından `# --- the reads the descriptions
used to demand (Madde 125) ---` başlığına kadar olan blok silinir. İçindekiler:

`PLAN`, `_planned`, `test_a_step_is_ticked_off_a_plan_the_model_named_itself`,
`test_a_plan_named_the_old_way_is_still_found`, `test_a_step_that_was_approved_gets_its_box_filled`,
`test_nothing_but_the_box_is_touched`, `test_a_step_already_ticked_is_left_alone`,
`test_a_step_that_is_not_there_is_an_answer_rather_than_a_crash`,
`test_a_plan_that_is_not_there_is_an_answer_too`.

**`PLAN` başka yerde kullanılmıyor mu:** blok dışında okunmuyor — silinmeden önce dosyada aranır,
kalan bir okuyucu varsa yardımcı kalır.

- [ ] **A6 — motorun ulaşmadığı araç sayısı**

`test_the_runner_takes_an_engine_and_the_tools_that_do_not_need_one_carry_on`'un yorumu bugün
*"the other seventeen"* diyor ve **yanlış** — bugün 19 araç var, motoru alan bir tane, yani on
sekiz. Bu maddeden sonra doğru olacak; yorum bugünden doğru yazılır:

```python
def test_the_runner_takes_an_engine_and_the_tools_that_do_not_need_one_carry_on(tmp_path):
    # Madde 175. Every tool here answers out of the file store; one of them answers out of a model
    # as well, and the engine has to reach it without the other seventeen noticing. The count is
    # this madde's: nineteen tools became eighteen when the ticking one went.
    files = _with(tmp_path, "plan.md", "one\ntwo")
    answered = run_tool(files, "p1", "read_file", json.dumps({"name": "plan.md"}), engine=object())
    assert answered.outcome == "2 lines"
```

---

## Görev B · `test_modes.py`

- [ ] **B1 — `WRITES` adı bırakır**

`"mark_step_done",` satırı ve üstündeki üç satırlık 198 yorumu gider; `remove_frame` listenin son
adı olur. **Tek başına kırmızı vermez** — bu yüzden B2 var.

- [ ] **B2 — yokluk, listenin kendisinden**

```python
def test_no_mode_lets_the_step_ticking_tool_through():
    # Madde 203, read off the lists for 206's reason: needs_permission answers False for a tool
    # nobody knows, so a leftover entry claims nothing and passes green.
    from backend.features.workspace.domain.modes import _WITHOUT_ASKING

    for mode, allowed in _WITHOUT_ASKING.items():
        assert "mark_step_done" not in allowed, mode
```

---

## Görev C · `test_skills.py`

- [ ] **C1 — üç test bire iner**

`test_an_approved_step_is_ticked_by_the_tool_that_ticks_one` kalır, adını ve iddiasını değiştirir:

```python
def test_no_step_is_ticked_off_the_plan_at_all():
    # Madde 198 gave the flow a tool that fills one box, because "marked done" did not say which
    # tool it meant and the plan tool of the day rewrote the whole file to close one step (Madde
    # 126). What answered that was the box format, and the format stays.
    #
    # Madde 203 withdraws the rest, on correction 11's finding: the boxes are only a note, and what
    # says how far the work got is the project's files. Neither road back is offered -- not the
    # tool, and not edit_file, which is the hand-built anchor 126 was written against.
    said = _flow()
    assert "mark_step_done" not in said
    assert "edit_file" not in said
```

`test_a_finished_step_reaches_the_plan` ile `test_a_finished_step_is_closed_without_rewriting_the_plan`
**silinir**. Birincisinin dersi — taze bir sohbet nereden devam eder — 11 numarayla taşındığı testin
yorumuna yazılır:

```python
def test_where_the_work_stopped_is_read_off_the_files():
    # Correction 11. The boxes were the only thing the flow looked at, and a box is filled by a tool
    # nobody is obliged to call -- so a chat that stopped mid-step read its own plan as finished.
    # What the work produced is on disk either way, and that is what says how far it got.
    #
    # Since Madde 203 this is the whole of the promise: no turn fills a box any more, and this is
    # where a fresh chat learns where to carry on from.
    #
    # Lowered, because the sentence opens the bullet's second clause and starts with a capital:
    # asked of the text as written, this claim could never be met by any text at all.
    said = _flow().lower()
    assert "the project's files are what say how far it got" in said
    assert "the first step whose box is empty" not in said
```

İkincisinin dersi *(126)* yukarıdaki yeni testin yorumunda duruyor.

- [ ] **C2 — bekçi, dokunulmaz**

`test_a_plan_is_written_as_boxes_to_tick` *(`test_prompt.py`)* `- [ ]`'i tutuyor ve **yeşil kalır**:
bu madde kutuyu değil, kutuyu dolduran turu kaldırıyor.

---

## Görev D · Süit ve kırmızı commit

- [ ] **D1 — arka uç:** `python -m pytest queen-agent -q`

Beklenen: **altı kırmızı**.

| Görev | Kırmızı |
|---|---|
| A1 · envanter kümesi | 1 |
| A2 · araç yok | 1 |
| A3 · metinleri yok | 1 |
| A4 · `plan_name` yok | 1 |
| B2 · hiçbir kip geçirmiyor | 1 |
| C1 · akış anmıyor | 1 |

A5 yedi testi siler *(sayı düşer, kırmızı değil)*, A6 ve B1 yorum/liste düzeltmesi, C1 iki testi
siler. Beklenmeyen bir kırmızı çıkarsa uygulama turuna geçilmez.

- [ ] **D2 — ön uç:** `npm test --prefix queen-agent/frontend` → 648 yeşil.

- [ ] **D3 — commit.**

```
test(m203): red asks for a plan nobody ticks
```

---

## Kendi kontrolü

- **Spec'in her maddesi bir göreve düşüyor mu?** Araç yokluğu → A2; metinler → A3; kuyruk → A4;
  envanter → A1; kip listesi → B1–B2; akışın çekilen maddesi → C1; iki sayı → A6 *(test tarafı)*.
- **Yer tutucu var mı?** Yok.
- **Ad tutarlılığı:** `TOOL_SPECS`, `run_tool`, `_files`, `_with`, `_flow` — hepsi bugünkü adlar.
  `json` `test_tools.py`'de zaten içeri alınmış.
- **Silinen testin dersi kayboluyor mu?** Hayır: biri C1'in yorumunda, biri
  `test_where_the_work_stopped_is_read_off_the_files`'ın yorumunda.
