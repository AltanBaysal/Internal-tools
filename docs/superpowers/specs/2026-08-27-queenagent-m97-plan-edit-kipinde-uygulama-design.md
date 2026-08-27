# Madde 97 — Plan yazmak edit kipinin de işi olur · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 6, Madde 97 ·
**Turun birincisi:** [test turu](2026-08-27-queenagent-m97-plan-edit-kipinde-testler-design.md) —
bir kırmızı commit'lendi *(`bd26faa`)*.
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder.

---

## Değişen tek şey

`modes.py`'de edit kipinin araç listesi `write_plan`'ı da alıyor. Tek satır.

Yanındaki yorum bugün *"and not write_plan: in this mode a plan is an ordinary file"* diyor — cümle
artık yanlış değil ama eksik: plan bu kipte hâlâ sıradan bir dosya, ve **tam da bu yüzden** araç
buraya girebiliyor. Yorum bunu söyleyecek hâle geliyor.

## Turu bitirme kuralı ellenmiyor

`ends_the_turn` olduğu gibi kalıyor: çift hâlâ plan kipi ile `write_plan`. Edit kipinde plan yazan
bir tur devam ediyor, ve akış aynı turda bir sonraki sorusunu soruyor.

## Dokunulmayan

| Ne | Neden |
|---|---|
| Plan kipinin listesi | 91'in kararı; orada `create_file` yok ve olmayacak |
| `tools.py` | Araç zaten tanımlı, `WRITES_FILES`'ta ve adı `-plan.md`'ye zorlanıyor |
| Ön yüz | Kip seçici üç kipi göstermeye devam ediyor; `dist` derlenmiyor |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
```

Bir kırmızı yeşile döner. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.
