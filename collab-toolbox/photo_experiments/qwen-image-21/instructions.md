# Qwen Image 2.1 — Talimatlar

Madde 482 ve 484 *(v10 yol haritası)*. İki defter: `normal.ipynb` (25 adım) ve `turbo.ipynb` (8 adım).
Grafikler Comfy-Org'un **resmî şablonları**, olduğu gibi. Hangi dosya neden iniyor:
[indirilecekler.md](indirilecekler.md).

## Çalıştırma

1. Colab 🔑 Secrets'a **`CIVITAI_COOKIE`** ekle (LoRA'lar için zorunlu): civitai.red → giriş → F12 →
   Application → Cookies → `__Secure-civ-token`, değere çift tıkla → Ctrl+A → Ctrl+C. `HF_TOKEN` isteğe
   bağlı.
2. Defteri Colab'a yükle (**File → Upload notebook**), **Runtime → Change runtime type → A100**,
   **Run all**. Her şey baştan iner. En alttaki linke gir.
3. Sol kenarda **Workflows** → bir workflow → yaz → **Run** (Ctrl+Enter).

## Hangi workflow

- `…_t2i`: prompt'tan resim; `positive_prompt`'a yaz.
- `…_image_edit`: karakter referansı.
- `NoctQ_V4_workflow` *(yalnız normal)*: Noct Q, yazarının kendi ayarlarıyla (25 adım, cfg 3, negatif
  prompt).

## Karakter referansı

- Portreler Edit şablonunun `image_1` … `image_10` girişlerine. `image_1` düzenlenen resim, ve çıktının
  boyutu ondan gelir; ötekiler referans. Prompt'ta `<image1>`, `<image2>` diye anılırlar.
- Şablon Comfy'nin örnek resimleriyle açılır: kendi portreni bağlı `Load Image`'a yükle (normalde
  `image_1` ve `image_2`, Turbo'da yalnız `image_1`). Fazlası için yeni bir `Load Image` ekleyip
  büyük node'un ilk boş `image_N`'ine (normalde `image_3`, Turbo'da `image_2`) bağla.
- Başka bir boyut için `custom_size`'ı aç, `width` / `height`'ı ver.

## Noct Q'ya geçmek

- Büyük node'da `unet_name` → `NoctQ_V4_int8_convrot.safetensors` (t2i'de de Edit'te de).
- Turbo'da Noct Q'nun Turbo'su yok: aynı seçimin yanına `qwen_image_2.1_turbo_lora_avg_rank_178_bf16`
  LoRA'sını aşağıdaki gibi ekle. **Bu ikiliyi hiçbir kaynak denemedi.**

## LoRA eklemek

Büyük node'un alt grafiğine gir, `Load Diffusion Model` ile `QwenImage21Cache` arasına
`LoraLoaderModelOnly` koy ve `lora_name`'den seç; birden fazlası arka arkaya. `NoctQ_V4_workflow`'da:
`Load Diffusion Model` ile `KSampler` arasına.

## cfg

Noct Q ve LoRA kartları cfg'yi 1'in üstünde öneriyor (Noct Q 3, LoRA'lar 3 – 6); cfg 1'de negatif
prompt hiçbir şey yapmaz, ama iş yaklaşık iki kat hızlı. Şablonlar cfg 1'de açılıyor; `cfg` büyük
node'un üstünde. Turbo'da cfg 1 kalır; Turbo t2i'de cfg girişi yok.

## Prompt'lar

Deponun örnek senaryosundan dört kare
([docs/arsiv/research/2026-08-18-ornek-yapi.json](../../../docs/arsiv/research/2026-08-18-ornek-yapi.json)),
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
