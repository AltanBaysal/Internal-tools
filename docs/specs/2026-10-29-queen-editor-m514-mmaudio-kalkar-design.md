# Madde 514 · MMAudio kalkar — tasarım

**Tarih:** 29 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-13),
514 · v11-13 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Plan:**
[2026-10-29-queen-editor-m514-mmaudio-kalkar-plan.md](../plans/2026-10-29-queen-editor-m514-mmaudio-kalkar-plan.md)
· **Kurallar:** queen-editor [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md) · **Örnek:** 508
([spec](../arsiv/specs/2026-10-28-queen-editor-m508-qwen-kalkar-design.md))

## Kabul koşulu (maddeden)

MMAudio'yla yeni ses üretilemiyor. Yan paneldeki "Ses üret" sekmesi ve defterin MMAudio kutucuğu yok,
defter onun dosyalarını indirmiyor, üreticisi ve graph'ı gitti. Daha önce üretilmiş sesler olduğu gibi
kalıyor: kare sayfasında çalıyor, export'a giriyor, silinebiliyor.

Kullanıcı, 29 Ekim: *"mmaudio zaten silenecek roadmape ekle sil"*; *"girsin sadece modeli kaldır yeter
başka bir şeye karışma"*. Madde yalnız modeli kaldırıyor. 510'un ses düğmesi (koşulu dahil; 515 onu
değiştirecek), export'un sesle işi ve 511–513'ün kayıt ve sıra kuralları değişmiyor. Ekrandaki sürüm V11
kalıyor.

**Yapılırken kararlaşan** *(kullanıcı, 29 Ekim; ana ajanın aktardığı)*:
- Export ekranının *"⚠ N videonun sesi yok"* satırı **kalkar** — *"Kalksın"*. Satır ses katmanı olmayan
  her videoyu sayıyordu, ama H3 videosu kendi sesini taşıyor. 510'un *"⚠ N videonun sesi kapalı"*
  satırı kalır.
- Sırada borçlu ya da kırmızı eski bir ses işi için hiçbir şey değişmez — *"öyle bir proje yok"*.

MMAudio'nun graph'ı hiç olmadı: ses, FOUNDATION 6'nın eski kuralıyla Flask sürecinin içinde, kütüphane
olarak çalışıyordu. "Graph'ı gitti" burada şu demek: onu çağıran kod (sampler, üretici, ffmpeg kesici,
parça kuralı, prompt yazıcı) ve defterdeki kütüphane kurulumu gidiyor.

## Yeni ses nereden doğuyordu

Üç kapı yeni bir `audio` işi doğuruyordu. Üçü de kapanıyor:

| Kapı | Bugün | 514'ten sonra |
|---|---|---|
| Yan paneldeki **Ses üret** sekmesi → `POST …/layers/audio` | sıraya ses işi | sekme yok; rota `audio`'yu bugünkü yoluyla geri çevirir: `QUEUEABLE`'da yok → 404 *"Böyle bir katman yok: audio"* |
| Kare sayfası, ses sekmesi, **Yeniden üret — yeni kare** → `POST …/regenerate` | kopya karede yeni ses işi | düğme yok, sesin prompt'u salt okunur gösterilir; rota `audio`'yu aynı 404'le geri çevirir |
| Kare sayfası, kırmızı ses, **Tekrar dene** | kırmızı sesi sıraya geri koyar | değişmez (511–513'ün alanı); aşağıdaki "eski borç" gibi bekler |

Kopyalar (`copy_frames`, `carry_layers`) bitmiş sesi taşır, yeni ses üretmez; dokunulmaz.

## Çıkanlar

| Yer | Çıkan |
|---|---|
| `backend/features/photo_generation/data/mmaudio_sampler.py` | dosyanın tamamı |
| `backend/features/photo_generation/data/mmaudio_generator.py` | dosyanın tamamı |
| `backend/features/photo_generation/data/ffmpeg_audio.py` | dosyanın tamamı (yalnız MMAudio'ya video kesiyordu; export'unki `ffmpeg_video_exporter.py`) |
| `backend/features/photo_generation/domain/audio_chunks.py` | dosyanın tamamı (MMAudio'nun 8 sn parça kuralı) |
| `backend/features/photo_generation/data/prompt_writer.py` | `AUDIO_INSTRUCTION`, `AudioPromptWriter` |
| `backend/main.py` | MMAudio'nun, `FfmpegAudio`'nun ve `AudioPromptWriter`'ın import'u; `_audio_generator`; `_producers`'taki ve `_writers`'taki `layers.AUDIO` |
| `backend/config.py` | sesin graph'ı olmadığını söyleyen yorum |
| `backend/features/producers/domain/model_groups.py` | `HF_MMAUDIO_NSFW`, `GROUPS["audio"]`, `audio_weights` |
| `backend/features/producers/domain/ports.py`, `data/comfy_models.py` | `ModelFiles.path` — tek okuyucusu `audio_weights`'tı; `ComfyModelFiles` onu kendi içinde `_path` olarak kullanmaya devam eder |
| `backend/features/producers/domain/producers.py` | `AUDIO`, `ORDER`'daki ve `NAMES`'teki yeri — Üreticiler paneli iki satır |
| `backend/features/photo_generation/presentation/routes.py` | `QUEUEABLE`'daki `AUDIO`; `/regenerate` `queue.ORDER` yerine kendi `REMAKEABLE`'ına (fotoğraf, video) bakar |
| `colab/sound.py` | dosyanın tamamı |
| `queeneditor.ipynb` | `INSTALL_AUDIO` kutucuğu, assert'teki ve seçilenler listesindeki yeri, formdaki "ses ~9 GiB"; `MMAU`, `HF_AUDIO`, `hf_jobs`'taki, `SIZES`'taki ve `FOLDERS`'taki ses satırları; "Ses motoru" başlığı ve iki hücresi; yardımcılar hücresinde `colab.sound` import'u ve listedeki adı; girişte "video ve ses için" → "video için" |
| `frontend/…/SidePanel.jsx` | `PANELS`'teki "Ses üret", `GLYPH`'teki ses, `open === "audio"` |
| `frontend/…/LayerPanel.jsx` | `WORDS.audio` ("MMAudio v2" dahil), `eligible`'ın ses dalı, `words.model` yedeği, `SoundGlyph` import'u; ses paneli yüzünden duran `layer === "video"` soruları (mod varsayılanı, Kareden/Referanstan sekmeleri, taslak, havuzun kapanışı, Üretim modu satırı, video ayarları) — artık hep doğruydular |
| `frontend/…/PhotoDetail.jsx` | ses sekmesinde Yeniden üret ve yazılabilir prompt |
| `backend/…/usecases/export_summary.py`, `frontend/…/ExportScreen.jsx` | özetin `silent` sayısı (başka okuyanı yoktu) ve ekranın *"⚠ N videonun sesi yok"* satırı; `muted` ve satırı kalır |
| `queen-editor/BACKLOG.md` | "MMAudio silinecek" maddesi — bu madde onu yapıyor |
| testler | yalnız bunları sınayan dosyalar silinir: `test_mmaudio_generator.py`, `test_ffmpeg_audio.py`, `test_audio_chunks.py`, `test_colab_sound.py`; öteki dosyalardaki ses üretimi testleri ve örnekleri çıkar. Silinen adları kodda arayan bir tarama eklenmez; defterde kutucuğun ve indirmenin kalmadığını defterin testi söyler (kullanıcının gördüğü ~9 GiB'lık kutu) |

**Belgeler, bugün doğru olanı söylesin diye** *(ana ajan, 29 Ekim)*: FOUNDATION 6 (ses artık üretilmiyor;
ComfyUI tek motor) ve 9 (iki kutucuk), CODE-STANDARD'ın MMAudio satırı, `colab/` listesindeki `sound.py`
ve Tests'teki "MMAudio's weights", `queen-editor/README.md` ve `BACKLOG.md`'deki MMAudio sözleri. Belgeleri
okuyan test yok (madde 431).

## Kalanlar

- **Eski sesler:** kayıttaki satırları, dosyaları, `layers.AUDIO`, `queue.ORDER`'daki yeri, adları
  (`photo_name.layer_file`), galerinin "ses" rozeti, kare sayfasının Ses sekmesi ve oynatıcısı, 510'un
  düğmesi ve `mute.py`, **Sesi sil**, **Kareyi sil**, seçim çubuğunun **Sesleri sil**'i, export ve
  özetin `muted` sayısı. `REMOVABLE` sesi silmeye devam eder.
- **Ekranın ses sözleri:** kuyruk panelinin "Ses" kartı, `useGeneration`'ın sayımları, 509 bildiriminin
  "ses" kelimesi, `frame_status` ve `layer_words` — eski sesler ve eski borçlar için.
- **run_loop:** dokunulmaz. `_has_words`'ün ve `UNDER`'ın ses dalları artık ses işine hiç ulaşmaz
  (yazıcı da üretici de yok), ama döngü türleri bir haritadan okur ve ses türü verilerde duruyor.
- **LayerPanel'in biçimi:** bileşen, adı ve `layer` alanı kalır (`WORDS[layer]`, kopya ve kapsam sayımı
  onu okur; SidePanel `"video"` verir). Yalnız ses yüzünden duran dallar çıkar; paneli yeniden
  kurmuyor, başka bir davranışını değiştirmiyor.
- **Referans havuzunun sesleri** (`ReferencePanel`, kullanıcının yüklediği ses dosyaları) MMAudio değil,
  H3'ün okuduğu havuz: kalır. H3'ün kendi ses VAE'si de kalır.
- `collab-toolbox/mmaudio_generate.ipynb` ve README satırı kalır *(ana ajan, 29 Ekim — "leave
  collab-toolbox alone")*.

## Eski veri: sırada borçlu kalmış bir ses işi

Yeni kod yazılmıyor, 508 gibi. `layers.AUDIO` artık `_producers`'ta da `_writers`'ta da yok, bu yüzden
run_loop'un bugünkü kuralı geçerli: sıra o işe gelince durur ve `waiting`, `waitingFor: "audio"` der
(`run_loop.make_job`, *"the engine for it is not here"*). İşin prompt'u yazılmaz, DeepSeek'e istek gitmez,
satır yazılmaz; iş borçlu kalır.

- **Bildirim:** 509'un bekleme cümlesi gelir, *"Sıra durdu: ses üreticisi kurulu değil."*
- **Kuyruk paneli:** "Bekliyor — üretici kurulu değil", altında "N ses". Üreticiler listesinde ses satırı
  hiç dönmediği için **Kaldığı yerden devam et** çıkmaz; **Kuyruğu temizle** açıktır.
- **Kullanıcının çıkış yolu:** kareyi seçip **Sesleri sil**. `remove_layer` borçlu sesi `removed`'la
  sıradan çıkarır, kare ve videosu kalır; sonra Devam et ya da yeni bir Kuyruğa ekle sırayı sürdürür.
  Ya da **Kuyruğu temizle** (borçlu bütün işler çıkar).

Kuyruk panelinin, bildirimin ve kare sayfasının cümleleri ve Tekrar dene kapıları bunun için değişmez:
böyle bir proje yok *(kullanıcı, 29 Ekim — "öyle bir proje yok")*. Yukarısı, kodun bugünkü kurallarıyla ne
olacağını söyler, bir iş istemez.

## Colab'a daha önce yüklenmiş eski defter

Eski defter `from colab.sound import …` satırında *"No module named 'colab.sound'"* ile durur. Kullanıcı
yeni defteri yükler; 508'deki eski grafik listesi gibi.

## Maliyet

Yeni bir işlem yok; her istek bugünkünden az ya da onun kadar gider. Üreticiler listesi diski bir satır az
okur (sesin tek dosyası). Ses işini sırada gören tur bugünkü gibi planı, kaydı ve sırayı birer kez okur
(`snapshot`), sonra bekler: DeepSeek'e ve diske ek gidiş yok. Defter ~9 GiB ses indirmesini ve MMAudio'nun
pip kurulumunu (30 dk'ya kadar) artık hiç yapmaz. Export özeti aynı okumalarla döner, bir sayı eksik.
Silinen ve kaybolan veri yok: Drive'daki hiçbir şeye dokunulmaz.

## Bitti sayılır

- `main._producers` fotoğraf ve video; `main._writers` yalnız video. main'in kablosuyla, sırada eski bir
  ses işi olan bir proje `waiting` / `waitingFor: "audio"` ile durur, yazıcıya istek gitmez (testli).
- `GET /api/producers` iki satır verir: fotoğraf ve video.
- `POST …/layers/audio` ve `POST …/regenerate` (`layer: "audio"`) 404 ile *"Böyle bir katman yok: audio"*;
  `POST …/layers/audio/delete` sesi silmeye devam eder.
- Yan panelin rayında "Ses üret" yok; kare sayfasının ses sekmesinde ses çalıyor, prompt salt okunur,
  Yeniden üret yok, Sesi sil ve Kareyi sil var.
- Export özetinde `silent` yok, ekranında *"videonun sesi yok"* satırı yok; *"videonun sesi kapalı"*
  satırı var.
- Defterde `INSTALL_AUDIO`, `HF_AUDIO`, `MMAU`, `install_mmaudio`, `fetch_mmaudio_weights`, `colab.sound`
  yok; `colab/sound.py` yok.
- `queen-editor/` kodunda (belgeler ve 514'ün kendi testleri dışında) MMAudio'ya giden bir satır kalmaz.
- `dist` yeniden derlendi; iki queen-editor takımı yeşil.
