import { act, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import { checkProjectName } from "../../shared/api.js";
import NameModal from "./NameModal.jsx";

vi.mock("../../shared/api.js", () => ({
  checkProjectName: vi.fn(),
}));

const FORBIDDEN = "Proje adı şu karakterleri içeremez: :*?<>|";
const EMPTY = "Proje adı boş olamaz.";

// Advancing the fake clock inside act() flushes both the debounce timer and the promise it starts.
async function settle(ms = 0) {
  await act(async () => { await vi.advanceTimersByTimeAsync(ms); });
}

// The window as the projects screen opens it to make one: the same window the rename opens with
// other words.
function open(onSubmit = () => Promise.resolve()) {
  return render(<NameModal title="Yeni proje" submitLabel="Oluştur" busyLabel="Oluşturuluyor…"
                           onCancel={() => {}} onSubmit={onSubmit} />);
}

function box() {
  return document.querySelector(".wf-input");
}

function createButton() {
  return screen.getByText("Oluştur");
}

async function type(value) {
  fireEvent.change(box(), { target: { value } });
  await settle(300);
}

beforeEach(() => {
  vi.clearAllMocks();
  vi.useFakeTimers();
  checkProjectName.mockResolvedValue({ error: null });
});
afterEach(() => vi.useRealTimers());

describe("NameModal", () => {
  it("opens at its own measure: the caller does not give one", () => {
    open();

    // Fark 6: two windows, one form, one measure. It stopped being the caller's the moment the
    // second window turned out to want the same number.
    expect(createButton().closest(".wf-card").style.width).toBe("380px");
  });

  it("greets an untouched box with nothing to complain about", async () => {
    open();
    await settle(1000);

    expect(screen.queryByText(EMPTY)).toBeNull();
    expect(checkProjectName).not.toHaveBeenCalled();
    // Still nothing to create: the button is dead, it just does not say why.
    expect(createButton().disabled).toBe(true);
  });

  it("warns while the name is being typed, in the server's own words", async () => {
    checkProjectName.mockResolvedValue({ error: FORBIDDEN });
    const onSubmit = vi.fn();
    open(onSubmit);

    await type("a:b");

    expect(checkProjectName).toHaveBeenCalledWith("a:b");
    expect(screen.getByText(FORBIDDEN)).toBeTruthy();
    expect(createButton().disabled).toBe(true);
    expect(onSubmit).not.toHaveBeenCalled();
  });

  it("lets go the moment the name is fixed", async () => {
    checkProjectName.mockResolvedValue({ error: FORBIDDEN });
    open();
    await type("a:b");

    checkProjectName.mockResolvedValue({ error: null });
    await type("ab");

    expect(screen.queryByText(FORBIDDEN)).toBeNull();
    expect(createButton().disabled).toBe(false);
  });

  it("says why the button is dead once the box has been emptied again", async () => {
    open();
    fireEvent.change(box(), { target: { value: "a" } });

    checkProjectName.mockResolvedValue({ error: EMPTY });
    await type("");

    expect(screen.getByText(EMPTY)).toBeTruthy();
  });

  it("asks once the typing stops, not once per key", async () => {
    open();

    fireEvent.change(box(), { target: { value: "d" } });
    await settle(100);
    fireEvent.change(box(), { target: { value: "dü" } });
    await settle(100);
    fireEvent.change(box(), { target: { value: "düğ" } });
    await settle(300);

    expect(checkProjectName).toHaveBeenCalledTimes(1);
    expect(checkProjectName).toHaveBeenCalledWith("düğ");
  });

  it("keeps out of the way when the check itself cannot be made", async () => {
    checkProjectName.mockRejectedValue(new Error("Sunucuya ulaşılamadı — bağlantıyı kontrol et."));
    open();

    await type("düğün");

    expect(screen.queryByText(/ulaşılamadı/)).toBeNull();
    expect(createButton().disabled).toBe(false);
  });

  it("creates the project when the name checks out", async () => {
    const onSubmit = vi.fn().mockResolvedValue(null);
    open(onSubmit);
    await type("düğün");

    await act(async () => { fireEvent.click(createButton()); });

    expect(onSubmit).toHaveBeenCalledWith("düğün");
  });

  it("shows what the server said when the create itself is refused", async () => {
    const onSubmit = vi.fn().mockRejectedValue(new Error("Bu ad zaten kullanılıyor."));
    open(onSubmit);
    await type("düğün");

    await act(async () => { fireEvent.click(createButton()); });

    expect(screen.getByText("Bu ad zaten kullanılıyor.")).toBeTruthy();
    expect(createButton().disabled).toBe(true);
  });
});
