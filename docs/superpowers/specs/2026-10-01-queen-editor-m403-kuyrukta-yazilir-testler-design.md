# Madde 403 — Prompt'lar kuyruğa eklenirken yazılıp karta eklenir, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 4 · **Parça:** 403 · v8-3e · **Tur:** 1/2 — yalnız testler, kırmızı
commit'lenir.

**Kullanıcıdan gereken — yok.** Madde `ALIGNED`, kararlar yol haritasının 403 satırında: prompt katman
kuyruğa eklendiği anda yazılır ve karta eklenir, üretici sırası gelince onu kullanır; H3, WAN ve ses
için *(kullanıcı, 29 Eylül — "evet öyle")*. Yazan modellerin metinlerine dokunulmaz; DeepSeek'e ve
xAI'a hiçbir yerden gerçek istek gitmez.

## Bugün ne oluyor

Video ya da ses işi plana prompt'suz yazılır *(`queue_layer._job`: "a language model writes it when the
job's turn comes")*. Döngü *(`domain/run_loop.py`, `make_job`)* işi sırası gelince üretimin hemen
önünde yazara sorar — karenin sözleri, mod, `source`, `end`, `scene` — ve yazılanı yalnız bellekte
tutar (`written`); prompt ancak katman üretilince, üretilen satırla kayda girer. O zamana kadar karenin
sayfası *"Prompt yok — üretim sırası geldiğinde eklenecek."* der. Yazarın hatası o işin bir denemesi
sayılır: üç deneme, sonra çerçevenin hatasıysa *(`MissingEndFrame`)* kare kırmızı, değilse koşu durur ve
servisin kendi sözleri ekrana çıkar.

## Kurallar

1. **Prompt, iş kuyruğa girer girmez yazılır — her şeyden önce.** Kuyruğa giren her kapı —
   `queue_layer` (Video/Ses paneli), `regenerate` (Yeniden üret), `retry_frame` (Tekrar dene),
   `retry_failed` (hepsini tekrar dene), `resume_batch` (Kaldığı yerden devam et), `start_batch` ve
   `queue_references` — plana ya da kayda yazdıktan sonra `run_queue`'yu çağırır, ve döngü bunları bir
   sonraki turunda görür. Döngü her turda, bir şey üretmeden önce, borçlu işler arasında prompt'u
   yazılmamış olanı arar ve önce onu yazar; hiçbiri kalmayınca üretir. `start_batch` fotoğraf kuyruğa
   koyar (yazarı yok), `queue_references`'ın kartları kullanıcının sözlerini taşır: ikisi hiçbir zaman
   yazdırmaz ama aynı kapıdan geçer.
   **Neden istek içinde değil:** kuyruğa ekleyen istek hemen cevap verir *(routes: "a batch runs for
   minutes, so the request only reports that the work was accepted")*. Yazar her kare için bir istek,
   birkaç saniye; 40 karelik bir panel basışı isteği dakikalarca tutardı ve ekran cevabı bekler. Döngü
   meşgulse — bir fotoğraf ya da video üretiliyorsa — yazma o üretim bitince, sıradaki üretimden önce
   yapılır: her karenin prompt'u yine kendi üretimi başlamadan kartta.
2. **Hangi iş yazdırır — bugünkü kural:** tipinin yazarı var, iş kendi prompt'unu taşımıyor, ve karenin
   sözleri boş değil. Kullanıcının yazdığı prompt yine hiçbir zaman modele gitmez.
3. **Yazılan prompt karta eklenir: kayda.** Kayıt *(`photos.jsonl`)* her katmanın başına geleni tutan
   eklemeli günlük; "bu katmanın prompt'u yazıldı" da bir olay. Yeni satır katmanın durumu değildir:
   iş kuyrukta nasıl bekliyorsa öyle bekler — sırası, katmanın durumu, galerinin sayıları değişmez.
   Karenin sözleri *(`prompts()`)* onu okur: karenin sayfası o katmanın prompt'unu gösterir, ve aynı
   karenin sesini yazan model videonun yazılmış prompt'unu görür.
4. **Üretici karttaki prompt'u kullanır.** Yazılmış prompt, o katman hakkındaki bir sonraki satıra kadar
   geçerli — katman üretilince (üretilen satır aynı prompt'u taşır), kırmızıya dönünce, kuyruktan
   çıkarılınca ya da yeniden sıraya konunca biter. Sunucu yeniden başlasa da, koşu durup devam etse de
   kartta kalır ve yeniden yazdırılmaz.
5. **Tekrar dene yeniden yazdırır.** Sıraya yeniden konan katman yeniden kuyruğa girmiş bir katmandır:
   prompt'u yeniden yazılır, ve kart yenisini gösterir. Kırmızı karenin sayfası, yeniden sıraya
   konana kadar, üretimin hangi prompt'la denendiğini göstermeye devam eder.
6. **Yazarın hatası bugünkü gibi bir deneme sayılır.** Aynı işe üç deneme; çerçevenin hatasıysa kare
   kırmızı ve sebebi sayfasında, değilse koşu durur ve hata servisin kendi sözleriyle ekrana çıkar
   *(`Aynı kare 3 kez denendi — üretim durduruldu` + servisin cevabı)*. İş borçlu kalır, prompt'u
   yazılmamış; *Kaldığı yerden devam et* ya da yeni bir kuyruğa ekleme onu yeniden dener. Fark: yazma
   üretimden önce geldiği için, cevap vermeyen bir model koşuyu sıradaki fotoğraftan da önce durdurur.
7. **Yazılırken hiçbir kare "üretiliyor" görünmez.** Döngü yazarken durumunda üretilen iş yok
   (`current: None`), ve bütün borçlu kareler bekliyor.
8. **Yazara giden bugünkü gibi** — sözler, mod, `source`, `end`, `scene`; yazarların mesajları harfi
   harfine aynı *(404+ onları değiştirir)*. Bağlanacak karenin fotoğrafı yoksa yazar yine hiç sorulmaz.
9. **Sayfanın sözü değişir.** Kuyruktaki katmanın prompt'u henüz yazılmamışsa kutu
   *"Prompt yok — üretimden önce yazılacak."* der: artık üretim sırasını beklemiyor.

## Yazılacak testler

Kırmızı koşuda eksik bir isim toplamayı durdurmasın diye yeni port adları yalnız çağrıldıkları yerde
geçer.

### `test_photo_record.py` — yazılmış prompt kayıtta

Yeni port: `prompt_written(project, frame, layer, file, prompt, at)` yazar,
`written_prompts(project)` → `{frame: {layer: prompt}}` okur.

1. **Yazılan prompt borçlu katmanı bekliyor** — `prompt_written("düğün", "0_a", "video",
   "0_a_V1_0.mp4", "kadın dönüyor", "t")` → `written_prompts == {"0_a": {"video": "kadın dönüyor"}}`.
2. **Karenin sözleri onu söylüyor** — fotoğraf satırı + yazılmış video prompt'u → `prompts() ==
   {"0_a": {"photo": …, "video": "kadın dönüyor"}}`.
3. **Yazılmış prompt katmanın durumu değil** — hiç satırı olmayan katman için yazılınca `slots()` o
   kareyi hiç anmıyor; `queued` bir katman için yazılınca durum `queued` kalıyor.
4. **Katman hakkındaki sonraki satır onu bitiriyor** — parametreli, katmana yazılan bir satır:
   `done`, `failed`, `removed`, `queued`, `deleted` → `written_prompts == {}`.
5. **Yalnız kendi katmanını ilgilendiriyor** — video prompt'u yazıldıktan sonra aynı karenin
   fotoğrafına bir satır → video prompt'u duruyor.

### `test_photo_usecases.py` — döngü ne zaman yazıyor

`FakeRecord` gerçeğinin katladığı gibi katlar: `prompt_written` bir `"written"` satırı ekler, `slots()`
onu atlar, `written_prompts()` katman hakkındaki son satır oysa onu verir.

6. **Kuyruğa giren videonun prompt'u, video yapılmadan kartta** — bir fotoğrafı üretilmiş kare,
   `queue_layer` ile video; video üreticisi yok *(koşu bekliyor — üretim hiç başlamıyor)*, yazar var →
   `list_frames`'te karenin `owed == ["video"]` ve `prompts["video"] == yazarın cevabı`.
7. **Borçlu her prompt, bir şey üretilmeden önce yazılıyor** — iki videolu kare, ikisi de prompt'suz;
   üretici her çağrıda yazarın o ana kadarki soru sayısını not eder → `[2, 2]`.
8. **Karttaki prompt yeniden satın alınmıyor** — kayıtta o video için yazılmış bir prompt var (önceki
   bir koşudan) → `resume_batch`: yazar hiç sorulmuyor, üretici o prompt'la üretiyor, üretilen satır onu
   taşıyor.
9. **Ses, videonun yazılmış prompt'unu görerek yazılıyor** — aynı karede prompt'suz video ve ses işi,
   üretici yok → ses yazarının gördüğü `{"photo": …, "video": <video yazarının cevabı>}`.
10. **Tekrar dene yeniden yazdırıyor** — kırmızı video, kayıtta eski yazılmış prompt'u var → `retry_frame`:
    yazar bir kez soruluyor, üretici yeni cevapla üretiyor.
11. **Yazılırken hiçbir kare üretiliyor görünmüyor** — yazar sorulduğu anda `runner.status()["current"]`
    `None`.

**Bekçiler — değişmeden yeşil kalıyor:** yazarın soru testleri *(tek soru üç denemeye, kendi prompt'unu
taşıyan iş modele gitmez, sözsüz kare sorulmaz, cevap vermeyen model koşuyu durdurur ve iş borçlu
kalır)*; 400'ün ve 402'nin döngü testleri *(yazara giden resim, senaryo, vardığı resim; bağlanacak
fotoğrafı olmayan video yazarı sormadan kırmızı)*; üretilen satırın mod, `endsOn`, tohum testleri;
`queue_layer`'ın, `regenerate`'in, `retry_*`'ın bütün testleri; `test_producer_contract.py` *(yazarsız
koşu kaydın sözlerine hiç sormaz)*.

### `PhotoDetail.test.jsx` — sayfanın sözü

- *"centres the one line a waiting box holds"* ve *"opens the tab of the layer it is waiting for, with
  an empty box"* yeni sözü arar: *"Prompt yok — üretimden önce yazılacak."*
12. **Yazılmış prompt'u olan bekleyen katman onu gösteriyor** — `QUEUED_COPY`'nin `prompts.video`'su
    dolu → Video sekmesinde o metin var, not yok.

## Bitti sayılır

Dört test satırı koşulur. `queen-editor` pytest'inde 1–9 ve 11 kırmızı, doğru sebeple: kayıtta
`prompt_written` yok; döngü bekleyen koşuda yazmıyor, prompt'u üretimden hemen önce yazıyor, karttakini
okumuyor, yazarken işi üretiliyor diye bildiriyor. 10 kırmızı koşuda da yeşil — bugün de Tekrar dene
yazarı yeniden soruyor; uygulamadan sonra kural 5'in bekçisi. `queen-editor` vitest'inde değişen iki
test kırmızı, 12 yeşil *(sayfa bugün de `prompts`'u gösteriyor — bekçi)*. `queen-agent`'ın iki satırı
yeşil.
