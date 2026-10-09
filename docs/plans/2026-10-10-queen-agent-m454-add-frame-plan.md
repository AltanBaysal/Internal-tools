# Madde 454 — `add_scene` `add_frame` olur, plan

> **Koşum:** ana klasörde, `feat/queenagent-v10` dalında, **commit'lenmeden** ve hiçbir şey stage
> edilmeden — modele giden metni ana agent okur, commit onundur. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** frame'in üç tool'u tek kelimeyle: `add_frame`, `update_frame`, `remove_frame`. Davranış aynı.

**Yaklaşım:** önce testler yeni adı ister ve eski adın gittiğini söyler, kırmızı görülür; sonra kod.
Dosyalar Edit ile değişir.

**Spec:** [m454](../specs/2026-10-10-queen-agent-m454-add-frame-design.md)

## Her yere geçerli kurallar

- Yalnız adlar: tool `add_frame`, liste parametresi `frames` (ana agent, 10 Ekim), ve parametreyi anan
  üç cümle; öbür tarifler ve cevaplar aynı.
- 456'nın işi — karakter, kıyafet, mekânın add / update çiftleri — dokunulmaz.
- Skill metinleri, frontend, `dist`, queen-editor dokunulmaz.
- `git add`, commit, stash yok.

---

## Görev 1: Testler — kırmızı

- [ ] `test_tools.py`: `"add_scene"` dizeleri `"add_frame"`; test adlarındaki `add_scene` `add_frame`;
  `ADD_SCENE` içe aktarması `ADD_FRAME`; şimdiki tool'u anan yorumlar yeni adla.
- [ ] `test_tools.py`: yeni `test_add_scene_is_no_longer_a_tool` — runner *"no tool called add_scene"*
  diyor, ve `TOOL_SPECS`'in JSON'unda `add_scene` yok; `test_add_frames_is_no_longer_a_tool`'un yanında.
- [ ] `test_modes.py`: `WRITES`'ta ve Plan testinde `add_frame`; yeni
  `test_no_mode_lets_the_old_scene_tool_through`, listelerden okuyarak.
- [ ] `test_skills.py`: düzenleme skill'i `add_frame`'i anmıyor (`add_frames`'i de kapsar).
- [ ] `test_prompt.py`: `_descriptions_in`'in yorumu `add_frame`'i anar.
- [ ] `python -m pytest queen-agent/backend/tests/test_tools.py queen-agent/backend/tests/test_modes.py -q`
  — kırmızı.

## Görev 2: Kod — yeşil

- [ ] `prompt.py`: altı `ADD_SCENE*` sabiti `ADD_FRAME*`; metinler aynı.
- [ ] `tools.py`: `TOOL_SPECS`'te ad ve sabitler; `run_tool`'un dalı; `_add_scene` → `_add_frame`; ret
  cümlesi *"add_frame takes a list of scenes, …"*; `_numbered`'ın ve `_update_frame`'in yorumları.
- [ ] `modes.py`: Edit modunun listesinde `add_frame`.
- [ ] Aynı iki dosya — yeşil. `add_scene` için repo'da grep: yalnız eski adın gittiğini söyleyen
  testlerde ve `docs/`'ta.

## Görev 2b: `scenes` → `frames` (ana agent, 10 Ekim)

- [ ] `test_tools.py`: çağrılar `frames=`; şemanın testi `properties["frames"]`; liste değilken ret
  *"add_frame takes a list of frames"*; boş liste *"No frames were given, so scene.json is unchanged."*;
  yeni `test_the_frames_argument_is_named_after_what_it_holds`. `test_prompt.py`'nin yorumu. Kırmızı.
- [ ] `prompt.py`: `ADD_FRAME_SCENES` → `ADD_FRAME_FRAMES`, *"The frames to add. …"*. `tools.py`:
  parametre, zorunlular, `args.get("frames")`, iki cümle. Yeşil.

## Görev 2c: Reviewer'ın bulguları (ana agent, 10 Ekim)

- [ ] A: öğe reddi *"a frame is an object …"*, `ADD_FRAME`'in *"Every name a frame uses … every frame in
  the call"*; testi tam cümleyle.
- [ ] B: `_add_frame`'in döngüsü ve `_frame_from` öğeyi `given` der; docstring ve yorum *frame*; iki test
  adı *frame*.
- [ ] C: `test_modes.py`'nin yedi ad testi tek genel test; `test_add_scene_is_no_longer_a_tool` yalnız
  açıklama kontrolü olarak kalır (`test_no_tool_text_points_at_add_scene`).
- [ ] D: parametre kümesi tek eşitlik.
- [ ] E: "replays it" yorumları doğru olanı söyler — üç yerde.

## Görev 3: Dört suite

- [ ] `python -m pytest queen-agent -q`; `npm test --prefix queen-agent/frontend`;
  `python -m pytest queen-editor -q`; `npm test --prefix queen-editor/frontend` — birer birer.
- [ ] `git status`: yalnız spec, plan, `prompt.py`, `tools.py`, `modes.py` ve dört test dosyası.
