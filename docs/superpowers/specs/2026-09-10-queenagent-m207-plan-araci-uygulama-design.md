# Madde 207 — plan yazan araç kalkar · uygulama turu

**Kaynak:** [test turu](2026-09-10-queenagent-m207-plan-araci-testler-design.md) ve
[yol haritasının Madde 207'si](../plans/2026-09-06-queenagent-v8-roadmap.md).

On bir test kırmızı commit edildi *(`f685721`)*. Bu tur onları yeşile çeviren kodu yazıyor.

## Tasarımın özü

Araç iki şey taşıyordu, ve ikisi de aslında **kipin**:

| Araçta duruyordu | Nereye iniyor |
|---|---|
| plan kipinde sormadan koşan tek yazma | `_WITHOUT_ASKING[PLAN]` → `READS + ("create_file",)` |
| turu bitiren çift | `ends_the_turn` → `mode == PLAN and tool == "create_file"` |

Bir şey de gerçekten aracındı, ve o metne iniyor:

| Araçta duruyordu | Nereye iniyor |
|---|---|
| kutu biçimi *(`- [ ] 1.`)* | `START_A_SCENARIO`'nun 1. adımı *(10 numaralı düzeltmenin kararı)* |

Bir şey de **kaybolmuş oluyor**, ve onun yerini kod dolduruyor:

| Araçta duruyordu | Nereye iniyor |
|---|---|
| planın adı hep `<ad>-plan.md`'ydi *(`plan_name`)* | `mark_step_done` adı **önce yazıldığı gibi** arar, `-plan` biçimi yedek olur |

## Nereden ne kalkıyor

### `tools.py`

- `TOOL_SPECS`'teki `write_plan` şeması, iki parametresiyle
- `run_tool`'un `write_plan` dalı
- `WRITES_FILES`'taki `"write_plan"` — `create_file` zaten orada, yani plan kartı çizilmeye devam
- `WRITES_FILES`'in üstündeki yorumun son cümlesi *("write_plan is, because the first plan of a
  name is new")* artık yanlış olur, düşer

`plan_name` **kalıyor**: `mark_step_done` onu yedek olarak kullanıyor, ve 203 onu aracıyla birlikte
alacak.

### `mark_step_done` dalı — iki satır ekleniyor

```python
    if name == "mark_step_done":
        wanted = safe_name(args.get("name"))
        content = file_store.read(project_id, wanted)
        if content is None:
            wanted = plan_name(wanted)
            content = file_store.read(project_id, wanted)
        if content is None:
            return ToolResult(f"There is no {wanted}.", None, wanted, "No plan by that name")
```

Bulunamayan planın adı **yedeğin adıyla** söyleniyor, ve bu bilerek: bugün de öyle diyor
*(`ghost` → `There is no ghost-plan.md`)*, ve o cümle modele *"plan bu biçimde aranıyor"* diyen tek
yer.

### `modes.py`

- `PLAN` satırı `READS + ("create_file",)` olur, yorumu yeni sebebi söyler
- EDIT listesindeki `"write_plan"` girdisi ve onu anlatan yorum düşer
- `ends_the_turn` `create_file`'a bakar, docstring'i **reddedilen** çağrının da turu bitirdiğini
  söyler

### `prompt.py`

- `WRITE_PLAN`, `WRITE_PLAN_NAME`, `WRITE_PLAN_CONTENT` gider
- `SYSTEM_PROMPT`'un plan cümlesi:
  *"A job of several steps starts with a plan file: the plan is where the work keeps its place, and
  a fresh chat picks it up from the step left open. create_file writes it."*
- `START_A_SCENARIO`'nun 1. adımı `create_file` der ve kutu biçimini taşır

> **Akışın kelime tavanı 450**, ve testi tutuyor. 1. adım kutu biçimini kazanırken cümlenin geri
> kalanı kısalıyor; tavan aşılırsa kesilecek yer bu adımın kendi tekrarıdır.

## Ölen testler

- `test_a_plan_is_written_under_a_name_that_says_it_is_one`
- `test_writing_a_plan_again_replaces_it`
- `test_only_the_first_plan_reports_a_born_file`
- `test_the_plan_tool_does_not_demand_a_read_of_what_the_turn_just_wrote`
- `test_write_plan_ends_only_the_turn_that_was_asked_to_plan`
- `test_every_tool_is_declared_to_the_model` — silinmiyor, **kısalıyor**: ad ve yorumu çıkar
- `_planned` yardımcısı — silinmiyor, `create_file`'a geçer
- `test_modes.py`'nin `WRITES` listesi — `"write_plan"` çıkar

**Ne kaybolmuyor:** planın üzerine yazılması artık `create_file`'ın işi değil — o alınmış adı
reddediyor. Bu bir davranış farkı, ve kaydı 10 numarada duruyor: plan yalnız ilk turda, yalnız
ortada plan yokken yazılır. `test_a_refused_create_does_not_say_it_saved` o reddi zaten tutuyor.

## `test_xai_client.py`'nin kurgu adları

Üç testte akış parçaları `write_plan` adıyla kuruluyor. O testler adın **var olmasına**
dayanmıyor — istemcinin parçaları birleştirmesini ölçüyorlar — ama var olmayan bir araç adı taşıyan
kurgu, okuyanı yanıltır. `create_file`'a çevriliyor; iddiaları değişmiyor.

## Doğrulama

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

On bir kırmızı yeşile döner, silinen beş testle birlikte toplam düşer, başka hiçbir şey kırmızıya
dönmez. Ön uç ellenmiyor.
