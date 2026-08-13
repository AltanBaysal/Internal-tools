import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import ProducersPanel from "./ProducersPanel.jsx";
import { COLAB_INSTALL } from "./useProducers.js";

const THREE = [
  { id: "photo", name: "Fotoğraf üreticisi", installed: true },
  { id: "video", name: "Video üreticisi", installed: false },
  { id: "audio", name: "Ses üreticisi", installed: false },
];

function renderPanel(props) {
  return render(
    <ProducersPanel producers={THREE} error={null} onInstall={() => {}} {...props} />,
  );
}

describe("ProducersPanel", () => {
  it("says what each producer installs and what it is for", () => {
    renderPanel();

    expect(screen.getByText(
      "Her üretici kendi model grubunu kurar. Kullanmadığın kurulmaz.")).toBeTruthy();
    expect(screen.getByText("Fotoğraf üreticisi")).toBeTruthy();
    expect(screen.getByText("Video üreticisi")).toBeTruthy();
    expect(screen.getByText("Ses üreticisi")).toBeTruthy();
  });

  it("marks an installed producer and offers the others a way in", () => {
    renderPanel();

    expect(screen.getByText("✓ kurulu")).toBeTruthy();
    expect(screen.getAllByText("Kur")).toHaveLength(2);
  });

  it("draws no row it cannot vouch for when the answer never came", () => {
    renderPanel({ producers: null, error: "Sunucuya ulaşılamadı — kontrol et." });

    expect(screen.queryByText("Fotoğraf üreticisi")).toBeNull();
    expect(screen.getByText("Üretici durumu okunamadı")).toBeTruthy();
  });

  it("asks nothing before Kur, because nothing is started here", () => {
    const onInstall = vi.fn();
    renderPanel({ onInstall });

    fireEvent.click(screen.getAllByText("Kur")[0]);

    expect(onInstall).toHaveBeenCalledWith("video");
    expect(screen.queryByText("Video üreticisi kurulsun mu?")).toBeNull();
  });

  it("shows the row where the install really happens", () => {
    renderPanel({ producers: THREE.map((producer) => (producer.id === "video"
      ? { ...producer, note: COLAB_INSTALL } : producer)) });

    expect(screen.getByText(COLAB_INSTALL)).toBeTruthy();
    // The button stays: pressing it again is how the user asks again.
    expect(screen.getAllByText("Kur")).toHaveLength(2);
  });
});
