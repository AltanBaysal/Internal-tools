import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import ProducersPanel from "./ProducersPanel.jsx";

const THREE = [
  { id: "photo", name: "Fotoğraf üreticisi", installed: true },
  { id: "video", name: "Video üreticisi", installed: false },
  { id: "audio", name: "Ses üreticisi", installed: false },
];

const INSTALLING = THREE.map((producer) => (producer.id === "video"
  ? { ...producer, installing: { file: "wan.safetensors" } }
  : producer));

function renderPanel(props) {
  return render(
    <ProducersPanel producers={THREE} error={null} onInstall={() => {}} onCancel={() => {}}
                    {...props} />,
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

  it("asks before it starts a long download", () => {
    const onInstall = vi.fn();
    renderPanel({ onInstall });

    fireEvent.click(screen.getAllByText("Kur")[0]);

    expect(screen.getByText("Video üreticisi kurulsun mu?")).toBeTruthy();
    // Wide enough for the two-line body it carries (madde 105).
    expect(screen.getByText("Video üreticisi kurulsun mu?").closest(".wf-card").style.width)
      .toBe("360px");
    expect(screen.getByText("Kurulum uzun sürebilir. Üretimi engellemez, arkada sürer."))
      .toBeTruthy();
    expect(onInstall).not.toHaveBeenCalled();

    // The modal's own Kur is the one added on top.
    fireEvent.click(screen.getAllByText("Kur").at(-1));
    expect(onInstall).toHaveBeenCalledWith("video");
  });

  it("names what the running install is fetching, and offers a way out", () => {
    renderPanel({ producers: INSTALLING });

    expect(screen.getByText("kuruluyor… wan.safetensors")).toBeTruthy();
    expect(screen.getByText("İptal")).toBeTruthy();
  });

  it("shows a failed install with the server's own words and a way to try again", () => {
    renderPanel({ producers: THREE.map((producer) => (producer.id === "video"
      ? { ...producer, error: "bağlantı yok" } : producer)) });

    expect(screen.getByText("bağlantı yok")).toBeTruthy();
    expect(screen.getAllByText("Kur")).toHaveLength(2);
  });

  it("asks before it throws away what has come down so far", () => {
    const onCancel = vi.fn();
    renderPanel({ producers: INSTALLING, onCancel });

    fireEvent.click(screen.getByText("İptal"));

    expect(screen.getByText("Kurulum iptal edilsin mi?")).toBeTruthy();
    expect(screen.getByText("Kurulum iptal edilsin mi?").closest(".wf-card").style.width)
      .toBe("360px");
    expect(onCancel).not.toHaveBeenCalled();

    fireEvent.click(screen.getByText("İptal et"));
    expect(onCancel).toHaveBeenCalledWith("video");
  });
});
