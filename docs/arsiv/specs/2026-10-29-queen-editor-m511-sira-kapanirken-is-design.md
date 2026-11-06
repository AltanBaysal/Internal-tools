# Madde 511 · Sıra kapanırken eklenen iş de başlar — tasarım

**Tarih:** 29 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-10),
511 · v11-10 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Kurallar:** queen-editor
[FOUNDATION](../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

[518](2026-10-30-queen-editor-m518-acik-sayfa-isi-gorur-design.md) bu bekçiyi `features/queue_watch/` (`QueueWatch`, `GET /api/queue/watch`) olarak genişletti.

## Kabul koşulu (maddeden)

- Kuyruğa ne zaman bir iş eklenirse eklensin, sıra kapanırken eklense bile, o iş başlıyor; hiçbir iş
  sırada başlamadan kalmıyor.
- İş varken "Sıradaki bütün fotoğraf ve videolar bitti." bildirimi gelmiyor.

Kararlar maddede yazılı: *"abi kesinlik lütfen düzeltelim"*; bildirim sıranın nasıl çalıştığını
etkilemez — *"bildirim tamamne ayrı bir şey sıra mantığın ıdeğiştiremez"*. Bu yüzden düzeltme sıranın
kendisinde (`run_queue`, `PhotoRunner` ve `make_job`'un başı); 509'un bildirim kodu (`ended`,
`features/queue_ended/`) değişmez ve sıraya hiçbir şey söylemez. Ekrandaki sürüm V11 kalır.

## Hata, görüldüğü gibi

Kuyruğa iş ekleyen her kapı (`start_batch`, `queue_layer`, `regenerate`, `queue_references`,
`retry_frame`, `retry_failed`, ajanın `fix_photo`'su) önce kuyruğu yazar (plan, kayıt ya da sıra),
sonra `run_queue`'yu çağırır; `resume_batch` hiçbir şey yazmadan yalnız onu çağırır. Kuyruğa iş
ekleyen başka bir kapı yok: `copy_frames` iş planlamaz, `save_order` yalnız sırayı değiştirir, silme
ve temizleme iş eksiltir. `run_queue` işçi aynı projede çalışıyorsa hiçbir şey yapmadan dönüyordu
(*"the live loop will reach the new jobs by itself"*). Ama döngü son turunda olabilir:

1. döngü (`run_loop.make_job`) planı okur, borçlu iş bulmaz;
2. **bu arada** Kuyruğa ekle yeni işi plana yazar, `run_queue` işçiyi "çalışıyor" görür ve döner;
3. döngü `summary("done")` ile döner (planı bir daha okur, ama artık karar verilmiştir);
4. `PhotoRunner._run` `done`'ı yayımlar ve 509'dan beri bildirimi çaldırır.

Yeni iş borçlu kalır, işçi boştadır, kimse onu başlatmaz. Drive'da 1 ile 4 arası birkaç saniye (üç
okuma `snapshot`'ta, üçü `summary`'de). Hata 509'dan eski; 509 yalnız ona yanlış bir bildirim ekledi.

Test önce kırmızı görüldü (`test_a_job_queued_as_the_queue_closes_still_starts`): "ilk" işlenir,
döngünün boş bulduğu okumanın hemen ardından "ikinci" kuyruğa eklenir; eski kodda üretilen yalnız
`['ilk']`, "ikinci" borçlu kalıyor.

**Aynı yerde iki pencere daha** (reviewer'ın okumasından): `run_queue` önce `status()`'a bakıp sonra
`make_job` ve `start` çağırıyordu, ve bakmakla almak arasında başka bir basış işçiyi alabiliyordu:

- **Aynı projenin iki basışı, işçi boştayken:** ikisi de boş görür, biri alır, öteki `start`'ı
  kaybeder ve "Zaten bir üretim sürüyor." der; oysa işi kazananın koşusu yapacaktır.
- **Başka bir projenin basışı:** boş görülür, başka proje işçiyi alır, ardından `make_job`'un
  `named.took(project)`'u o projenin **koşan** döngüsünün okuduğu adı bu projeye çevirir. O döngü adı
  her turda okur (`named.now()`), yani sonraki turdan itibaren yanlış projenin kuyruğunu okur ve
  Drive'da yanlış klasöre yazar. Basışımız `Busy` alır, ama zarar verilmiştir.

İkisi de testle kırmızı görüldü (`Overtaken`: `status()` cevap verdikten sonra, `start()`
çalışmadan önce öteki basışı içeri alan işçi).

**Ve bir isim:** `_run` bitişi koşunun başındaki proje adıyla yayımlıyordu; koşu sürerken proje yeniden
adlandırıldıysa bitiş eski adla çıkıyordu. Ekran (`useGeneration.js`) koşunun kendisine ait olduğunu
bu adı sayfanın adıyla karşılaştırarak anlar. Testle kırmızı görüldü.

## Ne yapılır

**`PhotoRunner.start(project, job)`** — işçinin kilidinde tek adım:

| İşçi | Ne olur | Döner |
|---|---|---|
| başka projeyi çalıştırıyor | hiçbir şey | `False` |
| bu projeyi çalıştırıyor | `_joined` kalkar (katılım); `job` kullanılmaz, durdurma isteği olduğu gibi kalır | `True` |
| boşta | işçi alınır, `_stop` iner; kilitten sonra `named.took(project)` ve `spawn` | `True` |

Adın tutucusunu (`RunningName`) yalnız bu alış, ve yalnız alışı kazanan basış yönlendirir. Kilidin
dışında, çünkü alış zaten tek kişilik: kazanandan başka kimse o noktaya varmaz. İçeride olsaydı,
işçinin kilidi tutucunun kilidini, o da bir yeniden adlandırmanın Drive'daki klasör taşımasını
bekleyebilirdi — o sürede `/api/status`, Durdur, temizleme ve her başka basış dururdu. `_joined` alışta indirilmez, çünkü hiç
çalışmayan bir işçide kalkık olamaz: koşu bitişini ancak bayrak inikken yayımlar ve yalnız koşan
işçiye katılınır.

**`PhotoRunner._run` ve `_finish(summary)`** — her geçiş (`job()` çağrısı) bitince, ne ile bittiyse,
`_finish` kilitte bayrağa bakar: kalkıksa indirir, hiçbir şey yayımlamaz ve iş bir daha çalışır;
inikse durumu yazar ve döner. Durum, projenin **o anki** adıyla damgalanır
(`self._state["project"]`, `rename`'in tuttuğu ad). `ended` eskisi gibi döngüden sonra, kilidin
dışında ve yalnız yayımlanan durumla çağrılır.

**`make_job`** — `named` verilmezse işçinin tutucusunu kullanır, ama artık onu **yönlendirmez**
(`took` çağırmaz): iş alış kazanılmadan önce kurulur, ve yönlendirme başka projenin koşusunu taşırdı.
Projenin adını yalnız tutucudan okuduğu için `project` parametresi gider; `run_queue` adı `start`'a
verir. İşi kendisi çalıştıran testler adı içinde bir `RunningName("düğün")` verir.

**`run_queue`** — `job = make_job(...)`, sonra `if not runner.start(project, job): raise Busy(...)`.
`status()` ön bakışı ve `join` yok. İş, basış yalnız katılsa da kurulur: bir kapanıştır, kurulurken
hiçbir şey okumaz.

Döngünün turlarına (`run_loop`'un içi) dokunulmaz.

### Neden her bitiş

Bir basış ne zaman gelirse gelsin aynı şeyi demeli (*"ne zaman eklenirse eklensin"*). Koşuya katılan
basışa, koşu bittikten hemen sonra gelmiş bir basışa verilecek cevap verilir — döngü bir daha döner ve
bulduğunu söyler:

- `done`: yeni iş varsa yapılır; yoksa `done` yine, bir kez.
- `paused`: durdurma isteği katılımda inmez, döngü ilk adımında onu görür ve yine `paused` döner. (Boş
  bir işçiye gelen basış `_stop`'u indirir ve sırayı başlatır; katılan basış ise Durdur'dan önce ya da
  sonra gelmiş olsun, Durdur'u geçersiz kılmaz.)
- `error`: döngü baştan, üç taze denemeyle — bitişten hemen sonra basılmış gibi.
- `waiting`: üretici hâlâ yoksa yine `waiting`.

## Neden hiçbir iş kaybolmaz

Bir kuyruk basışı iki adımdır: **Y** (kuyruğu Drive'a yazar) ve ondan sonra **A** (`start`, kilitte).
İşçinin her geçişi **B** anında başlar — ilk geçiş için boş işçiyi alan bir A, sonrakiler için
reddedilen bir yayımlama; ikisi de kilitte bayrağı inik bırakır — ve kuyruğu B'den sonra okur. Geçiş
bitince işçi **S** anında, kilitte, bayrağa bakar. Bütün A'lar, B'ler ve S'ler aynı kilitte olduğu
için sıraları kesindir. Bir basışın A'sı:

- **İşçi boşken:** işçiyi kendisi alır; bu A, yeni koşunun B'sidir ve geçiş Y'den sonra okur.
- **Bu projenin bir geçişinin B'si ile S'si arasında:** bayrağı kaldırır; S yayımlamaz, yeni bir
  geçiş başlar (yeni B, A'dan ve Y'den sonra) ve işi görür.
- **Başka projenin koşusu sürerken:** `False`, basış `Busy` alır; iş kuyrukta kalır ve o projenin bir
  sonraki basışı onu başlatır (bugünkü gibi). Hiçbir yönlendirme olmadığı için koşan döngü kendi
  klasöründe kalır.

A'nın B'den önce, S'den sonra ve "aralarında" dışında bir yeri yok: işçi ya boştur ya bir geçiş
sürüyordur, ve geçişler arasındaki tek an S ile onun hemen ardından gelen B'dir, ikisi aynı kilit
tutuşunda. Yani her basış ya işçiyi alır ya Y'den sonra okuyacak bir geçişe katılır. Bitiş yalnız S'de
ve bayrak inikken yayımlanır: o geçiş B'den sonra başladı ve ondan önceki her basışın işini gördü,
sonra katılan olmadı. Bildirim yalnız yayımlanan durumu duyduğu için borçlu iş varken "bitti" çalmaz.

Aynı projenin iki basışı aynı anda: ikisinin de A'sı kilitte sırayla olur; ilki işçiyi alır, ikincisi
katılır. Yanlış `Busy` yok.

## Maliyet

- **Kuyruk basışı:** bir `start` (bellek, tek kilit) ve bir `make_job` kapanışı (bellek). `status()`
  ön bakışı gider. Drive'a ek okuma ya da yazma yok, proje, kare ve dosya sayısından bağımsız: O(1).
- **Döngünün turu:** değişmez; bayrağa tur başına bakılmaz.
- **Koşunun sonu:** koşu sürerken en az bir basış katıldıysa koşu bir geçiş daha döner. `done` ile
  biten koşuda bu, reddedilen özetin boşa giden üç okuması (plan, kayıt, sıra) ve yeni geçişin borç
  bulmayan turu ile özeti, altı okuma; `paused` ve `waiting`'de de birkaç okuma. Koşu başına bir kez
  (arada yeni bir basış katılmadıkça), kare sayısından bağımsız; Drive'da birkaç saniye. `error`'da ek
  geçiş üç yeni deneme demek — bitişten hemen sonra basılmış gibi. Hiç katılım olmayan koşunun
  maliyeti aynı.

## Ne kaybolabilir, ne bozulabilir

- Hiçbir şey yazılmaz; bayrak bellekte yaşar. Sunucu ölürse koşu da ölür; işler planda ve kayıtta
  borçlu kalır ve sonraki basış onları başlatır (bugünkü gibi).
- Başka projenin koşusu artık hiçbir basışla yönlendirilemez: tutucuyu yalnız işçiyi alışı kazanan
  basış yönlendirir.
- İşçinin kilidi tutulurken ne disk ne istek var, ve o kilit içinde başka bir kilit alınmaz.
- `ended()` eskisi gibi kilidin dışında, yayımlamadan sonra; `TOLD` aynı.

## Sınırlar

- Ek geçiş sürerken ekran birkaç saniye daha "çalışıyor" görür, son işin ilerlemesiyle; yeni iş
  varsa ilk turu yeni ilerlemeyi yazar.
- Durdur'a basılmış bir koşuya katılan iş başlamaz: koşu `paused` biter, iş sonraki Devam'ı bekler.
- Başka projenin koşusu sürerken eklenen iş eskisi gibi `Busy` alır ve kuyrukta bekler.
- Aynı projeye aynı anda bir basış ve bir yeniden adlandırma gelirse iş yine bekleyebilir: basış işi
  eski ada yazar, yeniden adlandırma klasörü taşır, basış işçiyi eski adla alır ve koşu var olmayan
  klasörü okuyup biter. İki sekme ya da yeniden adlandırma sürerken basan ajan gerekir; düzeltmesi
  işçiyi almakla yeniden adlandırmanın adı kimin tuttuğunda anlaşmasını ister. Bu madde dokunmuyor:
  [BACKLOG](../../queen-editor/BACKLOG.md), *"Aynı anda gelen kuyruk basışı ve yeniden adlandırma bir
  işi bekletebilir"*.

## Ne zaman bitti

- Döngünün boş bulduğu okumanın hemen ardından kuyruğa eklenen iş aynı koşuda üretiliyor; borçlu iş
  kalmıyor; ikinci bir işçi başlamıyor; bitiş bir kez, `done` ile ve iş bittikten sonra söyleniyor.
- `start`: başka projenin koşusunda `False`; bu projenin koşusunda `True` ve ikinci bir `spawn` yok;
  tutucu alan projede kalıyor.
- Aynı projenin öteki basışı, bu basışın bakmasıyla alması arasında işçiyi alırsa bu basış katılıyor,
  `Busy` almıyor.
- Başka projenin basışı o arada işçiyi alırsa bu basış `Busy` alıyor ve tutucu o projede kalıyor.
- Katılım olan koşu, `done`, `paused`, `error` ve `waiting`'in her birinde bir geçiş daha dönüyor;
  katılım Durdur'u indirmiyor.
- Sürerken yeniden adlandırılan koşunun bitişi yeni adla yayımlanıyor ve söyleniyor.
- `make_job`'u kendisi çalıştıran testler `named=RunningName(...)` veriyor.
- `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend` yeşil. Ekran
  değişmediği için `dist` yeniden kurulmaz.

## Yalnız Colab'da görülecek

- Gerçek bir sıranın son işi biterken Kuyruğa ekle'ye basılınca yeni işin başlaması ve "bitti"
  bildiriminin ancak o da bitince gelmesi.
