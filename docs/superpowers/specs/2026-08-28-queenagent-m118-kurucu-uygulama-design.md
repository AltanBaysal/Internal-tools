# Madde 118 — Akış kurucuyu çağırmaz · Tur 2 (uygulama) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 118 ve
[tur 1'in tasarımı](2026-08-28-queenagent-m118-kurucu-testler-design.md). Testler kırmızı
commit'te; bu tur onların tarif ettiği cümleleri yazar.

## Değişen tek yer

`skills.py` · `START_A_SCENARIO` · 5. adım. Frame yasağının cümlesi ile *"Like the plan"*
arasına:

> build_prompts is never called here either: the builder is that skill's too, and the file this
> flow leaves holds no frames for it to build from. The handoff offers nothing and asks nothing
> -- it states what is standing and where the work continues, and the next move is the user's in
> the skills menu.

**Neden burası:** yasağın yanına, çünkü ikisi aynı yasağın iki yarısı — yazmak ve kurmak; ve
*"it is the last word"* cümlesinin önüne, çünkü önermezlik o son sözün nasıl bir söz olduğunu
söylüyor.

## Bilerek yapılmayanlar

- **`modes.py` ellenmez** — araçların istekte durması Madde 99'un kararı; iş metnin.
- **Taban yönergenin tek-soru cümlesi ellenmez** — devir adımı onun istisnası ve istisna akışın
  metnine yazıldı.
- **2. adımın önizleme teklifi ellenmez** — *"Offer it"* karakter adımının kendi işi.
- **`dist` derlenmez** — ön yüz bu maddede yok.

## Beklenen yeşil

`test_skills.py`'ın iki yenisi dahil bütün suite; kalan iki kırmızı `test_notebook`'un ve dal
yaşadıkça bilinen kırmızı.
