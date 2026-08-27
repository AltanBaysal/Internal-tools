# Madde 97 — Plan yazmak edit kipinin de işi olur · **test turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) — Blok 6, Madde 97 ·
**Kararı:** [karar defteri](../../2026-08-27-queenagent-skill-kararlari.md) K22 ·
**Şartı yok.**
**Tur:** ikiden birincisi — bu belge **yalnız testleri** tarif eder.

---

## Bugün ne oluyor

`write_plan` yalnız plan kipinde elde *(Madde 91)*. Sebebi oradaydı ve doğruydu: plan kipinde
`create_file` verilseydi model aynı turda hem planı hem teslimatı yazabilirdi.

Ama kısıt ters yönde de duruyor — **edit kipinde plan yazılamıyor.** Madde 101'in akış skill'i edit
kipinde çalışıyor, çünkü dosya yazıyor, ve nerede kaldığını bir plan dosyasında tutuyor. Bugünkü
listeyle akışın ilk adımı hiç atılamaz.

## Ne olur

`write_plan` edit kipinin listesine de giriyor. Kipin anlamı değişmiyor: edit zaten yazan kip, ve
plan onun için sıradan bir dosya.

## Turu bitirme kuralı değişmiyor

`ends_the_turn` bir **çift** soruyor: plan kipi *ve* `write_plan`. Edit kipinde plan yazmak turu
bitirmiyor, yani akış aynı turda soru sormaya devam edebiliyor *(K22)*.

Kural neden çift: *"plan yazıldı, sıra kullanıcıda"* demek yalnız plan kipinde doğru. Edit kipinde
aynı araç, üstüne yazılan sıradan bir dosya.

## Kırmızıya dönecek testler

**`test_modes.py` — bir**

1. Edit kipi `write_plan`'ı da veriyor.

**Yerinde kalan, ve bu maddenin asıl bekçisi:** `test_only_a_written_plan_ends_the_turn`. Bugün
`ends_the_turn("edit", "write_plan")`'in yanlış olduğunu zaten söylüyor, ve bu madde onu yeşil
bırakmak zorunda — araç geldi diye turun bitmesi, maddenin tam olarak kaçındığı şey.

**`test_stream_answer.py` — bir ad düzeltmesi**

2. `test_a_turn_that_names_no_mode_carries_all_five` artık beşi saymıyor: kip 96'da altıncıyı,
   burada yedinciyi aldı. Test adı sayı yerine iddiasını söylüyor — mod adı taşımayan turun yazma
   araçlarıyla geldiğini. İddia değişmiyor, kırmızıya da dönmüyor; düzelen şey yalan söyleyen bir ad.

## Dokunulmayan

| Ne | Neden |
|---|---|
| Plan kipinin listesi | 91'in kararı; `create_file` oraya girmiyor |
| `plan_name` | Adın `-plan.md` ile bitmesi aynen duruyor |
| `write_plan`'ın üstüne yazması | Akışın planı ilerledikçe güncelleniyor, ikinci bir dosya doğmuyor |
| Ön yüz | `dist` derlenmiyor |

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
```

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.
