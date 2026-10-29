# Queen Editor — Yol Haritası v11

**Tarih:** 2026-10-24 · **Koşu dalı:** `feat/queen-editor-v11` · **Durum:** 7/7 · bitti; kullanıcı 28 Ekim'de denedi *(kullanıcı, 28 Ekim — "ve gerisi düzgün queen agnetı ve editoru maine mergelyebilrisn")*

**Yama v11.1:** 2026-10-29 · **Koşu dalı:** `feat/queen-editor-v11.1` · **Durum:** 1/2 *(kullanıcı, 29 Ekim —
"patch gibi düşün ubnları"; "queen editorun son roadmpine ekle zaten var v11.1 yap direkt sonuna ekle işte
ynei madde olarak")*. 509 · v11-8 ve 510 · v11-9 bu yamanın maddeleri; yine tek tek yürürler. Ekrandaki sürüm V11
kalır, yama onu artırmaz *(kullanıcı, 29 Ekim — "ekran sürümü değişmesin")*.

**Önceki sürüm:** [v10](2026-10-20-queen-editor-v10-roadmap.md) — bitti.

**Sıra: tek tek, dalga yok** *(kullanıcı, 27 Ekim — "ilk queen ediytor tasklarını yapıcaz bitincebana
haber vericeksin queen anget tasklarına geçiçez"; "sıryaal paralel yapmicaz")*. Koşu bu roadmap'le
başlar, QueenAgent v12 bundan sonra gelir. Bir madde birleşince sıradaki başlar; worktree açılmaz, iş
ana klasörde koşunun dalında yürür.

1. **496 · v11-6** — sürüm V11, koşunun ilk işi.
2. **497 · v11-3** — Drive'a kayıt olmayınca hata. Fotoğraf kaybettirdiği için öteki işlerden önce.
3. **498 · v11-2** — sıra boşken bildirim.
4. **499 · v11-1** — Krea'da SNOFS + Slime, ve Qwen.
5. **500 · v11-5** — arşiv; koşunun belgeleri yazıldıktan sonra, linkler bir seferde düzelsin diye.
6. **501 · v11-4** — femboy ve futa LoRA'ları, kullanıcıyla, en sonda *("bir femboy taskını son al çünkü ban ihtiaçın
   olcak")*. Bitince kullanıcıya haber verilir, sonra QueenAgent v12'ye geçilir.
7. **508 · v11-7** — Qwen kalkar; kullanıcının sondaki denemesinden çıktı.
8. **509 · v11-8** — "orada mısın?" kalkar, üretim bitince bildirim gelir.
9. **510 · v11-9** — videonun sesi kartından kapatılabilir.

---

| Numara | İş | Durum |
|---|---|---|
| 499 · [v11-1](#v11-1) | Translucent Penetration: Krea'da, ve Qwen yeni model olarak | ✅ *(gerçek Krea + Slime ve Qwen fotoğrafları, Qwen graph'ının ComfyUI'de çalışması ve A100'de bellek kullanıcının sondaki Colab denemesinde; ilk çalıştırma iki yeni LoRA için `CIVITAI_COOKIE` ister)* · `ALIGNED` |
| 498 · [v11-2](#v11-2) | Sıra boşken bildirim | ✅ *(gerçek 10 dk, tünelden geçen açık istek ve işletim sisteminin bildirimi kullanıcının sondaki Colab denemesinde)* · `ALIGNED` |
| 497 · [v11-3](#v11-3) | Drive'a kayıt olmayınca hata verip dursun | ✅ *(Colab'da dolu Drive ve kopan bağlantı kullanıcının sondaki denemesinde)* · `ALIGNED` |
| 501 · [v11-4](#v11-4) | Femboy ve futa LoRA'ları | ✅ *(DaSiWa'nın kutusunda Futa ve Futa on male; gerçek kareler ve iki dosyanın inişi kullanıcının sondaki Colab denemesinde; ilk çalıştırma iki yeni LoRA için `CIVITAI_COOKIE` ister)* · `ALIGNED` |
| 500 · [v11-5](#v11-5) | Eski belgeler ve roadmap'ler arşive | ✅ · `ALIGNED` |
| 496 · [v11-6](#v11-6) | Sürüm V11 | ✅ · `ALIGNED` |
| 508 · [v11-7](#v11-7) | Qwen kalkar | ✅ · `ALIGNED` |
| 509 · [v11-8](#v11-8) | "Orada mısın?" kalkar, üretim bitince bildirim gelir | ✅ *(tünelden gelen işletim sistemi bildirimi ve ona tıklayınca sekmenin öne gelmesi kullanıcının sondaki Colab denemesinde)* · `ALIGNED` |
| 510 · [v11-9](#v11-9) | Videonun sesi kartından kapatılabilir | `ALIGNED` |

---

<a id="v11-1"></a>
### 499 · v11-1 — Translucent Penetration: Krea'da, ve Qwen yeni model olarak

**Kabul koşulu:**
- Krea seçiliyken LoRA kutusunda üç seçenek var: **SNOFS** (bugünkü gibi, varsayılan), **SNOFS + Slime**
  (ikisi birlikte yüklenir) ve **Boş** (LoRA yok).
- Fotoğraf üretirken **Qwen Image 2.1 Turbo** seçilebiliyor. LoRA kutusunda iki seçenek var:
  **Translucent Penetration** ve **Boş**.
- Bir Krea senaryosunun kareleri Qwen seçilerek de üretilebiliyor.

Bugün Translucent Penetration panelde "Slime" adıyla yalnız Nova ve DaSiWa'da var. Krea onu
kullanmıyor; kendi graph'ındaki SNOFS'la çiziyor. Qwen ise 484'ün denemesinden sonra Queen Editor'e
hiç girmedi.

**Kullanıcının kararları** *(27 Ekim)*:
- **Krea'da SNOFS'un yanına girer:** *"SNOFS'un yanına girsin. İkisi aynı anda yüklenir. Slime
  fotoğrafında SNOFS da etkisini sürdürür."*
- **Seçilince devreye girer, ve bir de Boş seçeneği olur:** *"Seçilince. Panelde Krea'nın LoRA kutusuna
  "SNOFS + Slime" gibi bir seçenek eklenir. Seçilmezse bugünkü gibi yalnız SNOFS çizer."*; *"bir de
  snofs olmadan bir sürümünü eklme boş"*.
- **Qwen doğrudan Queen Editor'e girer:** *"queen editore direkt girsin ve tek lora translucent
  penetration olsun"*. Deneme yapılmaz.
- **Hangi Qwen:** *"Qwen Image 2.1 Turbo: resmi şablon, 8 adım, cfg 1."*
- **Qwen'in LoRA kutusu:** *"boş ve etransulent penetration 2 versiyon"*.
- **Qwen'in prompt'ları** *(cevap: "3")*: şimdilik Krea senaryosu Qwen'le de çizilir, QueenAgent'ta bir
  şey değişmez. LoRA'nın tetik kelimesini, Nova'daki Slime'da olduğu gibi Queen Editor ekler. İlk
  fotoğraflar Qwen'in ayrı kural istediğini gösterirse QueenAgent'a ayrı bir madde açılır.
- **Claude'un kararları** *(kullanıcı, 27 Ekim — "sen karar ver")*: Translucent Penetration'ın Krea ve
  Qwen sürümlerini coder Civitai'de bulur ve hangisini seçtiğini spec'e yazar; kullanıcı sondaki Colab
  denemesinde görür. Güçler LoRA sayfasının önerdiği; SNOFS bugünkü gibi 0.8. Qwen notebook'a Krea
  gibi kendi kutucuğuyla girer: yalnız işaretlenirse iner.

<a id="v11-2"></a>
### 498 · v11-2 — Sıra boşken bildirim

**Kabul koşulu:** Sıra 10 dk boş kalınca ekranda "orada mısın?" çıkıyor ve tarayıcı bildirimi
geliyor. Sıra boş kaldıkça ikisi her 10 dk'da bir yeniden geliyor. Bir export ya da ajanın cevabı
sürerken ikisi de gelmiyor.

**Neden:** Colab boşta açık kalınca A100 boşa para yiyor, ve sekme arka planda kalmış olabilir.

**Kullanıcının kararları** *(27 Ekim)*:
- **Süre:** *"10dk"*.
- **Bildirim:** *"bir de bildirim atabiliryosa iyi olur arkaplanda kalmış olabilri çünkü"*.
- **Colab'ı kapatmak bu maddeden çıktı:** *"bence bunu roadmapten backloga koyalım şuanlık kapatmak
  yerine bildirim yollasın sadece ve 1 sayılsın"*. "1": süren export ya da ajan cevabı iş sayılır.
  Kapatma [BACKLOG.md](../../../queen-editor/BACKLOG.md)'de, *"Boşta Colab kapansın"*.
- **Tekrar** *(cevap: "2")*: bildirime cevap gelmezse sıra boş kaldıkça her 10 dk'da bir yeniden gelir.
- **Ekranda da sorulur** *(cevap: "yes")*: bildirimle birlikte ekranda "orada mısın?" çıkar.
- **Claude'un kararları** *(kullanıcı, 27 Ekim — "sen karar ver")*: kutuda tek bir **"Buradayım"**
  düğmesi olur; basınca kutu kapanır ve 10 dk yeniden başlar. Tarayıcının bildirim izni ilk kez
  Kuyruğa ekle'ye basılınca istenir, çünkü tarayıcı izni ancak bir tıklamadan sonra sorabiliyor; izin
  verilmezse yalnız ekrandaki kutu çıkar. 10 dk sıra bittiği andan sayar; uygulama boş bir sırayla
  açılırsa açıldığı andan.
- **Yapılırken kararlaşan** *(Claude, 27 Ekim; 498'in coder'ının sorusu üzerine)*: ekranın bugünkü
  sorguları işin bittiğini her ekranda göremiyor — proje listesi hiçbir şey sormuyor, ajanın
  çalıştığı yalnız paneli açıkken biliniyor. Bu yüzden sunucu tek bir soruya cevap verir: sıra, export
  ya da herhangi bir projede ajan çalışıyor mu. Bunu sunucuda merkezi bir bekçi bilir.
- **Olayla, sorarak değil** *(kullanıcı, 27 Ekim — "make it eent dirven dont check it again againü";
  "hayır abi ortka kontrol eden bir yap ı olsun ve hepsi biterse direkt evetn driven 10 dakika geri
  sayı başlasın bir şey gelemze bir şey gelilr tünel içinde queenagentta çözmüştük ordan
  bakabilrisn")*: sıra, export ve ajan işe başlayınca ve bitince bekçiye söyler. Hepsi bitince bekçi
  10 dk'lık geri sayımı kendisi başlatır; arada bir iş başlarsa geri sayım iptal olur. 10 dk dolunca
  "orada mısın?" olayı doğar, ve ekran onu QueenAgent'ın 491'deki long polling'iyle öğrenir: açık bir
  istek, olay olunca hemen cevaplanır. Buradayım geri sayımı yeniden başlatır. Önce yazılan "dakikada
  bir sorulur" yolu bununla değişti. **İzin bekleyen ajan iş sayılmaz:** İzin ver / Reddet'i
  bekleyen ajan kullanıcıyı bekliyor, ve onu iş saymak kutuyu hiç çıkarmazdı.

<a id="v11-3"></a>
### 497 · v11-3 — Drive'a kayıt olmayınca hata verip dursun

**Kabul koşulu:** Fotoğraf, video ya da export Drive'a kaydedilirken Drive bağlı değilse ya da Drive
doluysa, ekranda bir hata çıkıyor ve o sırada süren iş duruyor. Hata, sistemin kendi sözünü taşıyor.
Kaydı yapılamayan iş ekranda bitmiş görünmüyor.

*(İlk yazılan ikinci koşul — "ekranda bitmiş görünen her iş, Colab kapatılıp açıldıktan sonra da
Drive'da duruyor" — 27 Ekim'de kullanıcının kararıyla çıktı; aşağıda.)*

**Ne oldu** *(kullanıcı, 27 Ekim)*: fotoğraflar üretildi ve ekranda hepsi bitmiş göründü; *"ai bazen
düzgün fotoğraf üretmiyor bozukları siliyoruz"*. Sonra videolar üretildi, bozukları silindi, ve Colab
kapatıldı. Yeniden açılınca fotoğrafların yarısı yoktu. Hiç hata görülmedi; *"fotoğraf için yok bu
arada çalışmıyor video içindeo lmuyor"*.

**Kullanıcının kararları** *(27 Ekim)*:
- *"karmaşıklaştırma hata versin ve üretim yad aexport ne yapılıyorsa dursun"*. Önceden uyarı da işi
  bekletme de yok.
- *"drive dolduğuan özel değil drive kayıt olmadığında genel bir hata çıksın"*.
- Durduktan sonrası *"normal hata davranışı neyse o"*: bugün üretimi durduran bir hatada iş sıradan
  düşmüyor, yeniden başlatınca o kare yeniden çiziliyor.

**Sebep** *(497'nin coder'ı, 27 Ekim)*: Colab'ın Drive bağlantısı dosyayı önce kendi diskine alıp
"kaydedildi" diyor, Drive'a sonra arka planda gönderiyor. Drive dolu olduğunda bu gönderim sessizce
düştü; Queen Editor hiçbir hata görmedi. Google'ın kendi Colab kodu da bunu söylüyor:
`drive.flush_and_unmount` "bekleyen yazmaları gönderir". Silme sebep değil: aynı dosyayı paylaşan
kareyi koruyan kural var ve testi var, ve silme kaybı aynı oturumda gösterirdi. Kullanıcının
gördükleri de buna uyuyor *(27 Ekim — "collabte uyarı görnemdeimdrive doludu"; "bazıları krıık
dutuyordu açınca fotoğraf bulunamıyor diyordu muhtemeln jsona metadası gitmiş")*: kayıt satırı
Drive'a ulaştı, fotoğraf dosyası ulaşmadı.

**Drive API'ye geçilmiyor** *(kullanıcı, 27 Ekim — "şimdilik apiye geçmeyelim boşverelim onu sadece
drive mounted mı diye bakalım bir de drive dolu mu diye baklaım daha önce bunlardan patladık sadece")*.
Her kayıttan sonra dosyanın Google'a ulaştığını sormak için API gerekiyordu; v10'da (472) da
reddedilmişti. Bu yüzden Drive'ın kendi arka plan gönderiminin düşmesi bu maddede yakalanmıyor; madde
bilinen iki sebebi, bağlantının kopmasını ve Drive'ın dolmasını, kayıttan önce yakalıyor. Yukarıdaki
*"drive dolduğuan özel değil"* kararının yerini bu karar alıyor: dolu Drive için de ayrıca bakılır.

**Ne zaman bakılır:** her kayıttan önce *(kullanıcı, 27 Ekim — "1 den devam edleim o zaman")*.
Kullanıcı önce arka planda paralel bir bakış istedi *("parelel baksın sıralı bakya gerek yok")*; bakışın
tek bir sistem çağrısı olduğu, kaydı fark edilir biçimde bekletmediği, ve arka plandaki bir bakışın
iki bakış arasındaki kayıtları kaçıracağı söylenince kayıttan önce bakmayı seçti. "Drive bağlı mı"
bakışı v10'dan (472) beri her Drive işleminden önce var; bu madde yalnız yer bakışını ekliyor.

**Hata nerede görünür:** sıra durunca hata sıra panelinde görünür, başka bir yerde değil *(kullanıcı,
27 Ekim — "sıra panelinde görünüyorsa yeter hata")*. Ekrandan yapılan bir kayıt reddedilince — örneğin
Kuyruğa ekle — ekran sunucunun cümlesini gösterir, sabit bir metin değil.

<a id="v11-4"></a>
### 501 · v11-4 — Femboy ve futa LoRA'ları

**Kabul koşulu:** Femboy ve futa adaylarının deneme sonucu yazılı. Kullanıcının her biri için seçtiği
LoRA Queen Editor'de Nova ve DaSiWa'nın LoRA kutusunda seçilebiliyor.

**Kullanıcının kararları** *(27 Ekim)*: *"Seninle birlikte, deneme notebook'unda. femboysXL ve
Civitai'den 1–2 aday daha ComfyUI'de denenir, hangisinin kalacağına sen karar verirsin."*; *"bunu
yapalım sonra karar veridğimizi queen editore koyarız"*. Deneme notebook'u
`collab-toolbox/photo_experiments/` altına girer.
- **QueenAgent'a ne gider:** *"şöyle özel bir prompt gerkeilyors mesela bir tetik çümlesi bu roadmpai
  koşarken queen agent yeni bir görev aç unaligned gerkiyorsa tabi"*. Seçilen LoRA bir tetik cümlesi
  gibi özel bir prompt istiyorsa, koşu sırasında QueenAgent v12 roadmap'ine `UNALIGNED` yeni bir
  madde açılır; istemiyorsa açılmaz.
- **Sıra:** *"bir femboy taskını son al çünkü ban ihtiaçın olcak"*. Deneme kullanıcıyla birlikte
  yapıldığı için bu madde koşunun en sonunda yürür.
- **Futa da girer, aynı denemeye** *(kullanıcı, 27 Ekim — "futa içinde 3 model indirir msiin"; "bu
  taskı femboyla berabe yap zaten nerdeyse aynı şeyler 3 model yer,ne 6 tane denerim")*: femboy'un 3
  adayının yanına Civitai'den 3 futa LoRA'sı eklenir; tek notebook, tek Colab oturumu, 6 aday.
- **Yapılırken kararlaşan: deneme Nova'nın defterinde** *(kullanıcı, 28 Ekim — "photo generator novaya
  gerekli loraları indirttir ordan direkt kullanıp test edeyim foto experimentide silelim")*. Ayrı
  deneme defterinin workflow'ları Colab'da bozuk açıldı, ve Nova'nın `workflow_manual.json`'u elle
  sürüklenince de *"t.findInputSlot is not a function"* hatası çıktı (`impact-pack.js`). Altı aday
  `photo_generator/nova-3dcg/manual.ipynb`'den iner, deneme onun "Nova preset" hücresinde yazılı;
  `photo_experiments/femboy-futa-lora/` silindi. Hatanın sebebi Impact-Pack'le ComfyUI'nin yeni arayüzü
  arasında: arayüz 1.47'den beri node numaralarını yazı olarak tutuyor, Impact-Pack'in ImpactSwitch'i
  ise yüklenirken numarayı node yerine veriyor. Defter arayüzü 1.46.15'te sabitler; yerelde 1.57.6'da
  aynı hata çıktı, 1.46.15'te grafik hatasız ve eksik node'suz açıldı.
- **Yapılırken kararlaşan: kare yok, yalnız tetikler** *(kullanıcı, 28 Ekim — "ben senden kare yamanı
  istemedim yazdığı nyerdende temizle promtpları")*. Prompt'ları kullanıcı kendisi yazar; defterde
  adaylar, güçleri ve tetikleri kalır, POSITIVE'e tetik + `, ` + kendi prompt'u yazılır. Hazır kareler
  ve onlara dayanan karşılaştırma defterden, spec'ten ve plandan silindi.
- **Yapılırken kararlaşan: seçim — yalnız DaSiWa, iki futa seçeneği** *(kullanıcı, 28 Ekim — "tamam test
  ettim / bunlar dasiwa için olacak / 2 senecek olucak / 1 futa sadece futa flaccid olacak 0.50 ile / 2.
  seçenekte futa on male olacak buda 0.50 futa flaccid 1.00 futa on male olucak 2 lora / novada ikisde
  iyi çalımıyor çünkü / tetik kelilerini queen editor otomaik eklicek")*. Kabul koşulundaki "Nova ve
  DaSiWa'nın LoRA kutusu" bununla değişti: iki LoRA Nova'da iyi çizmediği için yalnız DaSiWa'nın kutusuna
  girer, Nova'nınki bugünkü gibi kalır. DaSiWa'nın kutusunda iki yeni seçenek var: **Futa** —
  `futa_flaccid_v3` 0,50, tek başına; **Futa on male** — `futa_flaccid_v3` 0,50 ve `futa_on_male_il_v2`
  1,00, ikisi birlikte. Tetikleri Queen Editor prompt'un önüne kendisi ekler: `flaccid futa`, ve ikincide
  `flaccid futa, futa on male, futa with male, futanari`. Femboy seçilmedi, Queen Editor'e girmez.
  QueenAgent'a madde açılmadı: istenen yalnız tetikler, onları Queen Editor ekliyor. İki dosya defterde
  yalnız DaSiWa işaretliyse iner; Nova'nın defterindeki altı aday ve deneme bölümü çıktı.
  - **Bir yan etki:** DaSiWa'nın artık kendi kutusu olduğu için seçimi de kendisinin. Nova'da seçilen
    Slime, DaSiWa'ya geçince DaSiWa'da görünmez; DaSiWa kendi seçimi yapılana kadar USNR'de açılır.
  - **Kullanıcının Colab'da deneyeceği:** `PHOTO_DASIWA` işaretliyken iki dosyanın inmesi (ilk koşuda
    aynada olmadıkları için Civitai'den, çerezle; sonraki koşularda aynadan) ve işaretsizken inmemesi;
    panelde DaSiWa seçiliyken LoRA kutusunda Futa ve Futa on male, Nova seçiliyken olmaması; Futa ve Futa
    on male ile birer DaSiWa karesi.

<a id="v11-5"></a>
### 500 · v11-5 — Eski belgeler ve roadmap'ler arşive

*(Kullanıcı, 26 Ekim — "ee bu belgeyi arayacak claude code böyle yaparsan queen editor roadmapine
eklemeyi ve düzeltemeyi belgleri ve eski roadmpaleri arşive almayı".)*

**Kabul koşulu:**
- Eski bir belgede adı geçen her belge, linkine tıklanınca açılıyor.
- `docs/roadmaps/`, `docs/specs/`, `docs/plans/`, `docs/research/` ve `docs/design-needs/` içinde
  yalnız açık sürümlerin ve açık işlerin belgeleri duruyor; bitenler `docs/arsiv/`'de.

`4403108a`, `docs/` kökündeki on çalışma notunu sildi ve onlara giden linkleri düz yazıya çevirdi.
Örneğin v6 roadmap'inde şimdi yalnız *"skill problemleri belgesi"* yazıyor. Bunu okuyan, Claude Code
da olsa, o belgeyi arar ve bulamaz.

**Kullanıcının kararları** *(27 Ekim)*:
- **Tek arşiv** *(cevap: "Önerim: 1")*: `docs/arsiv/`, içinde `roadmaps/`, `specs/`, `plans/`,
  `research/`, `design-needs/` ve `notlar/`.
- **Arşive girenler:** *"1'dekiler, ayrıca bitmiş işlere ait research/ ve design-needs/ belgeleri."*
  Yani biten sürümlerin roadmap'leri, spec'leri ve planları; git'ten geri gelen on not
  (`notlar/`'a); ve bitmiş işlere ait `research/` ile `design-needs/` belgeleri.
- Taşınan her belgeye giden linkler yeni yere göre düzeltilir, düz yazıya çevrilmiş linkler de yeniden
  link olur. Spec'lerin çoğu kendi roadmap'ine link veriyor, bu yüzden bu iş yüzlerce linke dokunur.
- **"Biten" ne demek** *(Claude'un kararı; kullanıcı, 27 Ekim — "sen karar ver")*: açık iki roadmap,
  Queen Editor v11 ve QueenAgent v12, dışındaki her roadmap biten sayılır; onlara ait spec, plan,
  research ve design-needs belgeleri de arşive girer.

<a id="v11-6"></a>
### 496 · v11-6 — Sürüm V11

*(Kullanıcı, 27 Ekim — "bir de her roadmapin başında şun uyapmanı istiyorum ui daki sürümü arttıralım
olur mu"; "ilk görev o olsun ynai".)*

**Kabul koşulu:** Queen Editor'ün ekranında "Queen Editor V11" yazıyor; bugün "V10".

<a id="v11-7"></a>
### 508 · v11-7 — Qwen kalkar

*(Kullanıcı, 28 Ekim, koşunun sonundaki Colab denemesinde — "qweni kaldıralım iyi bir şey üretmiyor
gereksiz kalabalık".)*

**Kabul koşulu:** Queen Editor'de Qwen Image 2.1 Turbo yok: model listesinde, LoRA kutusunda ve
defterin CONFIG'inde görünmüyor, defter onun dosyalarını indirmiyor. 499'un Qwen'le gelen her parçası
— graph'ı, üreticisi, LoRA satırı, testleri — gider; Krea'nın SNOFS + Slime'ı ve Boş'u kalır. Daha önce
Qwen'le çizilmiş fotoğraflar Drive'da durur.

<a id="v11-8"></a>
### 509 · v11-8 — "Orada mısın?" kalkar, üretim bitince bildirim gelir

*(Kullanıcı, 29 Ekim — "10 dk sorma olayında kullanıc aktif olsada videoları inceleip silsede orda mısın
diye soruyo".)*

**Kabul koşulu:**
- 10 dk'lık geri sayım ve "orada mısın?" kutusu yok; kullanıcı ne yaparsa yapsın çıkmıyor.
- Sıra boşalınca, yani sıradaki bütün fotoğraf ve videolar bitince, bir kez tarayıcı bildirimi
  geliyor. Bildirim A100 demiyor.

**Bugün:** [498](#v11-2) sıra boş kaldıkça her 10 dk'da bir kutu ve bildirim çıkarıyor; ekranda çalışan
kullanıcıyı görmüyor, ve cümlesi her oturumda "A100" diyor.

**Kullanıcının kararları** *(29 Ekim)*:
- **Basit olsun:** *"bu özelliği kaldır üretim bitince bildirim atsın yeter bu kadar basit yapalım"*.
  Önce etkileşimi de sayan bir kural konuşuldu (*"10 dakikadır üretim yoksa && 10 dakikadır etkileşim
  yoksa"*); kullanıcı onu karışık bulup bıraktı.
- **"Üretim bitti" ne demek** *(cevap: "Sıra boşalınca: sıradaki bütün fotoğraf ve videolar bitince")*:
  export'un bitişi bildirim getirmez.
- **Sıra boşalmadan durunca da** *(cevap: "gelsin"; yapılırken reviewer'ın sorusu üzerine)*: sıra bir
  hatayla ya da kurulu olmayan bir model yüzünden durunca da kendi cümlesiyle bildirim gelir. Durdur'a
  basılınca gelmez; basan zaten ekranın başında.
- **A100:** *"sürekli a100 diyor ama hep a100 kualnımıyor garip oluyor"*.

<a id="v11-9"></a>
### 510 · v11-9 — Videonun sesi kartından kapatılabilir

*(Kullanıcı, 29 Ekim — "bir m3 sesli video üretebiliyor ama bzen sesin kapatmak istiyourz spefisfik bir
videonun exportt olurken yapamıyoruz".)*

**Kabul koşulu:** Yandaki video ekranında, sesi olan her videonun kartının sağ üstünde bir ses ikonu
var; basınca o videonun sesi kapanıyor, bir daha basınca açılıyor. Sesi kapalı video export'ta sessiz,
öteki videolar sesli çıkıyor. Ses projede durmaya devam ediyor; yalnız kapalıyken export'a girmiyor.

**Bugün:** export her karenin videosuna, varsa o karenin MMAudio sesini ekliyor. Tek bir kare için sesi
atlamanın yolu yok.

**Kullanıcının kararları** *(29 Ekim)*:
- **Hangi ses:** MMAudio'nun sesi; Queen Editor'de videoya ses ekleyen tek model o.
- **Nereden:** *"export erkanında değil cardlarlar sesi olan video sesini kaptma özelliğ olursa daha güzel
  olur"*; *"yan vidoe ekranınd acardda sağ üste fala nses ikonu aç kapa yapıyor gibi düşün"*.
- **Kalıcı:** kapatılan ses, yeniden açılana kadar kapalı kalır.
