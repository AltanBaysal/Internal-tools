# Madde 246 · dynv2 sahneye göre ve en başta — uygulama turunun tasarımı

**Tarih:** 19 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Test turu:** [tasarım](2026-09-19-queen-editor-m246-dynv2-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey bu turda. Etkisi Colab'da görülür.

## Ne değişiyor

**`xai_prompt_writer.py` — `H3_VIDEO_INSTRUCTION`** kullanıcıyla birlikte yazılan metne dönüyor,
olduğu gibi:

```
You are a prompt writer for the MiniMax H3 video model.

I give you: the SDXL prompt of a photo. This photo is the first frame of the video.

I want: the H3 prompt for that video.

Write it like this:

dynv2.

integrated_multimodal_description: [Shot 1] <the motion>

overall_soundscape: <the sounds>

non_diegetic_music: N/A

Rules:
- dynv2. is the first line. Write it for most scenes. Leave it out only if the scene is calm or still.
- The motion: do not describe the photo again, the model already sees it. Say what moves and how. The camera does not move. Keep it natural.
- The sounds: only what the scene and the motion would make.
- Write only the prompt. No quotes, no explanations, no extra text.
```

**`comfy_h3_video_generator.py` — `generate`:** prompt `dynv2` ile başlıyorsa kelime ve ardındaki
nokta ile boşluklar prompt'tan alınıyor, ve modele giden metin `dynv2. <resim cümlesi>\n\n<geri kalanı>`
oluyor. Başlamıyorsa bugünkü gibi `<resim cümlesi>\n\n<prompt>`. Dört yere aynı metin yazılmaya devam
ediyor.

WAN'ın talimatı ve üreticisi değişmiyor.
