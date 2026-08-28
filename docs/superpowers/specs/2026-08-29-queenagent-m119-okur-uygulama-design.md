# Madde 119 — Şema okurunu söyler · Tur 2 (uygulama) tasarımı

**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md) Madde 119 ve
[tur 1'in tasarımı](2026-08-29-queenagent-m119-okur-testler-design.md). Testler kırmızı commit'te.

## Değişen tek yer: `schema.py` · `STRUCTURE`

**1. En başa, olgu paragrafı** *("The structure is one JSON file..." cümlesinden önce)*:

> Every prompt built from this file goes to an SDXL-family image model. The model reads tags,
> never sentences, and one prompt renders one single still picture -- a frozen instant. Nothing
> that needs time to be seen reaches the picture: no motion, no sound, no before and after. A
> movement is written as the pose it passes through -- mid-stride, leaning in, head thrown back.

En başa, çünkü dosyadaki her kararın (etiket biçimi, kadraj kuralı, kamera sözlüğü) türediği olgu
bu; şemayı okuyan önce kime yazdığını öğrenir.

**2. Kamera paragrafında** *"Both are written, and the pair is chosen..."* şuna genişler:

> Both are written, both halves come from the lists just given -- a half that is not in them is
> not a tag -- and the pair is chosen for the scene rather than kept from the frame before.

## Korunan süpürmeler

Olgu paragrafı `{` içermiyor *(artikel süpürmesi örneği ilk `{`'den bulur)*, `shot` geçmiyor,
örnek değerleri değişmiyor.

## Bilerek yapılmayanlar

- **Skill metinleri ellenmez** — bağlam 120'nin işi.
- **Kural defteri ellenmez** — girdiler 121'in işi.
- **`dist` derlenmez.**

## Beklenen yeşil

`test_schema.py`'ın dördü dahil bütün suite; defter çifti bilinen kırmızı.
