# Madde 328 — Mystic XXX LoRA'sı, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** `cff9c38f`'in yedi kırmızı testi yeşil, geri kalan her şey — defterin tavanı dahil — yeşil
kalıyor.

**Spec:** [m328 uygulama turu](../specs/2026-09-24-queen-editor-m328-mystic-lora-uygulama-design.md)

## Her yere geçerli kurallar

- Ad her yerde aynı dize: `MysticXXX_MMH3-V4.safetensors`.
- Yorum ve docstring **İngilizce** ve yalnız *neden*; defterin kod hücresine yorum girmiyor.
- Kırmızı testlere dokunulmuyor; üretici ve ekran değişmiyor.

---

## Görev 1: İki grafik

**Dosyalar:** Değiştir: `queen-editor/assets/workflow_video_h3_api.json` ve
`queen-editor/assets/workflow_video_h3_first_last_api.json` — `2678.inputs.stack_data`.

- [ ] **Adım 1: Yuva 1.** İkisinde de dosyanın ham metninde, Motion Booster'ın ardındaki yuvada:

```
önce:  ...\"lora\":\"H3_Motion_BoosterV2.safetensors\",\"str\":0.7,\"vs\":1,\"as\":1},{\"on\":true,\"lora\":\"None\",\"str\":1,...
sonra: ...\"lora\":\"H3_Motion_BoosterV2.safetensors\",\"str\":0.7,\"vs\":1,\"as\":1},{\"on\":true,\"lora\":\"MysticXXX_MMH3-V4.safetensors\",\"str\":1,...
```

## Görev 2: Panelin grubu

**Dosya:** Değiştir: `queen-editor/backend/features/producers/domain/model_groups.py` — `H3_VIDEO`'nun
sonu.

- [ ] **Adım 1: Satır ve yorum.**

```python
    # The lora stack's two, inside its JSON where a scan for model names cannot see them.
    {"folder": "loras", "name": "H3_Motion_BoosterV2.safetensors"},
    {"folder": "loras", "name": "MysticXXX_MMH3-V4.safetensors"},
]
```

## Görev 3: Defter

**Dosya:** Değiştir: `queen-editor/queeneditor.ipynb` — modeller hücresinde `CIVITAI_H3`'ün sonu.
Hücre tek bir JSON dizesi; düzenleme ham metinde, kaçışlı tırnak ve `\n`'lerle.

- [ ] **Adım 1: Satır.** Hücrenin okunduğu hâliyle:

```python
    (3228867, LORA, "H3_Motion_BoosterV2.safetensors", "H3 Motion Booster"),
    (3266628, LORA, "MysticXXX_MMH3-V4.safetensors", "H3 Mystic XXX"),
]
```

- [ ] **Adım 2: Giriş hücresi.** Secrets maddesinin son üç satırı:

```
   oradan iner, yenileri oraya yüklenir); `CIVITAI_COOKIE` aynada henüz olmayan ya da aynası
   kapalı bir dosya için (civitai.red → F12 → Application → Cookies → `__Secure-civ-token`, ~30
   günde bir yenilenir); video için `XAI_API_KEY` (video prompt'unu yazan dil modeli).
```

## Görev 4: Aynasız liste

**Dosya:** Değiştir: `queen-editor/colab/downloads.py` — `MIRRORLESS = set()`'in yerine; üstündeki 327
yorumu olduğu gibi.

- [ ] **Adım 1: Girdi.**

```python
MIRRORLESS = {
    # H3's Mystic XXX lora, while the user tries it (madde 328).
    "MysticXXX_MMH3-V4.safetensors",
}
```

## Görev 5: README

**Dosya:** Değiştir: `queen-editor/README.md` — Secrets tablosunun iki satırı.

- [ ] **Adım 1: `CIVITAI_COOKIE`.**

```
| `CIVITAI_COOKIE` | The `__Secure-civ-token` cookie from `civitai.red` (log in → F12 → Application → Cookies). A gated file comes from Civitai with this cookie when the Hugging Face mirror does not hold it yet, or when it is on `MIRRORLESS` in [colab/downloads.py](colab/downloads.py) and skips the mirror; a run that fetches no such file needs none. It expires every ~30 days; re-paste it when an install stops with Civitai's own response. |
```

- [ ] **Adım 2: `HF_TOKEN`.**

```
| `HF_TOKEN` | Your private Hugging Face repo that mirrors the Civitai files (`HF_MIRROR` in CONFIG), all but those on `MIRRORLESS` in [colab/downloads.py](colab/downloads.py). A file it holds comes from there, fast; a file it lacks comes from Civitai once and is uploaded to it. Make it fine-grained, **that one repo only, read and write**. |
```

## Görev 6: Koşu

- [ ] **Adım 1: Dört satırı koş** — hepsi yeşil; defter tavanın altında.
- [ ] **Adım 2: Durup dön** — commit orkestratörün: kod, grafikler, defter, README, spec ve bu plan,
  `feat(m328): …`.
