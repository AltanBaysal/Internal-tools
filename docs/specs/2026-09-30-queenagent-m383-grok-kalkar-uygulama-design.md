# Madde 383 — Grok ve xAI anahtarı kalkar · uygulama turu

**Kaynak:** [yol haritasının 383'ü](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md);
[test turu](2026-09-30-queenagent-m383-grok-kalkar-testler-design.md) (`efbe762f`), kararları
oradadır: yeni adlar, sohbet kimliğinin kalkması, OpenAI uyumlu biçimlerin kalması, tek satırlık
tablo.

**Kullanıcıdan gereken:** hiçbir şey.

## Ne değişir

**Taşıyıcı.** `backend/services/xai/client.py` → `backend/services/model/client.py` (`git mv`, klasör
de taşınır). `XaiClient` → `ModelClient`, `XaiFailed` → `ModelFailed`, `XaiNotConfigured` →
`ModelNotConfigured`. `_IS_XAI` sabiti, `stream`'in ve `_request`'in `conversation_id`'si ve başlığı
koyan satırlar kalkar. Modül belge dizesi ve yorumlar protokolü anar: tek parça gelen çağrı ve iç
içe önbellek sayısı *"OpenAI uyumlu biçim"*dir, DeepSeek'in düz alanı onun yanında okunur.

**Motor.** `data/xai_engine.py` → `data/model_engine.py` (`git mv`). `XaiEngine` → `ModelEngine`,
`ROLE_FOR_XAI` → `ROLE_FOR_MODEL`, `_for_xai` → `_for_model`; `stream`'in `conversation_id`'si
kalkar.

**Port ve kullanım.** `domain/ports.py`'deki `Engine.stream`'in `conversation_id`'si ve onu anlatan
paragraf kalkar. `usecases/stream_answer.py`'deki `conversation_id=chat_id` ve yorumu kalkar.

**Bileşim kökü.** `main.py` yeni adları import eder ve kurar; başka bir şeyi değişmez.

**Yapılandırma.** `config.py`: `XAI_API_KEY` ve `grok-4.3` satırı kalkar. Anahtarın yorumu
(*"One road for the key..."*) `DEEPSEEK_API_KEY`'in üstüne geçer; *"ikinci sağlayıcının anahtarı,
notebook ikisini de ister"* yorumu kalkar. Tablonun tarihçe yorumuna 383 bir cümleyle eklenir.

**Notebook.** CONFIG hücresinden `XAI_API_KEY`'in `try` bloğu, `assert`'i ve *"Both keys..."*
paragrafı kalkar; *"All three"* → *"Both"*; son `print` yalnız `GITHUB_TOKEN` ve
`DEEPSEEK_API_KEY`'i anar. Serve hücresinin ortamından `XAI_API_KEY` satırı kalkar, yorum tek anahtarı
anlatır. Kod hücrelerine yeni yorum eklenmez; var olan yorumlardan yalnız xAI'yi ya da iki anahtarı
anlatanlar kısaltılır.

**Belgeler.**
- `README.md`: `export DEEPSEEK_API_KEY=...`.
- `FOUNDATION.md`: 1. kararda anahtar `DEEPSEEK_API_KEY`; 6. kararın Madde 146 paragrafına, ilk
  sağlayıcının 383'te anahtarı ve başlığıyla kalktığı ve katmanın durduğu bir cümle olarak eklenir.
- `CODE-STANDARD.md`: servis listesinde `model/` — OpenAI uyumlu sohbet taşıyıcısı; `settings`
  paragrafında *"the xAI key"* → *"the API key"*.
- `BACKLOG.md`: xAI'yi anmıyor, dokunulmaz.

**Diskte kalan artık.** `git mv` izlenmeyen `__pycache__`'i taşımaz; `services/xai/` klasörü
yalnız onunla kalırsa bu çalışma ağacında silinir (izlenmiyor, commit'e girmez).

## Davranış

DeepSeek anahtarı yokken bugünkü gibi: uygulama açılır, yalnız bir cevap istemek
`ModelNotConfigured("No API key is set.")` ile düşer; notebook ise `DEEPSEEK_API_KEY` yokken
CONFIG'de durur. xAI anahtarı artık ne okunur ne sorulur. Ön yüz değişmez, `dist` derlenmez.

## Nasıl görülür

CLAUDE.md'deki dört satır yeşil. Adım adım dökümü
[uygulama planında](../plans/2026-09-30-queenagent-m383-grok-kalkar-uygulama-plan.md).
