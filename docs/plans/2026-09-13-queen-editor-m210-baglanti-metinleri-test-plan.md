# Madde 210 · Bağlantı metinleri — test turunun planı

**Spec:** [test turu](../specs/2026-09-13-queen-editor-m210-baglanti-metinleri-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testi** koyar. 120 dosyanın metni uygulama turunda düzelir.

## Adımlar

**1 · İki sabit eklenir.**

| Sabit | Ne | Neden |
|---|---|---|
| `LINK` | `\[([^\]]+)\]\(([^()\s]*-roadmap\.md)\)` | metni ve hedefi birlikte yakalar; var olan bağlantı çivisi yalnız hedefi yakalıyor |
| `IN_TEXT` | `\bv(\d+)\b` | metinde anılan sürüm |

**2 · `test_a_links_text_names_the_version_it_goes_to` yazılır.** Her markdown dosyası
*(`_markdown()` zaten iki tool'un dokümanlarını ve CLAUDE.md'yi veriyor)* taranır; her bağlantı için:

- hedefin dosya adı `SHAPE`'e uymuyorsa atlanır *(yol haritası değil ya da bozuk ad — onu başka çivi
  tutuyor)*;
- metinde `adıyla` geçiyorsa atlanır *(eski adı bilerek anan cümle)*;
- metindeki her `v<N>`, hedefin sürümüne eşit olmalı.

İhlal listesi dosya adıyla, metniyle ve hedefiyle basılır — uygulama turu o listeden çalışacak.

**3 · Takım koşulur.** Beklenen: tek kırmızı, içinde 120 dolayında ihlal.

```
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Kırmızının listesi **okunur**, körü körüne kabul edilmez: numarası ürüne ait olan bir metin
*(örneğin "tasarım v2")* yol haritasına bağlanıyorsa o yanlış kırmızıdır, ve çivi düzelir — belge
değil.

**4 · Kırmızı commit'lenir.**

## Değişen dosya

`queen-editor/backend/tests/test_version_record.py`.
