# Queen Editor v5 · Görev 24 — Oynatma · Uygulama planı

> Tasarım: [Görev 24 spec](../specs/2026-08-12-queen-editor-v5-gorev-24-oynatma-design.md).
> Önce kırmızı test, sonra en küçük kod.

**Hedef:** video sekmesinde video döngüde oynasın; ses sekmesinde ses ona eşlik etsin ve çubuğun
yerini dalga formu alsın.

## Genel kısıtlar

- Kod/yorum/test **İngilizce**, arayüz metni **Türkçe**.
- Test komutları (birebir): `npm test --prefix queen-editor/frontend -- --run` ·
  `npm run build --prefix queen-editor/frontend` · `python -m pytest queen-editor -q`

---

## Görev 1 — Dosya adresi kendi adıyla anılır

**Dosyalar:** `shared/api.js` ve `photoUrl` çağıran her yer

- [ ] `photoUrl` → `fileUrl`; yolu (`/photos/...`) **değişmez**, yorumu bunu söyler:

```js
// Any file the project folder holds -- a photo, a video, a sound. The route is still called
// /photos because that is the server's own name for the project's file area.
export function fileUrl(project, file) {
```

Çağıranlar: `Gallery.jsx`, `PhotoDetail.jsx` ve üç test dosyasındaki api mock'ları.

- [ ] `npm test --prefix queen-editor/frontend -- --run` → yeşil (davranış değişmedi).

---

## Görev 2 — Oynatıcı

**Dosyalar:** yeni `features/photo_generation/LayerPlayer.jsx`, yeni
`features/photo_generation/LayerPlayer.test.jsx`

**Arayüz:** `<LayerPlayer videoUrl audioUrl />` — `audioUrl` verilmişse ses eşlik eder ve çubuğun
yerini dalga formu alır.

- [ ] **Adım 1 — kırmızı testler:**

```jsx
import { act, fireEvent, render, screen } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";

import LayerPlayer from "./LayerPlayer.jsx";

// jsdom has neither a media pipeline nor Web Audio: the element's own methods are stubbed and the
// waveform stays flat, which is exactly the fallback the design asks for.
beforeEach(() => {
  vi.spyOn(window.HTMLMediaElement.prototype, "play").mockImplementation(function play() {
    this.dispatchEvent(new Event("play"));
    return Promise.resolve();
  });
  vi.spyOn(window.HTMLMediaElement.prototype, "pause").mockImplementation(function pause() {
    this.dispatchEvent(new Event("pause"));
  });
});

const videoOf = () => document.querySelector("video");

describe("LayerPlayer", () => {
  it("loops the video and starts paused", () => {
    render(<LayerPlayer videoUrl="/photos/d/P0_0_V1_0.mp4" />);

    expect(videoOf().getAttribute("src")).toBe("/photos/d/P0_0_V1_0.mp4");
    expect(videoOf().loop).toBe(true);
    expect(screen.getByRole("button", { name: "Oynat" })).toBeTruthy();
  });

  it("plays and pauses from the one round button", () => {
    render(<LayerPlayer videoUrl="/v.mp4" />);

    fireEvent.click(screen.getByRole("button", { name: "Oynat" }));
    expect(screen.getByRole("button", { name: "Duraklat" })).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Duraklat" }));
    expect(screen.getByRole("button", { name: "Oynat" })).toBeTruthy();
  });

  it("says where the video is and how long it is", () => {
    render(<LayerPlayer videoUrl="/v.mp4" />);

    act(() => {
      Object.defineProperty(videoOf(), "duration", { value: 5, configurable: true });
      Object.defineProperty(videoOf(), "currentTime", { value: 2, configurable: true });
      fireEvent(videoOf(), new Event("loadedmetadata"));
      fireEvent(videoOf(), new Event("timeupdate"));
    });

    expect(screen.getByText("0:02")).toBeTruthy();
    expect(screen.getByText("0:05")).toBeTruthy();
    expect(document.querySelector("[data-progress]").style.width).toBe("40%");
  });

  it("brings the sound along and draws a waveform in place of the bar", () => {
    render(<LayerPlayer videoUrl="/v.mp4" audioUrl="/s.wav" />);

    expect(document.querySelector("audio").getAttribute("src")).toBe("/s.wav");
    expect(document.querySelectorAll("[data-bar]").length).toBe(46);
    expect(document.querySelector("[data-progress]")).toBeNull();
  });

  it("keeps the sound with the picture when they drift apart", () => {
    render(<LayerPlayer videoUrl="/v.mp4" audioUrl="/s.wav" />);
    const audio = document.querySelector("audio");

    act(() => {
      Object.defineProperty(videoOf(), "currentTime", { value: 3, configurable: true });
      audio.currentTime = 1;                       // half a second is fine; a second is not
      fireEvent(videoOf(), new Event("timeupdate"));
    });

    expect(audio.currentTime).toBe(3);
  });
});
```

- [ ] **Adım 2:** `npm test --prefix queen-editor/frontend -- --run` → kırmızı.

- [ ] **Adım 3 — `LayerPlayer.jsx`:**

```jsx
const BARS = 46;
// How far the sound may drift from the picture before it is pulled back. Below this nobody hears
// it; correcting on every tick would make the sound stutter.
const DRIFT = 0.25;
```

- `useRef` ile `video` ve `audio` ögeleri; `playing`, `at`, `length` durumları.
- `toggle()` → ikisini birlikte başlatır/durdurur.
- `onTimeUpdate` → `at` güncellenir, kayma düzeltilir.
- `onLoadedMetadata` → `length = video.duration`.
- Dalga formu: `peaks` durumu; `useEffect` içinde `fetch(audioUrl) → arrayBuffer →
  AudioContext.decodeAudioData` (yoksa atlanır), 46 tepe hesaplanır.
- Süre biçimi: `m:ss`.

- [ ] **Adım 4:** yeşil.

---

## Görev 3 — Sekme oynatıcıyı açar

**Dosyalar:** `PhotoDetail.jsx`, test: `PhotoDetail.test.jsx`

- [ ] **Adım 1 — kırmızı testler:**

```jsx
  it("plays the video on its own tab", async () => {
    await open("P0_0.png", { frames: [LAYERED] });

    fireEvent.click(tab("Video"));

    expect(document.querySelector("video").getAttribute("src"))
      .toBe("/photos/düğün/P0_0_V1_0.mp4");
    expect(document.querySelector("audio")).toBeNull();
  });

  it("brings the sound along on the sound tab", async () => {
    await open("P0_0.png", { frames: [LAYERED] });

    fireEvent.click(tab("Ses"));

    expect(document.querySelector("video")).toBeTruthy();
    expect(document.querySelector("audio").getAttribute("src"))
      .toBe("/photos/düğün/P0_0_V1_0_S1_0.wav");
  });

  it("leaves the photo tab as it was", async () => {
    await open("P0_0.png", { frames: [LAYERED] });

    expect(document.querySelector("video")).toBeNull();
    expect(screen.getByAltText("P0_0.png")).toBeTruthy();
  });
```

> Test dosyasının `beforeEach`'ine oynatma taklidini de ekle (Görev 2'deki spy).

- [ ] **Adım 2:** kırmızı.

- [ ] **Adım 3 — `PhotoDetail.jsx`:** görsel alanda, üretilmiş kare için:

```jsx
            {open !== "photo" && produced ? (
              <LayerPlayer videoUrl={fileUrl(project, frame.layers.video)}
                           audioUrl={open === "audio"
                             ? fileUrl(project, frame.layers.audio)
                             : null} />
            ) : produced ? (
              <img … />
            ) : …}
```

- [ ] **Adım 4:** yeşil.

---

## Görev 4 — Tam takım, build, commit

- [ ] `npm test --prefix queen-editor/frontend -- --run`
- [ ] `python -m pytest queen-editor -q`
- [ ] `npm run build --prefix queen-editor/frontend`
- [ ] `dist/` ile tek commit:

```
feat(queen-editor): the video plays where the frame is read
```
