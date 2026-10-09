# Mira Faz 8 (Ajan döngüsü) — Uygulama Planı

**Hedef:** Ajan döngüsü ve üç araç (Madde 17-19).

**Mimari:** Döngü `stream_answer`'ın içindedir; motora her turda araçlarla gidilir, çağrılar sunucuda
çalışır, sonuçları yalnız motora giden listeye eklenir. Diske tek bir `ai` mesajı düşer.

**Kaynak spec:** [Faz 8](../specs/2026-08-09-mira-faz-8-ajan-design.md)

## Global Kısıtlar

- Araçları **sunucu** çalıştırır; hangi projede olduğumuz çağrının değil, isteğin bilgisidir.
- Modelden gelen dosya adı olduğu gibi kullanılmaz.
- Olmayan dosya ve bilinmeyen araç **hata değil**, modele verilen bir cevaptır.
- Ara mesajlar sohbette saklanmaz.
- Commit: `git add <yollar>` → `git commit -m <mesaj> -- <aynı yollar>`.

---

### Task 1: Servisin araç çağrılarını yüzeye çıkarması

**Dosyalar:** Değiştir `services/xai/client.py`, `data/xai_engine.py`, `domain/usecases/stream_answer.py`,
`domain/ports.py` · Test `test_xai_client.py`, `test_stream_answer.py` (güncelleme)

`stream` artık tek anahtarlı sözlükler üretir: `{"text": "…"}` ve `{"tool_calls": [...]}`.
`_delta` de buna göre döner. Mevcut testler yeni biçime çevrilir; `stream_answer` da öyle.

- [ ] **Adım 1-4:** test → FAIL → yaz → PASS

---

### Task 2: Dosya deposu ve araçlar

**Dosyalar:** Oluştur `domain/tools.py`, `data/file_file_store.py` · Değiştir `domain/ports.py` ·
Test `backend/tests/test_tools.py`

`domain/tools.py`:

```python
"""The three tools Mira can reach for, and the rules around them."""
import json
import re

MAX_ROUNDS = 8
DEFAULT_NAME = "note.md"

TOOL_SPECS = [ ... ]  # OpenAI-shaped definitions


def safe_name(raw):
    """A name from the model never reaches the disk as it is."""
    name = str(raw or "").replace("\\", "/").split("/")[-1].strip()
    name = re.sub(r"[^A-Za-z0-9._-]+", "-", name).lstrip(".")
    if not name:
        return DEFAULT_NAME
    return name if "." in name else f"{name}.md"


def unique_name(existing, name):
    """Nothing is ever overwritten: plan.md becomes plan-2.md."""
    if name not in existing:
        return name
    stem, _, extension = name.rpartition(".")
    number = 2
    while f"{stem}-{number}.{extension}" in existing:
        number += 1
    return f"{stem}-{number}.{extension}"


def run_tool(file_store, project_id, name, arguments):
    """Runs one call and answers the model in words -- a miss is an answer, not a crash."""
```

- [ ] **Adım 1-4:** test → FAIL → yaz → PASS

---

### Task 3: Döngü

**Dosyalar:** Değiştir `domain/usecases/stream_answer.py`, `domain/prompt.py`,
`presentation/routes.py`, `main.py` · Test `test_stream_answer.py` (genişletme),
`test_chats_api.py` (ekleme)

`stream_answer(chat_store, file_store, engine, project_id, chat_id, now)` döngüyü kurar; rota ve
`main.py` yeni parametreyi taşır.

- [ ] **Adım 1-4:** test → FAIL → yaz → PASS

---

## Öz-denetim

**Spec kapsaması.** On bir cümle: 1-6 Task 3'ün döngü testleri · 7-8 Task 2'nin araç testleri ·
9-10 Task 2'nin ad testleri · 11 Task 1.

**Ad tutarlılığı.** `stream` sözlük üretiyor; `XaiEngine`, port ve `stream_answer` aynı iki anahtarı
biliyor. `FileStore.write(project_id, name, content) -> str` gerçek adı döndürüyor ve `run_tool` onu
modele söylüyor.

**Risk.** Döngü içindeki `engine.stream` her turda yeni bir üreteç açıyor; turlar arası mesaj listesi
**yerel** tutulmalı, sohbete yazılmamalı — yoksa ara mesajlar diske sızar.
