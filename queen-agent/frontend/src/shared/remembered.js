import { useEffect, useState } from "react";

// A value this browser keeps across a reload. Not the server: since Madde 86 nothing there reads a
// selection back, and what is kept here is a preference of this browser rather than the chat's own
// record. Madde 86's worry does not come back either -- there is still one value, and this is only
// where it is born.
//
// Every touch of storage is wrapped. A browser with it switched off, or a private window, throws on
// the read as well as the write, and what is lost is the memory: the selection still holds for the
// session it was made in.
const PREFIX = "queenagent.";

function kept(name) {
  try {
    return window.localStorage.getItem(PREFIX + name);
  } catch {
    return null;
  }
}

function keep(name, value) {
  try {
    window.localStorage.setItem(PREFIX + name, value);
  } catch {
    // Nothing to do and nothing to say.
  }
}

export function useRemembered(name, fallback) {
  // Read in the initialiser, so it happens once on the first render rather than on every one -- and
  // what a later read would find is what this already wrote.
  const [value, setValue] = useState(() => {
    const written = kept(name);
    // null is "never chosen" and "" is "chosen and then let go". Folding the two together would
    // undo the user's dropping of a skill on every reload.
    return written === null ? fallback : written;
  });

  // The first render writes back what it just read, which changes nothing. A flag to skip that one
  // pass would be its own thing to get wrong, for no gain.
  useEffect(() => {
    keep(name, value);
  }, [name, value]);

  return [value, setValue];
}

// What does not parse never happened: storage is shared with every past version of the app, and a
// map that will not read is an empty map rather than a crash.
function parsedMap(text) {
  try {
    const parsed = JSON.parse(text);
    if (parsed && typeof parsed === "object" && !Array.isArray(parsed)) return parsed;
  } catch {
    // Nothing to do and nothing to say.
  }
  return {};
}

// A map under one name: an entry per chat, so what one chat picks never stands in another
// (Madde 105). The write goes through the functional form -- two picks in one breath must not
// undo each other.
export function useRememberedMap(name) {
  const [kept, setKept] = useRemembered(name, "{}");
  const remember = (key, value) =>
    setKept((current) => JSON.stringify({ ...parsedMap(current), [key]: value }));
  return [parsedMap(kept), remember];
}
