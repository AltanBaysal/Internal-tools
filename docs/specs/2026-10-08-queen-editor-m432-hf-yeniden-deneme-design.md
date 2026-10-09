# Madde 432 · HF indirmesi düşünce yeniden denenir — tasarım

**Tarih:** 8 Ekim 2026 · **Madde:** [v9 yol haritası](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md),
432 · **Dal:** `feat/queen-editor-v9` · **Kurallar:** [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Kod için hiçbir şey: deneme sayısı ve aradaki bekleme 8 Ekim'de kabul edildi *(aşağıda)*. Kullanıcı
Colab'da dener — notebook dalı çektiği için push'tan sonra: bir indirme düşerse konsolda hatanın
kendisi görünür ve indirme yeniden denenir.

## Ne, neden

Notebook'un Hugging Face'ten indirdiği her dosya `colab/downloads.py`'nin `hf_fetch`'inden geçer; HF
aynasındaki Civitai dosyaları da (`civitai_fetch`, madde 311). İndirme arada yarıda düşüyor
*(kullanıcı, 2 Ekim — "arada oluyor")*: H3 Eros Max beta5 %97'de şununla düştü —
`File reconstruction error: CAS Client Error: Request middleware error: error sending request for url
(https://us.gcp.cdn.hf.co/xorbs/…)`. Bugün `hf_fetch` ilk hatada durur, ve notebook'un hücresi onunla
biter.

İlk hâlin uyarı satırına — `HF indirmesi düştü (deneme 1/3) — … — 30 sn sonra yeniden deneniyor` —
kullanıcı şunu dedi: *"bir uyarı mesajıda değil hatayı yada responsu direky tpaıştır abi görelim
olru"*. Konsola bizim cümlemiz değil, **hatanın kendisi** basılır.

## Olacak

**Bir deneme düşünce** konsolda iki şey görünür:

- Bir satır olgu: hangi dosya (etiketi, repo'su ve yolu), kaçıncı deneme, ve ne zaman yeniden
  deneneceği.
- Altında **hata, atıldığı gibi**: türü ve mesajının tamamı, `Tür: mesaj` — kısaltılmadan. Hata
  başka bir hatadan atıldıysa zincirin her halkası kendi satırında, atılan hata başta — Python'un
  bağladığı gibi (`__cause__`, yoksa `__context__`). huggingface_hub HF'nin bazı cevaplarını kendi bir
  cümlesinin altına koyuyor — dosyayı Hub'da bulamayınca `LocalEntryNotFoundError` — ve o cümle cevap
  taşımıyor; asıl hata ve HF'nin cevabı altında. Zincir kendine dönerse orada, ve en geç beşinci
  halkada biter.
- HF bir cevap verdiyse **cevabın kendisi** de: zincirde cevap taşıyan ilk hatanın cevabı,
  `--- response: HTTP <kod> ---` ve altında gövdesi, geldiği gibi; gövde boşsa `(boş gövde)`.
  Kimsenin okumadığı akışlı bir gövde istenince hata atar (httpx'in `ResponseNotRead`'i); o zaman
  gövdenin yerinde atılan hata durur — `(gövde okunamadı — Tür: mesaj)`. Atılsaydı hücre okuyucunun
  hatasıyla dururdu, ve düşüş yeniden denenmezdi. Durum satırı ve yeniden deneme kararı değişmez.

Örnek — 2 Ekim'deki düşüş, ilk denemede:

```
⚠️  [14:02:11] H3 Eros Max beta5: HF TenStrip/10Eros-Max/10Eros_Max_h3_TURBO-hybrid_beta5_int8.safetensors, deneme 1/3 — 30 sn sonra yeniden
RuntimeError: Data processing error: File reconstruction error: CAS Client Error: Request middleware error: error sending request for url (https://us.gcp.cdn.hf.co/xorbs/…)
```

HF cevap verdiyse — örneğin bir 502:

```
⚠️  [14:02:11] H3 TAE: HF Kijai/MiniMax-H3-TAE/vae_approx/taeh3.safetensors, deneme 1/3 — 30 sn sonra yeniden
HfHubHTTPError: 502 Server Error: Bad Gateway for url: https://huggingface.co/…
--- response: HTTP 502 ---
<html>…</html>
```

**Yeniden deneme** *(Claude'un önerisi, kullanıcı kabul etti — 8 Ekim)*: en çok 3 deneme; her yeniden
denemeden önce 30 saniye beklenir, sonuncudan sonra beklenmez. Hücreyi durdurmak beklemenin ortasında
da çalışır: yakalanan yalnız `Exception`, durdurmak (`KeyboardInterrupt`) değil.

**Yeniden denenmeyenler:**

- **HF'nin dosya hakkındaki cevabı: 401, 403, 404** — dosya yok ya da bize kapalı. Yeniden sorulan HF
  aynı cevabı verir. Kod basılan cevabınkidir — zincirde cevap taşıyan ilk hatanın: huggingface_hub'ın
  cümlesinin altındaki bir 403 da yeniden sorulmaz. `civitai_fetch` dosyanın
  aynada olmadığını aynanın 404'ünden öğrenir ve Civitai'ye geçer (madde 311); bu beklemesiz kalır.
- **Tam inmiş ama bozuk dosya** — boyut denetimi (`_settled`). Denetim indirmeden sonra, denemelerin
  dışında yapılır: dosya geldi, HF'nin verdiği buydu. Bugünkü gibi yerinde kalır, incelemek için.

**Son deneme de düşünce** hücreyi durduran hata aynı şeyi taşır: olgu satırı (deneme 3/3, ya da
yeniden denenmeyen bir cevapta deneme 1/3) ve altında hatanın kendisi ve HF'nin cevabı. Bu son hata
ayrıca uyarı satırı olarak basılmaz; hücrenin hatası olarak bir kez görünür.

**`civitai_fetch` değişmez.** Aynadan inen bir dosya düşerse o da 3 kez denenir; üçü de düşerse bugünkü
gibi aynanın hatası basılır ve dosya Civitai'den iner.

## Sınırlar

- Yalnız `queen-editor/colab/downloads.py`'nin `hf_fetch`'i ve
  `queen-editor/backend/tests/test_colab_downloads.py` değişir. Adresle inen `fetch` (curl, aria2c),
  `civitai_fetch`, notebook ve uygulama değişmez; frontend ve `dist`'e dokunulmaz.
- Basılan cevap, zincirdeki hataların taşıdığı `response`. Zincirinde cevap olmayan bir hata — 2
  Ekim'deki Xet düşüşü gibi — yalnız türü ve mesajıyla basılır.
- 401, 403 ve 404'ün dışındaki her hata yeniden denenir, yeniden denemenin düzeltemeyecekleri de; bunun
  bedeli en çok iki 30 saniyelik bekleme.
- Yeniden denemenin kaldığı yerden mi devam ettiği yoksa baştan mı başladığı HF'nin
  (`hf_hub_download`'ın) işi.
- Dosyanın satırındaki süre (madde 312'nin tablosu) ilk denemeden dosyanın inmesine kadar sayılır,
  düşen denemeler ve beklemeler dahil — bugün de `start` indirmeden önce alınıyor, ve yeri değişmez.

## Testler — `backend/tests/test_colab_downloads.py`

Ağ sahte, bekleme sahte: `time.sleep` her testte kaydedici bir sahteyle değişir, ve hiçbir test gerçek
bir saniye beklemez.

- **Sahteler HF gibi:** `_hub` bir `errors` listesi alır — ilk çağrılar sırayla onları atar, sonra
  dosya iner. HF'nin cevap verdiği hata, üstünde `response`'u — `status_code` ve `text` — taşıyan bir
  `HfHubHTTPError` sahtesi. `_mirror`'ın aynada olmayan dosyası ve
  `test_a_failed_huggingface_download_says_what_hugging_face_said`'in hatası, gerçek HF gibi, 404'lü
  bir `HfHubHTTPError` olur: bugün cevapsız bir `OSError` atıyorlar, ve öyle kalırlarsa yeniden
  denenirler.
- **Yeni testler:**
  - Düşen indirme yeniden denenir ve iner: iki çağrı, bir 30 saniyelik bekleme, dosya yerinde.
  - Düşen deneme hatayı atıldığı gibi basar: `RuntimeError: <mesajın tamamı>`, 4000 karakteri aşan bir
    mesajla — kısaltılmadığı görülsün; olgu satırında etiket, `deneme 1/3` ve `30 sn`.
  - Düşen deneme HF'nin cevabını geldiği gibi basar: hatanın türü ve mesajı, `HTTP 502` ve gövdesi.
  - Üç denemeden sonra vazgeçilir: üç çağrı, beklemeler `[30, 30]` — sonuncudan sonra bekleme yok;
    hücreyi durduran hata `deneme 3/3`'ü ve hatayı atıldığı gibi taşır.
  - Gövdesi okunamayan cevap düşüşü gizlemez: `.text`'i `ResponseNotRead` atan bir 502 yeniden
    denenir — iki çağrı, beklemeler `[30]` — ve konsolda hata, `HTTP 502` ve okuyucunun hatası.
  - Hücreyi durduran hata HF'nin cevabını da taşır: `HTTP 500` ve gövdesi.
  - 401, 403 ve 404 yeniden sorulmaz: bir çağrı, bekleme yok, ve hata kodu ve gövdeyi taşır.
  - huggingface_hub'ın cümlesinin altındaki cevap da okunur ve basılır: `__cause__`'u 403'lü bir
    `HfHubHTTPError` olan bir `LocalEntryNotFoundError` sahtesi; hata iki halkayı da — atılan başta —
    ve `HTTP 403`'ü gövdesiyle taşır; bir çağrı, bekleme yok.
  - Tam inmiş ama bozuk dosya yeniden indirilmez: bir çağrı, bekleme yok.
  - Aynada olmayan dosya beklemeden Civitai'ye geçer: bekleme yok, ve konsolda aynanın cevabı —
    `HTTP 404` ve `(boş gövde)`.
- Bugünkü testlerin hepsi yeşil kalır.

## Bitti sayılır

- Yeni testler kod değişmeden kırmızı, değişince yeşil — biri dışında: tam inmiş ama bozuk dosyanın
  testi kod değişmeden de yeşil, çünkü bugünkü `hf_fetch` de onu yeniden indirmiyor; test bu davranışı
  sabitler. Bugünkü testler baştan sona yeşil.
- Dört satır yeşil.
- Colab'da: bir HF indirmesi düşerse konsolda hatanın kendisi — ve HF cevap verdiyse cevabın
  kendisi — görünür, indirme yeniden denenir ve dosya tamamlanır. Kullanıcının denemesinde görülecek.
