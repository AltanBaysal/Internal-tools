# Madde 397 — Kutu QueenAgent'ın yeni listesini okur, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Spec'in on bir testi ve `plan_frames`'in iki değişen testi — yeni testler kırmızı.

**Spec:** [m397 test turu](../specs/2026-09-30-queen-editor-m397-yeni-liste-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**; cümleler sunucudan harfi harfine. Kaynak kod değişmiyor.
- Yeni okuyucu modülün üstünden çağrılıyor — `prompt_list.parse_photo_list` — ki kırmızı koşuda eksik
  isim toplamayı durdurmasın.

---

## Görev 1: `queen-editor/backend/tests/test_prompt_list.py`

İçe aktarmaya modülün kendisi:

```python
from backend.features.photo_generation.domain import prompt_list
from backend.features.photo_generation.domain.prompt_list import InvalidPrompts, parse_prompts
```

Dosyanın sonuna:

```python
# QueenAgent's list, in the shape its build_prompts.render_module writes: a record per frame, each
# value in triple quotes.
QUEEN_AGENT_LIST = '''PROMPTS = [
    {
        "scene": """Kraliçe tahtında oturuyor; salon boş ve karanlık.""",
        "photo": """score_9_up, 1girl, queen, crown BREAK sitting on a throne, throne room""",
    },
    {
        "scene": """Kraliçe gece bahçede yürüyor, fenerler yanıyor.""",
        "photo": """score_9_up, 1girl, queen BREAK walking, night garden, lanterns""",
    },
]
'''


def test_queen_agent_s_list_gives_each_frame_its_photo_prompt_and_scene():
    assert prompt_list.parse_photo_list(QUEEN_AGENT_LIST) == [
        {"prompt": "score_9_up, 1girl, queen, crown BREAK sitting on a throne, throne room",
         "scene": "Kraliçe tahtında oturuyor; salon boş ve karanlık."},
        {"prompt": "score_9_up, 1girl, queen BREAK walking, night garden, lanterns",
         "scene": "Kraliçe gece bahçede yürüyor, fenerler yanıyor."},
    ]


def test_the_flat_list_reads_as_it_does_today_and_carries_no_scene():
    assert prompt_list.parse_photo_list('PROMPTS = ["a", "", "b"]') == [{"prompt": "a"},
                                                                       {"prompt": "b"}]


@pytest.mark.parametrize("text", [
    '[{"photo": "a"}]',
    '[{"scene": "s"}]',
    '[{"scene": "s", "photo": 3}]',
    '["a", {"scene": "s", "photo": "p"}]',
    '{"scene": "s", "photo": "p"}',
])
def test_a_list_of_records_it_cannot_read_gets_the_same_one_line(text):
    with pytest.raises(InvalidPrompts) as exc:
        prompt_list.parse_photo_list(text)
    assert str(exc.value) == "Format hatası — liste okunamadı"


def test_a_record_with_a_blank_photo_is_left_out_like_a_blank_item():
    text = '[{"scene": "s", "photo": "a"}, {"scene": "t", "photo": "  "}]'
    assert prompt_list.parse_photo_list(text) == [{"prompt": "a", "scene": "s"}]
```

## Görev 2: `queen-editor/backend/tests/test_photo_usecases.py` — iki değişen test

`test_plan_frames_is_prompt_major`'da yalnız çağrı:

```python
    assert plan_frames(3, [{"prompt": "ilk"}, {"prompt": "ikinci"}], "neg", 2,
                       lambda: next(seeds), "nova.safetensors") == [
```

Beklenen dört satır olduğu gibi — `scene` alanı yok.

`test_a_planned_frame_carries_the_lora_it_was_submitted_under`'da:

```python
    frames = plan_frames(0, [{"prompt": "kraliçe"}], "", 1, lambda: 7, model="nova3dcg",
                         lora="slime")
```

## Görev 3: `queen-editor/backend/tests/test_photo_routes.py` — yeni blok, dosyanın sonuna

```python
# Madde 397: the photo panel's box reads QueenAgent's list. Its shape is QueenAgent's own
# (build_prompts.render_module): a record per frame, each value in triple quotes.
THRONE = "Kraliçe tahtında oturuyor; salon boş ve karanlık."
GARDEN = "Kraliçe gece bahçede yürüyor, fenerler yanıyor."
QUEEN_AGENT_LIST = '''PROMPTS = [
    {
        "scene": """Kraliçe tahtında oturuyor; salon boş ve karanlık.""",
        "photo": """score_9_up, 1girl, queen, crown BREAK sitting on a throne, throne room""",
    },
    {
        "scene": """Kraliçe gece bahçede yürüyor, fenerler yanıyor.""",
        "photo": """score_9_up, 1girl, queen BREAK walking, night garden, lanterns""",
    },
]
'''


def scenes_of(client, project="düğün"):
    """{card: its scene} -- what the frames API hands out."""
    return {row["id"]: row["scene"]
            for row in client.get(f"/api/projects/{project}/frames").get_json()["frames"]}


def test_queen_agent_s_list_opens_a_card_per_frame(tmp_path):
    generator = FakeGenerator()
    client, _ = make_client(tmp_path, generator=generator)

    resp = generate(client, prompts=QUEEN_AGENT_LIST, variants=1)

    assert resp.status_code == 202
    assert resp.get_json()["added"] == 2
    # The photo prompt is the record's photo, and the negative is the panel's own: the list brings
    # none (v8-3).
    assert [(prompt, negative) for prompt, negative, _seed, _model in generator.calls] == [
        ("score_9_up, 1girl, queen, crown BREAK sitting on a throne, throne room", "blurry"),
        ("score_9_up, 1girl, queen BREAK walking, night garden, lanterns", "blurry"),
    ]


def test_the_frames_api_hands_out_each_card_s_scene(tmp_path):
    client, _ = make_client(tmp_path)

    generate(client, prompts=QUEEN_AGENT_LIST, variants=1)

    assert scenes_of(client) == {"P0_0": THRONE, "P1_0": GARDEN}


def test_a_card_from_the_flat_list_has_no_scene(tmp_path):
    client, _ = make_client(tmp_path)

    generate(client, prompts='["a"]', variants=1)

    assert scenes_of(client) == {"P0_0": ""}


def test_a_video_variant_keeps_the_scene_of_the_frame_it_was_copied_from(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts=QUEEN_AGENT_LIST, variants=1)

    client.post("/api/projects/düğün/layers/video", json={"variants": 2})

    assert scenes_of(client)["P0_1"] == THRONE


def test_a_twin_keeps_its_sources_scene(tmp_path):
    client, _ = make_client(tmp_path)
    generate(client, prompts=QUEEN_AGENT_LIST, variants=1)

    copy_frames_request(client, ["P0_0"])

    assert scenes_of(client)["C1_P0_0"] == THRONE


def test_a_frame_made_again_with_new_words_keeps_the_scene(tmp_path):
    # New words start a new prompt's family, but the picture is still this frame's.
    client, _ = make_client(tmp_path)
    generate(client, prompts=QUEEN_AGENT_LIST, variants=1)

    frame = regenerate_request(client, "P0_0", prompt="başka").get_json()["frame"]

    assert scenes_of(client)[frame] == THRONE


def test_a_card_whose_photo_is_deleted_keeps_its_scene(tmp_path):
    client, drive = make_client(tmp_path)
    generate(client, prompts=QUEEN_AGENT_LIST, variants=1)
    give_it_a_video(drive)

    delete_layer_request(client, ["P0_0"], layer="photo")

    assert scenes_of(client)["P0_0"] == THRONE
```

## Görev 4: Koşu ve kırmızı commit

- [ ] Dört satır paralel, yazıldığı gibi *(CLAUDE.md, Commands)*; iki npm satırı arka planda.
- [ ] Beklenen: `queen-editor` pytest'inde kırmızı — Görev 1'in dört testi *(parametreliyle sekiz
      durum; `parse_photo_list` yok)*, `test_plan_frames_is_prompt_major` *(satırın `prompt`'u girdinin
      kendisi)*, Görev 3'ün yedi testi *(yeni listeye `Format hatası`, kartta `scene` yok)*. Lora testi
      yeşil. Öteki üç satır yeşil.
- [ ] Spec, plan ve üç test dosyası tek commit'te: `test(queen-editor): Madde 397 red -- …`.
