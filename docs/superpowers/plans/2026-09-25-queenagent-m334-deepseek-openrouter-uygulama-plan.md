# Madde 334 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-25-queenagent-m334-deepseek-openrouter-uygulama-design.md](../specs/2026-09-25-queenagent-m334-deepseek-openrouter-uygulama-design.md)
**Test turu:** [2026-09-24-queenagent-m334-deepseek-openrouter-testler-design.md](../specs/2026-09-24-queenagent-m334-deepseek-openrouter-testler-design.md) — 16 kırmızı, `c8e9e587`.
**Kaynak:** [yol haritasının Madde 334'ü](../roadmaps/2026-09-21-queen-agent-v9-roadmap.md).

**Komutlar** *(sabit satırlar, birebir, paralel; kuyruk eklenmez, daraltılmaz)*:

```bash
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
npm run build --prefix queen-agent/frontend
```

**Yürüten:** kodu alt ajan yazar; takımı koşan, `dist`'i derleyen ve commit eden ana oturum.

---

## Bağlayıcı kurallar

- **Commit'lenmiş testlere dokunulmaz.** Biri yanlış görünürse durulur ve koordinatöre söylenir.
- Testlerin istediğinden fazlası yazılmaz; yorumlar yalnız bu maddeyle yalan olanlarda düzelir.
- Yorum **neden**'i söyler ve yalnız bugün doğru olanı; `OLD`/`NEW` izi yok. Yoğunluk çevredeki
  kodunki kadar.
- Defterde çalışma zamanı metni Türkçe, yorumlar İngilizce; *"Settings"* kelimesi yazılmaz
  (`test_the_notebook_no_longer_points_at_a_settings_screen`), `print` bir anahtarın değerini asla
  içine almaz.
- Defter JSON'da hücre başına tek satır dize olarak duruyor: düzenleme kaçışlı metnin birebir
  parçasıyla yapılır, dosya yeniden yazılmaz — başka hiçbir satır kımıldamasın.
- `dist` bu turda alt ajan tarafından derlenmez; koordinatör derler ve kaynakla aynı commit'e koyar.
- Commit mesajında çift tırnak yok; amend yok.

## Değişen dosyalar

| Dosya | Ne oluyor |
|---|---|
| `queen-agent/backend/config.py` | üçüncü anahtar, sabitleme, iki satır, `engine_for`'un beş değeri |
| `queen-agent/backend/services/xai/client.py` | `extra` parametresi, gövdede önce o |
| `queen-agent/main.py` | istemci `[3]` ile kuruluyor, `[4]` `extra` olarak veriliyor |
| `queen-agent/queenagent.ipynb` | CONFIG okuyor, istiyor, sayıyor; Serve geçiriyor |
| `queen-agent/frontend/src/features/workspace/models.js` | yalnız yorum |
| `queen-agent/README.md` | yerel çalıştırmanın anahtarı |

---

## Görev 1 · `config.py`

- [ ] **1.1 — anahtarlar ve sabitleme.** `DEEPSEEK_API_KEY`'in yorumu ve arkasına iki tanım:

```python
# DeepSeek's own key, since Madde 146, and it travels the same road. No row spends it since Madde
# 334 -- the account has no credit, so the pair goes through OpenRouter -- and it is read all the
# same: going back is a madde of its own, and it is the two rows below pointing at
# https://api.deepseek.com again (no /v1: that is DeepSeek's own documented base, and the client
# appends /chat/completions to whatever it is handed).
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
# What every answer spends while the DeepSeek pair goes through OpenRouter (Madde 334), on the
# same road.
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")

# Who may answer the DeepSeek pair on OpenRouter, and it is a terms choice rather than a routing
# preference.
#
# OpenRouter serves these weights from many providers and picks one on its own; `order` names
# DeepSeek and `allow_fallbacks` false is what keeps it there. Whichever provider answers is whose
# terms the request runs under, at least one of them forbids this work, and DeepSeek's are the ones
# the direct API ran under. When DeepSeek does not answer, the error shows rather than another
# provider answering -- the user's call of 25 September, and Madde 149's road with DeepSeek where
# DeepInfra was.
#
# A body field rather than a header: this is where OpenRouter reads it.
_ONLY_DEEPSEEK = {"provider": {"order": ["deepseek"], "allow_fallbacks": False}}
```

- [ ] **1.2 — tablo.** `MODELS`'in üstündeki yoruma bir paragraf, Grok satırının yorumunda sayı
  gidiyor, DeepSeek satırları OpenRouter'a:

```python
# Madde 82 named one model here and Madde 146 made it three. That madde tore the picking machinery
# out because a single model left it idle; two more ended the premise rather than overturned it.
#
# Since Madde 334 a row can say two more things, and only the DeepSeek pair does: `model` is what
# the provider is told when that is not the id itself, and `extra` is what the row adds to the body
# of every request it makes. Absent rather than empty on Grok's -- a field saying nothing is noise.
MODELS = {
    # Nothing points here since Madde 202 moved the writing to DeepSeek, and by Madde 183's own rule
    # -- a row nobody will use is dead configuration -- this one would go. Kept knowingly: deleting
    # it takes XAI_API_KEY and its secret in the notebook with it, and what the run was for was
    # trying another writer. If the lines come out worse, going back is the constant below.
    "grok-4.3": {"base_url": "https://api.x.ai/v1", "key": "XAI_API_KEY"},
    # Through OpenRouter until DeepSeek's own account is paid for (Madde 334). The ids stay
    # DeepSeek's own -- the menu and every message on disk carry them -- and OpenRouter is told
    # V4.1 Flash for both, because that is what DeepSeek's own API had been answering both with
    # since 14 September.
    "deepseek-v4-flash": {
        "base_url": "https://openrouter.ai/api/v1",
        "key": "OPENROUTER_API_KEY",
        "model": "deepseek/deepseek-v4.1-flash",
        "extra": _ONLY_DEEPSEEK,
    },
    "deepseek-v4-pro": {
        "base_url": "https://openrouter.ai/api/v1",
        "key": "OPENROUTER_API_KEY",
        "model": "deepseek/deepseek-v4.1-flash",
        "extra": _ONLY_DEEPSEEK,
    },
}
```

- [ ] **1.3 — `engine_for`.** Docstring'in ilk satırı ve dönüş:

```python
def engine_for(model_id):
    """Which model, over which address, spending which key, told the provider under which name, and
    carrying what in its body.
    ...
    """
    chosen = model_id if model_id in MODELS else DEFAULT_MODEL
    wiring = MODELS[chosen]
    # The module's own constant, looked up by the name the row carries -- not a second read of the
    # environment. There is one road for a key and it is the assignment above; a row that fetched
    # its own would be a second one, and the two would part the day either moved.
    #
    # `get` on the last two: a row whose provider knows the model by its id has no other name to
    # give, and a row with nothing for the body has nothing -- a row with nothing to say rather than
    # a row missing something.
    return (
        chosen,
        wiring["base_url"],
        globals()[wiring["key"]],
        wiring.get("model", chosen),
        wiring.get("extra"),
    )
```

**Yeşile dönen:** `test_config.py`'nin sekizi.

---

## Görev 2 · `client.py`

- [ ] **2.1 — parametre.**

```python
    def __init__(self, read_key, model, base_url, extra=None, opener=urllib.request.urlopen):
        ...
        self._base_url = base_url.rstrip("/")
        # What this model's row adds to the body on top of the ordinary fields (Madde 334). Carried,
        # never read: what it says is config's business. A dict from here on, because None cannot be
        # spread and one conversion beats a condition on every request.
        self._extra = extra or {}
```

- [ ] **2.2 — gövde.** `_request`'te:

```python
        # One model, named once where this client is built. There used to be a per-call one that
        # won over it, back when a chat could pick its own.
        #
        # What the row adds leads and this client's own fields follow, so a row can never decide
        # which model a request names or what it carries (Madde 334). An order rather than a list of
        # names a row may not use: such a list would be a second place to keep up to date, and the
        # day it fell behind it would fail open.
        payload = {**self._extra, "model": self._model, **body}
```

**Yeşile dönen:** `test_xai_client.py`'nin üçü. `write_once` ve `stream` `_request`'i paylaşıyor,
ayrıca değişmiyorlar.

---

## Görev 3 · `main.py`

- [ ] **3.1**

```python
# Where the key comes from is still this file's decision, not the client's -- which is why it is
# handed over as a function even though the value settles once, at startup. `engine_for` is asked
# for each id in turn, so the address and the key a model spends stay its own -- and since Madde
# 334 so do the name its provider knows it by and what its row adds to the body. The map stays
# keyed by the app's own id, the one a message carries; only the client is told the provider's.
engine = XaiEngine(
    {
        model: XaiClient(
            lambda wiring=config.engine_for(model): wiring[2],
            config.engine_for(model)[3],
            config.engine_for(model)[1],
            extra=config.engine_for(model)[4],
        )
        for model in config.MODELS
    },
```

**Yeşile dönen:** `test_composition.py`'nin ikisi. Öteki üçü *(`config.engine_for` geçiyor,
`os.environ` geçmiyor, `config.PROMPT_MODEL` geçiyor)* yeşil kalıyor.

---

## Görev 4 · `queenagent.ipynb`

Her adım, kaçışlı JSON dizesinin birebir bir parçasını değiştirir.

- [ ] **4.1 — CONFIG, sayı:** `# All three from Colab's Secrets store` → `# All four from Colab's
  Secrets store`.
- [ ] **4.2 — CONFIG, okuma:** DeepSeek'in `try` bloğunun arkasına:

```python
try:
    OPENROUTER_API_KEY = userdata.get("OPENROUTER_API_KEY")
except Exception:
    OPENROUTER_API_KEY = ""
```

- [ ] **4.3 — CONFIG, gerekçe ve istek:** *"Both keys, not one of them..."* paragrafının yerine, ve
  `assert XAI_API_KEY`'in önüne:

```python
# OPENROUTER_API_KEY is what every answer spends since Madde 334: both models the composer
# offers go through OpenRouter, and so does the frame writer (config.PROMPT_MODEL). The other two
# are asked for as the ways back -- xAI's since Madde 202 took the writing off Grok, DeepSeek's
# until its own account is paid for again -- and a secret dropped here would be one more thing to
# bring back.
assert OPENROUTER_API_KEY, (
    "❌ OPENROUTER_API_KEY yok — Colab solundaki 🔑 Secrets panelinden 'OPENROUTER_API_KEY' adıyla "
    "kendi OpenRouter anahtarını ekle ve bu deftere erişimi aç "
    "(openrouter.ai/keys üzerinden alınır)."
)
```

- [ ] **4.4 — CONFIG, `print`:**

```python
print("✓ GITHUB_TOKEN, XAI_API_KEY, DEEPSEEK_API_KEY ve OPENROUTER_API_KEY Secrets'tan okundu")
```

- [ ] **4.5 — Serve, yorum:**

```python
# Four things the app learns only from here. QUEENAGENT_ROOT is where it writes; left unset it
# falls back to a home directory, which here is Colab's own disk -- everything would die with the
# runtime and the user would only find out the next day. The three keys are the whole of what it
# knows about them: it saves none, asks for none, and reads these at startup (backend/config.py).
# Which of them a turn spends is decided by the model picked in the composer, and config.py's table
# is what turns that choice into a key.
```

- [ ] **4.6 — Serve, çevre:** `"DEEPSEEK_API_KEY": DEEPSEEK_API_KEY,`'in altına
  `"OPENROUTER_API_KEY": OPENROUTER_API_KEY,`.

**Yeşile dönen:** `test_notebook.py`'nin üçü. `test_no_api_key_is_ever_printed` yeşil kalıyor:
`print` adları düz metin olarak sayıyor.

---

## Görev 5 · Yazılar

- [ ] **5.1 — `models.js`, yalnız yorum.** 9–13. satırlar:

```js
// The names are this file's own, and only this file's. An id is the key config.py's table is
// looked up by and what every message on disk records, so renaming one strands the records that
// name it -- and what the provider is told is config.py's business, which since Madde 334 is not
// always the id. Queen Flash and Queen Pro are what a person sees instead. Nothing enforces that
// the ids here match config.py's table: Python and JS cannot read each other, and this sentence is
// the whole of what keeps the two in step.
```

- [ ] **5.2 — `README.md`.** Export satırı ve iki cümle:

```bash
export OPENROUTER_API_KEY=...  # or set it however your shell does
```

*"The key is read at startup and the app saves none of it"* → *"The keys are read at startup and
the app saves none of them"*; *"that, the key and every other setting"* → *"that, the keys and
every other setting"*.

---

## Görev 6 · Takım, `dist` ve commit *(ana oturum)*

- [ ] **6.1** — dört sabit test satırı, paralel. Beklenen: 16 kırmızı yeşil; başka kırmızı yok.
- [ ] **6.2** — `npm run build --prefix queen-agent/frontend`; `dist` değiştiyse kaynakla aynı
  commit'e.
- [ ] **6.3 — commit:**

```
feat(m334): the DeepSeek pair answers through OpenRouter, from DeepSeek alone
```

---

## Kendi kontrolü

- **Tasarımın her maddesi bir göreve düşüyor mu?** config → Görev 1; client → 2; main → 3; defter →
  4; `models.js` ve README → 5.
- **Yer tutucu var mı?** Yok.
- **Ad tutarlılığı:** satır alanları `model` ve `extra`; `engine_for`'un `[3]`'ü `model`, `[4]`'ü
  `extra`; `XaiClient(..., extra=...)`; `_ONLY_DEEPSEEK` iki satırda aynı nesne;
  `OPENROUTER_API_KEY` config'te, defterin okumasında, `assert`'te, `print`'te ve Serve'de aynı
  yazılış.
