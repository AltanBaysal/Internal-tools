# Madde 460 — Modele giden isteğin süre sınırı, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** bir süre hiç ses gelmeyen model isteği kesilir; kesilen deneme kara kutunun bir başarısız
denemesidir; konuşan uzun cevap kesilmez.

**Yaklaşım:** önce testler, kırmızı görülür, sonra kod. Dosyalar Edit ve Write ile değişir.

**Spec:** [m460](../specs/2026-10-10-queen-agent-m460-model-sure-design.md)

## Her yere geçerli kurallar

- Kod, yorum ve test adları İngilizce.
- `black_box.py`, frontend ve queen-editor değişmez.

---

## Görev 1: testler — `backend/tests/test_model_client.py`

- [ ] `IDLE = 0.3`; `_client` ve anahtarın her istekte okunduğu test, sahte `opener`'ı
  `lambda request, timeout: opener(request)` ile sarar.
- [ ] `_service(*replies)`: her bağlantıya sıradaki cevap (bayt gönderilir, sayı beklenir), söylenmeyen
  her şey sessizlik. `_silent_server`'ın yerini alır: `_blocked_read` `_service([HEAD])` kullanır, ve
  istemcisi 30 saniyelik sınırla kurulur — Stop'un kesmesi zaman aşımlı bir sokette de uyandırmalı.
- [ ] `_ended(run)`: 5 saniyede bitmeyen koşu testi düşürür.
- [ ] Başlıktan önce ve sonra susan istek `ModelFailed`, düz soketin sözüyle `timed out` (yorum TLS'nin
  `The read operation timed out`'unu da anar); konuşan uzun cevap kesilmez. Kara kutunun sayması
  `test_black_box.py`'de zaten tutuluyor, burada test edilmez.
- [ ] Kırmızı görülür: önce kurucunun parametresi yok; parametre eklenip `urlopen`'a verilmeyince
  sessizlik testleri *"the request was never cut"* ile düşer, konuşan cevap testi geçer.

## Görev 2: `backend/services/model/client.py`

- [ ] `ModelClient(read_key, model, base_url, idle_seconds, opener=urlopen)`; `stream`
  `self._opener(request, timeout=self._idle_seconds)` açar.
- [ ] Yorumlar: sınırın neden sessizliği ölçtüğü, ve `OSError` kolunun `timed out`'u da taşıdığı.

## Görev 3: `backend/config.py` ve `main.py`

- [ ] `config.py`: `MODEL_IDLE_SECONDS = 180`, neden ve sınırlarıyla.
- [ ] `main.py`: her `ModelClient`'a `config.MODEL_IDLE_SECONDS`.

## Görev 4: suite'ler

- [ ] Dördü sırayla, biri bitince öteki: `python -m pytest queen-agent -q`,
  `npm test --prefix queen-agent/frontend`, `python -m pytest queen-editor -q`,
  `npm test --prefix queen-editor/frontend`.
