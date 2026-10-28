# Madde 383 — Grok ve xAI anahtarı kalkar · test turu planı

> **Ajanlar için:** bu plan satır içinde, tek oturumda uygulanır (CLAUDE.md: istenmedikçe alt ajan
> yok). Adımlar `- [ ]` ile işaretlenir.

**Amaç:** Grok'un ve xAI anahtarının QueenAgent'tan kalktığını söyleyen testleri yazmak — yalnız
testleri — ve süiti kırmızı commit'lemek.

**Mimari:** Yeni bir süpürme testi, `config`, notebook ve port testlerinin yeni iddiaları; taşıyıcı ve
motor testleri `git mv` ile yeni adlarına taşınır; sahte motorlar port'un yeni imzasını taşır.

**Teknoloji:** pytest, vitest.

**Spec:** [2026-09-30-queenagent-m383-grok-kalkar-testler-design.md](../specs/2026-09-30-queenagent-m383-grok-kalkar-testler-design.md)

## Genel kısıtlar

- Yeni adlar: `backend.services.model.client` → `ModelClient`, `ModelFailed`, `ModelNotConfigured`;
  `backend.features.workspace.data.model_engine` → `ModelEngine`.
- Port'un `stream` imzası: `(self, messages, tools=None, on_open=None)` — `conversation_id` yok.
- Tablo: `config.MODELS == {"deepseek-flash": {...}}`.
- Notebook'un Secrets'tan okuduğu adlar: `{"GITHUB_TOKEN", "DEEPSEEK_API_KEY"}`.
- Test adları, yorumlar İngilizce; iddia mesajları Türkçe (dosyaların bugünkü düzeni).
- Hiçbir test susturulmaz; testler yalnız dört satırla koşar.

---

### Görev 1: Süpürme testi

**Dosyalar:** Oluştur: `queen-agent/backend/tests/test_retired_provider.py`

- [ ] **Adım 1: Testi yaz**

```python
"""Madde 383: Grok and its key are gone from QueenAgent, and this is what keeps them gone.

The proof of a deletion is an absence, and only a test that looks for it sees one (test_skills.py's
DELETED list keeps the same watch). This file is the one place the words are written, because it
cannot look for them without naming them.
"""
import os
import re

_QUEEN_AGENT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_THIS = os.path.abspath(__file__)
RETIRED = re.compile(r"grok|xai|x\.ai", re.IGNORECASE)
# Built, fetched or left behind rather than written by anyone.
_SKIPPED_DIRS = {"dist", "node_modules", "__pycache__"}
# An integrity hash, where the letters meet by chance.
_SKIPPED_FILES = {"package-lock.json"}


def _written():
    for folder, dirs, files in os.walk(_QUEEN_AGENT):
        dirs[:] = [d for d in dirs if d not in _SKIPPED_DIRS and not d.startswith(".")]
        for name in files:
            path = os.path.join(folder, name)
            if name not in _SKIPPED_FILES and os.path.abspath(path) != _THIS:
                yield path


def test_the_sweep_reads_the_tool():
    # Asked so the two below cannot pass by walking nothing.
    assert any(path.endswith("config.py") for path in _written())


def test_no_path_names_the_retired_provider():
    named = [os.path.relpath(p, _QUEEN_AGENT) for p in _written() if RETIRED.search(os.path.relpath(p, _QUEEN_AGENT))]
    assert named == [], f"Adında hâlâ geçiyor: {named}"


def test_no_file_mentions_the_retired_provider():
    found = []
    for path in _written():
        with open(path, encoding="utf-8", errors="replace") as handle:
            for number, line in enumerate(handle, 1):
                if RETIRED.search(line):
                    found.append(f"{os.path.relpath(path, _QUEEN_AGENT)}:{number}")
    assert found == [], f"Hâlâ geçiyor: {found}"
```

### Görev 2: Tablo

**Dosyalar:** Değiştir: `queen-agent/backend/tests/test_config.py`

- [ ] `test_the_api_key_comes_from_the_environment` (XAI) silinir; DeepSeek'inki zaten var.
- [ ] `test_without_it_the_key_is_empty_rather_than_missing` `DEEPSEEK_API_KEY` üzerine taşınır.
- [ ] `test_the_grok_row_is_kept_as_the_way_back` ve `test_the_writer_grok_4_3_replaced_is_gone_from_the_table` silinir.
- [ ] `test_deepseek_is_wired_under_the_one_name_it_has_today`: `set(config.MODELS) == {"deepseek-flash"}`.
- [ ] Adres ve anahtar testleri yalnız `deepseek-flash` satırını sorar.
- [ ] Yeni:

```python
@pytest.mark.parametrize("model", list(config.MODELS))
def test_every_row_resolves_at_startup(model):
    # main.py walks the table at startup, and engine_for looks each row's key up by name among
    # config's own constants. A row naming a key config no longer holds stops the app there.
    assert config.engine_for(model)[0] == model
```

### Görev 3: Notebook

**Dosyalar:** Değiştir: `queen-agent/backend/tests/test_notebook.py`

- [ ] xAI'nin üç testi (`test_the_xai_key_comes_from_secrets`, `test_a_missing_xai_key_says_what_to_do`,
  `test_the_xai_key_travels_to_the_app_in_the_environment`) silinir; yerine:

```python
def test_the_notebook_asks_for_the_token_and_one_key():
    """Madde 383: every turn and every action line goes to DeepSeek, so its key is the one the app
    spends. A secret asked for and never spent is one more thing a user has to go and get."""
    asked = set(re.findall(r'userdata\.get\("(\w+)"\)', _source()))
    assert asked == {"GITHUB_TOKEN", "DEEPSEEK_API_KEY"}, f"Defter başka bir şey de soruyor: {asked}"
```

- [ ] `import re` eklenir.
- [ ] `test_a_missing_deepseek_key_says_what_to_do`'nun belge dizesi iki anahtarı anmaz.
- [ ] `test_no_api_key_is_ever_printed` yalnız `DEEPSEEK_API_KEY` için döner; belge dizesindeki
  eski ad ve "both keys" cümlesi yeniden yazılır.

### Görev 4: Port

**Dosyalar:** Değiştir: `queen-agent/backend/tests/test_ports.py`

- [ ] Importlar `ModelEngine`, `ModelClient`; parametre listeleri yeni adlarla.
- [ ] Yeni:

```python
@pytest.mark.parametrize("layer", [Engine, ModelEngine, ModelClient])
def test_a_turn_names_no_conversation(layer):
    # Madde 383. The id only ever reached one provider's header, and that provider is gone.
    assert "conversation_id" not in inspect.signature(layer.stream).parameters
```

### Görev 5: Taşıyıcı ve motor testleri

**Dosyalar:** `git mv` `test_xai_client.py` → `test_model_client.py`, `test_xai_engine.py` →
`test_model_engine.py`.

- [ ] Taşıyıcı: import `ModelClient, ModelFailed, ModelNotConfigured`; `_client` ve öteki kurulumlar
  `"deepseek-flash", "https://api.deepseek.com"`; beklenen URL `https://api.deepseek.com/chat/completions`;
  sohbet başlığı bölümü (üç test) silinir; tek parça çağrı ve iç içe önbellek örneklerinin yorumları
  protokolü anar.
- [ ] Motor: import `ModelEngine`; `DEFAULT = "deepseek-flash"`; sahte istemcide `conversation_id`
  yok; `test_the_conversation_id_travels_down_to_the_client` silinir; prompt yazanı soran test
  `{"deepseek-flash": agent, "writer": writer}`; `test_every_turn_is_spoken_by_the_default`'un
  değişkenleri `turns, other`; rol yorumu "the model is told OpenAI's".

### Görev 6: Sahte motorlar ve adsız örnekler

- [ ] `test_stream_answer.py`: sahte `stream` imzası `(self, messages, tools=None, on_open=None)`,
  `conversation_ids` listesi ve `test_the_engine_is_told_which_chat_is_asking` silinir.
- [ ] `test_chats_api.py` (iki sahte), `test_files_api.py`, `test_last_activity.py`,
  `test_pin_archive.py`, `test_projects_api.py`: aynı imza.
- [ ] `grok-4.3` → `deepseek-v4-pro`: `test_chats_api.py:586`, `test_file_chat_store.py:90,118`,
  `ChatScreen.test.jsx:918,920`.
- [ ] `Composer.test.jsx:120` → `Flash`; `Menu.test.jsx:82,88` → `Pro` / `Flash`;
  `sse.test.js:66,69` → `the model answered 401: bad key`.
- [ ] `test_permissions.py:44`, `test_stops.py:40`: yorum modelin bağlantısını anar.

### Görev 7: Koş ve commit'le

- [ ] Dört satır, paralel, yazıldığı gibi. Beklenen: queen-agent arka ucu kırmızı (süpürme, tablo,
  notebook, port/taşıyıcı/motor importu, sahte motoru değişen dosyaların tur çalıştıran testleri);
  öteki üçü yeşil.
- [ ] Commit: `test(queen-agent): Madde 383 red -- Grok and the xAI key go`, spec ve plan ile.
