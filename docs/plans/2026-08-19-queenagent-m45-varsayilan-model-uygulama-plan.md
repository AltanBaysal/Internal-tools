# Madde 45 — Varsayılan model `grok-4.3` · Uygulama Turu Planı

**Test turu:** [2026-08-19-queenagent-m45-varsayilan-model-testler-design.md](../specs/2026-08-19-queenagent-m45-varsayilan-model-testler-design.md)
**Kırmızı commit:** `caca83f`
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

Ayrı bir tasarım belgesi yok: değişen tek şey bir dize, ve neden değiştiği test turunun belgesinde
yazıyor. Bir sayfa daha yazmak, aynı cümleyi ikinci kez eskitmek olurdu.

---

## Adım 1 — `config.py`

`XAI_MODEL` varsayılanı `grok-4.5` → `grok-4.3`. Yanındaki yorum sebebi taşır: ucuz ve uzun bağlam,
ve bu ürünün turları uzun. Doğrulama tarihi güncellenir.

## Adım 2 — Yeşili gör, commitle

---

## Kapanış denetimi

- Kendi modelini seçmiş sohbetler etkilenmiyor: `chat.model` boşsa varsayılan kullanılıyor, dolu ise
  değil. Bugünkü davranış, testi var.
