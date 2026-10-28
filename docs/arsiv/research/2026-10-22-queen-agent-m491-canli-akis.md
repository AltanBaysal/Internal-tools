# Madde 491 · Süren tur ekranda neden canlı akmıyor — araştırma

**Tarih:** 22 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-20-queen-agent-v11-roadmap.md),
491 · v11-2, adım 2 · **Kod yok, deneme yok.** Kullanıcının sözü *(20 Ekim)*: *"ilk önce araştır test
etme bana haber vermeden test etme bulamazsan çözmezsen collabte ben bakarım"*. Bu belge yalnız
belgelerden, bilinen kayıtlardan ve depodaki koddan yazıldı; hiçbir tünel açılmadı, uygulama
çalıştırılmadı.

**Görülen** *(backlog girdisi, 13 Ekim)*: Colab'da bir tur sürerken token sayısı ve araç çağrıları
ekranda belirmiyor; F5'te o anki hâl geliyor; tur bitince cevap kendiliğinden çıkıyor.

İşaretler: **[doğrulandı]** resmî bir belgeden ya da depodaki koddan okundu · **[rapor]** üçüncü
tarafın kendi denemesi ya da bir Cloudflare çalışanının issue yorumu, resmî belge değil · **[çıkarım]**
yukarıdakilerden çıkarıldı, kimse ölçmedi.

## Sonuç

**En olası sebep: Cloudflare Quick Tunnel, GET ile açılan bir akışın cevabını istek bitene kadar
tutuyor.** EventSource her zaman GET'tir; 462'den beri tur `GET …/events` ile dinleniyor, ve tünel
kareleri turun sonuna kadar biriktirip birden veriyor. Sunucu ve ekran kodu doğru; aynı kod tünelsiz
canlı akıyor (462'nin denemesi). Bu sebep görüleni üç noktada birden açıklıyor: tur sürerken hiçbir
şey, F5'te o anki hâl (F5'in okuduğu `GET …/chats/<id>` biten sıradan bir istek), sonda cevap (akış
bitince bütün kareler bir anda iner, son kare `{turn: null}` kaydı okutur).

**En küçük düzeltme adayı: aynı kapıda uzun yoklama (long polling).** Her cevap biten bir GET olduğu
için tünelin tutacağı açık bir akış kalmıyor; sunucudaki `changed_since` bunu zaten yapıyor.
Sıralama ve bedelleri [aşağıda](#düzeltme-adayları-sıralı).

## 1. Cloudflare'in kendi sözü

- *"Quick Tunnels do not support Server-Sent Events (SSE)."* — Quick Tunnel'ın sınırlamaları listesinde,
  200 eşzamanlı istek sınırı ve çalışma süresi güvencesi olmamasıyla yan yana. **[doğrulandı]**
  [Quick Tunnels — Limitations](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/)
  (eski adresi: [trycloudflare](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/)).
- Belge **ne olduğunu** söylemiyor: akışın düştüğünü mü, tutulduğunu mu, hangi metotta. WebSocket'ten
  hiç söz etmiyor. **[doğrulandı]** aynı sayfa.
- **Named tunnel'da farklı.** Cloudflare'den bir katkıcı *(jcsf, 22 Nisan 2025)* aynı örneğin *"works as
  expected with named tunnels"* olduğunu, Quick Tunnel'daki davranışın bir koruma sınırı olduğunu
  (*"quick-tunnels are only meant for demo purposes"*) yazdı; ertesi gün *"We will try to have SSE work
  on quick tunnels, but I can't give an ETA."* Issue hâlâ açık. **[rapor]**
  [cloudflared #1449](https://github.com/cloudflare/cloudflared/issues/1449)
- 2026'nın cloudflared sürümlerinde (2026.9.x'e kadar) bunu düzelten bir not bulunamadı. **[rapor]**
  aramada çıkan sürüm notu özeti:
  [helmforgedev/charts #1236](https://github.com/helmforgedev/charts/pull/1236) — resmî changelog
  doğrudan okunmadı.

## 2. Tünel tam olarak ne yapıyor: GET tutuluyor, POST akıyor

- **cloudflared #1449** *(12 Nisan 2025, cloudflared 2025.2.1, FastAPI + sse-starlette)*: aynı `/sse`
  hem GET hem POST'a bağlı, 0,5 sn'de bir 20 kare. Tünelden **POST canlı aktı; GET hiçbir şey vermedi,
  sunucu bağlantıyı kapatınca 20 kare birden geldi.** Sunucunun başlıkları doğruydu:
  `content-type: text/event-stream`, `cache-control: no-store`, `x-accel-buffering: no`,
  `transfer-encoding: chunked`. Yazarın sonucu: tutma sunucudan sonra, tünelde ya da kenarda.
  **[rapor]** [cloudflared #1449](https://github.com/cloudflare/cloudflared/issues/1449)
- **Flavio Copes** *(denemesi 22 Eylül 2026, yazı 7 Ekim 2026)*: *"Through the tunnel, the client saw the
  headers arrive, then nothing for five seconds, then all five lines at once"*; *"Every GET response was
  held until it completed"*; *"When I switched my test route to POST, the chunks came through as they
  were written"*; *"EventSource, the browser API for SSE, always uses GET, so SSE arrives all at once at
  the end."* Kendisi de uyarıyor: *"This is what I observed, not documented behaviour, and it can change
  on Cloudflare's side without notice."* **[rapor]**
  [The complete guide to Cloudflare Quick Tunnels](https://flaviocopes.com/cloudflare-quick-tunnels/)
- **la-sala-app** *(PR, 7 Ekim 2026)*: *"Through a Cloudflare Quick Tunnel the board loaded and listed the
  pistes but never showed a bout or a score change."* — bizim gördüğümüzün aynısı. **[rapor]**
  [la-sala-app #25](https://github.com/pbelaustegui/la-sala-app/pull/25)
- **cctop** *(8 Ekim 2026)*: aynı belgeye dayanıp akış takılınca yoklamaya düşen bir yedek yol yazdı.
  **[rapor]** [cctop #172](https://github.com/flolep2607/cctop/issues/172)

**Başlıkların gördüğü yer.** Bir başlık bunu açmıyor: #1449'daki sunucu `no-cache`'ten de sıkı
`no-store`'u ve `X-Accel-Buffering: no`'yu zaten gönderiyordu. `X-Accel-Buffering` nginx'e söylenen bir
sözdür; Cloudflare'in onu dinlediğine dair bir belge yok. **[rapor + çıkarım]**

**Eski, kapanmış bir kayıt karıştırılmasın.** [cloudflared #199](https://github.com/cloudflare/cloudflared/issues/199)
*("Server-sent-events are buffered", 2020)* named tunnel'larda `text/event-stream` dışındaki türlerin
tutulmasıyla ilgiliydi; 14 Mayıs 2025'te *"Server Sent Events have been fixed"* diye kapandı. #1449
ondan sonra da açık ve Quick Tunnel'a özgü. **[rapor]**

**Sıkıştırma sebep değil.** Cloudflare'in varsayılan olarak sıkıştırdığı türler arasında
`text/event-stream` yok. **[doğrulandı]**
[Content compression](https://developers.cloudflare.com/speed/optimization/content/compression/)
QueenAgent'ın kendisi de hiçbir şey sıkıştırmıyor (Flask'tan başka bağımlılık yok). **[doğrulandı]**
[queenagent.ipynb](../../../queen-agent/queenagent.ipynb), Clone hücresi.

**Dolgu (padding) hilesi.** Bazı vekillerde kareleri 2–4 KB'lık boşlukla şişirmek tamponu boşaltır
(#199'daki bir yorumda 3–4 KB'lık tampon). Quick Tunnel için bunun işe yaradığına dair bir kayıt
bulunamadı. #1449 ile Flavio'nun denemeleri küçük gövdelerle yapıldı, yani "istek bitene kadar" ile
"birkaç KB dolana kadar" ayrılmıyor. Ama ikisi de "bitince birden geldi" diyor, ve bizde tur bitince
cevabın kendiliğinden gelmesi de "bitene kadar"a uyuyor. **[çıkarım]** Bu yüzden aday değil.

**`--protocol http2`.** Defter tüneli varsayılan QUIC'le açıyor; Queen Editor'ün galeri araştırması
http2'ye geçişi hız için önermişti ([galeri yavaşlığı](2026-08-23-queen-editor-galeri-yavasligi.md)).
Protokolün GET'in tutulmasına etkisi olduğuna dair bir kayıt bulunamadı. **[çıkarım: bilinmiyor]**

## 3. 461'den önceki POST akışı

- 462'den önceki akış `text/event-stream`'di ama **POST'tu**, ve `fetch` + `response.body.getReader()`
  ile okunuyordu (`shared/sse.js`, 462'de silindi; dosyanın ilk satırı: *"EventSource can only GET, and
  the door a message goes through is a POST, so the stream is read straight off the response body"*).
  **[doğrulandı]** `git show 17ae3f8a^:queen-agent/frontend/src/shared/sse.js`
- Başkalarının kaydına göre bu şekil Quick Tunnel'dan **canlı akar**: #1449'da POST canlı, Flavio'da POST
  canlı, Ollama ve OpenAI biçimli akan POST API'leri çalışıyor. **[rapor]**
  [#1449](https://github.com/cloudflare/cloudflared/issues/1449),
  [Flavio Copes](https://flaviocopes.com/cloudflare-quick-tunnels/)
- Kullanıcı o günlerde Colab'da canlı akıp akmadığını hatırlamıyor *(20 Ekim — "hatırlamıyorum")*. v4
  yol haritası *"cloudflared akışı taşır"* diyor, ama kaynağını yazmıyor
  ([v4](../roadmaps/2026-08-20-queen-agent-v4-roadmap.md)). Yani bizde gözlem yok; kayıtlar POST'un
  aktığını söylüyor. **[rapor + çıkarım]**
- Yol haritasının sorusunun cevabı *(v11-2, "Bilinenler" 4)*: **tüneli bozan SSE'nin kendisi değil,
  GET.** 462 akışı POST'tan GET'e, `fetch`'ten EventSource'a taşıdığında akış tünelin tuttuğu yola
  geçti. **[rapor + çıkarım]**

## 4. Bugünkü kod ve defter

- **Kapı:** `GET /api/projects/<p>/chats/<c>/events` →
  `Response(_listened(live), mimetype="text/event-stream", headers=EVENT_HEADERS)`;
  `EVENT_HEADERS = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"}`. Content-Length yok.
  **[doğrulandı]** [routes.py](../../../queen-agent/backend/features/workspace/presentation/routes.py)
  satır 68 ve 137–143.
- **Akış:** `_listened` önce o anki snapshot'ı, sonra her değişiklikte bütün snapshot'ı bir kare olarak
  yazıyor; 15 sn sessizlikte `": beat"` yorum satırı; tur bitince akış bitiyor. Değişiklik
  `live.changed_since(version, BEAT_SECONDS)` ile bekleniyor. **[doğrulandı]** aynı dosya, satır
  344–366.
- **Sunucu:** `app.run` — Werkzeug'un geliştirme sunucusu. Content-Length olmayan HTTP/1.1 cevabını
  chunked yazıyor ve **her `write`'tan sonra `wfile.flush()`** çağırıyor, yani kareler sunucudan
  bekletilmeden çıkıyor. **[doğrulandı]** [main.py](../../../queen-agent/main.py) son satır;
  [werkzeug serving.py](https://github.com/pallets/werkzeug/blob/main/src/werkzeug/serving.py)
  (`run_wsgi` içindeki `write`). 462'nin spec'i bunu gerçek Werkzeug sunucusunda tünelsiz denedi:
  *"kareler anında, sinyaller aralıkla"*. **[doğrulandı]**
  [m462 spec](../specs/2026-10-10-queen-agent-m462-ekran-sunucu-durumu-design.md), Sınırlar; aynı yerde
  *"trycloudflare üstünden `EventSource` denenmedi"*.
- **Ekran:** `useChat.js` her tur için bir `new EventSource(eventsOf(project, id))` açıyor, her karede
  `heard` turu çiziyor; kopmayı EventSource kendisi onarıyor, yalnız `CLOSED` kodun işi. **[doğrulandı]**
  [useChat.js](../../../queen-agent/frontend/src/features/workspace/useChat.js) satır 71–112.
- **Defter:** Serve hücresi `cloudflared tunnel --url http://127.0.0.1:8100` ile bir Quick Tunnel açıyor,
  `--protocol` vermeden; linki `trycloudflare.com` adresinden okuyor. Colab'ın kendi port vekili
  *"forwards only GET"* diye seçilmemiş. **[doğrulandı]**
  [queenagent.ipynb](../../../queen-agent/queenagent.ipynb), Serve hücresi. `colab/` diye bir yardımcı klasör
  depoda yok; QueenAgent'ın Colab'daki her şeyi bu üç hücrede.

## 5. Quick Tunnel'dan geçen başka yollar

| Yol | Quick Tunnel'dan geçer mi | Kaynak |
|---|---|---|
| **Biten GET'ler** — kısa ya da uzun yoklama | Evet: tünel GET'i bitene kadar tutuyor, biten GET'in tutulacak bir şeyi yok. F5'in çalışması da bunu gösteriyor. | **[çıkarım]** #1449 ve Flavio'nun "held until it completed"ından; uygulamanın bütün öbür GET'leri zaten böyle çalışıyor |
| **POST + `fetch` okuyucusu** | Evet, canlı akıyor — ama belgelenmemiş bir davranış | **[rapor]** [#1449](https://github.com/cloudflare/cloudflared/issues/1449), [Flavio Copes](https://flaviocopes.com/cloudflare-quick-tunnels/) |
| **WebSocket** | Evet: *"WebSockets go through quick tunnels … about a quarter of a second behind the local run"* | **[rapor]** [Flavio Copes](https://flaviocopes.com/cloudflare-quick-tunnels/); Cloudflare'in Quick Tunnel sayfası WebSocket'ten söz etmiyor |
| **Named Cloudflare Tunnel** | Cloudflare katkıcısına göre SSE çalışıyor | **[rapor]** [#1449](https://github.com/cloudflare/cloudflared/issues/1449) yorumu; hesap, alan adı ve Colab'da bir tünel token'ı ister |
| **localhost.run** (SSH tüneli) | SSE canlı güncellendi | **[rapor]** [la-sala-app #25](https://github.com/pbelaustegui/la-sala-app/pull/25) |
| **ngrok** | SSE'ye dair kayıt bulunamadı. Ücretsiz planda tarayıcı trafiğinin önüne bir uyarı sayfası koyuyor | **[doğrulandı]** uyarı sayfası: [ngrok free plan limits](https://ngrok.com/docs/pricing-limits/free-plan-limits/); SSE **bilinmiyor** |
| **Colab'ın port vekili** (`serve_kernel_port_as_window`) | Kullanılamaz: POST `500 (Not Allowed)` | **[rapor]** [colabtools #3925](https://github.com/googlecolab/colabtools/issues/3925), v4'te okundu |

## Düzeltme adayları, sıralı

Hepsinde turun kendisi, `LiveTurns` ve snapshot'ın biçimi aynı kalıyor; değişen yalnız ekranın turu
nasıl duyduğu. Hiçbiri diske gitmiyor (tur bellekte); fark, tünelden kaç istek geçtiği.

1. **Uzun yoklama, aynı kapıda.** `GET …/events?after=<sürüm>`: sunucu `changed_since(after, 15)` ile
   bekler ve **tek bir JSON snapshot döner** — değişiklik olunca hemen, olmazsa 15 sn sonra aynı
   sürümle. Ekran cevabı çizer ve hemen yenisini sorar; `{turn: null}` gelince durur. **Neden ilk:**
   belgelenmemiş hiçbir davranışa dayanmıyor — her cevap biten sıradan bir GET, tünel ne yaparsa
   yapsın. Sunucuda `changed_since` zaten var; `_listened`'ın döngüsü bir isteğe bir kareye iner.
   Snapshot zaten bütün hâli taşıyor, yani arada kaçan değişiklik yok (462'nin *"a listener that wakes
   after several changes lands where the turn is"* sözü). **Bedel:** değişiklik başına bir istek, boşta
   15 sn'de bir; bir değişiklikle ekran arasında bir tünel gidiş-dönüşü; disk 0. Kaybedilen: EventSource'un
   kendi yeniden bağlanması — bunu döngü yapar, ve `gaveUp`'ın 502/524 yolu sade bir `fetch` hatasına
   döner (EventSource'un saklayıp `reach` ile ayrıca sorulan sebebi artık cevabın kendisinde).
   **[çıkarım]**
2. **POST + `fetch` okuyucusu, 462'den önceki gibi.** Kapı POST'u da kabul eder, ekran akışı
   `response.body.getReader()` ile okur. Sunucu tarafı en küçük değişiklik; kareler ve beat aynen kalır.
   **Neden ikinci:** Quick Tunnel'da canlı aktığı yalnız gözlem — Cloudflare'in belgesi SSE'yi hiç
   desteklemediğini söylüyor ve Flavio *"it can change on Cloudflare's side without notice"* diyor.
   Yeniden bağlanmayı EventSource yerine kod yazar; okunan bir şey için POST kullanılır. **Bedel:** tur
   başına bir uzun istek, değişiklik başına sıfır ek istek. **[rapor + çıkarım]**
3. **Kısa yoklama.** Ekran tur sürerken `GET …/chats/<id>`'i (tur sürerken diske gitmiyor, 461) 1–2 sn'de
   bir okur; sunucuda hiç değişiklik yok. **Neden üçüncü:** her yoklamada sohbetin bütün kaydı tünelden
   geçer, değişiklik olsun olmasın; değişiklik ile ekran arasında yarım aralık gecikme. **Bedel:** tur
   süresi / aralık kadar istek, her biri bütün sohbet. **[çıkarım]**
4. **Named tunnel.** Kod değişmez, defter değişir: Cloudflare hesabı, kullanıcının alan adı, Colab
   Secrets'ta bir tünel token'ı. Linkin sabit kalması da gelir. **Neden dördüncü:** SSE'nin orada çalıştığı
   bir Cloudflare katkıcısının yorumu, belge değil; kurulum kullanıcının işi ve bizde denenmedi.
   **[rapor]**
5. **WebSocket** ya da **başka bir tünel** (localhost.run, ngrok). WebSocket Flask'a ikinci bir bağımlılık
   ekler (defterin *"the app's only third-party dependency"* sözüne karşı); başka tünel defteri ve
   güvenlik uyarısını değiştirir, ngrok'ta SSE bilinmiyor. **[çıkarım]**

**Aday olmayanlar:** yeni başlıklar (`no-store`, `no-transform`, `X-Accel-Buffering` — #1449'da
vardı, işe yaramadı), dolgu (Quick Tunnel'da işe yaradığına dair kayıt yok), sıkıştırmayı kapatmak
(sıkıştırılan bir şey yok).

## Colab'da bakılacak yer — araştırma karar veremezse

Kayıtlar tutarlı ve görüleni açıklıyor, ama bizim tünelimizde ölçülmedi. Kullanıcı bakmak isterse,
**tur sürerken**:

1. QueenAgent'ın sekmesinde **F12 → Network**, filtreye `events` yaz, sohbette bir mesaj gönder.
2. Listede `events` isteğine tıkla → **EventStream** sekmesi. Bakılacak: satırların **Time** sütunu.
   - Satırlar tur boyunca birer birer, değişiklik oldukça beliriyorsa: tünel tutmuyor, sebep başka
     (o zaman ekran kodu yeniden açılır).
   - Tur sürerken liste boş kalıyor, tur bitince bütün satırlar aynı saniyede düşüyorsa: **tünel GET'i
     tutuyor** — bu araştırmanın sebebi.
3. Aynı isteğin **Timing** sekmesi: *Waiting (TTFB)* kısa, *Content Download* turun bütün süresi kadarsa
   ikinci hâl doğrulanır.
4. İsteğe bağlı, sunucuyu tünelsiz görmek için: Serve hücresi `tail -f`'le açık durduğu için yeni bir
   hücre sırada bekler. Ya Colab'ın Terminal'inden, ya da Serve hücresini durdurup (sunucu ve tünel
   arka planda sürer, hücre bunu yazar) yeni bir hücreden, tur sürerken:
   `!curl -sN http://127.0.0.1:8100/api/projects/<proje>/chats/<sohbet>/events` — kareler burada birer
   birer geliyorsa sunucu doğru, tutan tünel.
