import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import ProducersPanel from "./ProducersPanel.jsx";

const THREE = [
  { id: "photo", name: "Fotoğraf üreticisi", installed: true },
  { id: "video", name: "Video üreticisi", installed: false },
  { id: "audio", name: "Ses üreticisi", installed: false },
];

describe("ProducersPanel", () => {
  it("says what each producer installs and what it is for", () => {
    render(<ProducersPanel producers={THREE} error={null} />);

    expect(screen.getByText(
      "Her üretici kendi model grubunu kurar. Kullanmadığın kurulmaz.")).toBeTruthy();
    expect(screen.getByText("Fotoğraf üreticisi")).toBeTruthy();
    expect(screen.getByText("Video üreticisi")).toBeTruthy();
    expect(screen.getByText("Ses üreticisi")).toBeTruthy();
  });

  it("marks an installed producer and offers the others a way in", () => {
    render(<ProducersPanel producers={THREE} error={null} />);

    expect(screen.getByText("✓ kurulu")).toBeTruthy();
    expect(screen.getAllByText("Kur")).toHaveLength(2);
  });

  it("keeps the Kur button held until the flow behind it exists", () => {
    render(<ProducersPanel producers={THREE} error={null} />);

    expect(screen.getAllByText("Kur")[0].closest("button").disabled).toBe(true);
  });

  it("draws no row it cannot vouch for when the answer never came", () => {
    render(<ProducersPanel producers={null} error="Sunucuya ulaşılamadı — kontrol et." />);

    expect(screen.queryByText("Fotoğraf üreticisi")).toBeNull();
    expect(screen.getByText("Üretici durumu okunamadı")).toBeTruthy();
  });
});
