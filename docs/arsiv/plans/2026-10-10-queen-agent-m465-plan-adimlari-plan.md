# Madde 465 — Planın adımları sırayla, plan

> **Koşum:** ana klasörde, `feat/queenagent-v10` dalında, **commit'lenmeden** ve hiçbir şey stage
> edilmeden — modele giden metni ana agent okur ve commit'ler. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** `SYSTEM_PROMPT`'un Planning bölümü bir planın adımlarını tek tek, her birini kendi döngüsüyle
(bağlamı topla, eylemi yap, sonucu doğrula) yürütmeyi söyler.

**Yaklaşım:** önce test, kırmızı görülür, sonra metin. Dosyalar Edit ile değişir.

**Spec:** [m465](../specs/2026-10-10-queen-agent-m465-plan-adimlari-design.md)

## Görev 1: Test — `queen-agent/backend/tests/test_prompt.py`

- [ ] `test_the_base_says_the_plan_and_carries_on`'un yanına
  `test_a_plans_steps_go_one_at_a_time_each_verified`: Planning bölümünün bir satırı `one at a time`
  ile `verify`'ı, bir satırı `next step` ile `complete`'i birlikte söyler.
- [ ] `python -m pytest queen-agent/backend/tests/test_prompt.py -q -k one_at_a_time` — kırmızı.

## Görev 2: Metin — `queen-agent/backend/features/workspace/domain/prompt.py`

- [ ] `SYSTEM_PROMPT`'ta *"Do not stop to ask for a yes to your plan"* satırının hemen altına
  yol haritasındaki satır, sözü sözüne; dizgi dosyanın üslubuyla bölünür. Başka satır değişmez.
- [ ] Aynı test — yeşil.

## Görev 3: Dört suite, sırayla

- [ ] `python -m pytest queen-agent -q`
- [ ] `npm test --prefix queen-agent/frontend`
- [ ] `python -m pytest queen-editor -q`
- [ ] `npm test --prefix queen-editor/frontend`
