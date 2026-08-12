import { useEffect, useState } from "react";

import { fileUrl } from "../../shared/api.js";
import { navigate, photoPath, projectPath } from "../../shared/router.js";
import ConfirmModal from "../../shared/ConfirmModal.jsx";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Btn, Hand, Icon, Mono, Note } from "../../vendor/kit.jsx";
import { Pill, Rendering } from "./frame_status.jsx";
import { PlayGlyph, SoundGlyph } from "./glyphs.jsx";
import LayerPlayer from "./LayerPlayer.jsx";
import { useGeneration } from "./useGeneration.js";

const HEADER = {
  display: "grid", gridTemplateColumns: "1fr auto 1fr", alignItems: "center",
  padding: "14px 32px", background: "var(--bg-2)", borderBottom: "1px solid var(--border)",
};
const STAGE = {
  flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: 24,
  position: "relative", background: "var(--bg)", minHeight: 0,
};
// The design's arrows: plain glyphs at the two ends of the photo area, glowing enough to stay
// legible over any photo.
const ARROW = {
  position: "absolute", top: "50%", transform: "translateY(-50%)", color: "#fff", fontSize: 44,
  lineHeight: 1, fontWeight: 300, textShadow: "0 0 4px rgba(0,0,0,.9), 0 2px 8px rgba(0,0,0,.7)",
  userSelect: "none",
};
const SIDE = {
  width: 300, flexShrink: 0, borderLeft: "1px solid var(--border)", padding: 16,
  display: "flex", flexDirection: "column", gap: 14, boxSizing: "border-box", minHeight: 0,
};
const LABEL = { color: "var(--ink-3)", letterSpacing: ".08em", textTransform: "uppercase" };
// A frame with no photo yet still has to hold the stage: a square the height of the area, inside
// the same 120px arrow gutter the photo keeps clear.
const HOLDER = {
  height: "100%", aspectRatio: "1/1", maxWidth: "calc(100% - 120px)", boxSizing: "border-box",
  display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", gap: 8,
};

function Arrow({ glyph, side, onClick }) {
  // No handler means there is nowhere to go: the design says the ends do not wrap around, so the
  // arrow is dimmed rather than hidden -- the two ends stay where the eye expects them.
  const enabled = Boolean(onClick);
  return (
    <div role="button" onClick={onClick}
         style={{ ...ARROW, [side]: 20, cursor: enabled ? "pointer" : "default",
                  opacity: enabled ? 1 : 0.25 }}>
      {glyph}
    </div>
  );
}

// Madde 73's strip: three joined buttons over the stage. A layer the frame does not have stays
// disabled rather than hidden -- the user sees what a frame could still become.
const TABS = [
  { id: "photo", label: "Foto" },
  { id: "video", label: "Video", Glyph: PlayGlyph },
  { id: "audio", label: "Ses", Glyph: SoundGlyph },
];
const LAYER_ORDER = TABS.map((row) => row.id);
// What each layer's own file and prompt are called in the column.
const LAYER_WORD = { photo: "Foto", video: "Video", audio: "Ses" };

const STRIP = { position: "absolute", top: 16, left: "50%", transform: "translateX(-50%)",
                display: "flex", zIndex: 2 };

function LayerTabs({ open, has, onOpen }) {
  return (
    <div style={STRIP}>
      {TABS.map(({ id, label, Glyph }, index) => (
        <button key={id} type="button" disabled={!has[id]}
                aria-current={open === id ? "page" : undefined}
                onClick={() => onOpen(id)} className="wf-stroke"
                style={{ display: "flex", alignItems: "center", gap: 4, padding: "4px 10px",
                         background: "var(--bg-2)", cursor: has[id] ? "pointer" : "default",
                         opacity: has[id] ? 1 : 0.35,
                         color: open === id ? "var(--accent)" : "var(--ink-3)",
                         borderColor: open === id ? "var(--accent)" : "var(--border)",
                         // Joined, not three separate pills: one control with three states.
                         marginLeft: index ? -1 : 0 }}>
          {Glyph && <Glyph size={10} />}
          <Mono size={10}>{label}</Mono>
        </button>
      ))}
    </div>
  );
}

function Field({ label, value, muted }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
      <Mono size={10} style={LABEL}>{label}</Mono>
      <Mono size={13} style={{ color: muted ? "var(--ink-4)" : "var(--ink)" }}>{value}</Mono>
    </div>
  );
}

// Prompt and negative are the same block twice: both take an equal share of whatever the two small
// fields leave behind, and each scrolls inside itself so a long negative cannot squeeze the prompt.
function TextBlock({ label, text }) {
  const empty = !text;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1, minHeight: 0 }}>
      <Mono size={10} style={LABEL}>{label}</Mono>
      <div className="wf-stroke" style={{ flex: 1, minHeight: 0, overflowY: "auto", padding: 10 }}>
        {/* The box is drawn even with nothing in it: an empty negative is an answer, and a box that
            came and went with the frame would make the column jump between frames. */}
        <Note size={12} style={{ color: empty ? "var(--ink-4)" : "var(--ink-2)", display: "block",
                                 lineHeight: 1.6 }}>
          {empty ? "—" : text}
        </Note>
      </div>
    </div>
  );
}

// The open layer's own prompt, in the user's hands. Only this one box is writable: what is sent is
// the open layer's prompt alone, and a box under it that changed nothing would be a lie.
//
// Nothing is saved. The words live on screen until they are made into a frame or the frame is left
// (madde 76) -- a stored draft is a concept the design never asked for.
function PromptBox({ label, value, changed, onChange }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1, minHeight: 0 }}>
      <Mono size={10} style={LABEL}>{label}</Mono>
      <textarea className="wf-stroke wf-note" value={value} onChange={(e) => onChange(e.target.value)}
                style={{ flex: 1, minHeight: 0, overflowY: "auto", padding: 10, resize: "none",
                         background: "transparent", color: "var(--ink-2)", fontSize: 12,
                         lineHeight: 1.6,
                         // The accent says one thing: pressing now makes a NEW prompt rather than
                         // another variant of this one. Space around the words is not that.
                         borderColor: changed ? "var(--accent)" : undefined }} />
    </div>
  );
}

// Artboard 10: the frame as large as it fits, between two arrows; the 300px column on the right
// says where it sits, what it is called and what it was asked to be. Every frame in the gallery
// opens here -- produced, waiting, being rendered or failed -- and the page is live, so the one the
// worker is holding turns into its photo without a reload.
export default function PhotoDetail({ project, file }) {
  const { frames, current, currentLayer, error, removePhotos, regenerate } = useGeneration(project);
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  // Which layer is open. The photo to begin with: it is the frame itself, and the others are what
  // was laid over it.
  const [open, setOpen] = useState("photo");
  // Only a removal of ours puts the card on screen: the hook's error is also where a failed poll
  // lands, and that one has nothing to do with this frame.
  const [refused, setRefused] = useState(false);
  // What the user has typed, per layer. An untouched layer is absent rather than empty: that is
  // what lets the box fall back to the frame's own words as the poll refreshes them.
  const [words, setWords] = useState({});
  // The layers already sent off to be made again. Their result is a frame of its own, so this page
  // will never see it land -- the button has to remember the press itself.
  const [sent, setSent] = useState([]);
  const [refusedLayer, setRefusedLayer] = useState(false);

  const index = frames ? frames.findIndex((frame) => frame.file === file) : -1;
  const frame = index >= 0 ? frames[index] : null;
  const previous = index > 0 ? frames[index - 1] : null;
  const next = frames && index >= 0 && index < frames.length - 1 ? frames[index + 1] : null;
  // The frame being rendered has no state on disk -- the live worker's file name is what says so,
  // exactly as in the gallery. Only a photo render empties the page: a frame whose video is being
  // made still has its picture.
  const state = frame && frame.file === current && (currentLayer || "photo") === "photo"
    ? "running"
    : frame?.status;
  const produced = state === "done";

  // What the frame really holds: a layer that blew up occupies its slot but is not something the
  // frame has, so its tab stays shut.
  const has = Object.fromEntries(LAYER_ORDER.map((layer) => [
    layer,
    Boolean((frame?.layers || {})[layer]) && !(frame?.failed || []).includes(layer),
  ]));
  // Every layer up to the open one: the column shows their file names, then the open layer's own
  // prompt, then the ones under it (madde 75).
  const shown = LAYER_ORDER.slice(0, LAYER_ORDER.indexOf(open) + 1);
  // Is the open layer really there? The photo tab needs no answer from `layers`: a produced frame
  // IS its photo. Only a layer that exists can be made again, and only it can be edited.
  const holds = open === "photo" ? produced : has[open];
  // What the layer was made from -- the frame's own words until the user types over them.
  const said = (frame?.prompts || {})[open] ?? (open === "photo" ? frame?.prompt : "") ?? "";
  const typed = words[open] ?? said;
  // Compared trimmed, exactly as the server compares it: what the accent border promises and what
  // the new frame's name turns out to be must be the same answer (madde 99).
  const changed = typed.trim() !== said.trim();

  // The arrows swap the frame under a page that stays mounted, so anything said about the old one
  // has to go with it -- a refusal card from the previous frame would read as this one's, and a
  // tab it does not have would be open on a frame that never had that layer.
  useEffect(() => {
    setRefused(false);
    setConfirming(false);
    setBusy(false);
    setOpen("photo");
    // The editing belonged to that frame, and so did the presses: both go with it.
    setWords({});
    setSent([]);
    setRefusedLayer(false);
  }, [file]);

  useEffect(() => {
    const onKey = (e) => {
      if (confirming) return;                    // the modal owns the keyboard while it is open
      if (e.key === "Escape") navigate(projectPath(project));
      if (e.key === "ArrowLeft" && previous) navigate(photoPath(project, previous.file));
      if (e.key === "ArrowRight" && next) navigate(photoPath(project, next.file));
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [project, previous, next, confirming]);

  // One button, two meanings: a photo is deleted from Drive and asks first, a frame only leaves the
  // queue and does not. Where to go afterwards is decided before the list changes -- the next frame,
  // the one before it when this was the last, or the gallery when nothing is left.
  function handleRemove() {
    setBusy(true);
    setRefused(false);
    const after = next || previous;
    return removePhotos([file]).then((body) => {
      setBusy(false);
      setConfirming(false);
      // Refused: the frame is still there, so staying on it is the only honest thing to do.
      if (!body) return setRefused(true);
      navigate(after ? photoPath(project, after.file) : projectPath(project));
    });
  }

  // No confirm box and nowhere to go: the frame on screen keeps everything it has, and what was
  // asked for turns up in the gallery as a frame of its own (madde 77).
  function handleRegenerate() {
    setRefusedLayer(false);
    const layer = open;
    return regenerate(file, layer, typed).then((body) => {
      if (!body) return setRefusedLayer(true);
      setSent((layers) => [...layers, layer]);
    });
  }

  return (
    <div style={{ display: "flex", flexDirection: "column", height: "100vh" }}>
      <div style={HEADER}>
        <Hand size={20}><span className="wf-hl">Queen Editor</span></Hand>
        <Hand size={20}>{project}</Hand>
        <Btn ghost style={{ justifySelf: "end" }} onClick={() => navigate(projectPath(project))}>
          <Icon.Left /> Galeriye dön
        </Btn>
      </div>

      {frames === null ? (
        <div style={STAGE}><span className="wf-spinner" /></div>
      ) : !frame ? (
        // Not one of the three states the design draws, but a fourth thing: an address that names
        // no frame at all -- a deleted one's old link, or a hand-typed URL.
        <div style={{ ...STAGE, flexDirection: "column", gap: 12 }}>
          <StatusErrorCard text="Fotoğraf bulunamadı" raw={error || file} />
        </div>
      ) : (
        <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
          <div style={STAGE}>
            <LayerTabs open={open} has={has} onOpen={setOpen} />
            {/* The corner label the gallery uses, with this page's own sentence: the queue took the
                job, and what it makes will be a frame of its own rather than this one changing. */}
            {sent.length > 0 && (
              <Pill color="var(--accent)">yeniden üretilecek — kuyrukta</Pill>
            )}
            <Arrow glyph="‹" side="left"
                   onClick={previous
                     ? () => navigate(photoPath(project, previous.file))
                     : undefined} />
            <Arrow glyph="›" side="right"
                   onClick={next ? () => navigate(photoPath(project, next.file)) : undefined} />
            {produced && open !== "photo" ? (
              /* The layer's own tab plays it. The sound opens no player of its own: it rides the
                 video, which is what "sesli oynar" means here (madde 74). */
              <LayerPlayer videoUrl={fileUrl(project, frame.layers.video)}
                           audioUrl={open === "audio"
                             ? fileUrl(project, frame.layers.audio)
                             : null} />
            ) : produced ? (
              /* contain, not a fixed ratio: the server does not know the photo's shape, and the
                 design's rule is that it is never cropped. 120px is the design's own arrow gutter. */
              <img src={fileUrl(project, frame.file)} alt={frame.file}
                   style={{ maxWidth: "calc(100% - 120px)", maxHeight: "100%", width: "auto",
                            height: "auto", objectFit: "contain", display: "block" }} />
            ) : state === "running" ? (
              <Rendering style={HOLDER} />
            ) : state === "failed" ? (
              <div className="wf-img" style={{ ...HOLDER, borderStyle: "dashed",
                                               borderColor: "var(--danger)",
                                               background: "var(--danger-bg)",
                                               backgroundImage: "none" }}>
                <span style={{ color: "var(--danger)" }}><Icon.Warn /></span>
                <Mono size={12} style={{ color: "var(--danger)" }}>üretilemedi</Mono>
              </div>
            ) : (
              /* Madde 82: the holder keeps the frame's own shape and its two lines are drawn
                 faintly -- a frame with no pixels yet is not an error, only not here yet. */
              <div data-holder className="wf-img"
                   style={{ ...HOLDER, borderStyle: "dashed", opacity: 0.45 }}>
                <Mono size={12} style={{ color: "var(--ink-3)" }}>bekliyor</Mono>
                <Note size={12} style={{ color: "var(--ink-3)" }}>henüz üretilmedi</Note>
              </div>
            )}
          </div>

          <div style={SIDE}>
            <div style={{ display: "flex", gap: 24, flexWrap: "wrap" }}>
              {/* The same number the tile carries: the badge counts up from the bottom, so walking
                  down the gallery with › walks the counter down with it. */}
              <Field label="Sıra" value={`${frames.length - index} / ${frames.length}`} />
              {/* One row per layer up to the open tab. With only the photo on screen the row keeps
                  its old name -- and with nothing on disk yet it says the name is a plan. */}
              {shown.map((layer) => (
                <Field key={layer}
                       label={shown.length === 1
                         ? (produced ? "Dosya adı" : "Dosya adı (planlanan)")
                         : LAYER_WORD[layer]}
                       value={(frame.layers || {})[layer] || frame.file}
                       muted={layer === "photo" && !produced} />
              ))}
            </div>

            {/* The open layer's own prompt first, then the ones under it -- those are what it was
                made from, and this page never asks them to be changed (madde 75). */}
            {[...shown].reverse().map((layer) => (
              layer === open && holds ? (
                <PromptBox key={layer} label="Prompt" value={typed} changed={changed}
                           onChange={(text) => setWords((kept) => ({ ...kept, [layer]: text }))} />
              ) : (
                <TextBlock key={layer}
                           label={layer === open ? "Prompt" : `${LAYER_WORD[layer]} prompt`}
                           text={(frame.prompts || {})[layer]
                                 ?? (layer === "photo" ? frame.prompt : "")} />
              )
            ))}
            {/* The negative belongs to the photo alone: video and sound jobs carry none. It stays
                read-only: the design gives the user the prompt, not the whole submission. */}
            {open === "photo" && <TextBlock label="Negatif" text={frame.negative} />}

            {holds && (
              /* Accent whether the prompt was touched or not (madde 78): making the frame again is
                 what this page is for, and a changed prompt only decides the new frame's name. */
              <Btn sm hl disabled={sent.includes(open)} onClick={handleRegenerate}
                   style={{ justifyContent: "center" }}>
                {sent.includes(open)
                  ? "Kuyruğa eklendi"
                  : <><Icon.Regen /> Yeniden üret — yeni kare</>}
              </Btn>
            )}

            {refusedLayer && <StatusErrorCard text="Kare yeniden üretilemedi" raw={error} />}
            {refused && (
              <StatusErrorCard text={produced ? "Fotoğraf silinemedi" : "Kare kuyruktan çıkarılamadı"}
                               raw={error} />
            )}

            <Btn sm disabled={busy || state === "running"}
                 onClick={produced ? () => setConfirming(true) : handleRemove}
                 style={{ color: "var(--danger)", borderColor: "var(--danger)",
                          justifyContent: "center" }}>
              <Icon.Trash /> {produced ? "Sil" : "Kuyruktan çıkar"}
            </Btn>
          </div>
        </div>
      )}

      {confirming && (
        <ConfirmModal title="Bu fotoğraf silinsin mi?" body="Bu işlem geri alınamaz."
                      confirmLabel="Sil" busyLabel="Siliniyor…" danger busy={busy}
                      onCancel={() => setConfirming(false)} onConfirm={handleRemove} />
      )}
    </div>
  );
}
