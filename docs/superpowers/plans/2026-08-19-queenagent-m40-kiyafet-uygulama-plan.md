# Madde 40 — Yapıya kıyafet giriyor · Uygulama Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m40-kiyafet-uygulama-design.md](../specs/2026-08-19-queenagent-m40-kiyafet-uygulama-design.md)
**Kırmızı commit:** `f66c20f` — on düşen test
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adım 1 — `build_prompts.py`

- `outfits = structure.get("outfits") or {}`.
- Yeni yardımcı `_worn(field)` — karenin `characters` alanını `(ad, kıyafet listesi)` çiftlerine
  çevirir: harita, eski liste, ve listeye sarılmamış tek dize. Yorumu iki şeklin neden bir arada
  yaşadığını söyler.
- Döngü her karakter için önce kimliği, sonra kıyafetlerini ekler — blok bitişik kalır.
- Kıyafet de `_looked_up` ile aranır, alan adı `outfits`.

## Adım 2 — `skills.py`

- `GENERATE_PROMPTS_PLUS` şeması: `"outfits"` haritası; karede `"characters": { "aylin": ["gunluk"] }`.
- Ayrım cümlesi: kalıcı olan `characters`'ta, karelere göre değişen `outfits`'te; kıyafet giyene
  göre değil giysiye göre adlandırılır.
- `RULEBOOK`: kıyafet kuralı ikinci sıraya girer, sonrakiler kayar.
- `CREATE_CHARACTER_PROMPT`: "what they are wearing" düşer; kıyafetin `outfits` girdisi olduğu
  yazılır.

## Adım 3 — Örnek yapı belgesi

`docs/superpowers/research/2026-08-18-ornek-yapi.json` — `"shots"` → `"frames"`.

## Adım 4 — Yeşili gör, commitle

---

## Kapanış denetimi

- Kıyafetsiz eski dosya hâlâ üretiyor (testi var).
- Yönerge ile yapı aynı commit'te; arada çelişik bir hâl kalmadı.
