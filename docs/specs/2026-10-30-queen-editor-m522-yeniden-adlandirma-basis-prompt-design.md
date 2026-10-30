# Madde 522 · Yeniden adlandırma bir basışı ya da prompt'u kaybettirmez — tasarım

**Tarih:** 30 Ekim 2026 · **Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-21),
522 · v11-21 (yama v11.1) · **Dal:** `feat/queen-editor-v11.1` · **Plan:**
[2026-10-30-queen-editor-m522-yeniden-adlandirma-basis-prompt-plan.md](../plans/2026-10-30-queen-editor-m522-yeniden-adlandirma-basis-prompt-plan.md)
· **Kurallar:** queen-editor [FOUNDATION](../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../queen-editor/CODE-STANDARD.md)

## Kabul koşulu (maddeden)

Proje yeniden adlandırılırken aynı anda Kuyruğa ekle'ye basılsa da iş başlıyor; sıra çalışırken
adlandırma hiçbir videoyu boş prompt'la ürettirmiyor.

Kullanıcı — *"bu hatalarıda çöz istersen"*. BACKLOG'un iki işi: *"Aynı anda gelen kuyruk basışı ve
yeniden adlandırma bir işi bekletebilir"* (511'in reviewer'ı) ve *"Yeniden adlandırma bir videoyu boş
prompt'la ürettirebilir"* (513'ün coder'ı). İkisi de bu yamadan eski. Ekran değişmez; `dist` derlenmez.

Seçenekler (aşağıda) ana ajana soruldu; reviewer'ın da onayıyla 1. seçenek seçildi.

## Hata, görüldüğü gibi

Testler gerçek bir geçici klasörde (`Storage`, `DrivePlanStore`, `DrivePhotoRecord`), yeniden
adlandırmayı tam o ana sokarak yazıldı: ad klasörün kendisi olduğu için, adı yok sayan sahte depolar
hatayı gösteremez. Eski kodda (`test_rename_under_queue.py`):

**1. Basış ile yeniden adlandırma.** Kuyruğa iş koyan her kapı işini projenin yazma kapısında
(`plan_store.held`, 512) yazar, sonra kapının **dışında** `run_queue` ile işçiyi alır ya da çalışan
koşuya katılır (511). Yeniden adlandırma o kapıyı hiç almaz. Taşıma bu ikisinin arasına düşebilir:

- **İşçi boştayken:** basış işi `düğün`'e yazar; yeniden adlandırma klasörü `nişan`'a taşır (adın
  tutucusu `düğün`'ü tutmadığı için yönlendirilmez); basış işçiyi `düğün` adıyla alır ve tutucuyu
  `düğün`'e çevirir; koşu var olmayan `düğün`'ü okur, borç bulmaz, `done` der. İş `nişan`'da borçlu
  kalır, kimse başlatmaz. Kırmızı: `generator.calls == []` (beklenen `['ilk']`).
- **Projenin koşusu sürerken** (bu madde buldu): taşıma koşuyu `nişan`'a götürür; basış ardından
  `start('düğün')` ile gelir, işçinin projesi `nişan` olduğu için `Busy` — *"Zaten bir üretim
  sürüyor."* İşi koşunun kendi kuyruğundadır, ama koşu son bakışını yapmış olabilir (511'in durumu) ve
  basış katılamadığı için bir geçiş daha dönmez. Kırmızı: `Busy`.

Taşıma bir kapının kendi yazmaları arasına da düşebiliyordu: `queue_layer`'ın `record.mark(QUEUED)`'u
`düğün`'e iner, `plan_store.append`'i taşınan klasörde düşer — kayıtta "sırada", planda işi yok.

**2. Turun okumaları ile yeniden adlandırma.** 513 turun ilk üç okumasını (plan, kayıt, sıra) adın
kapısında (`named.steady()`) tek adla okudu. Turun sonraki okumaları — altındaki fotoğraf
(`_source_for`), bitiş resmi (`_end_for`), karenin sözleri (`record.prompts`), yazılmış prompt
(`written_prompts`), referans havuzu — o adla ama kapının **dışında** yapılıyordu:

- Fotoğraf okunduktan sonra taşıma: `written_prompts('düğün')` boş gelir, video `''` prompt'la üretilip
  `nişan`'a yazılır. Kırmızı: `[''] == ['kız yavaşça dönüyor']`.
- Yazarın yolunda aynı an: `_prompts_of('düğün')` boş gelir, model hiç söz olmadan prompt yazmaya
  çağrılır (uydurulmuş bir prompt). Kırmızı: `[{}] == [{'photo': 'kız yürüyor'}]`.
- `_unwritten`'ın iki okuması arasında taşıma: yazılmış prompt eksik okunur, model yeniden çağrılır.
  Bugün bu gizli kalıyor — ardından gelen fotoğraf okuması da eski adda düşer ve deneme baştan alınır —
  ama sonraki okumalar şimdiki adı çözünce açığa çıkardı. Bu yüzden onun da testi var (bugün yeşil).

## Ne yapılır

### Yeniden adlandırma projenin yazma kapısını alır; kapılar işçiyi kapıda alır

- **`follow_rename(runner, plan_store, old, new, move)`** — taşımayı ve tutucunun, damganın
  yönlendirilmesini `plan_store.held(old)` içinde yapar. `main.py`'deki `partial` `_plan_store`'u da
  verir. Projeler özelliği hiçbir şey bilmez: `move` portu aynı.
- **Kuyruğa iş koyan sekiz kapı** işini yazar, işçiyi alır ya da koşuya katılır ve tutucuyu yönlendirir —
  hepsini aynı kapı tutuşunda:
  - `start_batch`, `queue_layer`, `regenerate`, `queue_references`, `fix_photo`: `run_queue` çağrısı
    kendi `with plan_store.held(project)` bloğunun içine girer;
  - `retry_frame`, `retry_failed`, `resume_batch` (bugün kapısız): projenin varlığına bakıştan işçinin
    alınışına kadar her şey kapıya girer.
  - Projenin varlığına bakan her kapı (`start_batch`, `queue_references`, `retry_*`, `resume_batch`)
    bakışı kapının içinde yapar, çünkü taşımanın hangi yanında olduğu ancak orada kesindir: bakış ile
    kapı arasına düşen bir taşıma, basışı "Proje yok" yerine plan dosyasını yazamayan işletim
    sisteminin cümlesiyle düşürüyordu (reviewer). `queue_references` havuzun boş olup olmadığına da
    kapının içinde, varlık bakışından sonra bakar; böylece eski sekmenin basışı her kapıda aynı cevabı
    alır.
- `run_queue`'nun kendisi değişmez; docstring'i kapının içinde çağrıldığını ve nedenini söyler.

### Turun okumaları da adın kapısında

`make_job`'un turu iki tutuşta okur, ikisi de adı tutuşun başında çözer ve yalnız içinde kullanır:

1. **Birinci tutuş:** `snapshot(project)` (plan, kayıt, sıra) ve `_unwritten` (sözler, yazılmış
   prompt'lar). `snapshot` artık adı kendisi almaz, tutuştaki adla okur; `summary` kendi tutuşunu alır.
2. **İkinci tutuş**, `try`'ın içinde: `_source_for`, `_end_for`, yazarın yolunda `_prompts_of`, render'ın
   yolunda yazılmış prompt ve referans havuzu.

Yazarın çağrısı (DeepSeek) ve render hiçbir kilitte değil. `runner.report(...)` iki tutuşun da dışında:
ilerleme raporu birinci tutuştan sonra, `startedAt` raporu ikinci tutuştan sonra. `MissingSource` ve
`MissingEndFrame` eskisi gibi `try`'ın içinde atılır ve deneme sayılır.

### Ters çevrilen iki karar

- **512:** *"`run_queue` kilidin dışında kalır: işçiyi almak bellekte bir adımdır (511) ve tutmaya
  ihtiyacı yoktur; dışarıda olunca kilidin içinde başka bir kilit (işçinin kilidi) alınmaz."* Gerekçe
  artık tutmuyor: işçinin alınışı, işin yazıldığı klasörle aynı taşıma tarafında olmalı, ve bunu ancak
  yazmayı ve alışı aynı kapıda tutmak sağlar. Kapının içinde alınan işçi kilidi bir yaprak: içinde hiçbir
  kilit alınmaz, tutulurken ne disk ne istek var — kilit grafiğinde döngü açamaz.
- **513:** *"yazma kapısını tutan kapılar adın kilidini almaz."* Artık alır: işçiyi alan basış tutucuyu
  (`named.took`) kapının içinde yönlendirir. Gerekçesi kilitlenme korkusuydu; aşağıdaki sıra bunun
  olmadığını gösterir, çünkü adın kilidini tutan hiç kimse yazma kapısını almaz.

### Neden yalnız bu

- *`start` var olmayan bir adı reddetsin:* tek dosya, ama basış "Proje yok" alırken işi `nişan`'da
  borçlu kalır — maddenin "iş başlıyor"u olmaz.
- *`RunningName` bir ad geçmişi tutsun, `start` `düğün`'ü `nişan`'a çevirsin:* eski adla yeni bir proje
  açılınca yanlış klasöre yönlendirir, ve bir kaydın ne zaman unutulacağını söyleyen bir şey yok.

## Neden hiçbir iş kaybolmaz

Bir basışın kapı tutuşu **K** (işi yazar, işçiyi alır ya da katılır, tutucuyu yönlendirir), yeniden
adlandırmanın kapı tutuşu **T** (taşır, tutucuyu ve damgayı yönlendirir). İkisi `düğün`'ün aynı
kilidinde, yani biri ötekinden tamamen önce olur:

- **K, T'den önce:** iş `düğün`'de, işçi `düğün` için alınmış ya da `düğün`'ün koşusuna katılınmış,
  tutucu `düğün`'ü tutuyor. T ardından klasörü taşır; `moved` tutucu `düğün`'ü tuttuğu için onu
  `nişan`'a çevirir, `runner.rename` damgayı çevirir. Koşunun her turu adı tutucudan çözdüğü için
  `nişan`'da işi bulur. 511'in kanıtı aynen geçer: basış ya işçiyi aldı ya işi sonra okuyacak bir geçişe
  katıldı.
- **T, K'den önce:** K `düğün`'e geldiğinde klasör yok. Kapı projeyi bulamaz (`ProjectMissing` —
  *"Proje yok: düğün"*, ya da yazması klasörü bulamayıp `FileNotFoundError` olur), hiçbir şey yazmaz,
  işçiyi almaz. Borçlu kalan iş yok; ekran gerçeği söyler.

Bir kapının yazmaları arasına da taşıma düşmez: hepsi K'nin içinde.

## Neden hiçbir prompt boşalmaz

Taşıma (`RunningName.moved`) adın kilidinde ve klasörü bütün olarak, tek bir `os.rename` ile taşır.
Turun her tutuşu adı kendi başında çözer ve okumalarını yalnız içinde yapar; yani bir tutuşun bütün
okumaları taşımanın aynı yanında, aynı klasörden. Bir tutuşun okuduğu şey, klasör sonra taşınsa da yeni
adıyla aynı içeriktir — bu yüzden iki tutuş farklı adları çözse de birbirine yalan söylemez: birinci
tutuşun `slots`'u ikinci tutuşta `nişan` diye okunan klasör için de doğrudur. Fotoğraf ile yazılmış
prompt artık aynı tutuşta okunur: ikisi de ya `düğün`'den ya `nişan`'dan, ikisi de dolu. Yazarın
gördüğü sözler aynı tutuşta okunduğu için hiç boş gelmez; `_unwritten`'ın iki okuması da aynı tutuşta.
Turun yazmaları zaten 513'ten beri kendi tutuşlarında.

## Kilitler

Dört kilit: projenin yazma kapısı **G** (`plan_store.held`, proje başına), adın kilidi **N**
(`RunningName`), işçinin kilidi **R** (`PhotoRunner._lock`), ve yapraklar (`QueueWatch`, kayıt).

| Kim | Sıra |
|---|---|
| Kuyruğa iş koyan kapı | G → R (bırakılır) → N (`took`, bırakılır) → `QueueWatch.started` |
| Yeniden adlandırma | G(eski) → N (`moved`, içinde taşıma) → bırakılır → R (`rename`) |
| Döngü | N (tutuşlar); R ayrı, N'nin içinde değil; G hiç |
| İşçiyi alan başka proje | R → bırakılır → N |

Kenarlar G→R, G→N; R ve N hiç iç içe değil; N'yi tutan hiç kimse G'yi almaz; iki G hiç iç içe alınmaz
(yeniden adlandırma yalnız eski adınkini alır). Döngü yok, kilitlenme yok.

**GPU hiçbir kapıyı beklemez:** döngü G'yi hiç almaz. N'yi döngüden başka yalnız yeniden adlandırma ve
boş işçiyi alan basışın `took`'u ister; döngü en çok bir klasör taşımasını bekler (bugün de öyle).

## Maliyet

- **Basış başına:** Drive'a ek okuma ya da yazma yok; kapılar eskisi kadar okuyup yazar. Kapı tutuşu
  işçinin alınışını da kapsar: bellekte bir kilit ve, işçi boşsa, N'nin kısa tutuşu. `retry_*` ve
  `resume_batch` için bir kilit sözlüğü bakışı ve bir kilit alışı. Proje, kare ve dosya sayısından
  bağımsız: O(1).
- **Yeniden adlandırma:** Drive'a ek işlem yok. Aynı projeye o an süren bir basış varsa onun bitmesini
  bekler (o kapının okumaları ve yazmaları, Drive'da birkaç gidiş dönüş, birkaç saniye); o an bir tur
  ikinci tutuşundaysa onu da bekler (altındaki dosyanın okunuşu — bir fotoğraf ya da videonun baytları
  — ve kaydın okunuşu; referanslı bir işte havuzdaki N referans dosyası).
- **Basış, süren bir yeniden adlandırmayı** bekler: bir klasör taşıması.
- **Döngü:** okumaları aynı, sayısı aynı; yalnız ikinci grubu kilitte yapar. Yeniden adlandırma
  sürerken en çok bir taşımayı bekler.

## Ne kaybolabilir, ne bozulabilir

- Diskte hiçbir biçim değişmez; kilitler bellekte. Sunucu ölürse işler planda ve kayıtta borçlu kalır,
  sonraki basış başlatır (bugünkü gibi).
- Taşımadan sonra eski adla gelen bir yazma artık hayalet klasör açmaz: Drive'ın kapısı proje klasörünü
  hiç açmaz (472), yazma `FileNotFoundError` ile düşer. `running_name.py`'nin ve `run_loop.py`'nin
  "hayalet proje" yorumları bu yüzden yanlıştı; yeni doğru neden yazıldı: bir okuma ya da yazma, taşımanın
  götürmediği klasörü çözmeli.
- Testlerde `spawn` satır içinde çalıştığında (`sync_runner`) döngü basışın kapı tutuşunun içinde
  koşar; döngü G'yi almadığı ve kilit yeniden girilebilir olduğu için bir şey değişmez. Üretimde
  `spawn` bir iş parçacığı açar ve hemen döner.

## Sınırlar

- Yeniden adlandırmadan sonra eski sekmede basılan Kuyruğa ekle, Devam ya da Tekrar dene "Proje yok"
  alır; iş yazılmaz. Sayfa yeni adı yenileyince bilir.
- `resume_batch`'in T'den önceki bakışı da kapıda olduğu için, adlandırılmış bir projede eski adla Devam
  hiçbir koşu başlatmaz — eskiden boş klasörde bir `done` koşusu başlatabiliyordu.
- Proje silinirken gelen bir basış aynı türden bir pencere bırakıyor (`delete_project` kapıyı almaz);
  bu madde dokunmuyor, BACKLOG'a yazıldı: *"Proje silinirken gelen bir basış silinecek klasörde koşu
  başlatabilir"*.

## Ne zaman bitti

- İşçi boşken, işin yazılmasıyla işçinin alınması arasına sokulan yeniden adlandırma bekler; iş
  `nişan`'da üretilir, borç kalmaz, işçinin damgası `nişan`.
- Koşu sürerken aynı anda gelen basış `Busy` almaz, koşuya katılır; ikinci bir işçi başlamaz.
- Sekiz kapının her biri işçiyi kendi kapısını tutarken alır (`test_every_door_…`).
- Kapıyı almadan hemen önce sokulan yeniden adlandırmada `start_batch` `ProjectMissing` verir, işçiyi
  almaz, hiçbir şey yazmaz.
- Fotoğrafın okunmasından sonra sokulan yeniden adlandırma videoyu yazılmış prompt'la ürettirir;
  yazarın yolunda model karenin sözleriyle çağrılır; `_unwritten`'ın okumaları arasında sokulan
  yeniden adlandırma modeli bir daha çağırtmaz.
- 513'ün yeniden adlandırma testi yeni imzayla yeşil.
- BACKLOG'dan iki iş silindi, silme penceresi eklendi.
- `python -m pytest queen-editor -q` (bilerek kırmızı iki `test_notebook_clones_its_branch` testi
  dışında) ve `npm test --prefix queen-editor/frontend` yeşil.

## Yalnız Colab'da görülecek

- Gerçek Drive'da sıra bir video üretirken projeyi yeniden adlandırmak: videonun prompt'u kartta
  yazılı olan, dosya yeni klasörde.
- İki sekmede aynı anda Kuyruğa ekle ve yeniden adlandırma: iş yeni adla başlıyor, ya da basış "Proje
  yok" diyor ve hiçbir şey yazmıyor.
