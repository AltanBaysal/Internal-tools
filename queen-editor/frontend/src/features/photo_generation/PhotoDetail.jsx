import { useEffect, useState } from "react";

import { fileUrl } from "../../shared/api.js";
import { navigate, photoPath, projectPath } from "../../shared/router.js";
import ConfirmModal from "../../shared/ConfirmModal.jsx";
import { StatusErrorCard } from "../../shared/StatusErrorCard.jsx";
import { Btn, Hand, Icon, Mono, Note } from "../../vendor/kit.jsx";
import { Corner, Pill, Rendering, StatusPill } from "./frame_status.jsx";
import { PlayGlyph, SoundGlyph } from "./glyphs.jsx";
import { lostLayers } from "./layer_words.js";
import LayerPlayer from "./LayerPlayer.jsx";
import { LINKED, MODES, STANDARD, labelOf, nounOf } from "./production_modes.js";
import { useGeneration } from "./useGeneration.js";

// minmax(0, …) rather than plain columns: a long project or file name would otherwise widen the
// bar past the window and take the whole page sideways with it (madde 107).
const HEADER = {
  display: "grid", alignItems: "center",
  gridTemplateColumns: "minmax(0, 1fr) minmax(0, auto) minmax(0, 1fr)",
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
// What a layer is called inside a sentence. Read off the tabs rather than written a second time:
// the window that says a video could not be deleted and the tab it was deleted from must not end up
// calling the same layer two different things.
const LAYER_LABEL = Object.fromEntries(TABS.map((row) => [row.id, row.label]));

const STRIP = { position: "absolute", top: 16, left: "50%", transform: "translateX(-50%)",
                display: "flex", zIndex: 2 };

// The one destructive thing a layer tab offers (madde 80): it takes its own layer and whatever
// lies over it, and says what survives. The photo tab is not here -- deleting the base layer is
// deleting the frame, and that window counts the frame's layers instead of naming one.
const DESTRUCTIVE = {
  video: { label: "Videoyu sil — kare kalır", title: "Video silinsin mi?",
           body: "Bu video ve üzerindeki ses kalıcı olarak silinir — bu geri alınamaz. "
                 + "Kare ve fotoğrafı galeride kalır." },
  audio: { label: "Sesi sil — video kalır", title: "Ses silinsin mi?",
           body: "Bu ses kalıcı olarak silinir — bu geri alınamaz. Video ve kare kalır; "
                 + "video sessiz oynar." },
};
// Red text, red border, no fill -- the app-wide destructive standard (madde 83).
const DANGER = { color: "var(--danger)", borderColor: "var(--danger)", background: "none",
                 justifyContent: "center" };

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
      <Mono size={10} data-field style={LABEL}>{label}</Mono>
      <Mono size={13} style={{ color: muted ? "var(--ink-4)" : "var(--ink)" }}>{value}</Mono>
    </div>
  );
}

// Prompt and negative are the same block twice: both take an equal share of whatever the two small
// fields leave behind, and each scrolls inside itself so a long negative cannot squeeze the prompt.
//
// `hint` is what an empty box says when the emptiness has a reason -- a layer nobody has written
// the words for yet (madde 81). It is centred while a real prompt is not: a prompt is read from the
// left, an absence is a notice and stands in the middle of the box (Fark 92). Without a hint an
// empty box says "—", because an empty negative is an answer of its own.
function TextBlock({ label, text, hint }) {
  const empty = !text;
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 6, flex: 1, minHeight: 0 }}>
      <Mono size={10} style={LABEL}>{label}</Mono>
      <div className="wf-stroke" style={{ flex: 1, minHeight: 0, overflowY: "auto", padding: 10 }}>
        {/* The box is drawn even with nothing in it: a box that came and went with the frame would
            make the column jump between frames -- and an empty one reads as a prompt somebody
            deleted, which is the whole reason the hint exists. */}
        <Note size={12} style={{ color: empty ? "var(--ink-4)" : "var(--ink-2)", display: "block",
                                 lineHeight: 1.6,
                                 ...(empty && hint ? { textAlign: "center" } : {}) }}>
          {empty ? (hint || "—") : text}
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
export default function PhotoDetail({ project, frame: fid }) {
  const { frames, current, currentLayer, error, removePhotos, removeLayer, regenerate,
          retry } = useGeneration(project);
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
  // What a refused request of ours was trying to do, as the heading over the server's own words.
  // Held as the sentence rather than a flag: the two actions on a layer fail differently and the
  // card must not say the wrong one.
  const [refusedAct, setRefusedAct] = useState(null);
  // What the video should be made in next. Untouched until the box is used, so the default can
  // follow the poll: null means this video's own mode, whatever the record last said it was.
  const [newMode, setNewMode] = useState(null);

  // By identity, never by file: a copy frame shows its source's picture, and the two of them are
  // different frames at different places in the sequence.
  const index = frames ? frames.findIndex((row) => row.id === fid) : -1;
  const frame = index >= 0 ? frames[index] : null;
  const previous = index > 0 ? frames[index - 1] : null;
  const next = frames && index >= 0 && index < frames.length - 1 ? frames[index + 1] : null;
  // Which layer the worker is holding on THIS frame, if any -- the one thing about a frame that
  // has no state on disk.
  const running = frame && frame.id === current ? (currentLayer || "photo") : null;
  // The photo layer's state is the frame's own: it is the frame.
  const state = running === "photo" ? "running" : frame?.status;
  const produced = state === "done";

  // What one layer is doing, or null when the frame never asked for it. One rule for the tab strip
  // and for what the open tab draws: a layer that blew up and one that is still coming both have
  // something to show (madde 79, 81).
  const stateOf = (layer) => {
    if (layer === "photo") return state;
    if (running === layer) return "running";
    if ((frame?.failed || []).includes(layer)) return "failed";
    if ((frame?.owed || []).includes(layer)) return "pending";
    return (frame?.layers || {})[layer] ? "done" : null;
  };
  // A tab opens for every layer that is in the plan, whatever became of it; one the frame never
  // asked for stays disabled rather than hidden -- what it could still become is worth seeing.
  const has = Object.fromEntries(LAYER_ORDER.map((layer) => [layer, stateOf(layer) !== null]));
  const openState = stateOf(open);
  // Only a layer that is really there can be made again, and only it can be edited.
  const holds = openState === "done";
  // Does removing this frame take a file off the disk? Only when the picture is its own: a copy
  // frame holds its source's, and a frame with nothing produced holds nothing at all (madde 101).
  const ownsItsPhoto = produced && frame.file === `${frame.id}.png`;
  // Is anything still coming for it? A frame in the queue is taken out of it; a red one is not in
  // it at all, so saying "kuyruktan çıkar" there would be a lie.
  const awaited = (frame?.owed || []).length > 0;
  // Which layer that is: the one the worker is on, or the first one still owed. The frame's own
  // answer rather than the open tab's, because it is the frame that is waiting.
  const coming = running || (frame?.owed || [])[0] || null;
  // What the layer was made from -- the frame's own words until the user types over them.
  const said = (frame?.prompts || {})[open] ?? (open === "photo" ? frame?.prompt : "") ?? "";
  const typed = words[open] ?? said;
  // How the open layer was made, when its line said so. Only a video has an answer today, and only
  // a produced one: a failed or deleted layer's latest line names no mode.
  const madeIn = (frame?.modes || {})[open];
  // Linked names the picture rather than the frame's number -- the sequence can be dragged, and a
  // number would then be a lie about a video nobody touched.
  const arrivesAt = (frame?.endsOn || {})[open];
  // The mode the form would send. This video's own until the box is touched (madde 94).
  const picked = newMode ?? madeIn ?? STANDARD;
  // The same question the server asks: the gallery's top is the film's last frame, and a next whose
  // picture has not landed is no target either. A sentence when linking is dead here, nothing when
  // it is alive -- the closing and its reason never come apart.
  const nextInFilm = index > 0 ? frames?.[index - 1] : null;
  const noTarget = picked === LINKED
    && (index === 0
      ? "Bu son kare — bağlanacak sonraki kare yok."
      : nextInFilm?.status === "done" ? null : "Sonraki karenin fotoğrafı henüz üretilmedi.");
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
    setRefusedAct(null);
    // The box belongs to the video behind it, so it goes with the frame.
    setNewMode(null);
  }, [fid]);

  useEffect(() => {
    const onKey = (e) => {
      if (confirming) return;                    // the modal owns the keyboard while it is open
      if (e.key === "Escape") navigate(projectPath(project));
      if (e.key === "ArrowLeft" && previous) navigate(photoPath(project, previous.id));
      if (e.key === "ArrowRight" && next) navigate(photoPath(project, next.id));
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
    return removePhotos([fid]).then((body) => {
      setBusy(false);
      setConfirming(false);
      // Refused: the frame is still there, so staying on it is the only honest thing to do.
      if (!body) return setRefused(true);
      navigate(after ? photoPath(project, after.id) : projectPath(project));
    });
  }

  // No confirm box and nowhere to go: the frame on screen keeps everything it has, and what was
  // asked for turns up in the gallery as a frame of its own (madde 77).
  function handleRegenerate() {
    setRefusedAct(null);
    const layer = open;
    // undefined off the video tab: a body with no mode is what the server has always read, and a
    // mode on a sound would be refused outright.
    return regenerate(frame.id, layer, typed, layer === "video" ? picked : undefined)
      .then((body) => {
        if (!body) return setRefusedAct("Kare yeniden üretilemedi");
        setSent((layers) => [...layers, layer]);
      });
  }

  // The red layer goes back into the queue on this very frame -- no copy, no new name (madde 68).
  // The page keeps showing red until the poll brings the frame back as a waiting one, which is why
  // the button remembers the press itself.
  function handleRetry() {
    const layer = open;
    setSent((sentLayers) => [...sentLayers, layer]);
    return retry(frame.id);
  }

  // The open tab's own layer, and whatever lies over it. The frame stays in the gallery, so the
  // page stays on it -- only the tab it was showing is gone, and the photo is always there.
  function handleRemoveLayer() {
    setBusy(true);
    setRefusedAct(null);
    const layer = open;
    return removeLayer([frame.id], layer).then((body) => {
      setBusy(false);
      setConfirming(false);
      if (!body) return setRefusedAct(`${LAYER_LABEL[layer]} silinemedi`);
      setOpen("photo");
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
          <StatusErrorCard text="Kare bulunamadı" raw={error || fid} />
        </div>
      ) : (
        <div style={{ flex: 1, display: "flex", minHeight: 0 }}>
          <div style={STAGE}>
            <LayerTabs open={open} has={has} onOpen={setOpen} />
            {/* The corner label the gallery uses, with this page's own sentence: the queue took the
                job, and what it makes will be a frame of its own rather than this one changing. */}
            {sent.length > 0 ? (
              <Corner><Pill color="var(--accent)">yeniden üretilecek — kuyrukta</Pill></Corner>
            ) : coming ? (
              /* What the frame is waiting for, in the gallery's own words. A copy frame's page is
                 full of its source's picture, and this is the only thing that says the video is
                 still coming (madde 81). A failed layer gets no pill: the stage says that across
                 its whole width. */
              <Corner>
                <StatusPill layer={coming} state={running ? "running" : "pending"} />
              </Corner>
            ) : null}
            <Arrow glyph="‹" side="left"
                   onClick={previous
                     ? () => navigate(photoPath(project, previous.id))
                     : undefined} />
            <Arrow glyph="›" side="right"
                   onClick={next ? () => navigate(photoPath(project, next.id)) : undefined} />
            {holds && open !== "photo" ? (
              /* The layer's own tab plays it. The sound opens no player of its own: it rides the
                 video, which is what "sesli oynar" means here (madde 74). */
              <LayerPlayer videoUrl={fileUrl(project, frame.layers.video)}
                           audioUrl={open === "audio"
                             ? fileUrl(project, frame.layers.audio)
                             : null} />
            ) : openState === "running" ? (
              <Rendering style={HOLDER} />
            ) : openState === "failed" ? (
              /* Madde 79: red border, red ground, and the renderer's own sentence under the two
                 words -- the one place the reason is readable. */
              <div className="wf-img" style={{ ...HOLDER, borderColor: "var(--danger)",
                                               background: "var(--danger-bg)",
                                               backgroundImage: "none", padding: 24 }}>
                <span style={{ color: "var(--danger)" }}><Icon.Warn /></span>
                <Mono size={12} style={{ color: "var(--danger)" }}>Bu kare üretilemedi</Mono>
                {(frame.errors || {})[open] && (
                  <Note size={12} style={{ color: "var(--ink-2)", textAlign: "center",
                                           lineHeight: 1.5 }}>
                    {frame.errors[open]}
                  </Note>
                )}
              </div>
            ) : produced ? (
              /* The picture the frame holds -- its own, or its source's when this is a copy waiting
                 for the layer above it (madde 81). contain, not a fixed ratio: the server does not
                 know the photo's shape and it is never cropped. 120px is the arrow gutter. */
              <img src={fileUrl(project, frame.file)} alt={frame.file}
                   style={{ maxWidth: "calc(100% - 120px)", maxHeight: "100%", width: "auto",
                            height: "auto", objectFit: "contain", display: "block" }} />
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
              {/* The frame's own name, on every tab. The design took this row away too; it was put
                  back because the page's header carries the project's name and not the frame's, so
                  this is the only place the identity appears at all (karar 23). The layers' own
                  file names are what really went. With nothing on disk yet the name is a plan. */}
              <Field label={produced ? "Dosya adı" : "Dosya adı (planlanan)"}
                     value={(frame.layers || {}).photo || frame.file}
                     muted={!produced} />
              {open === "video" && madeIn && (
                /* Information, never a control: changing the mode is making the video again, and
                   that is the form further down (madde 94). */
                <Field label="Üretim modu"
                       value={madeIn === LINKED && arrivesAt
                         ? `${labelOf(madeIn)} → ${arrivesAt}`
                         : labelOf(madeIn)} />
              )}
            </div>

            {/* The open layer's own prompt, and nothing under it: what a layer was made from is no
                longer this page's to show (madde 87). */}
            {holds ? (
              <PromptBox label="Prompt" value={typed} changed={changed}
                         onChange={(text) => setWords((kept) => ({ ...kept, [open]: text }))} />
            ) : (
              <TextBlock label="Prompt"
                         text={(frame.prompts || {})[open]
                               ?? (open === "photo" ? frame.prompt : "")}
                         // A layer still in the queue has no words yet, and nobody typed the
                         // missing ones. Not the photo's: those words are the user's own, so a
                         // notice about a prompt nobody has written would be false there.
                         hint={openState === "pending" && open !== "photo"
                           ? "Prompt yok — üretim sırası geldiğinde eklenecek."
                           : null} />
            )}
            {/* The negative belongs to the photo alone: video and sound jobs carry none. It stays
                read-only: the design gives the user the prompt, not the whole submission. */}
            {open === "photo" && <TextBlock label="Negatif" text={frame.negative} />}

            {holds && open === "video" && (
              /* Only a video arrives at a picture, so only its form has this to ask. */
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                <Mono size={10} style={LABEL} id="yeni-mod">Yeni mod</Mono>
                <select className="wf-input" aria-labelledby="yeni-mod" value={picked}
                        onChange={(e) => setNewMode(e.target.value)}
                        style={{ fontSize: 12.5, color: "var(--ink)", cursor: "pointer",
                                 // Danger first: a box that cannot be pressed through must not look
                                 // like an ordinary change.
                                 borderColor: noTarget ? "var(--danger)"
                                   : picked !== (madeIn ?? STANDARD) ? "var(--accent)" : undefined }}>
                  {MODES.map((one) => (
                    <option key={one.id} value={one.id}>{one.label}</option>
                  ))}
                </select>
                {noTarget && <Note size={12} style={{ color: "var(--danger)" }}>{noTarget}</Note>}
              </div>
            )}

            {holds && (
              /* Accent whether the prompt was touched or not (madde 78): making the frame again is
                 what this page is for, and a changed prompt only decides the new frame's name. */
              <Btn sm hl disabled={sent.includes(open) || Boolean(noTarget)}
                   onClick={handleRegenerate} style={{ justifyContent: "center" }}>
                {sent.includes(open)
                  ? "Kuyruğa eklendi"
                  : <><Icon.Regen /> Yeniden üret — yeni kare</>}
              </Btn>
            )}
            {holds && open === "video" && (
              /* What one press opens, in the mode's own words: a copy frame beside this one, never
                 a video written over the one that is here (madde 77). */
              <Note size={12} style={{ color: "var(--ink-3)", textAlign: "center" }}>
                Yeni bir kare açılır — {frame.id} kopyası, {nounOf(picked, "video")}.
              </Note>
            )}
            {openState === "failed" && (
              /* The way back from a red layer, on the page it is read (madde 79). Retrying makes no
                 new frame -- it is the one exception to "üret = ekle" -- so it asks nothing and
                 only says the queue took it. */
              <Btn sm hl disabled={sent.includes(open)} onClick={handleRetry}
                   style={{ justifyContent: "center" }}>
                {sent.includes(open) ? "Kuyruğa eklendi" : <><Icon.Regen /> Tekrar dene</>}
              </Btn>
            )}

            {refusedAct && <StatusErrorCard text={refusedAct} raw={error} />}
            {refused && (
              <StatusErrorCard text={produced ? "Kare silinemedi" : "Kare kuyruktan çıkarılamadı"}
                               raw={error} />
            )}

            {/* One destructive button per tab (madde 80): the frame on the photo tab, the layer on
                the others. Only a frame whose picture is its own loses a file, and only that one
                asks first; the other two say which of the frame's two ends it is at. */}
            {open === "photo" ? (
              <Btn sm disabled={busy || state === "running"}
                   onClick={ownsItsPhoto ? () => setConfirming(true) : handleRemove}
                   style={DANGER}>
                <Icon.Trash /> {ownsItsPhoto ? "Sil" : (awaited ? "Kuyruktan çıkar" : "Kareyi sil")}
              </Btn>
            ) : holds && (
              <Btn sm disabled={busy} onClick={() => setConfirming(true)} style={DANGER}>
                <Icon.Trash /> {DESTRUCTIVE[open].label}
              </Btn>
            )}
          </div>
        </div>
      )}

      {confirming && (open === "photo" ? (
        <ConfirmModal title="Bu kare silinsin mi?"
                      // A live list: the frame can vanish under an open window, and an empty
                      // list is a sentence that promises nothing rather than a crash.
                      body={lostLayers(frame ? [frame] : []) + "Bu işlem geri alınamaz."}
                      confirmLabel="Sil" busyLabel="Siliniyor…" danger busy={busy}
                      onCancel={() => setConfirming(false)} onConfirm={handleRemove} />
      ) : (
        // Wider than the frame's own window (madde 80): these two say what survives the deletion,
        // and that sentence does not fit 320.
        <ConfirmModal title={DESTRUCTIVE[open].title} body={DESTRUCTIVE[open].body} width={400}
                      confirmLabel="Sil" busyLabel="Siliniyor…" danger busy={busy}
                      onCancel={() => setConfirming(false)} onConfirm={handleRemoveLayer} />
      ))}
    </div>
  );
}
