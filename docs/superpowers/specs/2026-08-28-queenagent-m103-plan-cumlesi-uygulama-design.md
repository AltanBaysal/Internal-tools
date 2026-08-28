# Madde 103 — write_plan turun sonunu kipe değil işe bağlar · **uygulama turu**

**Tarih:** 2026-08-28 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 6, Madde 103 ·
**Turun birincisi:** [test turu](2026-08-28-queenagent-m103-plan-cumlesi-testler-design.md) — bir
kırmızı commit'lendi *(`30209f6`)*.
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder.

---

## Değişen tek şey

`tools.py`'de `write_plan`'ın açıklamasının son cümlesi. Bugün:

> The turn ends here: the user reads the plan, fixes it in the file if they want to, and runs it
> themselves.

Oluyor:

> A turn asked only to plan ends with this call -- the user reads the plan, fixes it in the file
> if they want to, and runs it themselves. A plan that is the first step of a larger job is an
> ordinary step: carry on from it.

İlk iki cümle — işi böl, planı kaydet, var olanın üstüne yaz, önce oku — olduğu gibi duruyor.

## Neden işe bağlanıyor, kipe değil

Model kipi hiç görmüyor: istek konuşma + yönerge taşıyor, kip sunucuda kalıyor. *"Plan kipinde tur
biter"* diye bir cümle modelin uygulayamayacağı bir koşul olurdu. Modelin görebildiği şey ne
istendiği — ve iki hâl oradan ayrılıyor: plan istendiyse tur bitiyor *(kullanıcı planı okuyacak)*,
plan büyük bir işin ilk adımıysa sürüyor *(akışın 1. adımı tam olarak bu)*.

## İki kipte ne olur

- **Plan kipi:** hiçbir şey değişmiyor. Turu kesen sunucu *(`ends_the_turn`)*, ve plan istenen
  turda model bitişi doğru bekliyor — söyleyeceğini çağrıdan önce ya da planın içine koymaya devam
  ediyor.
- **Edit kipi + akış:** model artık devam edeceğini biliyor. Skill metninin *"the plan is written
  before anything is asked"* dediği şeyle araç açıklaması aynı yöne bakıyor; ilk soru aynı turda.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `ends_the_turn` ve `modes.py` | Sunucunun kuralı doğruydu; yanlış olan modele söylenendi |
| Skill metinleri | Akış metni zaten doğruyu söylüyor |
| Ön yüz | Cümle modele gidiyor, ekrana değil; `dist` derlenmiyor |
| m91 planı ve 26 Ağustos haritasındaki kopyalar | Tarihli kayıt — kendi günlerini anlatıyorlar |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Bir kırmızı yeşile döner. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.
