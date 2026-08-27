# Madde 99 — Kapı çalıştırma anına iner · **uygulama turu**

**Tarih:** 2026-08-28 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [izin tasarımı](2026-08-28-queenagent-izin-tasarimi-design.md) — ve onun kaynağı
[v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Blok 6, Madde 99 ·
**Turun birincisi:** [test turu](2026-08-28-queenagent-m99-izin-testler-design.md) — otuz beş
kırmızı commit'lendi *(`27abf7f`)*.
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder.

---

## Yeni modül: `domain/permission.py`

Duraklamış bir turun parçaları: soru, nabız, karar, ve reddin modele giden cümlesi. Kendi
modülünde, `tools.py`'nin bir köşesinde değil — bunların hiçbiri bir aracın kendi işiyle ilgili
değil. Kapı aracın **önünde** açılıyor, ve araç kapıdan geçtiğini hiç öğrenmiyor.

`Decision` onay ile sebebi taşıyor. Onayın söyleyecek bir şeyi yok, o yüzden sebep varsayılan boş.

`refusal_text` üç şey söylüyor: ne reddedildi, reddin kipten geldiği, ve kullanıcı yazdıysa kendi
cümlesi. Üzerinde hiçbir şey yazmayan bir duvara model tekrar yürür.

## Kural: `domain/modes.py`

`tools_for` **gidiyor**, `needs_permission` geliyor. Liste hâlâ kural, ama bir adım sonra duruyor:
bütün araçlar isteğe giriyor, ve bu liste hangilerinin **sormadan** çalıştığını söylüyor.

İki eleme:

- **Kimsenin bilmediği kip** varsayılan gibi davranıyor — eski listenin sebebiyle aynı: kipi
  olmayan bir gövde ya da eski bir tarayıcı, kimsenin beklemediği bir soruyla karşılaşmasın.
- **Kimsenin bilmediği araç** hiç sorulmuyor. Cevap ne olursa olsun çalışmayacak, ve sormak
  kullanıcının önüne bu uygulamada olmayan bir ad koyup onaylatmak olurdu.

Modülün başlığı Madde 91'in cümlesini koruyor ve üstüne bugünü ekliyor: yetki zayıflamadı, yalnız
yeri değişti.

## Kayıt: `data/memory_permissions.py`

`MemoryStops`'un kardeşi, ve bilerek aynı biçim: bellekte, sohbet başına, iki iş parçacığından
birden okunuyor — biri cevabı akıtan, öteki kararı taşıyan. Kilit bu yüzden var.

Sohbet başına bir `threading.Event`. `wait` beklemeden **önce de** bakıyor: cevap çoktan
bırakılmış olabilir, ve yalnız sonradan bakan bir bekleyiş kararı elinde tutarken bir tur boyu
otururdu.

Karar **tüketiliyor.** Aynı turda ikinci bir soru sorulabilir, ve o soru bir sorudur — ilk cevabın
çoktan çözdüğü bir şey değil. Soruyu ayrıca açan bir çağrı olmamasının sebebi de bu: tüketme,
ikisini ayıran şeyin kendisi.

`wake` kararsız uyandırıyor. Duran tur bunu Stop'tan alıyor.

## Bekleyiş: `usecases/stream_answer.py`

`HEARTBEAT_SECONDS = 15`. **Bu bir zaman aşımı değil** — bekleyiş süresiz. Modelin bağlantısının
öteki ucunda bekleyen kimse yok: araç çağrısı turun son karesiyle geliyor ve o istek kapı
açılmadan çoktan kapanıyor. Sayının söylediği tek şey, hiçbir şey olmazken tarayıcının bizden ne
sıklıkla haber aldığı.

Bekleyiş kendi alt üreticisinde. Üretici olması gerekiyor çünkü nabzın, cevabın geldiği bağlantıdan
çıkması lazım. Geri verdiği şey karar, ya da kararsız biten bir bekleyişte hiçbir şey.

Duran tur `stops`'a **kesme yerine uyandırma** bırakıyor. Kesilecek soket yok — model isteği turla
birlikte kapandı — ve bu satır olmasa Stop düğmesi soru durduğu sürece hiçbir şey yapmazdı.
`hold` zaten *"tuşa daha önce basıldıysa hemen çalıştır"* yarışını taşıyor, ve burada da aynı yarış
var.

Tur döngüsünde **bir satır daha**: araç döngüsünden `cut_short` ile çıkıldığında tur döngüsü de
kırılıyor. Bugün `cut_short` ancak bir sonraki turun başında sorulduğu için, o satır olmadan
durdurulmuş bir tur modele bir istek daha gönderirdi.

## Kapı: `presentation/routes.py`

İki yeni kare. Soru `event: permission`, ve aracın adıyla **ham argümanlarını** taşıyor. Nabız
hiçbir olay satırı taşımıyor — tarayıcının ayrıştırıcısı onu bu yüzden düşürüyor, ve düşürmesi
zaten işin kendisi: o kare okunmak için değil, susmuş bir bağlantıda bayt olmak için var.

İzin kapısı durdurma kapısının kardeşi: kendi isteğinde, kendi bağlantısında, çünkü cevapladığı tur
hâlâ başka bir bağlantıdan akıyor. Sohbet yoksa 404. Onun dışında cevap boş — kararın ne ettiği bu
istekte değil, açtığı akışta görülüyor.

## Dokunulan yardımcılar

Test turunun bilerek bıraktığı iki yer burada kapanıyor: `test_stream_answer.py`'nin `_run`'ı
`_gated`'e devrediyor, ve iki API dosyasının `_client`'ları kurucuya izin kaydını da veriyor. Bu
turda **yeni test yazılmıyor**; değişen yalnız var olan testlerin ortak kurulumu.

## Dokunulmayan

| Ne | Neden |
|---|---|
| `run_tool` ve araçların kendisi | Kapı önlerinde açılıyor, içlerinde değil |
| `MemoryStops` | Uyandırma bugünkü `hold`'una veriliyor; sınıf değişmiyor |
| `ends_the_turn` | Kural yerinde. Onaydan sonra kip edit olduğu için o turda işlemiyor, ve doğrusu bu: kullanıcı *"yaz"* demiştir |
| Ön yüz | Kart **Madde 102**'nin işi; `dist` derlenmiyor |
| Yönerge metinleri | Yetkiye dair bir cümle girmiyor *(Madde 91)* |

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
```

Otuz beş kırmızı yeşile döner. **İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.
