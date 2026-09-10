# Madde 207 · Tur 1 (testler) — Plan

**Tasarım:** [2026-09-10-queenagent-m207-plan-araci-testler-design.md](../specs/2026-09-10-queenagent-m207-plan-araci-testler-design.md)
**Kaynak madde:** [yol haritasının Madde 207'si](2026-09-06-queenagent-v8-roadmap.md)

**Bu turda kod yazılmaz.** On bir test kırmızıya döner, iki test de bekçi olarak yeşil kalır.

**Komutlar** *(sabit satırlar, kuyruk eklenmez)*:

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Amaç:** `write_plan`'in yokluğunu, ve yokluğunda plan kipinin bugünkü davranışını koruduğunu
tutan testleri yazmak.

**Yaklaşım:** Aracın taşıdığı iki ayrıcalık `modes.py`'ye, kutu biçimi akış metnine, planın adı da
`mark_step_done`'ın aramasına iner. Testler bu dört yeri ayrı ayrı tutar.

**Yürüten:** bu oturum, tek başına. *(CLAUDE.md: istenmedikçe alt-ajan ve workflow yok.)*

---

## Bağlayıcı kurallar

- **Testler kırmızıyken commit'lenir.** `skip`/`xfail` yeşil yapmanın yolu değil.
- **Kod bu turda açılmaz.** `prompt.py`, `tools.py`, `modes.py` ellenmez.
- **Ölecek testler bu turda silinmez.** Bugün yeşiller; silmek kırmızıyı görmeden yeşile boyamaktır.
- **Kaybolabilecek adlar testin içinden import edilir.** Dosyanın başında bir toplama hatası bütün
  süiti durdurur ve turun öteki kırmızıları hiçbir yerde görünmez.
- **Yorum neden'i söyler.** İngilizce, ve yalnız bugün doğru olanı.
- **Commit mesajında çift tırnak yok**, ve **amend yok**.

---

## Değişen dosyalar

| Dosya | Sorumluluğu | Bu turda |
|---|---|---|
| `backend/tests/test_tools.py` | araç şemaları ve `run_tool` | 3 yokluk testi + 2 işaretleme testi |
| `backend/tests/test_modes.py` | kipin neyi sormadan koştuğu | 2 test yeniden yazılır, 1 eklenir |
| `backend/tests/test_prompt.py` | taban metnin cümleleri | 2 test yeniden yazılır |
| `backend/tests/test_skills.py` | akış metninin adımları | 2 test yeniden yazılır |
| `backend/tests/test_stream_answer.py` | turun nerede bittiği | 1 test yeniden yazılır |

---

## Planlarken çıkan üç tuzak

Bunlar spec yazılırken görülmemişti; testler bu yüzden burada yazıldıkları hâlle yazılır.

1. **`create_file` taban metinde zaten geçiyor** *(`prompt.py:44`, `create_file`'ın ne zaman
   çağrılacağı)*. Yani `assert "create_file" in SYSTEM_PROMPT` **bugün de yeşil** — plan cümlesi
   hakkında hiçbir şey söylemez. Test cümlenin kendi kelimelerini tutar.
2. **Plan kipinde izin kapısına takılan bir tur da tek istek gönderir.** `len(engine.seen) == 1`
   tek başına *"tur planla bitti"* ile *"tur izin sorusuyla durdu"*u ayırmıyor — bugün de yeşil
   verir. Test ayrıca dosyanın doğduğunu tutar.
3. **Eski ad testi kırmızı değil, bekçi.** `bar-scene-plan.md` bugün de bulunuyor; o test yedeğin
   *durduğunu* tutar, gelmesini değil.

---

## Görev 1 · `test_tools.py` — aracın yokluğu

**Dosya:** `queen-agent/backend/tests/test_tools.py`
**Yer:** 206'nın kaldırma testlerinin hemen ardı *(`test_the_character_preview_text_is_gone`'dan
sonra, `TAG_TOOLS` parametrik testinden önce)*.

- [ ] **Adım 1 — üç testi yaz**

```python
def test_the_plan_tool_is_gone(tmp_path):
    # Madde 207. It wrote a file, and create_file writes a file. The one thing it carried on its own
    # was the box shape, and correction 10 had already moved that into the flow's own sentence. What
    # was left of its reason -- running without a question in plan mode, and ending that turn -- is
    # the mode's behaviour rather than the tool's, and modes.py says it of create_file now.
    assert "write_plan" not in {spec["function"]["name"] for spec in TOOL_SPECS}
    said = run_tool(
        _files(tmp_path),
        "p1",
        "write_plan",
        json.dumps({"name": "bar-scene", "content": "1. ..."}),
    ).text
    assert "no tool called" in said


def test_no_tool_but_create_file_writes_a_plan():
    # The card the chat draws for a plan is unchanged. What draws it is not.
    from backend.features.workspace.domain.tools import WRITES_FILES

    assert "write_plan" not in WRITES_FILES
    assert "create_file" in WRITES_FILES


def test_the_plan_tools_texts_are_gone():
    from backend.features.workspace.domain import prompt

    assert not hasattr(prompt, "WRITE_PLAN")
    assert not hasattr(prompt, "WRITE_PLAN_NAME")
    assert not hasattr(prompt, "WRITE_PLAN_CONTENT")
```

- [ ] **Adım 2 — kırmızıyı bekle**

Beklenen: üçü de `AssertionError`. Birincisi kümede duran adda, ikincisi `WRITES_FILES`'ta,
üçüncüsü `hasattr(prompt, "WRITE_PLAN")`'ın `True` dönmesinde.

---

## Görev 2 · `test_tools.py` — planı modelin verdiği adla işaretlemek

**Yer:** `PLAN` sabitinin hemen altı *(Madde 198'in bölümü, `_planned` yardımcısından sonra,
`test_a_step_that_was_approved_gets_its_box_filled`'dan önce)*.

**Neden bu tur:** `write_plan` her adı `plan_name`'den geçiriyordu, yani plan **hep**
`<ad>-plan.md` oluyordu ve `mark_step_done` oraya bakarak buluyordu. `create_file` bunu yapmıyor:
ad modelin. `plan.md` diye yazılmış bir plan `plan-plan.md` diye aranır, bulunamaz, ve ikinci
deneme de aynı yere düşer — `plan-plan` zaten `-plan` ile bitiyor. Akışın ana döngüsü kapanır.

- [ ] **Adım 1 — iki testi yaz**

```python
def test_a_step_is_ticked_off_a_plan_the_model_named_itself(tmp_path):
    # Madde 207. write_plan put every name through plan_name, so a plan was always <name>-plan.md
    # and this tool could look there and find it. create_file does not: the name is the model's.
    # Looked up as it was written, or the flow's own loop closes on nothing -- plan.md would be
    # searched for as plan-plan.md, and asking again lands in the same place, because plan-plan
    # already ends in -plan.
    files = _files(tmp_path)
    _call(files, "create_file", name="plan.md", content=PLAN)
    _call(files, "mark_step_done", name="plan.md", step=1)
    assert files.read("p1", "plan.md").startswith("- [x] 1.")


def test_a_plan_named_the_old_way_is_still_found(tmp_path):
    # The -plan shape is a fallback now rather than the rule, and this is what keeps it: a plan
    # written under that name is still found when the model asks for it by the stem.
    files = _files(tmp_path)
    _call(files, "create_file", name="bar-scene-plan.md", content=PLAN)
    _call(files, "mark_step_done", name="bar-scene", step=2)
    assert "- [x] 2." in files.read("p1", "bar-scene-plan.md")
```

- [ ] **Adım 2 — kırmızıyı bekle**

Beklenen: **yalnız birincisi** kırmızı. `plan.md` dosyası `- [ ] 1.` ile başlamaya devam eder,
çünkü araç `plan-plan.md`'yi aramış ve bulamamıştır. İkincisi **bugün de yeşil** — o bir bekçi.

---

## Görev 3 · `test_modes.py` — iki ayrıcalık kipin kendisine geçer

**Dosya:** `queen-agent/backend/tests/test_modes.py`

- [ ] **Adım 1 — `test_plan_mode_writes_a_plan_without_asking_and_asks_for_the_rest`'i değiştir**

Eski hâli `write_plan`'in sorulmadığını, `create_file`'ın sorulduğunu tutuyordu. Yeni hâli:

```python
def test_plan_mode_writes_one_file_without_asking():
    # Madde 207. The privilege used to be write_plan's, and the fear was that create_file would let
    # the mode write the plan and the deliverable in one turn. It cannot: the first write is what
    # ends the turn, one line below this.
    assert not _asks("plan", "create_file")
    assert _asks("plan", "edit_file")
    assert _asks("plan", "add_scene")
```

- [ ] **Adım 2 — kipin listesine bakan testi ekle**

```python
def test_no_mode_lets_the_plan_tool_through():
    # Madde 207, read off the lists for 206's reason: needs_permission answers False for a tool
    # nobody knows, so a leftover entry claims nothing and passes green.
    from backend.features.workspace.domain.modes import _WITHOUT_ASKING

    for mode, allowed in _WITHOUT_ASKING.items():
        assert "write_plan" not in allowed, mode
```

- [ ] **Adım 3 — `test_only_a_written_plan_ends_the_turn`'ü değiştir**

```python
def test_only_the_plan_modes_own_file_ends_the_turn():
    # The plan reached disk and the next move is the user's. Nothing else stops a turn early -- the
    # same call in edit mode is an ordinary write, which is what it has always been there.
    from backend.features.workspace.domain.modes import ends_the_turn

    assert ends_the_turn("plan", "create_file")
    assert not ends_the_turn("edit", "create_file")
    assert not ends_the_turn("plan", "read_file")
```

- [ ] **Adım 4 — kırmızıyı bekle**

Beklenen: üçü de kırmızı. Bugün plan kipi `create_file`'ı **soruyor**, iki kipin listesi
`write_plan` taşıyor, ve `ends_the_turn` `write_plan`'e bakıyor.

**Dosyanın kendi `WRITES` listesi bu turda ellenmiyor:** araç hâlâ var, ve o liste `ask` kipinin
testini besliyor. Uygulama turunun işi.

---

## Görev 4 · `test_prompt.py` — taban cümlesi ve kutu biçimi

**Dosya:** `queen-agent/backend/tests/test_prompt.py`

- [ ] **Adım 1 — `test_the_base_starts_a_long_job_with_the_plan`'i değiştir**

`assert "create_file" in SYSTEM_PROMPT` **yazılmaz**: o ad taban metinde zaten geçiyor
*(`prompt.py:44`)* ve test hiçbir şey söylemeden yeşil geçerdi. Cümlenin kendisi tutulur:

```python
def test_the_base_starts_a_long_job_with_the_plan():
    # Skill-less chats had no reason to plan; the flow got one in its own text and the base got
    # nothing. The plan file is where a job keeps its place -- which is also how a chat that grew
    # too long is survived.
    #
    # Madde 207 changed the tool it names. Asked of the sentence rather than of the word
    # create_file: that word is already in this text, about when to save a document, so a test
    # looking only for it would pass without holding this sentence at all.
    assert "keeps its place" in SYSTEM_PROMPT.lower()
    assert "create_file writes it" in SYSTEM_PROMPT
    assert "write_plan" not in SYSTEM_PROMPT
```

- [ ] **Adım 2 — `test_a_plan_is_written_as_boxes_to_tick`'in baktığı yeri değiştir**

```python
def test_a_plan_is_written_as_boxes_to_tick():
    # Madde 198. The ticking was instructed long before the shape was, and an instruction without a
    # shape is one the model answers differently every turn -- so the plan a fresh chat opens says
    # nothing about where the work stopped.
    #
    # The shape used to live in write_plan's description; Madde 207 takes that tool away, and
    # correction 10 had already decided where the shape goes instead: into the sentence of the step
    # that writes the plan, so that it holds whichever tool writes it.
    from backend.features.workspace.domain import prompt

    assert "- [ ]" in prompt.START_A_SCENARIO
```

- [ ] **Adım 3 — kırmızıyı bekle**

Beklenen: ikisi de kırmızı. Taban metin bugün `write_plan` diyor; `- [ ] 1.` bugün yalnız
`WRITE_PLAN`'in tarifinde duruyor *(`prompt.py:595`)*.

---

## Görev 5 · `test_skills.py` — akışın 1. adımı

**Dosya:** `queen-agent/backend/tests/test_skills.py`

- [ ] **Adım 1 — `test_the_flow_writes_the_plan_before_it_asks_anything`'i değiştir**

```python
def test_the_flow_writes_the_plan_before_it_asks_anything():
    # Step one whatever the user's opening sentence was. Without it the flow starts somewhere
    # different every time, and has nowhere to keep its place.
    #
    # Madde 207: the tool is create_file, and the step's own sentence is what says a plan is boxes.
    said = _flow()
    assert "create_file" in said
    # Ordered against the next step rather than against the schema fetch, which Madde 172 retired.
    assert said.index("create_file") < said.index("2. The characters")
```

- [ ] **Adım 2 — `test_no_instruction_reaches_for_the_listing_tool`'un son iddiasını çöz**

Son satırı bugün *"first turn opens with write_plan"* diye bir dizge tutuyor, ve o cümle kalkıyor.
İddia, o testin kendi konusuna — ilk turun kendine ait olması — geri döner:

```python
def test_no_instruction_reaches_for_the_listing_tool():
    # Madde 127: the tool is gone, and a text still naming it would send the model after something
    # that cannot answer. The flow's first turn still writes the plan; the listing that stood before
    # it is what the request now carries on its own.
    for skill, said in INSTRUCTIONS.items():
        assert "list_files" not in said, skill
    assert "A chat's first turn" in _flow()
```

- [ ] **Adım 3 — kırmızıyı bekle**

Beklenen: **yalnız birincisi** kırmızı — akış metni bugün `create_file` demiyor. İkincisi bugün de
yeşil; orada yapılan, kalkacak bir cümleye bağlı iddiayı çözmek.

---

## Görev 6 · `test_stream_answer.py` — plan kipinde turun bitişi

**Dosya:** `queen-agent/backend/tests/test_stream_answer.py`

**Neden tek `assert` yetmiyor:** `_in_mode` izin defteri olarak `UNASKED` veriyor. Bugün plan
kipinde `create_file` izin istiyor, tur **izin sorusuyla** duruyor — ve o tur da tek istek
gönderdiği için `len(engine.seen) == 1` yeşil verir. İki hâli ayıran şey dosyanın doğması.

- [ ] **Adım 1 — testi değiştir**

```python
def test_in_plan_mode_the_turn_ends_when_the_plan_is_written(tmp_path):
    # The plan is on disk and the next move is the user's: they read it, fix it in the file itself,
    # then run it in edit mode. A second round here would be the model running its own plan.
    #
    # Madde 207: the plan is an ordinary create_file now, and plan mode is what makes it a plan --
    # it runs without a question there, and it is what ends the turn. The file card is asserted as
    # well as the one request: a turn that stopped to ask permission also sends one, and would read
    # as green here.
    rounds = [
        [{"tool_calls": [call("create_file", name="bar-scene-plan.md", content="1. ...")]}],
        [{"text": "never reached"}],
    ]
    _, engine, produced = _in_mode(tmp_path, rounds, "plan")
    assert len(engine.seen) == 1
    assert [piece for piece in produced if isinstance(piece, FileWritten)]
```

`FileWritten` bu dosyada zaten import edilmiş *(satır 12)*.

- [ ] **Adım 2 — kırmızıyı bekle**

Beklenen: `AssertionError` son satırda — bugün dosya doğmuyor, çünkü tur izin kapısında duruyor.

---

## Görev 7 · Süit, ve kırmızı commit

- [ ] **Adım 1 — arka ucu koş**

```bash
python -m pytest queen-agent -q
```

Beklenen: **11 kırmızı**, geri kalan yeşil.

| Nerede | Kaç |
|---|---|
| `test_tools.py` — yokluk | 3 |
| `test_tools.py` — modelin adıyla işaretleme | 1 |
| `test_modes.py` | 3 |
| `test_prompt.py` | 2 |
| `test_skills.py` | 1 |
| `test_stream_answer.py` | 1 |

Kırmızıların her biri **kendi sebebiyle** kırmızı olmalı. Beklenmeyen bir kırmızı çıkarsa
uygulama turuna geçilmez: önce sebebi anlaşılır.

- [ ] **Adım 2 — ön ucu koş**

```bash
npm test --prefix queen-agent/frontend
```

Beklenen: 648 yeşil. Bu tur ön uca dokunmuyor.

- [ ] **Adım 3 — commit**

```bash
git add -A
git commit -m @'
test(m207): red asks the plan tool to be gone and the mode to carry its two privileges

...

Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>
'@
```

---

## Kendi kontrolü

- **Spec'in her maddesi bir göreve düşüyor mu?** Aracın yokluğu → 1; kutu biçimi → 4; planın adı →
  2; kipin iki ayrıcalığı → 3; akış metni → 5; turun bitişi → 6. Açık kalan yok.
- **Yer tutucu var mı?** Yok: her adımın kodu tam.
- **Spec'in üç yeri düzeltilecek** *(bu plan yazılırken görüldü)*: kırmızı sayısı on bir ama
  dağılımı farklı, eski ad testi bekçi, ve taban metnin testi `create_file` kelimesini değil
  cümleyi tutuyor.
