# Madde 520 · Seçilen bir kare yalnız kendisi sayılır — plan

**Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-19), 520 · v11-19 ·
**Spec:** [2026-10-30-queen-editor-m520-secim-yalniz-kendisi-design.md](../specs/2026-10-30-queen-editor-m520-secim-yalniz-kendisi-design.md)

Önce test: testler yeni kuralı söyler (kırmızı), sonra kod (yeşil). Kopyala'nın seçimi ikizlere taşıması
kullanıcının kararıyla kalır (30 Ekim, "2"); galeriye dokunulmaz.

## 1. Testler

**Sunucu** — `backend/tests/test_photo_usecases.py`
- `test_a_selection_of_one_frame_leaves_its_twin_alone`: `twin_project((0, "a"))`, `copy_of(["0_a"])`;
  önce bugünkü çağrıyla (`files=["0_a.png"]`) yazılır ve 2 iş görülür (kırmızı), sonra `frames=["0_a"]`.
- Seçimle çağıran testler kimliğe: `ask_again`'in `files`'ı `frames`; `queue_video`'nun kullanılmayan
  `files`'ı kalkar; `frames_in_scope(gallery, …, ["0_a.png"])` → `["0_a"]` (dört test); `files=["…png"]`
  → `frames=["…"]` (seçimi daraltma, her varyantın kopya olması, kopyanın yeri, galerinin çizimi).

**Sunucu** — `test_made_once.py`, `test_plan_hold.py`
- `video_press`, iki varyantlı çift basış, kopyanın tuttuğu videonun üstüne yazılmaması
  (`parametrize("frames", [None, ["P1_0"]])`), 516'nın kilit testi: kimlikle.

**Sunucu** — `test_photo_routes.py`
- `{"frames": ["P0_0"]}` yalnız `P0_0`'a video planlar; `{"frames": "P0_0"}` 400 ve cümle, plana video
  yazılmaz.
- `{"frames": null}` 400 ve aynı cümle, plana video yazılmaz (kırmızı: 202).
- `{"files": ["P0_0.png"]}` 400 ve *"Kareler frames ile gönderilmeli."*, plana video yazılmaz (kırmızı:
  202).

**Ekran** — `features/photo_generation/LayerPanel.test.jsx`
- "asks only for what is selected": `C1_0_a` ikiziyle, `onQueue(["0_a"], 1, "loop")`.
- Bağlantı kırılınca düşen mod: `onQueue(["2_a", "0_a"], 1, "standard")`.

**Ekran** — `shared/api.test.js`
- `queueLayer("düğün", "video", ["0_a"], 2, "loop")` gövdesi `{frames: ["0_a"], variants: 2, mode: "loop"}`.

## 2. Kod

**Sunucu**
- `domain/usecases/queue_layer.py`: `files` → `frames`; doğrulama `frame_list.checked(frames,
  "Katman eklenecek")`; `InvalidScope` kalkar; `frames_in_scope` `frame["id"]` ile seçer.
- `presentation/routes.py`: `files` taşıyan gövde 400; `frames` anahtarı varsa `checked` (`null` 400),
  yoksa `None`; `InvalidFrames` → 400;
  `InvalidScope` importu kalkar.
- `domain/frame_list.py`: docstring kimlik listesi alan kapıları sayar.

**Ekran**
- `useGeneration.js`: `queueLayer`'ın parametresi `frames`.
- `LayerPanel.jsx`: seçimin kimlikleri gönderilir.
- `shared/api.js`: `queueLayer` gövdesi `{frames}`.

## 3. Bitiş

- BACKLOG'dan iş silinir (davranış v4'ün kararı).
- `npm run build --prefix queen-editor/frontend`.
- Takımlar sırayla: `python -m pytest queen-editor -q`, `npm test --prefix queen-editor/frontend`.
