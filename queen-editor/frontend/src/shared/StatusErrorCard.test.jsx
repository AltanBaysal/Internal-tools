import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StatusErrorCard } from "./StatusErrorCard.jsx";

describe("StatusErrorCard", () => {
  it("puts the raw output in the same box the queue panel uses", () => {
    // One unbounded block was enough to lock a panel; this card is drawn on three screens, so it
    // gets the same box rather than waiting its turn to lock one of them.
    const raw = Array.from({ length: 40 }, (_, i) => `satır ${i}`).join("\n");

    render(<StatusErrorCard text="İstek reddedildi" raw={raw} />);

    const box = document.querySelector("[data-raw]");
    expect(box).toBeTruthy();
    expect(box.textContent).toBe(raw);
  });
});
