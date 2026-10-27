# Madde 38 — Sessiz tur meşru · Uygulama Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m38-sessiz-tur-uygulama-design.md](../specs/2026-08-19-queenagent-m38-sessiz-tur-uygulama-design.md)
**Kırmızı commit:** `bd4cef1` — yedi düşen test
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adım 1 — `append_message.py`

Koşul `not trimmed` yerine `not trimmed and not files`. Yorum kuralı söyler: bir mesaj bir şey
taşımalı — söz ya da dosya; kullanıcının mesajı dosya taşımadığı için o taraf gevşemez.

Beklenen: `test_stream_answer.py`'daki üç test yeşile döner; `test_chats_api.py`'daki 6 ve 7 de.

## Adım 2 — `routes.py`

`_sse`'ye ikinci bir `except`: `EmptyMessage` → `error` çerçevesi, cümlesi
**"The model returned nothing."** `EmptyMessage` zaten bu dosyada import edilmiş durumda.

Beklenen: `test_chats_api.py`'daki 8 ve 9 yeşile döner.

## Adım 3 — Yeşili gör

İki komut da koşulur. Beklenen: pytest 316 geçer (309 + 7), vitest 442 geçer. Düşen tek test
kalmamalı.

## Adım 4 — Yeşil commit

Commit mesajı ne değiştiğini söyler, çift tırnak taşımaz.

---

## Kapanış denetimi

- `stream_answer.py` değişmedi.
- Ön yüzde hiçbir dosya değişmedi.
- Boş mesajın 400'leri yerinde: `post_message` ve `post_chat` testleri geçiyor.
