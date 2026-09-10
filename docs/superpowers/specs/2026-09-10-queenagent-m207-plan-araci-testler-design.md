# Madde 207 — plan yazan araç kalkar · test turu

**Kaynak:** [yol haritasının Madde 207'si](../plans/2026-09-06-queenagent-v8-roadmap.md).

## Ne kanıtlanacak

`write_plan` bir dosya yazıyor, `create_file` de bir dosya yazıyor. Aracın kendi başına taşıdığı
tek şey kutu biçimiydi *(`- [ ] 1.`)*, ve **10 numaralı düzeltme onu zaten akışın kendi cümlesine
taşıdı**.

Kalan gerekçe aracın değil **kipin**: plan kipinde sormadan koşan tek yazma odur, ve turu bitiren
çift odur. İkisi de `modes.py`'de duruyor, ve ikisi de `create_file`'a geçince plan kipi bugünkü
davranışını korur — sormadan bir dosya yazar, ve o dosyayla tur biter.

## İki sonuç, ve ikisi de bu turda teste bağlanıyor

### 1 · Kutu biçimi akışa taşınır

Bugün `- [ ] 1.` yalnız `WRITE_PLAN`'in tarifinde duruyor. Araç kalkınca o metin de kalkıyor, yani
biçimi söyleyen tek yer akış metni olacak — 10 numaranın kararı da buydu. Test `START_A_SCENARIO`'ya
bakar, araç tarifine değil.

### 2 · Planın adı artık modelin

`write_plan` her adı `plan_name`'den geçiriyordu: plan hep `<ad>-plan.md` oluyordu. `create_file`
bunu yapmıyor — ad modelin. Ama `mark_step_done` planı hâlâ `plan_name` üzerinden **arıyor**, ve
`plan.md` diye yazılmış bir planı `plan-plan.md` diye arar. Bulamaz, ve ikinci deneme de aynı yere
düşer *(`plan-plan` zaten `-plan` ile bitiyor)* — yani akışın ana döngüsü kapanır.

Bu bir kenar durum değil, olağan yol. Testi bunu tutuyor: **model planı ne ad verdiyse o adla
işaretlenir**, ve `-plan` biçimi kural değil **yedek** olur.

> Düzeltmenin metinde değil kodda olmasının sebebi: akış metninin kelime tavanı var *(450)*, ve bir
> ad kuralı yazmak her isteğe kelime ekler. Kodda iki satır, isteğe sıfır kelime — üstelik akışsız
> sohbetleri de kurtarır.

## Yazılacak testler

### `test_tools.py`

- **`test_the_plan_tool_is_gone`** — ad `TOOL_SPECS`'te yok, ve o adla yapılan bir çağrı
  `no tool called` diyor.
- **`test_no_tool_but_create_file_writes_a_plan`** — `WRITES_FILES` `write_plan` taşımıyor,
  `create_file` taşıyor: kartı çizen küme değişmiyor, çizdiren araç değişiyor.
- **`test_the_plan_tools_texts_are_gone`** — `prompt` modülünde `WRITE_PLAN`, `WRITE_PLAN_NAME`,
  `WRITE_PLAN_CONTENT` yok.
- **`test_a_step_is_ticked_off_a_plan_the_model_named_itself`** — `create_file` ile `plan.md`
  yazılır, `mark_step_done` onu adıyla bulur ve kutusunu doldurur.
- **`test_a_plan_named_the_old_way_is_still_found`** — `bar-scene-plan.md` yazılır ve
  `mark_step_done` `bar-scene` adıyla da bulur. **Bugün de yeşil:** bu bir kırmızı değil, yedeğin
  yerinde durduğunu tutan bekçi.

### `test_modes.py`

- **`test_plan_mode_writes_one_file_without_asking`** — plan kipi `create_file`'ı sormuyor, ötekini
  soruyor.
- **`test_only_the_plan_modes_own_file_ends_the_turn`** — `ends_the_turn("plan", "create_file")`
  doğru, `ends_the_turn("edit", "create_file")` değil.
- **`test_no_mode_lets_the_plan_tool_through`** — hiçbir kipin listesi `write_plan` taşımıyor.

### `test_prompt.py`

- **`test_the_base_starts_a_long_job_with_the_plan`** — var olan test, iddiası değişiyor. Aranan
  şey `create_file` **kelimesi değil**, cümlenin kendisi: o kelime taban metinde zaten geçiyor
  *(`prompt.py:44`, belgenin ne zaman kaydedileceği)*, ve yalnız onu arayan bir test plan cümlesi
  hakkında hiçbir şey söylemeden yeşil geçerdi. Test *"create_file writes it"* dizgesini ve
  `write_plan`'in **yokluğunu** tutar.
- **`test_a_plan_is_written_as_boxes_to_tick`** — var olan test, baktığı yer değişiyor:
  `WRITE_PLAN` yerine `START_A_SCENARIO`.

### `test_skills.py`

- **`test_the_flow_writes_the_plan_before_it_asks_anything`** — akış planı `create_file` ile
  yazıyor, ve bunu 2. adımdan önce söylüyor.
- **`test_no_instruction_reaches_for_the_listing_tool`** — son satırındaki *"first turn opens with
  write_plan"* iddiası aracın adını bırakır.

### `test_stream_answer.py`

- **`test_in_plan_mode_the_turn_ends_when_the_plan_is_written`** — kurgusu `create_file`'a geçer,
  **ve bir iddia kazanır:** dosyanın doğduğu. Tek başına *"bir istek gönderildi"* yetmiyor, çünkü
  izin kapısında duran bir tur da tek istek gönderir — o hâliyle test bugün de yeşil geçerdi.

## Bu turda yazılmayanlar

- **Ölecek testler silinmiyor:** `write_plan`'in dört araç testi, iki tarif testi, ve
  `test_every_tool_is_declared_to_the_model`'in içindeki ad bugün yeşil. Uygulama turunun işi.
- **`plan_name` kalıyor:** `mark_step_done` onu yedek olarak kullanmaya devam ediyor, ve 203 onu
  aracıyla birlikte alacak.
- **Reddedilen bir `create_file` de turu bitirir.** Bugün `write_plan` hiç reddetmiyor, yani bu yeni
  bir durum — ama kural aynı kural: *"kipin var olduğu çağrı yapıldı, sıra kullanıcıda."* Ayrı bir
  test yazılmıyor; kayıt bunu söylüyor.

## Nasıl görülür

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**On bir test kırmızı**, iki test bekçi olarak yeşil, geri kalan süit yeşil. Kırmızı hâliyle
commit edilir.

| Nerede | Kırmızı |
|---|---|
| `test_tools.py` — aracın yokluğu | 3 |
| `test_tools.py` — modelin verdiği adla işaretleme | 1 |
| `test_modes.py` | 3 |
| `test_prompt.py` | 2 |
| `test_skills.py` | 1 |
| `test_stream_answer.py` | 1 |

Adım adım dökümü [test turunun planında](../plans/2026-09-10-queenagent-m207-test-plan.md).
