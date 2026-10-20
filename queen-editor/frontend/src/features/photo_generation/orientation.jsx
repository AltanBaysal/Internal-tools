// Which way a generation stands (madde 477): yatay or dikey, set per generation the way its negative
// is. The words are the engine's (domain/orientation.py); only the Turkish labels live here.
const LANDSCAPE = "yatay";
const PORTRAIT = "dikey";

// What a box opens on when nothing it was given names one: a project that never saved a pick, or a
// frame whose line predates the choice and whose picture has not arrived yet. The server's default
// for a request that names none, shown so the segment is never blank -- the request always carries
// what the segment shows, and the server holds it to the two words.
export const FIRST_ORIENTATION = LANDSCAPE;

const OPTIONS = [
  { id: LANDSCAPE, label: "Yatay" },
  { id: PORTRAIT, label: "Dikey" },
];

/** The orientation a picture of this size stands in -- wider than tall is yatay.
 *
 * The H3 producer's own reading of a photo (comfy_h3_video_generator), used here only to open a box
 * on the frame's own value: the page is already showing the picture, so this costs no request.
 */
export function shapeOf(width, height) {
  return width > height ? LANDSCAPE : PORTRAIT;
}

/** The two-button segment, with no label of its own: each form draws its heading in its own face.
 *
 * The length and Mutlu son segments' shape (LayerPanel). aria-pressed rather than the class alone,
 * so which one is on can be read by something other than the eye.
 */
export function OrientationSegment({ value, onChange }) {
  return (
    <div className="wf-segment" style={{ display: "flex" }}>
      {OPTIONS.map((one) => (
        <button key={one.id} type="button" aria-pressed={value === one.id}
                className={value === one.id ? "is-on" : ""} style={{ flex: 1 }}
                onClick={() => onChange(one.id)}>
          {one.label}
        </button>
      ))}
    </div>
  );
}
