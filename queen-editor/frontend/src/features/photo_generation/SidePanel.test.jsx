import { fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

// Which panel is open is remembered for the length of a visit, and that memory lives in the module.
// So each test gets the module itself fresh -- otherwise a test that closes the column would be
// deciding how the next one opens. Nothing is mocked in this file, so resetModules really does
// rebuild it.
let SidePanel;

beforeEach(async () => {
  vi.resetModules();
  ({ default: SidePanel } = await import("./SidePanel.jsx"));
});

const SETTINGS = { prompts: '["ilk prompt"]', negative: "", variants: 4 };
const RUNNING = { status: "running", project: "düğün", done: 7, failed: 0, total: 48 };
const PROMPT_BOX = '["ilk prompt", "ikinci prompt"]';

// The element apart from the render: one test draws the same column twice, before and after the
// project record lands, and rerender has to be handed the same element.
function column(props) {
  return (
    <SidePanel
      job={{ status: "idle" }}
      known
      error={null}
      busyElsewhere={false}
      settings={SETTINGS}
      project="düğün"
      stopping={false}
      queue={[]}
      onGenerate={() => Promise.resolve()}
      onStop={() => {}}
      onResume={() => {}}
      onCancel={() => {}}
      onClearError={() => {}}
      {...props}
    />
  );
}

function renderColumn(props) {
  return render(column(props));
}

describe("SidePanel — the icon rail", () => {
  it("opens on the form panel", () => {
    renderColumn();

    expect(screen.getByPlaceholderText(PROMPT_BOX)).toBeTruthy();
    expect(screen.getByLabelText("Fotoğraf üret").getAttribute("aria-current")).toBe("page");
    expect(screen.getByLabelText("Kuyruğu takip et").getAttribute("aria-current")).toBeNull();
  });

  it("closes the open panel when its own icon is pressed again", () => {
    renderColumn();

    fireEvent.click(screen.getByLabelText("Fotoğraf üret"));

    expect(screen.queryByPlaceholderText(PROMPT_BOX)).toBeNull();
    expect(screen.getByLabelText("Fotoğraf üret")).toBeTruthy();      // the rail stays
  });

  it("opens it again on the next press", () => {
    renderColumn();

    fireEvent.click(screen.getByLabelText("Fotoğraf üret"));
    fireEvent.click(screen.getByLabelText("Fotoğraf üret"));

    expect(screen.getByPlaceholderText(PROMPT_BOX)).toBeTruthy();
    expect(screen.getByLabelText("Fotoğraf üret").getAttribute("aria-current")).toBe("page");
  });

  it("marks no icon as open while the panel is closed", () => {
    const { container } = renderColumn();

    fireEvent.click(screen.getByLabelText("Fotoğraf üret"));

    expect(container.querySelectorAll("[aria-current='page']")).toHaveLength(0);
  });

  it("swaps the panel when another icon is pressed", () => {
    renderColumn({ job: RUNNING, queue: [{ layer: "photo", owed: 2 }] });

    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    expect(screen.queryByPlaceholderText(PROMPT_BOX)).toBeNull();
    expect(screen.getByText("Foto — üretiliyor")).toBeTruthy();
    expect(screen.getByLabelText("Kuyruğu takip et").getAttribute("aria-current")).toBe("page");
  });

  it("keeps the run's own words out of the form panel", () => {
    renderColumn({ job: RUNNING });

    // The form panel is open: the status card belongs to the queue panel, not here.
    expect(screen.queryByText("Üretiliyor")).toBeNull();
    expect(screen.queryByText("Duraklat")).toBeNull();
  });

  it("opens the agent panel and leaves it deliberately empty", () => {
    renderColumn();

    fireEvent.click(screen.getByLabelText("AI agent"));

    expect(screen.getByText("Agent buradan çalışacak.")).toBeTruthy();
  });

  it("marks the photo panel with its own layer's glyph, not a plus", () => {
    renderColumn();

    expect(screen.getByLabelText("Fotoğraf üret").querySelector("[data-glyph='photo']"))
      .toBeTruthy();
  });

  it("opens the sound panel from its own wave on the rail", () => {
    renderColumn();

    expect(screen.getByLabelText("Ses üret").querySelector("[data-glyph='sound']")).toBeTruthy();
    fireEvent.click(screen.getByLabelText("Ses üret"));

    expect(screen.getByRole("heading", { name: "Ses üret" })).toBeTruthy();
    expect(screen.getByText("MMAudio v2")).toBeTruthy();
  });

  it("puts the producers panel at the foot of the rail", () => {
    renderColumn();

    const rail = [...document.querySelectorAll("button[aria-label]")]
      .map((button) => button.getAttribute("aria-label"));
    expect(rail.at(-1)).toBe("Üreticiler");
  });

  it("opens the producers panel with its own heading", () => {
    renderColumn();

    fireEvent.click(screen.getByLabelText("Üreticiler"));

    expect(screen.getByRole("heading", { name: "Üreticiler" })).toBeTruthy();
    expect(screen.getByText(
      "Her üretici kendi model grubunu kurar. Kullanmadığın kurulmaz.")).toBeTruthy();
  });

  it("never marks the producers icon, because nothing lands while the app is up", () => {
    // Models come down in the notebook, before this process starts (FOUNDATION 9), so there is no
    // such thing as an install running behind a closed panel.
    renderColumn({ producers: { producers: [
      { id: "video", name: "Video üreticisi", installed: false }], error: null } });

    expect(screen.getByLabelText("Üreticiler").querySelector(".qe-dot--alive")).toBeNull();
  });

  it("names the open panel above it", () => {
    renderColumn();

    expect(screen.getByRole("heading", { name: "Fotoğraf üret" })).toBeTruthy();

    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    expect(screen.getByRole("heading", { name: "Kuyruk" })).toBeTruthy();
  });

  it("hands the queue panel the producer rows", () => {
    renderColumn({ queue: [{ layer: "video", owed: 3 }],
                   producers: { producers: [
                     { id: "video", name: "Video üreticisi", installed: false }], error: null } });

    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    // The wiring is the half that breaks silently: the panel can only say what it was given.
    expect(document.querySelector('[data-kind="video"]').textContent)
      .toContain("Üretici kurulu değil.");
  });
});

describe("SidePanel — while the project record is still missing", () => {
  it("waits inside its own column", () => {
    const { container } = renderColumn({ settings: null });

    // The waiting belongs to the panel that asked for the record, not to the screen: the boxes
    // are not there yet and the ring stands where they will be.
    expect(container.querySelector(".wf-spinner")).toBeTruthy();
    expect(screen.queryByPlaceholderText(PROMPT_BOX)).toBeNull();
    // The rail is untouched, so every other panel is still one press away.
    expect(screen.getByLabelText("Kuyruğu takip et")).toBeTruthy();
  });

  it("opens the panels that never needed the record", () => {
    renderColumn({ settings: null, job: RUNNING, queue: [{ layer: "photo", owed: 2 }] });

    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    // The queue reads the server's own status, not the project's record. It had no reason to wait
    // and now it does not.
    expect(screen.getByText("Foto — üretiliyor")).toBeTruthy();
  });

  it("fills the boxes once the record lands", () => {
    const { rerender } = render(column({ settings: null }));

    rerender(column({ settings: SETTINGS }));

    // The form is still seeded once, at its own mount -- it simply mounts inside a live screen
    // now. Nothing is synced afterwards, so nothing can be typed over.
    expect(screen.getByPlaceholderText(PROMPT_BOX).value).toBe('["ilk prompt"]');
  });

  it("shows an unreadable record inside the panel, with a way to ask again", () => {
    const asked = vi.fn();

    renderColumn({ settings: null, settingsError: "Proje bulunamadı: düğün",
                   onRetrySettings: asked });

    expect(screen.getByText("Proje ayarları yüklenemedi")).toBeTruthy();
    // The gallery behind it is untouched, so the way back belongs to this column too.
    fireEvent.click(screen.getByText("Tekrar dene"));
    expect(asked).toHaveBeenCalled();
  });

  it("does not let the queue panel speak before the server has", () => {
    renderColumn({ known: false, job: { status: "idle" }, queue: null });

    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));

    // The column only carries this; the sentence it prevents belongs to the panel.
    expect(screen.queryByText("Kuyruk boş")).toBeNull();
  });
});

describe("SidePanel — coming back to the column", () => {
  it("opens on the panel that was open when it was last torn down", () => {
    const first = renderColumn({ job: RUNNING, queue: [{ layer: "photo", owed: 2 }] });
    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));
    first.unmount();

    // Opening a frame tears the whole project screen down, this column with it. Watching the queue
    // and then looking at a frame should not cost the panel.
    renderColumn({ job: RUNNING, queue: [{ layer: "photo", owed: 2 }] });

    expect(screen.getByRole("heading", { name: "Kuyruk" })).toBeTruthy();
    expect(screen.getByLabelText("Kuyruğu takip et").getAttribute("aria-current")).toBe("page");
  });

  it("comes back closed when it was left closed", () => {
    const first = renderColumn();
    fireEvent.click(screen.getByLabelText("Fotoğraf üret"));      // closes the open panel
    first.unmount();

    renderColumn();

    // Closed is an answer too: the width was given back to the gallery on purpose. It is also the
    // trap in the store -- closed is null, and so is having nothing remembered.
    expect(screen.queryByPlaceholderText(PROMPT_BOX)).toBeNull();
    expect(document.querySelectorAll("[aria-current='page']")).toHaveLength(0);
    expect(screen.getByLabelText("Fotoğraf üret")).toBeTruthy();  // the rail stays
  });

  it("still opens on the form panel when nothing has been chosen yet", () => {
    renderColumn();

    // The first visit of a session has nothing to go on, and the form is where the column opens.
    expect(screen.getByPlaceholderText(PROMPT_BOX)).toBeTruthy();
    expect(screen.getByLabelText("Fotoğraf üret").getAttribute("aria-current")).toBe("page");
  });

  it("opens another project on its own default", () => {
    const first = renderColumn({ job: RUNNING, queue: [{ layer: "photo", owed: 2 }] });
    fireEvent.click(screen.getByLabelText("Kuyruğu takip et"));
    first.unmount();

    renderColumn({ project: "başka" });

    // Which panel is being watched is the user's work in one project, never a fact about the app.
    expect(screen.getByPlaceholderText(PROMPT_BOX)).toBeTruthy();
  });
});
