# Qwen Image 2.1 — ilk bakış — Talimatlar

Madde 482 *(v10 yol haritası)*. İki defter, her biri yalnız kendi modelini indirir; grafik ikisinde de
Comfy-Org'un **resmî şablonu**, olduğu gibi. Hangi dosya neden iniyor:
[indirilecekler.md](indirilecekler.md).

## Çalıştırma

| Defter | Şablon |
|---|---|
| `normal.ipynb` *(25 adım)* | `image_qwen_image_2_1_t2i` |
| `turbo.ipynb` *(8 adım)* | `image_qwen_image_2_1_turbo_t2i` |

1. Defteri Colab'a yükle (**File → Upload notebook**), **Runtime → Change runtime type → A100**,
   **Run all**. En alttaki linke gir.
2. Sol kenarda **Workflows** → defterin şablonu (defter oraya koydu).
3. `positive_prompt`'a yaz → **Run** (Ctrl+Enter).

⚠️ İki şablon da cfg 1'de koşuyor, ve **cfg 1'de negatif prompt hiçbir şey yapmaz** (şablonun notu:
*"negative_prompt: unused while cfg is 1"*).

## Prompt'lar

Deponun örnek senaryosundan dört kare
([docs/research/2026-08-18-ornek-yapi.json](../../../docs/research/2026-08-18-ornek-yapi.json)),
her biri iki hâliyle.

- **Etiket:** QueenAgent'ın `build_prompts`'unun bu kare için yazdığı prompt, `BREAK` dahil birebir
  kopyalandı.
- **Düzyazı:** aynı karenin cümleyle yazılmışı; etiketin söylediğinden fazlasını söylemez. Tek bilerek
  eklenen, baştaki `Anime-style illustration` cümlesi.

### Kare 1 — yatak odası, mektup

Etiket:

```
score_9_up, score_9, score_8_up, masterpiece, best quality, raw, high quality, 4k, absurdres, 1girl, solo, woman in her mid 20s, goth woman, pale skin, long black hair, green eyes, slim body, white nightgown, lace trim, bare shoulders BREAK sitting on the edge of the bed, holding a letter, pensive expression, medium shot, from slightly above, cozy bedroom, morning light through curtains, indoors
```

Düzyazı:

```
Anime-style illustration. A goth woman in her mid twenties with pale skin, long black hair, green eyes and a slim build sits on the edge of the bed in a cozy bedroom, holding a letter, with a pensive expression. She wears a white nightgown with lace trim and her shoulders are bare. Morning light comes in through the curtains. Medium shot, seen from slightly above.
```

### Kare 2 — kapı önü, tam boy

Etiket:

```
score_9_up, score_9, score_8_up, masterpiece, best quality, raw, high quality, 4k, absurdres, 1girl, solo, woman in her mid 20s, goth woman, pale skin, long black hair, green eyes, slim body, oversized long black t-shirt, black thong BREAK standing in doorway, door opening, light blush, soft flirty smile, looking at viewer, full body, apartment doorway, daytime, natural light, indoors
```

Düzyazı:

```
Anime-style illustration. A goth woman in her mid twenties with pale skin, long black hair, green eyes and a slim build stands in the doorway of an apartment as the door opens. She wears an oversized long black t-shirt and a black thong. She has a light blush and a soft, flirty smile, and she is looking at the viewer. Daytime, natural light indoors. Full-body shot.
```

### Kare 3 — iki karakter

Etiket:

```
score_9_up, score_9, score_8_up, masterpiece, best quality, raw, high quality, 4k, absurdres, 1girl, solo, woman in her mid 20s, goth woman, pale skin, long black hair, green eyes, slim body, oversized long black t-shirt, black thong, red knit scarf BREAK 1boy, man in his late 20s, short black hair, stubble, athletic build, dark grey suit, white shirt, no tie BREAK handing over a small package, fingers touching, surprised expressions, medium shot, side view, apartment doorway, daytime, natural light, indoors
```

Düzyazı:

```
Anime-style illustration of two people at an apartment doorway in daytime, natural light indoors. A goth woman in her mid twenties with pale skin, long black hair, green eyes and a slim build wears an oversized long black t-shirt, a black thong and a red knit scarf. A man in his late twenties with short black hair, stubble and an athletic build wears a dark grey suit and a white shirt with no tie. A small package is being handed over, their fingers are touching, and both have surprised expressions. Medium shot, side view.
```

### Kare 4 — yakın plan, gözyaşı

Etiket:

```
score_9_up, score_9, score_8_up, masterpiece, best quality, raw, high quality, 4k, absurdres, 1girl, solo, woman in her mid 20s, goth woman, pale skin, long black hair, green eyes, slim body BREAK extreme close-up of her eyes, single tear, soft focus, extreme close-up, cozy bedroom, morning light through curtains, indoors
```

Düzyazı:

```
Anime-style illustration. An extreme close-up of the eyes of a goth woman in her mid twenties with pale skin, long black hair, green eyes and a slim build, with a single tear. Soft focus. A cozy bedroom indoors, morning light through the curtains.
```
