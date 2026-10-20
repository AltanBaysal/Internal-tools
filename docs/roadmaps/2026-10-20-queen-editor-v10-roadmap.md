# Queen Editor — Yol Haritası v10

**Tarih:** 2026-10-20 · **Koşu dalı:** `feat/queen-editor-v10` *(henüz açılmadı)* · **Durum:** 0/5 · v10-1, v10-2, v10-3 ve v10-6 hizalandı *(20 Ekim)*; v10-4 kullanıcıyı bekliyor
**Öncesi:** [v9](2026-10-05-queen-editor-v9-roadmap.md) — 30/30 kapandı ve main'e birleşti; sonradan
açılan 469 ve 470 de main'de.
**Kaynak:** Maddelerin hepsi kullanıcının 19 – 25 Ekim haftası için yazdığı plandan, 20 Ekim'de
verildi: v10-1 planın 10. maddesi, v10-2 11.'si, v10-3 1.'si, v10-4 2.'si. v10-2
[BACKLOG.md](../../queen-editor/BACKLOG.md)'deki *"Export'u Drive'da bulmak zor"*u içine aldı, ve girdi
oradan çıkarıldı. **Yatay video ve çizim tarzı Queen Editor'ün işi** *(kullanıcı, 20 Ekim — "Çizim
tarzıda yeni fotoğraf modelleri denicez o queen editore gidiyor"; yatay video için de aynı gün Queen
Editor dedi)*.
**QueenAgent'ta da:** planın 10. maddesi iki uygulama için *("Uygulamalar")*; QueenAgent'taki karşılığı
[QueenAgent v11](2026-10-20-queen-agent-v11-roadmap.md)'in v11-1'i, ve o ayrı hizalanacak. **İki araç ayrı proje**
*(kullanıcı, 8 Ekim — "abi iki aracı tutan bir test olamsın bunu istemiorum bunalr tammaen ayrı bir
proje")*: iki madde ayrı yazılır, ayrı koşar, ve ikisini bağlayan bir test yazılmaz. **Hangi koşunun
önce koşacağı kullanıcıya sorulacak.**
**Planın bu belgede olmayanları:** Futa kontrolü *(kullanıcı, 20 Ekim — "futa kontrolü teknik değil
önce benim denemem lazım")*; Patreon, thumbnail ve kanal işleri bu araçların işi değil.

**Numaralar:** maddeler v10-1 – v10-4 ve v10-6 diye yazıldı, ve koşu başlarken ortak sayaçtan gerçek
numaralarını alır. Sayaçta en yüksek numara bugün 470. QueenAgent v10'un v10-… adları başkaydı; o
koşunun maddeleri gerçek numaralarını çoktan aldı.

**Sıra, dalgalarla** — tablonun sırası dalgaların sırası. Bir dalganın maddeleri aynı anda koşabilir,
aynı yere dokunmaz, ve ikisi birden frontend'e dokunmaz: her biri bütün `dist`'i yeniden kurar. Dalga,
öncekiler birleşince başlar.

- **Dalga 1:** v10-6 ve v10-1. v10-6 koşunun ilk işi, yalnız frontend'deki sürüm. v10-1 Drive'a giden
  her okuma ve yazma yoluna dokunur, yani öteki maddelerin hepsiyle bir yer paylaşır. Frontend'e
  dokunmaz: ekran hatayı bugün de gösteriyor.
- **Dalga 2:** v10-2, v10-3. v10-2 export'un yerine — `photo_store.py`, `run_export.py` ve proje
  listesi —, v10-1'in `Storage`'ından geçerek; v10-3 üretimin yönüne — seçeneğin ekranı, fotoğraf ve H3
  grafiklerinin boyutu, üretici. Frontend'e yalnız v10-3 dokunur. v10-3 birleşik export'un tuvaline
  (`ffmpeg_video_exporter.py`) dokunmak zorunda kalırsa bile o dosya v10-2'nin dokunduklarından ayrı.
- **Dalga 3:** v10-4, en sonda *(kullanıcı — "bunu en sona bekle")*.

**Backlog'a döndü:** planın 14. maddesi, *"Düşük çözünürlükle üretim hızı"*, v10-5 olarak yazılmıştı
*(kullanıcı, 20 Ekim — "bu taskı backloga ekle")*; [BACKLOG.md](../../queen-editor/BACKLOG.md)'de.

---

| # | İş | Bitti sayılır |
|---|---|---|
| v10-1 | `ALIGNED` *(20 Ekim)* · **Tek kapı: Drive'a giden her okuma ve yazma tek bir `Storage`'dan geçer, ve bir kayıt ancak yazıldığı kanıtlanınca başarılı görünür.** *(Kullanıcı, 20 Ekim — "Başarılı mesajı, veri kalıcı hafızaya yazıldıktan sonra gösterilsin", "Sorun: Uygulamalar veriyi sadece cache'e yazınca "başarılı" gösteriyor; kalıcı kayıt yapılmadan işlem tamamlanmış görünüyor. Veri kaybı riski."; "bunu aslıdna architecture güncelleme gibi yapabilirz", "uygulama data nın nereye yazıldığını bilmez sadeve save yapar ve save bekler işlem başarılı dönünce devam eder gibi"; hizalarken — "şöyle bizim laeylerımız var ya mesela frontedn sonra backend sonra database şuan drive", "database tek bir class yada katman olsun", "aynı shareprefernce gibi encapsulate etsin altındaki karmaşayı", "uygulama sadece save i bilir ve save olunca fonskiyon başarılı döner save olduğu bilir gibi", "yani drive ve backen arasında backend en altındaki katmaan datasource gibi", "amacım save için save olduğu kanıtlanmadan user başarılı göstermek yok  ve bütün saveler ve readler bu katmandan geçer bu kadar basit", "şöyle overengineering yaplımaz ama SOLID Prensibleri takip edilir".)* **Tasarım onaylandı:** iki mimar ve bir reviewer çizdi, kullanıcı 20 Ekim'de onayladı — CLAUDE.md'nin "koddan önce tasarım" adımı bitti, spec yazılabilir. Drive API'si ve sunucu tarafında kanıt bırakıldı *(kullanıcı — "şuan bence güzel değil ve gereksiz karmaşık geliyor"; "google drive mountu kopmuştu ama uygulam çalışmnya devam ediyordu belki bunu takip edebilirz hızlı bir çözüm olur hem? onu dışında bir sıkınıt yaşamadık ama bu merkezileştime işini net yapamlıyız")*. **Bugün** notebook Drive'ı `drive.mount` ile bağlıyor; bağlantı oturum ortasında koparsa yazmalar makinenin kendi diskine düşer ve ekran başarılı der *(QueenAgent'ın 13 Ekim incelemesinin B'si, [colabtools #3441](https://github.com/googlecolab/colabtools/issues/3441))*. **(1) Tek kapı.** Bugünkü `DriveStorage` *([storage.py](../../queen-editor/backend/services/drive/storage.py))* tek kapı olur, adı `Storage`, yeri `backend/services/storage/` *(kullanıcı — "adı değişsin sıkıntı yok")*; tek uygulaması olduğu için Protocol yok. Drive'a her okuma ve yazma ondan geçer, bugün yanından geçenler de: `photo_store`'un `make_export_folder`, `make_videos_dir`, `copy_photo`, `copy_export`, `remove_dir`, `photo_dir` / `file_path` / `export_dir`'i; `run_export`'un ayrı modu — ffmpeg parçaları bugün doğrudan bağlantıya yazıyor, artık makinede yazıp dosyayı `Storage`'a verir; `reference_store`'un ffprobe yolu; ve dosyaları `send_from_directory` ile sunan route'lar. Makinenin geçici alanı — `tempfile`, `make_pieces_dir` — `Storage`'ın dışında kalır. Store'ların dosya adları ve şemaları değişmez, domain değişmez. **(2) Bağlantı kontrolü.** `Storage` her işlemden önce Drive'ın kökünü bir kez stat eder, ve aygıt kimliğini ilk kullanımda kaydettiğiyle karşılaştırır. Stat hatası (Errno 107), "bulunamadı" ya da başka bir aygıt işlemi hatayla durdurur. Ekran yalnız hatayı gösterir; yeniden bağlanma yok, ek talimat yok *(kullanıcı — "hata versin yeter biz anlarız")*. **(3) Kayıt.** Bir kayıt hedefin kendi klasöründe, tanınır bir önekli geçici dosyaya yazılır, fsync edilir, sonra `os.replace` ile yerine konur; listeler o öneki atlar. Başarı yalnız bu demek. İki ekleme kaydı — `photos.jsonl` ve `chats.jsonl` — ekleme olarak kalır: ekleme kipi ve fsync. **(4) Örtük klasör yok.** Yazmalar kökü ya da bir proje klasörünü açmaz; projeyi yalnız `make_dir` açar. `rename_dir`'deki `makedirs` kalkar. **(5) "Yok" yalnız FileNotFoundError.** Başka her OSError okumada, listede, `dir_exists`'te ve `stamp`'te yükseltilir. Okunamayan bir `plan.json` ya da `arsiv.json`, ekleme ya da işaret güncellemesinde boş diye yeniden yazılmaz, hata verir. **(6) Ekranda gerçek hata.** `web/app.py`'de OSError için tek bir hata işleyicisi 503 ve `{"error": str(exc)}` döner. `api.js` `body.error`'u zaten gösteriyor: frontend değişmez, `dist` yeniden kurulmaz. **(7) Ad sınırı — acil düzeltme bu maddeye katıldı** *(kullanıcı — "acil düzeltmeyi direve maddesiyle beraber ypa")*. `Storage` boş olan, `.` ya da `..` olan, ya da `/`, `\` veya NUL içeren her klasör ya da ad parçasını, birleştirmeden ve diske dokunmadan reddeder. Sebep, reviewer'ın 20 Ekim'de bulduğu ve Flask'ın test istemcisiyle denenen — Colab'da uçtan uca değil —: `DELETE /api/projects/..` (`%2E%2E` de) `delete_dir("..")`'ya ulaşıyor ve `rmtree` bütün MyDrive'ı siliyor; `.` bütün projeleri siliyor; `/photos/../<dosya>` MyDrive'ın en üstündeki dosyaları sunuyor. Tünel herkese açık ve girişsiz. **(8) Kabul edilen sınır** *(kullanıcı — "evet sıkıntı yok")*. "Kanıtlandı", canlı Drive bağlantısının dosyanın tamamını kabul etmesi demek; Google'a yükleme birkaç saniye sonra gelir, ve o saniyelerde ölen bir makine başarılı gösterilmiş bir kaydı kaybedebilir. **(9) Sonraya kalan.** Okumaları hızlandıracak yerel önbellek *(kullanıcı — "ama readleri hızlandırmak için colalb cihazını chache gibi kullanbilirz ... ama dışarı bilmez")* şimdi kurulmaz; okumalar yavaş çıkarsa sonra `Storage`'ın içine, dışarıdan görünmeden girer. Değişiklik izleme, iki oturum ve Drive API'si de dışarıda. **(10) Maliyet** — koddan sayıldı, ölçülmedi: galerinin bir sorgusu yaklaşık 8 dosya sistemi çağrısından yaklaşık 12'ye çıkar (her birinde bir kök stat'ı). Yavaş gelirse kontrol yalnız yazmalarda yapılır. QueenAgent v11-1 ayrı hizalanacak; kod ve test paylaşılmaz. Kutu çizimi aşağıda, *v10-1*'in başlığında. | Drive bağlantısı kopukken yapılan bir kayıt ekranda Drive'ın hatasını gösteriyor, ve Colab'ın kendi diskine bir şey yazılmıyor. Yarım dosya yok: bir kayıt ya bütün duruyor ya hiç yok. Düşen bir kayıt ekranda "HTTP 500" değil, gerçek cümleyi gösteriyor. Okunamayan bir şey — bulunamayan ya da ulaşılamayan — hiçbir zaman boş gösterilmiyor. `..` ve `.` proje adları reddediliyor, ve queenEditor'ün dışında hiçbir şeye dokunulmuyor. Drive'a `Storage`'ın dışından hiçbir şey yazmıyor. Colab'da `order.json` arka arkaya 20 kez değiştirildi, ve Drive'ın web'inde ve çöp kutusunda bakıldı: çöp kutusu dolmuyor, aynı addan iki dosya yok; olmazsa birleştirmeden önce kullanıcıya söyleniyor. |
| v10-2 | `ALIGNED` *(20 Ekim)* · **Export dosyaları proje klasörünün içine değil, projelerin yanındaki `Exportlar` klasörüne kaydedilecek.** *(Kullanıcı, 20 Ekim — "Export dosyaları proje dosyalarının içine değil, ayrı bir klasöre kaydedilsin", "Sorun: Export'lar proje dosyalarının arasına karışıyor, bulmak zor.")* **Backlog'daki "Export'u Drive'da bulmak zor" buraya katıldı** *(kullanıcı, 3 Ekim — "queen editorun exportunu driveda bulmak çok zor çünkü ilk proje dosyasını sonra içidne export bulmak lazım", "Exporltar ve projeler iki klasöre ayrılsa ve exportlarda export tarhi ve proje adı olarak adlandırılsa bulması oldukça kolaylaşırdı")*. **Bugün** bir export `MyDrive/queenEditor/<proje klasörü>/export/<YYYY-MM-DD HH-MM>/`'ye yazılıyor — dakikaya kadar tarihli bir klasör, tasarım v3'ün 92'si; ayrı ve birleşik export aynı tarihli klasörü paylaşıyor, fotoğraflar onun içinde kendi klasöründe *([photo_store.py](../../queen-editor/backend/features/photo_generation/data/photo_store.py))*. **Kararlar** *(kullanıcı, 20 Ekim — Claude'un üç önerisini seçti, ve klasör ağacını görünce: "bu olsun")*: **Yer:** yeni export'lar `MyDrive/queenEditor/Exportlar/`'a, projelerin yanına gider. Uygulama `Exportlar`'ı proje olarak listelemez, yani hiçbir proje bu adı alamaz. **Ad:** her export'un kendi klasörü, önce tarih sonra proje — `2026-10-20 14-30 Proje A`; Drive adla dizdiği için en yeni export'lar bir arada durur. **Eskiler:** bugüne kadarki export'lar `<proje>/export/<tarih>/`'de kalır; oraya yeni bir şey yazılmaz, hiçbir şey taşınmaz. **İçi değişmez:** `foto/`, ayrı export'ta `video/01.mp4…`, birleşik export'ta `<Proje>.mp4`. Export v10-1'in `Storage`'ından geçer, bu yüzden v10-1'in arkasından koşar. Klasör ağacı aşağıda, *v10-2*'nin başlığında. | Bir export bittikten sonra `queenEditor/Exportlar/`'ın altında adı *"<tarih> <proje>"* olan yeni bir klasör var, ve export'un bütün dosyaları onun içinde. Proje klasörünün içinde yeni bir export klasörü açılmıyor. Proje listesinde `Exportlar` görünmüyor. Eski export'lara dokunulmamış. |
| v10-3 | `ALIGNED` *(20 Ekim)* · **Yatay ya da dikey: her üretimde yön seçilir, varsayılan yatay; video fotoğrafın oranını izler.** *(Kullanıcı, 20 Ekim — "Yatay video üretimi için gereken teknolojiyi geliştir", "Üretimi dikeyden yataya geçir"; "Neden: Şu an sadece dikey video üretiyoruz ve bu kötü görünüyor. Yatay video 8 kanalın hepsinde büyümeyi artırmalı."; hizalarken — "zaten fotolar yatay olacka önce sonra videolar ama burda şunu sitiyorum biz fotoyu seçelim yatay dikey video oluştururken video oluşturucu fotoğrafla aynı oranı takip etsin", "üretim başına negative prompt gibi 2 ospyion olsun sadece sen eistediğin gibi ekle sonra tasarımcıdan t asarım gelicne düzeltiriz", "yok en son deneriz ama h3 ün çalıştığı oranlar var o oranlarda olmalı pixel sayılarındadikka et ona nromal saıylar dğeil çünkğ".)* **Bugün** üretim yalnız dikey: fotoğraf 1024×1536 *(`assets/workflow_api.json`)*, H3 videosu 576×864 *(`assets/workflow_video_h3_api.json`, `…_first_last_api.json`)*, ikisi de tam 2:3. Birleşik export her parçayı oranını koruyarak 1920×1080'lik tuvale sığdırıp iki yanını bantla dolduruyor *([ffmpeg_video_exporter.py](../../queen-editor/backend/features/photo_generation/data/ffmpeg_video_exporter.py), 259)*. **Kararlar:** **Seçenek:** her üretimde iki seçenek, yatay ya da dikey — negatif prompt'un üretim başına ayarlandığı gibi; varsayılan yatay. Ekrandaki yerini şimdilik Claude koyar, tasarımcının tasarımı gelince düzeltilir. **Oran fotoğraftan:** fotoğraf seçilen yönde üretilir; video üreticisi sormaz, fotoğrafın oranını izler. **Eskiler:** bugüne kadarki dikey kareler olduğu gibi kalır; onlardan yapılan video dikey çıkar ve 16:9 export'ta bugünkü gibi bantlı görünür. **Boyutlar** yalnız H3'ün gerçekten çalıştığı çözünürlükler, rastgele sayılar değil, ve fotoğrafın boyutu videonun oranına tam uyar. **Yatay tam 16:9** *(kullanıcı, 20 Ekim — "abicim 16 9 olsun ama pixelelar taskta h3 araştırması yapıp bul")*: dikeyin aynası 1536×1024 / 864×576 3:2 olduğu için elendi — export'un bugünkü sığdırması 3:2'lik bir videoyu 1620×1080'e büyütür ve iki yanda 150'şer piksel bant kalır. Piksel sayıları maddenin içinde, H3 araştırılarak bulunur: H3'ün çalıştığı bir 16:9 video boyutu *(1024×576 bir aday, doğrulanmadı)*, ve fotoğraf için oranı tam aynı bir boyut *(ör. 1536×864)*. **Deneme en sonda:** yatay H3 Colab'da maddenin sonunda denenir. Frontend'e dokunur. | Bir üretim yatay ya da dikey ayarlanabiliyor, varsayılan yatay. Yatay bir fotoğraf ve ondan yapılan video ikisi de yatay, H3'ün desteklediği boyutlarda ve aynı oranda. Birleşik export'ta yatay video 1920×1080'lik tuvali bantsız dolduruyor. Dikey bir üretim bugünkü gibi çalışıyor. Kullanıcı yatay H3'ü en sonda Colab'da denedi. |
| v10-4 | `UNALIGNED` · hizalanmayacak, kullanıcıyla birlikte · **Çizim tarzı çeşitlenecek: tek tarz yerine birden fazla tarz, yeni fotoğraf modelleriyle.** *(Kullanıcı, 20 Ekim — "Tek çizim tarzının yerine birden fazla tarz kullan"; "Neden: Bütün içeriklerimiz tek bir çizim tarzında. Tarzları çeşitlendirmek 8 kanalın hepsinde büyümeyi artırmalı."; ve "Çizim tarzıda yeni fotoğraf modelleri denicez o queen editore gidiyor".)* **Bugün** notebook iki fotoğraf modeli kurabiliyor — Nova 3DCG XL IL v9.0 ve DaSiWa Illustrious Anime EpitaphEcstasy —, model kare başına seçilebiliyor *(madde 140)*, ve hangi model seçilirse seçilsin aynı iki LoRA iniyor, biri stil LoRA'sı *(`USNR_STYLE_ILL_V1`, [model_groups.py](../../queen-editor/backend/features/producers/domain/model_groups.py))*. **En sona bekler, ve hizalanmaz** *(kullanıcı, 20 Ekim — "bunu en sona bekle ilk önce beim o foto mdoelelrini bulmam alzım sonra senle yaparız bu taskın aling olmasına gerek yok beraber yapucaz bunu")*: önce kullanıcı fotoğraf modellerini bulur, sonra madde Claude'la birlikte yapılır. **İlgili, backlog'da duran iki girdi:** *"Gerçekçi bir model eklenecek"* *(kullanıcı, 18 Eylül — "gerçekçi bir model eklenecek")* ve *"Fotoğraf modeli her şeyi NSFW'ye çeviriyor"* *(kullanıcı, 11 Eylül; çözümün yeni bir fotoğraf modeli olup olmayacağı kararlaşmamıştı)*. İkisi de yeni modele değiyor, ama aynı istek değil. | Kullanıcıyla birlikte yapılırken belli olur. Kullanıcının sözünden: Queen Editor'de aynı projede birden fazla çizim tarzında kare üretilebiliyor. |
| v10-6 | `ALIGNED` *(20 Ekim)* · **Başlıkta sürüm V10 yazar, koşunun başında.** *(Kullanıcı, 20 Ekim — "v10 btin ceditorde sürüm bump etmeyide yaz sonra unutyorsun", "yad başta bump et ui da".)* Sürüm ekranda [version.js](../../queen-editor/frontend/src/shared/version.js)'in `VERSION`'ından okunuyor, bugün `"V9"`; v9'da bunu 428 yapmıştı. Koşunun ilk işi olarak `"V10"` olur; başka bir şey değişmez. *(v10-5 adı backlog'a dönen maddenindi, bu yüzden 6.)* | Projeler sayfasının ve proje ekranının başlığında "Queen Editor V10" yazıyor. |

---

### v10-1 — Tek kapı

```
Bugün                                         Sonra

Ekran                                         Ekran
  │                                             │  hata: 503 {"error": "<diskin cümlesi>"}
  ▼                                             ▼
backend store'ları                            backend store'ları
  │        │            │                       │  (dosya adları ve şemalar aynı)
  ▼        ▼            ▼                       ▼
DriveStorage  os/shutil   ffmpeg,             Storage   backend/services/storage/
              doğrudan    send_from_directory   │  1. kontrol: kök stat + aygıt kimliği
  │        │            │                       │     (Errno 107 / bulunamadı / başka aygıt → ✘)
  ▼        ▼            ▼                       │  2. ad sınırı: "", ".", "..", / \ NUL → ✘
/content/drive                                  │  3. geçici dosya, hedefin klasöründe
  (bağlantı koparsa yazmalar makinenin          │  4. fsync
   diskine düşer, ekran yine ✔ der)             │  5. os.replace → ✔
                                                ▼
                                              /content/drive
```

### v10-2 — Export klasörü

Bugün:

```
MyDrive/queenEditor/
├── arsiv.json
├── Proje A/
│   ├── settings.json, plan.json, ... 001.png, 001_V1_1.mp4, referans/
│   └── export/2026-10-18 21-05/
│       ├── foto/
│       └── Proje A.mp4
└── Proje B/ ...
```

Sonra *(kullanıcı, 20 Ekim — "bu olsun")*:

```
MyDrive/queenEditor/
├── arsiv.json
├── Exportlar/
│   ├── 2026-10-20 14-30 Proje A/
│   │   ├── foto/
│   │   └── Proje A.mp4
│   └── 2026-10-21 09-45 Proje B/
│       ├── foto/
│       └── video/01.mp4, 02.mp4
├── Proje A/
│   ├── settings.json, plan.json, ... 001.png, 001_V1_1.mp4, referans/
│   └── export/2026-10-18 21-05/ ...   ← eski, kalır; buraya yeni bir şey yazılmaz
└── Proje B/ ...
```