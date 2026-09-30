# Madde 400 — H3 prompt'unu Queen AI yazar, uygulama turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 2 · **Parça:** 400 · v8-3b · **Tur:** 2/2 — kırmızı testleri yeşile
çeviren kod. **Testler:** [m400 test turu](2026-10-01-queen-editor-m400-h3-queen-ai-testler-design.md).

**Kullanıcıdan gereken — yok.** Kararlar test spec'inde; buradakiler kodun nasıl yazılacağı.

## Parçalar

### 1. Taşıyıcı — `backend/services/deepseek/client.py` *(yeni)*

`xai/client.py`'nin ikizi, kendi klasöründe: servis servisi içe aktarmaz *(CODE-STANDARD)*, o yüzden
`NotConfigured` da kendi modülünde. `DeepSeekClient(api_key, model, url, http=requests, timeout=120)`;
anahtar kurulurken kırpılır.

`complete(system, text="", images=())` → cevabın metni. `images` `[(ad, bayt)]`; her biri
`data:<tür>;base64,<…>` olarak bir `image_url` parçası, tür `mimetypes.guess_type(ad)`'dan — fotoğraflar
`.png`. User içeriği önce resimler, sonra söz varsa bir `text` parçası; system mesajı düz metin, çünkü
DeepSeek system mesajındaki resme 400 diyor. Hata, biçim ve boş cevap xAI'daki gibi, başlıkları
`DeepSeek`. Anahtar yoksa: `NotConfigured("DEEPSEEK_API_KEY yok — Colab Secrets'a ekle ve notebook
erişimini aç")`.

Resimleri istemci kodluyor, yazar değil: data URL taşıma biçimi, ne söyleneceği değil.

### 2. Ayar — `backend/config.py`

```python
DEEPSEEK_API_KEY = os.environ.get("QE_DEEPSEEK_API_KEY", "")
DEEPSEEK_MODEL = "deepseek-flash"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_TIMEOUT = 120
```

Model ve adres ortamdan okunmaz: xAI'ınkiler defterin yoklaması uygulamayla aynı şeyi sorsun diye
ortamdan geliyor; DeepSeek'i yoklayan yok *(ön deneme yok)*.

### 3. Port — `domain/ports.py`

`PromptWriter.write(prompts, mode, source=None, scene="")`. `source` üreticinin portundaki `source`'un
kendisi — katmanın yapıldığı dosya, `(ad, bayt)`: videoda fotoğraf, seste video. `scene` karenin
senaryosu, yoksa boş. Döngünün tek çağrı biçimi var: WAN'ın ve sesin yazarı ikisini de alır ve yok
sayar, `references`'ı her üreticinin alması gibi.

### 4. Senaryo — `domain/scene.py` *(yeni)*

397'nin kuralı tek yerde: `by_number(planned)` → `{numara: senaryo}`, `of(found, fid)` →
`found.get(number_of(fid), "")`. `list_frames` bugünkü satır içi sözlüğü bununla değiştirir;
döngü aynısını sorar. Ayrı modül, çünkü `list_frames` döngüyü `start_batch` üzerinden içe aktarıyor —
döngü `list_frames`'i içe aktarsa döngüsel olur.

### 5. Döngü — `domain/run_loop.py`

`_source_for` yazarın sorusundan önceye alınır ve sonuç hem yazara hem üreticiye gider — bir kez
okunur. Yazar `writer.write(words, mode, source=under, scene=scene.of(scene.by_number(jobs), fid))`
ile sorulur; `jobs` turun kendi anlık görüntüsü. Karenin sözlerini tutan yerel değişken `source`'tan
`words`'e döner: `source` artık porttaki dosyanın adı. **Sorunun sorulup sorulmayacağı değişmez:**
iş prompt taşımıyorsa ve karenin sözleri varsa, iş başına bir kez.

### 6. Yazarlar — `data/xai_prompt_writer.py`

- `H3_VIDEO_INSTRUCTION` ve `LOOP_RULE` `tmp/queen-editor-prompts.md`'nin "H3 (400)" ve "Loop"
  bölümleri, kelimesi kelimesine; dosyanın alışkanlığıyla üç tırnağın içinde baştan ve sondan birer
  satır sonu. Üstlerindeki yorumlar şimdi doğru olanı söyler: metni kim yazdı ve kullanıcı sonra
  okuyacak; hizalama satırı ve dynv2 neden istenmiyor; loop'ta kamera neden duruyor.
- `H3VideoPromptWriter.write(prompts, mode, source=None, scene="")`:
  `client.complete(asked(H3_VIDEO_INSTRUCTION, mode), f"Scenario: {scene}" if scene else "", [source])`.
  Sözler gitmez. Bağlı mod `asked()`'dan H3 metnini tek başına alır — 402'ye kadar.
- `VideoPromptWriter` ve `AudioPromptWriter` `source` ve `scene`'i alır, kullanmaz.
- Dosyanın adı kalır: `LOOP_RULE` ve `asked()` iki motorun ortak malı, ve 406 grok'u silerken dosya
  yeniden şekillenir. Modülün docstring'i hangi yazarın hangi taşıyıcıyla konuştuğunu söyler.

### 7. Kompozisyon kökü — `backend/main.py`

`_xai` H3/WAN dalından önce kurulur. H3 dalı `H3VideoPromptWriter(DeepSeekClient(config.DEEPSEEK_API_KEY,
config.DEEPSEEK_MODEL, config.DEEPSEEK_URL, timeout=config.DEEPSEEK_TIMEOUT))`, WAN dalı
`VideoPromptWriter(_xai)`; `_writers` bu yazarı ve `AudioPromptWriter(_xai)`'ı taşır.

### 8. Defter — `queen-editor/queeneditor.ipynb`

JSON metni olarak, yalnız gereken satırlar: anlatımın Secrets maddesinde `DEEPSEEK_API_KEY`; CONFIG'in
`# === Secrets ===` bölümünde `XAI_API_KEY`'in yanına aynı biçimde
`DEEPSEEK_API_KEY = (userdata.get("DEEPSEEK_API_KEY") or "").strip()`; Flask hücresinin ortamında
`"QE_DEEPSEEK_API_KEY": DEEPSEEK_API_KEY`. Yorum yok; yoklama yok.

### 9. README

Secrets tablosuna `DEEPSEEK_API_KEY` satırı — H3'ün prompt'u, QueenAgent'ınkiyle aynı secret —, ve
`XAI_API_KEY` satırı şimdi doğru olanı söyler: WAN'ın video prompt'u ve ses prompt'u.

## Bilinçli olarak yapılmayan

- Fotoğrafı olan ama sözü olmayan kare *(havuzdan doğmuş kartın ilk kare resmi)* bugünkü gibi
  sorulmaz; soru kuralı bu maddenin değil.
- `source` ya da baytları eksikse ayrı bir koruma yok: üretici de o dosyayla üretemez, ve hata döngünün
  üç denemesine düşer.
- Resim küçültülmez; DeepSeek resim başına en çok 1024 token sayıyor *(belge)*.

## Bitti sayılır

Dört satır yeşil; `xai_prompt_writer.py`'deki iki metin `tmp/queen-editor-prompts.md`'dekilerle
karakteri karakterine aynı.
