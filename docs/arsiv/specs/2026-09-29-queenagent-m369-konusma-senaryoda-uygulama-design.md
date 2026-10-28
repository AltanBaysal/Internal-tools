# Madde 369 (v9-11) — Konuşma senaryonun içine yazılır: uygulama

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 369 · v9-11.
**Testler:** [test spec'i](2026-09-29-queenagent-m369-konusma-senaryoda-testler-design.md), kırmızı
commit `3aa51a0a`.

**Kullanıcıdan gereken:** yok.

## Ne yazılır

İki madde işareti, ikisi de `queen-agent/backend/features/workspace/domain/prompt.py`'de. Kod
değişmez: `_frame_seen` ve `build_prompts` sahne cümlesini zaten olduğu gibi taşıyor.

### 1. `START_A_SCENARIO`, Step 4

Yeni satır, `Write them with add_scene: one sentence each, ...` satırının hemen altına — konu o cümle,
ve 368'in kıyafet satırı ile `Write no actions here.` arkasından gelir:

> - If the user wants someone to speak in a frame, write their words, in quotation marks, into that
>   frame's scene sentence: the video's prompt is written from it.

- **Tırnak:** H3 prompt'unu yazan model söylenen sözü cümlenin anlatımından ayırabilsin diye; söz
  kelimesi kelimesine taşınır.
- **Neden cümlenin sonunda:** "the video's prompt is written from it" — model bir kuralı nedeniyle
  birlikte daha iyi uygular, ve bu, sözün fotoğrafa değil videoya ait olduğunu söyler.
- **Koşullu:** yalnız kullanıcı istediğinde. Konuşma icat edilmez; bunu ayrı bir yasakla söylemek
  gerekmiyor, SYSTEM_PROMPT zaten "Ask rather than invent" diyor.
- **Yalnız konuşma** — ses, müzik ya da başka bir ekstra yok *(kullanıcı — "başka yok gibi")*.

### 2. `WRITE_FRAME_SYSTEM_PROMPT`

Yeni satır, `Use what you are shown only to make your line fit it. ...` satırının altına — ikisi de
yazara gösterilenden ne alınacağını söylüyor:

> - If somebody speaks in the scene, leave their words out of your line. The model cannot draw
>   speech, and quoted words come back drawn as text in the picture.

- `SDXL_PROMPT_RULES`'a girmez: o metin altı harita aracıyla da gidiyor, ve hiçbiri aksiyon yazmıyor.
- Yalnız **sözler** dışarıda kalır; açık ağız gibi bir yüz ifadesini yazmak yazarın kendi işi, bu kural
  ona karışmaz.

## Kelime sayısı

Start a scenario 475 kelimeden 504'e çıkar (+29), tavan 1000 *(Madde 367)*. Edit prompts değişmez.

## Kapsam dışı

- **Edit prompts:** orada ajan aksiyonu kendisi `update_frame` ile yazıyor, ve `UPDATE_FRAME_ACTION`
  onu "as tags" diye tarif ediyor. Bir sızıntı görülürse ayrı bir madde; burada kural tek yerde, onu
  okuyan yazarda.
- **Araç tarifleri** (`ADD_SCENE_SCENE`, `UPDATE_FRAME_SCENE`): madde Start a scenario'nun adımına ait.
