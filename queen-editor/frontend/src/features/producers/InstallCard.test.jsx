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

  it("turns into progress while the download runs", () => {
    render(<InstallCard producer={{ ...MISSING, installing: { done: 5, total: 10, file: "wan" } }}
                        onInstall={() => {}} />);

    expect(screen.getByText("kuruluyor… bitince bu kart kaybolur")).toBeTruthy();
    expect(screen.queryByText("Kur")).toBeNull();
  });

  it("is nothing at all once the producer is installed", () => {
    const { container } = render(
      <InstallCard producer={{ id: "photo", name: "Fotoğraf üreticisi", installed: true }}
                   onInstall={() => {}} />);

    expect(container.firstChild).toBeNull();
  });
});
