import { useCallback, useEffect, useRef, useState } from "react";

import { sayHere, waitForIdle } from "../../shared/api.js";
import { notify } from "./notification.js";

// What the box and the notification say.
export const IDLE_SENTENCE = "Sıra 10 dakikadır boş. Colab açık kaldıkça A100 boşa para yiyor.";

// After an ask that did not arrive -- the tunnel dropped, Colab went away -- the next one waits this
// long, so a server that is gone is not asked in a tight loop.
const AGAIN_MS = 10_000;

// "Orada mısın?" as the server's idle watch has it (madde 498). The server counts down and asks;
// the screen only listens: one ask held open at a time, asked again from the version each answer
// brings. Opening the page is being here, so it starts with Buradayım: someone who has just opened
// it is not asked whether they are there.
export function useIdleWatch() {
  const [asking, setAsking] = useState(false);
  // The version last heard. One that asks and is new is a new question -- the one ten minutes
  // later included -- and it rings again.
  const seen = useRef(null);
  // For Buradayım's answer, which can land after the box is gone. The listening has its own flag
  // per run of the effect: a run taken down must not listen again when its requests land, even
  // though the next run has the hook mounted again.
  const mounted = useRef(true);

  const take = useCallback((said) => {
    if (!mounted.current) return;
    if (said.asking && said.version !== seen.current) notify(IDLE_SENTENCE);
    seen.current = said.version;
    setAsking(said.asking);
  }, []);

  useEffect(() => {
    mounted.current = true;
    let alive = true;
    let timer = null;
    const listen = () => {
      waitForIdle(seen.current).then(
        (said) => {
          if (!alive) return;
          take(said);
          listen();
        },
        () => { if (alive) timer = setTimeout(listen, AGAIN_MS); },
      );
    };
    // A refused Buradayım still listens: with no version heard, the first ask answers at once.
    sayHere()
      .then((said) => { if (alive) take(said); }, () => {})
      .finally(() => { if (alive) listen(); });
    return () => {
      alive = false;
      mounted.current = false;
      clearTimeout(timer);
    };
  }, [take]);

  // The box goes at once; the server's answer, and the held ask woken by it, follow.
  const here = useCallback(() => {
    setAsking(false);
    sayHere().then(take, () => {});
  }, [take]);

  return { asking, here };
}
