// Which pictures this session has already put on screen. Opening a frame's page builds the whole
// gallery again, and a tile that starts empty waits for the viewport and then for a queue slot --
// that waiting is what the user sees as their photos disappearing (İstek 1.2). The bytes are in the
// browser's cache either way; what is kept here is that the waiting is already over.
//
// Beside the queue rather than inside it: one is a ceiling on what may be in flight, the other a
// note of what has already landed.
//
// URLs, and a session's worth of short strings -- nothing is evicted because nothing grows.
export const shownPictures = new Set();
