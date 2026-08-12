# Queen Editor — Yol Haritası v6

**Tarih:** 2026-08-13 · **Koşu dalı:** `feat/queen-editor-v3` (v5 ile aynı dal, henüz doğrulanmadı) ·
**Durum:** koşu başlamadı.
**Yerini aldığı doküman:** yok — bu, [v5 roadmap](2026-08-12-queen-editor-v5-roadmap.md)'in
kapanışında kullanıcıya kalan iki üretim dosyasının yerine geçen küçük bir koşu.
**Kaynak:** kullanıcı kararı (2026-08-13) — fark belgesi yok, bulgu koşunun kendisinden çıktı.

## Neden bu koşu var

v5 bitti ama uygulama iki üretim dosyası olmadan çalışamıyor: `workflow_video_api.json` ve
`workflow_audio_api.json`. İkisini de "kullanıcı ComfyUI'den Export (API) ile çıkarsın" diye
bıraktık. İkisi de yanlış çıktı:

- **Video grafiği zaten repoda.** `collab-toolbox/video_generator/wan22-arbuzai/workflow_api.json`
  API formatında ve `comfy_video_generator.py`'nin beklediği üç node'un üçünü de taşıyor (287,
  210, 233:240) — `photo_to_video.ipynb` bu grafiğin Drive kopyasını okuyor, aslı burada. Dışa
  aktarılacak bir şey yok, kopyalanacak bir dosya var.
- **Ses için ComfyUI grafı hiç kurulmamış.** `mmaudio_generate.ipynb` ComfyUI kullanmıyor: MMAudio
  reposunu klonlayıp **süreç içinde** çalıştırıyor, NSFW fine-tune ağırlıklarla. queen-editor'ün
  ses üreticisi ise olmayan bir ComfyUI grafiğine (`VHS_LoadVideoPath` + `MMAudioSampler`) yazıldı.

**Kullanıcı kararı (2026-08-13):** ses için ComfyUI grafı kurulmayacak. *"Şu an mmaudio için ne
kullanıyorsak birebir aynısı."* Yani queen-editor de MMAudio'yu süreç içinde çalıştıracak.

## Kapsam sınırı

- **Ses dışındaki motor değişmiyor.** Foto ve video ComfyUI'de kalır; değişen yalnız ses.
- **Defterin toplu iş mantığı taşınmaz.** `mmaudio_generate.ipynb`'in Drive tarama, batch, atlama
  ve mp4'e mux etme kısmı queen-editor'ün işi değil — queen-editor kuyruğu kendisi yönetiyor ve
  sesi ayrı bir `.wav` olarak saklıyor (video ile birleştirme export'un işi, Görev 30). Taşınan
  şey **ses üretiminin kendisi**: model yükleme, chunk'lama, `generate` çağrısı, parametreler.
- **Prompt yazımı değişmez.** Ses prompt'unu bugün olduğu gibi Grok yazıyor (`xai_prompt_writer`);
  defterdeki elle yazılmış `ACTION_PROMPTS` listesi taşınmaz. Defterin **negative prompt'u** ise
  taşınır: o bir model ayarı, kullanıcı metni değil.
- **Foto grafiği değişmez.**

## Bozulan yazılı karar

**FOUNDATION madde 6** bugün *"ComfyUI is the generation engine"* diyor. Ses artık süreç içinde
çalışacağı için bu madde daralıyor: ComfyUI **foto ve video**nun motoru; ses, uygulamanın kendi
sürecinde koşan ikinci bir motor. Maddenin yeniden yazılması Görev 6'nın işi — gerekçesiyle
birlikte, çünkü "neden iki motor" sorusunu ilk soran kişi o dosyaya bakacak.

## Nasıl çalışacağız

v5'teki dört adımın aynısı, görev bitmeden sonrakine geçilmez:

1. **Spec** — `docs/superpowers/specs/`, görevin kararları burada verilir.
2. **Plan** — `docs/superpowers/plans/`, TDD adımlarıyla.
3. **Full TDD** — hiçbir üretim kodu satırı, önce kırmızı bir test yokken yazılmaz.
4. **Commit** — görev başına bir commit; ön yüz değiştiyse `dist/` aynı commit'te.

Komutlar her seferinde birebir aynı: `python -m pytest queen-editor -q`,
`npm test --prefix queen-editor/frontend -- --run`, `npm run build --prefix queen-editor/frontend`.

---

## Blok 1 · Video grafiği

### Görev 1 — Video grafiği repoya girer

- **Ne çalışır:** `queen-editor/workflow_video_api.json` repoda durur; video üreticisi onu açar,
  üç node'unu bulur ve yamalar. Dosya `collab-toolbox`'tan **kopyalanır** — çalışma anında oradan
  okunmaz (CODE-STANDARD'ın bağımsızlık kuralı).
- **Nasıl görülür:** üreticiyi gerçek dosyayla besleyen bir test, üç node'un varlığını ve API
  formatını doğrular; "graf yok" hatası artık çıkmaz. Testin yeri belli: `test_workflow_asset.py`
  foto grafiği için aynısını zaten yapıyor, video onun ikizi olarak yanına yazılır.

### Görev 2 — Model listesi grafiğin istediğini söyler

- **Ne çalışır:** `model_groups.py`'deki video grubu, grafiğin gerçekten adını verdiği dosyalarla
  örtüşür. Bugün örtüşmüyor: graf `SmoothMix_Animations_XXX_High/Low` da istiyor, grup yalnız
  `SmoothMix_I2V_v2_High/Low` sayıyor. Üretici paneli eksik modeli "kurulu" diye gösteriyor.
- **Nasıl görülür:** shipped grafiği okuyup adı geçen her model dosyasının grupta bulunduğunu
  doğrulayan bir test; panel eksik dosyayı eksik olarak söyler.
- **Karar bekliyor:** grafın dört checkpoint'i de gerekli mi, yoksa ikisi devre dışı bir dalda mı
  — Görev 2 spec'inde grafın kendisine bakılarak verilir.

---

## Blok 2 · Ses motoru süreç içine taşınır

### Görev 3 — MMAudio üreticisi

- **Ne çalışır:** yeni bir veri katmanı adaptörü, ses üreticisi portunu ComfyUI yerine MMAudio ile
  karşılar: video dosyasını alır, sesini `.wav` olarak döndürür. Defterin ayarları birebir —
  `large_44k` mimarisi + NSFW fine-tune ağırlık, `NUM_STEPS=40`, `CFG_STRENGTH=5.5`,
  `INFERENCE_MODE="euler"`, negative prompt `"music, speech, voices, singing, talking, vocals"`,
  ve 10 saniyeyi aşan videoda 8 saniye hedefli chunk + 100 ms crossfade.
- **Nasıl görülür:** sahte bir mmaudio modülüyle koşan testler — üretici doğru parametreleri
  geçirir, seed'i kullanır, uzun videoyu parçalar, kısa videoyu parçalamaz, çıkan dosya `.wav`.
- **Üç uygulama gerçeği**, plan yazılırken sürpriz olmasın diye burada:
  - **`torch` ve `mmaudio` import'u tembel olmalı.** Test makinesinde ikisi de yok; modül
    yüklenirken import edilirse tüm takım çöker. İçeri girme noktası enjekte edilir, tıpkı
    diğer adaptörlerin istemcisi gibi.
  - **Port bayt veriyor, MMAudio dosya istiyor.** Üretici portu videoyu `(ad, bayt)` olarak
    veriyor; ffmpeg ve `load_video` yol istiyor. Adaptör baytı geçici bir dosyaya yazar ve
    işi bitince siler.
  - **Seed defterden taşınmaz.** Defter dosya adından seed türetiyor çünkü kuyruğu yok;
    queen-editor her işe zaten kendi seed'ini veriyor, o kullanılır.
- **Karar bekliyor:** modelin ne zaman yükleneceği ve bellekte kalıp kalmayacağı (ComfyUI da aynı
  GPU'da); chunk'lamanın bu sürümde ölü kod olup olmadığı (video süresi sabit ~5 sn); işin kendi
  negative prompt'u boş değilse defterin sabiti mi yoksa işinki mi kazanır.

### Görev 4 — Ses üreticisinin kurulumu

- **Ne çalışır:** üretici paneli sesin gerçekten neye ihtiyacı olduğunu sayar: NSFW ağırlık dosyası
  ve MMAudio'nun kendi temel ağırlıkları. Bugünkü `mmaudio_large_44k_v2.pth` satırı ComfyUI
  node'una aitti ve karşılığı yok.
- **Nasıl görülür:** ses üreticisi kurulu değilken panel eksik dosyayı adıyla söyler; kurulunca
  kuyruk ses işini alır.

### Görev 5 — Bağlama ve eski kodun kaldırılması

- **Ne çalışır:** `main.py` ses üreticisi olarak yeni adaptörü bağlar; `ComfyAudioGenerator` ve
  `AUDIO_WORKFLOW_PATH` silinir. Kuyruk, katman ve export tarafında hiçbir şey değişmez — port
  aynı port.
- **Nasıl görülür:** tam takım yeşil; `workflow_audio_api.json` adı repoda hiçbir yerde geçmez.

### Görev 6 — Defter ve belgeler

- **Ne çalışır:** `app.ipynb`'in kurulum hücresi MMAudio reposunu kurar (klonla + `pip install -e .`)
  ve ağırlıkları hazırlar; `BRANCH` `feat/queen-editor-v3` olur. FOUNDATION madde 6 iki motoru
  anlatacak biçimde yeniden yazılır, CODE-STANDARD'ın miras tablosuna MMAudio satırı eklenir.
- **Nasıl görülür:** defter baştan sona koşunca ses üretimi çalışır; belgelerde ComfyUI'ın tek
  motor olduğunu söyleyen cümle kalmaz.

---

## Kapsam tablosu

| Bulgu | Görev |
|---|---|
| Video grafiği repoda yok | 1 |
| Model listesi grafiğe uymuyor | 2 |
| Ses ComfyUI grafiği yok, olmayacak da | 3 |
| Ses üreticisinin model listesi yanlış | 4 |
| Eski ses adaptörü ve config girdisi | 5 |
| Defter kurulumu ve dal adı | 6 |
| FOUNDATION madde 6 daralıyor | 6 |

## Açık sorular

Hiçbiri bu belgede verilmez; her biri kendi görevinin spec'inde karara bağlanır:

| Seçim | Nerede |
|---|---|
| Grafın dört checkpoint'inin hepsi gerekli mi | Görev 2 |
| MMAudio modeli ne zaman yüklenir, bellekte kalır mı (ComfyUI ile aynı GPU) | Görev 3 |
| Chunk'lama bu sürümde taşınsın mı (video süresi sabit ~5 sn) | Görev 3 |
| Negative prompt: defterin sabiti mi, işin kendi alanı mı | Görev 3 |
| NSFW ağırlığı uygulama mı indirir, defter mi | Görev 4 |

## Sıradaki adım

**Görev 1'in spec'i.** Dal aynı kalır (`feat/queen-editor-v3`); Görev 1 — *Video grafiği repoya
girer* — spec → plan → full TDD döngüsüne girer.
