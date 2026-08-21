import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { useKeptScroll } from "./useKeptScroll.js";

// A box standing in for the gallery's scroll container: the hook only ever asks it for scrollTop
// and gives it back, so nothing else about it matters. jsdom keeps the value it is given -- it does
// no layout, so there is nothing to clamp it against.
function Box({ project }) {
  return <div data-box ref={useKeptScroll(project)} />;
}

const boxOf = () => document.querySelector("[data-box]");

describe("useKeptScroll", () => {
  it("starts a gallery it has never seen at the top", () => {
    render(<Box project="hiç görülmemiş" />);

    expect(boxOf().scrollTop).toBe(0);
  });

  it("brings the box back to where it was left", () => {
    const first = render(<Box project="düğün" />);
    boxOf().scrollTop = 640;

    first.unmount();
    render(<Box project="düğün" />);

    // The whole of the item: what the user left is what they come back to.
    expect(boxOf().scrollTop).toBe(640);
  });

  it("keeps one project's place out of another's", () => {
    const first = render(<Box project="nikah" />);
    boxOf().scrollTop = 320;
    first.unmount();

    render(<Box project="kına" />);

    expect(boxOf().scrollTop).toBe(0);
  });
});
