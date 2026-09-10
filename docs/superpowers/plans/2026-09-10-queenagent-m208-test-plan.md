# Madde 208 · Tur 1 (testler) — Plan

**Tasarım:** [2026-09-10-queenagent-m208-tek-kare-araci-testler-design.md](../specs/2026-09-10-queenagent-m208-tek-kare-araci-testler-design.md)
**Kaynak madde:** [yol haritasının Madde 208'i](2026-09-06-queenagent-v8-roadmap.md)

**Bu turda kod yazılmaz.** Altı test kırmızıya döner; üç test de bekçi olarak kurulur ve bugün
yeşil geçer.

**Komutlar** *(sabit satırlar, kuyruk eklenmez)*:

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Amaç:** `write_frame_prompt`'un yokluğunu, ve yokluğunda iki yolun *(toplu ilk yazım, ajanın
kendi düzeltmesi)* yerinde durduğunu tutan testleri yazmak.

**Yürüten:** bu oturum, tek başına.

---

## Bağlayıcı kurallar

- Testler **kırmızıyken** commit'lenir; `skip`/`xfail` yok.
- Kod bu turda açılmaz.
- Ölecek testler bu turda silinmez.
- Kaybolabilecek adlar testin içinden import edilir.
- Yorum neden'i söyler, İngilizce, ve yalnız bugün doğru olanı.
- Commit mesajında çift tırnak yok; amend yok.

---

## Bekçilerin sebebi

Kalkan aracın testlerinden üçünün **iddiası** yaşıyor ama bugün yalnız o araç üzerinden tutuluyor.
Yerleri bu turda kuruluyor ki uygulama turunda eskisi silinirken iddia bir an bile tutulmasız
kalmasın:

| İddia | Bugün nerede | Yeni yeri |
|---|---|---|
| Yazara sahne, kadro ve mekân gösterilir | tek kare aracının testi | toplu aracın testi |
| Yazılan cümle cevaba konmaz *(Madde 130)* | tek kare aracının testi | toplu aracın testi |
| Editör metni iki şikâyeti ayırır | *"not"* yolu üzerinden | hatanın nerede olduğu üzerinden |

---

## Görev 1 · `test_tools.py` — aracın yokluğu *(iki kırmızı)*

**Yer:** 206 ve 207'nin kaldırma testlerinin ardı *(`test_the_plan_tools_texts_are_gone`'dan
sonra)*.

- [ ] **Adım 1 — iki testi yaz**

```python
def test_the_single_frame_tool_is_gone(tmp_path):
    # Madde 208. Madde 174 kept the action out of the frame tools because the main model would not
    # write that kind of sentence, and 176 handed it to one that would. 201 wrote down that this is
    # no longer true and took the correction back, which left this tool one job: having a line
    # written afresh from the scene, by a model that has not read the line, through a note. That is
    # the very road 201 argued against.
    assert "write_frame_prompt" not in {spec["function"]["name"] for spec in TOOL_SPECS}
    said = run_tool(
        _files(tmp_path),
        "p1",
        "write_frame_prompt",
        json.dumps({"file": "scene.json", "frame": 1}),
    ).text
    assert "no tool called" in said


def test_the_single_frame_tools_texts_are_gone():
    # The note is named as well as the description, because the note is what this madde is actually
    # about: a whole correction carried to somebody who never saw the line.
    from backend.features.workspace.domain import prompt

    assert not hasattr(prompt, "WRITE_FRAME_PROMPT")
    assert not hasattr(prompt, "WRITE_FRAME_PROMPT_NOTE")
```

- [ ] **Adım 2 — kırmızıyı bekle**

Beklenen: ikisi de `AssertionError` — ad `TOOL_SPECS`'te duruyor, ve `hasattr` `True` dönüyor.

---

## Görev 2 · `test_tools.py` — iki tarif kendi ayakları üstünde *(iki kırmızı)*

**Yer:** var olan `test_a_new_frame_points_at_the_writer_and_a_frame_being_corrected_does_not`'in
yerine *(satır ~2617)*, ve onun altına ikincisi.

- [ ] **Adım 1 — var olan testi yeniden yaz**

```python
def test_a_new_frame_points_at_the_bulk_writer_and_a_frame_being_corrected_does_not():
    # Turned around by Madde 201 and finished by 208. A frame is born without an action, so add_scene
    # still says who writes the first one -- and with the single-frame tool gone, that is the bulk
    # one. update_frame is where a line that exists is corrected, in the agent's own words; pointing
    # from there at a writer as well would offer two roads for one job and settle neither.
    assert "write_missing_actions" in _said_by("add_scene")
    assert "write_frame_prompt" not in _said_by("add_scene")
    assert "write_missing_actions" not in _said_by("update_frame")
```

- [ ] **Adım 2 — toplu aracın metni için test yaz**

```python
def test_the_bulk_tools_text_stands_on_its_own():
    # It borrowed the gone tool's name twice: for which model it asks, and for where a line already
    # written is rewritten. The first is now said in its own words; the second is update_frame.
    said = _said_by("write_missing_actions")
    assert "write_frame_prompt" not in said
    assert "update_frame" in said
```

- [ ] **Adım 3 — kırmızıyı bekle**

Beklenen: ikisi de kırmızı. `ADD_SCENE` bugün kalkan aracı anıyor; `WRITE_MISSING_ACTIONS` iki kez
anıyor ve `update_frame` demiyor.

---

## Görev 3 · `test_modes.py` — kipin listesi *(bir kırmızı)*

- [ ] **Adım 1 — testi yaz** *(207'nin aynı biçimli testinin altına)*

```python
def test_no_mode_lets_the_single_frame_tool_through():
    # Madde 208, read off the lists for 206's reason: needs_permission answers False for a tool
    # nobody knows, so a leftover entry claims nothing and passes green.
    from backend.features.workspace.domain.modes import _WITHOUT_ASKING

    for mode, allowed in _WITHOUT_ASKING.items():
        assert "write_frame_prompt" not in allowed, mode
```

- [ ] **Adım 2 — kırmızıyı bekle**

Beklenen: `AssertionError: edit` — EDIT listesi adı taşıyor.

**`WRITES` listesi bu turda ellenmiyor:** araç hâlâ var, ve o liste `ask` kipinin testini besliyor.

---

## Görev 4 · `test_skills.py` — editör metni *(bir kırmızı)*

**Yer:** var olan `test_a_correction_names_the_single_frame_tool`'un yerine *(satır ~124)*.

- [ ] **Adım 1 — testi yeniden yaz**

```python
def test_the_editor_sends_a_wrong_line_to_the_agent_itself():
    # Madde 208. Both roads out of a wrong line lead to the same place now: correcting one, and
    # wanting one afresh from the scene, are the agent's own writing. Neither goes back to a model
    # that has not read the line -- which is the road 201 argued against and this madde closes.
    said = _edit()
    assert "write_frame_prompt" not in said
    assert "update_frame" in said
```

- [ ] **Adım 2 — kırmızıyı bekle**

Beklenen: `AssertionError` ilk satırda — editör metni bugün kalkan aracı anıyor.

---

## Görev 5 · Üç bekçi *(bugün yeşil)*

- [ ] **Adım 1 — `test_tools.py`, toplu yazarın gördüğü**

**Yer:** toplu aracın bölümü, `test_each_request_carries_its_own_frame_and_no_other`'ın ardı.

`FakeWriter` **kullanılmaz:** iki kare aynı anda gidiyor ve o sınıf yalnız sonuncuyu tutuyor —
hangisi olduğu iş parçacıklarına kalır. `PickyWriter` hepsini biriktiriyor.

```python
def test_the_bulk_writer_is_handed_the_scene_the_cast_and_the_place(tmp_path):
    # What _frame_seen shows, asked on the road that keeps it. Picked out of the collected requests
    # rather than read off the writer's last one: two frames go out at the same time here.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    writer = PickyWriter(scene="nothing matches this")
    _filled(files, writer, file="scene.json")
    said = next(asked for asked in writer.asked if "Scene: one" in asked)
    assert "aylin" in said                     # the name the scene sentence uses
    assert "1girl, long teal hair" in said     # and the tags, which are what the prompt is made of
    assert "white nightgown" in said           # the outfit's tags, not just its name
    assert "bedroom" in said and "sunlit bedroom" in said
```

- [ ] **Adım 2 — `test_tools.py`, cevabın makbuz olması**

```python
def test_the_bulk_answer_is_a_receipt_rather_than_the_prompt(tmp_path):
    # Madde 130 on this road: what was written sits in the file, and the answer names the frames
    # rather than repeating their lines. The numbers are held one test above; this holds the
    # absence, which is the half that would go unnoticed.
    files = _with(tmp_path, "scene.json", WITH_ACTION)
    said = _filled(files, FakeWriter("she turns her head, close-up"), file="scene.json").text
    assert "turns her head" not in said
```

- [ ] **Adım 3 — `test_skills.py`, iki şikâyetin ayrılması**

**Yer:** var olan `test_a_complaint_is_written_again_rather_than_edited`'in altına. Eski test
uygulama turunda silinir — *"not"* yolu kodla birlikte kalkıyor.

```python
def test_a_complaint_is_told_apart_by_where_the_fault_lives():
    # Two roads and the text names both, because they answer different complaints. One frame's
    # sentence is wrong: that is the frame's own line. Somebody looks wrong in every frame they are
    # in: that is their entry, and one update reaches all of them.
    said = _edit()
    assert "update_frame" in said
    assert "update_character" in said
```

- [ ] **Adım 4 — üçünün de yeşil olduğunu gör**

Bugün geçmeleri gerekiyor. Biri kırmızı verirse iddia sandığım yerde tutulmuyor demektir, ve
uygulama turuna geçilmeden sebebi anlaşılır.

---

## Görev 6 · Süit ve kırmızı commit

- [ ] **Adım 1 — arka uç**

```bash
python -m pytest queen-agent -q
```

Beklenen: **6 kırmızı**.

| Nerede | Kaç |
|---|---|
| `test_tools.py` — yokluk | 2 |
| `test_tools.py` — iki tarif | 2 |
| `test_modes.py` | 1 |
| `test_skills.py` | 1 |

Beklenmeyen bir kırmızı çıkarsa uygulama turuna geçilmez.

- [ ] **Adım 2 — ön uç**

```bash
npm test --prefix queen-agent/frontend
```

Beklenen: 648 yeşil.

- [ ] **Adım 3 — commit**

---

## Kendi kontrolü

- **Spec'in her maddesi bir göreve düşüyor mu?** Aracın yokluğu → 1; iki tarif → 2; kip → 3;
  editör → 4; üç bekçi → 5.
- **Yer tutucu var mı?** Yok.
- **Ad tutarlılığı:** `PickyWriter`, `FakeWriter`, `_filled`, `_with`, `WITH_ACTION`, `_said_by`,
  `_edit` — hepsi bugünkü adlar, ve `_filled` ile `PickyWriter` toplu aracın bölümünde tanımlı,
  yani bekçiler onların **altına** yazılır.
