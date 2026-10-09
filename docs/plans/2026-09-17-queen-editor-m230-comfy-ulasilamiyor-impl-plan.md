# Madde 230 · ComfyUI'ye ulaşılamayınca ekran ne olduğunu ve log'u söyleyecek — uygulama turunun planı

**Spec:** [uygulama turu](../specs/2026-09-17-queen-editor-m230-comfy-ulasilamiyor-uygulama-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

## Adımlar

**1 · `errors.py`.** `ComfyUnreachable(base, cause, log_path)`: mesaj üç blok, log okunamazsa yolu ve
`OSError`'ın cümlesi.

**2 · `client.py`.** `log_path=""` parametresi, `_send(method, url, **kw)`, beş çağrı ondan geçer.

**3 · `config.py`, `main.py`.** `COMFY_LOG` ve tesisat.

**4 · Defter.** Flask hücresinin ortamına `QE_COMFY_LOG`.

**5 · Takım koşulur**, dördü de. Beklenen: dördü yeşil.

**6 · Commit**, madde roadmap'te işaretlenir. Ön yüz değişmiyor, `dist` yok.
