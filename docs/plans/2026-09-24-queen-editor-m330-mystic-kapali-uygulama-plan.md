# Madde 330 — H3 videoları Mystic XXX'siz, uygulama turunun planı

> **Koşum:** bu oturumda, satır satır. Commit orkestratörün.

**Hedef:** `876704fe`'nin altı kırmızı testi yeşil, geri kalan her şey yeşil kalıyor.

**Spec:** [m330 uygulama turu](../specs/2026-09-24-queen-editor-m330-mystic-kapali-uygulama-design.md)

## Her yere geçerli kurallar

- Yorum **İngilizce** ve yalnız *neden*.
- Testlere dokunulmuyor; üretici, defter, `colab/downloads.py`, README ve ekran değişmiyor.
- Grafikler ham metinlerinde düzenleniyor: yeniden export yok, biçim değişmiyor.

---

## Görev 1: İki grafik

**Dosyalar:** Değiştir: `queen-editor/assets/workflow_video_h3_api.json` ve
`queen-editor/assets/workflow_video_h3_first_last_api.json` — `2678.inputs.stack_data`.

- [ ] **Adım 1: Mystic'in yuvası.** İkisinde de dosyanın ham metninde:

```
önce:  ...{\"on\":true,\"lora\":\"MysticXXX_MMH3-V4.safetensors\",\"str\":0.5,\"vs\":1,\"as\":1}...
sonra: ...{\"on\":true,\"lora\":\"None\",\"str\":1,\"vs\":1,\"as\":1}...
```

## Görev 2: Panelin grubu

**Dosya:** Değiştir: `queen-editor/backend/features/producers/domain/model_groups.py` — `H3_VIDEO`'nun
sonu.

- [ ] **Adım 1: Satır ve yorum.**

```python
    # Inside the lora stack's JSON, where a scan for model names cannot see it.
    {"folder": "loras", "name": "H3_Motion_BoosterV2.safetensors"},
]
```

## Görev 3: Koşu

- [ ] **Adım 1: Dört satırı koş**, paralel, yazıldığı gibi — hepsi yeşil. Dokunulmamış bir dosyada tek
  bir 5000 ms zaman aşımı görülürse o satır değiştirilmeden yeniden koşulur; iki koşu da bildirilir.
- [ ] **Adım 2: Durup dön** — commit orkestratörün: grafikler, grup, spec ve bu plan, `feat(m330): …`.
