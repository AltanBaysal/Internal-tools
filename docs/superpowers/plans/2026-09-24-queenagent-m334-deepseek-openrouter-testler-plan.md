# Madde 334 · Tur 1 (testler) — Plan

**Tasarım:** [2026-09-24-queenagent-m334-deepseek-openrouter-testler-design.md](../specs/2026-09-24-queenagent-m334-deepseek-openrouter-testler-design.md)
**Kaynak:** [yol haritasının Madde 334'ü](../roadmaps/2026-09-21-queen-agent-v9-roadmap.md).

**Bu turda kaynak kod yazılmaz.** On altı test kırmızıya döner, üçü yeşilden yeşile değişir.

**Komutlar** *(sabit satırlar, birebir, paralel; kuyruk eklenmez, daraltılmaz)*:

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

**Yürüten:** testleri alt ajan yazar; takımı koşan ve commit eden ana oturum.

---

## Bağlayıcı kurallar

- **Yalnız test dosyaları.** `config.py`, `main.py`, `client.py`, `models.js`, `queenagent.ipynb` bu
  turda değişmiyor — değişirse tur ikiye karışmış demektir.
- `skip` / `xfail` yok: kırmızı kırmızı commit ediliyor.
- **Ad ve sabitleme satırın alanlarından değil `engine_for`'dan sorulur:** `[3]` sağlayıcıya söylenen
  ad, `[4]` satırın gövdeye eklediği alanlar. Alanların yazılışı uygulama turunun.
- **Model adı ve sağlayıcı kullanıcının 25 Eylül kararı:** `deepseek/deepseek-v4.1-flash`, yalnız
  `deepseek`, `allow_fallbacks` kapalı.
- `dist` bu turda derlenmez: ön uç kaynağı değişmiyor.
- Commit mesajında çift tırnak yok; amend yok.

## Değişen dosyalar

| Dosya | Ne oluyor |
|---|---|
| `queen-agent/backend/tests/test_config.py` | beş test doğar, üçü yeni davranışı ister, bir yorum düzelir |
| `queen-agent/backend/tests/test_xai_client.py` | üç test doğar |
| `queen-agent/backend/tests/test_composition.py` | iki test doğar |
| `queen-agent/backend/tests/test_notebook.py` | üç test doğar, biri genişler, birinin docstring'i düzelir |

---

## Görev 1 · Üçüncü anahtar çevreden gelir

**Dosya:** `queen-agent/backend/tests/test_config.py`

- [ ] **1.1** — `test_the_deepseek_key_comes_from_the_environment`'ın hemen altına:

```python
def test_the_openrouter_key_comes_from_the_environment(monkeypatch):
    # Madde 334: the DeepSeek pair is answered through OpenRouter until DeepSeek's own account is
    # paid for, and that key travels the road the other two do.
    monkeypatch.setenv("OPENROUTER_API_KEY", "or-from-the-environment")
    try:
        assert _reloaded().OPENROUTER_API_KEY == "or-from-the-environment"
    finally:
        monkeypatch.undo()
        _reloaded()
```

**Kırmızının sebebi:** `config`'te `OPENROUTER_API_KEY` yok — `AttributeError`.

---

## Görev 2 · DeepSeek çifti OpenRouter'a, OpenRouter'ın adıyla, yalnız DeepSeek'e

**Dosya:** `queen-agent/backend/tests/test_config.py`

- [ ] **2.1 — adres.** `test_the_three_models_resolve_to_their_provider`'ın gövdesi:

```python
def test_the_three_models_resolve_to_their_provider():
    assert config.MODELS["grok-4.3"]["base_url"] == "https://api.x.ai/v1"
    # Madde 334: the DeepSeek pair goes through OpenRouter while DeepSeek's own account has no
    # credit, and there it is held to DeepSeek itself -- the pin test further down.
    assert config.MODELS["deepseek-v4-flash"]["base_url"] == "https://openrouter.ai/api/v1"
    assert config.MODELS["deepseek-v4-pro"]["base_url"] == "https://openrouter.ai/api/v1"
```

- [ ] **2.2 — anahtar.** `test_each_model_names_the_key_it_spends`'in gövdesi:

```python
def test_each_model_names_the_key_it_spends():
    # Which key a model costs is the model's own business rather than something the composition
    # root is told twice. Madde 334 leaves DEEPSEEK_API_KEY without a row and still read: going
    # back to DeepSeek's own API is a madde of its own, and the way back is these two rows.
    assert config.MODELS["grok-4.3"]["key"] == "XAI_API_KEY"
    assert config.MODELS["deepseek-v4-flash"]["key"] == "OPENROUTER_API_KEY"
    assert config.MODELS["deepseek-v4-pro"]["key"] == "OPENROUTER_API_KEY"
```

- [ ] **2.3 — ilk iki değer.** `test_a_known_model_resolves_to_its_own_wiring`'in gövdesi:

```python
def test_a_known_model_resolves_to_its_own_wiring():
    # The first value is still the app's own id -- the one a message is written with and the engine
    # finds its client by. What the provider is told comes after the key (Madde 334).
    model, base_url = config.engine_for("deepseek-v4-flash")[:2]
    assert (model, base_url) == ("deepseek-v4-flash", "https://openrouter.ai/api/v1")
```

- [ ] **2.4 — sağlayıcıya söylenen ad.** 2.3'ün hemen altına:

```python
def test_the_deepseek_pair_is_sent_under_openrouter_s_names():
    # Madde 334. OpenRouter knows a model as author/slug, while the menu and every stored message
    # carry DeepSeek's own ids -- so the table says what the provider is told, and the ids stay.
    # One name for both rows: DeepSeek's own API had been answering both with V4.1 Flash since 14
    # September, and this keeps that (the user's decision, 25 Eylül).
    assert config.engine_for("deepseek-v4-flash")[3] == "deepseek/deepseek-v4.1-flash"
    assert config.engine_for("deepseek-v4-pro")[3] == "deepseek/deepseek-v4.1-flash"


def test_grok_is_sent_under_its_own_id():
    # xAI knows its model by the id the table is keyed by, and Madde 334 leaves the xAI models as
    # they are.
    assert config.engine_for("grok-4.3")[3] == "grok-4.3"
```

- [ ] **2.5 — sabitleme.** 2.4'ün hemen altına:

```python
PINNED_TO_DEEPSEEK = {"provider": {"order": ["deepseek"], "allow_fallbacks": False}}


def test_the_deepseek_pair_is_answered_by_deepseek_alone():
    """A terms assertion rather than a routing preference (Madde 334, the user's call of 25 Eylül).

    OpenRouter serves these weights from many providers and picks one on its own; `order` names
    DeepSeek and `allow_fallbacks` false is what keeps it from going anywhere else. Whichever
    provider answers is whose terms the request runs under, at least one of them forbids this work,
    and DeepSeek's are the ones the direct API ran under. When DeepSeek does not answer, the error
    shows rather than another provider answering. Madde 149's road, with DeepSeek where DeepInfra
    was.
    """
    assert config.engine_for("deepseek-v4-flash")[4] == PINNED_TO_DEEPSEEK
    assert config.engine_for("deepseek-v4-pro")[4] == PINNED_TO_DEEPSEEK


def test_grok_adds_nothing_to_its_body():
    # Asked as "nothing" in whatever shape config settles on: the point is that an xAI request does
    # not carry OpenRouter's routing.
    assert not config.engine_for("grok-4.3")[4]
```

- [ ] **2.6 — yorum.** `test_the_grok_row_is_kept_as_the_way_back`'in yorumunda *"the notebook's
  three secrets"* → *"its secret in the notebook"*: sırlar dört oluyor, ve sayı söylemeyen cümle iki
  hâlde de doğru. Yeşilden yeşile.

**Kırmızının sebebi:** 2.1 ve 2.3 adres hâlâ `https://api.deepseek.com`; 2.2 anahtar hâlâ
`DEEPSEEK_API_KEY`; 2.4'ün ikisi dördüncü değeri, 2.5'in ikisi beşinci değeri bulamıyor
(`IndexError`).

**Dokunulmayan:** `test_an_unknown_or_absent_model_falls_back_to_the_default` — `[0]` okuyor ve
doğru kalıyor.

---

## Görev 3 · İstemci satırın eklediğini gövdeye katar, kendi alanlarını ezdirmeden

**Dosya:** `queen-agent/backend/tests/test_xai_client.py`

- [ ] **3.1** — `test_a_one_shot_write_sends_no_tools`'un altına,
  `test_an_http_error_carries_the_services_own_words`'ün hemen önüne. `_Lines` aşağıda tanımlı ama
  yalnız opener çalışırken aranıyor, yani sıra sorun değil.

```python
# --- what a row adds to the body (Madde 334) -----------------------------------------------------
#
# OpenRouter reads which provider may answer from the request body, and config holds the DeepSeek
# pair to DeepSeek there. The client carries whatever its row hands it and knows nothing of what it
# means.

_PINNED = {"provider": {"order": ["deepseek"], "allow_fallbacks": False}}


def _openrouter(opener, extra):
    return XaiClient(
        lambda: "key",
        "deepseek/deepseek-v4.1-flash",
        "https://openrouter.ai/api/v1",
        extra=extra,
        opener=opener,
    )


def test_what_a_row_adds_reaches_a_one_shot_request():
    # The frame writer's road (config.PROMPT_MODEL). A pin that held only on the stream would leave
    # every written frame to whichever provider OpenRouter picked.
    seen = {}

    def opener(request):
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return _Response({"choices": [{"message": {"content": "hi"}}]})

    _openrouter(opener, _PINNED).write_once(MESSAGES)
    assert seen["body"]["provider"] == _PINNED["provider"]


def test_what_a_row_adds_reaches_a_streamed_request_too():
    # The road every answer the user waits on takes.
    seen = {}

    def opener(request):
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return _Lines([b"data: [DONE]"])

    list(_openrouter(opener, _PINNED).stream(MESSAGES))
    assert seen["body"]["provider"] == _PINNED["provider"]


def test_the_clients_own_fields_win_over_what_a_row_adds():
    """A row adds; it never takes over. The model is the name the client was built with and the rest
    is the call's own, so what a row adds goes in first and the client writes over it. An order
    rather than a list of names a row may not use: such a list would be a second place to keep up
    to date, and the day it fell behind it would fail open."""
    seen = {}

    def opener(request):
        seen["body"] = json.loads(request.data.decode("utf-8"))
        return _Lines([b"data: [DONE]"])

    extra = {"model": "a-model-nobody-asked-for", "messages": [], "stream": False}
    list(_openrouter(opener, extra).stream(MESSAGES))
    assert seen["body"]["model"] == "deepseek/deepseek-v4.1-flash"
    assert seen["body"]["messages"] == MESSAGES
    assert seen["body"]["stream"] is True
```

**Kırmızının sebebi:** üçünde de `XaiClient` `extra` almıyor — `TypeError: __init__() got an
unexpected keyword argument 'extra'`.

---

## Görev 4 · Bileşim kökü istemciyi o adla ve o alanlarla kurar

**Dosya:** `queen-agent/backend/tests/test_composition.py`

- [ ] **4.1** — `test_the_prompt_writer_is_wired_from_config`'in hemen altına:

```python
def test_each_client_is_built_with_the_name_its_provider_knows():
    """Madde 334. The engine finds a client by the app's own id, and the client sends the model it
    was built with -- so what OpenRouter is told has to be handed over here, from config's wiring
    like the address and the key beside it."""
    assert "config.engine_for(model)[3]" in _main(), (
        "İstemci, modelin sağlayıcıdaki adıyla kurulmuyor"
    )


def test_each_client_is_handed_what_its_row_adds_to_the_body():
    """Madde 334. The pin that keeps the DeepSeek pair on DeepSeek travels in the request body, and
    only the client writes the body -- so what engine_for gives for it has to be handed over here."""
    assert "config.engine_for(model)[4]" in _main(), (
        "İstemciye satırın gövdeye eklediği alanlar verilmiyor"
    )
```

**Kırmızının sebebi:** `main.py` istemciyi `model` ile kuruyor; metinde `engine_for(model)[3]` de
`[4]` de yok.

---

## Görev 5 · Defter üçüncü anahtarı ister ve geçirir

**Dosya:** `queen-agent/backend/tests/test_notebook.py`

- [ ] **5.1 — DeepSeek sırrının gerekçesi.** `test_a_missing_deepseek_key_says_what_to_do`'nun
  docstring'i *(gövde aynı)*:

```python
    """Required rather than optional (kullanıcı kararı, 2 Eylül), and still required though no row
    spends it since Madde 334: the DeepSeek pair goes through OpenRouter only until DeepSeek's own
    account is paid for, and the way back is two rows in config.py -- a secret dropped here would
    be a third thing to bring back."""
```

- [ ] **5.2 — üç yeni test.** `test_the_deepseek_key_travels_to_the_app_in_the_environment`'ın
  hemen altına:

```python
def test_the_openrouter_key_comes_from_secrets():
    """Madde 334: both models the composer offers are answered through OpenRouter until DeepSeek's
    own account is paid for, and the key takes the road the others take."""
    assert 'userdata.get("OPENROUTER_API_KEY")' in _source(), (
        "OpenRouter anahtarı Secrets'tan okunmuyor"
    )


def test_a_missing_openrouter_key_says_what_to_do():
    """Every model the composer offers spends it, and so does the frame writer -- a run opened
    without it could answer nothing at all."""
    said = _cell("assert OPENROUTER_API_KEY")
    assert said, "OpenRouter anahtarı yokken defter sessizce devam ediyor"
    assert "Secrets" in said and "OPENROUTER_API_KEY" in said, "Ne yapılacağı söylenmiyor"


def test_the_openrouter_key_travels_to_the_app_in_the_environment():
    assert '"OPENROUTER_API_KEY": OPENROUTER_API_KEY' in _cell(SERVE), (
        "OpenRouter anahtarı uygulamaya geçirilmiyor"
    )
```

- [ ] **5.3 — kilit genişler.** `test_no_api_key_is_ever_printed`'in docstring'inin son paragrafı ve
  döngüsü:

```python
    Over every key since Madde 146, and the third joined in Madde 334: a rule written for some of
    them is a rule the rest escape.
    """
    for name in ("XAI_API_KEY", "DEEPSEEK_API_KEY", "OPENROUTER_API_KEY"):
```

**Kırmızının sebebi:** 5.2'nin üçü — defterde `OPENROUTER_API_KEY` hiç geçmiyor. 5.1 ve 5.3 yeşilden
yeşile: biri gerekçe, öteki bugün de yarın da geçen bir kilit.

---

## Görev 6 · Takım ve kırmızı commit *(ana oturum)*

- [ ] **6.1** — dört sabit satır, paralel.

Beklenen:

- `python -m pytest queen-agent -q` → **16 yeni kırmızı**: Görev 1'in biri, Görev 2'nin yedisi,
  Görev 3'ün üçü, Görev 4'ün ikisi, Görev 5.2'nin üçü. Başka kırmızı yok.
- `npm test --prefix queen-agent/frontend` → dokunulmadı, yeni kırmızı yok.
- queen-editor'ün iki satırı → dokunulmadı.

- [ ] **6.2 — commit:** yalnız dört test dosyası, tasarım ve bu plan.

```
test(m334): red asks the DeepSeek pair to reach DeepSeek alone through OpenRouter
```

---

## Kendi kontrolü

- **Tasarımın her iddiası bir göreve düşüyor mu?** 1 → Görev 1; 2 ve 3 → 2.4; 4 ve 5 → 2.5; 6–8 →
  Görev 3; 9 ve 10 → Görev 4; 11–13 → 5.2. *Değişen* tablosu: dört `test_config.py` satırı →
  2.1–2.3 ve 2.6; iki `test_notebook.py` satırı → 5.1 ve 5.3.
- **Yer tutucu var mı?** Yok.
- **Ad tutarlılığı:** `OPENROUTER_API_KEY` (config sabiti, çevre adı, Secrets adı, Serve'deki anahtar —
  dördü aynı yazılış); `engine_for(...)[3]` ad, `[4]` gövde alanları — Görev 2 ve 4'te aynı sıra;
  `extra=` istemcinin yeni parametresi, 149'un adı; `deepseek/deepseek-v4.1-flash` ve
  `{"provider": {"order": ["deepseek"], "allow_fallbacks": False}}` Görev 2 ve 3'te birebir aynı.
  `_reloaded`, `_main`, `_source`, `_cell`, `SERVE`, `_Response`, `_Lines`, `MESSAGES` — hepsi ilgili
  dosyada zaten kurulu.
- **`dist` gerekiyor mu?** Hayır: bu tur kaynağa dokunmuyor.
