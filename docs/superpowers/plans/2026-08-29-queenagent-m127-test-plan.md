# Madde 127 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-29-queenagent-m127-dosya-adlari-testler-design.md](../specs/2026-08-29-queenagent-m127-dosya-adlari-testler-design.md)
**Bu tur yalnız test dosyalarına dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `test_stream_answer.py`: dört yeni test; mevcut `list_files` örnekleri kardeşine çevrilir.

## B. `test_tools.py`: yeni yokluk testi; davranış testleri silinir, yardımcı kullanımlar `list_names`'e çevrilir.

## C. `test_modes.py` ve araç sayımı: `list_files` listeden çıkar.

## D. `test_prompt.py` ve `test_skills.py`: metin pinleri.

## E. İki komut koşulur; beklenen: yalnız bu maddenin kırmızıları + bilinen defter çifti.

## F. Kırmızı commit.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; kod ellenmez; kayıt testleri ve ön yüz testleri
`list_files` adını taşımaya devam eder.
