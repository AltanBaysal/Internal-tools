# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Internal tools monorepo. Each tool lives in its own subfolder with its own `CLAUDE.md`, `requirements.txt`, and entry points.

## Repository Structure

```
internal-tools/
├── colab-tutorial/           # Google Colab tutorial notebook
│   └── CLAUDE.md             # Tool-specific docs
├── mmaudio-generate/         # Text-to-audio generation with MMAudio
│   └── CLAUDE.md             # Tool-specific docs
├── video-frame-extractor/    # First frame extraction from video files
│   └── CLAUDE.md             # Tool-specific docs
├── .gitignore
└── CLAUDE.md                 # This file (root index)
```

## Tools

- **[colab-tutorial](colab-tutorial/CLAUDE.md)** — Google Colab'ı öğrenmek için basit bir Jupyter notebook (GPU kontrolü, toplama, dosya indirme).
- **[mmaudio-generate](mmaudio-generate/CLAUDE.md)** — MMAudio modeli ile metin açıklamasından ses dosyası üretme (text-to-audio).
- **[video-frame-extractor](video-frame-extractor/CLAUDE.md)** — Extracts the first frame from video files (MP4, AVI, MOV, MKV, WEBM) as JPG/PNG.

## Adding a New Tool

1. Create a new subfolder: `my-tool/`
2. Add a `CLAUDE.md` inside it with commands, architecture, and design decisions
3. Add a `requirements.txt` for its dependencies
4. Add the tool to the **Tools** list above
