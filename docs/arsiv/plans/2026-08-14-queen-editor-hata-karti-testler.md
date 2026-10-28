# Uzun hata metni: TEST döngüsü (uygulama planı)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ham çıktının kendi kutusunda kalmasını ve kopyalanabilmesini sınayan testleri yazmak,
takımı kırmızı commit'lemek.

**Architecture:** Üç dosya. İkisi yeni (`RawOutput` ve `StatusErrorCard`'ın testleri), biri mevcut
(`QueuePanel.test.jsx`).

**Tech Stack:** React 18, vitest, jsdom.

**Tasarım:** [test spec'i](../specs/2026-08-14-queen-editor-hata-karti-testler-design.md)

## Global Constraints

- **Bu döngüde üretim kodu yazılmıyor.** `RawOutput.jsx` bu döngüde **oluşturulmaz** — testler onu
  içe aktarır ve içe aktaramadıkları için düşer.
- Test adları ve yorumlar **İngilizce**.
- Commit mesajında **çift tırnak yok**.
- Komut: `npm test --prefix queen-editor/frontend`
- `dist/` **derlenmiyor**.

## File Structure

| Dosya | Sorumluluk | İşlem |
|---|---|---|
| `src/shared/RawOutput.test.jsx` | kutunun kendisi | **yeni** |
| `src/shared/StatusErrorCard.test.jsx` | ortak hata kartı | **yeni** |
| `src/features/photo_generation/QueuePanel.test.jsx` | durdu kartı | 2 test eklenir |

**Sınanan arayüz** (implementasyon döngüsü bunu yazacak):
`RawOutput({ text })` — `src/shared/RawOutput.jsx`'ten adlandırılmış dışa aktarım. Kayan kutuyu
`data-raw` ile işaretler, altında "Kopyala" yazan bir düğme çizer.

---

### Task 1: Kutunun kendi testleri

**Files:**
- Create: `queen-editor/frontend/src/shared/RawOutput.test.jsx`

- [ ] **Step 1: Dosyayı yaz**

```jsx
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import { RawOutput } from "./RawOutput.jsx";

// What a real failure looks like: one useful line, then sixty nobody reads on screen.
const LONG = ["POST /prompt -> node_errors", "{"]
  .concat(Array.from({ length: 60 }, (_, i) => `  "line ${i}": "value",`))
  .concat(["}"])
  .join("\n");

// jsdom ships no clipboard, so the test supplies one and watches what it is handed.
function stubClipboard(answer) {
  const writeText = vi.fn(() => answer);
  Object.defineProperty(navigator, "clipboard", { value: { writeText }, configurable: true });
  return writeText;
}

const box = () => document.querySelector("[data-raw]");
const copy = () => screen.getByRole("button", { name: /Kopyala/ });

describe("RawOutput", () => {
  it("keeps a long output inside its own box", () => {
    // jsdom does not scroll, so what can be tested is that the rule to scroll is there. Whether it
    // really scrolls is the Colab round's answer -- and the rule is what kept disappearing.
    render(<RawOutput text={LONG} />);

    expect(box().style.overflowY).toBe("auto");
    expect(box().style.maxHeight).not.toBe("");
  });

  it("shows the whole output rather than a cut of it", () => {
    // The repo rule: print what the service actually said. Folding is allowed, losing is not.
    render(<RawOutput text={LONG} />);

    expect(box().textContent).toBe(LONG);
  });

  it("copies exactly what it shows", async () => {
    const writeText = stubClipboard(Promise.resolve());
    render(<RawOutput text={LONG} />);

    fireEvent.click(copy());

    expect(writeText).toHaveBeenCalledWith(LONG);
    expect(await screen.findByText("Kopyalandı")).toBeTruthy();
  });

  it("says so when the clipboard refuses", async () => {
    // Silence would leave the user believing they had the text. The box is still selectable, so
    // saying it failed is also saying take it by hand.
    stubClipboard(Promise.reject(new Error("denied")));
    render(<RawOutput text={LONG} />);

    fireEvent.click(copy());

    expect(await screen.findByText("Kopyalanamadı")).toBeTruthy();
  });
});
```

- [ ] **Step 2: Koş**

Run: `npm test --prefix queen-editor/frontend -- src/shared/RawOutput.test.jsx`
Expected: dosya çöküyor — `RawOutput.jsx` yok. Dört test de düşer.

---

### Task 2: Ortak kartın testi

**Files:**
- Create: `queen-editor/frontend/src/shared/StatusErrorCard.test.jsx`

- [ ] **Step 1: Dosyayı yaz**

```jsx
import { render } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import { StatusErrorCard } from "./StatusErrorCard.jsx";

describe("StatusErrorCard", () => {
  it("puts the raw output in the same box the queue panel uses", () => {
    // One unbounded block was enough to lock a panel; this card is drawn on three screens, so it
    // gets the same box rather than waiting its turn to lock one of them.
    const raw = Array.from({ length: 40 }, (_, i) => `satır ${i}`).join("\n");

    render(<StatusErrorCard text="İstek reddedildi" raw={raw} />);

    const box = document.querySelector("[data-raw]");
    expect(box).toBeTruthy();
    expect(box.textContent).toBe(raw);
  });
});
```

- [ ] **Step 2: Koş**

Run: `npm test --prefix queen-editor/frontend -- src/shared/StatusErrorCard.test.jsx`
Expected: 1 düşen — `[data-raw]` yok.

---

### Task 3: Durdu kartının testleri

**Files:**
- Modify: `queen-editor/frontend/src/features/photo_generation/QueuePanel.test.jsx`

- [ ] **Step 1: Dosyanın sonuna yeni bir blok ekle**

```jsx
// 2026-08-14: ComfyUI refused four nodes at once and the engine printed the sixty lines it
// answered with. The panel does not scroll, the block had no ceiling, and both buttons went off
// the bottom -- the run could neither be continued nor emptied.
describe("QueuePanel — a stopped run with a lot to say", () => {
  const NOISE = ["POST /prompt -> node_errors", "{"]
    .concat(Array.from({ length: 60 }, (_, i) => `  "node ${i}": "value_not_in_list",`))
    .concat(["}"])
    .join("\n");
  const RULE = "Aynı kare 3 kez denendi — üretim durduruldu";
  const HALTED = { status: "error", project: "düğün", error: `${RULE}\n${NOISE}` };

  function renderHalted() {
    return renderPanel({ job: HALTED, queue: [{ layer: "video", owed: 8 }] });
  }

  it("does not let the output push the buttons off the panel", () => {
    renderHalted();

    expect(document.querySelector("[data-raw]")).toBeTruthy();
    expect(screen.getByText("Kuyruğu boşalt")).toBeTruthy();
    expect(screen.getByText("Kaldığı yerden devam et")).toBeTruthy();
  });

  it("leaves the rule's own sentence outside the box", () => {
    // Two different things: one is read, the other is folded away and copied. Inside one block
    // they read as a single technical dump and the sentence is lost in it.
    renderHalted();

    expect(screen.getByText(RULE)).toBeTruthy();
    expect(document.querySelector("[data-raw]").textContent).toBe(NOISE);
  });
});
```

- [ ] **Step 2: Koş**

Run: `npm test --prefix queen-editor/frontend -- src/features/photo_generation/QueuePanel.test.jsx`
Expected: 2 düşen; dosyanın geri kalanı yeşil.

---

### Task 4: Takım ve kırmızı commit

- [ ] **Step 1: Tam takım**

Run: `npm test --prefix queen-editor/frontend`
Expected: **3 düşen test + 1 yüklenemeyen dosya.** `RawOutput.test.jsx` içe aktardığı bileşen
olmadığı için hiç yüklenmiyor; dört testi toplanmadığından sayıya girmiyor. Koşup düşen üç test
`QueuePanel` (2) ve `StatusErrorCard` (1). Geri kalan 324 yeşil.

- [ ] **Step 2: Commit**

```bash
git add queen-editor/frontend/src docs/superpowers
git commit -F - <<'EOF'
test(queen-editor): give a long error somewhere to live

Red on purpose -- the implementation cycle turns these green.

A stopped run printed the sixty lines ComfyUI answered with, the panel does
not scroll, and the block had no ceiling: both buttons went off the bottom of
the panel and could not be reached. The queue could neither be continued nor
emptied.

Seven failures, all saying the same thing -- there is no box. Four describe
the box itself, which does not exist yet: it holds the whole output rather
than a cut of it, it scrolls inside its own ceiling, it copies exactly what it
shows, and it says so when the clipboard refuses rather than leaving the user
believing they have the text. Two put the queue panel s stopped card in front
of a real sixty line failure and ask whether the buttons survived, and whether
the rule s own sentence stayed outside the box. One asks the same of
StatusErrorCard, which is drawn on three screens and has the same unbounded
block waiting to lock one of them.
EOF
git log --oneline -1
```

## Self-Review

**Spec kapsamı:** 1–4 → Task 1 · 5–6 → Task 3 · 7 → Task 2. Eksik yok. Spec'te dört madde sayılmıştı
ama Task 1'de beş test var: "gösterdiğinin tamamını gösteriyor" testi eklendi, çünkü kesmeme kuralı
spec'in kendi başlığı ve sınanmadan kalırsa ilk sadeleştirmede düşer.

**Kontrol edilen tuzak:** `RawOutput.jsx` bu döngüde yazılmıyor. Yazılsaydı Task 1 yeşil doğar ve
kırmızı commit yalan olurdu.

**Kontrol edilen tuzak 2:** `stubClipboard` `navigator.clipboard`'ı `configurable: true` ile
tanımlıyor — jsdom'da özellik yoksa `Object.defineProperty` gerekiyor, ve testler arası yeniden
tanımlanabilir kalması gerekiyor.

**Kontrol edilen varsayım:** `getByText(RULE)` bugün düşer, çünkü cümle ham metinle **aynı** elemanın
içinde ve `getByText` varsayılan olarak elemanın tüm metnini karşılaştırır. Yani ikinci test bugün
gerçekten kırmızı.
