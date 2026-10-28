# Madde 325 — Referanstan'ın prompt listesi sunucuya ulaşıyor, test turunun planı

> **Koşum:** bu oturumda, satır satır. Alt ajan yok *(CLAUDE.md, Gotchas)*.

**Hedef:** Video panelinin prompt listesinin yan panelden `onQueueLayer`'a geçtiğini söyleyen tek
test — kırmızı.

**Yaklaşım:** Yan panel gerçek LayerPanel'iyle koşuluyor, `onQueueLayer` dinleniyor. Panelin kendi
yarısını LayerPanel'in testi zaten tutuyor; kırılan bağlantı bu.

**Spec:** [m325 test turu](../specs/2026-09-24-queen-editor-m325-prompt-listesi-yolda-testler-design.md)

## Her yere geçerli kurallar

- Test adı ve yorum **İngilizce**.
- Testler dört satırla koşulur; `skip` / `xfail` / `.skip` / `.todo` yok. Bu turda kaynak kod
  değişmiyor.

---

## Görev 1: Test

**Dosya:** Değiştir: `queen-editor/frontend/src/features/photo_generation/SidePanel.test.jsx` —
import satırına `act`; test `hands the layer panel what the photo panel already gets`'in hemen
altına.

- [ ] **Adım 1: `act`'i import et.**

```jsx
import { act, fireEvent, render, screen } from "@testing-library/react";
```

- [ ] **Adım 2: Test.**

```jsx
  it("passes the reference prompt list through to the queue", async () => {
    // Madde 325: the panel hands onQueue four arguments from the pool, and the column's wiring
    // passed on three -- the prompts were dropped on the way and the server got none. The panel's
    // own test cannot see this; only the column's wiring can.
    const onQueueLayer = vi.fn().mockResolvedValue({ added: 2 });
    renderColumn({ frames: [], onQueueLayer });

    fireEvent.click(screen.getByLabelText("Video üret"));
    fireEvent.click(screen.getByText("Referanstan"));
    fireEvent.change(screen.getByLabelText("Prompt listesi"),
                     { target: { value: '["gotik kız", "dans"]' } });
    await act(async () => { fireEvent.click(screen.getByText("Kuyruğa ekle")); });

    expect(onQueueLayer).toHaveBeenCalledWith("video", null, 1, "reference",
                                              '["gotik kız", "dans"]');
  });
```

## Görev 2: Koşu ve kırmızı commit

- [ ] **Adım 1: Dört satırı koş** — `queen-editor/frontend` vitest'te yalnız bu test kırmızı
  *(çağrı beşinci argümansız)*; öteki üç satır yeşil.
- [ ] **Adım 2: Kırmızı commit** — test dosyası, spec ve bu plan: `test(m325): …(red)`.
