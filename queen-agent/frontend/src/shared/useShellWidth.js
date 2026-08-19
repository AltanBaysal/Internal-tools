import { useEffect, useRef, useState } from "react";

// The design's three thresholds. Here and nowhere else: the stylesheet knows the step by name and
// never repeats a number.
const STEPS = [
  [1000, "app-shell--narrow"],
  [780, "app-shell--tight"],
  [640, "app-shell--compact"],
];

// The steps stack: at 600 all three hold, so every rule states its own threshold once.
export function shellSteps(width) {
  // Zero is the absence of a measurement rather than the narrowest screen. Reading it as a step
  // would draw the wrong layout for the first frame of every load.
  if (!width) return "";
  return STEPS.filter(([limit]) => width <= limit)
    .map(([, name]) => name)
    .join(" ");
}

// What is measured is the shell, not the window: the same screen embedded in a frame has to answer
// the same way, and a media query can only ask about the window.
export function useShellWidth() {
  const shell = useRef(null);
  const [width, setWidth] = useState(0);

  useEffect(() => {
    const element = shell.current;
    // No observer means no measurement, which is the widest layout -- the app still draws.
    if (!element || typeof ResizeObserver === "undefined") return undefined;
    const observer = new ResizeObserver(([entry]) => setWidth(entry.contentRect.width));
    observer.observe(element);
    return () => observer.disconnect();
  }, []);

  // The number as well as the steps: the stylesheet asks in steps, but whether the rail still fits
  // beside the conversation is arithmetic, and it is answered in JS (railWidth.js).
  return { shell, width, steps: shellSteps(width) };
}
