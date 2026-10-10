# Madde 460 · Modele giden isteğin süre sınırı — tasarım

**Tarih:** 10 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
460 · **Dal:** `feat/queenagent-v10`, ana klasörde · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Kaynak:** mimarın sohbet tasarımı, 1. adım ve 5. bölüm (`tmp/chat-turn-design.md`) · **Öncesi:**
[440](2026-10-09-queen-agent-m440-kara-kutu-design.md) — kara kutu ve denemeleri.

## Ne, neden

Bugün `client.py` isteği `urlopen(request)` ile, süresiz açıyor. Model hiç cevap vermezse — başlık
bile gelmezse, ya da başlıktan sonra susarsa — okuma sonsuza kadar bekler: tur, sunucu yeniden
başlayana kadar asılı kalır. Kara kutu bunu hiç görmez, çünkü deneme hiç bitmez.

**Olacak:** istek bir süre hiç ses gelmezse kesilir. Ölçülen sessizliktir, toplam süre değil; değer
`config.py`'de, `MODEL_IDLE_SECONDS = 180`. Kesilen deneme kara kutunun bir başarısız denemesidir;
beşi de kesilirse sohbetteki teknik hata kartı isteğin kendi sözünü yazar — soketin sözünü: gerçek
servislerin hepsinde olduğu gibi TLS üzerinden `The read operation timed out`, düz HTTP'de ve
bağlanırken `timed out`.

## Nasıl

- **`urlopen(request, timeout=...)`, tek satır.** urllib bu değeri sokete verir, soket de onu her
  beklemeye ayrı ayrı uygular: bağlanma, başlığın beklenmesi, akışın her okuması. Cevap 440'tan beri
  ekrana bütün gidiyor, ama `client.py` onu hâlâ SSE akışı olarak, satır satır okuyor
  (`for raw in response`, alttaki her `recv` ayrı bir bekleyiş). Yani sınır sessizliği ölçer: her
  bayt saati sıfırlar, ve konuşan bir cevap ne kadar uzarsa uzasın kesilmez. Ayrı bir zamanlayıcı ya
  da iş parçacığı gerekmiyor. Bu, bir varsayım değil, gerçek bir soketle test edildi: on kelime,
  aralarında 0,1 saniye, toplam süre sınırın üç katı — kesilmiyor.
- **Hangi hata çıkıyor:** başlıktan önceki de sonraki de sessizlik `TimeoutError` olarak çıkıyor (bir
  `OSError`); `client.py`'nin var olan `OSError` kolu onu `ModelFailed` yapıyor, soketin kendi
  sözüyle. O söz iki biçimde: TLS üzerinden (gerçek her servis) `The read operation timed out`, düz
  HTTP'de `timed out`; bağlanırken zaman aşımı da `timed out` der. Kart isteğin ne dediğini yazar;
  neden sustuğunu bu katman bilmiyor, söylemiyor. Kara kutu her `Exception`'ı bir başarısız deneme
  sayıyor (`black_box.ask`), dolayısıyla kara kutuda değişiklik yok.
- **Değerin yolu:** `config.py` → `main.py` → `ModelClient(..., idle_seconds)`. Servis `config`'i
  okumaz; anahtarı ve adresi gibi bu değeri de kompozisyon kökü verir. Parametre zorunlu:
  varsayılanı olsaydı, `config.py`'nin değerinin ikinci bir kopyası olurdu.
- **Stop:** `_cut` soketi kapatıyor, ama kesme `on_open`'a ancak `urlopen` döndükten sonra, yani
  başlık geldikten sonra ulaşıyor. Başlık gelmişse Stop bugünkü gibi hemen keser; soketin artık bir
  zaman aşımı olması bunu değiştirmiyor (`test_a_cut_wakes_a_read_that_is_blocked_on_the_socket` 30
  saniyelik sınırla kurulu bir istemciyle koşuyor ve 5 saniyede uyanmayı bekliyor). **Başlık
  beklenirken basılan Stop ise `MODEL_IDLE_SECONDS` içinde yerine ulaşır**: istek sınırda kesilir,
  kara kutu durdurulduğunu görür ve yeniden denemez. 460'tan önce o Stop hiç ulaşmıyordu. Bu boşluğu
  kapatmak istemcinin yapısını değiştirir; ayrı bir yol haritası maddesi olur.
- **Kontrol isteği** (445, `stream_alone`) aynı istemciden gidiyor, aynı sınırla.

## Maliyet

- Disk: hiç. Ağ: deneme başına bugünkü gibi bir istek; sınır yeni bir okuma ya da istek eklemiyor.
- Bir deneme, istek ve — sözle dönen cevapta — onun kontrolüdür (445); ikisi de ayrı ayrı sınıra
  tabi. Kara kutu bir `ask`'ta en çok 5 deneme yapar: hiç cevap vermeyen bir servisin en kötü
  maliyeti `ask` başına, yani döngünün her adımı başına 5 × 180 s ≈ 15 dakika (kontrol de susarsa
  daha fazla). Bir turun en kötüsü adım sayısı çarpı bu.

## Sınırlar

- **Her bayt ses sayılır**, servisin kuyruktayken gönderdiği keep-alive yorumları (`: keep-alive`) da.
  Durmadan keep-alive gönderip hiç cevap vermeyen bir servis kesilmez — madde sessizliği istiyor;
  böyle bir servisin kendi sınırı ne zaman keseceğini belirler.
- **İsteğin gönderilmesi** (`sendall`) Python'da toplam süreyle sınırlanıyor: istek gövdesinin 180
  saniyede gönderilmesi gerekiyor. Konuşma geçmişi bu boyda bir sorun değil.
- **DNS çözümlemesi sınırlı değil**, ve `create_connection` sınırı her adrese ayrı uyguluyor: IPv6 ve
  IPv4 adresi olan bir sunucuya bağlanmak 2 × 180 s sürebilir.
- 180 başlangıç değeri: uzun bir DeepSeek turu henüz ölçülmedi (tasarımın notu). Değişirse tek satır.
- Turun kendisi hâlâ onu başlatan HTTP isteği; tünelin ~100 sn'lik kesmesi 461'in işi.

## Testler

`test_model_client.py`'de, gerçek bir yerel soketle (sahte bir `opener` sokete ne olduğunu
söyleyemez); testlerde sınır 0,3 saniye. Sahte servis tek bir yardımcı, `_service`: her bağlantıya
sıradaki cevabı verir; Stop testlerinin eski `_silent_server`'ı onun `[HEAD]` cevabı oldu.

- Başlıktan önce susan istek ve başlıktan sonra susan akış: ikisi de `ModelFailed` ile bitiyor, düz
  soketin sözüyle `timed out` (değişiklikten önce: 5 saniyede bitmiyor, *"the request was never
  cut"*). Kartın gerçek serviste göstereceği söz bu değil, TLS'ninki; test bunu söylüyor.
- Konuşan uzun cevap kesilmiyor.
- Kesilen denemenin kara kutuda bir deneme sayılması ayrıca test edilmiyor: `test_black_box.py` her
  hatanın bir deneme olduğunu, bu testler sessizliğin `ModelFailed` fırlattığını tutuyor.
- Sahte `opener`'lı testler `_client`'ta bir adaptörle `timeout`'u yutuyor; sınır onlar için anlamsız.

## Bitti sayılır

Hiç cevap vermeyen bir model isteği sessizlik süresinden sonra kesiliyor ve kara kutu yeniden
deniyor; beşi de kesilince kart isteğin kendi sözünü yazıyor (TLS üzerinden `The read operation timed
out`); uzun ama konuşan bir cevap kesilmiyor; başlıktan sonra basılan Stop hemen, başlık beklenirken
basılan `MODEL_IDLE_SECONDS` içinde kesiyor; dört suite yeşil.
