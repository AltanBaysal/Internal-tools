# Madde 139 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-02-queenagent-m139-break-uygulama-design.md](../specs/2026-09-02-queenagent-m139-break-uygulama-design.md)
**Dal:** `feat/v6`
**Kırmızı commit:** `70d5542`
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. Ayraç kodda tek bir yerde durur.

`DEFAULT_QUALITY`'nin yanına, modül başına:

```python
# What goes between two character blocks. A feature of the interface that reads the prompt, not of
# the model: queen-editor's positive encoder splits on this literal string (Madde 138), and an
# encoder that does not know it would take the word as a tag. Spaces rather than commas on either
# side, because the split leaves whatever touches it inside the chunk.
BREAK = " BREAK "
```

## B. `build_prompts`'ın döngüsü blok listesi kurar.

Bugün tek bir `parts` listesi var ve sonunda tek bir `_tags` çağrısı. Yerine:

```python
        lead = [structure.get("quality") or DEFAULT_QUALITY, frame.get("people", "")]
        in_frame = _worn(frame.get("characters"))
        lead.extend(_block(in_frame[:1], characters, outfits, number, misses))
        place = frame.get("location") or ""
        if place:
            lead.append(_looked_up(place, locations, "locations", number, misses))
        lead.append(frame.get("action", ""))
        lead.append(frame.get("camera", ""))
        # Everyone behind the lead gets a block of their own rather than a comma: the encoder that
        # reads this splits on BREAK, so two descriptions on either side of one are encoded apart.
        blocks = [lead] + [
            _block([person], characters, outfits, number, misses) for person in in_frame[1:]
        ]
        # Empty blocks are dropped rather than joined: a prompt ending in a break, or carrying two
        # of them side by side, would ask the encoder to encode nothing.
        built.append(BREAK.join(tags for tags in map(_tags, blocks) if tags))
```

`_block` bir kişilik liste alıyor ve o kişinin kimliğiyle kıyafetlerini yan yana veriyor — bugün
zaten yaptığı iş, tek fark her seferinde bir kişiyle çağrılması.

**Sıra değişmiyor.** `lead`'in içi bugünkü `parts`'ın ilk yarısının aynısı, ve arkadakiler yine
`camera`'dan sonra.

→ Dört kırmızının dördü de yeşile döner.

## C. Koşuldu: **662 yeşil, 0 kırmızı.**

`python -m pytest queen-agent -q` — dört kırmızının dördü döndü, bekçilerin hiçbiri düşmedi. Sırayı
indeksle ölçen üç eski test yeşil kaldı, yani sıra gerçekten değişmedi.

`npm test --prefix queen-agent/frontend` — **36 dosya, 570 yeşil**, kırmızı turdakiyle birebir aynı.

## D. Yeşil commit.

`build_prompts.py` ve bu turun iki belgesi.

`dist` yeniden derlenmiyor: ön yüz değişmiyor.

## Bilerek yapılmayanlar

**`_tags`, `_block`, `_worn`, `_looked_up`** — dördü de ellenmiyor. Madde birleştirmenin üstünde
duruyor, içinde değil.

**`build_character_prompts`** — ellenmiyor, ve bekçisi bunu tutuyor.

**Skill metni ve şema** — [tasarımda](../specs/2026-09-02-queenagent-m139-break-uygulama-design.md)
gerekçesi yazılı: `BREAK`'i model yazmıyor, kod yerleştiriyor.

**Ön yüz ve `dist`.**
