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
      audio.currentTime = 1;                       // a quarter of a second is fine; a second is not
      fireEvent(videoOf(), new Event("timeupdate"));
    });

    expect(audio.currentTime).toBe(3);
  });

  it("brings the clock inside the video", () => {
    render(<LayerPlayer videoUrl="/v.mp4" />);

    // Fark 114: the times and the line sat under the video in a framed row of their own, so the
    // player read as two things stacked rather than one.
    expect(document.querySelector("[data-scene] [data-track]")).toBeTruthy();
    expect(document.querySelector("[data-track]").style.position).toBe("absolute");
  });

  it("takes the frame off the progress line", () => {
    render(<LayerPlayer videoUrl="/v.mp4" />);

    // A line over a picture needs no box around it: the picture is the contrast.
    expect(document.querySelector("[data-progress]").parentElement.className)
      .not.toContain("wf-stroke");
  });

  it("brings the waveform inside the video too", () => {
    render(<LayerPlayer videoUrl="/v.mp4" audioUrl="/s.wav" />);

    expect(document.querySelector("[data-scene] [data-bar]")).toBeTruthy();
  });

  it("draws the bars nobody has reached yet in translucent white", () => {
    render(<LayerPlayer videoUrl="/v.mp4" audioUrl="/s.wav" />);

    // Fark 115: the faintest ink is a tone for text on the panel's own ground, and these bars
    // stand on a picture.
    expect(document.querySelectorAll("[data-bar]")[45].style.background)
      .toMatch(/rgba\(255,\s*255,\s*255/);
  });

  it("gives the play button an outline and a drawn glyph", () => {
    render(<LayerPlayer videoUrl="/v.mp4" />);

    // Fark 116: the mark inside it was a text character, which is a different shape in every font
    // the browser might fall back to.
    const button = screen.getByRole("button", { name: "Oynat" });
    expect(button.style.borderStyle).toBe("solid");
    expect(button.querySelector("[data-glyph=play]")).toBeTruthy();
  });
});
