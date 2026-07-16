// Direction E — Video Editor Layout
// Top: large preview of selected scene + inline prompt + composer.
// Bottom: horizontal "scene timeline" strip with thumbnails side-by-side.
// Scrollbar visible when overflowing, with playhead-style position indicator.
// States: Empty, Editor (full), Generating new at end.

const TimelineCard = ({ n, prompt, selected, loading, dim, narrow }) => (
  <div className={"wf-card"} style={{
    width: narrow ? 130 : 160,
    flexShrink: 0,
    position: "relative",
    padding: 6,
    display: "flex",
    flexDirection: "column",
    gap: 6,
    borderColor: selected ? "var(--accent)" : "var(--border)",
    borderWidth: 1,
    boxShadow: selected ? "0 0 0 1px var(--accent)" : "none",
    background: selected ? "var(--bg-3)" : "var(--bg-2)",
    opacity: dim ? .55 : 1,
    cursor: "grab",
  }}>
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      {/* number reads as editable: dashed underline + caret hint, click to renumber */}
      <span
        title="Sırayı değiştir — yeni numara yaz"
        style={{
          display: "inline-flex", alignItems: "center", gap: 3,
          borderBottom: "1px dashed " + (selected ? "var(--accent)" : "var(--border-strong)"),
          paddingBottom: 1, cursor: "text",
        }}
      >
        <Seq n={n} hl={selected} />
        <span style={{ display: "inline-flex", color: selected ? "var(--accent)" : "var(--ink-3)" }}><Icon.Pencil /></span>
      </span>
      <span style={{ flex: 1 }} />
      {/* clear drag handle for reordering */}
      <Grip style={{ opacity: .9, cursor: "grab" }} />
    </div>
    <ImgPH loading={loading} style={{ aspectRatio: "16/10", width: "100%" }} label={`sc ${n}`} />
  </div>
);

// Add-scene tile — identical shell to TimelineCard so it slots into the
// timeline rhythm. The photo area is replaced with the call-to-action.
// `nextN` softly shows the position this scene WILL take (last + 1).
const AddSceneTile = ({ narrow, nextN, selected }) => (
  <button className={"wf-card"} style={{
    width: narrow ? 130 : 160,
    flexShrink: 0,
    position: "relative",
    padding: 6,
    display: "flex",
    flexDirection: "column",
    gap: 6,
    borderColor: selected ? "var(--accent)" : "var(--border-strong)",
    borderWidth: 1,
    borderStyle: "dashed",
    background: selected ? "var(--bg-3)" : "transparent",
    boxShadow: selected ? "0 0 0 1px var(--accent)" : "none",
    cursor: "pointer",
    font: "inherit",
    color: selected ? "var(--accent)" : "var(--ink-2)",
    textAlign: "left",
    transition: "border-color .12s, background .12s, color .12s",
  }}
    onMouseEnter={(e) => { if (!selected) { e.currentTarget.style.borderColor = "var(--accent)"; e.currentTarget.style.color = "var(--accent)"; } }}
    onMouseLeave={(e) => { if (!selected) { e.currentTarget.style.borderColor = "var(--border-strong)"; e.currentTarget.style.color = "var(--ink-2)"; } }}
  >
    {/* Same header rhythm: soft preview of the slot number (last+1). */}
    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
      {nextN != null && (
        <span style={{
          fontFamily: "IBM Plex Mono, monospace",
          fontSize: 11,
          padding: "2px 6px",
          border: "1px dashed currentColor",
          borderRadius: 3,
          color: "currentColor",
          letterSpacing: ".05em",
          opacity: selected ? .85 : .55,
        }}>{String(nextN).padStart(3, "0")}</span>
      )}
      <span style={{ flex: 1 }} />
      <span style={{ width: 18 }} />
    </div>
    {/* Photo slot → "sahne ekle" label, same aspect ratio + diagonal-stripe vibe */}
    <div style={{
      aspectRatio: "16/10",
      width: "100%",
      border: "1px dashed currentColor",
      borderRadius: "var(--r-sm)",
      backgroundImage: "repeating-linear-gradient(-45deg, rgba(167,139,250,.04) 0 6px, transparent 6px 14px)",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      gap: 6,
      color: "currentColor",
    }}>
      <span style={{ fontSize: 20, fontWeight: 400 }}>＋</span>
      <span style={{
        fontFamily: "IBM Plex Mono, monospace",
        fontSize: 10,
        }}>sahne ekle</span>
    </div>
  </button>
);

// Custom faux scrollbar — sketchy
const FauxScrollbar = ({ progress = 0.25, thumb = 0.35, marks = 0 }) => (
  <div style={{ position: "relative", height: 14, padding: "0 4px" }}>
    <div style={{
      position: "absolute",
      left: 4, right: 4, top: 6,
      height: 2,
      background: "var(--border)",
      borderRadius: 2,
    }} />
    {/* tick marks for total scene count */}
    {marks > 0 && Array.from({ length: marks }).map((_, i) => (
      <div key={i} style={{
        position: "absolute",
        left: `calc(${4 + (i / (marks - 1)) * 100}% - ${(i / (marks - 1)) * 8 + 4}px)`,
        top: 3,
        width: 1, height: 8,
        background: "var(--ink-4)",
      }} />
    ))}
    {/* thumb */}
    <div style={{
      position: "absolute",
      top: 0,
      left: `calc(${progress * 100}% + 4px)`,
      width: `${thumb * 100}%`,
      height: 14,
      background: "var(--ink-2)",
      borderRadius: 7,
      maxWidth: "calc(100% - 8px)",
      transform: "translateX(0)",
    }} />
  </div>
);

const EditorTopBarE = ({ title, status }) => (
  <header style={{
    display: "flex", alignItems: "center", gap: 12,
    padding: "14px 24px",
    borderBottom: "1px solid var(--border)",
    background: "var(--bg-2)",
  }}>
    <Hand size={24}><span className="wf-hl">Queen Editor</span></Hand>
    {title && <Hand size={16} style={{ color: "var(--ink-2)" }}>· {title}</Hand>}
    <span style={{ flex: 1 }} />
    {status}
  </header>
);

// Composer pinned below preview — Tekil/Liste sits next to Üret so the mode
// is one glance away from the action. When a scene is selected, the textbox
// is pre-filled with that scene's prompt; pressing Üret regenerates it
// (changed or not). To add a new scene the user clicks the + tile in the
// timeline which clears this composer.
const InlineComposerE = ({ disabled, defaultValue = "", generating, mode = "Tekil", editingSeq = null }) => (
  <div className="wf-stroke" style={{
    padding: 10, display: "flex", alignItems: "center", gap: 10,
    background: "var(--bg-2)",
    boxShadow: "none",
  }}>
    {editingSeq != null && <Seq n={editingSeq} hl />}
    <input className="wf-input" style={{ flex: 1 }} placeholder={mode === "Tekil" ? "bir sonraki sahneyi tarif et…" : "1. ilk sahne\n2. ikinci sahne\n…"} defaultValue={defaultValue} disabled={disabled} />
    <div style={{
      display: "flex", alignItems: "center", gap: 8,
    }}>
      <Segment options={["Tekil", "Liste"]} value={mode} hl />
      {generating
        ? <Status dot hl>Çalışıyor</Status>
        : <Btn primary hl disabled={disabled}><Icon.Sparkle /> Üret</Btn>}
    </div>
  </div>
);

// Vertical composer for the right rail. Roomier textarea for long prompts.
const SideComposer = ({ disabled, defaultValue = "", generating, mode = "Tekil" }) => (
  <aside className="wf-stroke" style={{
    width: 360, flexShrink: 0,
    padding: 14, display: "flex", flexDirection: "column", gap: 12,
    background: "var(--bg-2)",
    minHeight: 0,
  }}>
    <textarea
      className="wf-input"
      style={{ flex: 1, minHeight: 180, resize: "none" }}
      placeholder={mode === "Tekil" ? "sahnede ne oluyor + kamera açısı…" : "1. ilk sahne\n2. ikinci sahne\n…"}
      defaultValue={defaultValue}
      disabled={disabled}
    />

    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <Segment options={["Tekil", "Liste"]} value={mode} hl />
      <span style={{ flex: 1 }} />
      <Btn primary hl disabled={disabled}><Icon.Sparkle /> Üret</Btn>
    </div>
  </aside>
);

const TimelineFooter = ({ scenes, selectedIdx, loadingAtEnd, scrollProgress = 0, thumb = 0.35, empty, addSelected }) => {
  const total = scenes.length + (loadingAtEnd ? 1 : 0);
  const curr = empty ? 0 : (addSelected ? scenes.length + 1 : (selectedIdx + 1));
  return (
    <footer style={{
      background: "var(--bg)",
      borderTop: "1px solid var(--border)",
      padding: "10px 0 8px",
      display: "flex",
      flexDirection: "column",
      gap: 6,
      flexShrink: 0,
    }}>
      {/* minimal strip header: reorder hint + nav + position counter */}
      <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "0 24px" }}>
        {!empty && (
          <Mono size={11} style={{ color: "var(--ink-3)", display: "inline-flex", alignItems: "center", gap: 6 }}>
            <Grip style={{ opacity: .8 }} /> sürükle ya da numaraya dokun — sıra otomatik güncellenir
          </Mono>
        )}
        <span style={{ flex: 1 }} />
        {!empty && (
          <>
            <Btn sm ghost icon title="prev"><Icon.Left /></Btn>
            <Btn sm ghost icon title="next"><Icon.Right /></Btn>
          </>
        )}
        <Mono size={11} style={{ color: "var(--ink-3)", paddingLeft: 4 }}>
          {String(curr).padStart(3, "0")} / {String(total).padStart(3, "0")}
        </Mono>
      </div>

      {/* strip itself */}
      <div style={{
        display: "flex",
        gap: 8,
        alignItems: "stretch",
        overflowX: "hidden",
        padding: "4px 24px",
        position: "relative",
      }}>
        <div style={{
          display: "flex",
          gap: 8,
          transform: `translateX(-${scrollProgress * 100}%)`,
          transition: "none",
          paddingRight: 100,
        }}>
          {scenes.map((p, i) => (
            <TimelineCard key={i} n={i + 1} prompt={p} selected={i === selectedIdx} />
          ))}
          {loadingAtEnd && (
            <TimelineCard n={scenes.length + 1} prompt="eski kütüphane, toz, ışık huzmesi" loading selected />
          )}
          <AddSceneTile nextN={scenes.length + (loadingAtEnd ? 2 : 1)} selected={addSelected} />
        </div>
      </div>

      {/* fake scrollbar — only when there is actually something to scroll */}
      {!empty && (
        <div style={{ padding: "0 24px" }}>
          <FauxScrollbar progress={scrollProgress} thumb={thumb} marks={Math.min(scenes.length, 12)} />
        </div>
      )}
    </footer>
  );
};

// ──────────────────────────────────────────────────────────────────────────
// Sample setup data used across boards 02–04
// ──────────────────────────────────────────────────────────────────────────
const SAMPLE_SETUP = {
  projectName: "İstanbul Film Notları",
};

// Empty editor — no scenes yet, composer ready, timeline empty
const ArtboardE_SetupDone = () => (
  <div className="wf" style={{ display: "flex", flexDirection: "column", height: "100%", background: "var(--bg)" }}>
    <EditorTopBarE title={SAMPLE_SETUP.projectName} />

    <main style={{ flex: 1, display: "flex", padding: "20px 24px 16px", gap: 16, minHeight: 0 }}>
      <div className="wf-stroke wf-stroke--dashed" style={{
        flex: 1, background: "var(--bg-2)",
        display: "flex", alignItems: "center", justifyContent: "center",
      }}>
        <Mono size={11} style={{ color: "var(--ink-3)" }}>preview</Mono>
      </div>
      <SideComposer />
    </main>

    <TimelineFooter scenes={[]} selectedIdx={-1} empty />
  </div>
);

const ArtboardE_Editor = () => {
  const scenes = [
    "gün batımında deniz kenarında oturan kadın, sıcak tonlar, film grain",
    "kahve fincanı, ahşap masa, soft ışık, üstten görünüm",
    "neon ışıklı dar sokak, yağmur, yansımalar, gece",
    "minimal beyaz oda, tek sandalye, doğal ışık",
    "dağ manzarası, sis, geniş açı, mavi saat",
    "vintage daktilo close-up, makro, sıcak ışık",
    "köpek koşuyor sahilde, hareket bulanıklığı",
    "kütüphane, kitap rafları, perspektif",
    "boğaz, vapur, sabah",
    "rıhtım, balıkçı, vinil doku",
    "tramvay durağı, yağmur damlaları",
    "çatı katı, gün doğumu, panorama",
  ];
  const selectedIdx = 2;
  return (
    <div className="wf" style={{ display: "flex", flexDirection: "column", height: "100%", background: "var(--bg)" }}>
      <EditorTopBarE title={SAMPLE_SETUP.projectName} />

      <main style={{ flex: 1, display: "flex", padding: "20px 24px 16px", gap: 16, minHeight: 0 }}>
        {/* Preview fills width minus the right composer */}
        <section style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
          <div style={{ position: "relative", flex: 1, minHeight: 0 }}>
            <ImgPH style={{ width: "100%", height: "100%" }} label={`scene ${selectedIdx + 1} preview`} />
            <div style={{ position: "absolute", top: 12, left: 12 }}>
              <Seq n={selectedIdx + 1} xl hl />
            </div>
            <div style={{ position: "absolute", top: 12, right: 12, display: "flex", gap: 6 }}>
              <Btn sm ghost icon style={{ color: "var(--danger)", borderColor: "var(--danger)" }}><Icon.Trash /></Btn>
            </div>
          </div>
        </section>

        <SideComposer defaultValue={scenes[selectedIdx]} editingSeq={selectedIdx + 1} />
      </main>

      <TimelineFooter scenes={scenes} selectedIdx={selectedIdx} scrollProgress={0.18} thumb={0.45} />
    </div>
  );
};

// Reorder demo — a card lifted mid-drag, an insertion line at the target slot,
// and a soft "→ 002" badge previewing the new number. Communicates that scenes
// can be reordered by dragging (or by editing the number directly).
const ArtboardE_Reorder = () => {
  const scenes = [
    "gün batımında deniz kenarında oturan kadın, sıcak tonlar, film grain",
    "kahve fincanı, ahşap masa, soft ışık, üstten görünüm",
    "neon ışıklı dar sokak, yağmur, yansımalar, gece",
    "minimal beyaz oda, tek sandalye, doğal ışık",
    "dağ manzarası, sis, geniş açı, mavi saat",
    "vintage daktilo close-up, makro, sıcak ışık",
  ];
  return (
    <div className="wf" style={{ display: "flex", flexDirection: "column", height: "100%", background: "var(--bg)" }}>
      <EditorTopBarE title={SAMPLE_SETUP.projectName} />

      <main style={{ flex: 1, display: "flex", padding: "20px 24px 16px", gap: 16, minHeight: 0 }}>
        <section style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
          <div style={{ position: "relative", flex: 1, minHeight: 0 }}>
            <ImgPH style={{ width: "100%", height: "100%" }} label="scene 006 preview" />
            <div style={{ position: "absolute", top: 12, left: 12 }}>
              <Seq n={6} xl hl />
            </div>
          </div>
        </section>
        <SideComposer defaultValue={scenes[5]} editingSeq={6} />
      </main>

      {/* Custom footer in a drag-in-progress state */}
      <footer style={{
        background: "var(--bg)", borderTop: "1px solid var(--border)",
        padding: "10px 0 8px", display: "flex", flexDirection: "column", gap: 6, flexShrink: 0,
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, padding: "0 24px" }}>
          <Mono size={11} style={{ color: "var(--accent)", display: "inline-flex", alignItems: "center", gap: 6 }}>
            <Grip style={{ opacity: .9 }} /> 006 → 002 konumuna taşınıyor — bırakınca diğerleri yeniden numaralandırılır
          </Mono>
          <span style={{ flex: 1 }} />
          <Mono size={11} style={{ color: "var(--ink-3)", paddingLeft: 4 }}>006 / 006</Mono>
        </div>

        <div style={{ display: "flex", gap: 8, alignItems: "stretch", overflowX: "hidden", padding: "4px 24px", position: "relative" }}>
          <div style={{ display: "flex", gap: 8, paddingRight: 100, alignItems: "flex-start" }}>
            <TimelineCard n={1} prompt={scenes[0]} />

            {/* insertion indicator where the dragged card will land */}
            <div style={{ position: "relative", width: 0, flexShrink: 0, alignSelf: "stretch" }}>
              <div style={{
                position: "absolute", top: -2, bottom: -2, left: -4, width: 3,
                background: "var(--accent)", borderRadius: 2,
                boxShadow: "0 0 0 3px rgba(167,139,250,.18)",
              }} />
            </div>

            {/* dragged card, lifted: rotated, shadow, grabbing. Shows its new number 002 */}
            <div className="wf-card" style={{
              width: 160, flexShrink: 0, padding: 6, display: "flex", flexDirection: "column", gap: 6,
              borderColor: "var(--accent)", borderWidth: 1,
              background: "var(--bg-3)",
              boxShadow: "0 14px 28px rgba(0,0,0,.5), 0 0 0 1px var(--accent)",
              transform: "translateY(-10px) rotate(-3deg)", cursor: "grabbing", zIndex: 3,
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                <span style={{ display: "inline-flex", alignItems: "center", gap: 4 }}>
                  <Seq n={6} style={{ textDecoration: "line-through", opacity: .5 }} />
                  <span style={{ color: "var(--accent)", display: "inline-flex" }}><Icon.Right /></span>
                  <Seq n={2} hl />
                </span>
                <span style={{ flex: 1 }} />
                <Grip style={{ opacity: 1, cursor: "grabbing" }} />
              </div>
              <ImgPH style={{ aspectRatio: "16/10", width: "100%" }} label="sc 006" />
            </div>

            {/* remaining cards keep their old numbers until drop; dimmed to read as 'shifting' */}
            <TimelineCard n={2} prompt={scenes[1]} dim />
            <TimelineCard n={3} prompt={scenes[2]} dim />
            <TimelineCard n={4} prompt={scenes[3]} dim />
            <TimelineCard n={5} prompt={scenes[4]} dim />

            {/* gap left behind where 006 was lifted from */}
            <div style={{
              width: 160, flexShrink: 0, alignSelf: "stretch",
              border: "1px dashed var(--border-strong)", borderRadius: "var(--r-md)",
              background: "repeating-linear-gradient(135deg, transparent, transparent 6px, rgba(255,255,255,.02) 6px, rgba(255,255,255,.02) 12px)",
              display: "flex", alignItems: "center", justifyContent: "center",
            }}>
              <Mono size={10} style={{ color: "var(--ink-3)" }}>boş yer</Mono>
            </div>
          </div>
        </div>

        <div style={{ padding: "0 24px" }}>
          <FauxScrollbar progress={0.05} thumb={0.5} marks={6} />
        </div>
      </footer>
    </div>
  );
};

const ArtboardE_AddScene = () => {
  const scenes = [
    "gün batımında deniz kenarında oturan kadın, sıcak tonlar, film grain",
    "kahve fincanı, ahşap masa, soft ışık, üstten görünüm",
    "neon ışıklı dar sokak, yağmur, yansımalar, gece",
    "minimal beyaz oda, tek sandalye, doğal ışık",
    "dağ manzarası, sis, geniş açı, mavi saat",
    "vintage daktilo close-up, makro, sıcak ışık",
    "köpek koşuyor sahilde, hareket bulanıklığı",
    "kütüphane, kitap rafları, perspektif",
    "boğaz, vapur, sabah",
    "rıhtım, balıkçı, vinil doku",
    "tramvay durağı, yağmur damlaları",
    "çatı katı, gün doğumu, panorama",
  ];
  return (
    <div className="wf" style={{ display: "flex", flexDirection: "column", height: "100%", background: "var(--bg)" }}>
      <EditorTopBarE title={SAMPLE_SETUP.projectName} />

      <main style={{ flex: 1, display: "flex", padding: "20px 24px 16px", gap: 16, minHeight: 0 }}>
        <section style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
          <div className="wf-stroke wf-stroke--dashed" style={{
            flex: 1, background: "var(--bg-2)",
            display: "flex", alignItems: "center", justifyContent: "center",
          }}>
            <Mono size={11} style={{ color: "var(--ink-3)" }}>preview</Mono>
          </div>
        </section>

        <SideComposer defaultValue="" />
      </main>

      <TimelineFooter scenes={scenes} selectedIdx={-1} addSelected scrollProgress={0.45} thumb={0.45} />
    </div>
  );
};

const ArtboardE_Generating = () => {
  const scenes = [
    "gün batımında deniz kenarında oturan kadın, sıcak tonlar",
    "kahve fincanı, ahşap masa, soft ışık",
    "neon ışıklı dar sokak, yağmur, yansımalar",
    "minimal beyaz oda, tek sandalye, doğal ışık",
    "dağ manzarası, sis, geniş açı",
    "vintage daktilo close-up, makro",
    "köpek koşuyor sahilde",
    "kütüphane, kitap rafları",
    "boğaz, vapur, sabah",
    "rıhtım, balıkçı, vinil doku",
  ];
  const selectedIdx = scenes.length; // the new one being generated
  return (
    <div className="wf" style={{ display: "flex", flexDirection: "column", height: "100%", background: "var(--bg)" }}>
      <EditorTopBarE title={SAMPLE_SETUP.projectName} />

      <main style={{ flex: 1, display: "flex", padding: "20px 24px 16px", gap: 16, minHeight: 0 }}>
        <section style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
          <div style={{ position: "relative", flex: 1, minHeight: 0 }}>
            <ImgPH loading style={{ width: "100%", height: "100%" }} />
            <div style={{ position: "absolute", top: 12, left: 12 }}>
              <Seq n={selectedIdx + 1} xl hl />
            </div>
          </div>
        </section>

        <SideComposer disabled generating defaultValue="eski kütüphane, toz, ışık huzmesi" editingSeq={selectedIdx + 1} />
      </main>

      <TimelineFooter scenes={scenes} selectedIdx={selectedIdx} loadingAtEnd scrollProgress={0.55} thumb={0.4} />
    </div>
  );
};

// Delete confirm overlay — shown when user clicks trash on a scene preview.
// Compact danger dialog. Shows what will be deleted + how subsequent scenes
// renumber after delete.
const ArtboardE_DeleteConfirm = () => {
  const scenes = [
    "gün batımında deniz kenarında oturan kadın, sıcak tonlar, film grain",
    "kahve fincanı, ahşap masa, soft ışık, üstten görünüm",
    "neon ışıklı dar sokak, yağmur, yansımalar, gece",
    "minimal beyaz oda, tek sandalye, doğal ışık",
    "dağ manzarası, sis, geniş açı, mavi saat",
  ];
  const n = 3; // deleting scene 003
  return (
    <div className="wf" style={{ display: "flex", flexDirection: "column", height: "100%", background: "var(--bg)", position: "relative", overflow: "hidden" }}>
      {/* Faded editor underneath */}
      <div style={{ filter: "blur(2px)", opacity: .5, display: "flex", flexDirection: "column", height: "100%" }}>
        <EditorTopBarE title={SAMPLE_SETUP.projectName} />
        <main style={{ flex: 1, display: "flex", padding: "20px 24px 16px", gap: 16, minHeight: 0 }}>
          <section style={{ flex: 1, display: "flex", flexDirection: "column", minWidth: 0 }}>
            <div style={{ position: "relative", flex: 1, minHeight: 0 }}>
              <ImgPH style={{ width: "100%", height: "100%" }} label={`scene ${n}`} />
              <div style={{ position: "absolute", top: 12, left: 12 }}>
                <Seq n={n} xl hl />
              </div>
            </div>
          </section>
          <SideComposer defaultValue={scenes[n - 1]} />
        </main>
      </div>

      <div className="wf-scrim">
        <div className="wf-card" style={{
          width: 460,
          padding: 20, display: "flex", flexDirection: "column", gap: 14,
          background: "var(--bg-2)",
          borderColor: "var(--danger)",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <span style={{
              padding: "2px 6px",
              border: "1px solid var(--danger)",
              borderRadius: 3,
              color: "var(--danger)",
              fontFamily: "IBM Plex Mono, monospace",
              fontSize: 11,
              fontWeight: 500,
              letterSpacing: ".05em",
            }}>{String(n).padStart(3, "0")}</span>
            <Hand size={20}>Sahneyi sil?</Hand>
          </div>

          <Note size={13} style={{ color: "var(--ink-2)" }}>
            <Mono size={12} style={{ color: "var(--ink)" }}>{String(n).padStart(3, "0")}</Mono> numaralı sahne silinecek. Emin misin?
          </Note>

          <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
            <Btn>Vazgeç</Btn>
            <span style={{ flex: 1 }} />
            <Btn style={{
              background: "var(--danger)",
              color: "var(--bg)",
              borderColor: "var(--danger)",
            }}><Icon.Trash /> Sil</Btn>
          </div>
        </div>
      </div>
    </div>
  );
};

window.ArtboardE_SetupDone = ArtboardE_SetupDone;
window.ArtboardE_Editor = ArtboardE_Editor;
window.ArtboardE_Reorder = ArtboardE_Reorder;
window.ArtboardE_AddScene = ArtboardE_AddScene;
window.ArtboardE_Generating = ArtboardE_Generating;
window.ArtboardE_DeleteConfirm = ArtboardE_DeleteConfirm;
