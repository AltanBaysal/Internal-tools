// The design names the rail's icons but never draws them: it says a photo frame, a video camera, a
// wave. They are drawn here in the kit's own language -- 14x14 box, currentColor, 1.5 rounded
// stroke -- and not in vendor/, which is a verbatim copy of the design's own files.
//
// data-glyph is the icon's identity. Which glyph got drawn is otherwise unreadable from the DOM,
// and the photo panel draws the same one twice -- on the rail and on its button -- so that sameness
// has to be something a test can hold on to.
function Glyph({ name, size = 16, children }) {
  return (
    <svg data-glyph={name} width={size} height={size} viewBox="0 0 14 14" fill="none"
         aria-hidden="true">
      {children}
    </svg>
  );
}

// A framed picture: the frame, a sun in its corner, a hill line across it.
export const PhotoGlyph = ({ size }) => (
  <Glyph name="photo" size={size}>
    <rect x="1.75" y="2.75" width="10.5" height="8.5" rx="1.5"
          stroke="currentColor" strokeWidth="1.4" />
    <circle cx="4.9" cy="5.6" r=".95" stroke="currentColor" strokeWidth="1.2" />
    <path d="M2.4 9.9 5.4 7l1.9 1.8L9.1 7.4l2.5 2.5" stroke="currentColor" strokeWidth="1.4"
          strokeLinecap="round" strokeLinejoin="round" />
  </Glyph>
);

export const QueueGlyph = ({ size }) => (
  <Glyph name="queue" size={size}>
    <path d="M2 4h10M2 7h10M2 10h6" stroke="currentColor" strokeWidth="1.5"
          strokeLinecap="round" />
  </Glyph>
);

// A video camera: the body and the lens barrel the design asks for.
export const VideoGlyph = ({ size }) => (
  <Glyph name="video" size={size}>
    <rect x="1.6" y="3.6" width="7.6" height="6.8" rx="1.4" stroke="currentColor"
          strokeWidth="1.4" />
    <path d="M9.2 6.5 12.4 4.7v4.6L9.2 7.5z" stroke="currentColor" strokeWidth="1.4"
          strokeLinejoin="round" />
  </Glyph>
);

// A wave: what the design puts on the sound panel's rail icon and in front of its button.
export const SoundGlyph = ({ size }) => (
  <Glyph name="sound" size={size}>
    <path d="M1.8 7c.9-2.6 1.7-2.6 2.6 0s1.7 2.6 2.6 0 1.7-2.6 2.6 0 1.7 2.6 2.6 0"
          stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round" />
  </Glyph>
);

// The play triangle the design asks for on the ownership badge. Filled, not stroked: at 9px a
// stroked triangle reads as a smudge.
export const PlayGlyph = ({ size }) => (
  <Glyph name="play" size={size}>
    <path d="M4.4 2.9 11 7l-6.6 4.1z" fill="currentColor" />
  </Glyph>
);

// A crate: what a producer's model group arrives in.
export const ProducersGlyph = ({ size }) => (
  <Glyph name="producers" size={size}>
    <path d="M7 1.9 12.1 4.4v5.2L7 12.1 1.9 9.6V4.4L7 1.9z" stroke="currentColor"
          strokeWidth="1.3" strokeLinejoin="round" />
    <path d="M1.9 4.4 7 6.9l5.1-2.5M7 6.9v5.2" stroke="currentColor" strokeWidth="1.3"
          strokeLinejoin="round" />
  </Glyph>
);

export const AgentGlyph = ({ size }) => (
  <Glyph name="agent" size={size}>
    <path d="M2 4.5A1.5 1.5 0 0 1 3.5 3h7A1.5 1.5 0 0 1 12 4.5v4A1.5 1.5 0 0 1 10.5 10H6l-3 2V10
             A1 1 0 0 1 2 9V4.5z" stroke="currentColor" strokeWidth="1.4" strokeLinejoin="round" />
  </Glyph>
);

// Two sheets, one behind the other. The front one is whole; the back one shows only the edge the
// front does not cover, which is what makes the pair read as a copy rather than two boxes.
export const CopyGlyph = ({ size }) => (
  <Glyph name="copy" size={size}>
    <rect x="4.6" y="1.9" width="7.5" height="7.5" rx="1.3" stroke="currentColor"
          strokeWidth="1.4" />
    <path d="M9.4 12.1H3.2a1.3 1.3 0 0 1-1.3-1.3V4.6" stroke="currentColor" strokeWidth="1.4"
          strokeLinecap="round" strokeLinejoin="round" />
  </Glyph>
);
