import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import InstallCard from "./InstallCard.jsx";

const MISSING = { id: "video", name: "Video üreticisi", installed: false };

describe("InstallCard", () => {
  it("names the producer and offers a Kur that asks nothing", () => {
    const onInstall = vi.fn();
    render(<InstallCard producer={MISSING} onInstall={onInstall} />);

    expect(screen.getByText("Video üreticisi kurulu değil.")).toBeTruthy();
    fireEvent.click(screen.getByText("Kur"));

    expect(onInstall).toHaveBeenCalledWith("video");
  });

  it("says what is coming down while the download runs", () => {
    render(<InstallCard producer={{ ...MISSING, installing: { file: "wan.safetensors" } }}
                        onInstall={() => {}} />);

    expect(screen.getByText("kuruluyor… wan.safetensors")).toBeTruthy();
    expect(screen.queryByText("Kur")).toBeNull();
  });

  it("draws no progress bar at all", () => {
    const { container } = render(
      <InstallCard producer={{ ...MISSING, installing: { file: "wan.safetensors" } }}
                   onInstall={() => {}} />);

    expect(container.querySelector("[data-bar]")).toBeNull();
  });

  it("shows the failure of the last attempt next to a fresh Kur", () => {
    render(<InstallCard producer={{ ...MISSING, error: "bağlantı yok" }} onInstall={() => {}} />);

    expect(screen.getByText("bağlantı yok")).toBeTruthy();
    expect(screen.getByText("Kur")).toBeTruthy();
  });

  it("is nothing at all once the producer is installed", () => {
    const { container } = render(
      <InstallCard producer={{ id: "photo", name: "Fotoğraf üreticisi", installed: true }}
                   onInstall={() => {}} />);

    expect(container.firstChild).toBeNull();
  });
});
