# Madde 401 — Karenin senaryosu, implementasyon turunun planı

> **Koşum:** bu oturumda, satır satır. Takımı ve commit'i maddeyi koşan ajan yapıyor
> *(yol haritası, Dalga 2)*.

**Hedef:** `82c50959`'un 14 kırmızı testi yeşile döner, öteki testler yeşil kalır.

**Spec:** [m401 implementasyon turu](../specs/2026-10-01-queen-editor-m401-senaryo-uygulama-design.md)

## Her yere geçerli kurallar

- Dört dosya, hepsi `queen-editor/frontend/src/features/photo_generation/` altında: `glyphs.jsx`,
  `LayerPlayer.jsx`, `frame_status.jsx`, `PhotoDetail.jsx`. Testlere dokunulmaz; `dist` yapılmaz.
- Yorum İngilizce, neden'i söyler; ekrandaki sözler *"Senaryo"* ve *"Bu karenin senaryosu yok"*.

---

## Görev 1: İkon — `glyphs.jsx`

`CopyGlyph`'in ardına, tasarımın `scenario` çizgisiyle:

```jsx
// A page with lines of text: the scenario is a written sentence, not a picture.
export const ScenarioGlyph = ({ size }) => (
  <Glyph name="scenario" size={size}>
    <rect x="2.5" y="1.8" width="9" height="10.4" rx="1.3" stroke="currentColor"
          strokeWidth="1.4" />
    <path d="M4.7 5.2h4.6M4.7 7.4h4.6M4.7 9.6h2.6" stroke="currentColor" strokeWidth="1.3"
          strokeLinecap="round" />
  </Glyph>
);
```

## Görev 2: Resmin kutuları üstlerine konanı taşır

`LayerPlayer.jsx` — imza `LayerPlayer({ videoUrl, audioUrl, onReady, onFail, children })`; sahnenin
(`data-scene`) son çocuğu, `data-track`'in ardına:

```jsx
        {/* Whatever the page lays over the picture -- the scenario card (madde 401). Inside the
            scene so it measures itself from the player's own edges. */}
        {children}
```

`frame_status.jsx` — `Rendering({ style, children })`, halkanın ardına `{children}`; docstring'e:
*"What it is handed lies over the holder: the frame page's scenario card (madde 401)."*

## Görev 3: Kart — `PhotoDetail.jsx`

`ScenarioGlyph` import'a eklenir. `STRIP`'in ardına:

```jsx
// The frame's scenario over its picture (madde 401), in the design's bottom place (the owner's
// pick): along the bottom edge of the picture's own box, so one rule fits a square photo, a tall
// one, a wide one and the 16:9 player alike. On the player it stands above the clock and its line,
// or the waveform, instead of covering them. The dark of the page's other boxes over a picture, and
// deaf to clicks: the player takes a click on the picture to play and pause.
const SCENARIO = { position: "absolute", left: 12, right: 12, zIndex: 3, boxSizing: "border-box",
                   background: "rgba(10,8,7,.72)", borderRadius: 4, padding: "8px 12px",
                   fontSize: 12.5, lineHeight: 1.5, textAlign: "center",
                   textShadow: "0 1px 3px rgba(0,0,0,.6)", pointerEvents: "none" };

function ScenarioCard({ scene, lifted }) {
  return (
    <div data-scenario style={{ ...SCENARIO, bottom: lifted ? 40 : 12,
                                // An absence is a notice, not a sentence of the frame's own.
                                color: scene ? "#fff" : "rgba(255,255,255,.55)" }}>
      {scene || "Bu karenin senaryosu yok"}
    </div>
  );
}
```

## Görev 4: Düğme — `LayerTabs`

İmza `LayerTabs({ open, has, onOpen, sceneShown, onScene })`; yorumuna *"and after them, set apart,
the scenario's switch (madde 401)"*. `TABS.map(…)`'in ardına:

```jsx
      {/* A switch rather than a fourth tab: it lays something over the picture instead of opening
          a layer, so it wears no stroke box and no ground, behind a thin line of its own. */}
      <span style={{ width: 1, alignSelf: "stretch", background: "var(--border)",
                     margin: "0 2px" }} />
      <button type="button" aria-pressed={sceneShown} onClick={onScene}
              style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 10px",
                       background: "none", border: "none", cursor: "pointer",
                       transition: "color .12s",
                       color: sceneShown ? "var(--accent)" : "var(--ink-3)" }}>
        <ScenarioGlyph size={10} />
        <Mono size={10}>Senaryo</Mono>
      </button>
```

## Görev 5: Hâl ve kartın yerleri — `PhotoDetail`

`unfolded`'ın ardına:

```jsx
  // Whether the frame's scenario lies over the picture (madde 401). The user's press rather than the
  // frame's, like the details fold: checking a run of frames against their scenarios costs one press.
  const [sceneShown, setSceneShown] = useState(false);
```

`stageKey`'in ardına:

```jsx
  // The card for whichever box holds the picture; `lifted` on the player, over its clock.
  const scenarioCard = (lifted) => sceneShown && <ScenarioCard scene={frame.scene} lifted={lifted} />;
```

Effect'in yorumunda *"The open tab stays, and so does the details fold (madde 399), which was never
the frame's."* → *"The open tab stays, and so do the details fold (madde 399) and the scenario card
(madde 401), neither of which was ever the frame's."*

`<LayerTabs … sceneShown={sceneShown} onScene={() => setSceneShown((was) => !was)} />`, ve sahnenin
dallarında:

- `LayerPlayer`: `<LayerPlayer …>{scenarioCard(true)}</LayerPlayer>`
- katman üretilirken `FRAMED`: `<Making layer={open} />`'ın ardına `{scenarioCard(false)}`
- `<Rendering style={HOLDER}>{scenarioCard(false)}</Rendering>`
- hata alan yer tutucu: sebep satırının ardına `{scenarioCard(false)}`
- üretilmiş `FRAMED`: `<img …/>`'in ardına `{scenarioCard(false)}`
- kuyruktaki yer tutucu: *"henüz üretilmedi"*nin ardına `{scenarioCard(false)}`

## Görev 6: Koşu ve commit

- [ ] Dört satır, paralel — dördü de yeşil.
- [ ] `feat(queen-editor): 401 -- …`.
