import { useEffect, useLayoutEffect } from "react";

// How tall the field's text is, written as its height. At its rows a long text shows the scrollbar
// (app.css), which narrows the lines and adds a wrapped line to what is measured, so the bar is
// hidden for the measuring alone; past the stylesheet's limit it is wanted.
function fit(element) {
  element.style.height = "auto";
  element.style.overflowY = "hidden";
  const content = element.scrollHeight;
  // Every box is border-box (app.css), and scrollHeight stops inside the border. Read in the same
  // layout as the content, before anything is written again.
  const border = element.offsetHeight - element.clientHeight;
  element.style.overflowY = "";
  // A field that is not drawn measures nothing; it keeps its rows until it is measured again.
  if (content) element.style.height = `${content + border}px`;
}

// A field as tall as what is written in it (Madde 504). Only the measuring is here: how tall it may
// get is its stylesheet's max-height, which stays true when the window does not, and how short is its
// rows, which is what the field falls back to while it is measured. The ref is handed in rather than
// made here, because a field that already keeps one for its own reasons (the composer's focus) would
// otherwise need a second.
export function useGrowingField(field, value) {
  // When the text changes. A layout effect, so the height is set before the frame is drawn and the
  // field never shows at its old size for one frame.
  useLayoutEffect(() => {
    if (field.current) fit(field.current);
  }, [field, value]);

  // And when its width does, since the same text wraps into another number of lines (Madde 505). On
  // a narrow window's first load the shell is not measured yet and the composer is drawn a few pixels
  // wide, and its placeholder wrapped into eight lines; a field shown after being hidden goes from no
  // width to its own, so this also measures the composer as the full chat's notice gives it back.
  // Only the width: the height is what fit writes. And a frame later rather than in the callback:
  // resizing the observed field there leaves its own notice undelivered, which the browser reports
  // as an error.
  useEffect(() => {
    const element = field.current;
    if (!element || typeof ResizeObserver === "undefined") return undefined;
    let width = null;
    let frame = 0;
    const observer = new ResizeObserver(([entry]) => {
      const next = entry.contentRect.width;
      if (next === width) return;
      width = next;
      // Hidden, it is drawn at no width and there is nothing to measure. It keeps the height it had,
      // so a draft unchanged while hidden comes back at its size rather than at its rows for a frame.
      if (!next) return;
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => fit(element));
    });
    observer.observe(element);
    return () => {
      observer.disconnect();
      cancelAnimationFrame(frame);
    };
  }, [field]);
}
