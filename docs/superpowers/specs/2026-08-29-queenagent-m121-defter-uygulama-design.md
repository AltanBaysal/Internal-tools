# Madde 121 — Action sızıntıları kural defterine girer · Tur 2 (uygulama) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 121 ve
[tur 1'in tasarımı](2026-08-29-queenagent-m121-defter-testler-design.md). Testler kırmızı
commit'te.

## Değişen tek yer: `schema.py` · `RULEBOOK` — 9'un ardına beş girdi

> 10. A movement or a span of time inside an action -- moving, back and forth, slowly. One
> prompt is one frozen instant; write the pose the movement passes through.
> 11. Camera language inside an action -- full body view, upper body visible -- when camera is
> its own field. Two framings fight, and the picture obeys neither.
> 12. A story role naming a character inside an action -- stepson, lover, boss. The camera sees
> a person, not a relationship, and the frame's characters map already says who is in it.
> 13. An or inside any value. The model draws one picture; an or is a coin it cannot toss. Pick
> one, or make two frames.
> 14. An outfit named after its wearer, or two entries carrying the same text for two wearers.
> The garment names the outfit, and one garment is one entry, whoever wears it.

## Korunan süpürmeler

Girdilerde `style` yok *(mevcut süpürme onu yasaklıyor)*, `shot` yok, artikel süpürmesi örnek
bölgesine bakıyor ve defter o bölgede değil.

## Bilerek yapılmayanlar

- **Şemanın düzyazısı değişmez** — 119 kendi yarısını yazdı.
- **Kod değişmez** — `build_prompts` ne bulursa basar *(K26'nın çizgisi)*; yakalamak yazanın işi.
- **`dist` derlenmez.**

## Beklenen yeşil

`test_schema.py`'ın beşi dahil bütün suite; defter çifti bilinen kırmızı.
