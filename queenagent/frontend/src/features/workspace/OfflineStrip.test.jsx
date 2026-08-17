import { render, screen } from "@testing-library/react";
import { expect, test } from "vitest";

import OfflineStrip from "./OfflineStrip.jsx";

test("nothing is drawn while the connection is there", () => {
  const { container } = render(<OfflineStrip online />);
  expect(container.textContent).toBe("");
});

test("offline, it says what is saved and what waits", () => {
  render(<OfflineStrip online={false} />);
  // The server is on this machine: the message lands, the answer is what needs the network.
  expect(screen.getByTestId("offline").textContent).toContain("Messages are saved");
  expect(screen.getByTestId("offline").textContent).toContain("answer when the connection is back");
});
