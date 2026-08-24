import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

// What was typed and not yet sent is remembered for the length of a visit, and that memory lives in
// the module. So each test gets the module itself fresh -- otherwise a test that types into a box
// would be deciding what the next one opens with. Nothing is mocked in this file, so resetModules
// really does rebuild it.
let GeneratePanel;

beforeEach(async () => {
  vi.resetModules();
  ({ default: GeneratePanel } = await import("./GeneratePanel.jsx"));
});

const SETTINGS = { prompts: '["ilk prompt"]', negative: "", variants: 4, model: "" };
const PROMPT_BOX = '["ilk prompt", "ikinci prompt"]';
const RUNNING = { status: "running", project: "düğün", done: 7, failed: 0, total: 48 };
const MODELS = ["nova.safetensors", "başka.safetensors"];

function renderPanel(props) {
  return render(
    <GeneratePanel
      job={{ status: "idle" }}
      error={null}
      busyElsewhere={false}
      settings={SETTINGS}
      project="düğün"
      models={MODELS}
      modelsError={null}
      onGenerate={() => Promise.resolve({ added: 4 })}
      onClearError={() => {}}
      {...props}
    />,
  );
}

const promptBox = () => screen.getByPlaceholderText(PROMPT_BOX);
const variantBox = () => screen.getByRole("spinbutton");
const modelBox = () => screen.getByRole("combobox");

describe("GeneratePanel — the button", () => {
  it("adds to the queue instead of starting a run", () => {
    renderPanel();

    expect(screen.getByText("Kuyruğa ekle")).toBeTruthy();
    expect(screen.queryByText("Üret")).toBeNull();
  });

  it("carries the same glyph on the button as the rail carries for this panel", () => {
    renderPanel();

    expect(screen.getByText("Kuyruğa ekle").querySelector("[data-glyph='photo']")).toBeTruthy();
  });

  it("stays open while the queue flows", () => {
    renderPanel({ job: RUNNING });

    expect(promptBox().disabled).toBe(false);
    expect(variantBox().disabled).toBe(false);
    expect(screen.getByText("Kuyruğa ekle").closest("button").disabled).toBe(false);
  });

  it("holds the queue button while the producer that would do the work is missing", () => {
    renderPanel({ producer: { id: "photo", name: "Fotoğraf üreticisi", installed: false } });

    expect(screen.getByText("Fotoğraf üreticisi kurulu değil.")).toBeTruthy();
    expect(screen.getByText("Kuyruğa ekle").closest("button").disabled).toBe(true);
  });

  it("lets go of it once the group has landed", () => {
    renderPanel({ producer: { id: "photo", name: "Fotoğraf üreticisi", installed: true } });

    expect(screen.queryByText(/kurulu değil/)).toBeNull();
    expect(screen.getByText("Kuyruğa ekle").closest("button").disabled).toBe(false);
  });

  it("is disabled on an empty list", () => {
    renderPanel({ settings: { ...SETTINGS, prompts: "   " } });

    expect(screen.getByText("Kuyruğa ekle").closest("button").disabled).toBe(true);
  });

  it("is disabled while another project holds the worker", () => {
    renderPanel({ job: { status: "running", project: "balo" }, busyElsewhere: true });

    expect(screen.getByText("Kuyruğa ekle").closest("button").disabled).toBe(true);
    expect(screen.getByText("Üretim sürüyor: balo — bitmesini bekle.")).toBeTruthy();
  });

  it("holds only the button while the request is in flight, never the fields", async () => {
    let release;
    renderPanel({ onGenerate: () => new Promise((resolve) => { release = resolve; }) });

    fireEvent.click(screen.getByText("Kuyruğa ekle"));

    expect(screen.getByText("Ekleniyor…").closest("button").disabled).toBe(true);
    expect(promptBox().disabled).toBe(false);

    await act(async () => { release({ added: 4 }); });
  });

  it("never shows the prompt times variant preview", () => {
    renderPanel({ settings: { ...SETTINGS, prompts: '["a", "b"]', variants: 3 } });

    expect(screen.queryByText(/varyant =/)).toBeNull();
  });
});

describe("GeneratePanel — the model field", () => {
  it("is the first field, and offers what the renderer reported", () => {
    renderPanel();

    expect(screen.getByText("Model")).toBeTruthy();
    expect([...modelBox().options].map((o) => o.value)).toEqual(MODELS);
    // First in the document: the design has put it at the top of the panel since v1.
    expect(screen.getByText("Model").compareDocumentPosition(screen.getByText("Prompt listesi"))
      & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("opens on the saved model rather than the first one", () => {
    renderPanel({ settings: { ...SETTINGS, model: "başka.safetensors" } });

    expect(modelBox().value).toBe("başka.safetensors");
  });

  it("falls back to the first model when nothing was saved", () => {
    renderPanel();

    expect(modelBox().value).toBe("nova.safetensors");
  });

  it("sends the chosen model with the batch", async () => {
    const onGenerate = vi.fn().mockResolvedValue({ added: 4 });
    renderPanel({ onGenerate });

    fireEvent.change(modelBox(), { target: { value: "başka.safetensors" } });
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onGenerate).toHaveBeenCalledWith(expect.objectContaining({
      model: "başka.safetensors",
    }));
  });

  it("keeps a saved model that is no longer installed, and says so", () => {
    renderPanel({ settings: { ...SETTINGS, model: "gitmiş.safetensors" } });

    expect(modelBox().value).toBe("gitmiş.safetensors");
    expect(screen.getByText("Bu model artık kurulu değil.")).toBeTruthy();
  });

  it("says the list could not be read without standing in the way", () => {
    renderPanel({ models: [], modelsError: "Sunucuya ulaşılamadı — bağlantıyı kontrol et." });

    expect(screen.getByText("Model listesi okunamadı")).toBeTruthy();
    expect(screen.getByText("model bulunamadı")).toBeTruthy();
    // The queue did not fail -- only the listing did.
    expect(screen.getByText("Kuyruğa ekle").closest("button").disabled).toBe(false);
  });

  it("waits rather than claiming there is nothing while the list is still coming", () => {
    renderPanel({ models: null });

    expect(screen.getByText("yükleniyor…")).toBeTruthy();
    expect(screen.queryByText("model bulunamadı")).toBeNull();
  });
});

describe("GeneratePanel — the confirmation", () => {
  beforeEach(() => vi.useFakeTimers({ shouldAdvanceTime: true }));
  afterEach(() => vi.useRealTimers());

  it("quotes the number of frames the server took in its own part of the card", async () => {
    renderPanel({ onGenerate: () => Promise.resolve({ added: 48 }) });

    fireEvent.click(screen.getByText("Kuyruğa ekle"));

    await waitFor(() => expect(screen.getByText("48 kare kuyruğa eklendi")).toBeTruthy());
    expect(screen.getByText("✓")).toBeTruthy();
  });

  it("stays long enough to be read after the eyes have moved on", async () => {
    renderPanel({ onGenerate: () => Promise.resolve({ added: 48 }) });

    fireEvent.click(screen.getByText("Kuyruğa ekle"));
    await waitFor(() => expect(screen.getByText("48 kare kuyruğa eklendi")).toBeTruthy());

    await act(async () => { vi.advanceTimersByTime(4000); });
    expect(screen.getByText("48 kare kuyruğa eklendi")).toBeTruthy();

    await act(async () => { vi.advanceTimersByTime(6000); });
    expect(screen.queryByText("48 kare kuyruğa eklendi")).toBeNull();
  });

  it("takes the refusal back the moment the user starts a new attempt", async () => {
    renderPanel({ onGenerate: () => Promise.resolve(null) });

    fireEvent.click(screen.getByText("Kuyruğa ekle"));
    await waitFor(() => expect(screen.getByText("Kuyruğa eklenemedi — tekrar dene")).toBeTruthy());

    fireEvent.change(promptBox(), { target: { value: '["yeni"]' } });

    expect(screen.queryByText("Kuyruğa eklenemedi — tekrar dene")).toBeNull();
  });

  it("says one line when the queue would not take the frames", async () => {
    renderPanel({ onGenerate: () => Promise.resolve(null) });

    fireEvent.click(screen.getByText("Kuyruğa ekle"));

    await waitFor(() => expect(screen.getByText("Kuyruğa eklenemedi — tekrar dene")).toBeTruthy());
    expect(screen.queryByText(/kuyruğa eklendi/)).toBeNull();
  });
});

describe("GeneratePanel — the variant box", () => {
  it("opens at two when the project has never saved a count", () => {
    // A project with nothing saved is what a new one looks like, and two is what the user asked
    // the box to start at (İstek 8).
    renderPanel({ settings: { ...SETTINGS, variants: null } });

    expect(variantBox().value).toBe("2");
  });

  it("opens at the saved count rather than the default", () => {
    // The default is for an empty setting, not a correction: a project saved with a count of its
    // own keeps it, whatever a new one now starts at.
    renderPanel({ settings: { ...SETTINGS, variants: 6 } });

    expect(variantBox().value).toBe("6");
  });

  it("refuses a value outside 1-26", () => {
    renderPanel();

    fireEvent.change(variantBox(), { target: { value: "27" } });
    expect(variantBox().value).toBe("4");

    fireEvent.change(variantBox(), { target: { value: "0" } });
    expect(variantBox().value).toBe("4");

    fireEvent.change(variantBox(), { target: { value: "26" } });
    expect(variantBox().value).toBe("26");
  });

  it("snaps an emptied box back to 1 when it loses focus", () => {
    renderPanel();

    fireEvent.change(variantBox(), { target: { value: "" } });
    expect(variantBox().value).toBe("");        // clearing has to be possible while typing

    fireEvent.blur(variantBox());
    expect(variantBox().value).toBe("1");
  });

  it("has no error state of its own, and answers under the button instead", () => {
    renderPanel({ error: "Varyant sayısı 1-26 arası bir tam sayı olmalı.", errorField: "variants" });

    expect(variantBox().style.borderColor).toBe("");
    expect(screen.getByText("Varyant sayısı 1-26 arası bir tam sayı olmalı.")).toBeTruthy();
  });
});

describe("GeneratePanel — a format error", () => {
  it("reddens the prompt box and labels it short, with the sentence under the button", () => {
    renderPanel({ error: "Format hatası — liste okunamadı", errorField: "prompts" });

    expect(screen.getByText("Format hatası")).toBeTruthy();
    expect(screen.getByText("Format hatası — liste okunamadı")).toBeTruthy();
    expect(promptBox().style.borderColor).toBe("var(--danger)");
  });

  it("leaves the box wordless when the sentence has no short form", () => {
    renderPanel({ error: "Prompt listesi boş.", errorField: "prompts" });

    expect(screen.getAllByText("Prompt listesi boş.")).toHaveLength(1);
    expect(promptBox().style.borderColor).toBe("var(--danger)");
  });

  it("does not blame the queue for a request that never reached it", async () => {
    renderPanel({ error: "Format hatası — liste okunamadı", errorField: "prompts",
                  onGenerate: () => Promise.resolve(null) });

    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(screen.queryByText(/Kuyruğa eklenemedi/)).toBeNull();
    expect(screen.getByText("Format hatası — liste okunamadı")).toBeTruthy();
  });

  it("clears the error once typing starts", () => {
    const onClearError = vi.fn();
    renderPanel({ error: "Format hatası — liste okunamadı", errorField: "prompts", onClearError });

    fireEvent.change(promptBox(), { target: { value: '["a"]' } });

    expect(onClearError).toHaveBeenCalled();
  });
});

describe("GeneratePanel — coming back to the form", () => {
  it("keeps a prompt that was typed but never sent", () => {
    const first = renderPanel();

    fireEvent.change(promptBox(), { target: { value: '["yazdım ama göndermedim"]' } });
    first.unmount();

    // Opening a frame tears the whole project screen down, this panel with it. What was typed
    // reached no disk -- only pressing the button does that -- so React dropping the state is the
    // whole of the loss.
    renderPanel();

    expect(promptBox().value).toBe('["yazdım ama göndermedim"]');
  });

  it("keeps the negative, the model and the variant count too", () => {
    const first = renderPanel();

    fireEvent.change(screen.getByDisplayValue(""), { target: { value: "bulanık" } });
    fireEvent.change(modelBox(), { target: { value: "başka.safetensors" } });
    fireEvent.change(variantBox(), { target: { value: "9" } });
    first.unmount();

    // One form, one loss: remembering the prompt and forgetting the three boxes under it would be
    // remembering half of an unfinished piece of work.
    renderPanel();

    expect(screen.getByDisplayValue("bulanık")).toBeTruthy();
    expect(modelBox().value).toBe("başka.safetensors");
    expect(variantBox().value).toBe("9");
  });

  it("fills the boxes from the record when nothing has been typed yet", () => {
    renderPanel({ settings: { ...SETTINGS, prompts: '["kayıttaki"]', variants: 6 } });

    // The first visit of a session has nothing to go on, and the project's own record is where the
    // boxes come from. Losing this would mean showing someone else's text to a user who typed none.
    expect(promptBox().value).toBe('["kayıttaki"]');
    expect(variantBox().value).toBe("6");
  });

  it("does not carry one project's draft into another", () => {
    const first = renderPanel();

    fireEvent.change(promptBox(), { target: { value: '["düğünün prompt listesi"]' } });
    first.unmount();

    renderPanel({ project: "balo" });

    // What is half-written is the user's work in one project, never a fact about the app.
    expect(promptBox().value).toBe('["ilk prompt"]');
  });
});
