# Madde 212 · Oynatma düğmesi — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-13-queen-editor-m212-oynatma-dugmesi-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı `ac6dbfa`'da. Bu tur bileşeni değiştirir; teste dokunulmaz.

## Adımlar

**1 · `SCENE`'e imleç.** `cursor: "pointer"` — kare artık tıklanabilir ve bunu söylemesi gerekiyor.

**2 · Sahne tıklamayı alır.** `<div data-scene style={SCENE} onClick={toggle}>`.

**3 · Düğme duruma göre çizilir ve kabarmayı durdurur.**

```
style={{ ...BUTTON, opacity: playing ? 0 : 1 }}
onClick={(event) => { event.stopPropagation(); toggle(); }}
```

`BUTTON` sabiti bölünmüyor; üzerine yalnız `opacity` biniyor.

**4 · `dist` derlenir.**

```
npm run build --prefix queen-editor/frontend
```

**5 · Takım koşulur**, dördü de:

```
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Üç kırmızı yeşile döner, on bir eski test ayakta kalır — özellikle *"plays and pauses from the one
round button"*, çünkü düğme DOM'dan çıkmıyor.

**6 · Kaynak ve `dist` aynı commit'te.** Ayrı commit'lenirse defter tarafında görünen şey eski
derlemedir.

## Değişen dosyalar

`queen-editor/frontend/src/features/photo_generation/LayerPlayer.jsx` ve
`queen-editor/frontend/dist`.
