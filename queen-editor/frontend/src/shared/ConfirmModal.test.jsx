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
  it("başlığı ve gövdeyi basar", () => {
    renderModal({ body: "Bu işlem geri alınamaz." });

    expect(screen.getByText("Bu fotoğraf silinsin mi?")).toBeTruthy();
    expect(screen.getByText("Bu işlem geri alınamaz.")).toBeTruthy();
  });

  it("gövdesiz de çizilir", () => {
    renderModal({ title: "Projeden çıkılsın mı?", confirmLabel: "Çık" });

    expect(screen.getByText("Projeden çıkılsın mı?")).toBeTruthy();
    expect(screen.getByText("Çık")).toBeTruthy();
  });

  it("yıkıcı onay kırmızı, yıkıcı olmayan accent görünür", () => {
    const { unmount } = renderModal({ danger: true });
    expect(screen.getByText("Sil").style.background).toBe("var(--danger)");
    unmount();

    renderModal({ confirmLabel: "Çık" });
    expect(screen.getByText("Çık").className).toContain("wf-btn--hl");
  });

  it("Esc iptal eder, iş sürerken etmez", () => {
    const onCancel = vi.fn();
    const { unmount } = renderModal({ onCancel });

    fireEvent.keyDown(window, { key: "Escape" });
    expect(onCancel).toHaveBeenCalledTimes(1);
    unmount();

    renderModal({ onCancel, busy: true });
    fireEvent.keyDown(window, { key: "Escape" });
    expect(onCancel).toHaveBeenCalledTimes(1);
  });

  it("onaya basınca onConfirm çağrılır", () => {
    const onConfirm = vi.fn();
    renderModal({ onConfirm });

    fireEvent.click(screen.getByText("Sil"));

    expect(onConfirm).toHaveBeenCalled();
  });
});
