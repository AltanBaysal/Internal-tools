# Madde 45 — Varsayılan model `grok-4.3` · Test Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m45-varsayilan-model-testler-design.md](../specs/2026-08-19-queenagent-m45-varsayilan-model-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adım 1 — yeni `test_config.py`

`test_the_default_model_is_the_cheap_one_with_the_long_context` — `config.XAI_MODEL` `grok-4.3`;
yorum sebebini taşır.

`XAI_MODEL` ortam değişkeni sabiti geçersiz kılabiliyor, ve çözülmüş değer içeri gömülüyor — test
onu ayıramaz. Ortamında bu değişkeni tanımlamış biri için test düşer, ve düştüğünde **doğru** bir
şey söyler: bu makinedeki varsayılan, deponun gönderdiği değil. Yorum bunu yazar.

## Adım 2 — `models.test.js`

`the default the server starts from is a row in this menu` — `grok-4.3` listede.

## Adım 3 — Kırmızıyı gör, commitle

---

## Kapanış denetimi

- `git status` yalnız iki test dosyasını gösteriyor.
