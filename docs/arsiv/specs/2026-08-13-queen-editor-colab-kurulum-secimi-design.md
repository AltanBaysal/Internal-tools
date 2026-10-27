# Queen Editor — Colab defterinde üretici seçimi (tasarım)

**Tarih:** 2026-08-13 · **Araç:** queen-editor · **Dal:** feat/queen-editor-v3

## Sorun

Defter yalnız fotoğraf modellerini kuruyor. Video ve ses modelleri hiçbir yerde inmiyor: uygulama
artık indirmiyor (FOUNDATION 9), defter de bu iki grubu tanımıyor. Sonuç, arayüzde iki üreticinin
kalıcı olarak "kurulu değil" görünmesi.

İkinci sorun: fotoğraf ~8 GiB, video ~37 GiB, ses ~9 GiB (2 GiB fine-tune + MMAudio'nun kendi ~7
GiB'ı). Üçü birden her makineye sığmıyor ve her oturumda hepsini indirmek çoğu iş için gereksiz.
Kullanıcının **ne kuracağını seçmesi** gerekiyor.

## Ne yapılacak

Defterin CONFIG hücresine üç onay kutusu giriyor; işaretlenen grubun modelleri iniyor, ötekiler hiç
denenmiyor. Video ve ses indirmeleri `collab-toolbox`'ta kanıtlanmış hücrelerden geliyor —
yöntem icat edilmiyor, taşınıyor.

## Kararlar

**Üç kutu, üçü de kapalı, hiçbiri seçilmezse defter durur.** Hiçbir üretici kurulmadan açılan
uygulama açılır ve çalışır ama hiçbir şey üretemez: kuyruğa atılan iş "üretici kurulu değil" diye
bekler. Bunu 15 dakika sonra arayüzde öğrenmek yerine CONFIG'de ilk saniyede öğrenmek daha iyi, o
yüzden üçü de kapalıyken `assert` düşüyor.

**Değişken adları İngilizce:** `INSTALL_PHOTO`, `INSTALL_VIDEO`, `INSTALL_AUDIO`. Colab kutunun
etiketi olarak değişken adını gösteriyor; yine de bunlar kod ve repo kuralı kodu İngilizce tutuyor
(CONFIG'deki `BRANCH`, `DRIVE_FOLDER` gibi).

**Drive önbelleği yok.** Modeller her oturumda baştan iniyor (kullanıcı kararı, 2026-08-13). Drive'a
kopyalamak indirme süresini kopyalama süresine çeviriyor ve ikinci bir "hangi dosya nerede" listesi
doğuruyor.

**Custom node'lar kutulara bağlanmıyor.** 19 node'un tamamı her koşuda kuruluyor. Ağır olan modeller;
node'lar birkaç dakika. Node'ları da koşullamak ComfyUI'nin ayakta gelen node kümesini koşudan koşuya
değiştirir, yani hata biçimlerini çoğaltır — kazancı yok.

**Ses kutusu kütüphaneyi de kuruyor.** MMAudio ComfyUI'de çalışmıyor, uygulamanın kendi sürecinde
`import mmaudio` ile çağrılıyor. Ağırlık tek başına işe yaramaz, o yüzden `INSTALL_AUDIO` işaretliyse
repo klonlanıp `pip install -e .` ile kuruluyor.

**Temel ağırlıklar uygulamanın çalışma dizinine iniyor.** MMAudio `./weights` ve `./ext_weights`
yollarını **çalışma dizinine göre** çözüyor, uygulama da `CLONE_DIR/queen-editor` içinden başlıyor.
Defter `download_if_needed()`'ı başka bir dizinde çağırırsa uygulama ilk ses işinde aynı ~6 GiB'ı
sessizce yeniden indirir. Bu yüzden çağrı `APP_DIR` içinden yapılıyor.

**Civitai çerezi koşullu.** Kapılı dosyalar yalnız foto ve video gruplarında; sadece ses kuran bir
koşu çerez olmadan çalışmalı. `assert` bu iki kutudan biri işaretliyse çalışıyor.

**İndirmeden önce disk kontrolü.** İşaretli grupların toplamı + 5 GiB pay boş yer yoksa hücre kendi
sayılarıyla duruyor. Video tek başına ~37 GiB: T4 runtime'ının boş diski buna çoğu zaman yetmiyor,
ve bunu 40 dakikalık indirmenin ortasında "disk dolu" olarak öğrenmek en kötü öğrenme biçimi.
Kontroldeki sayılar (foto 8, video 37, ses 9 GiB) bilerek yukarı yuvarlı: eksik tahmin diski
doldurup yarım dosya bırakır, fazla tahminin bedeli bir uyarı.

## Defterin yeni şekli

### CONFIG (hücre `8215086b`)

Hücrenin en başına, `userdata` import'undan da önce üç satır ve hemen ardından seçim assert'i:

```python
INSTALL_PHOTO = False  #@param {type:"boolean"}
INSTALL_VIDEO = False  #@param {type:"boolean"}
INSTALL_AUDIO = False  #@param {type:"boolean"}
```

Aynı hücreye ek olarak:
- `assert INSTALL_PHOTO or INSTALL_VIDEO or INSTALL_AUDIO` — hiçbiri seçilmemişse dur. En üstte,
  çünkü seçim yoksa okunacak secret'ın da anlamı yok.
- Civitai çerezi assert'i `if INSTALL_PHOTO or INSTALL_VIDEO:` altına iniyor.
- `APP_DIR = f"{CLONE_DIR}/queen-editor"` — ses ağırlıkları ve Flask hücresi aynı yolu kullanıyor;
  bugün Flask hücresinde ayrıca hesaplanıyor, o kopya siliniyor.
- Özet satırı ne kurulacağını yazıyor.
- Çerez yorumu düzeltiliyor: "bu defter hiçbir şey indirmez, çerez uygulamaya geçer" cümlesi v9'dan
  beri yanlış — çerezi bu defter kullanıyor.

### Model indirme (hücre `f0df85b4`)

Tek hücre kalıyor, üç gruba açılıyor. Makine (`check_binary`, `fetch`, `civitai_url`,
`cookie_header`, `civitai_probe`) olduğu gibi duruyor.

Listeler her zaman tanımlı — veri; çalıştırılacak iş kutulardan derleniyor:

| Liste | Yöntem | Satır |
|---|---|---|
| `PHOTO_CIVITAI` | curl + çerez | 2 (nova3DCGXL, USNR lora) |
| `PHOTO_OPEN` | aria2c | 3 (Remacri, yolov9c, SAM ViT-B) |
| `VIDEO_HF` | aria2c | 4 (lightx2v High/Low, Wan2.1 VAE, UMT5-XXL) |
| `VIDEO_CIVITAI` | curl + çerez | 4 (SmoothMix I2V High/Low, Animations XXX High/Low) |
| `AUDIO_HF` | aria2c | 1 (`phazei/NSFW_MMaudio` fine-tune → `models/mmaudio/`) |

Açık indirme satırları `(url, dir, filename, label, min_bytes)` — `min_bytes=None` ise
`check_safetensors`, doluysa `check_binary` (`.pt`/`.pth` kendi boyunu söylemiyor).

Dosya adları `model_groups.py`'nin saydığı adların aynısı; video için Civitai sürüm numaraları
`wan22-arbuzai/api.ipynb`'den geliyor: 2513182 / 2513186 (diffusion_models), 2376136 / 2376143
(loras).

Akış: disk kontrolü → seçili kapılı varlıkların tamamı için `civitai_probe` → açık indirmeler →
kapılı indirmeler → yalnız seçili grupların klasör özeti.

### Ses motoru (yeni iki hücre)

`INSTALL_AUDIO` kapalıysa ikisi de "atlandı" yazıp geçiyor.

1. **Kütüphane:** `/content/MMAudio` klonu + `pip install -e .`. `!` yerine defterin kendi fail-loud
   `run()`'ı: koşul bloğunun içinde çalışıyor ve sessiz başarısızlık bırakmıyor.
2. **Temel ağırlıklar:** `APP_DIR` içinden `all_model_cfg["large_44k"].download_if_needed()` — vae,
   synchformer ve taban checkpoint (~6 GiB). Ayrı hücre, çünkü `pip install -e .` ile aynı hücrede
   `import mmaudio` yapmak taze kurulmuş paketi görmeyebiliyor; kanıtlanmış defterde de ayrı.

Yeri: modellerden sonra, ComfyUI başlamadan önce. Kurulumların hepsi ComfyUI ayağa kalkmadan bitiyor,
böylece pip bir bağımlılığı yükseltirse ComfyUI zaten son ortamla başlıyor.

### Markdown hücreleri

- Giriş (`34c9ff58`): "şimdilik yalnız fotoğraf" notu gidiyor; yerine üç kutu, boyutlar ve
  `CIVITAI_COOKIE`'nin hangi seçimlerde gerektiği.
- ComfyUI (`8de17e98`): "ses motorunun kurulumu hiçbir yerde yapılmıyor" cümlesi artık yanlış —
  ses ComfyUI'de değil, aşağıdaki kendi hücresinde kuruluyor.
- Modeller (`4d387058`): üç grup, seçime göre inen boyut, video için disk uyarısı.

## Uygulama tarafı

- `useProducers.js`'teki `COLAB_INSTALL` cümlesi: "app.ipynb'yi çalıştır" eksik kaldı — kutuyu
  işaretlemeden çalıştırmak hiçbir şey kurmuyor. Cümle kutuyu söyleyecek. Testler sabiti import
  ettiği için metin değişikliği testleri kırmıyor; `frontend/dist` yeniden derlenip aynı commit'e
  giriyor.
- Flask hücresi `QE_COMFY_ROOT`'u da geçiyor. Bugün uygulama kendi varsayılanına düşüyor ve iki yer
  aynı `/content/ComfyUI` sabitini ayrı ayrı yazıyor; defter artık o ağaca kuran taraf olduğuna göre
  yolu söyleyen de o olmalı.

## Testler

`backend/tests/test_notebook_installs_the_photo_group.py` →
`test_notebook_installs_the_producer_groups.py` olarak genişliyor:

1. Üç grubun **her** dosya adı defterde geçiyor (`GROUPS`'tan okunarak — panelin saydığı bir dosya
   defterde unutulamıyor).
2. Kapılı dosyalar kanıtlanmış yoldan: `civitai_probe` + `civitai.red/api/download/models`.
3. Her grubun indirmesi kendi anahtarının arkasında: `INSTALL_PHOTO`, `INSTALL_VIDEO`,
   `INSTALL_AUDIO` defterde geçiyor ve üçü de `#@param {type:"boolean"}` ile tanımlı.
4. Hiçbiri seçilmezse defter duruyor (assert metni defterde).
5. Ses kutusu kütüphaneyi de kuruyor: `hkchengrex/MMAudio` ve `download_if_needed` defterde.
6. Flask hücresi `QE_COMFY_ROOT` geçiyor.

Testler defterin metnini okuyor, çalıştırmıyor — Colab'a bağımlı bir test yazılamaz, ama "panelin
saydığı dosya defterde iniyor mu" sorusu metin üzerinde dürüstçe cevaplanabiliyor.

## Kapsam dışı

- **EKSIKLER.md'ye dokunulmuyor.** Oradaki üç kurulum maddesi (foto 403, video 403, ses "görünmüyor")
  uygulamanın kurulum yapmasıyla ilgiliydi; o yol v9'da kapandı, ama yerine gelenin çalıştığını
  kullanıcının Colab testi söyleyecek. Liste o testten sonra güncellenir.
- **Drive önbelleği**, **model listesine yeni model eklemek**, **video grafiğinin T4'te çalışması**.
- Video render'ının kendisi: bu iş modelleri indiriyor, üretimi değiştirmiyor.

## Riskler

- **MMAudio'nun `pip install -e .`'i bir bağımlılığı yükseltebilir** (torch dahil). Kurulum ComfyUI
  başlamadan bittiği için ComfyUI son ortamla kalkıyor; yine de ilk Colab koşusunda bakılacak yer
  burası.
- **Disk:** üçü birden ~54 GiB. T4 runtime'ının boş diski buna yetmiyor; video isteyen A100'e
  geçmeli. Kontrol bunu indirmeden önce söylüyor.
- **`download_if_needed()` kütüphanenin metodu** — imzası değişirse defter kırılır. Uygulamanın
  kendi çağrısıyla aynı metot olduğu için yeni bir bağımlılık değil, var olanın aynısı.
