# Madde 388 — Edit prompts olmayan negatif dosyayı söylemez — uygulama

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 388 (Dalga 8).
**Testler:** [2026-09-30-queenagent-m388-negatif-dosya-testler-design.md](2026-09-30-queenagent-m388-negatif-dosya-testler-design.md),
kırmızı commit `17d41190`.

**Kullanıcıdan gereken:** yok.

## Ne yazılır

Yalnız `queen-agent/backend/features/workspace/domain/prompt.py`.

1. **`EDIT_PROMPTS`, `Step 4 -- the checks`, Check 4 maddesi.** `Otherwise skip it.`'in arkasına, aynı
   maddede bir cümle:

   - Önce: `- Check 4 runs only if your change touched the scenario's cast: a character added,
     changed or taken out. Otherwise skip it.`
   - Sonra: `- Check 4 runs only if your change touched the scenario's cast: a character added,
     changed or taken out. Otherwise skip it. If the scenario has no negative file, close by naming
     the prompt file alone.`

   Neden bu yer: dosyanın yokluğu yalnız Check 4 atlanınca doğar — Check 4 koşunca dosyayı yazar. Neden
   bu söz: kapanışın kendi fiili (`close by naming`) tekrar edilir ki model iki cümleyi aynı işin
   iki hâli diye okusun; `alone` kapanışın `and the negative file`'ını düşürür. Dosyanın var olup
   olmadığını model her turda gelen dosya listesinden görür (`FILES_HELD`), o yüzden nasıl bakılacağı
   yazılmaz.

2. **`THE_CHECKS`'in docstring'i**, son paragraf: kapanışın da koşulunun editörde olduğu, ve neden,
   bir cümleyle eklenir. Model okumaz; bugün doğru olanı söyler.

## Ne yazılmaz

- `THE_CHECKS`'in metni (kapanış dahil) değişmez: akış ve Improve Check 4'ü hep koşar, dosya orada hep
  var. 390'ın açık noktası 1'e dokunulmaz.
- Olmayan dosyayı yazdırmak için bir talimat yok: madde yalnız kapanışın ne söylediği hakkında.

## Kelime sayısı

Cümle 14 kelime: Edit prompts 856'dan 870'e, testin tavanı 870. Akış 1025'te, Improve değişmez.

## Doğrulama

Dört satır, olduğu gibi, paralel; `test_after_an_edit_the_closing_names_the_negative_file_only_if_there_is_one`
yeşil, suite'in geri kalanı yeşil kalır.
