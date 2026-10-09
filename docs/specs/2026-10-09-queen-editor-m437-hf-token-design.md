# Madde 437 · Notebook HF_TOKEN'ı kendisi okur — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
437 · **Dal:** `feat/queen-editor-v9` · **Kurallar:** [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Kod için hiçbir şey. Token yokken koşunun sürüp sürmeyeceğine Claude karar verdi *(aşağıda)*.
Kullanıcı roadmap bitince Colab'da dener.

## Ne, neden

Colab'da, 9 Ekim: modeller hücresinin HF indirmesi huggingface_hub'ın kendi uyarısını bastı:
`Requesting secret HF_TOKEN timed out. Secrets can only be fetched when running from the Colab UI.`
İndirme token'sız sürdü (`You are sending unauthenticated requests to the HF Hub`), ve H3 Eros Max
%50'de `429 Too Many Requests` ile düştü. Token geçerli: bir hücrede `userdata.get("HF_TOKEN")` ve
`whoami` kullanıcının adını verdi. Kullanıcı kendi açtığı bir hücrede
`os.environ["HF_TOKEN"] = userdata.get("HF_TOKEN")` çalıştırınca uyarılar gitti, ve indirme yetkili
oldu.

### Bugün

- Notebook `HF_TOKEN`'ı hiç okumuyor. CONFIG `GITHUB_TOKEN`'ı, `CIVITAI_COOKIE`'yi ve
  `DEEPSEEK_API_KEY`'i `userdata.get` ile okuyor; HF'nin token'ını huggingface_hub'a bırakıyor.
- `colab/downloads.py`'nin `hf_fetch`'i `hf_hub_download(repo, path, local_dir=STAGE)` çağırıyor,
  `_upload`'u `HfApi().upload_file(...)`. İkisi de token vermiyor: huggingface_hub token'ı kendisi
  arar, indirmenin ortasında Colab'ın kasasına gider, ve kasa orada cevap vermedi.

### Kasa neden yine sorulurdu

huggingface_hub token verilmeyince onu kendisi arar. Claude'un bildiği sürümlerde Colab'da **önce
kasaya** bakar, ortamdaki `HF_TOKEN`'a ancak kasa bir şey vermezse; ve kasanın cevabını oturum boyunca
saklar. Kullanıcının denemesinde uyarıların gitmesi buna uyuyor: kasa o oturumda bir kez sorulmuş ve
boş dönmüştü, sonraki istekler ortamdakini aldı. Yeni bir oturumda yalnız ortama koymak, ilk HF
isteğini yine kasaya gönderebilir. Bu, kütüphanenin koduna bakılarak doğrulanmadı (depo dışı).
**Bu yüzden indirme ve yükleme token'ı huggingface_hub'a açıkça verir:** token bir metin olarak
verilince kütüphane hiçbir yere bakmaz. Sıra Claude'un bildiği gibi olmasa da açık token zararsız.

## Olacak

### 1. Token, indirmelerden önce, notebook'un kendi okumasıyla ortama girer

`colab/downloads.py`'ye `use_hf_token(read)` eklenir. `read`, `userdata.get`'tir; test sahte bir okuyucu
verir. Fonksiyon:

- `read("HF_TOKEN")`'ı çağırır, sonucu kırpar (`DEEPSEEK_API_KEY` gibi — yapıştırma satır sonu taşır).
- **Okunduysa** `os.environ["HF_TOKEN"]`'a koyar ve basar:
  `✅ [..] HF_TOKEN okundu — Hugging Face'e token'la gidilecek`. Token basılmaz.
- **Okuma bir hata attıysa** — kasada yok (`SecretNotFoundError`), erişim verilmedi
  (`NotebookAccessError`), zaman aşımı, ne olursa — basar:
  `⚠️ [..] HF_TOKEN okunamadı — <Tür>: <mesaj>`, ve altında ne olacağı (bölüm 3).
- **Değer boşsa** basar: `⚠️ [..] HF_TOKEN boş`, ve altında aynı cümle.
- Okunamayan ya da boş token'da ortamdaki `HF_TOKEN` silinir: aynı çekirdekte önceki bir koşudan
  kalan token, satırın "token'sız" dediği koşuda kullanılmasın.

**Nerede çağrılır: ortak yardımcılar hücresinde**, `colab/`'ın import'larının hemen altında:
`use_hf_token(userdata.get)`. Brief CONFIG'i önerdi, ama CONFIG klondan önce koşuyor ve `colab/`
klonla geliyor; CONFIG onu import edemez. Yardımcılar hücresi klonun hemen ardından, ComfyUI'nin
kurulumundan ve ilk HF indirmesinden önce koşar. `userdata` CONFIG'de import edilmişti. Bu, hücre
dışında test edilebilen tek yer; madde 438 öteki secret'ların yerine kendisi bakar.

### 2. İndirme ve yükleme token'ı açıkça verir

- `hf_fetch`: `hf_hub_download(repo, path, local_dir=STAGE, token=_token())`.
- `_upload`: `HfApi().upload_file(..., token=_token())`.
- `_token()`: ortamdaki `HF_TOKEN`, yoksa `False`. `False` huggingface_hub'a "token'sız git, arama"
  demektir: token yokken de kasaya gidilmez, uyarı çıkmaz.

### 3. Token yoksa koşu sürer

**Karar: sürer, ve satır sonucunu söyler.** Neden:

- H3'ün, fotoğrafın ve sesin HF'deki dosyaları açık repolarda; token'sız iner (429 riskiyle).
- Ayna özel: token'sız HF 401 döner. `civitai_fetch` bunu bugün de karşılıyor — aynanın cevabını
  basar, dosyayı Civitai'den indirir (çerez gerekirse çerezi ister), yükleme reddi bir uyarı satırı.
- Durdurmak, aynaya hiç ihtiyacı olmayan bir koşuyu da durdururdu (ör. yalnız ses). CONFIG çerezi de
  bu yüzden baştan istemiyor (madde 311).

Satırın altındaki cümle:
`Hugging Face'e token'sız gidilecek: açık dosyalar iner ama HF 429 dönebilir; aynadan alma ve aynaya
yükleme olmaz — Civitai dosyaları çerezle Civitai'den iner. Colab 🔑 Secrets'a 'HF_TOKEN' adıyla ekle.`
"Çerezle": çerez yoksa `civitai_fetch` bugünkü gibi `CIVITAI_COOKIE`'yi isteyerek durur.

## Sınırlar

- **Flask süreci** `os.environ`'u devralır, yani `HF_TOKEN` artık uygulamanın ortamında da var. Uygulama
  huggingface_hub ile bir şey indirirse (MMAudio'nun yan modelleri gibi) o kendi aramasını yapar; bu
  maddede ona dokunulmadı.
- **MMAudio'nun ağırlık hücresi** (`download_if_needed`) değişmez.
- **Kütüphanenin arama sırası doğrulanmadı** *(yukarıda)*; açık token iki durumda da doğru.
- Kasanın neden zaman aşımına uğradığı gösterilmedi. Okuma artık hücrenin kendi çağrısıyla, Colab
  arayüzünden çalışan bir hücrede yapılıyor — kullanıcının elle denediği gibi.

## Değişen dosyalar

| Dosya | Değişiklik |
|---|---|
| `colab/downloads.py` | Yeni `use_hf_token(read)`, onun `_without_token(said)`'i ve `_token()`; `hf_fetch` ve `_upload` token'ı açıkça verir |
| `queeneditor.ipynb` | Ortak yardımcılar hücresi `use_hf_token`'ı import eder ve `use_hf_token(userdata.get)` çağırır |
| `backend/tests/test_colab_downloads.py` | Yeni testler |
| `backend/tests/test_notebook_installs_the_producer_groups.py` | Yeni test |

## Testler

- **`test_colab_downloads.py`:**
  - Okunan token kırpılıp ortama girer, satır okunduğunu söyler, token basılmaz.
  - Okuma hata atınca satır `HF_TOKEN okunamadı` ve hatanın türünü ve mesajını, ve token'sız
    gidileceğini söyler; ortamda önceden duran `HF_TOKEN` silinir.
  - Boş değer (`""`, `None`) için satır `HF_TOKEN boş` der; ortamda token kalmaz.
  - `hf_fetch` ortamdaki token'ı `hf_hub_download`'a `token=` ile verir; ortamda yoksa `token=False`.
  - Aynaya yükleme token'ı `upload_file`'a verir; yoksa `False`.
  - İki test de `_hub`'ın ve `_mirror`'ın sahtesini sarar, yeni bir sahte yazmaz.
- **`test_notebook_installs_the_producer_groups.py`:** yardımcılar hücresi
  `use_hf_token(userdata.get)` çağırır, ve onu `colab.downloads`'tan import eder. İsmin modülde
  olduğunu bugünkü `test_every_name_the_notebook_imports_from_its_code_exists` sorar.
- Bugünkü testlerin hepsi yeşil kalır: sahte `hf_hub_download` ve `upload_file` `**_` ile ek
  argümanı alıyor.

## Bitti sayılır

- Yeni testler kod değişmeden kırmızı, değişince yeşil; dört satır yeşil.
- Colab'da, kullanıcının denemesinde görülecek: modeller hücresi `HF_TOKEN` uyarısı olmadan, yetkili
  indiriyor; token yoksa ya da okunamazsa yardımcılar hücresi bunu, okumanın attığı hatayla söylüyor.
