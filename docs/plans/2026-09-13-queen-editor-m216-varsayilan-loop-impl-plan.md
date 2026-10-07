# Madde 216 · Varsayılan mod Loop — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-13-queen-editor-m216-varsayilan-loop-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Kırmızı `d3e1313`'te. Bu tur bileşeni değiştirir; teste dokunulmaz.

## Adımlar

**1 · Varsayılan katmana sorar.** `LayerPanel.jsx`:

```
const [mode, setMode] = useState(layer === "video" ? LOOP : STANDARD);
```

Yanındaki not, ikinci sebebi de söyler: ses işine Standart'tan başka bir mod verilirse sunucu
reddediyor, ve o red ekrana ulaşmıyor.

**2 · `production_modes.js`'in listesindeki not düzelir.** *"Standart başta çünkü panel orada
açılıyor"* artık doğru değil; sıra aynı kalıyor, gerekçesi değişiyor.

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

Sekiz kırmızı yeşile döner, ses tarafındaki *"still asks for the plain mode"* yeşil kalır.

**5 · Kaynak ve `dist` aynı commit'te.**

## Değişen dosyalar

`queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx`,
`queen-editor/frontend/src/features/photo_generation/production_modes.js`,
`queen-editor/frontend/dist`.
