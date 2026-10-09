# Madde 403 — Prompt'lar kuyruğa eklenirken yazılıp karta eklenir, uygulama turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 4 · **Parça:** 403 · v8-3e · **Tur:** 2/2 — kırmızı testleri yeşile
çeviren kod. **Testler:** [m403 test turu](2026-10-01-queen-editor-m403-kuyrukta-yazilir-testler-design.md).

**Kullanıcıdan gereken — yok.** Kararlar test spec'inde; buradakiler kodun nasıl yazılacağı.

## Seçilen yol

Döngü her turun başında, üretimden önce, borçlu işler arasında prompt'u yazılması gereken ilkini bulur
ve onu yazar; yazılanı kayda bir satır olarak ekler. Hiç kalmayınca bugünkü gibi üretir — iş kendi
prompt'unu taşımıyorsa kayıtta onun için yazılmış olanla.

Bırakılan yollar:
- **İstek içinde yazmak** (`queue_layer`, `regenerate`, `retry_*` yazarı kendisi sorar) — yazar kare
  başına bir istek; 40 karelik bir basış isteği dakikalarca tutardı, ama kuyruğa ekleyen istek hemen
  202 döner ve ekran onu bekler. Yedi kapıya yedi kez aynı kod da girerdi; döngü hepsinin ortak ucu.
- **Prompt'u plan satırına yazmak** — plan yalnız eklenir, ve her batch'te bir kez baştan yazılır:
  yarıda kalan bir yazma bütün kuyruğu götürür *(plan_store)*. Her prompt için bir kez yazmak o riski
  kırk katına çıkarır; plan ayrıca istekler de onu yazarken döngünün iş parçacığından yazılırdı.
- **Dördüncü bir dosya** — kayıt zaten her katmanın başına geleni tutan eklemeli günlük, ve "prompt'u
  yazıldı" o günlüğün bir olayı; karenin sözleri de oradan okunuyor. Ayrı bir dosya ikinci bir okuma
  yeri olurdu.
- **Bellekte tutmak** (bugünkü `written`) — sayfa göremez, ve sunucu yeniden başlayınca kaybolur.

## Parçalar

### 1. Kayıt — `data/photo_record.py`

- `WRITTEN = "written"` — dosyanın kendi satır biçimi; alan adları gibi yalnız burada bilinir. Domain
  onu hiç görmez.
- `prompt_written(project, frame, layer, file, prompt, at)` — `{"frame", "layer", "file", "status":
  "written", "prompt", "at"}` satırı ekler. `file` katmanın dosya adı: okuyucu dosya adı olmayan satırı
  atlar, ve eski satırların karesi dosya adından okunur.
- `slots()` `written` satırını atlar: katmanın durumu değil — borçlu iş, hiç yazılmamış ya da yeniden
  sıraya konmuş, nasılsa öyle kalır; sırası da *(queue.open_jobs'un iki kademesi)* değişmez.
- `written_prompts()` → `{frame: {layer: prompt}}`: katman hakkındaki son satır `written` ise onun
  prompt'u. Sonraki herhangi bir satır — üretilen, `failed`, `removed`, `queued`, `deleted` — onu
  bitirir.
- `prompts()` değişmez: `prompt` taşıyan her satırı katlar, yazılmış satır da ona girer. Docstring'i
  bunu söyler: bekleyen bir katman için, üretileceği prompt.
- `list()` ve `max_number()` değişmez: yazılmış satır hiçbir zaman fotoğrafın değil, ve numarası
  karenin numarası.

### 2. Port — `domain/ports.py`

`PhotoRecord`'a `prompt_written` ve `written_prompts`; `prompts`'un docstring'i bekleyen katmanı da
anar.

### 3. Döngü — `domain/run_loop.py`

- `_unwritten(owed, writers, record, project)` — borçlu işler arasında, sırayla, prompt'u yazılacak
  ilki ya da `None`. Kural bugünkü: tipinin yazarı var, iş kendi prompt'unu taşımıyor, kayıtta onun için
  yazılmış bir prompt yok, karenin sözleri boş değil. Kaydın sözlerine ancak yazarı olan, prompt'suz
  bir iş varsa sorulur: yazarsız bir koşu kayda bu soruyu hiç sormaz *(test_producer_contract'ın
  sahte kaydı `prompts()` taşımıyor, bilerek)*.
- Tur: `writing = _unwritten(…)`; `current = writing or owed[0]`. Üretici yoksa bekleme yalnız üretim
  turunda: yazma üreticiyi beklemez. Tohum yalnız üretim turunda seçilir.
- Rapor: yazma turunda `"current": None` ve bütün borçlular `pending` — `report` durumu birleştirdiği
  için alan açıkça `None` yazılır, yoksa bir önceki üretimin işi kalırdı.
- Try bugünkü: `under`, `ending`; yazma turunda yazar sorulur, üretim turunda üretici. Hata aynı
  yoldan: aynı işe üç deneme (`holding` katmanın adı, iki turda da aynı), sonra çerçevenin hatasıysa
  kırmızı, değilse koşu durur. Yazma başarılıysa satır `named.steady()` altında eklenir — bir yeniden
  adlandırmanın yarısında eski klasöre düşmesin — ve tur biter.
- Üretim turunda prompt: `current["prompt"] or record.written_prompts(project)…` — kaydın cevabı
  yalnız iş prompt taşımıyorsa istenir.
- Bellekteki `written` kalkar. Modülün, `make_job`'un ve yazarın sorulduğu yerin yorumları şimdi doğru
  olanı söyler: prompt katman kuyruğa girer girmez, her şeyden önce yazılır ve karta eklenir.

### 4. Kuyruğa koyan yerler — yalnız yorum

`queue_layer._job` ("a language model writes it when the job's turn comes") ve
`queue_references.plan_reference_cards` ("a language model writes one when its turn comes") şimdi
doğru olanı söyler. Kodları değişmez: yedi kapı da `run_queue`'yu çağırıyor. Aynı cümle
`LayerPanel.jsx`'in bir yorumunda ve README'nin `DEEPSEEK_API_KEY` / `XAI_API_KEY` satırlarında da
düzelir; README anahtarsız ne olduğunu da doğru söyler: yazma üretimden önce geldiği için, anahtar
yokken bir video ya da ses kuyruğa girince koşu durur.

### 5. Sayfa — `PhotoDetail.jsx`

Not: *"Prompt yok — üretimden önce yazılacak."*; üstündeki yorum nedenini söyler.

## Bilinçli olarak yapılmayan

- Yazarlar ve metinleri değişmez; yazara giden bugünkü gibi.
- `list_frames` değişmez: karenin sözlerini `prompts()`'tan okuyor.
- Yazarın hatası için ayrı bir kural yok: bugünkü üç deneme ve çerçeve/koşu ayrımı.
- `main.py` değişmez.

## Bitti sayılır

Dört satır yeşil. Frontend değişti: dist'i koşuyu yöneten oturum kurar.
