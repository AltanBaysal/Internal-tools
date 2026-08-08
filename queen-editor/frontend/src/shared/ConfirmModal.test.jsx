import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import ConfirmModal from "./ConfirmModal.jsx";

function renderModal(props) {
  return render(
    <ConfirmModal title="Bu fotoğraf silinsin mi?" confirmLabel="Sil"
                  onCancel={() => {}} onConfirm={() => {}} {...props} />,
  );
}

describe("ConfirmModal", () => {
  it("renders the title and the body", () => {
    renderModal({ body: "Bu işlem geri alınamaz." });

    expect(screen.getByText("Bu fotoğraf silinsin mi?")).toBeTruthy();
    expect(screen.getByText("Bu işlem geri alınamaz.")).toBeTruthy();
  });

  it("renders without a body too", () => {
    renderModal({ title: "Projeden çıkılsın mı?", confirmLabel: "Çık" });

    expect(screen.getByText("Projeden çıkılsın mı?")).toBeTruthy();
    expect(screen.getByText("Çık")).toBeTruthy();
  });

  it("dresses a destructive confirm in the outline standard and a plain one in accent", () => {
    // The app-wide rule: no filled red button anywhere -- outline, red text, trash icon.
    const { unmount } = renderModal({ danger: true });
    const destructive = screen.getByRole("button", { name: "Sil" });
    expect(destructive.style.background).toBe("none");
    expect(destructive.style.color).toBe("var(--danger)");
    expect(destructive.querySelector("svg")).toBeTruthy();
    unmount();

    renderModal({ confirmLabel: "Çık" });
    expect(screen.getByText("Çık").className).toContain("wf-btn--hl");
  });

  it("cancels on Esc, but not while the work is running", () => {
    const onCancel = vi.fn();
    const { unmount } = renderModal({ onCancel });

    fireEvent.keyDown(window, { key: "Escape" });
    expect(onCancel).toHaveBeenCalledTimes(1);
    unmount();

    renderModal({ onCancel, busy: true });
    fireEvent.keyDown(window, { key: "Escape" });
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("calls onConfirm when the confirm button is pressed", () => {
    const onConfirm = vi.fn();
    renderModal({ onConfirm });

    fireEvent.click(screen.getByText("Sil"));

    expect(onConfirm).toHaveBeenCalled();
  });
});
