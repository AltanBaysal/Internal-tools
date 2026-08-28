# Madde 120 — İşin bağlamı skillere ve plana iner · Tur 2 (uygulama) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 120 ve
[tur 1'in tasarımı](2026-08-29-queenagent-m120-baglam-testler-design.md). Testler kırmızı
commit'te.

## Değişen tek dosya: `skills.py`

**1. `GENERATE_PROMPTS_PLUS` açılışı** — ilk cümlenin önüne:

> All of this serves one end: the user is turning a story into prompts for an SDXL-family image
> model, and every prompt renders one single frozen frame of it.

**2. `START_A_SCENARIO` açılışı** — ilk cümlenin önüne:

> The end of this road is the same one: a story turned into prompts for an SDXL-family image
> model, one frozen frame at a time; everything gathered here is gathered for that.

Çekirdek dizilim iki metinde aynı — *"prompts for an SDXL-family image model"* — test ikisini tek
pinle tutuyor.

**3. Akışın 1. adımı** — *"it is where the flow keeps its place."* cümlesinin ardına:

> The plan opens with one line of context -- what is being made, and for what -- so a fresh chat
> that reads it inherits the work rather than only the steps.

## Bilerek yapılmayanlar

- **Taban yönerge ellenmez** — skill'siz sohbetin belli bir işi yok, bağlam işin skill'inde.
- **Şema ellenmez** — 119 kendi yarısını yazdı; iki metin aynı olguyu iki derinlikte söylüyor,
  kopya değil: şema dosya yazarken, skill açılışı her turda.
- **`dist` derlenmez.**

## Beklenen yeşil

`test_skills.py`'ın üçü dahil bütün suite; defter çifti bilinen kırmızı.
