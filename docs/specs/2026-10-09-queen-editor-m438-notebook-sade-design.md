# Madde 438 · Notebook sadeleşir: kodu `colab/` modüllerine taşınır — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
438 · **Dal:** `feat/queen-editor-v9` · **Kurallar:** [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Ne, neden

Kullanıcı, 9 Ekim: *"bu kodlar oalbildiğince pythona alalım noteboo ksade olsun böylece kodu verfiy
etmemizde kolaylaşır"*. Hücrede duran kod pytest altında hiç koşmuyor. Testler bugün yalnız hücrenin
metnini okuyabiliyor; bir satırın orada yazılı olduğunu söylüyorlar, çalıştığını değil. Madde 433
`start_comfy`'yi böyle taşıdı: kod `colab/comfy.py`'de, testli, ve hücre onu çağıran bir satır. Bu madde
aynısını notebook'un kalan hücrelerine yapar.

437'nin incelemesi bir şey daha buldu. Kasadan okuma notebook'ta dört kez yazılı:
`try: (userdata.get(X) or "").strip() except …`. Okunanlar `GITHUB_TOKEN`, `CIVITAI_COOKIE`,
`DEEPSEEK_API_KEY` ve 437'nin `use_hf_token`'daki `HF_TOKEN`'ı. Bu madde son üçünü tek bir `colab/`
fonksiyonuna toplar. `GITHUB_TOKEN` klondan önce okunur, ve klondan önce `colab/` yok; o yüzden
CONFIG'de kalır.

## Kurallar

- **Davranış değişmez.** Aynı adımlar, aynı sırayla, aynı konsol satırlarıyla. Bugün çalıştırılan bir
  hücre bugünkü işi yapar. Bunun dışında kalan her fark aşağıda, *Değişen* başlığında adıyla yazılı.
- **Notebook'ta kalan üç şey var:**
  - Colab'ın form alanları (CONFIG'in `#@param`'ları).
  - Başlıklar ve açıklamalar.
  - Klondan önce koşması gerekenler: `colab/` klonla gelir.
- **İndirme listeleri notebook'ta kalır**, onları seçen kutuların yanında. `colab/downloads.py`'nin
  docstring'i ve FOUNDATION 9 öyle diyor: adresler orada durur. Ne indirileceğini söyleyen her veri
  de aynı sebeple kalır: hangi grubun diske ne kadar yer tuttuğu ve özetin hangi klasörleri gösterdiği.
  Hepsi kutulara bağlı.
- **Her iş kendi modülünde.** Bir hücrenin işi ona uyan bir modüle gider, var olana ya da yeni bir
  modüle. Bir dosya zaten import edildiği için ona iş konmaz.
- **Uygulama `colab/`'u hiç import etmez, `colab/` da uygulamadan hiçbir şey import etmez**
  (CODE-STANDARD, *Notebook code*).

## Hücre hücre

Hücreler Run all'ın sırasıyla. "Kalır" diyen her satır nedenini de söylüyor.

### 0 · Giriş (markdown) — kalır

Bir başlık ve açıklama. Değişmez.

### 1 · CONFIG — kalır; iki secret çıkar

Bu hücre klondan önce koşar ve `colab/`'u göremez. İçindekiler:

- **Sayaç** (madde 312). Drive'ın ve klonun süresini de ölçtüğü için `colab/`'dan gelemez.
  CODE-STANDARD bunu zaten söylüyor.
- **Form alanları** ve iki seçim kontrolü (`assert`). Seçim kontrolleri, bir şey kurulmadan önce
  koşmalı.
- **`GITHUB_TOKEN`'ın okunuşu ve kontrolü.** Klon onunla yapılıyor.
- **Sabitler:** `BRANCH`, `REPO`, `CLONE_DIR`, `APP_DIR`, `APP_PORT`, `DRIVE_FOLDER`, `HF_MIRROR`,
  ComfyUI'nin portu, kökü, log'u ve adresi. Her hücre bunları okur. Drive klasörü ve ayna burada,
  bir kez adlanır (FOUNDATION 7).
- **GPU kontrolü** ve özet satırları. Ağır işten önce düşmeli; bugün de CONFIG'de düşüyor.

**Çıkan:** `=== Secrets ===` bölümü, yani `CIVITAI_COOKIE`'nin ve `DEEPSEEK_API_KEY`'in okunuşu.
İkisi ortak yardımcılar hücresine gider ve `read_secret`'le okunur (hücre 4).

### 2 · Drive'ı bağla — kalır

Klondan önce koşar. Sayaç onun süresini ölçüyor; bu süreye kullanıcının izin penceresinde beklediği
zaman da giriyor.

### 3 · Klon — kalır

`colab/`'u getiren hücre bu; kendisi de klondan önce yazılmış olmalı. Klondan sonra kontrol ettikleri
— derlenmiş arayüz ve üç grafik — klonun kendi doğrulaması. Bunları sonraki hücreye almak klonun işini
iki hücreye bölerdi.

### 4 · Ortak yardımcılar — kalır, ve üç secret'ı okur

Bu hücre `colab/`'u yola koyuyor ve import ediyor; kendisi `colab/`'dan gelemez. İçindekiler:

- `sys.modules`'tan eski `colab`'u siliyor, ve `APP_DIR`'i `sys.path`'e ekliyor.
- Import'lar. Her hücrenin çağırdığı her ad burada import edilir, 433'teki gibi. Notebook'un artık
  çağırmadığı adlar import listesinden çıkar: `hf_fetch`, `civitai_fetch`, `install_node`, `human`,
  `run`.
- `✓ Ortak yardımcılar hazır (klondan: …)` satırı. Satır modülleri sayıyor, ve yeni modüller ona
  eklenir.
- **Kasa, klondan sonraki ilk yer.** Üç secret burada, ve bugünkü sırayla okunur:
  - `COOKIE_VALUE, _ = read_secret(userdata.get, "CIVITAI_COOKIE")`
  - `DEEPSEEK_API_KEY, _ = read_secret(userdata.get, "DEEPSEEK_API_KEY")`
  - `use_hf_token(userdata.get)`. Bu da içeride `read_secret`'i çağırır.

**Neden burada, kullanıldıkları hücrede değil:** bugün ikisi de CONFIG'de, yani en başta okunuyor.
Klondan sonraki ilk hücre o ana en yakın yer. Kasa ayrıca yalnız Colab'ın arayüzünden koşulunca cevap
veriyor (437); Run all'ın başında okunan bir secret, indirmenin ortasında kasaya gidilmesini önler.

### `read_secret` — yeni `colab/vault.py`

```python
def read_secret(read, name):
    """(value, problem): the secret read with `read` -- the notebook's userdata.get -- and trimmed, with
    problem None; or "" and the sentence that says why there is none."""
```

- Okunduysa ve boş değilse `(kırpılmış değer, None)` döner.
- Okuma bir hata attıysa `("", f"{name} okunamadı — {Tür}: {mesaj}")` döner.
- Değer boşsa, `None`'sa ya da yalnız boşluksa `("", f"{name} boş")` döner.
- Hiçbir şey basmaz. Ne basılacağına çağıran karar verir.

`use_hf_token` bugünkü iki cümlesini `read_secret`'in verdiği `problem`'den alır. Metin harfi harfine
aynı kalır (`HF_TOKEN okunamadı — …`, `HF_TOKEN boş`). Çerez ile DeepSeek anahtarının `problem`'i,
bugünkü gibi, basılmaz.

Modülün adı `secrets` değil, `vault`: Python'un standart `secrets` modülüyle karışmasın. "Kasa" sözü
yol haritasınınki de.

### 5 · Başlık: ComfyUI + Custom Node'lar (9) — kalır

### 6 · ComfyUI + custom node'lar — liste kalır, kod çıkar

**Kalan:** `CUSTOM_NODES` listesi. CODE-STANDARD, listenin ComfyUI hücresinde durduğunu söylüyor;
başlıktaki ve girişteki sayı onunla karşılaştırılıyor.

**Hücre olur:**

```python
apt_install("aria2", "ffmpeg")
install_comfy(COMFY_ROOT)

CUSTOM_NODES = [ … ]                      # dokuz satır, bugünkü gibi
install_nodes(CUSTOM_NODES, f"{COMFY_ROOT}/custom_nodes")
```

- **`apt_install(*packages)` — yeni `colab/system.py`: makinenin kendi paketleri.** Önce
  `apt-get update -qq`, sonra `apt-get install -y <paketler>`. Çıktıları bugünkü gibi basılmaz
  (`> /dev/null 2>&1`). Liste yenilenir, çünkü runtime'ın paket listesi arşivden eski olabilir; o
  zaman kurulum artık olmayan dosyaları ister *(QA, 9 Ekim)*. aria2 indirme
  için, ffmpeg uygulamanın export'u ve ComfyUI'nin video node'ları için; ikisi de ComfyUI'nin değil, o
  yüzden `comfy.py`'ye gitmez.
- **`install_comfy(root)` — `colab/comfy.py`'ye.** Modül ComfyUI'yi başlatıyor; artık onu kuruyor da.
  Sırasıyla:
  1. Klasör yoksa `git clone https://github.com/comfyanonymous/ComfyUI.git <root>`.
  2. `git pull -q`.
  3. `pip install -q -r requirements.txt`.
  4. `pip install -q opencv-python imageio imageio-ffmpeg`.

  Hepsi `console.run`'dan geçer; klon dışındakiler `cwd=root` ile. Çıktıları hücreye canlı gelir.
  Düşen bir klon ya da pip hücreyi durdurur. **Düşen `git pull` ise durdurmaz:** git'in kendi
  satırları bir `WARN` ile basılır, ve kurulum yerindeki ComfyUI'yle sürer. Pull yalnız yerinde
  duran, çalışan bir ComfyUI'de koşar. Aynı runtime'daki ikinci Run all onu git'in pull
  yapamayacağı bir halde bulabilir, örneğin detached HEAD ya da yerel değişiklik *(QA, 9 Ekim)*.
- **`install_nodes(nodes, folder)` — `colab/nodes.py`'ye.** Bugün hücrede duran döngü: her node için
  `install_node`, sonra `✅ 9 custom node hazır`.
- **`pip install -q -U hf_xet` bu hücreden çıkar**, ve modeller hücresinin başına gider (hücre 8).
  O bir indirme işi, ComfyUI'nin değil. İki hücre arasında başka bir şey koşmuyor, bu yüzden sıra
  değişmez.

### 7 · Başlık: Modeller — kalır

### 8 · Modeller — listeler ve seçim kalır, iş çıkar

**Kalanlar, hepsi veri:**

- **Hedef klasörler** (`CKPT`, `LORA`, …): listeler onlarla yazılıyor.
- **İndirme listeleri:** `PHOTO_CHECKPOINTS`, `PHOTO_MODELS`, `CIVITAI_PHOTO`, `HF_PHOTO`, `HF_H3`,
  `CIVITAI_H3`, `HF_AUDIO`.
- **Seçimler:** `CHOSEN_MODELS`, `CHOSEN_CHECKPOINTS`, `civitai_jobs`, `hf_jobs`.
- **Boyutlar:** `PHOTO_GIB` ve `SIZES`.
- **Özetin göstereceği klasörler:** `FOLDERS`. Bugünkü `if INSTALL_…: folders += […]` zinciri,
  `SIZES` gibi bir tabloya döner: `(açık mı, başlık, klasör, desen)`. Sıra aynı kalır: checkpoints,
  upscale_models, diffusion_models, vae, text_encoders, vae_approx, loras, mmaudio. loras'ın anahtarı
  `INSTALL_PHOTO or INSTALL_VIDEO`, bugünkü gibi.

**Hücrenin işi olur:**

```python
install_hf_xet()
check_disk(SIZES)
landed = download_models(hf_jobs, civitai_jobs, HF_MIRROR, COOKIE_VALUE)
show_folders(FOLDERS)
download_summary(landed)
if INSTALL_PHOTO:
    log(f"Fotoğraf modelleri: {', '.join(CHOSEN_MODELS)}")
log("Seçilen modeller indirildi ve doğrulandı", "OK")
```

Hepsi `colab/downloads.py`'de, çünkü hepsi indirmenin kendisi:

- **`install_hf_xet()`:** `pip install -q -U hf_xet`, `console.run`'la. hf_xet olmazsa
  huggingface_hub HF'nin köprüsüne döner (xet-core #821); kural `hf_fetch`'in kuralı.
- **`check_disk(sizes)`:** bugünkü `Seçim: … — ~N GiB | Diskte boş: X GiB` satırını basar.
  `/content`'te seçilenler + 5 GiB pay yer yoksa bugünkü `❌ Disk yetmiyor: …` hatasını atar. Pay,
  modülün `HEADROOM = 5`'i.
- **`download_models(hf_jobs, civitai_jobs, mirror, cookie)`:** önce HF dosyaları, sonra Civitai
  dosyaları, bugünkü sırayla. Her dosyanın satırını toplar ve listeyi döndürür. Klasörü açan
  indiricilerin kendisi *(reviewer, 9 Ekim)*:
  - `hf_fetch`, dosyayı yerine koymadan önce;
  - `fetch`, curl ya da aria2c `.part`'ı içine yazmadan önce.
- **`show_folders(folders)`:** açık olan her klasör için `📂 <başlık>/` ve altında dosyaları,
  boyutlarıyla. Bugünkü glob'un aynısı, `recursive=True` ile.
- `download_summary` bugünkü gibi.

Son iki `log` hücrede kalır. İkisi de kutulara bağlı tek satır; bir fonksiyona sarmak hiçbir şey
kazandırmaz.

### 9 · Başlık: Ses motoru — kalır

### 10 · Ses motoru, kütüphane — kutu kalır, iş çıkar

```python
MMAUDIO_DIR = "/content/MMAudio"

if INSTALL_AUDIO:
    install_mmaudio(MMAUDIO_DIR)
else:
    log("Ses motoru: atlandı (INSTALL_AUDIO kapalı)")
```

**`install_mmaudio(folder)` — yeni `colab/sound.py`: ses motoru.** Bugünkü sırayla:

1. Klasör yoksa `MMAudio klonlanıyor…`, sonra `git clone --depth 1`, 300 sn.
2. `MMAudio kuruluyor…`, sonra `pip install -e .`, `-q` olmadan, 1800 sn (madde 398).
3. `✅ MMAudio kütüphanesi kuruldu`.

Modülün adı `mmaudio` değil, `sound`: MMAudio'nun kendi paketi `mmaudio`, ve aynı ad okuyanı yanıltır.

**Kutu hücrede kalır:** kararı kutu veriyor, işi fonksiyon yapıyor. Fonksiyona bir `if` bayrağı
geçmek, onun işini ikiye bölerdi.

### 11 · Ses motoru, ağırlıklar — kutu kalır, iş çıkar

```python
if INSTALL_AUDIO:
    fetch_mmaudio_weights(MMAUDIO_DIR, APP_DIR)
else:
    log("MMAudio ağırlıkları: atlandı (INSTALL_AUDIO kapalı)")
```

**`fetch_mmaudio_weights(folder, app_dir)` — `colab/sound.py`'ye.** Bugünkü sırayla:

1. `app_dir` yoksa bugünkü cümleyle düşer: `❌ Uygulama klasörü yok: …`.
2. `folder` `sys.path`'te değilse en başa eklenir.
3. Çalışma klasörü `app_dir` olur.
4. `mmaudio.eval_utils.all_model_cfg["large_44k"].download_if_needed()` çağrılır.
5. Çalışma klasörü, hata olsa da, eski haline döner.
6. `✅ MMAudio ağırlıkları hazır → <app_dir>`.

### 12 · Başlık: ComfyUI'yi başlat — kalır

### 13 · ComfyUI'yi başlat — değişmez

Madde 433'ten beri tek satır: `comfy_process = start_comfy(COMFY_ROOT, COMFY_PORT, COMFY_LOG)`.

### 14 · Flask + cloudflared — ayarlar kalır, iş çıkar

```python
FLASK_LOG = "/content/flask.log"

link = serve(APP_DIR, APP_PORT, FLASK_LOG, {
    "QE_DRIVE_ROOT": DRIVE_ROOT, "QE_COMFY_URL": COMFYUI_URL, "QE_COMFY_ROOT": COMFY_ROOT,
    "QE_COMFY_LOG": COMFY_LOG, "QE_PHOTO_MODELS": ",".join(CHOSEN_MODELS),
    "QE_DEEPSEEK_API_KEY": DEEPSEEK_API_KEY})
show_link(link, cell_elapsed())
follow(FLASK_LOG)
```

**Kalan:** uygulamaya geçen ayarlar (`QE_*`). Bunlar notebook'un uygulamaya söylediği şeyler ve
CONFIG'in değerlerini adlandırıyorlar. Uygulama, hangi modellerin seçildiğini ve dosyaların nerede
olduğunu ancak buradan öğrenir.

**`cell_elapsed()` hücrede çağrılır:** sayaç notebook'ta, ve süre bağlantı alındığı anda okunur.

**Yeni `colab/server.py`: uygulamanın sunucusu ve tüneli.** Hepsi bugünkü sırayla, bugünkü
satırlarla:

- **`serve(app_dir, port, log_path, settings)`** bağlantıyı döndürür:
  1. `pkill -f backend.main`, `pkill -f cloudflared`, 2 sn bekle.
  2. Flask'ı başlatır: `python -m backend.main`, `cwd=app_dir`. Ortamı `os.environ` +
     `settings`; çıktısı `log_path`'e.
  3. 2 sn'de bir, en çok 45 kez `/api/health`'e bakar. Cevap gelince `✓ Flask ayakta (Ns)` basar.
     90 sn'de gelmezse Flask log'unun son 30 satırını basar, ve
     `❌ Flask 90 sn içinde /api/health'e cevap vermedi — yukarıdaki log'a bak` hatasını atar.
  4. `/content/cloudflared` yoksa indirir ve çalıştırılabilir yapar.
  5. Tüneli açar: `--protocol http2`, `--url http://127.0.0.1:<port>`; çıktısı
     `/content/cloudflared.log`'a.
  6. Saniyede bir, en çok 30 kez log'da `https://….trycloudflare.com`'u arar. 30 sn'de bulamazsa
     log'un son 1000 karakterini basar, ve `❌ cloudflared linki 30 sn içinde alınamadı` hatasını
     atar.
- **`show_link(link, took)`:** `✓ Link <took>'de hazır`, `🔗 Queen Editor: <link>`, ve
  `⬆️  Linke gir → …` satırı.
- **`follow(log_path)`:** `📡 Sunucu çalışıyor — BU HÜCREYİ KAPATMA. Canlı log:`, sonra
  `tail -n +1 -f`. Kullanıcı hücreyi durdurunca bugünkü `Hücre durduruldu — …` satırını basar.

## Değişen

"Davranış değişmez" kuralının dışında kalan, adıyla bilinen farklar şunlar:

1. **apt-get'in, git'in ve pip'in hatası artık hücreyi durdurur.** Bugün `!apt-get`, `!git clone`,
   `!git pull` ve `!pip` hata verince kimse fark etmiyor: hücre bir sonraki satırla sürüyor, ve hata
   ancak sonra, başka bir yerde çıkıyor. Artık `console.run` ve `apt_install` hücreyi komutun kendi son
   satırlarıyla durdurur. Komut başarılıysa konsol aynı kalır. Bu bir davranış değişikliği; kural
   CLAUDE.md'nin: hata, komutun kendi söylediğini basar *(ana ajan, 9 Ekim — 2(a))*.
   **İki istisna, QA'dan** *(9 Ekim)*:
   - **`git pull` durdurmaz.** Bir `WARN` basar ve sürer; yerindeki ComfyUI çalışıyor.
   - **apt'nin listesi önce yenilenir** (`apt-get update -qq`). Eski bir liste bugün sessizce
     düşerdi; artık bütün Run all'ı durdururdu.
2. **Yeni bir adım: `apt-get update -qq`.** Kurulumdan önce koşar, ve çıktısı basılmaz.
3. **Klonun ve pip'in ilerleme çıktısı büyük olasılıkla kısalır.** Komutlar artık Colab'ın
   terminaline değil, `console.run`'ın borusuna yazıyor. git de pip de boruya yazarken ilerleme
   çubuğunu çoğunlukla basmaz. Klonun satırı da artık şöyle okunur:
   `Cloning into '/content/ComfyUI'...`. Bugün `'ComfyUI'` yazıyor, çünkü klon göreli bir yolla
   yapılıyor.
4. **hf_xet'in pip satırı ve süresi** artık modeller hücresinin `⏱️` satırına girer, ComfyUI
   hücresininkine değil.
5. **cloudflared'in indirilmesi** `subprocess.run(…, check=True)` yerine `console.run`'dan geçer.
   Böylece hata `CalledProcessError` olarak değil, wget'in kendi satırlarıyla gelir. `chmod +x`
   `os.chmod`'a döner.
6. **Çekirdeğin çalışma klasörü `/content/ComfyUI`'ye taşınmaz.** Bugün ComfyUI hücresi `%cd` ile
   çekirdeği oraya götürüyor. Sonraki hiçbir adım göreli bir yol okumuyor: `start_comfy` `cwd=root`
   ile, Flask `cwd=APP_DIR` ile başlıyor, ağırlıklar `APP_DIR`'e geçip geri dönüyor, ve indirmelerin
   yolları mutlak.
7. **İşaretlenmemiş bir grubun klasörü artık boş açılmaz.** Bugün on klasörün hepsi her koşuda
   açılıyor. Artık her dosyanın klasörü, o dosya inmeden önce açılır. Panel klasörün olmamasını
   "kurulmamış" sayıyor (`ComfyModelFiles.has_any`; docstring'i buna göre düzeltildi). Özet de yalnız
   işaretlenen grupların klasörlerini gösteriyor. Boş bir klasörü bu yüzden kimse okumuyor *(ana
   ajan, 9 Ekim — 5(a))*.
8. **Ortak yardımcıların satırı** yeni modülleri de sayar.
9. **`CIVITAI_COOKIE` artık kırpılır**, öteki secret'lar gibi. Kırpma yalnız yapıştırmanın getirdiği
   boşluğu ve satır sonunu alır.
10. **Ağırlıklar hücresinin "uygulama klasörü yok" hatası** `AssertionError` değil, `RuntimeError`
    olur. Metni aynı kalır; `colab/`'un bütün hataları gibi.
11. **`(cloudflared log yok)` dalı kalktı.** Tünelin log'unu `serve` kendisi açıyor, cloudflared
    başlamadan önce. Bu yüzden log her zaman var, ve o dala hiç girilemiyordu.
12. **İki log dosyası ikili açılır (`"wb"`)**, `start_comfy`'deki gibi. İçine yalnız başlatılan
    süreç yazıyor, devraldığı tanımlayıcıdan. Okunurken UTF-8 okunur, ve okunamayan bayt işaretle
    yer değiştirir.

## Sınırlar

- **`GITHUB_TOKEN` CONFIG'de, bugünkü gibi okunur.** Klondan önce `colab/` yok.
- **Hiçbir şey Colab'da koşturulmadı.** Testler makineyi sahteler: `apt-get`, git, pip, `pkill`,
  `Popen`, `urlopen`, `tail`, saat. Hücrelerin gerçek Colab'da bugünkü işi yaptığı, kullanıcının
  denemesinde görülür.
- **İndirme listelerinin yeri değişmez.** Ne indirilir sorusunun cevabı notebook'ta kalır
  (FOUNDATION 9).
- **`fetch`'in `parallel=True` yolu (aria2c)** madde 430'dan beri hiçbir listede kullanılmıyor. Ama
  aria2'nin kurulumu bu maddede kalır: davranış değişmez. Bu iş ayrı bir madde olur.

## Değişen dosyalar

| Dosya | Değişiklik |
|---|---|
| `colab/vault.py` | Yeni: `read_secret` |
| `colab/system.py` | Yeni: `apt_install` |
| `colab/comfy.py` | `install_comfy`. Docstring'i kurulumu da söyler |
| `colab/nodes.py` | `install_nodes` |
| `colab/console.py` | `TAIL = 5`: düşen komutun hatasına giren satır sayısı, `run` ile `apt_install`'un ortak sayısı |
| `colab/downloads.py` | `use_hf_token` `read_secret`'i çağırır. `hf_fetch` ve `fetch` klasörü kendileri açar. Yeni: `install_hf_xet`, `check_disk`, `download_models`, `show_folders` |
| `backend/features/producers/data/comfy_models.py` | `has_any`'nin docstring'i: klasörü notebook ancak ilk dosyası inerken açar |
| `colab/sound.py` | Yeni: `install_mmaudio`, `fetch_mmaudio_weights` |
| `colab/server.py` | Yeni: `serve`, `show_link`, `follow` |
| `queeneditor.ipynb` | Hücreler yukarıdaki gibi |
| `CODE-STANDARD.md` | *Notebook code* modülleri ve hücrede kalanları sayar. *Independence* tablosunun kurulum satırı ve *Tests* bölümünün sahteleri güncellenir |

## Testler

Hiçbir test ağa çıkmaz, bir komut koşmaz ya da gerçek bir saniye beklemez. `run`, `subprocess`,
`urlopen`, `time.sleep` ve `shutil.disk_usage` sahte. Dosyalar gerçek, `tmp_path`'te.

- **`test_colab_vault.py` (yeni):**
  - Okunan değer kırpılır, `problem` `None`; sorulan ad doğru.
  - Okuma hata atarsa değer `""`, ve `problem` okumanın kendi hatasını `Tür: mesaj` olarak söyler.
  - `""`, boşluk ve `None` için değer `""`, `problem` `<ad> boş`.
  - Hiçbir şey basılmaz; değer de basılmaz.
- **`test_colab_system.py` (yeni):**
  - `apt_install` önce `apt-get update -qq`, sonra `apt-get install -y aria2 ffmpeg` koşar. İki akış
    birleşir, ve çıktı basılmaz.
  - Düşen adım, ister update ister install olsun, komutun kendi son satırlarıyla düşer, ve ondan
    sonra apt çağrılmaz.
- **`test_colab_comfy.py`:**
  - Klasör yokken `install_comfy` önce klonlar, sonra bugünkü üç adımı `cwd=root` ile koşar.
  - Klasör varken klonlamaz.
  - Düşen pull git'in satırlarını bir uyarıyla basar, ve kurulum sürer.
  - Düşen klon hücreyi durdurur, ve ondan sonra komut koşmaz.
- **`test_colab_nodes.py`:** `install_nodes` her node'u sırayla `install_node`'dan geçirir, ve
  sonunda `9 custom node hazır` satırını basar.
- **`test_colab_downloads.py`:**
  - `install_hf_xet` `pip install -q -U hf_xet` koşar.
  - `check_disk` seçimi ve boş yeri söyler. Yer yetince düşmez; yetmeyince bugünkü hatayla düşer.
    Pay hesaba girer: tam sınırda düşmez, bir bayt eksikte düşer.
  - `download_models` önce HF'yi, sonra Civitai'yi indirir. Çerez ve aynayı `civitai_fetch`'e geçer,
    ve satırları sırayla döndürür.
  - `hf_fetch` ve `fetch` olmayan klasörü kendileri açar.
  - `show_folders` yalnız açık klasörleri, bugünkü biçimle ve alt klasörleriyle basar.
  - `use_hf_token`'ın üç testi değişmeden yeşil kalır.
- **`test_colab_sound.py` (yeni):**
  - `install_mmaudio`: klasör yokken önce klonlar, sonra kurar. Her aşamanın satırı aşama başlamadan
    basılır (madde 398). pip `-q`'suz ve 1800 sn. Klasör varken klonlamaz.
  - `fetch_mmaudio_weights`: sahte bir `mmaudio.eval_utils` `sys.modules`'ta. Ağırlıklar `app_dir`'de
    indirilir. Çalışma klasörü sonra geri döner, hata olsa da. Klasör `sys.path`'e bir kez eklenir.
    Uygulama klasörü yoksa bugünkü cümleyle düşer.
- **`test_colab_server.py` (yeni):**
  - `serve` eski Flask'ı ve tüneli durdurur, sonra Flask'ı `settings` ortamıyla başlatır.
  - Cevap gelince `✓ Flask ayakta (Ns)` basar. Tünel `--protocol http2` ile açılır (UDP kısılıyor,
    24 Ağustos ölçümü), ve log'daki bağlantı döner.
  - cloudflared yoksa indirilir; varsa indirilmez.
  - 90 sn cevap vermeyen Flask log'unun son 30 satırını basar ve düşer. 30 sn'de bağlantı vermeyen
    tünel log'unun sonunu basar ve düşer.
  - `show_link` süreyi bağlantının üstünde söyler.
  - `follow` `tail -n +1 -f` koşar; durdurulunca bugünkü satırı basar.
- **Notebook'u okuyan testler** (`test_notebook_*.py`), dikiş testlerine döner. Her hücre doğru
  fonksiyonu doğru değerlerle çağırıyor mu, ve onu klondan import ediyor mu; madde 314 ve 433'ün
  testleri gibi. Taşınan koda bakan metin testleri, kodla birlikte `test_colab_*.py`'ye gider ve orada
  koşar. Örnekler: MMAudio'nun pip'i, `os.chdir(APP_DIR)`, `sys.path.insert`, `--protocol http2`,
  `shutil.disk_usage`, `hf_xet`. Listelere, kutulara ve `QE_*` ayarlarına bakan testler aynı kalır.
- Bugünkü testlerin geri kalanı yeşil kalır.

## Bitti sayılır

- Notebook'un hücreleri, listeler ve form dışında, birkaç satırlık çağrılar. Taşınan kod `colab/`'da
  ve testli.
- Yeni testler kod taşınmadan kırmızı, taşınınca yeşil.
- Dört satır yeşil.
- Colab'da, kullanıcının denemesinde görülecek: notebook bugünkü işi aynı sırayla ve aynı satırlarla
  yapıyor.
