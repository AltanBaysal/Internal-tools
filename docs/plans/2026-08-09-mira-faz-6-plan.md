# Mira Faz 6 (Grok) — Uygulama Planı

**Hedef:** `xai/` servisi (Madde 13) ve mesaja gerçek cevap (Madde 14).

**Mimari:** Servis ürün kavramı bilmez — mesaj listesi alır, asistan mesajı döndürür. Sistem yönergesi
domain'de, taşımada değil. Kullanıcı mesajı motora gitmeden önce diske yazılır; motor patlarsa orada
kalır.

**Kaynak spec:** [Faz 6](../specs/2026-08-09-mira-faz-6-grok-design.md)

## Global Kısıtlar

- Hata metni **servisin gerçek çıktısını** taşır (durum kodu + gövde); uydurulmuş sebep yok.
- `urllib.request` kullanılır; yeni bağımlılık yok.
- Testlerde ağ yok: `XaiClient`'ın açıcısı sahtelenir, `Engine` use case testlerinde tamamen sahte.
- Commit: `git add <yollar>` → `git commit -m <mesaj> -- <aynı yollar>`.

---

### Task 1: `xai/` servisi

**Dosyalar:** Oluştur `backend/services/xai/__init__.py`, `backend/services/xai/client.py` ·
Değiştir `backend/config.py` · Test `backend/tests/test_xai_client.py`

**Arayüzler:** `XaiClient(api_key, model, base_url, opener=None)` · `complete(messages, tools=None)` ·
`XaiNotConfigured` · `XaiFailed`

`opener` enjekte edilebilir: varsayılanı `urllib.request.urlopen`, testte sahte. Ağa çıkan tek satır
budur ve testin değiştirebileceği tek yerdir.

- [ ] **Adım 1: Test yaz** — anahtar yoksa `XaiNotConfigured` · 401'de `XaiFailed` ve mesajda gövde ·
  başarılı çağrı `choices[0].message` döndürüyor · gövdede `model` ve `messages` var, `tools`
  verilmediyse anahtar hiç yok · `Authorization` başlığı `Bearer` taşıyor.
- [ ] **Adım 2:** `python -m pytest d:\code\github\internal-tools\mira -q` → FAIL
- [ ] **Adım 3: Yaz**

```python
"""XaiClient -- HTTP transport for xAI's OpenAI-compatible chat completions.

Knows no prompt, no chat and no file: it takes a message list and returns the assistant's message.
"""
import json
import urllib.error
import urllib.request


class XaiNotConfigured(Exception):
    """No API key. The app still starts; only asking for an answer fails."""


class XaiFailed(Exception):
    """The service answered with an error. Carries its own words, never a guessed cause."""


class XaiClient:
    def __init__(self, api_key, model, base_url, opener=urllib.request.urlopen):
        self._api_key = api_key
        self._model = model
        self._base_url = base_url.rstrip("/")
        self._opener = opener

    def complete(self, messages, tools=None):
        if not self._api_key:
            raise XaiNotConfigured("XAI_API_KEY is not set")
        body = {"model": self._model, "messages": messages}
        if tools:
            body["tools"] = tools
        request = urllib.request.Request(
            f"{self._base_url}/chat/completions",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with self._opener(request) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as failure:
            # The service's own words: a 401 is not necessarily an expired key, and a wrong model
            # name answers 404. Guessing a cause here would print a lie.
            raise XaiFailed(f"{failure.code} {failure.read().decode('utf-8', 'replace')}") from failure
        except urllib.error.URLError as failure:
            raise XaiFailed(str(failure.reason)) from failure
        return payload["choices"][0]["message"]
```

`config.py`: `XAI_MODEL = os.environ.get("XAI_MODEL", "grok-4.5")` ve
`XAI_BASE_URL = os.environ.get("XAI_BASE_URL", "https://api.x.ai/v1")`.

- [ ] **Adım 4:** koş → PASS

---

### Task 2: Cevabın üretilmesi

**Dosyalar:** Oluştur `domain/prompt.py`, `domain/usecases/answer_in_chat.py`,
`data/xai_engine.py` · Değiştir `domain/ports.py`, `domain/errors.py`, `presentation/routes.py`,
`main.py` · Test `backend/tests/test_answer_in_chat.py`, `test_chats_api.py` (ekleme)

**Arayüzler:** `Engine.complete(messages) -> dict` · `answer_in_chat(chat_store, engine, project_id,
chat_id, text, now) -> Chat` · `EngineFailed`

- [ ] **Adım 1: Test yaz** — sahte motorla: kullanıcı ve cevap sırayla ekleniyor · motor patlarsa
  kullanıcı mesajı duruyor ve `EngineFailed` çıkıyor · motora giden listenin başında sistem yönergesi
  var ve sohbette saklanmıyor · rota 502 döndürüyor ve gövdesinde motorun satırı var.
- [ ] **Adım 2:** koş → FAIL
- [ ] **Adım 3: Yaz**

```python
"""What Mira is told about itself before every answer."""

SYSTEM_PROMPT = (
    "You are Mira, a small AI workspace. "
    "Answer the user directly and concisely, in English."
)
```

```python
"""Answer a message: the user's words reach disk first, then the engine is asked."""
from backend.features.workspace.domain.errors import EngineFailed
from backend.features.workspace.domain.usecases.append_message import append_message


def answer_in_chat(chat_store, engine, project_id, chat_id, text, now):
    # Written before the engine is called: a dropped connection must not swallow what was typed.
    chat = append_message(chat_store, project_id, chat_id, text, now)
    try:
        answer = engine.complete(
            [{"role": message.role, "content": message.text} for message in chat.messages]
        )
    except Exception as failure:
        raise EngineFailed(str(failure)) from failure
    return append_message(chat_store, project_id, chat_id, answer["content"], now, role="ai")
```

`xai_engine.py` sistem yönergesini başa ekler ve `role="ai"`'yi xAI'nin beklediği `assistant`'a
çevirir — bu bir taşıma detayı, domain'in `ai` adı diskte kalır.

Rota: `EngineFailed` → 502 ve gövdesinde hatanın metni.

- [ ] **Adım 4:** koş → PASS

---

## Öz-denetim

**Spec kapsaması.** Sekiz cümle: 1-4 Task 1'in beş testi · 5-6 Task 2'nin use case testleri ·
7 rota testi · 8 `xai_engine` testi.

**Ad tutarlılığı.** `complete(messages, tools=None)` hem serviste hem portta aynı; Faz 8 `tools` ile
çağıracak. Diskteki rol adı `ai`, xAI'ye giderken `assistant` — çeviri yalnız `xai_engine.py`'de.

**Risk.** `answer_in_chat` `Exception` yakalıyor; bu geniş, ama amaç motorun **her** arızasını
kullanıcı mesajını koruyarak bildirmek. Daraltmak, tanımadığımız bir arızanın mesajı yutmasına izin
vermek olurdu.
