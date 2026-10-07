# Madde 39 — Shot düşer, frame gelir · Uygulama Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m39-kare-uygulama-design.md](../specs/2026-08-19-queenagent-m39-kare-uygulama-design.md)
**Kırmızı commit:** `486906a`
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Adım 1 — `build_prompts.py`

- Liste: `structure.get("frames") or structure.get("shots") or []`, yanında geçiş olduğunu söyleyen
  bir yorum.
- `BadStructure` cümleleri: "…characters, locations and frames." · "That file has no frames to
  build from."
- `_looked_up`'ın satırı: `frame {number}: …`.
- Docstring ve yorumlardaki "shot" → "frame" (`forty shots` → `forty frames` dahil).

## Adım 2 — `skills.py`

- Modül docstring'i, `CREATE_SCENARIO`, `CREATE_CHARACTER_PROMPT`, `GENERATE_PROMPTS`,
  `GENERATE_PROMPTS_PLUS`, `RULEBOOK` — birim adı olarak geçen her "shot" → "frame".
- `SPLIT_INTO_SHOTS` → `SPLIT_INTO_FRAMES`, `VERIFY_SHOTS` → `VERIFY_PROMPTS`; ikincisinin açılış
  cümlesi promptlar üzerinden konuşur.
- Şema örneğinde `"shots"` → `"frames"`, dosya adı `intro-shots.json` → `intro-frames.json`.
- **`"camera": "medium shot, from slightly above"` olduğu gibi kalır.**
- `INSTRUCTIONS` anahtarları: `split-into-frames`, `verify-prompts`.

## Adım 3 — `tools.py`

- `build_prompts` tarifi: "assembles every shot" → "every frame".
- `MAX_ROUNDS` yorumundaki "add the shots in batches" → "frames".

## Adım 4 — `skills.js`

- `split-into-shots` → `split-into-frames`, adı "Split into frames", açıklaması "Turn the scenario
  into frames. Stays in the chat."
- `verify-shots` → `verify-prompts`, adı "Verify prompts", açıklaması "Check the structure files
  against the rules."

## Adım 5 — Yeşili gör

İki komut da koşulur; ikisi de tamamen yeşil olmalı.

## Adım 6 — Yeşil commit

---

## Kapanış denetimi

- Kaynak dosyalarda birim adı olarak "shot" kalmadı; kalan tek geçiş `"medium shot"`.
- Eski `"shots"` okuması hâlâ çalışıyor (testi var).
