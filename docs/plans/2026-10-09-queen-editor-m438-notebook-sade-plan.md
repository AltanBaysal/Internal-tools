# Madde 438 — Notebook sadeleşir, plan

> **Koşum:** bu oturumda, ana klasörde, adım adım. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** Notebook'un hücrelerindeki kod `colab/`'daki testli fonksiyonlara taşınır, ve hücreler
onları çağıran birkaç satır olur. Listeler, form alanları ve klondan önce koşması gerekenler notebook'ta
kalır. Davranış ve konsol satırları aynı kalır; farklar spec'in *Değişen* başlığında.

**Yaklaşım:** Her modül için önce testler yazılır ve kırmızı görülür, sonra kod. Notebook en son
değişir, ve onu okuyan testler dikiş testlerine döner.

**Spec:** [m438](../specs/2026-10-09-queen-editor-m438-notebook-sade-design.md)

## Her yere geçerli kurallar

- Yorumlar, docstring'ler ve test adları **İngilizce**. Konsola ve `assert`'e giden metin **Türkçe**,
  ve taşınan her satır harfi harfine aynı.
- `colab/` uygulamadan hiçbir şey import etmez. Testler modülü fixture'da `importlib` ile alır.
- Notebook'un import satırları tek satır kalır: `test_every_name_the_notebook_imports_from_its_code_exists`
  onları satır satır okuyor.
- Yol haritasına dokunulmaz.

---

## Görev 1: `colab/vault.py` — `read_secret`

- [ ] `backend/tests/test_colab_vault.py`:
  - değer kırpılır ve `problem` `None` olur;
  - okuma hata atarsa `problem` `Tür: mesaj` söyler;
  - `""`, boşluk ya da `None` gelirse `problem` `<ad> boş` olur;
  - hiçbir şey basılmaz.
  Testler kırmızı.
- [ ] `colab/vault.py`. Testler yeşil.
- [ ] `colab/downloads.py`: `use_hf_token` `read_secret`'i çağırır. `use_hf_token`'ın üç testi yeşil
  kalır.

## Görev 2: `colab/system.py` — `apt_install`

- [ ] `backend/tests/test_colab_system.py`:
  - komut `apt-get install -y …`, ve çıktı basılmaz;
  - başarısız komut kendi son satırlarıyla düşer.
- [ ] `colab/system.py`. Komut `subprocess.run(capture_output=True)` ile koşar.

## Görev 3: `colab/comfy.py` — `install_comfy`; `colab/nodes.py` — `install_nodes`

- [ ] `test_colab_comfy.py`:
  - klasör yokken önce klonlanır, sonra `pull`, `requirements` ve ek paketler kurulur, hepsi
    `cwd=root` ile;
  - klasör varken klonlanmaz.
- [ ] `test_colab_nodes.py`: node'lar sırayla kurulur, sonra `N custom node hazır` basılır.
- [ ] İki fonksiyon. `comfy.py`'nin docstring'i kurulumu da söyler.

## Görev 4: `colab/downloads.py` — `install_hf_xet`, `check_disk`, `download_models`, `show_folders`

- [ ] `test_colab_downloads.py`'ye:
  - **`install_hf_xet`:** komut `pip install -q -U hf_xet`.
  - **`check_disk`:**
    - seçim satırını basar;
    - yer yetince geçer;
    - tam sınırda geçer;
    - sınırın altında bugünkü hatayla düşer.
  - **`download_models`:** önce HF, sonra Civitai. Ayna ve çerez geçer, satırlar sırayla döner, ve
    klasör açılır.
  - **`show_folders`:** yalnız açık klasörler, alt klasörleriyle.
- [ ] Kod.

## Görev 5: `colab/sound.py` — `install_mmaudio`, `fetch_mmaudio_weights`

- [ ] `backend/tests/test_colab_sound.py`:
  - **Klon:** klasör yokken önce klonlanır; varken klonlanmaz.
  - **Satırlar:** her aşamanın satırı aşamadan önce basılır.
  - **pip:** `-q`'suz ve 1800 sn.
  - **Ağırlıklar:** sahte `mmaudio.eval_utils` `app_dir`'de çağrılır.
  - **Çalışma klasörü:** sonra geri döner, hata olsa da.
  - **`sys.path`:** klasör bir kez eklenir.
  - **Uygulama klasörü:** yoksa bugünkü cümleyle düşülür.
- [ ] `colab/sound.py`.

## Görev 6: `colab/server.py` — `serve`, `show_link`, `follow`

- [ ] `backend/tests/test_colab_server.py`. Sahteler: `subprocess.run`/`Popen`, `urlopen`,
  `time.sleep`, `run`; tünelin log'unu sahte `Popen` yazar.
  - **Sıra:** eski süreçler durdurulur, sonra Flask `settings` ortamıyla başlar.
  - **Hazır:** `✓ Flask ayakta (Ns)` basılır, tünel `--protocol http2` ile açılır, ve bağlantı döner.
  - **cloudflared:** yoksa indirilir; varsa indirilmez.
  - **Flask cevap vermezse:** 90 sn sonra log'un son 30 satırı basılır ve düşülür.
  - **Tünel bağlantı vermezse:** 30 sn sonra düşülür, log'un son 1000 karakteriyle.
  - **`show_link`:** süreyi bağlantının üstünde söyler.
  - **`follow`:** önce `📡` satırını basar, sonra `tail -n +1 -f` koşar; durdurulunca bugünkü satırı
    basar.
- [ ] `colab/server.py`.

## Görev 7: Notebook ve onu okuyan testler

- [ ] Önce `test_notebook_installs_the_producer_groups.py` ve `test_notebook_times_its_cells.py`
  dikişe döner. Kırmızı olurlar.
  - **Hücreler:** her hücre doğru çağrıyı yapar, ve her ad klondan import edilir.
  - **Taşınan koda bakan metin testleri:** `test_colab_*`'teki karşılıklarıyla değişir, ya da kalkar.
    Bunlar MMAudio'nun pip'i, `chdir`, `sys.path`, `http2`, `disk_usage`, `hf_xet`, `landed`
    döngüleri ve `install_node` döngüsü.
- [ ] `queeneditor.ipynb`, hücre hücre, spec'teki gibi. `NotebookEdit` ile.
  - **CONFIG:** `=== Secrets ===` çıkar.
  - **Yardımcılar:** import'lar ve üç secret.
  - **ComfyUI:** `apt_install`, `install_comfy`, liste ve `install_nodes`.
  - **Modeller:** `install_hf_xet`, `FOLDERS` tablosu ve beş çağrı.
  - **Ses:** iki `if/else`.
  - **Flask:** `serve`, `show_link` ve `follow`.
- [ ] Testler yeşil.

## Görev 8: `CODE-STANDARD.md`

- [ ] *Notebook code* bölümü:
  - modülleri sayar;
  - hücrede kalanları sayar: sayaç, CONFIG, Drive, klon ve yardımcılar, yani klondan önce koşanlar ve
    import'u kuran hücre.
- [ ] *Independence* tablosunun kurulum satırı ComfyUI'nin kurulumunu ve başlatılmasını da sayar.
- [ ] *Tests* bölümü, `colab/` testlerinde neyin sahte olduğunu sayar.

## Görev 9: Koş

- [ ] Dört satır, birer birer, depo kökünden:

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
```

## Görev 10: Reviewer'ın ve QA'nın bulguları *(9 Ekim)*

- [ ] **`system.py`:**
  - `apt_install` önce `apt-get update -qq` koşar;
  - iki akış `stdout=PIPE, stderr=STDOUT` ile birleşir;
  - kuyruğun uzunluğu `console.TAIL`'den gelir.
  - Testler: iki adım, ve ikisinden biri düşünce ne olduğu.
- [ ] **`comfy.py`:**
  - düşen `git pull` bir `WARN` basar ve sürer; düşen klon durdurur. İkisinin de testi var.
  - `EXTRAS = [` boşluğu.
- [ ] **Klasörler:** klasörü `hf_fetch` ve `fetch` açar; `download_models` yalnız iki döngü. İki
  indiricinin testi.
- [ ] **Geçmiş anlatan yorumlar:** yorumlar ve test docstring'leri bugün doğru olanı söyler.
- [ ] **`test_notebook_times_its_cells.py`:** yalnız `show_link(link, cell_elapsed())`'a bakar.
- [ ] **`comfy_models.py`:** `has_any`'nin docstring'i.
- [ ] **`CODE-STANDARD.md`:** yardımcılar hücresi klondan sonra koşar; *Independence* satırı bugünü
  söyler.
- [ ] **Spec:** *Değişen*'e update, pull, ilerleme çıktısı ve hf_xet'in süresi eklenir.

## Görev 11: Commit — ana ajanın
