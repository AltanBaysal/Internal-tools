# Madde 491 · Süren tur uzun yoklamayla — tasarım

**Tarih:** 22 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-20-queen-agent-v11-roadmap.md),
491 · v11-2, adım 3 · **Dal:** `feat/queenagent-v11` · **Araştırma:**
[m491 canlı akış](../research/2026-10-22-queen-agent-m491-canli-akis.md) · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md)

## Ne ve neden

Araştırmanın sonucu: Cloudflare Quick Tunnel, GET ile açılan bir akışın cevabını istek bitene kadar
tutuyor. Tarayıcı süren turu 462'den beri `EventSource` ile `GET …/events` üstünden dinliyor, ve
tünel kareleri turun sonuna kadar biriktirip birden veriyor: tur sürerken ekrana hiçbir şey gelmiyor,
F5'te o anki hâl geliyor, sonda cevap.

Kullanıcı araştırmanın birinci adayını, **aynı kapıda uzun yoklamayı** seçti, en sade hâliyle
*(22 Ekim — "doğrudan yap ama daha basit ve az engineering")*. Her cevap biten sıradan bir GET olur;
tünelin tutacağı açık bir akış kalmaz. Ekranda hiçbir şey değişmez.

## Bugün — koddan okunanlar

- **Kapı** — `routes.py`'nin `get_events`'i turu `turns.get` ile bulur ve
  `Response(_listened(live), mimetype="text/event-stream", headers=EVENT_HEADERS)` döner. `_listened`
  önce snapshot'ı, sonra her değişiklikte bütün snapshot'ı bir kare olarak yazar
  (`live.changed_since(version, BEAT_SECONDS)` ile bekleyerek), 15 sn sessizlikte `": beat"` satırı,
  tur bitince akış biter. Son kare `_told(snapshot)`: `{"turn": null}`, turun kendi kodu kırıldıysa
  `{"turn": null, "error": "<cümle>"}`. Tur yoksa tek kare `{"turn": null}`. `_frame`, `EVENT_HEADERS`
  ve beat yalnız bu akış için var.
- **`changed_since`** — `LiveTurn`'de; snapshot `version`'ı `after`'dan farklı olunca hemen, olmazsa
  `timeout` saniye sonra o anki snapshot'ı döner. `_turn_json` `version`'ı taşımıyor.
- **Ekran** — `useChat.js`'in `follow`'u her tur için bir `new EventSource(eventsOf(...))` açar ve
  `streams` haritasında tutar; `heard` her kareyi çizer, `{turn: null}` ya da başka bir turun kimliği
  `finished`'e gider, o da kaydı okur. Kopmayı EventSource kendisi onarır; vazgeçtiği (`CLOSED`) akış
  `gaveUp`'a gider: hiç söz söylememişse sohbet bir kez okunur, kapı `api.js`'in `reach`'iyle elle
  sorulur, bir kez daha açılır (`probed`), yine vazgeçilirse `GAVE_UP` kartı çıkar.
- **Testler** — backend'de `_listen`/`_chunks`/`_data`/`_heard` akışı okur; `test_last_activity.py` ve
  `test_pin_archive.py` turun bitişini akışı sonuna kadar okuyarak bekler. Frontend'de
  `test-setup.js`'in `FakeEventSource`'u; `useChat.test.jsx` ve `App.test.jsx` kareleri onunla
  söyletir; `api.test.js` `reach`'i dener.

## Ne değişir

### 1. Sunucu — `get_events` bir kez cevap verir

Aynı adres, aynı metot. Cevap JSON, ve istek biter:

- **Soru `turn=<kimlik>` ile süren turdan başka bir turu adlıyorsa ya da tur yoksa** → hemen, beklemeden:
  adlanan tur o sohbette en son biten tursa `{"turn": null}`, turun kendi kodu kırıldıysa `"error"`
  ile; değilse sohbetin şimdiki hâli — tur yoksa `{"turn": null}`, varsa süren turun snapshot'ı ve
  sürümü (ekran başka bir tur görünce kendi turunun bittiğini anlar). Başka bir turun sürümünü
  beklemek tarayıcıyı boşuna 15 sn tutardı.
- **`after` yoksa** → `{**_told(snapshot), "version": snapshot.version}`, hemen.
- **`after=<sürüm>` varsa** → `live.changed_since(after, ASK_WAIT_SECONDS)`; dönen snapshot aynı
  biçimde. Değişiklik olunca hemen, olmazsa 15 sn sonra aynı sürümle.

`after` `request.args.get("after", type=int)` ile okunur: sayı olmayan bir değer yok sayılır ve
cevap hemen gelir. `turn` yalnız bir kimlikle karşılaştırılır. İkisi de hiçbir yere yol olarak gitmez.

**`LiveTurns` biten turu tutar** *(reviewer'ın bulgusu, ana ajanın onayıyla mevcut kod değişti)*:
`release` sohbeti bıraktığı kilidin içinde turu bitirir ve sohbet başına son biten turun
`(kimlik, kendi hatasının cümlesi ya da "")` çiftini `_ended`'e yazar; sonraki biten tur üstüne yazar. Yeni `ended(p, c)` onu verir, `Turns` port'una
eklendi. Bırakma, bitirme ve tutma tek adımda: sohbeti boş bulan herkes biten turu da tutulmuş bulur.
Kilidin içinde turun kilidini almak güvenli — hiçbir tur `LiveTurns`'ün kilidini almaz. Bellek:
sohbet başına bir kimlik ve bir cümle, süreç boyunca.

Silinen: `_listened`, `_frame`, `EVENT_HEADERS`, beat satırı, `json` ve `Response` import'ları (başka
kullanan yok). `BEAT_SECONDS`'ın adı `ASK_WAIT_SECONDS` olur: beat yok, sayı bir sorunun ne kadar
bekleyebileceği. `_told` kalır.

### 2. Ekran — `useChat.js`'te bir döngü

`follow` bir `EventSource` yerine bir dinleyici kaydeder ve `ask`'i çağırır:

1. `getJson(…/events?turn=<kimlik>)` — `after`'sız ilk soru; sonrakiler `&after=<son sürüm>` ile.
2. Cevap `heard`'e gider, bugünkü gibi: tur yoksa ya da başka bir tursa `finished` (kaydı okur, sonu
   ve hatayı söyler); değilse çizer ve dosyayı duyurur.
3. Dinleyici hâlâ kayıtlıysa (`listeners` haritasında aynı nesne) yeniden sorar, `after=` cevabın
   sürümüyle.
4. **Bir hata** — ağ hatası, tünelin 502/524'ü, ne olursa — `AGAIN_MS = 3000` sonra aynı `after`'la
   yeniden sorar. 3 sn EventSource'un kendi yeniden bağlanma beklemesiydi. Kart yok; ekranda tur
   durduğu gibi kalır. Bir cevap sayacı sıfırlar.
5. **Üst üste ikinci hata** — sunucu kendiliğinden dönmüyor: dinleyici bırakılır. Sohbet ekrandaysa
   tur kalkar ve kart hatanın kendi cümlesini gösterir; kartın Try again'i retry kapısıdır, süren turu
   geri verir ve dinleme yeniden başlar. Ekran başka yerdeyse ve tur bu hook'unsa, sonu duyulmayacağı
   için turun sonundaki işler (`ended`) bir kez burada yapılır.

Dinleyicinin bırakılması (`letGo`) yalnız onu haritadan çıkarır: havadaki sorunun cevabı gelince
dinleyici kayıtlı olmadığı için hiçbir şey çizilmez ve yeniden sorulmaz; bekleyen bir yeniden deneme
de aynı yerden durur. `streams` adı `listeners` olur, çünkü artık akış yok.

Silinen: `EventSource`, `onerror`, `gaveUp`, `GAVE_UP`, `probed`, `heard` bayrağı, `api.js`'in `reach`'i
ve testi, `test-setup.js`'in `FakeEventSource`'u. Ekranda akış ve kare diyen yorumlar
(`FailureCard.jsx`, `ChatScreen.jsx`, `App.jsx`, `App.test.jsx`) bugünkü sözle yazıldı.

### 3. Belgeler

`CODE-STANDARD.md`, *Stack*: canlı ilerleme artık uzun yoklama — sebebiyle, Quick Tunnel'ın GET
akışını tutması.

## Bu maddenin kararları

1. **Cevabın biçimi** `{"turn": …, "version": n}`, turun kendi hatasında `"error"` da; tur yoksa
   yalnız `{"turn": null}`. Sürüm `_turn_json`'a girmez: o nesne beş cevapta ortak, ve sürüm yalnız bu
   kapının işi.
2. **İlk soru `after`'sız** — kapı turu ve sürümünü hemen verir. Mesajın 202'si ve sohbet okuması
   sürümü taşımaz; taşısın diye `_turn_json`'ı değiştirmek beş cevabı değiştirir.
3. **Hatalar sayılır:** bir hata 3 sn sonra yeniden sorulur; üst üste ikincisi turu bırakır ve kartı
   hatanın kendi cümlesiyle gösterir. Bugünkü kod da ikinci bir HTTP reddinde kart gösteriyordu
   (`gaveUp`: kapıyı elle sorup `reach`'in cümlesini, ya da `GAVE_UP`'ı); fark, artık cümlenin
   cevabın kendisinden gelmesi ve elle sorma yolunun gitmesi. Sayaç olmadan ölü bir sunucu bitmeyen
   bir bekleme gösterirdi.
4. **Biten tur adla sorulur:** her soru `turn=<kimlik>` taşır, ve `LiveTurns` sohbet başına son biten
   turu tutar — iki soru arasında biten turun kendi hatası kaybolmasın diye.
5. **Havadaki soru kesilmez** (`AbortController` yok): cevabı en geç 15 sn sonra gelir ve atılır.
6. **Yeni başlık yok** — uygulamanın öbür GET'leri gibi sıradan bir JSON cevabı; `Last-Modified`
   olmadan tarayıcı saklamaz, Cloudflare uzantısız bir yolu saklamaz.

## Maliyet

Koddan sayıldı, ölçülmedi. Disk: **0** — tur bellekte (461), kapı hiçbir şey okumaz. Hepsi proje,
sohbet ve dosya sayısından bağımsız, O(1).

| İşlem | Bugün (SSE) | Sonra (uzun yoklama) |
|---|---|---|
| Bir tur dinlemek, başta | 1 açık istek | 1 istek, hemen döner |
| Turda bir değişiklik | 0 yeni istek, 1 kare | 1 istek (cevap = snapshot, birkaç yüz bayt) |
| Sessiz tur, 15 sn'de | 1 beat satırı | 1 istek, aynı sürümle |
| Tur bitişi | son kare + kayıt okuması | son cevap + kayıt okuması |
| Hata | EventSource ~3 sn'de bir yeniden bağlanır | bir kez 3 sn sonra yeniden sorar; ikincisinde durur |
| Biten tur | — | sohbet başına bir kimlik ve bir cümle bellekte |
| Sunucu | dinleyici başına 1 iş parçacığı, tur boyunca | bekleyen soru başına 1 iş parçacığı, en çok 15 sn |

Değişiklikle ekran arasındaki gecikme bir tünel gidiş-dönüşü. Arka arkaya gelen değişiklikler
birleşir: soru dönüp yenisi gelene kadar olan her şey bir sonraki snapshot'ta, kaçan bir şey yok.

## Ne kaybolabilir, ne bozulabilir

- **İki soru arasında olan değişiklikler** — kaybolmaz: yeni soru `after` ile sorar, sürüm ilerlemişse
  hemen döner, ve snapshot bütün hâli taşır.
- **Tur iki soru arasında biterse** — sıradaki soru turu bulamaz; ama turu adıyla sorduğu için
  `LiveTurns`'ün tuttuğu biten tur cevaplar: `{turn: null}`, turun kendi kodu kırıldıysa cümlesiyle.
  Ekran kaydı okur ve cümleyi kartta gösterir. Kaybolmaz.
- **Tur biter ve yenisi aynı aralıkta başlarsa** — soru eski turu adladığı için beklemez: eski tur en
  son biten tursa sonu cümlesiyle, değilse yeni tur hemen gelir ve ekran eskisinin bittiğini anlar.
- **İki sekme** — her biri kendi sorusunu sorar; bir koşul ikisini birden uyandırır.
- **Sunucu yeniden başlarsa** — tur süreçle öldü (461), tutulan biten turlar da; soru düşer ya da
  `{turn: null}` alır, ekran kaydı okur ve soru cevapsız görünür.
- **Sunucu dönmezse** — iki hata üst üste: ekranda kart, cümlesiyle; Try again sunucu dönünce çalışır.
- **Ekran sohbetten ayrılırsa** — dinleyici bırakılır; havadaki sorunun cevabı en geç 15 sn sonra gelir
  ve atılır. O süre boyunca tarayıcıda bir bağlantı ve sunucuda bir iş parçacığı tutulur.
- **Quick Tunnel sınırları** — 200 eşzamanlı istek: sohbet başına en çok bir bekleyen soru. ~100 sn
  boşta kapanma: her soru en geç 15 sn'de biter.
- **Gizli bir şey** — yok: `after` bir sayı, cevap ekranın zaten okuduğu tur.

## Sınırlar

- Turun kendisi, `changed_since`, `_turn_json`, snapshot'ın biçimi, ve öbür kapılar değişmez;
  `LiveTurns`'te yalnız `release` ve yeni `ended`. Model servisinin kendi SSE okuması (`services/model`) bu maddenin değil.
- Ekranda hiçbir şey değişmez, yalnız turun nasıl duyulduğu. Kart, bugünkü gibi, takip edilemeyen bir
  turda çıkar; cümlesi artık hep kapının ya da ağın kendi sözü.
- Tünel açılmadı, Cloudflare'den deneme yapılmadı *(roadmap, adım 2'nin sözü)*.

## Bitti sayılır

1. Testler gösteriyor ki:
   - tur yokken kapı `{turn: null}` diyor ve biter; `after`'sız soru turu ve sürümünü hemen veriyor;
   - `after` ile soru değişiklikte o anki snapshot'ı ve yeni sürümü veriyor; sessiz turda
     `ASK_WAIT_SECONDS` sonra aynı sürümle dönüyor; sayı olmayan `after` hemen cevaplanıyor;
   - tur bitince `{turn: null}`, turun kendi kodu kırıldıysa cümlesiyle; ikisi de beklerken gelen bir
     değişikliği iki dinleyici aynı duyuyor;
   - tur bittikten sonra gelen ve onu adlayan soru cümleyi yine alıyor; başka bir turu adlayan ya da
     hiç adlamayan almıyor; sonraki biten tur öncekinin yerini alıyor; süren turdan başka bir turu
     adlayan soru beklemeden cevaplanıyor;
   - `release` turu, sohbeti bıraktıktan sonra ve `LiveTurns`'ün kilidi altında bitiriyor;
   - ekran ilk soruyu `?turn=` ile, sonrakileri son sürümle soruyor, her cevabı çiziyor,
     `{turn: null}` gelince sormayı bırakıp kaydı okuyor;
   - bir soru düşünce ekran kart göstermeden 3 sn sonra aynı sürümle yeniden soruyor; araya giren bir
     cevap sayacı sıfırlıyor; üst üste ikinci hatada ekrandaki sohbet kartı cümlesiyle gösteriyor ve
     Try again dinlemeyi geri getiriyor, ekran dışındaki kendi tur sonundaki işleri bir kez yapıyor;
   - ekran sohbetten ayrılınca havadaki sorunun cevabı çizilmiyor ve yeniden sorulmuyor; bu hook'un
     başlattığı tur ekran başka yerdeyken de sonuna kadar dinleniyor.
2. `EventSource`, `_listened`, `EVENT_HEADERS`, `reach`, `GAVE_UP` kodda yok; `dist` yeniden kuruldu.
3. İki satır yeşil: `python -m pytest queen-agent -q` ve `npm test --prefix queen-agent/frontend`.
4. **Colab denemesi — kullanıcının:** notebook'un açtığı trycloudflare adresinden, tur sürerken token
   sayısı ve araç çağrıları ekrana geldikçe görünüyor; F5 gerekmiyor. F12 → Network'te `events`
   istekleri birbiri ardına bitiyor.
