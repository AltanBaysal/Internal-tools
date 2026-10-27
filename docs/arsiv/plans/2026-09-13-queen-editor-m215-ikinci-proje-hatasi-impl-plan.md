# Madde 215 · İkinci projede üretme hatası — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-13-queen-editor-m215-ikinci-proje-hatasi-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı `f170c29`'da. Bu tur bileşenleri değiştirir; teste dokunulmaz.

## Adımlar

**1 · `SidePanel.jsx` üç propu geçirir.** `LayerPanel` çağrısına `job`, `busyElsewhere` ve `error`.
Üçü de o bileşende zaten duruyor; gitmedikleri tek yer bu çağrıydı.

**2 · `LayerPanel.jsx` onları alır.**

- imzaya `job`, `busyElsewhere`, `error`;
- düğme: `disabled={submitting || missingProducer || busyElsewhere}`;
- düğmenin altındaki yuvaya iki dal, spec'in sırasıyla: yerel reddin ardından **sunucunun reddi**
  *(aynı kırmızı kart)*, sonra **başka proje sürüyor** notu *(gri, `var(--ink-3)`)*, sonra tahmin.

Cümle: `Üretim sürüyor: {job.project} — bitmesini bekle.`

**3 · `dist` derlenir.**

```
npm run build --prefix queen-editor/frontend
```

**4 · Takım koşulur**, dördü de:

```
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Dört kırmızı yeşile döner. **Okunacak:** fotoğraf panelinin kendi çivileri ve LayerPanel'in tahmin
cümlesini okuyan testler ayakta kalmalı — yeni dallar tahmini ancak meşgulken ya da hata varken
örtüyor, ve o testlerin hiçbiri öyle kurulmuyor.

**5 · Kaynak ve `dist` aynı commit'te.**

## Değişen dosyalar

`queen-editor/frontend/src/features/photo_generation/SidePanel.jsx`,
`queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`,
`queen-editor/frontend/dist`.
