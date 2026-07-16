// Queen Editor — Wireframe explorations
// Mounts the design canvas with the Video Editor direction (E).

const { useState, useEffect } = React;

const TWEAK_DEFAULTS = /*EDITMODE-BEGIN*/{
  "style": "sketchy",
  "accent": true,
  "annotations": true
}/*EDITMODE-END*/;

function App() {
  const [tweaks, setTweak] = useTweaks(TWEAK_DEFAULTS);

  // Apply tweak-driven body classes
  useEffect(() => {
    const root = document.documentElement;
    root.style.setProperty("--highlight", tweaks.accent ? "#ffe45c" : "transparent");
    root.classList.toggle("wf-no-anno", !tweaks.annotations);
  }, [tweaks.accent, tweaks.annotations]);

  const wfClass = "wf " + (tweaks.style === "clean" ? "is-clean" : "");
  // Inject style class to every artboard root by wrapping
  const wrap = (Comp) => () => (
    <div className={wfClass} style={{ width: "100%", height: "100%" }}>
      <Comp />
    </div>
  );

  return (
    <>
      <DesignCanvas>
        <DCSection
          id="intro"
          title="Queen Editor — Video Editor Yönü"
          subtitle="Prompt → foto → sıralı galeri. Üstte büyük preview, altta yatay sahne şeridi."
        >
          <DCArtboard id="brief" label="Brief & Sistem" width={520} height={720}>
            <BriefBoard />
          </DCArtboard>
        </DCSection>

        <DCSection
          id="dir-e"
          title="Video Editor Layout"
          subtitle="Sahne galerisi. Üstte büyük preview, altta yatay sahne şeridi. (v1 — proje kurulumu yok)"
        >
          <DCArtboard id="e-setupdone"  label="01 · Boş editör (sahne yok)" width={1440} height={900}>{React.createElement(wrap(ArtboardE_SetupDone))}</DCArtboard>
          <DCArtboard id="e-editor"     label="02 · Sahne seçili (12 sahne)" width={1440} height={900}>{React.createElement(wrap(ArtboardE_Editor))}</DCArtboard>
          <DCArtboard id="e-reorder"    label="03 · Sürükle-bırak ile sıralama" width={1440} height={900}>{React.createElement(wrap(ArtboardE_Reorder))}</DCArtboard>
          <DCArtboard id="e-addscene"   label="04 · Sahne ekle (boş prompt)" width={1440} height={900}>{React.createElement(wrap(ArtboardE_AddScene))}</DCArtboard>
          <DCArtboard id="e-generating" label="05 · Yeni sahne üretiliyor" width={1440} height={900}>{React.createElement(wrap(ArtboardE_Generating))}</DCArtboard>
          <DCArtboard id="e-deleteconfirm" label="06 · Sahneyi sil onayı"  width={1440} height={900}>{React.createElement(wrap(ArtboardE_DeleteConfirm))}</DCArtboard>
        </DCSection>
      </DesignCanvas>

      <TweaksPanel title="Tweaks">
        <TweakSection label="Stil" />
        <TweakRadio
          label="Çizim"
          value={tweaks.style}
          options={[{ value: "sketchy", label: "Sketchy" }, { value: "clean", label: "Clean" }]}
          onChange={(v) => setTweak("style", v)}
        />
        <TweakToggle
          label="Sarı vurgu"
          value={tweaks.accent}
          onChange={(v) => setTweak("accent", v)}
        />
        <TweakToggle
          label="El yazısı notlar"
          value={tweaks.annotations}
          onChange={(v) => setTweak("annotations", v)}
        />
      </TweaksPanel>
    </>
  );
}

// Brief recap board — shows scope + system at a glance
function BriefBoard() {
  return (
    <div className="wf wf--paper-grid" style={{ padding: 28, display: "flex", flexDirection: "column", gap: 16, overflow: "hidden", boxSizing: "border-box" }}>
      <div>
        <Hand size={32}><span className="wf-hl">Queen Editor</span></Hand>
        <Mono size={11} style={{ color: "var(--ink-3)", display: "block", marginTop: 4 }}>// wireframe brief</Mono>
      </div>

      <div className="wf-stroke" style={{ padding: 14 }}>
        <Hand size={18}>Akış</Hand>
        <div style={{ marginTop: 10, display: "flex", flexDirection: "column", gap: 10 }}>
          <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
            <Mono size={10} style={{ color: "var(--accent)", padding: "2px 6px", border: "1px solid var(--accent)", borderRadius: 3, flexShrink: 0 }}>v1</Mono>
            <div>
              <Note size={13} style={{ display: "block" }}><HL>Sahne Galerisi</HL> — prompt + kamera açısı</Note>
              <Mono size={11} style={{ color: "var(--ink-3)" }}>tek katman · proje kurulumu yok</Mono>
            </div>
          </div>
          <div style={{ display: "flex", gap: 10, alignItems: "flex-start" }}>
            <Mono size={10} style={{ color: "var(--ink-3)", padding: "2px 6px", border: "1px dashed var(--border-strong)", borderRadius: 3, flexShrink: 0 }}>son</Mono>
            <div>
              <Note size={13} style={{ display: "block", color: "var(--ink-3)" }}>Referans / karakter / arka plan</Note>
              <Mono size={11} style={{ color: "var(--ink-3)" }}>v1'de yok — ileride eklenecek</Mono>
            </div>
          </div>
        </div>
      </div>

      <div className="wf-stroke" style={{ padding: 12 }}>
        <Hand size={18}>Kurallar</Hand>
        <div style={{ display: "flex", flexDirection: "column", gap: 4, marginTop: 8 }}>
          <Note size={13} style={{ color: "var(--ink-2)" }}>· <HL>Numara = pozisyon</HL> · otomatik 001..N</Note>
          <Note size={13} style={{ color: "var(--ink-2)" }}>· Sıra <HL>sürükle-bırak</HL> ya da numara yazarak değişir</Note>
          <Note size={13} style={{ color: "var(--ink-2)" }}>· Üretim <HL>sona eklenir</HL></Note>
          <Note size={13} style={{ color: "var(--ink-2)" }}>· Her sahne <HL>tek prompt</HL>tan üretilir</Note>
        </div>
      </div>

      <div className="wf-stroke" style={{ padding: 12 }}>
        <Hand size={18}>Tip & Renk</Hand>
        <div style={{ display: "grid", gridTemplateColumns: "auto 1fr", gap: "8px 16px", marginTop: 10, alignItems: "baseline" }}>
          <Mono size={10} style={{ color: "var(--ink-3)" }}>ui</Mono>
          <Hand size={18}>IBM Plex Sans</Hand>
          <Mono size={10} style={{ color: "var(--ink-3)" }}>mono</Mono>
          <Mono size={13} style={{ color: "var(--ink)" }}>IBM Plex Mono · 001</Mono>
          <Mono size={10} style={{ color: "var(--ink-3)" }}>accent</Mono>
          <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <span style={{ width: 14, height: 14, borderRadius: 3, background: "var(--accent)" }} />
            <Mono size={12} style={{ color: "var(--ink-2)" }}>#a78bfa</Mono>
          </span>
        </div>
      </div>
    </div>
  );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
