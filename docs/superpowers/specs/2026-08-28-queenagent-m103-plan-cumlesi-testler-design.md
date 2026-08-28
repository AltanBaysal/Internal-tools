# Madde 103 — write_plan turun sonunu kipe değil işe bağlar · **test turu**

**Tarih:** 2026-08-28 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 6, Madde 103.
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder. Kod yazılmıyor, kırmızı
commit'leniyor.

---

## Neyin testi

Tek test, `test_tools.py`'de. `write_plan`'ın modele giden açıklamasının iki söz öbeğini tutuyor:

- **"asked only to plan"** — turun bitişi artık koşulsuz değil, işe bağlı.
- **"carry on"** — büyük bir işin ilk adımı olan plandan sonra tur sürüyor.

İkisi de bugünkü metinde yok; bugünkü metin *"The turn ends here"* diyor, koşulsuz. Test bu yüzden
kırmızı doğuyor.

## Neden metin testi

Modele giden cümle üründür — skill metinlerinin `test_skills.py`'deki testleri gibi, ve
`build_prompts`'ın açıklamasındaki *frame/shot* ayrımını tutan testin ta kendisi gibi
*(`test_tools.py`, aynı dosya)*. Sözcük tutulur, çünkü davranışın kendisi modelin elinde; kodun
tutabildiği tek şey modele ne söylendiği.

## Neden bu iki öbek

Sunucunun kuralı doğru ve test edilmiş durumda: `ends_the_turn` yalnız plan kipi + `write_plan`
çiftinde `True`, ve `test_modes.py` bunu iki satırla tutuyor. Yanlış olan modele söylenen — ve model
kipi hiç görmediği için düzeltme *"plan kipinde biter"* diyemez; modelin görebildiği tek şey ne
istendiği. Bağlanacak yer orası: yalnız plan istenen tur, ve büyük işin ilk adımı.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Arka yüzde **bir kırmızı** — yeni test. Ön yüz dokunulmuyor, yeşil kalıyor. **İki kırmızı bu
maddenin değildir:** `test_notebook`'un ikisi.
