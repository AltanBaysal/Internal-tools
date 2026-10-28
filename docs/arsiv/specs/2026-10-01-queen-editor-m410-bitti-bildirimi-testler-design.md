# Madde 410 — ComfyUI'nin bitti bildirimi, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8` · **Parça:** 410 · v8-7 · **Tur:** 1/2 — yalnız testler.

**Kullanıcıdan gereken — yok.** Madde 1 Ekim'de hizalandı *(kullanıcı — "ComfyUI'nin bitti
bildirimini dinlemek bunu yapabiliyorsan en mantıklısı bu abi gibi")*: iş biter bitmez fark edilir,
çıktı değişmez. Teknik kararlar Claude'un; ölçüm kullanıcının son testinde.

## Bugün ne oluyor

`ComfyClient.wait` *([client.py](../../../queen-editor/backend/services/comfy/client.py))*
`/history/<prompt_id>`'ye bakıyor; prompt orada yoksa `poll_interval` kadar uyuyor
(`config.POLL_INTERVAL = 5`) ve yeniden bakıyor. Biten iş bir sonraki bakışa kadar — ortalama 2,5,
en çok 5 saniye — fark edilmiyor. Fotoğraf, WAN ve H3 videosu (H3'ün sesi videonun içinde) bu yoldan
geçiyor. **MMAudio'nun sesi geçmiyor:** ComfyUI'nin dışında, Flask'ın kendi sürecinde koşuyor
*(FOUNDATION 6)* — onun beklediği bir bakış aralığı hiç yoktu.

## Araştırmadan, üstüne kurulanlar

- **"Bitti" bildirimi `executing`, `node: null` ve işin `prompt_id`'siyle.** ComfyUI'nin
  `prompt_worker`'ı işi koşturur, `q.task_done(...)` ile `/history` kaydını yazar, **sonra**
  `send_sync("executing", {"node": None, "prompt_id": prompt_id}, server_instance.client_id)` gönderir
  — iş başarılı da, hatalı da, durdurulmuş da olsa
  *([main.py](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/main.py))*. ComfyUI'nin
  kendi örneği de bitişi bununla anlıyor
  *([websockets_api_example.py](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/script_examples/websockets_api_example.py))*.
  Bildirim geldiğinde `/history`'de kayıt **zaten var**.
- **`execution_success` değil:** `PromptExecutor` onu `/history` yazılmadan **önce** gönderiyor
  *([execution.py](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/execution.py))*;
  ona bakıp `/history`'ye gidilse kayıt henüz olmayabilir.
- **Bildirim yalnız işi gönderen `client_id`'ye gider.** Soket `/ws?clientId=<id>` ile açılır, ve
  `submit` zaten `client_id` gönderiyor. **O id'yle açık soket yoksa mesaj sessizce düşer**
  *([server.py](https://raw.githubusercontent.com/comfyanonymous/ComfyUI/master/server.py),
  `send_json`)*: soketi işi gönderdikten sonra açan bir istemci, o arada biten işin bildirimini
  kaçırır. Bu yüzden **soket ilk bakıştan önce açılır**: ondan önce biten iş `/history`'de bulunur,
  sonra biten iş duyulur.
- **Bağlanınca gelen mesajlar** — `status`, ve yürüyen iş bizimse `executing` ile o anki node
  *(prompt_id'siz)*. İş koşarken her adımda `progress`, her node için `executing`, önizlemeler ikili
  mesaj olarak. Hiçbiri "bitti" değil.
- **Kütüphane: `websocket-client`** (modülü `websocket`). ComfyUI'nin kendi örneği onu kullanıyor,
  senkron — Flask'ın senkron dünyasına uyar. **Colab'ın runtime'ında kurulu geliyor**:
  `websocket-client==1.9.2`, Flask ve requests gibi
  *([Colab'ın paket listesi](https://raw.githubusercontent.com/googlecolab/backend-info/main/pip-freeze.txt))*
  — defter onları da kurmuyor, bunu da kurmaz. **Bu geliştirme makinesinde yok**, ve buraya bir şey
  kurulmuyor: kütüphane ilk kullanıldığı yerde içe aktarılır, modülün başında değil —
  `mmaudio_sampler.py`'nin torch için yaptığı gibi —, ve testler kendi sahtesini verir.
  `recv` zaman aşımında `WebSocketTimeoutException`, kopan bağlantıda
  `WebSocketConnectionClosedException` atıyor; ikisi de `WebSocketException`'dan
  *([_exceptions.py](https://raw.githubusercontent.com/websocket-client/websocket-client/master/websocket/_exceptions.py))*.

## Karar — bildirim yalnız "şimdi bak" der

**`/history` ne olduğunu söyleyen tek yer olarak kalır; soket yalnız ne zaman bakılacağını söyler.**
`wait` bugünkü gibi `/history`'ye bakar; prompt orada yoksa uyumak yerine soketi dinler: bu prompt'un
bitti bildirimi gelince hemen yeniden bakar. Soket **en çok bir bakış aralığı** (5 saniye) dinlenir:
bildirim gelmezse, ya da soket hiç açılmazsa ya da koparsa, bakış bugünkü aralıkla sürer. **Soket
yalnız hız kaybettirebilir, iş kaybettiremez.** Zaman aşımı bekçisi ve hata mesajları aynen kalır.

Elenenler:
- **Aralığı kısaltmak** (`POLL_INTERVAL = 0.5`) — en basiti, ama kullanıcı bildirimin dinlenmesini
  seçti, ve *Bitti sayılır* "ComfyUI'nin bildiriminden öğreniyor" diyor.
- **Soketten sonucu okumak** (`executed`'ın çıktıları, `execution_error`) — ikinci bir "ne oldu"
  kaynağı; bugünkü hata metni `/history`'nin `status`'undan çıkıyor ve öyle kalır.
- **Bildirim gelene dek susmadan dinlemek** — iş koşarken mesaj hiç kesilmiyor; bildirim kaçarsa
  `/history`'ye hiç bakılmaz, zaman aşımı bekçisi de dış döngüde olduğu için iş asılı kalır.
- **Bütün oturum için tek kalıcı soket** — kopunca yeniden açma, iki iş arasında birikmiş mesajlar;
  kazancı iş başına bir el sıkışma. Her `wait` kendi soketini açar ve kapatır.
- **Kendi yazdığımız websocket istemcisi** (stdlib `socket`) — protokol işi; kütüphane Colab'da hazır.

## Kurallar

1. **Soket işi gönderen id'yle açılır:** `ws://<ComfyUI'nin adresi>/ws?clientId=<client_id>` —
   `submit`'in `client_id`'si.
2. **Soket ilk `/history` bakışından önce açılır.**
3. **Bu prompt'un bitti bildirimi** — `executing`, `node` boş, `prompt_id` bu prompt — **bekleyişi
   hemen bitirir:** uyunmadan yeniden bakılır.
4. **Başka hiçbir mesaj bitirmez:** yürüyen bir node'un `executing`'i, başka bir prompt'un bitti
   bildirimi, `progress`, `status`, ikili önizlemeler.
5. **Ne olduğunu `/history` söyler:** bildirimden sonra da hata `ComfyExecutionError` olarak, bugünkü
   metniyle gelir.
6. **Soket en çok bir aralık dinlenir** — mesajlar hiç kesilmese de; sonra `/history`'ye bakılır.
   Açılırken de bir aralıktan uzun beklenmez.
7. **Sessiz soket** — bildirim hiç gelmezse — bakışı bir aralık sonra yapar; uyumaya gerek kalmaz,
   bekleyen soketti.
8. **Kopan soket bırakılır:** kapatılır, bir daha dinlenmez, bakış aralığı bugünkü gibi uyunur.
9. **Açılmayan soket bekleyişi bugünkü gibi bırakır:** bakış, aralık kadar uyku, bakış.
10. **Bekleyiş biterken soket kapanır** — iş bitince, hata gelince, zaman aşımında.
11. **Zaman aşımı bekçisi soketle de çalışır**, bugünkü mesajıyla: `prompt <id>: <n>s içinde bitmedi`.
12. **Hiçbir test gerçek bir soket açmaz, gerçek bir saniye beklemez.**

**Değişmeyen:** gönderilen grafik ve `client_id`, workflow'lar, ComfyUI'nin kurulumu ve başlatılması,
işlerin sırası, `fetch_output`, `upload_image`, `interrupt`, hata metinleri. Defter, ekran ve `dist`.

## Nasıl kanıtlanıyor

`ComfyClient` kütüphaneyi `http=requests` gibi alır: **`websocket=`** parametresi, verilmezse
kütüphanenin kendisi. Testler bir sahte modül verir — `create_connection(url, timeout)`,
`WebSocketException`, `WebSocketTimeoutException` —, ve sahte bağlantı `settimeout`, `recv`, `close`
taşır. Sahte bağlantı sıradaki mesajı verir (metin `str`, önizleme `bytes`, ya da atılacak bir
istisna); mesaj bitince, zaman aşımına kadar bekleyip hiçbir şey gelmemiş bir soket gibi
`WebSocketTimeoutException` atar. **Saat sahte, ve yalnız bekleyen bir şey onu ilerletir:** uyku
verdiği süre kadar, susan soket kendisine verilen zaman aşımı kadar, mesaj veren soket istenirse
mesaj başına bir adım. Bağlanma, `/history` bakışı ve `recv` tek bir günlüğe sırayla yazılır.

## Yazılacak testler — `backend/tests/test_comfy_client.py`

Dinleyen istemci: `poll_interval=5`, sahte saat, sahte soket. `ENTRY` başarılı, `FAILED` bugünkü
testteki hatalı kayıt; `DONE` `{"type": "executing", "data": {"node": null, "prompt_id": "p1"}}`.

1. **Soket işi gönderen id'yle açılır** — `submit`, sonra `wait`: tek bağlantı,
   `ws://comfy:8188/ws?clientId=<client.client_id>`; `submit`'in gönderdiği `client_id` aynı.
2. **Soket ilk bakıştan önce açılır** — günlük `connect`, `get` ile başlar.
3. **Bitti bildirimi bekleyişi hemen bitirir** — soket `DONE` verir; `/history` önce boş, sonra
   `ENTRY`. Dönen `ENTRY`; günlük `connect, get, recv, get`; uyku yok.
4. **Başka mesajlar bitirmez** — sırayla `progress`, `executing` node `"3"`, başka prompt'un (`p0`)
   bitti bildirimi, ikili önizleme, sonra `DONE`. İkinci bakış beş `recv`'den sonra.
5. **Bildirimden sonra da ne olduğunu `/history` söyler** — soket `DONE` verir, `/history` `FAILED`
   döner: `ComfyExecutionError`, metninde `CheckpointLoaderSimple`.
6. **Sessiz soket bir aralık sonra bakar** — mesaj yok: günlük `connect, get, recv, get`; `recv`'e
   verilen zaman aşımı 5; bağlanmaya verilen zaman aşımı 0'dan büyük, 5'ten büyük değil; uyku yok.
7. **Mesajlar kesilmese de soket bir aralıktan uzun dinlenmez** — yirmi `progress`, her biri saati bir
   saniye ilerletir: ikinci bakıştan önce en az bir, en çok beş `recv`; hiçbir zaman aşımı 5'i geçmez.
8. **Kopan soket bırakılır** — ilk `recv` bağlantı koptu der; `/history` iki kez boş, sonra `ENTRY`.
   Dönen `ENTRY`; tek `recv`; soket kapalı; uyku var ve her biri 5.
9. **Açılmayan soket bekleyişi bugünkü gibi bırakır** — bağlanma `ConnectionRefusedError`; `/history`
   önce boş, sonra `ENTRY`. Dönen `ENTRY`; uyku `[5]`.
10. **Bekleyiş biterken soket kapanır** — parametreli: iş biter (`ENTRY`) ya da hata gelir (`FAILED`,
    `ComfyExecutionError`). İkisinde de soket kapalı.
11. **Zaman aşımı bekçisi soketle de durdurur** — susan soket, `/history` hep boş, `timeout=12`:
    `TimeoutError`, mesajı `prompt p1: 12s içinde bitmedi`; soket kapalı.

### Değişen

- **`client_with`** her istemciye susan bir sahte soket verir: hiçbir test gerçek bir sokete ya da
  kütüphaneye ulaşmasın. `poll_interval=0` olduğu için o istemciler soketi dinlemez bile — eski testler
  bugünkü yoldan geçer.
- **`FakeHttp`** isteğe bağlı bir günlük alır, `get`'leri ona yazar.
- **`test_wait_times_out`** — saat `iter([0, 10, 20, 30])` yerine durmadan ilerleyen bir sayaç
  (`itertools.count(0, 10)`): bekleyiş saate artık her bakışta değil, dinlerken de soruyor, ve dört
  değer biter. Sorduğu aynı: zaman aşımında `TimeoutError`.

**Bekçi, bugün de yeşil:** `test_requirements.py` — modülün başında `import websocket` yazılsa
`websocket` adı `requirements.txt`'te olmadığı için kırmızıya döner, ve bu makinede de toplama düşer.

## Kırmızı beklenen

- `test_comfy_client.py`'nin tamamı kırmızı: `ComfyClient` `websocket=` parametresini tanımıyor
  (`TypeError: ... unexpected keyword argument 'websocket'`) — `client_with` de onu verdiği için eski
  testler de aynı sebeple düşer. Yeni arayüz uygulama turunun ilk işi.
- `queen-editor` pytest'inde öteki her şey yeşil — `test_composition_root.py` dahil: `main.py`
  `websocket=` vermiyor. Öteki üç satır yeşil.

## Bilinçli olarak yapılmayan

- Soket kopunca aynı bekleyiş içinde yeniden açılmaz: bir sonraki iş kendi soketini açar; o işin
  geri kalanı bugünkü gibi 5 saniyede bir bakar.
- Bozuk JSON'a karşı ayrı bir dal yok: ComfyUI metin mesajlarını yalnız `send_json` ile gönderiyor.
- `websocket-client` için kurulu mu yoklaması yok: Colab'da kurulu geliyor, gelmezse hata
  `ModuleNotFoundError`'ın kendi sözleriyle görünür — sebep uydurulmaz.
- Ekran, defter ve `dist` değişmez. Yol haritasına dokunulmaz.
