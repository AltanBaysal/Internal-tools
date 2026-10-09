import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import { getHappyEnding, getReferenceSettings, getVideoLength, saveHappyEnding,
         saveReferenceSettings, saveVideoLength } from "../../shared/api.js";
import LayerPanel from "./LayerPanel.jsx";

// Referanstan's record, the project's video length and its Mutlu son are the server's; everything
// else the panel needs arrives as props.
vi.mock("../../shared/api.js", async (importOriginal) => ({
  ...(await importOriginal()),
  getHappyEnding: vi.fn(),
  getReferenceSettings: vi.fn(),
  getVideoLength: vi.fn(),
  saveHappyEnding: vi.fn(),
  saveReferenceSettings: vi.fn(),
  saveVideoLength: vi.fn(),
}));

const done = (file, layers = {}) => ({ id: file.replace(".png", ""), file, status: "done", layers,
                                       failed: [] });

const FRAMES = [
  done("2_a.png"),
  done("1_a.png", { video: "1_a_V1_0.mp4" }),
  done("0_a.png"),
  { id: "3_a", file: "3_a.png", status: "pending", layers: {}, failed: [] },
];

const variantBox = () => screen.getByRole("spinbutton");

// Referanstan's draft is kept per project for the length of a visit, in the module. A name of its
// own for every render keeps one test's typing out of the next one's panel.
let rendered = 0;
const freshProject = () => `proje-${++rendered}`;

beforeEach(() => {
  vi.clearAllMocks();
  getReferenceSettings.mockResolvedValue({ prompts: "", variants: null });
  saveReferenceSettings.mockResolvedValue(null);
  // The project's length as the server says it when nothing is saved.
  getVideoLength.mockResolvedValue(8);
  saveVideoLength.mockResolvedValue(null);
  // Off, as the server says it when nothing is saved (madde 426).
  getHappyEnding.mockResolvedValue(false);
  saveHappyEnding.mockResolvedValue(null);
});

const tab = (name) => screen.getByRole("button", { name });
const labels = (view) => [...view.container.querySelectorAll("[data-label]")]
  .map((one) => one.textContent);

function renderPanel(props) {
  return render(
    <LayerPanel layer="video" project={freshProject()} frames={FRAMES} selected={[]}
                producer={null} onQueue={() => Promise.resolve({ added: 2 })}
                onInstall={() => {}} poolShown={false} onShowPool={() => {}} {...props} />,
  );
}

describe("LayerPanel — the scope", () => {
  it("counts the frames a video can still be hung on", () => {
    renderPanel();

    // 2_a and 0_a: the one with a video is out, and so is the one with no photo yet.
    expect(screen.getByText("Videosu olmayan kareler").closest("button").textContent)
      .toContain("2");
  });

  it("says what pressing the button would do", () => {
    renderPanel();

    // Madde 216: the panel opens on loop, so the estimate opens in loop's words.
    expect(screen.getByText("2 loop video üretilecek — her video kendine döner.")).toBeTruthy();
  });

  it("follows the gallery's selection rather than keeping one of its own", () => {
    renderPanel({ selected: ["0_a"] });

    expect(screen.getByText("Seçili kareler").closest("button").style.borderColor)
      .toBe("var(--accent)");
    expect(screen.getByText("1 loop video üretilecek — her video kendine döner.")).toBeTruthy();
  });

  it("leaves the selection row out of reach while nothing is selected", () => {
    renderPanel();

    expect(screen.getByText("Seçili kareler").closest("button").disabled).toBe(true);
  });

});

describe("LayerPanel — variants", () => {
  it("opens at one, whatever the photo panel's default is", () => {
    // İstek 8's second sentence: the photo panel's default moved and this one did not. Two panels,
    // two decisions -- and a number shared between them would have made one follow the other.
    renderPanel();

    expect(variantBox().value).toBe("1");
  });

  it("multiplies the estimate by the variant count", () => {
    renderPanel();

    fireEvent.change(variantBox(), { target: { value: "3" } });

    expect(screen.getByText("6 loop video üretilecek — her video kendine döner.")).toBeTruthy();
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
    expect(screen.getByText(
      "1 loop video üretilecek — videolu 1 kare için yeniler kopya kare olur, eskisi durur."))
      .toBeTruthy();
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

describe("LayerPanel — why the press was refused", () => {
  const addButton = () => screen.getByText("Kuyruğa ekle").closest("button");
  const press = () => fireEvent.click(addButton());
  // Every frame already carries the layer: the scope is empty and nothing is wrong.
  const ALL_HELD = [done("1_a.png", { video: "1_a_V1_0.mp4" })];
  // Nothing is a photo yet, so there is nothing to hang a video on at all.
  const NONE_MADE = [{ id: "3_a", file: "3_a.png", status: "pending", layers: {}, failed: [] }];

  it("stays pressable with nothing to do, and says nothing until it is pressed", () => {
    renderPanel({ frames: ALL_HELD });

    expect(addButton().disabled).toBe(false);
    expect(screen.queryByText(/Tüm karelerin/)).toBeNull();
    expect(screen.queryByText(/üretilecek bir şey yok/)).toBeNull();
  });

  it("says all the frames already have one", () => {
    renderPanel({ frames: ALL_HELD });

    press();

    expect(screen.getByText("Tüm karelerin videosu var.")).toBeTruthy();
  });

  it("does not send a request it refused", () => {
    const onQueue = vi.fn();
    renderPanel({ frames: ALL_HELD, onQueue });

    press();

    expect(onQueue).not.toHaveBeenCalled();
  });

  it("says the project has nothing produced yet", () => {
    renderPanel({ frames: NONE_MADE });

    press();

    expect(screen.getByText("Henüz üretilmiş kare yok.")).toBeTruthy();
  });

  it("says the chosen frames are not photos yet", () => {
    // İstek 4.3, word for word: the frames the user picked have no picture, and the panel used to
    // blame them for already having videos.
    renderPanel({ selected: ["3_a"] });

    press();

    expect(screen.getByText("Seçili karelerin fotoğrafı henüz üretilmedi.")).toBeTruthy();
  });

  it("says the variant box is empty", () => {
    renderPanel();

    fireEvent.change(variantBox(), { target: { value: "" } });
    press();

    expect(screen.getByText("Varyant sayısı girilmedi — en az 1 yaz.")).toBeTruthy();
  });

  it("turns the variant box red while it is empty", () => {
    renderPanel();
    expect(variantBox().style.borderColor).toBe("");

    fireEvent.change(variantBox(), { target: { value: "" } });

    expect(variantBox().style.borderColor).toBe("var(--danger)");
  });

  it("clears the reason as soon as the count is typed", () => {
    // Both halves, because the second one alone is true of a panel that never answers at all.
    renderPanel();
    fireEvent.change(variantBox(), { target: { value: "" } });
    press();
    expect(screen.getByText("Varyant sayısı girilmedi — en az 1 yaz.")).toBeTruthy();

    fireEvent.change(variantBox(), { target: { value: "2" } });

    expect(screen.queryByText("Varyant sayısı girilmedi — en az 1 yaz.")).toBeNull();
  });

  it("clears the reason when another scope is picked", () => {
    // The reason belongs to the press that made it -- the scope it named and the frames it counted.
    // Moving either one turns it into a stale answer under a button about to be pressed again.
    renderPanel({ selected: ["3_a"] });
    press();
    expect(screen.getByText("Seçili karelerin fotoğrafı henüz üretilmedi.")).toBeTruthy();

    fireEvent.click(screen.getByText("Videosu olmayan kareler").closest("button"));

    expect(screen.queryByText("Seçili karelerin fotoğrafı henüz üretilmedi.")).toBeNull();
  });

  it("dresses the reason as the green card's red twin", () => {
    renderPanel({ frames: ALL_HELD });

    press();

    const card = screen.getByText("Tüm karelerin videosu var.").closest(".wf-stroke");
    expect(card.style.borderColor).toBe("var(--danger)");
    expect(card.style.background).toBe("var(--danger-bg)");
  });

  it("keeps the button pressable while the reason stands", () => {
    renderPanel({ frames: ALL_HELD });

    press();

    expect(screen.getByText("Tüm karelerin videosu var.")).toBeTruthy();
    expect(addButton().disabled).toBe(false);
  });

  it("locks the button only while the request is in flight", async () => {
    // The other half of the rule: nothing before the press locks it, and the one thing that does
    // lets go again.
    let land;
    renderPanel({ onQueue: () => new Promise((resolve) => { land = resolve; }) });
    expect(addButton().disabled).toBe(false);

    await act(async () => { press(); });

    expect(screen.getByText("Ekleniyor…").closest("button").disabled).toBe(true);
    await act(async () => { land({ added: 2 }); });
    expect(addButton().disabled).toBe(false);
  });
});

describe("LayerPanel — the panel's own shape", () => {
  const rowOf = (label) => screen.getByText(label).closest("button");
  const blocks = () => [...document.querySelectorAll("[data-label]")].map((one) => one.textContent);

  it("names the scope in full, the way its sound twin is named", () => {
    // A slip rather than a choice: the app's own description wrote this row out in full, and only
    // the video side got shortened.
    renderPanel();

    expect(screen.getByText("Videosu olmayan kareler")).toBeTruthy();
    expect(screen.queryByText("Videosu olmayanlar")).toBeNull();
  });

  it("puts a circle at the head of each scope row, bright on the chosen one", () => {
    renderPanel();

    const chosen = rowOf("Videosu olmayan kareler").querySelector("[data-dot]");
    const other = rowOf("Seçili kareler").querySelector("[data-dot]");
    expect(chosen.style.borderWidth).toBe("2px");
    expect(chosen.style.borderColor).toBe("var(--accent)");
    expect(other.style.borderWidth).toBe("1px");
    expect(other.style.borderColor).toBe("var(--ink-3)");
  });

  it("draws its rows with more room, the scope rows and the mode rows alike", () => {
    // One look for both families: the mode row is drawn the way a scope row is drawn, and giving
    // the measure to only one of them would leave 8px rows sitting under 10px rows.
    renderPanel();

    expect(rowOf("Videosu olmayan kareler").style.padding).toBe("10px 12px");
    expect(rowOf("Loop").style.padding).toBe("10px 12px");
  });

  const VIDEO_ROW = { id: "video", name: "Video üreticisi", installed: true };
  const offered = () => [...screen.getByRole("combobox").options].map((one) => one.textContent);

  it("offers the model in the same box the photo panel uses", () => {
    // One option, because H3 is the one video model (madde 435) -- a box that opens and shows the
    // only thing there is. The name is the server's (madde 247).
    renderPanel({ producer: { ...VIDEO_ROW, model: "MiniMax H3" } });

    expect(screen.getByRole("combobox").className).toContain("wf-input");
    expect(offered()).toEqual(["MiniMax H3"]);
  });

  it("names no model before the server has said which", () => {
    // Empty rather than a name made up here: a guess once showed one model over another's session.
    renderPanel();

    expect(offered()).toEqual([""]);
  });

  it("has no block of its own for the length", () => {
    renderPanel();

    expect(screen.queryByText("Süre")).toBeNull();
    expect(screen.queryByText(/5 saniye/)).toBeNull();
  });

  it("keeps only the blocks the design leaves standing", () => {
    renderPanel();

    // The Üretim row is gone: where a video is made from is the tabs over the panel (madde 317).
    expect(blocks()).toEqual(["Model", "Kapsam", "Üretim modu", "Varyant"]);
  });
});

describe("LayerPanel — another project holds the worker", () => {
  const ELSEWHERE = { job: { status: "running", project: "balo" }, busyElsewhere: true };

  it("is disabled while another project holds the worker", () => {
    // Madde 215: there is one worker, so a second project has to wait -- and the photo panel has
    // said so properly all along. This panel was never handed what it needed to say it.
    renderPanel(ELSEWHERE);

    expect(screen.getByText("Kuyruğa ekle").closest("button").disabled).toBe(true);
    expect(screen.getByText("Üretim sürüyor: balo — bitmesini bekle.")).toBeTruthy();
  });

  it("says the same thing on the sound panel", () => {
    render(
      <LayerPanel layer="audio" frames={FRAMES} selected={[]} producer={null} {...ELSEWHERE}
                  onQueue={() => Promise.resolve({ added: 1 })} onInstall={() => {}} />,
    );

    expect(screen.getByText("Kuyruğa ekle").closest("button").disabled).toBe(true);
    expect(screen.getByText("Üretim sürüyor: balo — bitmesini bekle.")).toBeTruthy();
  });

  it("shows a refusal where the press was made", () => {
    // busyElsewhere arrives with the poll, so the other run can start between two of them and the
    // press goes through. The side column draws one panel at a time, and neither of the two that
    // drew the server's answer is this one -- so the press did nothing visible at all.
    renderPanel({ error: "Zaten bir üretim sürüyor." });

    expect(screen.getByText("Zaten bir üretim sürüyor.")).toBeTruthy();
  });

  it("leaves the button alone when nobody else is running", () => {
    renderPanel();

    expect(screen.getByText("Kuyruğa ekle").closest("button").disabled).toBe(false);
    expect(screen.queryByText(/Üretim sürüyor/)).toBeNull();
  });
});

describe("LayerPanel — sending", () => {
  it("asks for every frame with no video when that is the scope", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 2 });
    renderPanel({ onQueue });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    // Madde 216: untouched, the video panel now asks for loop -- and the card confirms in that
    // mode's own noun.
    expect(onQueue).toHaveBeenCalledWith(null, 1, "loop");
    expect(screen.getByText("2 loop video kuyruğa eklendi")).toBeTruthy();
  });

  it("asks only for what is selected when that is the scope", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 1 });
    // Matched by identity, sent by file name: two different things, and the whole value of this
    // test is that it says so in one breath.
    renderPanel({ selected: ["0_a"], onQueue });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(["0_a.png"], 1, "loop");
  });

  it("sends the variant count along with the scope", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 4 });
    renderPanel({ onQueue });

    fireEvent.change(variantBox(), { target: { value: "2" } });
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null, 2, "loop");
  });

  it("does not explain who writes the prompt -- the frame's own page does", () => {
    // The sentence was read once and then took up room at the foot of the panel on every open.
    // Where a prompt is actually read -- the frame's page -- an empty one still says that the
    // language model will write it when its turn comes.
    renderPanel();

    expect(screen.queryByText(/LLM/)).toBeNull();
  });
});

describe("LayerPanel — the production mode", () => {
  const modeRow = (label) => screen.getByText(label).closest("button");

  it("offers the three ways a video can be made", () => {
    renderPanel();

    expect(screen.getByText("Üretim modu")).toBeTruthy();
    expect(modeRow("Standart")).toBeTruthy();
    expect(modeRow("Loop")).toBeTruthy();
    expect(modeRow("Sonrakine bağla")).toBeTruthy();
  });

  it("opens on loop", () => {
    // Madde 216: loop is what gets asked for, so it is what the panel offers first.
    renderPanel();

    expect(modeRow("Loop").style.borderColor).toBe("var(--accent)");
    expect(modeRow("Standart").style.borderColor).toBe("var(--border)");
    expect(modeRow("Sonrakine bağla").style.borderColor).toBe("var(--border)");
  });

  it("stands between the scope and the variant count", () => {
    // The design's order, and the reason it is that order: the mode is part of deciding what to
    // make, so it belongs on the scope's side of the panel rather than after the count.
    const { container } = renderPanel();

    const text = container.textContent;
    expect(text.indexOf("Üretim modu")).toBeGreaterThan(text.indexOf("Kapsam"));
    expect(text.indexOf("Üretim modu")).toBeLessThan(text.indexOf("Varyant"));
  });

  it("sends the mode that was picked", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 2 });
    renderPanel({ onQueue });

    fireEvent.click(modeRow("Loop"));
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null, 1, "loop");
  });

  it("sends loop when nobody touched the row", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 2 });
    renderPanel({ onQueue });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null, 1, "loop");
  });

});

describe("LayerPanel — linking wants neighbours", () => {
  const modeRow = (label) => screen.getByText(label).closest("button");
  // 2_a and 0_a sit either side of 1_a in the gallery, so picking the two of them leaves a hole.
  const SCATTERED = ["2_a", "0_a"];
  const NEIGHBOURS = ["2_a", "1_a"];
  const WHY = "Zincir ancak bitişik karelerde kapanır — arada seçilmemiş kare var.";

  it("closes the option when the chosen frames are not neighbours", () => {
    renderPanel({ selected: SCATTERED });

    expect(modeRow("Sonrakine bağla").disabled).toBe(true);
  });

  it("says why, in one line, under the option it closed", () => {
    renderPanel({ selected: SCATTERED });

    expect(screen.getByText(WHY)).toBeTruthy();
  });

  it("opens the option again when the hole is closed", () => {
    renderPanel({ selected: NEIGHBOURS });

    expect(modeRow("Sonrakine bağla").disabled).toBe(false);
    expect(screen.queryByText(WHY)).toBeNull();
  });

  it("leaves the option open when the scope is every frame with no video", () => {
    // That set is scattered by its nature -- the frames between its members are the ones that
    // already have a video -- and each of its frames still has a next one to end on.
    renderPanel();

    expect(modeRow("Sonrakine bağla").disabled).toBe(false);
    expect(screen.queryByText(WHY)).toBeNull();
  });

  it("counts one frame as neighbours of itself", () => {
    renderPanel({ selected: ["1_a"] });

    expect(modeRow("Sonrakine bağla").disabled).toBe(false);
  });

  it("drops back to the plain mode when the selection breaks apart under it", async () => {
    // Otherwise a row nobody can click keeps going to the queue: the gallery is where the
    // selection changes, and the panel never hears a second click to correct itself.
    const onQueue = vi.fn().mockResolvedValue({ added: 1 });
    const { rerender } = renderPanel({ selected: NEIGHBOURS, onQueue });
    fireEvent.click(modeRow("Sonrakine bağla"));

    rerender(
      <LayerPanel layer="video" frames={FRAMES} selected={SCATTERED} producer={null}
                  onQueue={onQueue} onInstall={() => {}} />,
    );
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(["2_a.png", "0_a.png"], 1, "standard");
  });
});

describe("LayerPanel — the estimate speaks the mode", () => {
  const modeRow = (label) => screen.getByText(label).closest("button");

  it("says what a loop video is and what it does", () => {
    renderPanel();

    fireEvent.click(modeRow("Loop"));

    expect(screen.getByText("2 loop video üretilecek — her video kendine döner.")).toBeTruthy();
  });

  it("says what a linked video is and where it ends", () => {
    renderPanel();

    fireEvent.click(modeRow("Sonrakine bağla"));

    expect(screen.getByText("2 bağlı video üretilecek — her video sıradaki karede biter."))
      .toBeTruthy();
  });

  it("leaves no trace of the plain sentence once a mode is picked", () => {
    // The whole point of the item: three modes, three sentences, and the old single template gone
    // from all of them. Asserting the new sentence alone would pass with both on screen.
    renderPanel();

    fireEvent.click(modeRow("Loop"));

    expect(screen.queryByText(/her kare kendi videosunu alır/)).toBeNull();
  });

  it("confirms in the mode's own words", async () => {
    renderPanel({ onQueue: () => Promise.resolve({ added: 2 }) });

    fireEvent.click(modeRow("Loop"));
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(screen.getByText("2 loop video kuyruğa eklendi")).toBeTruthy();
  });

  it("keeps the words the queue was actually sent with", async () => {
    // The card stands for ten seconds and the row is one click away. Reading the live mode would
    // let it report a loop run that was never asked for.
    renderPanel({ onQueue: () => Promise.resolve({ added: 2 }) });

    fireEvent.click(modeRow("Loop"));
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });
    fireEvent.click(modeRow("Standart"));

    expect(screen.getByText("2 loop video kuyruğa eklendi")).toBeTruthy();
  });
});

describe("LayerPanel — the estimate warns about copies", () => {
  const modeRow = (label) => screen.getByText(label).closest("button");
  const COPY = "videolu 1 kare için yeniler kopya kare olur, eskisi durur.";

  it("says a frame that already has this layer will gain a twin", () => {
    // Production never writes over a layer that is there: it makes a copy frame beside it. Until
    // now nothing said so and the gallery growing by one was the first news of it.
    renderPanel({ selected: ["1_a"] });

    expect(screen.getByText(`1 loop video üretilecek — ${COPY}`)).toBeTruthy();
  });

  it("counts only the frames in scope that hold the layer", () => {
    // Two frames go to the queue, one of them is the copy. The two numbers in the line are
    // different numbers and a single count would read as either.
    renderPanel({ selected: ["1_a", "0_a"] });

    expect(screen.getByText(`2 loop video üretilecek — ${COPY}`)).toBeTruthy();
  });

  it("never warns on the scope that leaves those frames out", () => {
    // Videosu olmayanlar cannot contain a frame with a video, so the count is zero by its own
    // definition rather than by a second rule about which scope may warn.
    renderPanel();

    expect(screen.queryByText(/kopya kare olur/)).toBeNull();
  });

  it("puts the warning where the mode's own line would have been", () => {
    // The mode is still said -- it is in the head of the sentence -- so nothing is lost by giving
    // the tail to the news the user has no other way of hearing.
    renderPanel({ selected: ["1_a"] });

    fireEvent.click(modeRow("Loop"));

    expect(screen.getByText(`1 loop video üretilecek — ${COPY}`)).toBeTruthy();
    expect(screen.queryByText(/kendine döner/)).toBeNull();
  });

  it("warns in the sound panel's own words", () => {
    const held = done("2_a.png", { video: "2_a_V1_0.mp4", audio: "2_a_A1_0.wav" });

    render(
      <LayerPanel layer="audio" frames={[done("0_a.png"), held]} selected={["2_a"]} producer={null}
                  onQueue={() => Promise.resolve({ added: 1 })} onInstall={() => {}} />,
    );

    expect(screen.getByText(
      "1 ses üretilecek — sesi olan 1 kare için yeniler kopya kare olur, eskisi durur."))
      .toBeTruthy();
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

  it("still asks for the plain mode", async () => {
    // Madde 216: the mode is kept by both panels though only the video one draws the row, so a
    // default written without asking which layer it belongs to would travel with a sound job too --
    // and the server refuses any mode but the plain one here (production_mode.validate). Nothing on
    // screen would say why; the user would only see that no sound was made.
    const onQueue = vi.fn().mockResolvedValue({ added: 1 });
    renderSound({ onQueue });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null, 1, "standard");
  });

  it("already names its own scope in full", () => {
    // The anchor the video row is being matched to: this side was written out from the start, and
    // this test is what keeps it from drifting the other way.
    renderSound();

    expect(screen.getByText("Videosu olup sesi olmayan kareler")).toBeTruthy();
  });

  it("shows its own model in that same box", () => {
    renderSound();

    expect([...screen.getByRole("combobox").options].map((one) => one.textContent))
      .toEqual(["MMAudio v2"]);
  });

  it("has no length block either", () => {
    renderSound();

    expect(screen.queryByText("Süre")).toBeNull();
    expect(screen.queryByText("Ses videonun süresince üretilir.")).toBeNull();
  });

  it("says all the frames already have a sound", () => {
    renderSound({ frames: [
      done("1_a.png", { video: "1_a_V1_0.mp4", audio: "1_a_V1_0_S1_0.wav" })] });

    fireEvent.click(screen.getByText("Kuyruğa ekle").closest("button"));

    expect(screen.getByText("Tüm karelerin sesi var.")).toBeTruthy();
  });

  it("says nothing has a video to lay a sound over", () => {
    // Not the video panel's sentence: what is missing under a sound is a video, not a photo. An
    // empty project reads this too, and it is the nearer thing that is missing.
    renderSound({ frames: [done("0_a.png")] });

    fireEvent.click(screen.getByText("Kuyruğa ekle").closest("button"));

    expect(screen.getByText("Videosu olan kare yok.")).toBeTruthy();
  });

  it("says the chosen frames have no video yet", () => {
    renderSound({ selected: ["0_a"] });

    fireEvent.click(screen.getByText("Kuyruğa ekle").closest("button"));

    expect(screen.getByText("Seçili karelerin videosu henüz üretilmedi.")).toBeTruthy();
  });

  it("confirms in its own words", async () => {
    renderSound();

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(screen.getByText("1 ses kuyruğa eklendi")).toBeTruthy();
  });

  it("never offers a mode -- a sound ends nowhere", () => {
    // Loop and "Sonrakine bağla" are both about the picture a video ends on. A sound is laid over
    // the whole of one video and arrives nowhere, so there is nothing here to choose between.
    renderSound();

    expect(screen.queryByText("Üretim modu")).toBeNull();
    expect(screen.queryByText("Loop")).toBeNull();
  });

  it("still sends the plain mode, so the server reads one call shape", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 1 });
    renderSound({ onQueue });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null, 1, "standard");
  });

  it("does not explain who writes the prompt either", () => {
    // Both panels are one component and the design asks for them to be identical; leaving the
    // sentence on one of them would part them where nothing else does.
    renderSound();

    expect(screen.queryByText(/LLM/)).toBeNull();
  });
});

describe("LayerPanel — producing from the reference pool", () => {
  const promptBox = () => screen.getByLabelText("Prompt listesi");

  function openReference(props) {
    const view = renderPanel(props);
    fireEvent.click(screen.getByText("Referanstan"));
    return view;
  }

  it("asks the video panel where the video comes from, and never the sound panel", () => {
    renderPanel();
    // Kareden, not Standart: Standart already names a mode on the Kareden tab itself.
    expect(screen.getByText("Kareden")).toBeTruthy();
    expect(screen.getByText("Referanstan")).toBeTruthy();

    renderPanel({ layer: "audio" });
    // A sound is laid over a video that already exists; the pool has nothing to do with it.
    expect(screen.queryAllByText("Referanstan")).toHaveLength(1);
  });

  it("closes the rows that have no meaning without frames", () => {
    openReference();

    // No frame is involved at all: production makes cards (madde 303).
    expect(screen.queryByText("Videosu olmayan kareler")).toBeNull();
    // Loop and linking are a plain video's business (the roadmap's own decision).
    expect(screen.queryByText("Loop")).toBeNull();
    expect(screen.queryByText("Sonrakine bağla")).toBeNull();
  });

  it("takes a list of prompts, the way the photo panel does", () => {
    openReference();

    expect(promptBox()).toBeTruthy();
  });

  it("counts the cards the press would make", () => {
    openReference();

    fireEvent.change(promptBox(), { target: { value: '["gotik kız", "dans"]' } });
    fireEvent.change(variantBox(), { target: { value: "3" } });

    expect(screen.getByText("2 prompt × 3 varyant = 6 kart.")).toBeTruthy();
  });

  it("reads a Python list with a name in front, the way the photo panel does", () => {
    // Madde 323: a list that works in the photo panel works here -- pasted out of a notebook cell,
    // in single quotes, with its name in front.
    openReference();

    fireEvent.change(promptBox(), { target: { value: "PROMPTS = ['a', 'b']" } });

    expect(screen.getByText("2 prompt × 1 varyant = 2 kart.")).toBeTruthy();
  });

  it("reads a tuple, in either quote", () => {
    openReference();

    fireEvent.change(promptBox(), { target: { value: `("gotik kız", 'dans')` } });

    expect(screen.getByText("2 prompt × 1 varyant = 2 kart.")).toBeTruthy();
  });

  it("leaves the blank items out of the count", () => {
    // An empty item is how a line is switched off in the photo panel's list (prompt_list.py).
    openReference();

    fireEvent.change(promptBox(), { target: { value: '["gotik kız", "", "  ", "dans"]' } });

    expect(screen.getByText("2 prompt × 1 varyant = 2 kart.")).toBeTruthy();
  });

  it("says nothing under the button while the box is empty or its list cannot be read", () => {
    // Madde 323: the line counts what a press would make and nothing else. What is wrong with a
    // list is the server's to say, when the button is pressed.
    openReference();
    expect(screen.queryByText(/biçiminde olmalı/)).toBeNull();

    fireEvent.change(promptBox(), { target: { value: "gotik kız" } });

    expect(screen.queryByText(/= \d+ kart/)).toBeNull();
    expect(screen.queryByText(/biçiminde olmalı/)).toBeNull();
    expect(screen.queryByText(/Format hatası/)).toBeNull();
  });

  it("sends a list it cannot read as it was typed", async () => {
    // Madde 323: the screen reads the list only to count it. The press goes whatever that reading
    // made of it, and the refusal comes back in the server's own words (prompt_list.py).
    const onQueue = vi.fn().mockResolvedValue(null);
    openReference({ onQueue });

    fireEvent.change(promptBox(), { target: { value: "gotik kız" } });
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).toHaveBeenCalledWith(null, 1, "reference", "gotik kız");
    expect(screen.queryByText(/biçiminde olmalı/)).toBeNull();
  });

  it("sends the prompts and the variants under the reference kind", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 6 });
    openReference({ onQueue });

    fireEvent.change(promptBox(), { target: { value: '["gotik kız", "dans"]' } });
    fireEvent.change(variantBox(), { target: { value: "3" } });
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    // No frames: what the queue is handed is the words and how many of each.
    expect(onQueue).toHaveBeenCalledWith(null, 3, "reference", '["gotik kız", "dans"]');
  });
});

describe("LayerPanel — the two tabs", () => {
  it("opens the video panel on Kareden, with the frame form", () => {
    const view = renderPanel();

    expect(tab("Kareden").className).toContain("is-on");
    expect(tab("Referanstan").className).not.toContain("is-on");
    expect(labels(view)).toEqual(["Model", "Kapsam", "Üretim modu", "Varyant"]);
    // The row the tabs replace, and its old word for the frame side.
    expect(screen.queryByText("Üretim")).toBeNull();
    expect(screen.queryByText("Karelerden")).toBeNull();
  });

  it("lays Referanstan out in the design's order", () => {
    const view = renderPanel();

    fireEvent.click(tab("Referanstan"));

    expect(tab("Referanstan").className).toContain("is-on");
    expect(tab("Kareden").className).not.toContain("is-on");
    expect(labels(view)).toEqual(["Model", "Referanslar", "Prompt listesi", "Varyant"]);
  });

  it("gives the sound panel no tabs", () => {
    // A sound is laid over a video that already exists: the pool has nothing to give it.
    renderPanel({ layer: "audio" });

    expect(screen.queryByText("Kareden")).toBeNull();
    expect(screen.queryByText("Referanstan")).toBeNull();
  });
});

describe("LayerPanel — what Referanstan keeps", () => {
  const promptBox = () => screen.getByLabelText("Prompt listesi");

  it("keeps its prompt list and variants across the tabs, and Kareden keeps its own one", () => {
    renderPanel();
    fireEvent.click(tab("Referanstan"));
    fireEvent.change(promptBox(), { target: { value: '["gotik kız"]' } });
    fireEvent.change(variantBox(), { target: { value: "3" } });

    fireEvent.click(tab("Kareden"));
    // Kareden is the frame form as it was: its count starts at one on every opening.
    expect(variantBox().value).toBe("1");

    fireEvent.click(tab("Referanstan"));
    expect(promptBox().value).toBe('["gotik kız"]');
    expect(variantBox().value).toBe("3");
  });

  it("keeps them when the panel is built again, which opens on Kareden", async () => {
    // Opening the panel from the rail, or stepping into a frame and back, builds it afresh.
    const first = renderPanel({ project: "düğün-a" });
    await act(async () => { fireEvent.click(tab("Referanstan")); });
    fireEvent.change(promptBox(), { target: { value: '["gotik kız"]' } });
    fireEvent.change(variantBox(), { target: { value: "3" } });
    first.unmount();

    renderPanel({ project: "düğün-a" });

    expect(tab("Kareden").className).toContain("is-on");
    await act(async () => { fireEvent.click(tab("Referanstan")); });
    expect(promptBox().value).toBe('["gotik kız"]');
    expect(variantBox().value).toBe("3");
    // A draft is newer than the record by definition, so the record is asked once per visit.
    expect(getReferenceSettings).toHaveBeenCalledTimes(1);
  });

  it("fills the boxes from the project's record when nothing was typed this visit", async () => {
    getReferenceSettings.mockResolvedValue({ prompts: '["kayıt"]', variants: 4 });
    renderPanel({ project: "düğün-b" });

    await act(async () => { fireEvent.click(tab("Referanstan")); });

    expect(getReferenceSettings).toHaveBeenCalledWith("düğün-b");
    expect(promptBox().value).toBe('["kayıt"]');
    expect(variantBox().value).toBe("4");
  });

  it("opens Referanstan on one variant when the record has none", async () => {
    renderPanel({ project: "düğün-c" });

    await act(async () => { fireEvent.click(tab("Referanstan")); });

    expect(getReferenceSettings).toHaveBeenCalledWith("düğün-c");
    expect(variantBox().value).toBe("1");
  });

  it("does not write the record over what was typed while it was on its way", async () => {
    let answer;
    getReferenceSettings.mockReturnValue(new Promise((resolve) => { answer = resolve; }));
    renderPanel({ project: "düğün-d" });
    fireEvent.click(tab("Referanstan"));
    fireEvent.change(promptBox(), { target: { value: '["yeni"]' } });

    await act(async () => { answer({ prompts: '["eski"]', variants: 5 }); });

    expect(getReferenceSettings).toHaveBeenCalledWith("düğün-d");
    // Neither box: a draft is one thing, never half the record and half the hand.
    expect(promptBox().value).toBe('["yeni"]');
    expect(variantBox().value).toBe("1");
  });

  it("writes the record first when the press goes out, then sends the work", async () => {
    const onQueue = vi.fn().mockResolvedValue({ added: 3 });
    renderPanel({ project: "düğün-e", onQueue });
    await act(async () => { fireEvent.click(tab("Referanstan")); });
    fireEvent.change(promptBox(), { target: { value: '["gotik kız"]' } });
    fireEvent.change(variantBox(), { target: { value: "3" } });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(saveReferenceSettings).toHaveBeenCalledWith(
      "düğün-e", { prompts: '["gotik kız"]', variants: 3 });
    expect(onQueue).toHaveBeenCalledWith(null, 3, "reference", '["gotik kız"]');
    expect(saveReferenceSettings.mock.invocationCallOrder[0])
      .toBeLessThan(onQueue.mock.invocationCallOrder[0]);

    // Kareden's press is about frames: it writes no reference record.
    fireEvent.click(tab("Kareden"));
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });
    expect(saveReferenceSettings).toHaveBeenCalledTimes(1);
  });

  it("sends nothing when the record cannot be written", async () => {
    // The photo panel's rule: the record and the work land in the same folder, so a record that
    // cannot be written means the work could not be either.
    saveReferenceSettings.mockRejectedValue(new Error("Proje yok: düğün-g"));
    const onQueue = vi.fn();
    renderPanel({ project: "düğün-g", onQueue });
    await act(async () => { fireEvent.click(tab("Referanstan")); });
    fireEvent.change(promptBox(), { target: { value: '["gotik kız"]' } });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueue).not.toHaveBeenCalled();
    expect(screen.getByText("Proje yok: düğün-g")).toBeTruthy();
  });
});

describe("LayerPanel — the pool's one button", () => {
  it("asks for the pool on Referanstan and for the cards on Kareden", () => {
    const onShowPool = vi.fn();
    renderPanel({ onShowPool });

    fireEvent.click(tab("Referanstan"));
    expect(onShowPool).toHaveBeenLastCalledWith(true);

    fireEvent.click(tab("Kareden"));
    expect(onShowPool).toHaveBeenLastCalledWith(false);
  });

  it("closes the pool from the Referanslar block while it is shown", () => {
    const onShowPool = vi.fn();
    renderPanel({ poolShown: true, onShowPool });
    fireEvent.click(tab("Referanstan"));

    fireEvent.click(screen.getByText("Referansları kapat"));

    expect(onShowPool).toHaveBeenLastCalledWith(false);
  });

  it("opens it again from the same place while the cards are shown", () => {
    const onShowPool = vi.fn();
    renderPanel({ onShowPool });
    fireEvent.click(tab("Referanstan"));

    fireEvent.click(screen.getByText("Referansları aç"));

    expect(onShowPool).toHaveBeenLastCalledWith(true);
  });

  it("gives the cards back when the panel goes", () => {
    // The pool belongs to this panel's tab: with the panel gone there is nothing it belongs to.
    const onShowPool = vi.fn();
    const view = renderPanel({ onShowPool });
    fireEvent.click(tab("Referanstan"));

    view.unmount();

    expect(onShowPool).toHaveBeenLastCalledWith(false);
  });
});

describe("LayerPanel — what stops a run from the pool (madde 324)", () => {
  // The design's own sentence (V2-UPDATE §1), and the server's too. The one before it -- that the
  // session's video model was not H3 -- went with WAN (madde 435).
  const H3_ONLY =
    "Referanstan üretim için H3 gerekiyor — bu oturumda başka bir video modeli kurulu.";
  const NO_REFERENCES = "Havuzda referans yok — önce en az bir referans ekle.";
  const LIMITS = { picture: 9, video: 3, audio: 3 };
  // The pool the way the server answers it.
  const pool = (references) => ({ references, limits: LIMITS });
  const EMPTY = pool([]);
  const KEDI = pool([{ name: "kedi.png", kind: "picture", seconds: null, slot: 1 }]);
  // The video row as the server gives it: H3's, the one video model, which reads the pool.
  const H3 = { id: "video", name: "Video üreticisi", installed: true, model: "MiniMax H3" };
  const MISSING = { ...H3, installed: false };

  const promptBox = () => screen.getByLabelText("Prompt listesi");
  const addButton = () => screen.getByText("Kuyruğa ekle").closest("button");
  const write = (text) => fireEvent.change(promptBox(), { target: { value: text } });

  // One project per test, and the same one when a test hands the panel a new pool: a rerender of
  // the same panel, as when the pool in the middle answers again.
  async function openReference(props) {
    const project = freshProject();
    const panel = (more) => (
      <LayerPanel layer="video" project={project} frames={FRAMES} selected={[]} producer={H3}
                  onQueue={() => Promise.resolve({ added: 1 })} onInstall={() => {}}
                  poolShown={false} onShowPool={() => {}} {...props} {...more} />
    );
    const view = render(panel());
    await act(async () => { fireEvent.click(tab("Referanstan")); });
    return { again: (more) => view.rerender(panel(more)) };
  }

  it("says an empty pool before anything is pressed, between the variant box and the button",
     async () => {
    await openReference({ pool: EMPTY });

    const line = screen.getByText(NO_REFERENCES);
    // Right above the button it stops: the design's own place for it.
    expect(variantBox().compareDocumentPosition(line) & Node.DOCUMENT_POSITION_FOLLOWING)
      .toBeTruthy();
    expect(line.compareDocumentPosition(addButton()) & Node.DOCUMENT_POSITION_FOLLOWING)
      .toBeTruthy();
  });

  it("lets the line go the moment the pool holds one reference of any kind", async () => {
    const view = await openReference({ pool: EMPTY });
    write('["gotik kız"]');
    expect(screen.getByText(NO_REFERENCES)).toBeTruthy();
    expect(addButton().disabled).toBe(true);

    // A sound alone: one reference of any kind is enough (V2-UPDATE §1).
    view.again({ pool: pool([{ name: "kisa.wav", kind: "audio", seconds: 3, slot: 1 }]) });

    expect(screen.queryByText(NO_REFERENCES)).toBeNull();
    expect(addButton().disabled).toBe(false);
  });

  it("never says another video model is in the way, and opens the button", async () => {
    // H3 is the one video model there is (madde 435): the row says nothing about the pool, and
    // nothing on Referanstan waits on it.
    await openReference({ producer: H3, pool: KEDI });
    write('["gotik kız"]');

    expect(screen.queryByText(H3_ONLY)).toBeNull();
    expect(addButton().disabled).toBe(false);
  });

  it("says an empty pool while the video producer is missing", async () => {
    // The card at the top says what is missing; the line says what the pool lacks.
    await openReference({ producer: MISSING, pool: EMPTY });

    expect(screen.queryByText(H3_ONLY)).toBeNull();
    expect(screen.getByText(NO_REFERENCES)).toBeTruthy();
  });

  it("keeps the button closed while the prompt box is empty", async () => {
    await openReference({ pool: KEDI });
    expect(addButton().disabled).toBe(true);

    write("  \n ");
    expect(addButton().disabled).toBe(true);

    write('["gotik kız"]');
    expect(addButton().disabled).toBe(false);
  });

  it("keeps the line and its locks to Referanstan", async () => {
    await openReference({ pool: EMPTY });
    expect(screen.getByText(NO_REFERENCES)).toBeTruthy();

    fireEvent.click(tab("Kareden"));

    // The frame form is as it was: nothing it lacks locks it before the press (Fark 27).
    expect(screen.queryByText(NO_REFERENCES)).toBeNull();
    expect(addButton().disabled).toBe(false);
  });
});

describe("LayerPanel — the H3 video length (madde 424)", () => {
  // The video row the way the server gives it. H3 is the one video model (madde 435), so the row
  // says nothing about which: once it is read, the length is drawn.
  const H3 = { id: "video", name: "Video üreticisi", installed: true, model: "MiniMax H3" };
  const AUDIO = { id: "audio", name: "Ses üreticisi", installed: true, model: "MMAudio v2" };
  const PLAIN = ["Model", "Kapsam", "Üretim modu", "Varyant"];
  const LOOP_LINE = "2 loop video üretilecek — her video kendine döner.";

  const lengthButton = (seconds) => screen.getByRole("button", { name: `${seconds} saniye` });
  const chosen = () => [4, 8, 12].map((one) => lengthButton(one).className.includes("is-on"));

  // The video row read, unless told otherwise, and the project's length with it.
  async function renderReady(props) {
    const view = renderPanel({ producer: H3, ...props });
    await act(async () => {});
    return view;
  }

  it("sits right under the Model box, the project's 8 chosen", async () => {
    const project = freshProject();
    const view = await renderReady({ project });

    expect(labels(view)).toEqual(["Model", "Video uzunluğu", "Mutlu son", "Kapsam", "Üretim modu",
                                  "Varyant"]);
    // One segment, in the design's order; the number and its unit never part.
    const segment = lengthButton(8).parentElement;
    expect(segment.className).toContain("wf-segment");
    expect([...segment.children].map((one) => one.textContent))
      .toEqual(["4\u00a0sn", "8\u00a0sn", "12\u00a0sn"]);
    expect(chosen()).toEqual([false, true, false]);
    expect(getVideoLength).toHaveBeenCalledWith(project);
  });

  it("stands in the same place on Referanstan", async () => {
    const view = await renderReady();

    await act(async () => { fireEvent.click(tab("Referanstan")); });

    expect(labels(view))
      .toEqual(["Model", "Video uzunluğu", "Mutlu son", "Referanslar", "Prompt listesi", "Varyant"]);
  });

  it("opens on the length the project saved", async () => {
    getVideoLength.mockResolvedValue(12);
    await renderReady();

    expect(chosen()).toEqual([false, false, true]);
  });

  it("marks the pressed length at once and writes it to the project", async () => {
    saveVideoLength.mockReturnValue(new Promise(() => {}));
    const project = freshProject();
    await renderReady({ project });

    fireEvent.click(lengthButton(12));

    expect(chosen()).toEqual([false, false, true]);
    expect(saveVideoLength).toHaveBeenCalledWith(project, 12);
  });

  it("stays where it is, with its choice, when the tab changes", async () => {
    await renderReady();
    await act(async () => { fireEvent.click(lengthButton(12)); });

    await act(async () => { fireEvent.click(tab("Referanstan")); });
    expect(chosen()).toEqual([false, false, true]);
    await act(async () => { fireEvent.click(tab("Kareden")); });
    expect(chosen()).toEqual([false, false, true]);
  });

  it("leaves every other box as it was", async () => {
    await renderReady();
    fireEvent.click(screen.getByText("Standart").closest("button"));
    fireEvent.change(variantBox(), { target: { value: "3" } });

    await act(async () => { fireEvent.click(lengthButton(12)); });

    expect(variantBox().value).toBe("3");
    expect(screen.getByText("6 video üretilecek — her kare kendi videosunu alır. 12 sn."))
      .toBeTruthy();
  });

  it("opens a rebuilt panel on the length it knew, and the server's answer stands", async () => {
    getVideoLength.mockResolvedValue(12);
    (await renderReady({ project: "uzunluk-a" })).unmount();
    let answer;
    getVideoLength.mockReturnValue(new Promise((resolve) => { answer = resolve; }));

    await renderReady({ project: "uzunluk-a" });
    // Drawn at once: a block that came in a beat after every opening would push the panel down.
    expect(chosen()).toEqual([false, false, true]);

    await act(async () => { answer(4); });
    expect(chosen()).toEqual([true, false, false]);
  });

  it("keeps a length pressed while the read is on its way", async () => {
    (await renderReady({ project: "uzunluk-b" })).unmount();
    let answer;
    getVideoLength.mockReturnValue(new Promise((resolve) => { answer = resolve; }));
    await renderReady({ project: "uzunluk-b" });

    await act(async () => { fireEvent.click(lengthButton(4)); });
    await act(async () => { answer(12); });

    expect(chosen()).toEqual([true, false, false]);
  });

  it("is not drawn while the model is not read yet", async () => {
    const view = await renderReady({ producer: null });

    expect(labels(view)).toEqual(PLAIN);
    expect(screen.getByText(LOOP_LINE)).toBeTruthy();
    expect(getVideoLength).not.toHaveBeenCalled();
  });

  it("is drawn while the video producer is not installed yet", async () => {
    // The Model box names H3 either way, and the length is the project's, not the producer's.
    const view = await renderReady({ producer: { ...H3, installed: false } });

    expect(labels(view)).toContain("Video uzunluğu");
  });

  it("waits for the project's length before it draws the choice or says the length", async () => {
    getVideoLength.mockReturnValue(new Promise(() => {}));
    getHappyEnding.mockReturnValue(new Promise(() => {}));
    const view = await renderReady();

    expect(labels(view)).toEqual(PLAIN);
    expect(screen.getByText(LOOP_LINE)).toBeTruthy();
  });

  it("leaves the choice out, and says nothing of its own, when the length cannot be read",
     async () => {
    getVideoLength.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));
    getHappyEnding.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));
    const view = await renderReady();

    expect(labels(view)).toEqual(PLAIN);
    expect(screen.getByText(LOOP_LINE)).toBeTruthy();
    expect(screen.queryByText("Sunucuya ulaşılamadı — bağlantıyı kontrol et.")).toBeNull();
  });

  it("has no length on the sound panel", async () => {
    const view = await renderReady({ layer: "audio", producer: AUDIO,
                                     frames: [done("0_a.png", { video: "0_a_V1_0.mp4" })] });

    expect(labels(view)).toEqual(["Model", "Kapsam", "Varyant"]);
    expect(screen.getByText("1 ses üretilecek — her kare kendi sesini alır.")).toBeTruthy();
    expect(getVideoLength).not.toHaveBeenCalled();
  });

  it.each([
    ["Loop", "2 loop video üretilecek — her video kendine döner. 8 sn."],
    ["Sonrakine bağla", "2 bağlı video üretilecek — her video sıradaki karede biter. 8 sn."],
    ["Standart", "2 video üretilecek — her kare kendi videosunu alır. 8 sn."],
  ])("ends the line under the button with the length on %s", async (mode, line) => {
    await renderReady();

    fireEvent.click(screen.getByText(mode).closest("button"));

    // The space is unbreakable: the number never ends a line with its unit alone on the next.
    expect(screen.getByText(line).textContent.endsWith(" 8\u00a0sn.")).toBe(true);
  });

  it("ends the copy warning with the length too", async () => {
    await renderReady({ selected: ["1_a"] });

    expect(screen.getByText("1 loop video üretilecek — videolu 1 kare için yeniler kopya kare "
                            + "olur, eskisi durur. 8 sn.")).toBeTruthy();
  });

  it("says the length that was chosen", async () => {
    await renderReady();

    await act(async () => { fireEvent.click(lengthButton(12)); });

    expect(screen.getByText(`${LOOP_LINE} 12 sn.`)).toBeTruthy();
  });

  it("ends Referanstan's line with the length", async () => {
    await renderReady();
    await act(async () => { fireEvent.click(tab("Referanstan")); });

    fireEvent.change(screen.getByLabelText("Prompt listesi"),
                     { target: { value: '["gotik kız", "dans"]' } });
    fireEvent.change(variantBox(), { target: { value: "3" } });

    expect(screen.getByText("2 prompt × 3 varyant = 6 kart. 8 sn.")).toBeTruthy();
  });

  it("puts no length on the card that says what the queue took", async () => {
    await renderReady({ onQueue: () => Promise.resolve({ added: 2 }) });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(screen.getByText("2 loop video kuyruğa eklendi")).toBeTruthy();
  });

  it("says the server's sentence when the length cannot be written, and goes back to the saved one",
     async () => {
    saveVideoLength.mockRejectedValue(new Error("Proje yok: düğün"));
    await renderReady();

    await act(async () => { fireEvent.click(lengthButton(12)); });

    // The panel's own red card under the button, where its other failures are said.
    const card = screen.getByText("Proje yok: düğün");
    expect(card.closest(".wf-stroke").style.borderColor).toBe("var(--danger)");
    expect(screen.getByText("Kuyruğa ekle").compareDocumentPosition(card)
           & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(chosen()).toEqual([false, true, false]);
  });

  it("takes the card away with the next press that is written", async () => {
    saveVideoLength.mockRejectedValueOnce(new Error("Proje yok: düğün"));
    await renderReady();
    await act(async () => { fireEvent.click(lengthButton(12)); });

    await act(async () => { fireEvent.click(lengthButton(4)); });

    expect(screen.queryByText("Proje yok: düğün")).toBeNull();
    expect(chosen()).toEqual([true, false, false]);
  });
});

describe("LayerPanel — Mutlu son (madde 426)", () => {
  const H3 = { id: "video", name: "Video üreticisi", installed: true, model: "MiniMax H3" };
  const AUDIO = { id: "audio", name: "Ses üreticisi", installed: true, model: "MMAudio v2" };
  const LOOP_LINE = "2 loop video üretilecek — her video kendine döner.";

  const off = () => screen.getByRole("button", { name: "Mutlu son kapalı" });
  const on = () => screen.getByRole("button", { name: "Mutlu son açık" });
  const chosen = () => [off(), on()].map((one) => one.className.includes("is-on"));

  async function renderReady(props) {
    const view = renderPanel({ producer: H3, ...props });
    await act(async () => {});
    return view;
  }

  it("sits right under the length, off for a project that saved nothing", async () => {
    const project = freshProject();
    const view = await renderReady({ project });

    const order = labels(view);
    expect(order.indexOf("Mutlu son")).toBe(order.indexOf("Video uzunluğu") + 1);
    // The length's own segment, with two buttons: what the panel's neighbours already look like.
    const segment = off().parentElement;
    expect(segment.className).toContain("wf-segment");
    expect([...segment.children].map((one) => one.textContent)).toEqual(["Kapalı", "Açık"]);
    expect(chosen()).toEqual([true, false]);
    expect(getHappyEnding).toHaveBeenCalledWith(project);
  });

  it("stands in the same place on Referanstan", async () => {
    const view = await renderReady();

    await act(async () => { fireEvent.click(tab("Referanstan")); });

    const order = labels(view);
    expect(order.indexOf("Mutlu son")).toBe(order.indexOf("Video uzunluğu") + 1);
  });

  it("opens on what the project saved", async () => {
    getHappyEnding.mockResolvedValue(true);
    await renderReady();

    expect(chosen()).toEqual([false, true]);
  });

  it("turns on at once and writes it to the project", async () => {
    saveHappyEnding.mockReturnValue(new Promise(() => {}));
    const project = freshProject();
    await renderReady({ project });

    fireEvent.click(on());

    expect(chosen()).toEqual([false, true]);
    expect(saveHappyEnding).toHaveBeenCalledWith(project, true);
  });

  it("keeps its choice when the tab changes", async () => {
    await renderReady();
    await act(async () => { fireEvent.click(on()); });

    await act(async () => { fireEvent.click(tab("Referanstan")); });
    expect(chosen()).toEqual([false, true]);
    await act(async () => { fireEvent.click(tab("Kareden")); });
    expect(chosen()).toEqual([false, true]);
  });

  it("opens a rebuilt panel on what it knew", async () => {
    getHappyEnding.mockResolvedValue(true);
    (await renderReady({ project: "mutlu-a" })).unmount();
    getHappyEnding.mockReturnValue(new Promise(() => {}));

    await renderReady({ project: "mutlu-a" });

    expect(chosen()).toEqual([false, true]);
  });

  it("leaves the length's choice alone, and the length its", async () => {
    await renderReady();

    await act(async () => { fireEvent.click(on()); });
    await act(async () => { fireEvent.click(screen.getByRole("button", { name: "12 saniye" })); });

    expect(chosen()).toEqual([false, true]);
    expect(saveHappyEnding).toHaveBeenCalledTimes(1);
    expect(saveVideoLength).toHaveBeenCalledWith(expect.any(String), 12);
  });

  it("says the server's sentence when it cannot be written, and goes back to the saved one",
     async () => {
    saveHappyEnding.mockRejectedValue(new Error("Proje yok: düğün"));
    await renderReady();

    await act(async () => { fireEvent.click(on()); });

    const card = screen.getByText("Proje yok: düğün");
    expect(card.closest(".wf-stroke").style.borderColor).toBe("var(--danger)");
    expect(chosen()).toEqual([true, false]);
  });

  it("is not drawn while the model is not read yet", async () => {
    const view = await renderReady({ producer: null });

    expect(labels(view)).not.toContain("Mutlu son");
    expect(getHappyEnding).not.toHaveBeenCalled();
  });

  it("is not drawn, and says nothing, when it cannot be read", async () => {
    getHappyEnding.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));
    const view = await renderReady();

    expect(labels(view)).not.toContain("Mutlu son");
    expect(screen.getByText(`${LOOP_LINE} 8 sn.`)).toBeTruthy();
  });

  it("is not on the sound panel", async () => {
    const view = await renderReady({ layer: "audio", producer: AUDIO,
                                     frames: [done("0_a.png", { video: "0_a_V1_0.mp4" })] });

    expect(labels(view)).not.toContain("Mutlu son");
    expect(getHappyEnding).not.toHaveBeenCalled();
  });

  it("is said after the length once it is on", async () => {
    await renderReady();

    await act(async () => { fireEvent.click(on()); });

    expect(screen.getByText(`${LOOP_LINE} 8 sn, mutlu son.`)).toBeTruthy();
  });

  it("is said alone when the length cannot be read", async () => {
    getVideoLength.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));
    getHappyEnding.mockResolvedValue(true);
    await renderReady();

    expect(screen.getByText(`${LOOP_LINE} Mutlu son.`)).toBeTruthy();
  });

  it("ends the copy warning and Referanstan's line too", async () => {
    getHappyEnding.mockResolvedValue(true);
    await renderReady({ selected: ["1_a"] });

    expect(screen.getByText("1 loop video üretilecek — videolu 1 kare için yeniler kopya kare "
                            + "olur, eskisi durur. 8 sn, mutlu son.")).toBeTruthy();

    await act(async () => { fireEvent.click(tab("Referanstan")); });
    fireEvent.change(screen.getByLabelText("Prompt listesi"),
                     { target: { value: '["gotik kız", "dans"]' } });
    fireEvent.change(variantBox(), { target: { value: "3" } });

    expect(screen.getByText("2 prompt × 3 varyant = 6 kart. 8 sn, mutlu son.")).toBeTruthy();
  });
});
