# Madde 212 · Oynatma düğmesi — test turunun planı

**Spec:** [test turu](../specs/2026-09-13-queen-editor-m212-oynatma-dugmesi-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar. Bileşen ve `dist` uygulama turunda değişir.

## Adımlar

**1 · Dört `it` eklenir**, var olan on birin sonuna,
`queen-editor/frontend/src/features/photo_generation/LayerPlayer.test.jsx` içine.

| Test | Nasıl kurulur | Ne bekler |
|---|---|---|
| `hides the button while the video plays` | *Oynat*'a basılır | düğmenin `style.opacity` → `"0"`; *Duraklat*'a basılınca `"1"` |
| `starts the video when the picture is clicked` | `[data-scene]`'e tıklanır | düğme *Duraklat* der |
| `pauses the video when the picture is clicked` | önce oynatılır, sonra `[data-scene]`'e tıklanır | düğme *Oynat* der, `opacity` → `"1"` |
| `turns the video once when the button itself is clicked` | duruyorken düğmeye tıklanır | *Duraklat* — iki kez dönüp başa sarmıyor |

Düğme `aria-label` ile bulunuyor *(`Oynat` / `Duraklat`)*, dosyanın var olan alışkanlığı. Sahne
`[data-scene]` ile — o kanca da zaten orada.

**2 · Takım koşulur.** Beklenen: ilk üçü kırmızı, dördüncüsü yeşil *(spec bunun sebebini yazıyor —
bugünkü kodu değil, bu maddenin getireceği kabarmayı tutuyor)*.

```
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Kırmızı **okunur**: düşmesi gereken üç testin düşmesi ve var olan on birin ayakta kalması beklenir.
Özellikle *"plays and pauses from the one round button"* yeşil kalmalı — düğme DOM'dan çıkmıyor.

**3 · Kırmızı commit'lenir.**

## Değişen dosya

`queen-editor/frontend/src/features/photo_generation/LayerPlayer.test.jsx`.
