import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import InstallCard from "./InstallCard.jsx";
import { COLAB_INSTALL } from "./useProducers.js";

const MISSING = { id: "video", name: "Video üreticisi", installed: false };

describe("InstallCard", () => {
  it("names the producer and offers a Kur that asks nothing", () => {
    const onInstall = vi.fn();
    render(<InstallCard producer={MISSING} onInstall={onInstall} />);

    expect(screen.getByText("Video üreticisi kurulu değil.")).toBeTruthy();
    fireEvent.click(screen.getByText("Kur"));

    expect(onInstall).toHaveBeenCalledWith("video");
  });

  it("says where the install happens once the user has asked", () => {
    render(<InstallCard producer={{ ...MISSING, note: COLAB_INSTALL }} onInstall={() => {}} />);

    expect(screen.getByText(COLAB_INSTALL)).toBeTruthy();
    expect(screen.getByText("Kur")).toBeTruthy();
  });

  it("draws no progress bar at all", () => {
    const { container } = render(
      <InstallCard producer={{ ...MISSING, note: COLAB_INSTALL }} onInstall={() => {}} />);

    expect(container.querySelector("[data-bar]")).toBeNull();
  });

  it("is nothing at all once the producer is installed", () => {
    const { container } = render(
      <InstallCard producer={{ id: "photo", name: "Fotoğraf üreticisi", installed: true }}
                   onInstall={() => {}} />);

    expect(container.firstChild).toBeNull();
  });
});
