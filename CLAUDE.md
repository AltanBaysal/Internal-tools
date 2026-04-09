# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Internal tools monorepo. Each tool lives in its own subfolder with its own `CLAUDE.md`, `requirements.txt`, and entry points.

## Repository Structure

```
internal-tools/
├── desktop-toolbox/          # Desktop app bundling multiple internal tools (first module: video frame extraction)
│   └── CLAUDE.md             # Tool-specific docs
├── mmaudio-generate/         # Text-to-audio generation with MMAudio
│   └── CLAUDE.md             # Tool-specific docs
├── .gitignore
└── CLAUDE.md                 # This file (root index)
```

## Tools

- **[desktop-toolbox](desktop-toolbox/CLAUDE.md)** — Masaüstü uygulaması; birden fazla iç aracı modül olarak barındırır. İlk modül: video frame extraction (ilk kare çıkarma).
- **[mmaudio-generate](mmaudio-generate/CLAUDE.md)** — MMAudio modeli ile metin açıklamasından ses dosyası üretme (text-to-audio).

## Adding a New Tool

1. Create a new subfolder: `my-tool/`
2. Add a `CLAUDE.md` inside it with commands, architecture, and design decisions
3. Add a `requirements.txt` for its dependencies
4. Add the tool to the **Tools** list above
