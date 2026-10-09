# Madde 390 — v9'da yazılan prompt'lar öncekilerle aynı biçimde: uygulama

**Testler:** [2026-09-30-queenagent-m390-prompt-bicimi-testler-design.md](2026-09-30-queenagent-m390-prompt-bicimi-testler-design.md) —
kurallar, her v9 parçasının denetimi ve açık noktalar orada.

## Ne değişir

Yalnız `queen-agent/backend/features/workspace/domain/prompt.py`'deki `THE_CHECKS`'in ikinci
maddesinde kullanıcının sözü, v9 öncesindeki `"You decide"` gibi çift tırnağa alınır:

- Önce: `when the user says continue, carry on from there.`
- Sonra: `when the user says "continue", carry on from there.`

Söz aynı söz; kullanıcı Türkçe yazsa da ("devam") model onu v9 öncesinin `"you decide"`'ını okuduğu
gibi okur — tırnak kullanıcının dediği şeyi işaretler, hangi dilde dendiğini değil. Kelime sayısı
değişmez (tırnak kelimeye yapışık): Start a scenario 1025, Edit prompts ve Improve kendi
tavanlarının altında aynı sayıda kalır. `test_a_long_scenario_carries_the_checks_over_turns_through_the_plan`
`continue`'yu aramaya devam eder ve geçer.

Başka hiçbir metin değişmez; açık noktalar kullanıcının okumasına kalır.
