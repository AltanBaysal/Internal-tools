# Madde 125 · Tur 2 (uygulama) — Tasarım

**Kaynak:** [2026-08-25-queenagent-v5-roadmap.md](../plans/2026-08-25-queenagent-v5-roadmap.md) · Madde 125
**Testler kırmızı commit'te (be187dd).** Bu tur yalnız `tools.py`'nin iki tanım metnine dokunur.

## Cümleler

`edit_file`: *"...match what is on disk now: read the file first if this turn has not seen it --
what this turn read or wrote is already in front of you -- and include enough of what surrounds
it to be sure."*

`write_plan`: *"Writes over the plan of that name if there is one, so hand back the whole plan
rather than the part you changed -- read it first if this turn has not seen it."*

Koşul iki tanımda da aynı sözle *(`if this turn has not seen it`)*: iki ayrı kural okuyan model
hangisinin geçerli olduğunu sorar, aynı sözü okuyan sormaz.

## Ayakta kalması gerekenler

Tur 1 tasarımındaki liste: eşleşme şartı, tam-plan şartı, `asked only to plan` / `carry on`
pinleri, araç sayımı.

## Bilerek yapılmayanlar

Kod, parametreler, araç adları, taban yönerge ve skill metinleri ellenmez; okuma kopyasında
araç JSON'ı bu maddelerin sonunda topluca güncellenir.
