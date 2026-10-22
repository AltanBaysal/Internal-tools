# QueenAgent — Yol Haritası v11

**Tarih:** 2026-10-20 · **Koşu dalı:** `feat/queenagent-v11` *(22 Ekim'de `feat/queen-editor-v10`'dan açıldı: bu yol haritası ve v10'un işi orada; v10 main'e birleşmeden)* · **Durum:** 2/5 · v11-1, v11-2 ve v11-4 hizalandı *(20 Ekim)*; v11-3 22 Ekim'de backlog'a döndü; v11-5 21 Ekim'de, v11-6 22 Ekim'de eklendi, hizalanacak; kullanıcının ekleyeceği maddeler bekleniyor *(20 Ekim — "bu quee nagetn eksik ben biraz daha madde kelicek bekle")*
**Öncesi:** [v10](2026-10-05-queen-agent-v10-roadmap.md) — 27/27 kapandı ve main'e birleşti.
**Kaynak:** Maddelerin hepsi kullanıcının 19 – 25 Ekim haftası için yazdığı plandan, 20 Ekim'de
verildi: v11-1 planın 10. maddesi, v11-2 12.'si, v11-3 13.'sü. Üçü de
[BACKLOG.md](../../queen-agent/BACKLOG.md)'den bir girdiyi içine aldı, ve girdiler oradan çıkarıldı:
v11-1 *"Bazı projeler kayboldu"*, v11-2 *"Süren tur ekranda canlı akmıyor, F5'le güncelleniyor"*,
v11-3 *"read_file geliştirilecek"*. Girdilerin sözleri, bilinenleri ve sorulacakları tablonun altında,
maddenin kendi başlığında. **v11-3 backlog'a döndü** *(kullanıcı, 22 Ekim — "backloga al")*:
[BACKLOG.md](../../queen-agent/BACKLOG.md)'de *"Ajanın dosya araçları Claude Code'unkiler gibi olacak"*. v11-4, Queen Editor v10'da kullanıcının istediği sürüm işinin buradaki
karşılığı, Claude'un önerisi.
**Queen Editor'de de:** planın 10. maddesi iki uygulama için *("Uygulamalar")*; Queen Editor'deki
karşılığı [Queen Editor v10](2026-10-20-queen-editor-v10-roadmap.md)'un v10-1'i. Orada büyük bir
tasarım hizalandı; burada kullanıcı şimdilik küçük bir düzeltme seçti, ve büyük tasarım
[BACKLOG.md](../../queen-agent/BACKLOG.md)'de *"Veri ve kayıt akışı baştan tasarlanacak"* olarak
bekliyor. **İki araç ayrı proje**
*(kullanıcı, 8 Ekim — "abi iki aracı tutan bir test olamsın bunu istemiorum bunalr tammaen ayrı bir
proje")*: iki madde ayrı yazılır, ayrı koşar, ve ikisini bağlayan bir test yazılmaz.
**Hangi koşunun önce koşacağı kullanıcıya sorulacak.** v9 ile v10'da iki koşu aynı anda açık durmadı
*(kullanıcı, 5 Ekim — "iki roadmepi ortak koşmacayğız ve ortak klasöür olmayacak önce queen editoru
koşucaz bitiricez sonra queen agnetı koşucaz")*; o söz o iki koşu içindi.

**Numaralar:** maddeler v11-… diye yazıldı, ve koşu başlarken *(22 Ekim)* ortak sayaçtan, koşu
sırasıyla gerçek numaralarını aldı — sayaçta en yüksek numara 488'di (Queen Editor v10): **489 · v11-4,
490 · v11-1, 491 · v11-2, 492 · v11-5, 493 · v11-6.**

**Kullanıcıyla birlikte:** prompt'u değiştiren iki madde, v11-5 ve v11-6 *(kullanıcı, 22 Ekim — "içinde
prompt değiştirme olacak task'ları beraber yapıcaz, gerisini sen direkt koşabilirsin")*. Koşu onlara
gelince durur ve kullanıcıyı bekler.

**Sıra: tek tek, dalga yok** *(kullanıcı, 22 Ekim — "dalga yok sıralı yapılacak görevler")*. Bir
madde birleşince sıradaki başlar; worktree açılmaz, iş ana klasörde koşunun dalında yürür.

1. **v11-4** — sürüm V11, koşunun ilk işi.
2. **v11-1** — bağlantı kontrolü; `store.py`, `web/app.py`, `main.py`, 448'in dosyaları ve notebook.
3. **v11-2** — canlı akış; ilk adımı araştırma, kod değil.
4. **v11-5** — Krea için prompt.
5. **v11-6** — yön ve video süresi; v11-5 gibi QueenAgent'ın prompt talimatına dokunur, onun
   arkasından.

---

| # | İş | Bitti sayılır |
|---|---|---|
| 490 · v11-1 | ✅ *(Colab'da Drive'ı koparma denemesi kullanıcının sondaki denemesinde)* · `ALIGNED` *(20 Ekim)* · **Drive bağlantısı koparsa QueenAgent hatayı gösterip durur; 448'in taşıma kodu silinir.** *(Kullanıcı, 20 Ekim — "Başarılı mesajı, veri kalıcı hafızaya yazıldıktan sonra gösterilsin", "Sorun: Uygulamalar veriyi sadece cache'e yazınca "başarılı" gösteriyor; kalıcı kayıt yapılmadan işlem tamamlanmış görünüyor. Veri kaybı riski."; büyük tasarım konuşulduktan sonra — "yada abi bu kadar büyük bir işe girmeyelin şuanlık collabmounte çöküp çkmediğini kontrunul uyaoalım çökmüşse hata gösterelim durdurum bu yeter ne diyorsun şimdilik bu fix bizi kurtarır"; 448'in taşıma kodu anlatılınca — "sil".)* **Backlog'daki "Bazı projeler kayboldu" buraya katıldı** *(kullanıcı, 13 Ekim — "şuan queenagentta projeer kayboldu bazıalrı nasıl olduğunu anlamadık backloga at bunu araştırmamzı alzım")*. **Büyük tasarım şimdilik yok:** backlog'da *"Veri ve kayıt akışı baştan tasarlanacak"* olarak bekliyor. Bu madde yalnız beş şey: **(1) Bağlantı kontrolü.** `services/store/store.py`'nin `Store`'u QueenAgent'ın dosyalara giden tek kapısı — iki mimar her dosya erişiminin ondan geçtiğini doğruladı. `Store` her işlemden önce Drive'ın kökünü bir kez stat eder, ve aygıt kimliğini ilk kontrolde kaydettiğiyle karşılaştırır. Tutmazsa bir hata yükseltir — bilerek FileNotFoundError olmayan bir hata, ki çağıranların `except FileNotFoundError`'u kopmuş bağlantıyı "bulunamadı"ya çevirmesin. Hata işletim sisteminin kendi sözünü taşır. **(2) Kök açılmaz.** `Store` kökü hiç açmaz. Bugün `_into_folder` FileNotFoundError alınca bütün zinciri `os.makedirs` ile açıyor; kopmuş bağlantıda bu ağacı Colab'ın kendi diskinde yeniden kuruyor. Var olan kökün içinde klasör açılabilir: 447'den beri proje klasörünü ilk yazmada alıyor. **(3) Ekranda gerçek hata.** `web/app.py`'de OSError için tek bir hata işleyicisi 503 ve `{"error": str(exc)}` döner. Ekran `body.error`'u zaten gösteriyor *(`failure.js`, `useProjects`, `useChat`)*: ekran ve `dist` değişmez. Ajan turu sürerken `Store`'un hatası turu bugünkü yoldan — EngineFailed → `live_turns` → `events`'in hatası — bitirir, ve ekran hatayı gösterir. **(4) Açılış.** Bağlantı kontrolü açılışta tutmazsa sunucu açılmaz ve gerçek cümleyi yazar; hiçbir zaman boş bir proje listesi göstermez. **(5) 448'in taşıma kodu silinir:** `old_projects.py`, `take_in`, `Store.mtime`, `main.py`'deki satırı, ve notebook'ta yalnız 448 için duran ne varsa — sunucunun açılışını bekleme süresi `START_CAP = 600`, yorumu 448'i adlıyor. Sebep: A'nın yazanı bu — açılışta `projects.json`'a yanlışlıkla "bulunamadı" denince onu yalnız eski projelerle yeniden yazdı. Eski dosyalar — `project.json`, `pinned`, `archived` — Drive'da dokunulmadan kalır. **Olduğu gibi kalan:** 447'nin kuyruğu — düşen bir kuyruk yazması yine yalnız log'a yazılır, ve sonraki işlem bağlantı kontrolüne takılır —, ve geri kalan her şey. Arka plan aşağıda, *v11-1*'in başlığında. | Colab'da uygulama çalışırken Drive'ın bağlantısı kesilince, sonraki işlem hatayı gerçek cümlesiyle gösteriyor; süren bir ajan turu hatayla duruyor. Colab'ın kendi diskine bir şey yazılmıyor. Drive bağlı değilken açılış boş bir proje listesi değil, hata veriyor. 448'in kodu yok, ve var olan projeler değişiklikten sonra aynı listeleniyor. |
| v11-2 | `ALIGNED` *(20 Ekim — "evet doğru anladın")* · **Canlı akış çalışmıyor: süren tur ekranda canlı akacak.** *(Kullanıcı, 20 Ekim — haftalık planın 12. maddesi, üç adımla: v10'dan önce Colab'da token ve araç çağrılarının canlı akıp akmadığını cevaplamak; sebebin Cloudflare Quick Tunnel olduğunu, yazılı iki yoldan biriyle göstermek; gösterilince düzeltmeyi uygulamak.)* **Backlog'daki "Süren tur ekranda canlı akmıyor, F5'le güncelleniyor" buraya katıldı** *(kullanıcı, 13 Ekim — "queen agenttta o arkaplanda çalışıyor ama değişikleri steam etmiyor token artışını toolcalları vs ben f5 e basınca güncelleniyor neden incelerm sin"; incelemeden sonra: "backloa aekle bunu")*. **Bugün** tur sunucuda sürüyor, ama token sayısı ve araç çağrıları ekrana tur sürerken gelmiyor; sayfa yenilenince o anki hâl görünüyor. **Sebep gösterilmedi, ve gösterilmeden düzeltilmez.** Sırası planın üç adımı: (1) kullanıcının cevabı, (2) sebebin gösterilmesi, (3) düzeltme — şekli gösterilen sebebe göre. Bilinenler ve iki yol aşağıda, *v11-2*'nin başlığında. | Sebep gösterildi ve maddeye yazıldı. Colab'da, notebook'un açtığı adresten, tur sürerken token sayısı ve araç çağrıları ekrana geldikçe görünüyor; F5 gerekmiyor. |
| 489 · v11-4 | ✅ · `ALIGNED` *(20 Ekim — "evet lütfen")* · **Sürüm koşunun başında V11 olur.** **Bugün** [version.js](../../queen-agent/frontend/src/shared/version.js)'te `VERSION = "V10"`. Kullanıcı bunu Queen Editor v10 için istedi *(20 Ekim — "v10 btin ceditorde sürüm bump etmeyide yaz sonra unutyorsun", "yad başta bump et ui da")*; Claude aynısını burada öneriyor. Koşunun ilk işi. | QueenAgent'ın başlığında, koşunun başından itibaren *"QueenAgent V11"* yazıyor; `V10` hiçbir yerde yok. |
| v11-5 | `UNALIGNED` · **QueenAgent Krea için prompt yazabilir.** *(Kullanıcı, 21 Ekim — "for the queen agent roadmap add task for implementing prompts for krea", "queen agentta kreaya göre prompt yazabilmesi lazım mantıken … onun için bir task aç".)* Queen Editor'e Krea 2 Turbo, [Queen Editor v10](2026-10-20-queen-editor-v10-roadmap.md)'un 482'siyle fotoğraf seçeneği olarak giriyor; QueenAgent bugün yalnız bugünkü modellerin etiket prompt'larını yazıyor. Dalgası hizalanınca belli olur. | Krea için yazılan prompt'lar Krea'da istenen sahneyi ve tarzı veriyor. |
| v11-6 | `UNALIGNED` · **QueenAgent başta videonun yönünü ve süresini sorar, prompt'ları ona göre yazar.** *(Kullanıcı, 22 Ekim — "biz videoları yatay yapma özelliği eklemedik mi, queen agent başta sormalı ki ona göre prompt yazsın"; "bir de video süresi var".)* Queen Editor v10'da üretim yatay ya da dikey olabiliyor, varsayılan yatay *(476 – 477)*; QueenAgent'ın prompt talimatı bugün dikey 1024 × 1536 yazıyor. Dalgası hizalanınca belli olur. | QueenAgent yeni bir senaryoda yönü ve video süresini soruyor; yazdığı prompt'lar seçilen yöne ve süreye göre. |

---

### v11-1 — Bağlantı kontrolü *("Bazı projeler kayboldu"yu içine aldı)*

**Bu maddenin kapattıkları:** **A** — 448'in taşıma kodu gidiyor; **B** — bağlantı kontrolü ve kökün
açılmaması; ve her disk hatasının ekrana yalnız "HTTP 500" olarak gelmesi. **C ve D açık kalıyor.**
E'nin taşıması da 448'le gidiyor: 448'in okuyamayıp hiç taşımadığı eski bir proje varsa, bundan sonra
da listelenmez — klasörü Drive'da durur. Kullanıcıya göre öyle bir proje yok *(20 Ekim — "yok öyle bir
şey bütün projeler taşındı")*.

**Arka plan** — backlog girdisinden, 13 Ekim'deki hâliyle. Bazı projeler QueenAgent'ın listesinde artık
görünmüyor; nasıl olduğu anlaşılmadı. Sebep gösterilmedi.

**Araştırmanın bakacağı yerler** *(Claude, 13 Ekim — commit'lerden, sebep sayılmadan)*: v10'da proje
kaydı değişti. 447'den beri projelerin bilgisi tek bir `projects.json`'da, sunucu onu açılışta bir kez
okuyup bellekte tutuyor ve değişiklikleri sıralı bir yazıcıyla diske yazıyor. 448 eski projeleri her
açılışta bir kerelik oraya taşıyor; okunamayan, diskin reddettiği ya da zamanı metin olmayan bir projeyi
bütünüyle atlayıp log'a yazıyor, ve eski dosyalara dokunmuyor. *(Aşağıdaki A ile E bu taşımadan; kod
bu maddeyle siliniyor, eski dosyalar backlog'da silinmeyi bekliyor.)*

**Kullanıcının tahmini ve isteği** *(13 Ekim — "muhtemelen collabtin drive ile bağlantısı koptu böyle
bir şey olursa ilerlemyemliyiz hata gösteremlyiiz")*: Colab'ın Drive bağlantısı kopmuş olabilir; öyle
olursa QueenAgent devam etmez, hata gösterir. Bu madde isteği bağlantı kontrolüyle karşılıyor.

**İnceleme, 13 Ekim** *(bir subagent; kodda ve gerçek backend sınıflarıyla bir betikte denendi, Colab'da
değil. Hangisinin kullanıcıya olduğu kullanıcının kanıtıyla belli olur)*. 447'den *(9 Ekim)* beri açılan
bir projenin klasöründe `project.json` yok: satırı `projects.json`'dan düşerse onu bir daha hiçbir şey
listelemez, çünkü 448'in taşıması yalnız `project.json`'lu klasörleri okuyor. Daha eski projeler sonraki
açılışta eski dosyalarından geri gelir.

- **A — gösterildi, en güçlüsü:** açılışta `projects.json` bulunamazsa sunucu onu "hiç proje yok" sayar
  *(`file_project_store.py`'nin `_loaded`'ı)*, ve 448'in taşıması aynı açılışta eski projeleri bulup
  `projects.json`'ı yalnız onlarla **yeniden yazar** *(`old_projects.py`'nin `move_old_projects`'i,
  `take_in`)*. Drive'ın Colab bağlantısı duran bir dosyaya "bulunamadı" diyebiliyor
  *([colabtools #5970](https://github.com/googlecolab/colabtools/issues/5970), Mayıs 2026)*. Görülen: 9
  Ekim'den sonra açılan bütün projeler gider; eskiler 447'den önceki ad, iğne ve arşiv hâlleriyle geri
  gelir; kaybolanların klasörleri Drive'da durur.
- **B — gösterildi:** Drive oturum ortasında koparsa
  *([colabtools #3441](https://github.com/googlecolab/colabtools/issues/3441))* değişiklikler yalnız
  bellekte ya da makinenin kendi diskinde kalır, ekran başarılı der; sonraki açılışta gider. Yazıcı üç
  denemeden sonra yalnız log'a yazıp bırakıyor.
- **C — gösterildi:** aynı `projects.json`'da iki sunucu — başka bir Colab oturumu, ya da Serve hücresi
  yeniden çalışırken kapanmamış eski sunucu —: her biri kendi kopyasını bütün olarak yazar, sonuncu
  ötekinin eklediklerini siler.
- **D — şüphe:** oturum bittiğinde Drive'ın yerel önbelleğinde kalmış yazmalar; notebook Drive'ın
  `flush_and_unmount`'unu hiç çağırmıyor.
- **E — gösterildi:** 448 okuyamadığı eski bir projeyi her açılışta atlıyor; v9 onu listeliyordu.
- **F — şüphe, kayıp yok:** 12 Ekim 12:16'dan *(`e6bedf8b`)* önce açılmış bir oturum hâlâ v9'u çalıştırır,
  ve v9 v10'da açılan projeleri göstermez.
- **Elendi:** sohbet satırı yazmaları (463, 467) proje satırına dokunmuyor; proje yalnız onaylanan
  Delete'le gidiyor; ekran yalnız Archived sekmesi ve aramayla gizliyor.

**Drive hatasının yutulduğu ya da boş sonuca döndüğü yerler** *(kullanıcının isteği için, aynı
inceleme)*: `projects.json` bulunamazsa boş liste; `store.py`'nin `list_dir`'i olmayan klasörü boş liste
sayıyor; `_into_folder` "bulunamadı" alan her yazmada bütün klasör zincirini yeniden açıyor; yazıcının
düşen yazması yalnız log'da; silmede "bulunamadı" yok sayılıyor; bulunamayan sohbet ve dosya "chat not
found" / "file not found" oluyor; başka her disk hatası ekrana yalnız "HTTP 500" olarak geliyor; sağlık
kontrolü kökü hiç yoklamıyor, ve notebook kökün gerçekten Drive'da olduğuna bakmıyor.

**Kullanıcı baktı, 13 Ekim** *("durmuyorlar baktım muhtmelen mount koptu ama kullanırken bir hata
lamadığım için fark edemedim")*: eski `projects.json` ne sürüm geçmişinde ne çöp kutusunda. Kullanırken
hiçbir hata görülmedi. Bu B'yle bağdaşıyor: kopuk bağlantıda yazmalar Drive'a hiç ulaşmaz, ekran yine
başarılı der — Drive'ın geçmişinde de bu yüzden iz kalmaz. Gösterilmedi; log yok.

**Sebebi bulmak için açık kalanlar** *(13 Ekim'den; bu maddenin işi değil)*: hangi projeler kayboldu ve en son ne zaman
görüldüler; hepsi 9 Ekim'den sonra mı açıldı (evetse A–D); Drive'daki klasörleri duruyor mu —
kullanıcının *"durmuyorlar"*ı eski `projects.json` için mi klasörler için mi, belli değil; arşivde mi; ve mümkünse kaybolduğu Colab
oturumunun sunucu log'u. Serve hücresinin log'unda ilk v10 açılışından sonraki bir açılışta *"Moving
projects of the old layout into projects.json"* satırı A'yı gösterir; *"projects.json was not written
… [Errno 107]"* B'yi; *"Old project … was not moved"* E'yi.

### v11-2 — Canlı akış *("Süren tur ekranda canlı akmıyor"u içine aldı)*

**Bilinenler** *(Claude, 13 Ekim)*:

- Kodda bir kusur bulunmadı: tur her değişiklikte sürümünü artırıp dinleyenleri uyandırıyor
  (`live_turns.py`'nin `apply`'ı), `GET …/events` her değişiklikte bütün snapshot'ı bir kare olarak
  gönderiyor (`routes.py`'nin `_listened`'ı), ve ekran her kareyi çiziyor (`useChat.js`'in `heard`'ü).
- Canlı akışı 462 kurdu *(10 Ekim)*: tarayıcı turu EventSource'la, SSE olarak dinliyor. QA onu yalnız
  yerelde, tünelsiz denedi.
- Notebook uygulamayı bir Cloudflare Quick Tunnel'dan (trycloudflare) açıyor, ve Cloudflare'in belgesi
  *"Quick Tunnels do not support Server-Sent Events (SSE)"* diyor
  *([Limitations](https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/do-more-with-tunnels/trycloudflare/))*.
  Tünel kareleri tutuyorsa görülen tam bu: tur sürerken hiçbir şey, F5'te o anki hâl, sonda cevap.
- Bununla bağdaşmayan: 461'den önceki akış da `text/event-stream`'di, ama POST'tu ve `fetch`'le
  okunuyordu. O akış Colab'da canlı aktıysa tüneli bozan SSE'nin kendisi değil GET/EventSource farkı
  olabilir — düzeltmenin şeklini bu belirler.

**Adım 1 — kullanıcıya soruldu:** v10'dan önce *(10 Ekim'den önce)* Colab'da token ve araç çağrıları
canlı akıyor muydu. Kullanıcı hatırlamıyor *(20 Ekim — "hatırlamıyorum")*.

**Adım 2 — sebep önce araştırılır** *(kullanıcı, 20 Ekim — "ilk önce araştır test etme bana haber
vermeden test etme bulamazsan çözmezsen collabte ben bakarım")*: Cloudflare'in Quick Tunnel'ı,
SSE, GET/EventSource ile POST/`fetch` farkı belgelerden ve bilinen kayıtlardan araştırılır. Kullanıcıya
haber verilmeden hiçbir test yapılmaz — bilgisayarda bir tünel açmak da. Araştırma sebebi göstermezse
kullanıcı Colab'da bakar: tur sürerken F12 → Network → `events` → EventStream; satırlar canlı mı, tur
bitince topluca mı geliyor.

**Adım 3 — düzeltme:** gösterilen sebebe göre; şekli spec'te.

