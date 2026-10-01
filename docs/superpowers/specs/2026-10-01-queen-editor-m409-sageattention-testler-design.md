# Madde 409 — Fotoğraf üretimi SageAttention ile, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, ölçümden sonra en sonda · **Parça:** 409 · v8-4 · **Tur:** 1/2 — yalnız
testler. **Commit'lenmez:** değişiklik üretilen resmi değiştirebildiği için sahibi onu VS Code'un
Changes'inde okur, ve onun onayıyla commit'lenir *(kullanıcı, 1 Ekim — "bu hızlandırma taskında yaptığın
değişikliği görmek istiyorum onu commitleme olur mu")*.

**Kullanıcıdan gereken — yok.** Madde 1 Ekim'de yeniden hizalandı: **CONFIG'de bir kutu, varsayılanı
işaretli** *(kullanıcı — "deneyelim abi a100 check box olsun dediğin gibi defaultu açık olsun test
edelim iyi çalışmıyorsa silicem")*. İşaretliyken SageAttention yalnız onu destekleyen kartta kurulur
ve ComfyUI onunla başlar; T4'te kutu işaretli de olsa ComfyUI bugünkü gibi başlar; kutu kapalıyken
her kartta bugünkü gibi. Yalnız notebook değişir — workflow'lar ve ComfyUI'nin kodu değişmez. Ölçüm
sahibinin, Colab'da, koşudan sonra.

## Bugün ne oluyor

ComfyUI'yi başlatan hücre *(`2bc455dd`, `# === Start ComfyUI ===`)* yalnız `--listen` ve `--port`
veriyor. CONFIG *(`8215086b`)* kartın adını ve belleğini `nvidia-smi`'den okuyup basıyor; hangi kart
olduğuna göre hiçbir şey değişmiyor. SageAttention hiçbir yerde yok.

## Araştırmadan, üstüne kurulanlar

- **Hangi kart:** `nvidia-smi --query-gpu=name,compute_cap --format=csv,noheader` — örneğin
  `NVIDIA A100-SXM4-40GB, 8.0`. Destekleyen kart compute capability'si **8.0 ve üstü** olan: A100
  8.0, L4 8.9, H100 9.0 evet; T4 7.5 hayır
  *([NVIDIA](https://developer.nvidia.com/cuda-gpus))*. L4'ün de alması sorun değil.
- **Hangi sürüm:** PyPI'daki `sageattention==1.0.6` — 20 kB'lık, Triton çekirdekli saf Python
  wheel'i; `requires_dist` boş, torch'a dokunmaz, saniyeler içinde kurulur
  *([PyPI](https://pypi.org/pypi/sageattention/1.0.6/json))*. 2.x PyPI'da yok, her taze Colab
  makinesinde kaynaktan derlenmesi gerekir — kullanılmıyor.
- **Neden bekçi gerekiyor:** `--use-sage-attention` verilip paket yoksa ComfyUI açılırken kapanıyor —
  `comfy/ldm/modules/attention.py` `sageattn`'ı yüklenirken içe aktarıyor, `ImportError`'da hata
  satırını yazıp `exit(-1)` diyor
  *([kaynak](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/comfy/ldm/modules/attention.py))*.
  Bu yüzden bayrak **yalnız kurulum başarılıysa** verilir. `sageattn` çalışırken hata verirse ComfyUI
  hatayı log'a yazıp o çağrı için PyTorch'un attention'ına döner — çökmez.
- **Neyi etkiler:** fotoğraf (SDXL'in attention'ı) ve WAN değişir — aynı seed birebir aynı resmi
  vermez, çok yakın çıkar. H3 değişmez: grafiği backend'ini `ModelAttentionBackend` ile kendisi
  seçiyor. MMAudio ComfyUI'nin dışında.

## Karar — karar kodu nerede durur

**`colab/` altında küçük bir modülde: `colab/attention.py`, tek fonksiyon
`sage_attention_flags(wanted)`.** CODE-STANDARD'ın *Notebook code* bölümü: hücre pytest'te koşmuyor,
ve defterin boyut tavanı var. Kartı okuyan, kurulumu deneyen ve bayrağı veren karar maddenin özü —
T4'ün çökmemesi buna bağlı —, o yüzden okunarak değil **koşularak** test edilir. Defterde kalan:
kutu CONFIG'de; ComfyUI hücresinde fonksiyonun çağrısı; başlatma hücresinde dönen bayrakların komuta
eklenmesi.

- **Fonksiyon ComfyUI'nin başlatma komutuna eklenecek bayrakları döner:** `["--use-sage-attention"]`
  ya da `[]`. Bayrağın adı yalnız modülde yazılı; defter onu kendisi yazmaz, yalnız dönen listeyi
  ekler — bayrak pip "tamam" demeden komuta giremez.
- **Kart `nvidia-smi`'ye sorulur**, torch'a değil: torch'u notebook'un çekirdeğinde içe aktarmak,
  ComfyUI çalışırken kartta bir CUDA bağlamını boşuna tutardı.
- **Kurulum `colab.console.run` ile:** pip'in çıktısı hücreye akar, ve başarısızlıkta hata pip'in
  kendi son satırlarını taşır *(NOTEBOOK-STANDARD §2)*.

Elenenler: **hücrede satır içi karar** — koşmayan, yalnız metni okunan bir karar; **karta adıyla
bakmak** (`"T4" in name`) — adı bilinmeyen her kartta yanlış.

## Kurallar

1. **Destekleyen kartta, kutu işaretliyken** PyPI'daki `sageattention==1.0.6` pip ile kurulur, ve
   fonksiyon `["--use-sage-attention"]` döner.
2. **Desteklemeyen kartta** (T4, 7.5) hiçbir şey kurulmaz, fonksiyon `[]` döner — ComfyUI bugünkü
   gibi başlar. Konsol kartın adını ve compute capability'sini söyler: sahibi neden atlandığını görür.
3. **Kutu kapalıyken** karta da pip'e de bir şey sorulmaz, fonksiyon `[]` döner; konsol
   SageAttention'ın kapalı olduğunu söyler.
4. **Kurulum başarısızsa** hata hücreyi durdurmaz: fonksiyon `[]` döner, ve konsol pip'in kendi
   sözlerini basar — sebep uydurulmaz.
5. **CONFIG'de `SAGE_ATTENTION` kutusu, varsayılanı işaretli**, kendi bölümünde: video modellerinin
   altında, kendi ayracı ve `### SageAttention` başlığıyla. Başlığın altındaki Türkçe metin sahibine
   ne değiştiğini söyler — T4'ün bugünkü gibi kaldığını, fotoğrafla birlikte WAN'ın da değiştiğini.
6. **ComfyUI hücresi bayrakları fonksiyondan alır** — `SAGE_FLAGS = sage_attention_flags(SAGE_ATTENTION)`,
   fonksiyon klondan içe aktarılır —, **başlatma hücresi onları komutun sonuna ekler**.
7. **Defter `--use-sage-attention`'ı hiçbir yerde kendisi yazmaz** *(bekçi)*.

**Değişmeyen:** workflow'lar (`assets/workflow_*.json`), ComfyUI'nin kodu, `backend/` ve `frontend/`.
`colab/console.py`'nin `run`'ı olduğu gibi kalır.

## Nasıl kanıtlanıyor

Modülün testleri fonksiyonu koşar; **ağ ve kart sahte, gerisi gerçek** *(CODE-STANDARD, Tests)*:
`nvidia-smi` `subprocess.run`'ın yerine konan bir sahteyle cevaplanır — `name,compute_cap` sorusuna
nvidia-smi'nin verdiği satır, `Tesla T4, 7.5` gibi —, ve pip, `test_colab_nodes.py`'deki gibi modülün
`run`'ı sahtelenerek: komut hatırlanır, istenirse pip'in sözleriyle `RuntimeError` atılır. Defterin
tarafı, öteki defter testleri gibi okunarak.

## Yazılacak testler

### `backend/tests/test_colab_attention.py` — yeni; koşularak

Modül bir fixture'da içe aktarılır *(`importlib.import_module("colab.attention")`)*: henüz olmayan
modül her testi kendi başına düşürür, dosyanın toplanmasını değil; ve `test_requirements.py`
`backend/` altındaki her üst düzey import'u pip'in kuracağı bir paket sayıyor.

1. **Destekleyen kart PyPI'daki sürümü kurar ve bayrağı alır** — A100 `8.0`, L4 `8.9`, H100 `9.0`
   ile parametreli; kutu işaretli. Dönen `["--use-sage-attention"]`; tek komut koşuldu, `pip install`
   ile başlıyor ve `sageattention==1.0.6`'yı içeriyor.
2. **T4 hiçbir şey kurmaz ve bugünkü gibi başlar** — `Tesla T4, 7.5`. Dönen `[]`; komut yok.
3. **Konsol T4'ün neden atlandığını söyler** — çıktıda `Tesla T4` ve `7.5`.
4. **Kapalı kutu hiçbir şey sormaz** — kutu kapalı, kart A100. Dönen `[]`; `nvidia-smi` sorulmadı,
   komut yok; çıktıda `SageAttention`.
5. **Başarısız kurulum ComfyUI'yi onsuz başlatır** — A100, pip
   `RuntimeError("pip install sageattention: exit 1\nERROR: No matching distribution found for sageattention==1.0.6")`
   atıyor. Fonksiyon hata atmadan `[]` döner.
6. **Başarısız kurulum pip'in kendi sözlerini söyler** — aynı durumda çıktıda
   `No matching distribution found for sageattention==1.0.6`.

### `backend/tests/test_notebook_installs_the_producer_groups.py` — defter, okunarak

7. **CONFIG'de kutu var, varsayılanı işaretli** —
   `SAGE_ATTENTION = True  #@param {type:"boolean"}` CONFIG hücresinde.
8. **Kutunun kendi bölümü var, video modellerinin altında** — `VIDEO_H3 = ` < `#@markdown ---` <
   `#@markdown ### SageAttention` < `SAGE_ATTENTION = `.
9. **Bölüm sahibine ne değiştiğini söyler** — formun çizdiği satırlar *(`_drawn`)* başlıktan kutuya
   kadar `T4`'ü ve `WAN`'ı anıyor. Sözcükler serbest kalır; iki olgu kalamaz: T4'te ne olduğu ve
   fotoğrafın yanında neyin değiştiği.
10. **ComfyUI, kurulumun verdiği bayraklarla başlar** — `# === System deps + ComfyUI ===` hücresinde
    `SAGE_FLAGS = sage_attention_flags(SAGE_ATTENTION)`; başlatma hücresinde
    `["python", "main.py", "--listen", "127.0.0.1", "--port", str(COMFY_PORT)] + SAGE_FLAGS`; ve
    defter `sage_attention_flags`'i `colab.attention`'dan içe aktarıyor.
11. **Defter bayrağı kendisi yazmaz** *(bekçi)* — `--use-sage-attention` defterin kaynağında yok.

### Değişen

- **`test_the_form_leaves_the_model_section_at_its_heading`** — formun model bölümleri bugün CONFIG'in
  sonuna kadar uzanıyor, ve test ilk ayraçtan sona kadar her `#@markdown` satırını sayıyor. SageAttention
  bölümü video modellerinin altına geldiğinde metni de o sayıma girerdi. Test, model bölümlerini
  `### SageAttention` başlığının ayracında bitirir — başlık yoksa sona kadar. Sorduğu aynı: model
  bölümleri başlıklarından ibaret. Bugün de yeşil.

**Bekçiler, bugün de yeşil:** `test_every_name_the_notebook_imports_from_its_code_exists` *(uygulama
turunda yeni import satırını da okur)*, `test_the_notebook_defines_none_of_the_code_it_imports`,
`test_the_form_gives_video_models_a_section_of_their_own`, `test_notebook_stays_readable.py` —
defter tavanın altında kalmalı *(29.000 karakter, madde 239)*; ve `test_requirements.py`.

## Kırmızı beklenen

- 1 – 6 kırmızı: `colab.attention` yok, fixture her testi kendi başına düşürür.
- 7, 8, 9 ve 10 kırmızı: CONFIG'de kutu, bölüm ve çağrı yok.
- 11 ve değişen test yeşil — bekçiler.
- `queen-editor` pytest'inde öteki her şey yeşil; öteki üç satır yeşil.

## Bilinçli olarak yapılmayan

- Kurulumdan sonra `import sageattention`'ın ayrıca denenmesi yok: pip'in "tamam"ı paketin yerinde
  olduğunu söylüyor, ve içe aktarma yine de bozulursa ComfyUI'nin kendi log'u — başlatma hücresi
  90 saniyede onun son satırlarını basıyor — nedenini söyler. Bir yoklama yalnız hatanın yerini
  değiştirirdi: A100'de SageAttention'sız başlamak da *Bitti sayılır*'ı tutmuyor.
- `nvidia-smi`'nin cevap vermediği durum için ayrı bir dal yok: CONFIG kartı zaten soruyor ve kart
  yoksa durduruyor.
- Ekran, backend ve dist değişmez. Yol haritasına dokunulmaz. Hiçbir şey commit'lenmez.
