import { useEffect, useRef, useState } from "react";

import { Mono } from "../../vendor/kit.jsx";
import { PauseGlyph, PlayGlyph } from "./glyphs.jsx";

// Madde 74's numbers: a 64px round button in the middle of a 16:9 stage, and a waveform of 46 bars
// where the sound rides along.
const BARS = 46;
// How far the sound may drift from the picture before it is pulled back. Below this nobody hears
// it, and correcting on every tick would make the sound stutter.
const DRIFT = 0.25;

const SCENE = { position: "relative", width: "100%", maxWidth: "calc(100% - 120px)",
                aspectRatio: "16/9", background: "#000", borderRadius: "var(--r-sm)",
                overflow: "hidden" };
// Fark 116: an outline and a darker ground, so the button reads as a button over any frame the
// video happens to be paused on. Written in longhands -- the shorthand is not reliably read back.
const BUTTON = { position: "absolute", top: "50%", left: "50%", transform: "translate(-50%,-50%)",
                 width: 64, height: 64, borderRadius: "50%",
                 borderWidth: 1, borderStyle: "solid", borderColor: "rgba(255,255,255,.35)",
                 background: "rgba(10,8,7,.72)", color: "#fff", cursor: "pointer",
                 display: "flex", alignItems: "center", justifyContent: "center", zIndex: 2 };
// Fark 114/115: the clock, the line and the waveform live inside the picture now, a little above
// its bottom edge, so the player reads as one thing rather than two stacked.
const TRACK = { position: "absolute", left: 12, right: 12, bottom: 10, zIndex: 1,
                display: "flex", alignItems: "center", gap: 10 };
// White with a shadow rather than the panel's faint ink: what is under these is a picture now, and
// a tone chosen for a flat surface disappears over half of them.
const CLOCK = { color: "#fff", textShadow: "0 1px 3px rgba(0,0,0,.8)" };
const UNPLAYED = "rgba(255,255,255,.35)";

/** m:ss -- the only shape a five second clip needs. */
function clock(seconds) {
  const whole = Math.max(0, Math.floor(seconds || 0));
  return `${Math.floor(whole / 60)}:${String(whole % 60).padStart(2, "0")}`;
}

/** The sound's own peaks, read from the file itself.
 *
 * Drawn from the wav rather than invented: a waveform that does not belong to the sound would be a
 * picture of nothing. Where the browser cannot decode -- or the file cannot be read -- the bars
 * stay flat and only the played part still says where the sound is.
 */
function useWaveform(audioUrl) {
  const [peaks, setPeaks] = useState(null);
  useEffect(() => {
    const Context = window.AudioContext || window.webkitAudioContext;
    if (!audioUrl || !Context) return undefined;
    let alive = true;
    fetch(audioUrl)
      .then((answer) => answer.arrayBuffer())
      .then((bytes) => new Context().decodeAudioData(bytes))
      .then((sound) => {
        if (!alive) return;
        const samples = sound.getChannelData(0);
        const per = Math.floor(samples.length / BARS) || 1;
        const read = [];
        for (let bar = 0; bar < BARS; bar += 1) {
          let peak = 0;
          for (let i = bar * per; i < (bar + 1) * per && i < samples.length; i += 1) {
            peak = Math.max(peak, Math.abs(samples[i]));
          }
          read.push(peak);
        }
        const loudest = Math.max(...read) || 1;
        setPeaks(read.map((peak) => peak / loudest));
      })
      .catch(() => {});
    return () => { alive = false; };
  }, [audioUrl]);
  return peaks;
}

// Artboard: the video in a 16:9 stage with one round button over it, and near its bottom edge the
// time, the progress and the time again -- all of it inside the picture (Fark 114). The sound tab
// opens no player of its own (madde 74) -- it is this same one with the wav playing alongside and a
// waveform where the bar was.
export default function LayerPlayer({ videoUrl, audioUrl }) {
  const video = useRef(null);
  const audio = useRef(null);
  const [playing, setPlaying] = useState(false);
  const [at, setAt] = useState(0);
  const [length, setLength] = useState(0);
  const peaks = useWaveform(audioUrl);

  // A tab change swaps the source under a mounted player: whatever was playing does not carry over.
  useEffect(() => { setPlaying(false); setAt(0); }, [videoUrl, audioUrl]);

  function toggle() {
    const shown = video.current;
    if (!shown) return;
    if (playing) {
      shown.pause();
      if (audio.current) audio.current.pause();
      return;
    }
    if (audio.current) {
      audio.current.currentTime = shown.currentTime;
      audio.current.play();
    }
    shown.play();
  }

  function onTime() {
    const shown = video.current;
    if (!shown) return;
    setAt(shown.currentTime);
    // The video loops on its own; the sound has to be told, and a drift the ear would catch is
    // pulled back to where the picture is.
    if (audio.current && Math.abs(audio.current.currentTime - shown.currentTime) > DRIFT) {
      audio.current.currentTime = shown.currentTime;
    }
  }

  const done = length ? Math.min(1, at / length) : 0;

  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", width: "100%" }}>
      <div data-scene style={SCENE}>
        {/* Loops by itself: the design asks for a five second clip that keeps going round. */}
        <video ref={video} src={videoUrl} loop playsInline
               onPlay={() => setPlaying(true)} onPause={() => setPlaying(false)}
               onTimeUpdate={onTime}
               onLoadedMetadata={() => setLength(video.current?.duration || 0)}
               style={{ width: "100%", height: "100%", objectFit: "contain", display: "block" }} />
        {audioUrl && <audio ref={audio} src={audioUrl} loop />}
        <button type="button" aria-label={playing ? "Duraklat" : "Oynat"} onClick={toggle}
                style={BUTTON}>
          {playing ? <PauseGlyph size={22} /> : <PlayGlyph size={22} />}
        </button>

        <div data-track style={TRACK}>
          <Mono size={11} style={CLOCK}>{clock(at)}</Mono>
          {audioUrl ? (
            <div style={{ flex: 1, display: "flex", alignItems: "center", gap: 2, height: 24 }}>
              {Array.from({ length: BARS }, (_, bar) => (
                <span key={bar} data-bar
                      style={{ flex: 1,
                               // A flat bar is what an unread waveform looks like: still a progress
                               // strip, still not a shape anybody invented.
                               height: `${20 + 80 * (peaks ? peaks[bar] : 0.2)}%`,
                               borderRadius: 1,
                               background: bar / BARS <= done ? "var(--accent)" : UNPLAYED }} />
              ))}
            </div>
          ) : (
            /* No box around it: over a picture the contrast is the picture. */
            <div style={{ flex: 1, height: 4, borderRadius: 2, overflow: "hidden",
                          background: "rgba(255,255,255,.25)" }}>
              <div data-progress style={{ width: `${done * 100}%`, height: "100%",
                                          background: "var(--accent)" }} />
            </div>
          )}
          <Mono size={11} style={CLOCK}>{clock(length)}</Mono>
        </div>
      </div>
    </div>
  );
}
