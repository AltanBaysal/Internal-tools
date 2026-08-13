import { act, fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import LayerPanel from "./LayerPanel.jsx";

const done = (file, layers = {}) => ({ id: file.replace(".png", ""), file, status: "done", layers,
                                       failed: [] });

const FRAMES = [
  done("2_a.png"),
  done("1_a.png", { video: "1_a_V1_0.mp4" }),
  done("0_a.png"),
  { id: "3_a", file: "3_a.png", status: "pending", layers: {}, failed: [] },
];

const variantBox = () => screen.getByRole("spinbutton");

function renderPanel(props) {
  return render(
    <LayerPanel layer="video" frames={FRAMES} selected={[]} producer={null}
                onQueue={() => Promise.resolve({ added: 2 })} onInstall={() => {}} {...props} />,
  );
}

describe("LayerPanel — the scope", () => {
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
    renderPanel({ selected: ["0_a"] });

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

describe("LayerPanel — variants", () => {
  it("multiplies the estimate by the variant count", () => {
    renderPanel();

    fireEvent.change(variantBox(), { target: { value: "3" } });

    expect(screen.getByText("6 video üretilecek — her kare kendi videosunu alır.")).toBeTruthy();
  });

  it("refuses a count the server would refuse", () => {
    renderPanel();

    fireEvent.change(variantBox(), { target: { value: "27" } });

    expect(variantBox().value).toBe("1");
  });

  it("counts a selected frame that already has a video", () => {
    // Picking it by hand is how a second video is asked for -- it becomes a copy frame.
    renderPanel({ selected: ["1_a"] });

    expect(screen.getByText("Seçili kareler").closest("button").textContent).toContain("1");
    expect(screen.getByText("1 video üretilecek — her kare kendi videosunu alır.")).toBeTruthy();
  });

  it("counts the frame that was picked, not the one showing the same picture", () => {
    // Asking for a second video makes a copy frame, and the copy shows the same photo -- so a file
    // name cannot tell the two apart and an identity can. This is the whole reason the panel must
    // match on identity, and without this case the bug could be closed from the wrong end.
    const twin = { id: "0_a-2", file: "0_a.png", status: "done", layers: {}, failed: [] };

    renderPanel({ frames: [...FRAMES, twin], selected: ["0_a-2"] });

    expect(screen.getByText("Seçili kareler").closest("button").textContent).toContain("1");
  });
});

describe("LayerPanel — sending", () => {
  it("asks for every frame with no video when that is the scope", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 2 });
    renderPanel({ onQueue });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null, 1);
    expect(screen.getByText("2 video kuyruğa eklendi")).toBeTruthy();
  });

  it("asks only for what is selected when that is the scope", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 1 });
    // Matched by identity, sent by file name: two different things, and the whole value of this
    // test is that it says so in one breath.
    renderPanel({ selected: ["0_a"], onQueue });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(["0_a.png"], 1);
  });

  it("sends the variant count along with the scope", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 4 });
    renderPanel({ onQueue });

    fireEvent.change(variantBox(), { target: { value: "2" } });
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null, 2);
  });

  it("says the length is not a choice in this version", () => {
    renderPanel();

    expect(screen.getByText("Her video 5 saniye — bu sürümde sabit.")).toBeTruthy();
  });

  it("does not explain who writes the prompt -- the frame's own page does", () => {
    // The sentence was read once and then took up room at the foot of the panel on every open.
    // Where a prompt is actually read -- the frame's page -- an empty one still says that the
    // language model will write it when its turn comes.
    renderPanel();

    expect(screen.queryByText(/LLM/)).toBeNull();
  });
});

describe("LayerPanel — sound", () => {
  const SOUND_FRAMES = [
    done("0_a.png"),
    done("1_a.png", { video: "1_a_V1_0.mp4" }),
  ];

  function renderSound(props) {
    return render(
      <LayerPanel layer="audio" frames={SOUND_FRAMES} selected={[]} producer={null}
                  onQueue={() => Promise.resolve({ added: 1 })} onInstall={() => {}} {...props} />,
    );
  }

  it("counts only the frames that have a video and no sound", () => {
    renderSound();

    expect(screen.getByText("Videosu olup sesi olmayan kareler").closest("button").textContent)
      .toContain("1");
  });

  it("leaves out a frame whose video blew up -- there is nothing to lay the sound over", () => {
    renderSound({ frames: [done("1_a.png", { video: "1_a_V1_0.mp4" })].map(
      (frame) => ({ ...frame, failed: ["video"] }))
    });

    expect(screen.getByText("Videosu olup sesi olmayan kareler").closest("button").textContent)
      .toContain("0");
  });

  it("says what it would make, in its own words", () => {
    renderSound();

    expect(screen.getByText("MMAudio v2")).toBeTruthy();
    expect(screen.getByText("1 ses üretilecek — her kare kendi sesini alır.")).toBeTruthy();
  });

  it("says there is nothing to do in its own words", () => {
    renderSound({ frames: [done("0_a.png")] });

    expect(screen.getByText("Videosu olup sesi olmayan kare yok — üretilecek bir şey yok."))
      .toBeTruthy();
  });

  it("confirms in its own words", async () => {
    renderSound();

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(screen.getByText("1 ses kuyruğa eklendi")).toBeTruthy();
  });

  it("does not explain who writes the prompt either", () => {
    // Both panels are one component and the design asks for them to be identical; leaving the
    // sentence on one of them would part them where nothing else does.
    renderSound();

    expect(screen.queryByText(/LLM/)).toBeNull();
  });
});
