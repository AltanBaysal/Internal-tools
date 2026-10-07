# Madde 410 — ComfyUI'nin bitti bildirimi, uygulama turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8` · **Parça:** 410 · v8-7 · **Tur:** 2/2 — kod.
**Testler:** [test turu](2026-10-01-queen-editor-m410-bitti-bildirimi-testler-design.md), `9faf41ab`'de
kırmızı.

**Kullanıcıdan gereken — yok.** Araştırma ve karar test turunun spec'inde; bu tur yalnız kodun
şeklini söyler.

## Neler değişir

| Dosya | Değişiklik |
|---|---|
| `queen-editor/backend/services/comfy/client.py` | `websocket=` parametresi; `wait` soketi dinler; üç küçük yardımcı |
| `queen-editor/backend/config.py` | `POLL_INTERVAL`'ın yorumu: artık bakışlar arasındaki **en uzun** süre |
| `queen-editor/backend/requirements.txt` | `websocket-client>=1.8` — uygulamanın çalışırken ihtiyacı olan paket |

**Değişmeyen:** `main.py` (`websocket=` vermez — kütüphanenin kendisi kullanılır), `errors.py`, öteki
her servis ve özellik, defter, ekran, `dist`. Defter bir şey kurmaz: `websocket-client` Colab'ın
runtime'ında Flask ve requests gibi kurulu geliyor.

## `client.py`

**Kütüphane ilk `wait`'te içe aktarılır**, modülün başında değil — `_websocket_client()`:
geliştirme makinesinde kurulu değil, ve uygulama da test takımı da onsuz açılmalı
(`mmaudio_sampler.py`'nin torch için yaptığı gibi). `ComfyClient(..., websocket=None)`: verilen
nesne kullanılır, verilmezse `_websocket_client()`'ın döndürdüğü modül. `__init__` hiçbir şey içe
aktarmaz: `main.py` istemciyi modül yüklenirken kuruyor.

**`wait(prompt_id, timeout)`:**

1. `start = now()`; kütüphane alınır; **soket açılır** (`_listen`) — ilk bakıştan önce.
2. Döngü, bugünkü gibi: zaman aşımı bekçisi (aynı mesaj), `/history` bakışı, kayıt varsa bugünkü
   gibi hata ya da kayıt.
3. Kayıt yoksa: **soket yoksa** `sleep(poll_interval)` — bugünkü yol. **Soket varsa** `_hear_done`:
   bu prompt'un bitti bildirimi gelene ya da bir aralık dolana dek dinler. Soket koptuysa kapatılır ve
   bırakılır; döngü bir sonraki turdan itibaren uyur.
4. `finally`: soket hâlâ açıksa kapatılır — iş bitince, hata gelince, zaman aşımında.

**`_listen(websocket)`** — `ws` + adresin `http`'den sonrası + `/ws?clientId=<client_id>`;
`create_connection(url, timeout=poll_interval)`. `WebSocketException` ya da `OSError` (reddedilen
bağlantı, zaman aşımı) → `None`.

**`_hear_done(websocket, socket, prompt_id)`** — `deadline = now() + poll_interval`; kalan süre
sıfırın üstündeyken `settimeout(kalan)`, `recv()`.
- `WebSocketTimeoutException` → `True` (aralık doldu, soket sağlam).
- Başka bir `WebSocketException` ya da `OSError` → `False` (soket koptu).
- Gelen mesaj bitti bildirimiyse → `True`.
- Süre dolunca → `True`.

**`_is_done(message, prompt_id)`** — modül düzeyinde:
- `str` değilse (ikili önizleme) ya da boşsa (`recv` close frame'i `""` olarak döndürüyor) → `False`.
- `json.loads`; `type` `executing` değilse → `False`. `data`'ya yalnız `executing`'de bakılır:
  ComfyUI'nin kendi gönderdiği bir mesaj, `data`'sı her zaman sözlük — custom node'ların kendi
  olaylarının `data`'sına hiç dokunulmaz.
- `data["node"]` boş ve `data["prompt_id"]` bu prompt → `True`.

`close()` varsayılanıyla çağrılır: sunucunun close cevabını en çok 3 saniye bekler, localhost'ta
anında gelir. Bunun bir sebebi var: ComfyUI bir soket kapanınca o id'nin kaydını, kime ait olduğuna
bakmadan siler (`server.py`, `websocket_handler`'ın `finally`'si). Eski soketin temizliği aynı id'yle
açılan yeni soketten sonraya kalsa, yeni soket bildirim alamaz. Cevabı beklemek temizliği öne alır,
ve bir sonraki soket ancak çıktı indirilip yazıldıktan sonra açılır. Yarış yine de olursa yalnız o
işin hızına mal olur: bakışlar 5 saniyede bir sürer.

**Modülün docstring'i** "ComfyUI HTTP transport" yerine "ComfyUI transport" der ve `websocket`'i
enjekte edilenler arasında sayar.

## Neden böyle

- **Her `wait` kendi soketini açar** — açılır, dinlenir, kapanır; iki iş arasında taşınan bir durum
  yok.
- **Kopan soketi aynı bekleyişte yeniden açmak yok** — kopma ComfyUI'nin gitmesiyse sıradaki
  `/history` bakışı bunu bugünkü `ComfyUnreachable` sözleriyle söyler.
- **Bitti bildirimi yalnız "bak" der**, sonucu `/history` söyler: hata metni ve çıktılar tek yerden
  okunur.

## Bitti sayılır'a karşı

Fotoğraf, WAN ve H3 videosu ComfyUI'de bittiği anda `executing`/`node: null` gelir, `wait` hemen
`/history`'ye bakar, ve iş `fetch_output`'a geçer; 5 saniyelik aralık beklenmez. Gönderilen grafik,
`client_id`, çıktının seçimi ve indirilmesi değişmediği için resim, video ve ses bugünküyle aynı.
MMAudio'nun sesi ComfyUI'den geçmiyor: onda beklenen bir aralık yoktu, değişen de yok.

## Kontrol

Dört satır, paralel, yazıldığı gibi: `test_comfy_client.py`'nin 34 testi yeşile döner, gerisi yeşil
kalır — `test_composition_root.py` (`main.py` istemciyi kurar, kütüphane içe aktarılmaz) ve
`test_requirements.py` (modülün başında `websocket` içe aktarılmıyor) dahil.
