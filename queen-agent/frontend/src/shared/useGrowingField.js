import { useLayoutEffect } from "react";

// A field as tall as what is written in it (Madde 504), measured again whenever the text changes.
// Only the measuring is here: how tall it may get is its stylesheet's max-height, which stays true
// when the window does not, and how short is its rows, which is what the field falls back to below.
// The ref is handed in rather than made here, because a field that already keeps one for its own
// reasons (the composer's focus) would otherwise need a second.
//
// A layout effect, so the height is set before the frame is drawn and the field never shows at its
// old size for one frame.
export function useGrowingField(field, value) {
  useLayoutEffect(() => {
    const element = field.current;
    if (!element) return;
    element.style.height = "auto";
    // At its rows a long text shows the scrollbar (app.css), which narrows the lines and adds a
    // wrapped line to what is measured. Hidden for the measuring alone; past the stylesheet's limit
    // the bar is wanted.
    element.style.overflowY = "hidden";
    const content = element.scrollHeight;
    // Every box is border-box (app.css), and scrollHeight stops inside the border. Read in the same
    // layout as the content, before anything is written again.
    const border = element.offsetHeight - element.clientHeight;
    element.style.overflowY = "";
    // A field that is not drawn measures nothing; it keeps its rows until it is.
    if (content) element.style.height = `${content + border}px`;
  }, [field, value]);
}
