import { act, fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import VideoPanel from "./VideoPanel.jsx";

const done = (file, layers = {}) => ({ id: file.replace(".png", ""), file, status: "done", layers });

const FRAMES = [
  done("2_a.png"),
  done("1_a.png", { video: "1_a_V1_0.mp4" }),
  done("0_a.png"),
  { id: "3_a", file: "3_a.png", status: "pending", layers: {} },
];

function renderPanel(props) {
  return render(
    <VideoPanel frames={FRAMES} selected={[]} producer={null}
                onQueue={() => Promise.resolve({ added: 2 })} onInstall={() => {}} {...props} />,
  );
}

describe("VideoPanel — the scope", () => {
  it("counts the frames a video can still be hung on", () => {
    renderPanel();

    // 2_a and 0_a: the one with a video is out, and so is the one with no photo yet.
    expect(screen.getByText("Videosu olmayanlar").closest("button").textContent).toContain("2");
  });

  it("says what pressing the button would do", () => {
    renderPanel();

    expect(screen.getByText("2 video üretilecek — her kare kendi videosunu alır.")).toBeTruthy();
  });

  it("follows the gallery's selection rather than keeping one of its own", () => {
    renderPanel({ selected: ["0_a.png"] });

    expect(screen.getByText("Seçili kareler").closest("button").style.borderColor)
      .toBe("var(--accent)");
    expect(screen.getByText("1 video üretilecek — her kare kendi videosunu alır.")).toBeTruthy();
  });

  it("leaves the selection row out of reach while nothing is selected", () => {
    renderPanel();

    expect(screen.getByText("Seçili kareler").closest("button").disabled).toBe(true);
  });

  it("says there is nothing to do rather than treating it as a fault", () => {
    renderPanel({ frames: [done("1_a.png", { video: "1_a_V1_0.mp4" })] });

    expect(screen.getByText("Tüm karelerin videosu var — üretilecek bir şey yok.")).toBeTruthy();
    expect(screen.getByText("Kuyruğa ekle").closest("button").disabled).toBe(true);
  });
});

describe("VideoPanel — sending", () => {
  it("asks for every frame with no video when that is the scope", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 2 });
    renderPanel({ onQueue });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null);
    expect(screen.getByText("2 video kuyruğa eklendi")).toBeTruthy();
  });

  it("asks only for what is selected when that is the scope", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 1 });
    renderPanel({ selected: ["0_a.png"], onQueue });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(["0_a.png"]);
  });

  it("says the length is not a choice in this version", () => {
    renderPanel();

    expect(screen.getByText("Her video 5 saniye — bu sürümde sabit.")).toBeTruthy();
  });

  it("says who writes the prompt, since it never asks for one", () => {
    renderPanel();

    expect(screen.getByText(/LLM her fotonun kendi prompt'undan yazar/)).toBeTruthy();
  });
});
