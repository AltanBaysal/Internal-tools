# Madde 439 · Konsol ilerlemeyi gösterir, ve her hata ham hâliyle, bütün basılır — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
439 · **Dal:** `feat/queen-editor-v9` · **Kurallar:** [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Ne, neden

Kullanıcı, 9 Ekim: *"güzel bir console feedbaci veriliyormu ilerlemeyi görebiliyormuyum ve devamında
hatalarıda direkt hata mesaj olarak bsasıyor okuabilri bir şeye cevirmeden bir developer olarak buna
ihtiacım var hata mesajların ıcopy paste yapamya"*. Notebook'un konsolu iki şey yapmalı:

- **ilerlemeyi göstermek** — hücre ne yapıyor, nerede;
- **hatayı ham ve bütün basmak** — komutun ya da servisin kendi metni, kopyalanabilir hâliyle. Hiçbir
  hata bizim cümlemize çevrilmez.

438'den sonra `queen-editor/colab/`'da bu ikisini tutmayan üç yer kaldı (1–3). İncelemede, maddenin
başlığı "her hata ham hâliyle, bütün" olduğu için, bir hatayı kesen ya da saklayan dört yer daha
çıktı (4). Bu madde hepsini kapatır.

## 1 · `system.apt_install` — düşerse apt'nin bütün çıktısı

**Bugün:** apt-get'in çıktısı konsola gelmez; düşünce hata yalnız son 5 satırı (`console.TAIL`) taşır.
`console.run`'da son satırlar yeter, çünkü öncekiler konsolda zaten var. apt'de yoklar: kesilen satırlar
hiçbir yerde görünmez.

**Olacak:** Başarıda apt yine sessiz — iyi bir günde yüzlerce satır, kimse okumuyor. Düşünce hata
`<komut>: exit <kod>` satırını ve altında apt'nin **bütün** çıktısını taşır, olduğu gibi.

Çıktı ayrıca `print` edilmez, hatanın içinde gelir: hücreyi durduran hata tek parça, kopyalanınca
komutu da, çıkış kodunu da, apt'nin dediğini de birlikte taşır. `system.py` artık `TAIL`'i kullanmaz.

## 2 · git clone ve pip — ilerlemeyi gösterirler

**Bugün:** `comfy.install_comfy`, `nodes.install_node`, `sound.install_mmaudio` ve
`downloads.install_hf_xet` git'i ve pip'i `console.run` ile çalıştırır. `console.run` çıktıyı bir
borudan okur. git de pip de karşısında terminal görmeyince ilerleme çizmez. Ayrıca pip'in dört
çağrısında `-q` var: o, pip'in `Collecting …` / `Downloading …` satırlarını da kapatır. Yani bu dört
pip kurulumu bugün bitene kadar konsola hiçbir şey basmıyor.

**Olacak:**

- **Her `git clone`'a `--progress`.** ComfyUI'nin, MMAudio'nun ve her custom node'un klonu.
  `git clone -h`: `--[no-]progress  force progress reporting`. git'in kendi belgesi bunu "standart hata
  bir terminale bağlı olmasa da ilerlemeyi raporla" diye açıklıyor. Bu, borunun ta kendisi. git
  ilerlemeyi satırbaşıyla (`\r`) yeniden çizer, ve `console.run` satırbaşını olduğu gibi bırakır
  (madde 398'in testi). Colab'da ilerleme yerinde güncellenen tek bir satır olarak görünür.
- **Her `pip install`'a `--progress-bar on`.** pip'in yardımı (`pip install --help`):
  `--progress-bar <progress_bar>  Specify whether the progress bar should be used. In 'auto' mode,
  --quiet will suppress all progress bars. [auto, on, off, raw]`. `on`, seçeneklerin içinde.
- **pip'ten `-q` çıkar.** Seçim bu, çünkü:
  - `-q` pip'in yardımına göre günlük seviyesini WARNING'e çeker (`Give less output … corresponding to
    WARNING, ERROR, and CRITICAL logging levels`). `Collecting x`, `Downloading x (12.3 MB)` ve
    `Installing collected packages` INFO satırları. Çubuk hiç çizilmese bile pip'in hangi pakette
    olduğunu bunlar söyler.
  - Bedeli: başarıda daha çok satır (`Requirement already satisfied …` gibi). Kullanıcı ilerlemeyi
    istedi; bu satırlar ilerlemenin kendisi. `sound.install_mmaudio`'nun pip'i 398'den beri böyle,
    `-q`'suz.
- `comfy`'nin `git pull -q`'su değişmez. Pull yalnız var olan bir klonda koşar ve birkaç saniye sürer;
  düşerse git'in dediği zaten basılıyor (madde 438).

Bayrakların nedeni bir kez, `console.run`'ın docstring'inde, kendi paragrafında yazılır: git ve pip
ilerlemeyi yalnız bir terminale çizer, çağrılar onu açıkça ister. Çağrı yerlerinde de testlerde de
tekrar yazılmaz; testler yalnız neyi denetlediklerini söyler.

## 3 · Bir sunucunun cevap vermesini beklemek — `colab/wait.py`

**Bugün:** `server._start_flask` `/api/health`'e 45 kez bakar, ve her bakışın hatasını
`except Exception: continue` ile yutar. Zaman aşımında Flask'ın log'unun son 30 satırını basar, sonra
kendi cümlesini atar: `❌ Flask 90 sn içinde /api/health'e cevap vermedi — yukarıdaki log'a bak`. Son
bakışın ne dediği hiçbir yerde görünmez.

`comfy.start_comfy` aynı beklemeyi kendi başına yazıyor: aynı `LOOKS`/`STEP`, aynı uyu → bak → `None`
ise ayakta adımları, ve aynı üç parçalı hata. 438'in incelemesi de iki modülün "bir log'un son N
satırını" ayrı ayrı okuduğunu not etti.

**Olacak:** bekleme tek bir işin kendi yeri olur: yeni, küçük bir modül, `colab/wait.py`.

- `wait_for(url, name, log_path, process=None)` — `url`'ye iki saniyede bir, 45 kez (90 sn) bakar, ve
  cevap gelince kaç saniye sürdüğünü döner. Cevap gelmezse hata üç parçalı ve tek parça:

  ```
  ❌ Flask 90 sn içinde cevap vermedi — http://127.0.0.1:8000/api/health
  URLError: <urlopen error [Errno 111] Connection refused>
  --- /content/queen-editor.log · son 30 satır ---
  …log'un son 30 satırı…
  ```

- `process` verilirse her bakıştan sonra ona sorulur: bir cevap ancak o yaşarken sayılır, ve süreç
  bittiyse bekleme hemen `❌ <ad> kapandı — exit <kod>` ve log'un sonuyla durur. ComfyUI sürecini
  verir (madde 433'ün kuralı); Flask vermez, davranışı aynı kalır.
- `LOOKS`, `STEP` ve bakışın kendisi (`_asked`, `comfy._asked`'dan taşındı) `wait.py`'de durur.
  `comfy.py` ile `server.py`'den çıkarlar.
- Başarı satırları çağıranın: `ComfyUI hazır (6s)` ve `✓ Flask ayakta (6s)` değişmez.

`wait.py` CODE-STANDARD'ın `colab/` listesine eklenir.

**Log'un sonu `console.py`'de, `head_text`'in yanında:** `log_tail(path)` — log'un son `LOG_LINES`
(30) satırı, üstünde `--- <yol> · son 30 satır ---`. `comfy._tail`'in kendisi. `LOG_LINES` de
`console.py`'ye taşınır; `comfy.py`'de ve `server.py`'de ayrı ayrı tanımlıydı, ve ikisi aynıydı.
`head_text` bir dosyanın başını, `log_tail` sonunu hataya koyar.

**İlk satır sorulan adresi taşır**, ikisinde de: kullanıcı bu satırları kopyalıyor, ve sorulan şey o
adres. `❌ ComfyUI 90 sn içinde cevap vermedi — http://127.0.0.1:8188/system_stats`, ve Flask'ınki
`… — http://127.0.0.1:8000/api/health`. Flask'ın "/api/health'e" ve "— yukarıdaki log'a bak"
sözleri düşer; adres artık satırın sonunda, log da ayrıca basılmaz, hatanın içinde.

## 4 · Hatayı kesen ya da saklayan dört yer daha

- **cloudflared'ın zaman aşımı (`server._open_tunnel`).** Bugün log'un son 1000 karakteri hatadan
  ayrı basılıyor, sonra yalnız bizim cümlemiz atılıyor. cloudflared bir dosyaya yazıyor, yani log
  konsolda hiçbir yerde yok. Olacak: `❌ cloudflared linki 30 sn içinde alınamadı` ve altında
  `log_tail(TUNNEL_LOG)`, tek hata; ayrı `print` düşer. Satırlar artık bütün: 1000 karakter bir
  satırın ortasından kesebiliyordu.
- **wget (`server._open_tunnel`).** `wget -q` wget'in hatasını da saklıyor. Olacak: `-nv` — ilerleme
  yok, ama dosya başına bir satır ve hata söylenir.
- **Civitai denemesi (`downloads.civitai_probe`), curl'ün hatası.** `curl -s` hata mesajını da
  susturuyor, ve hata yalnız son 5 satırı taşıyordu. Olacak: `-sS` — ilerleme yok, hata var — ve hata
  curl'ün bütün stderr'ini taşır, apt'ninki gibi: `❌ probe <ad>: curl exit <kod>\n<stderr>`.
- **Civitai'nin yanıtı (`downloads.civitai_probe`).** Yanıt 512 bayta kesiliyordu. Olacak:
  `head_text` — indirmelerin hatası gibi, ilk 4000 bayt ve kalanın boyu. Deneme dosyasının yolu bir
  modül sabiti olur (`PROBE`), testin onu kendi klasörüne taşıyabilmesi için.
- **Civitai denemesinin zaman aşımı.** curl'ün 28'i (zaman aşımı) geçerli sayılır: `--limit-rate` ve
  `--max-time` iyi bir denemeyi de kesebilir. Ama iyi bir şey gelmediyse (kod `000`, boş gövde) curl'ün
  `curl: (28) Operation timed out…`'u yutuluyordu. Olacak: reddin hatası, curl bir şey dediyse, onun
  bütün stderr'ini Civitai'nin yanıtının altında taşır.
- **Ayrıştırılamayan safetensors başlığı (`downloads.check_safetensors`).** Yalnız istisnanın türü
  yazılıyordu. Olacak: `Tür: mesaj`, ör. `header parse failed (JSONDecodeError: Expecting value: line 1
  column 1 (char 0), 22.0B)`.

## Doğrulanamayanlar

Bayraklar bu makinedeki araçların kendi yardım metniyle doğrulandı: **git 2.55.0**, **pip 26.2.1**,
**curl 8.21.0** (`-S, --show-error  Show error even when -s is used`). Colab'ın sürümleri repoda
hiçbir yerde yazılı değil, ve aşağıdakiler yardım metninden çıkmıyor:

- **wget.** Bu makinede wget yok; `-nv`'nin (`--no-verbose`) yardım metni burada okunamadı. Bayrak
  wget'in uzun zamandır bilinen bir bayrağı, ama burada doğrulanmadı.
- **pip'in sürümü.** `--progress-bar` ve `on` değeri pip'te uzun zamandır var. `auto` ve `raw` ise yeni
  değerler. Biz `on`'u kullanıyoruz, yani Colab'ın pip'i daha eskiyse de bayrak tanınır. Bu varsayım
  yardım metninden doğrulanamıyor.
- **pip'in çubuğu bir borudan çizer mi?** Bu yardım metninden okunamıyor. Çizmezse `-q`'nun çıkmasıyla
  gelen `Collecting` / `Downloading` satırları ilerlemeyi yine gösterir.
- **`--recurse-submodules` ile alt modüllerin klonu** git'in `--progress`'ini alır mı? Yardım metni
  bunu söylemiyor. Klonun kendisi ilerlemeyi gösterir; alt modüllerinki görünmeyebilir.

Hepsi Colab'da, kullanıcının denemesinde görülür (yol haritasının "nasıl görülür"ü).

## Değişen konsol

- apt düşerse: hata apt'nin bütün çıktısını taşır (önce son 5 satır).
- ComfyUI'nin, MMAudio'nun ve her node'un klonu ilerlemeyi gösterir.
- Beş pip kurulumu ilerlemeyi gösterir: ComfyUI'nin `requirements.txt`'i, ComfyUI'nin ekleri, her
  node'un `requirements.txt`'i, hf_xet ve MMAudio. Önceki dördü `-q` ile sessizdi.
- ComfyUI cevap vermezse: ilk satırın sonunda sorulan adres.
- Flask cevap vermezse: `❌ Flask 90 sn içinde cevap vermedi — http://127.0.0.1:8000/api/health`, son
  bakışın `Tür: mesaj`'ı ve Flask'ın log'unun son 30 satırı, dosyanın adıyla, tek hatada. Log ayrıca
  basılmaz.
- cloudflared link vermezse: hata log'unun son 30 satırını taşır; ayrıca basılmaz.
- wget cloudflared'ı indirirken bir satır basar, düşerse hatasını.
- Civitai denemesi düşerse: curl'ün bütün hatası; Civitai reddederse: yanıtının ilk 4000 baytı, ve
  curl bir şey dediyse (zaman aşımı) onun bütün stderr'i.
- Başlığı ayrıştırılamayan bir safetensors: ayrıştırıcının `Tür: mesaj`'ı.

Başka hiçbir başarı satırı, hiçbir Türkçe cümle değişmez.

## Sınırlar

- Davranışın geri kalanı değişmez: aynı komutlar, aynı sıra, aynı süre sınırları.
- Notebook değişmez: hücreler aynı fonksiyonları aynı adlarla çağırıyor.
- `console.run`'ın kodu değişmez; yalnız docstring'ine bayrakların nedeni eklenir. Düşen komutun hatası
  yine son `TAIL` satırını taşır, çünkü öncekiler konsolda zaten var.
- Uygulama (`backend/`) ve frontend değişmez. Frontend derlenmez.

## Değişen dosyalar

- `queen-editor/colab/wait.py` — yeni: `wait_for`, `LOOKS`, `STEP`, `_asked`.
- `queen-editor/colab/console.py` — `log_tail`, `LOG_LINES`; `run`'ın docstring'i.
- `queen-editor/colab/system.py` — düşerse bütün çıktı; `TAIL` çıkar.
- `queen-editor/colab/comfy.py` — bayraklar; bekleme `wait_for`'a; `LOOKS`, `STEP`, `_asked`, `_tail`,
  `LOG_LINES` çıkar.
- `queen-editor/colab/server.py` — Flask'ın beklemesi `wait_for`'a; cloudflared'ın hatası `log_tail`'le;
  `wget -nv`; `LOOKS`, `STEP`, `LOG_LINES` çıkar.
- `queen-editor/colab/downloads.py` — hf_xet'in bayrakları; `civitai_probe`: `-sS`, bütün stderr,
  `head_text`, `PROBE`, zaman aşımında curl'ün stderr'i; `check_safetensors`: `Tür: mesaj`.
- `queen-editor/colab/nodes.py`, `sound.py` — bayraklar.
- `queen-editor/CODE-STANDARD.md` — `colab/` listesine `wait.py`.
- Testler: `backend/tests/test_colab_wait.py` (yeni), `test_colab_console.py`, `test_colab_system.py`,
  `test_colab_comfy.py`, `test_colab_nodes.py`, `test_colab_sound.py`, `test_colab_downloads.py`,
  `test_colab_server.py`.

## Testler

- **wait:** cevap gelince süre döner; hiç gelmezse 45 bakıştan sonra üç parçalı hata; süreç bittiyse
  cevap sayılmaz; başlarken biten süreç beklemeyi hemen durdurur.
- **console:** `log_tail` 40 satırlık bir log'un yalnız son 30'unu, dosyanın adının altında döner.
- **system:** düşen adımın hatası tam olarak komut, çıkış kodu ve apt'nin bütün çıktısı; başarıda konsol
  boş kalır.
- **comfy, nodes, sound, downloads:** her `git clone` `--progress`'le, her `pip install`
  `--progress-bar on`'la ve `-q`'suz çağrılır.
- **server:** cevap vermeyen Flask'ın hatası son bakışın `URLError: …`'ını ve log'un son 30 satırını
  taşır, tünel açılmaz; link vermeyen tünelin hatası log'unun son 30 satırını bütün taşır; cloudflared
  `wget -nv` ile iner.
- **downloads, deneme:** curl düşerse hata `-sS`'in getirdiği bütün stderr; Civitai reddederse 512
  bayttan uzun yanıtı bütün; bayt gelirse, 0'la da 28'le de, "erişim OK"; 28'le `000` gelirse hata
  curl'ün stderr'ini bütün taşır.
- **downloads, başlık:** ayrıştırılamayan başlık `JSONDecodeError: …` mesajıyla söylenir.
- ComfyUI'nin bugünkü başlatma testleri yeşil kalır.

## Bitti sayılır

- Yukarıdaki testler yeşil, dört suite yeşil.
- Colab'da, kullanıcının denemesinde: ComfyUI'nin klonu ve pip kurulumları ilerlemeyi gösteriyor; apt
  düşerse bütün çıktısı, Flask cevap vermezse son bakışın hatası konsolda.
