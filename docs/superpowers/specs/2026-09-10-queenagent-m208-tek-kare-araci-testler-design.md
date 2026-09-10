# Madde 208 — tek kare yazan araç kalkar · test turu

**Kaynak:** [yol haritasının Madde 208'i](../plans/2026-09-06-queenagent-v8-roadmap.md).

## Ne kanıtlanacak

`write_frame_prompt` kalkmış bir sebebin üstünde duruyor. Madde 174 aksiyonu kare araçlarının
dışında tuttu çünkü **ana model o cümleyi yazmıyordu**; 176 yazacak bir modele verdi. 201 bunun
artık doğru olmadığını kendi yorumuna yazdı — *"That is no longer true of the model running the
conversation"* — ve düzeltmeyi `update_frame`'e aldı.

Geriye aracın **tek** işi kaldı: bir satırı sahneden yeniden yazdırmak, ve bunu **satırı hiç
okumamış** bir modele not yazarak yaptırmak. 201 tam olarak bunu eleştirmişti.

**Toplu araç kalıyor.** `write_missing_actions` ilk yazımı paralel ve ucuz yapıyor — yirmi kare için
ajanın yirmi turu yerine yirmi ucuz istek. `_frame_seen` ile yazarın sistem mesajı onun için yerinde
kalır; yalnız `_frame_seen`'in `note` parametresi ölür, çünkü toplu yol oraya hep `None` geçiyor.

## İki yol, iki araç

| Ne isteniyor | Bugün | 208'den sonra |
|---|---|---|
| Boş karelerin satırı yazılsın | `write_missing_actions` | değişmiyor |
| Var olan bir satır düzeltilsin | `update_frame` *(201)* | değişmiyor |
| Var olan bir satır **sahneden yeniden** yazılsın | `write_frame_prompt` + not | `update_frame` — ajan kendi yazar |

Üçüncü satır maddenin tamamı. Ajanın elinde zaten sahne, kadronun etiketleri ve mekân var — hepsi
kendi yazdığı şeyler — ve satırı kendisi yazınca **tek çağrı** oluyor, ikinci sağlayıcıya para
gitmiyor.

**Ses tutarlılığı, ve kaydı dürüst olsun:** öteki kareler DeepSeek'ten geliyor, ajanın yazdığı bir
kare onlarla aynı üslupta olmayabilir. Bu ayrımı 201 açtı; bu madde onu genişletiyor, açmıyor.

## Yazılacak testler — kırmızı

### `test_tools.py`

- **`test_the_single_frame_tool_is_gone`** — ad `TOOL_SPECS`'te yok, ve o adla yapılan bir çağrı
  `no tool called` diyor.
- **`test_the_single_frame_tools_texts_are_gone`** — `prompt` modülünde ne `WRITE_FRAME_PROMPT` var
  ne `WRITE_FRAME_PROMPT_NOTE`. Not metni ayrıca anılıyor, çünkü **not yolu** bu maddenin asıl
  kaldırdığı şey.
- **`test_a_new_frame_points_at_the_bulk_writer`** — `add_scene`'in tarifi ilk yazımı
  `write_missing_actions`'a gönderir, kalkan aracı anmaz. Var olan testin *(`..._points_at_the_writer_...`)*
  yeniden yazılmış hâli; `update_frame` hakkındaki yarısı olduğu gibi duruyor.
- **`test_the_bulk_tools_text_stands_on_its_own`** — `WRITE_MISSING_ACTIONS` artık *"the same model
  write_frame_prompt asks"* demiyor, ve düzeltmeyi `update_frame`'e gönderiyor.

### `test_modes.py`

- **`test_no_mode_lets_the_single_frame_tool_through`** — hiçbir kipin sormadan-koşanlar listesi adı
  taşımıyor. Listeye bakarak, `needs_permission` üzerinden değil *(205'in kaydettiği tuzak)*.

### `test_skills.py`

- **`test_the_editor_sends_both_jobs_to_the_agent_itself`** — editör metni kalkan aracı anmıyor, ve
  hem *"yanlış okunan satır"* hem *"sahneden yeniden yazılacak satır"* için `update_frame` diyor.
  Var olan `test_a_correction_names_the_single_frame_tool`'un yerine geçer.

## Yazılacak testler — bekçi *(bugün de yeşil)*

Kalkan aracın testlerinden **ikisinin iddiası** toplu araçta da geçerli, ve bugün yalnız kalkan
araç üzerinden tutuluyor. Yerleri şimdi kuruluyor ki hiçbir iddia bir an bile tutulmasız kalmasın:

- **`test_the_bulk_writer_is_handed_the_scene_the_cast_and_the_place`** — `_frame_seen`'in içeriği,
  toplu yoldan.
- **`test_the_bulk_answer_is_a_receipt_rather_than_the_prompt`** — Madde 130: yazılan cümle cevaba
  konmaz. Toplu tarafta bugün yalnız *sayılar* tutuluyor, cümlenin **yokluğu** tutulmuyor.

## Bu turda yazılmayanlar

- **Ölecek testler silinmiyor.** Madde 176'nın bölümünde on dört test bugün yeşil.
- **`test_stream_answer.py`'nin dört kurgusu** kalkan aracı harcayan araç olarak kullanıyor. Onlar
  kodla birlikte `write_missing_actions`'a geçer — uygulama turunun işi.
- **`write_missing_actions`, `_frame_seen`, `WRITE_FRAME_SYSTEM_PROMPT`** duruyor.

## Nasıl görülür

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Altı test kırmızı**, iki bekçi yeşil, geri kalan süit yeşil. Kırmızı hâliyle commit edilir.
