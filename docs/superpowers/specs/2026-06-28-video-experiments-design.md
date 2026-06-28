# Video Experiments — İnteraktif ComfyUI Notebook'ları (Tasarım)

- Tarih: 2026-06-28
- Branch: `video-generation`
- İlgili: [collab-toolbox/video_generator/deneme-listesi.md](../../../collab-toolbox/video_generator/deneme-listesi.md)

## Amaç

Farklı video üretim workflow'larını/modellerini Colab Pro'da **görsel olarak** denemek. Her deneme için bağımsız bir notebook: ComfyUI'yi tüm bağımlılıklarıyla kurar, **tünelle bir UI linki** verir. Kullanıcı linke girip workflow JSON'unu UI'a **elle yükler** ve çalıştırır. Toplu/headless üretim yok — amaç deneyimleme/kıyaslama.

## Kapsam — denemeler

| Klasör | Kaynak | Model ailesi |
|---|---|---|
| `ltx23-eros` | LTX 2.3 I2V "Eros" (mrxin) | LTX-Video 2.3 (WAN dışı) |
| `wan22-painter` | WAN 2.2 I2V "PainterI2V" (Kenpechi) | WAN 2.2 I2V |
| `wan22-allinone` | WAN 2.2 I2V "All-in-One" (first/last + loop + upscale + interpolate) | WAN 2.2 I2V |
| `wan22-dasiwa` | DASIWA WAN 2.2 I2V 14B "Lightspeed" (kendi workflow'u ile) | WAN 2.2 I2V |

**Hedef referanslar** (çıktı hedefi — ayrı notebook değil): Civitai video #133122787, #132599076. Eşleşen model ailesinin notebook'unda, Civitai görseli ComfyUI'a sürüklenip workflow alınarak denenir.

## Kapsam dışı (YAGNI)

- Google Drive yok — mount yok, Drive'dan indirme yok.
- Batch/headless API üretimi yok; UI interaktif.
- Otomatik prompt/üretim yok; kullanıcı UI'da elle çalıştırır.
- Workflow JSON'larını notebook **indirmez**; kullanıcı Civitai'den indirip ilgili klasöre koyar, UI'a elle yükler.

## Klasör yapısı

```
collab-toolbox/video_experiments/
├── CLAUDE.md                     # klasör dokümanı (repo konvansiyonu)
├── ltx23-eros/      → ltx23-eros.ipynb      + workflow.json
├── wan22-painter/   → wan22-painter.ipynb   + workflow.json
├── wan22-allinone/  → wan22-allinone.ipynb  + workflow.json
└── wan22-dasiwa/    → wan22-dasiwa.ipynb    + workflow.json
```

Her deneme kendi alt klasöründe; notebook + kullanıcının koyacağı `workflow.json` bir arada.

## Notebook iskeleti (ortak — sadece indirme listeleri farklı)

1. **(md)** Başlık + Input/Output + Sıra
2. **CONFIG** — Civitai `__Secure-civitai-token` cookie (gated indirme), opsiyonlar. **Drive yok.**
3. **ComfyUI kurulumu** — `git clone` ComfyUI + ComfyUI-Manager
4. **Custom node'lar** — workflow'un gerektirdiği node'lar (`git clone` + requirements; Manager fallback)
5. **Model indirme** — HF büyük dosyalar `aria2c -x16`; Civitai gated dosyalar `curl` + **sadece cookie**. Hepsi `/content/ComfyUI/models/...` altına.
6. **Launch + tünel** — `python main.py --listen 0.0.0.0 --port 8188` (arka plan) + `cloudflared` → public link yazdırır; fail-loud sağlık kontrolü.
7. **(md)** "Linke gir → Workflow → `workflow.json` yükle → Run" talimatı.

## Kurallar / kısıtlar (repo standartları)

- **Drive YOK** — modeller her oturumda kaynaktan taze iner (Colab ephemeral disk).
- **Civitai:** sadece `__Secure-civitai-token` cookie; API key `?token=` **yok** (gated asset 401 verir — repo'da kanıtlı kalıp).
- **Fail-loud:** bozuk indirme `is_valid_safetensors` → `RuntimeError`; sunucu 90s'de kalkmazsa `RuntimeError`.
- **Tünel:** `cloudflared`, `--listen 0.0.0.0`.
- **Dil:** markdown + `print` mesajları Türkçe; kod yorumları + docstring İngilizce.

## Bağımlılıklar / sıra

- Her notebook'un **model + custom node listesi, kullanıcının koyacağı `workflow.json`'dan** çıkarılır. Yani JSON'lar klasörlere konduktan sonra notebook'lar doldurulur.
- Mevcut notebook'lar (`imageToVideo.ipynb`, `loop_maker/comfy_ui.ipynb`) şablon olarak kullanılır.
- Bitince kök `CLAUDE.md` + `collab-toolbox/CLAUDE.md` tablosu güncellenir.

## Açık riskler

- Gated Civitai model URL'leri / dosya adları JSON gelince netleşir.
- LTX 2.3 custom node'ları ve model formatı WAN'dan farklı — ayrı node paketleri gerekebilir.
- Colab disk/oturum: her notebook bağımsız oturum; 4 deneme tek oturumda toplanmaz.
