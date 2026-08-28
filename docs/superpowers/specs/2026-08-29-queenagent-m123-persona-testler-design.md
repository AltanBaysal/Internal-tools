# Madde 123 — Skill metinleri persona ile açılır ve kısalır · Tur 1 (testler) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 123.
**Dal:** `feat/queenagent-m123-skill-rewrite` — beğenilirse v5'e merge.

## Yaklaşım — writing-skills'ten

- **Baseline (RED) zaten elde:** beş denemenin belgeli arızaları *(108, 112, 113, 117, 118)*.
  Her biri bir pin testiyle kapatıldı ve **o testlerin hepsi korunuyor** — davranış envanterinin
  bekçisi onlar. Yeniden yazım onların altından geçmek zorunda.
- **Yeni kırmızıyı üç test verir:** iki persona açılışı ve kelime tavanı. Tavan, kısalmanın
  geri şişmemesinin bekçisi — bundan sonra eklenen her cümle bir şeyi silmeden giremez.
- **GREEN'i gerçek model verir:** doğrulama kullanıcının bu daldaki denemesi; pin testleri
  yalnız metnin sözünde durduğunu tutar.

## Test — `test_skills.py`, üç yeni

| Test | Aradığı |
|---|---|
| akış persona ile açılır | metin `You are an expert scenario writer` ile **başlar** |
| prompt+ persona ile açılır | metin `You are an expert SDXL prompt writer` ile **başlar** |
| metinler kısa kalır | akış ≤ **450** kelime, prompt+ ≤ **300** kelime |

Tavanlar hedef uzunluğun biraz üstü: bugün akış ~700, prompt+ ~470 — ikisi de kırmızı.

## Beklenen kırmızı

`test_skills.py` 3. Mevcut pinlerin hiçbiri bu turda değişmiyor; defter çifti dal yaşadıkça
bilinen kırmızı.

## Bilerek yapılmayanlar

- **`skills.py` açılmaz** — tur 2.
- **Mevcut pin testleri ellenmez** — bekçiler; tur 2'nin metni onların cümlelerini taşımak
  zorunda.
- **`dist` derlenmez.**
