# Queen Studio — Yol Haritası v1

**Tarih:** 2026-11-06 · **Koşu dalı:** `feat/queen-studio-v1` · **Durum:** 9/42 · koşuyor

queen-studio, queen-editor'ın özelliklerini bir AI agent'ın kullanabileceği biçimde sunan yeni bir
araç. Ne yaptığı [tasarım adımlarında](../research/2026-11-03-yeni-editor-v1-tasarim-adimlar.md).

Maddeler aşağıdaki sırayla, tek tek yapılır. İlk madde kurulumdur ve kullanıcıyla yapılır; ondan sonra
koşu durmaz. Son iki madde de kullanıcıyla: Pro'daki deneme ve DeepSeek harness'ı.

---

| Numara | İş | Durum |
|---|---|---|
| 525 · [v1-1](#v1-1) | Kurulum, kullanıcıyla adım adım | ✅ *(Colab Secrets CLI'da okunmuyor; [kararlar](2026-11-06-queen-studio-v1-kararlar.md#sapmalar))* · `ALIGNED` |
| 526 · [v1-2](#v1-2) | Aracın kuralları, tasarımcı ve tasarım reviewer'ı | ✅ · `ALIGNED` |
| 527 · [v1-3](#v1-3) | İskelet ve ilk ekran, sürüm V1 | ✅ · `ALIGNED` |
| 528 · [v1-4](#v1-4) | Drive'ın ölçümleri | ✅ *(ayrılmış kimliklerin 1, 3, 7 günlük bakışı 7, 9, 13 Kasım'da)* · `ALIGNED` |
| 529 · [v1-5](#v1-5) | Ortak sözleşme: hatalar, başlıklar, `GET /api` | ✅ · `ALIGNED` |
| 530 · [v1-6](#v1-6) | Liste sorgusu | ✅ *(regex yerine `like`/`ilike`; [kararlar 11](2026-11-06-queen-studio-v1-kararlar.md#sapmalar))* · `ALIGNED` |
| 531 · [v1-7](#v1-7) | Depo portu ve bellek içi adaptör | ✅ *(port kare, iş, edit bilmez; [kararlar 13](2026-11-06-queen-studio-v1-kararlar.md#sapmalar))* · `ALIGNED` |
| 532 · [v1-8](#v1-8) | Drive adaptörü: projeler ve kayıtlar | ✅ *(her mühür yeni blok; [kararlar 16](2026-11-06-queen-studio-v1-kararlar.md#sapmalar))* · `ALIGNED` |
| 533 · [v1-42](#v1-42) | Yapılmış kodun sınırları | ✅ *(bağlantı değil gövde; [kararlar 17](2026-11-06-queen-studio-v1-kararlar.md#sapmalar))* · `ALIGNED` |
| [v1-9](#v1-9) | Drive adaptörü: dosyalar | `ALIGNED` |
| [v1-10](#v1-10) | Bir değişiklik ve aynı istek iki kez | `ALIGNED` |
| [v1-34](#v1-34) | History | `ALIGNED` |
| [v1-11](#v1-11) | Projeler | `ALIGNED` |
| [v1-12](#v1-12) | Kareler | `ALIGNED` |
| [v1-13](#v1-13) | Medya | `ALIGNED` |
| [v1-14](#v1-14) | Modeller | `ALIGNED` |
| [v1-35](#v1-35) | Model indirme | `ALIGNED` |
| [v1-15](#v1-15) | İşler | `ALIGNED` |
| [v1-16](#v1-16) | ComfyUI kapısı: süreç | `ALIGNED` |
| [v1-36](#v1-36) | ComfyUI kapısı: graflar | `ALIGNED` |
| [v1-17](#v1-17) | Kuyruk | `ALIGNED` |
| [v1-37](#v1-37) | Kuyruğun beklemeleri ve başka projenin kuyruğu | `ALIGNED` |
| [v1-18](#v1-18) | Kuyruğun kendiliğinden durması ve core'un yeniden başlaması | `ALIGNED` |
| [v1-19](#v1-19) | Kuyruk iki Colab'da | `ALIGNED` |
| [v1-20](#v1-20) | Edit'ler | `ALIGNED` |
| [v1-21](#v1-21) | Export: videonun yapılması | `ALIGNED` |
| [v1-38](#v1-38) | Export: iptal, geri alma ve sınırlar | `ALIGNED` |
| [v1-22](#v1-22) | MCP adaptörü | `ALIGNED` |
| [v1-23](#v1-23) | Resimler resim olarak gider | `ALIGNED` |
| [v1-24](#v1-24) | Agent senaryoları | `ALIGNED` |
| [v1-25](#v1-25) | Başlatıcı ve notebook | `ALIGNED` |
| [v1-39](#v1-39) | Log'un Drive'a gitmesi ve boştayken sıfır çağrı | `ALIGNED` |
| [v1-26](#v1-26) | ComfyUI'nin Colab ölçümleri | `ALIGNED` |
| [v1-27](#v1-27) | Colab testleri | `ALIGNED` |
| [v1-40](#v1-40) | Colab'da dayanıklılık, gerçek Drive'la | `ALIGNED` |
| [v1-28](#v1-28) | UI tasarımı: dil, projeler ve kareler, örnek veriyle | `ALIGNED` |
| [v1-41](#v1-41) | UI tasarımı: kuyruk, agent, bildirim, silmek ve edit'ler | `ALIGNED` |
| [v1-29](#v1-29) | UI bağlantısı: projeler ve kareler | `ALIGNED` |
| [v1-30](#v1-30) | UI bağlantısı: kuyruk ve agent'ın yaptığı | `ALIGNED` |
| [v1-31](#v1-31) | UI bağlantısı: silmek ve edit'leri izlemek | `ALIGNED` |
| [v1-32](#v1-32) | Pro'da tek deneme, kullanıcıyla | `ALIGNED` |
| [v1-33](#v1-33) | DeepSeek harness'ı, kullanıcıyla | `ALIGNED` |

---

<a id="v1-1"></a>
### v1-1 — Kurulum, kullanıcıyla adım adım

*([13. adım, Yapım planı](../research/2026-11-03-yeni-editor-v1-13-yapim-plani.md);
[10. adım, Barındırma](../research/2026-11-03-yeni-editor-v1-10-barindirma.md))*

**Kabul koşulu:**
- Ücretsiz katman ve Drive testleri için ayrı bir deneme Google hesabı var.
- Bu makineden deneme hesabının Drive'ına API'yle gidiliyor; token depoda durmuyor.
- Deneme hesabının Colab Secrets'ında Hugging Face token'ı ve Civitai cookie'si var.
- Google'ın Colab CLI'ı bu makinede çalışıyor ve onunla açılan ücretsiz bir T4'te ilk deneme koştu.
- Testlerin ve Colab CLI'ın hesap ayarı yalnız deneme hesabını gösteriyor.

<a id="v1-2"></a>
### v1-2 — Aracın kuralları, tasarımcı ve tasarım reviewer'ı

*([5. adım, Backend yığını](../research/2026-11-03-yeni-editor-v1-5-backend-yigini.md);
[11. adım, Kod standardı](../research/2026-11-03-yeni-editor-v1-11-kod-standardi.md);
[13. adım, Yapım planı](../research/2026-11-03-yeni-editor-v1-13-yapim-plani.md);
[9. adım, UI](../research/2026-11-03-yeni-editor-v1-9-ui.md))*

**Kabul koşulu:**
- `queen-studio/FOUNDATION.md` ve `queen-studio/CODE-STANDARD.md` var; 5. ve 11. adımdan, öbür
  araçlarınki gibi kodun neden öyle kurulduğunu söylüyorlar.
- CLAUDE.md dört aracı sayıyor: queen-studio'nun kural dosyaları, UI'ının İngilizce olduğu, bir
  maddenin yalnız onun suite'lerini koştuğu ve ekranlarının queen-design'da değil bu repoda
  tasarımcıyla tasarlandığı yazıyor.
- `.claude/agents/designer.md` var: tasarımcı ekranları gerçek UI kodunda örnek veriyle kurar,
  `frontend-design`'ı ve kısa UX kontrol listesini kullanır, bağlantı yazmaz (13. ve 9. adım).
- `.claude/agents/design-reviewer.md` var: tasarım reviewer'ı deneyime bakar.
- CLAUDE.md'nin Subagents bölümü ikisini de anıyor.
- `queen-studio/BACKLOG.md` var, öbür araçlarınki gibi; yolda bulunup bu koşuya girmeyen iş oraya
  yazılır.

Yalnız belge; QA'sız.

<a id="v1-3"></a>
### v1-3 — İskelet ve ilk ekran, sürüm V1

*([13. adım, Kod](../research/2026-11-03-yeni-editor-v1-13-yapim-plani.md);
[5. adım](../research/2026-11-03-yeni-editor-v1-5-backend-yigini.md);
[6. adım, Adresler ve Discovery](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md))*

**Kabul koşulu:**
- `queen-studio/` var; core bu makinede tek komutla açılıyor ve UI'ı aynı adresten sunuyor: `/api`
  core'un, gerisi UI'ın.
- `GET /api/health` uygulamayı, core'un kimliğini ve sürümünü söylüyor, Drive'a gitmiyor.
- Ekran yalnız "Queen Studio V1" yazan bir yer tutucu sayfa; tasarlanan ekranlar sonda onun yerine
  geçer.
- Uygulamanın adı kodda tek yerde yazılı; adı değiştirmek tek yeri değiştirmek.
- UI'ın türleri `/api/openapi.json`'dan üretiliyor ve `tsc` onlara bakıyor.
- Core'un log'u diske yazılıyor; notebook'un çıktısı ve 5 dakikada bir Drive'a gitmesi
  [v1-25](#v1-25)'te eklenir.
- Suite'ler ve kontrol araçları (11. adım) birer testle yeşil; suite'lerin ve UI'ın derleme komutu
  CLAUDE.md'de. Derlenen `dist` commit'lenir, öbür araçlardaki gibi.

<a id="v1-4"></a>
### v1-4 — Drive'ın ölçümleri

*([4. adım, Depo — Ölçülmemiş varsayımlar](../research/2026-11-03-yeni-editor-v1-4-depo.md);
[10. adım, Colab'da ölçülecekler](../research/2026-11-03-yeni-editor-v1-10-barindirma.md))*

**Kabul koşulu:**
- 4. adımın ölçülmemiş varsayımlarının her biri ve çağrı süreleri ölçüldü: bu makineden deneme
  hesabıyla, bir kez de Colab'ın ücretsiz katmanında. Dört Colab'ın hız sınırı bu makineden, deneme
  hesabıyla dört süreçle ölçülür.
- Sonuçlar depoda kayıtlı; kodun dayandığı sayılar sonra onunla sınanır.
- Tutmayan varsayım varsa tasarım düzeltildi ve 4. adıma yazıldı; depo maddeleri ondan sonra başlar.

<a id="v1-5"></a>
### v1-5 — Ortak sözleşme: hatalar, başlıklar, `GET /api`

*([6. adım, Ortak kurallar ve Hatalar](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md);
[1. adım, Discovery](../research/2026-11-03-yeni-editor-v1-1-ozellik-envanteri.md);
[11. adım, Mesajlar](../research/2026-11-03-yeni-editor-v1-11-kod-standardi.md))*

**Kabul koşulu:**
- Her hata, FastAPI'nin kendi doğrulama hataları da, dört alanla dönüyor; hint kuralına her hata
  cevabında kendiliğinden bakılıyor.
- Değiştiren istek `Idempotency-Key` ve `Actor` olmadan yapılmıyor; bilinmeyen alan sessizce atılmıyor.
- `GET /api` kısa bir dizin, `?path=` bir adresin ayrıntısı; ikisi de koddan çıkıyor ve endpoint
  eklenince dizin bir satır büyüyor. Boyu kayıtlı bir sınırı aşarsa test düşüyor.
- Boy sınırı hata cevaplarına da bakıyor.

*(Kullanıcı, 5 Kasım — "token olarak efficient olsun, model tool listesi ve ne yaptığını bilsin, gerekince
detaylı olarak o endpoint'e baksın".)*

<a id="v1-6"></a>
### v1-6 — Liste sorgusu

*([6. adım, Liste sorgusu, Toplu seçim, Konum](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md))*

**Kabul koşulu:**
- Listeleyen her endpoint aynı PostgREST sorgusunu alıyor: süzmek, regex, tarih aralığı, sıralama,
  sayfa, alan seçimi. `imatch` Türkçe ve İngilizce i'leri birlikte buluyor.
- Yanlış sorgu, o listenin alanlarını sayan bir hatayla dönüyor; sorgu bellekte çalışıyor, Drive'a
  gitmiyor.
- Toplu seçim aynı süzgeçle; süzgeçsiz toplu istek `?all=true` olmadan reddediliyor.
- Listelerin varsayılan alan setinin boyu da kayıtlı bir sınırla sınanıyor.

*(Kullanıcı, 5 Kasım — "süzülsün, PostgREST dediğin olsun".)*

<a id="v1-7"></a>
### v1-7 — Depo portu ve bellek içi adaptör

*([4. adım, Depo — Depo portu, Bellek içi adaptör](../research/2026-11-03-yeni-editor-v1-4-depo.md))*

**Kabul koşulu:**
- Core veriye yalnız port üzerinden ulaşıyor; port projenin kayıtlarını anlatıyor, Drive'ın dosyalarını
  değil. Kalıcı silme yok, yalnız çöp.
- Bellek içi adaptör hata enjekte edebiliyor (yazmadan önce ya da sonra düşmek, yavaşlamak, reddetmek),
  aynı depo üstünde ikinci bir core açılabiliyor, saat dışarıdan veriliyor.
- Port'un sözleşme testleri bellek içi adaptörde yeşil; aynıları Drive adaptöründe de koşacak.

<a id="v1-8"></a>
### v1-8 — Drive adaptörü: projeler ve kayıtlar

*([4. adım, Depo](../research/2026-11-03-yeni-editor-v1-4-depo.md))*

**Kabul koşulu:**
- Port'un proje işlemleri Drive'da çalışıyor; sözleşme testleri taklit Drive API'ye karşı ve bu
  makineden gerçek Drive'da, deneme hesabıyla yeşil.
- Bir değişiklik Drive'a iki çağrı; proje büyüdükçe çağrı sayısı artmıyor; sayılar 4. adımın tablosuyla
  tam eşit.
- Hız sınırında istek yavaşlıyor, kaybolmuyor; belirsiz ya da reddedilen yazma Drive'ın sözüyle dönüyor;
  okunamayan bir baş dosyasının üstüne yazılmıyor.

<a id="v1-42"></a>
### v1-42 — Yapılmış kodun sınırları

*([CODE-STANDARD, Cost](../../queen-studio/CODE-STANDARD.md#cost);
[kararlar 12](2026-11-06-queen-studio-v1-kararlar.md#sapmalar))*

Yolda bulundu: madde 12'nin denetimi 527–529'un kodunda *(kullanıcı, 6 Kasım — "bundan ders çıkar hem
geçmiş hem gelecek değişikliklere bak"; "sen karar ver")*.

**Kabul koşulu:**
- `GET /api/health` bekleyen istekler sunucunun iş parçacıklarını doldursa da cevap veriyor.
- Gövde sınırı en büyük gerçek gövdeye göre (1 MiB); kötü bir gövdenin hatası yalnız gösterilen
  sorunları biçimliyor, kalanı sayıyor; liste alanlarının en çok öğesi var.
- Bellekte aynı anda tutulan istek gövdelerinin sınırı var; aşılınca dört alanlı hatayla reddediliyor.
- Her sınır küçük kurulmuş bir testle.

<a id="v1-9"></a>
### v1-9 — Drive adaptörü: dosyalar

*([4. adım, Depo — Depo portu, Kota çöp ve hesap](../research/2026-11-03-yeni-editor-v1-4-depo.md))*

**Kabul koşulu:**
- Port'un dosya işlemleri Drive'da çalışıyor; sözleşme testleri iki adaptörde ve gerçek Drive'da yeşil.
- Aynı yüklemenin tekrarı ikinci dosya bırakmıyor; kopan büyük yükleme kaldığı yerden sürüyor, yarım
  dosya kalmıyor; core hiçbir dosyayı kalıcı silmiyor.
- Çağrı sayıları 4. adımın tablosuyla tam eşit.

<a id="v1-10"></a>
### v1-10 — Bir değişiklik ve aynı istek iki kez

*([4. adım, Bir değişiklik ve Değerlendirme](../research/2026-11-03-yeni-editor-v1-4-depo.md);
[6. adım, Aynı istek iki kez](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md);
[2. adım, Her şey için ve History kaydı](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md))*

**Kabul koşulu:**
- Bir istek ya bütünüyle oluyor ya hiç ve engellerin hepsini sayıyor; bir projenin değişiklikleri
  birbirinin arasına girmiyor, öbür projeler ve okumalar beklemiyor.
- Aynı istek iki kez yapılmıyor, core yeniden başlasa da; 4. adımın Dayanıklılık tablosunun bu maddeye
  düşen satırları hata enjekte eden testlerle.
- Projeyi sırayla iki core'da değiştirmek birinin değişikliğini silmiyor; aynı saniyede kaybolan
  değişiklik söyleniyor.
- Her değişiklik history'de bir kayıt olarak yazılıyor; okunması [v1-34](#v1-34)'te.
- Bir projenin kilidini bekleyen istek sınırsız beklemiyor; aynı istek iki kez dizini anahtarları
  tutuyor, kayıtları değil. Değişikliklerin cevabındaki listeler en çok 20 öğe, gerisi sayıyla.

<a id="v1-34"></a>
### v1-34 — History

*([6. adım, History](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md);
[2. adım, History kaydı](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md))*

[v1-10](#v1-10)'dan bölündü *(kullanıcı, 6 Kasım — "roadmapte başka böyle büyük task varsa onları da
parçalara bölelim")*.

**Kabul koşulu:**
- `GET /projects/{p}/history` süzülüyor, sayfalanıyor; kayıt değişmiyor.
- Eski bir sayfa ya da süzgeç eski blokları sınırsız indirmiyor: bir istek sınırlı sayıda blok tarar,
  durursa nereden süreceğini söyler.

<a id="v1-11"></a>
### v1-11 — Projeler

*([1. adım, Projects](../research/2026-11-03-yeni-editor-v1-1-ozellik-envanteri.md);
[2. adım, Proje](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md);
[4. adım, Proje oluşturma, Başka Colab'ın yaptığını görmek, Bellek ve disk](../research/2026-11-03-yeni-editor-v1-4-depo.md))*

**Kabul koşulu:**
- Proje oluşturuluyor, listeleniyor, adı değişiyor, arşivleniyor; aynı adlı başka proje cevapta
  söyleniyor, kurala uymayan ad hangi kuralı bozduğunu söylüyor.
- Silinen projenin her şeyi, bitmiş export'lar dışında, Drive'ın çöpüne gidiyor ve ondan hiçbir şey
  okunmuyor.
- Başka bir Colab'daki değişiklik birkaç saniye içinde görünüyor; core yalnız istenen projeyi yüklüyor.
- Core yeniden başlasa da aynı anahtarla gelen oluşturma ikinci bir proje açmıyor.
- Belleğe sığmayacak kadar büyük proje yüklenmiyor, nedeni söyleniyor; yüklü projeler core'un bellek
  sınırını aşmıyor.

*(Kullanıcı, 5 Kasım — "komple silinsin, history'si okunamasın".)*

<a id="v1-12"></a>
### v1-12 — Kareler

*([1. adım, Frames](../research/2026-11-03-yeni-editor-v1-1-ozellik-envanteri.md);
[2. adım, Kare ve Karelerin sırası](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md);
[6. adım, Frames](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md))*

**Kabul koşulu:**
- Kareler sırasıyla listeleniyor ve süzülüyor; bir kare taşınıyor, bütün sıra tek seferde veriliyor ve
  eksik ya da fazla kare söyleniyor.
- Bir kare, birçok kare ya da bir karenin videosu siliniyor; videosu silinen kare aynı kimlikle, aynı
  yerde kalıyor.
- Paylaşılan fotoğraf, onu kullanan kare de iş de kalmayınca çöpe gidiyor.
- Bir projede en çok 20.000 kare, sahne en çok 500 karakter; toplu silme en çok 1000 kareye dokunuyor,
  cevabı en çok 100 kimlik ve sayı.

<a id="v1-13"></a>
### v1-13 — Medya

*([1. adım, Media](../research/2026-11-03-yeni-editor-v1-1-ozellik-envanteri.md);
[6. adım, Medya](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md);
[4. adım, Bellek ve disk](../research/2026-11-03-yeni-editor-v1-4-depo.md))*

**Kabul koşulu:**
- Karenin fotoğrafı tam ya da küçük boyutta, videosu ve videonun saniye saniye durağan görüntüleri
  alınıyor; her resim kendi çağrısının cevabı.
- Dosya ilk istekte Drive'dan, sonra diskten geliyor; küçük boyut ve durağan görüntüler diskte
  üretiliyor, saklanmıyor.
- ffmpeg'in hatası ffmpeg'in sözüyle dönüyor.
- Aynı anda en çok 2 ffmpeg, her biri süre ve bellek sınırıyla; sırası gelmeyen istek kısa bir
  beklemeden sonra "meşgul" alıyor.

*(Kullanıcı, 5 Kasım — "genel bakış için 1 saniye arayı biz yapalım".)*

<a id="v1-14"></a>
### v1-14 — Modeller

*([1. adım, Models](../research/2026-11-03-yeni-editor-v1-1-ozellik-envanteri.md);
[2. adım, Modeller](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md);
[10. adım, Modeller](../research/2026-11-03-yeni-editor-v1-10-barindirma.md))*

**Kabul koşulu:**
- `GET /models` indirilebilecek her ana modeli ve bu Colab'daki durumunu söylüyor; `GET /models/{id}`
  seçilebilecek her şeyi.
- Bu Colab'ın kartında çalışmayan model reddediliyor.
- Modeller ve LoRA seçimleri queen-editor'ın bugünküleridir; listesi (dosyalar, kaynaklar, güçler,
  tetikler) queen-editor'dan veri olarak alınır, kodu alınmaz.

*(Kullanıcı, 5 Kasım — "gidip T4'e H3 indirmeyelim".)*

<a id="v1-35"></a>
### v1-35 — Model indirme

*([10. adım, Modeller](../research/2026-11-03-yeni-editor-v1-10-barindirma.md);
[2. adım, Modeller](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md))*

[v1-14](#v1-14)'ten bölündü *(kullanıcı, 6 Kasım)*.

**Kabul koşulu:**
- Agent bir modeli önceden de indirtebiliyor; LoRA'ları ve yardımcı dosyaları onunla iniyor.
- İnen model yüzdesiyle görünüyor; `GET /models/{id}/wait` inmesi bitene kadar bekliyor.
- İnemeyen model üç denemeden sonra kaynağın sözüyle "inemedi" görünüyor.
- Diskte yer yetmeyen indirme başlamıyor; yarım inen dosya model sayılmıyor; aynı anda tek indirme.
- Takılan bağlantı süre sınırında kesiliyor; Civitai'nin anahtarı hata ve log'da görünmüyor.

*(Kullanıcı, 5 Kasım — "agent indirmeyi seçsin böylece önceden hazırlık bile yapabilir".)*

<a id="v1-15"></a>
### v1-15 — İşler

*([1. adım, Jobs](../research/2026-11-03-yeni-editor-v1-1-ozellik-envanteri.md);
[2. adım, İş](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md);
[6. adım, Jobs](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md))*

**Kabul koşulu:**
- `t2i` ve `i2v` iş veriyor; eksik ya da modelin almadığı alan hata; yalnız üretim alanlarından seed'in
  varsayılanı var.
- İş verildiği an karesi sıraya giriyor ve cevap düşeceği kareyi söylüyor.
- Modeli kurulu olmayan ve inmeyen iş verilemiyor; hint indirmeyi gösteriyor.
- İşler listeleniyor, tek tek ya da toplu çıkarılıyor; işi kuyrukta olan kare ve videosu silinmiyor.
- Prompt en çok 4000, negatif en çok 2000 karakter; seed JSON'un kesin taşıdığı aralıkta; bir projede
  en çok 1000 bekleyen iş (`queue_full`).

*(Kullanıcı, 3 Kasım — "Seed gibi gerçekten sorun olmayacak şeylerin varsayılan değeri olabilir, ama
video promptu gibi şeyler olmaz.")*

<a id="v1-16"></a>
### v1-16 — ComfyUI kapısı: süreç

*([7. adım, Hatalar ve süreler](../research/2026-11-03-yeni-editor-v1-7-uretim-ve-kuyruk.md);
[12. adım, Birim testle sınanamayanlar](../research/2026-11-03-yeni-editor-v1-12-test-stratejisi.md))*

**Kabul koşulu:**
- Core ComfyUI'yi kendisi başlatıyor ve cevap vermezse yeniden başlatıyor.
- Takılan üretim süre sınırında duruyor, iptal başka bir işe çarpmıyor; ComfyUI'nin hatası kendi
  sözüyle geliyor.
- İşin üretim süresi kaydında, ayrıntılı süreler log'da.
- ComfyUI'ye her çağrının süre sınırı var; kaydedilen hata ve durma nedeni kısa tutuluyor; ComfyUI'nin
  çıktı ve geçici klasörleri Colab'ın diskini doldurmuyor.

<a id="v1-36"></a>
### v1-36 — ComfyUI kapısı: graflar

*([2. adım, İş — Varyantlar](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md);
[7. adım](../research/2026-11-03-yeni-editor-v1-7-uretim-ve-kuyruk.md))*

[v1-16](#v1-16)'dan bölündü *(kullanıcı, 6 Kasım)*.

**Kabul koşulu:**
- Her modelin ComfyUI'ye giden grafı doğru (prompt, seed, LoRA, yön, uzunluk). Graflar
  queen-editor'dan veri olarak alınır.
- Art arda varyantlar, kart kaldırıyorsa birlikte üretiliyor.

<a id="v1-17"></a>
### v1-17 — Kuyruk

*([1. adım, Queue](../research/2026-11-03-yeni-editor-v1-1-ozellik-envanteri.md);
[2. adım, Kuyruk](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md);
[4. adım, Kuyruk ve Bir iş](../research/2026-11-03-yeni-editor-v1-4-depo.md);
[7. adım, Yarışlar](../research/2026-11-03-yeni-editor-v1-7-uretim-ve-kuyruk.md))*

**Kabul koşulu:**
- İş verilince kuyruk kendiliğinden çalışıyor; sırayı agent veriyor, kuyruk durduruluyor, sürdürülüyor,
  boşaltılıyor.
- Bu Colab'da proje silmek çalışan işi durduruyor ve kuyruğu boşaltıyor.
- Kendiliğinden durmuş kuyruğa verilen iş kabul ediliyor, cevap `stop_reason`'ı taşıyor.
- GPU yalnız işin başlamasındaki bakışı bekliyor; işin bitirilmesi GPU'nun yolunun dışında.

<a id="v1-37"></a>
### v1-37 — Kuyruğun beklemeleri ve başka projenin kuyruğu

*([2. adım, Kuyruk](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md);
[4. adım, Kuyruk](../research/2026-11-03-yeni-editor-v1-4-depo.md);
[7. adım, Yarışlar](../research/2026-11-03-yeni-editor-v1-7-uretim-ve-kuyruk.md))*

[v1-17](#v1-17)'den bölündü *(kullanıcı, 6 Kasım)*.

**Kabul koşulu:**
- Sırası gelen işin modeli iniyorsa kuyruk `waiting_model` der ve bekler.
- Bu Colab başka bir projenin kuyruğunu çalıştırırken verilen iş bekliyor; `resume` öbürünü bırakıyor
  (`released`).
- `/wait` kendiliğinden ilerlemeyen kuyrukta hemen dönüyor ve nedenini söylüyor; bekleyen `/wait`
  sunucunun bir iş parçacığını tutmuyor.

<a id="v1-18"></a>
### v1-18 — Kuyruğun kendiliğinden durması ve core'un yeniden başlaması

*([2. adım, Kuyruk](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md);
[4. adım, Kuyruk, Bir iş ve Kota](../research/2026-11-03-yeni-editor-v1-4-depo.md);
[6. adım, Export'un ve kuyruğun nedenleri](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md);
[7. adım, Hatalar ve süreler](../research/2026-11-03-yeni-editor-v1-7-uretim-ve-kuyruk.md))*

**Kabul koşulu:**
- Kendiliğinden durunca nedenini söylüyor: işin hatası (ComfyUI işi reddetti ya da üretim süresi
  doldu), ComfyUI, model inemedi, Drive'da yer yok, ürün yüklenemedi. Her birinde iş kaybolmuyor ve
  `resume` sürdürüyor; her neden için bir test.
- Kaynak karesi silinmiş `i2v` işi saklanan fotoğrafla yapılıyor.
- Core iş ortasında yeniden başlasa da hiçbir iş iki kez yapılmıyor, kaybolmuyor; kuyruk ComfyUI
  açılınca sürüyor, önceden durdurulmuşsa durmuş kalıyor.

*(Kullanıcı, 5 Kasım — "o case zaten kuyruğun durması acayip düşük, öyle olursa da dursun queue".)*

<a id="v1-19"></a>
### v1-19 — Kuyruk iki Colab'da

*([4. adım, Kuyruk ve Değerlendirme 4](../research/2026-11-03-yeni-editor-v1-4-depo.md);
[2. adım, Kuyruk](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md))*

**Kabul koşulu:**
- `resume` kuyruğu başka bir Colab'dan alıyor; öbürü en geç 30 sn içinde bırakıyor, yarıdaki iş burada
  baştan üretiliyor.
- Kapanmış bir Colab'ın kuyruğu kaldığı yerden sürüyor; kapanmış olabilecek Colab'ı `/wait` hemen
  söylüyor.
- Başka Colab'dan gelen durdurma, iptal ve proje silme kuyruğu çalıştıran Colab'da 30 sn içinde etkili.
- Hepsi aynı depoda iki core'lu testlerle.

*(Kullanıcı, 4 Kasım — "neredeyse bitmiş bir iş atılsın, bunun bize bir zararı yok, basitse".)*

<a id="v1-20"></a>
### v1-20 — Edit'ler

*([1. adım, Edits](../research/2026-11-03-yeni-editor-v1-1-ozellik-envanteri.md);
[2. adım, Edit ve yerleri](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md);
[6. adım, Edits](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md))*

**Kabul koşulu:**
- Edit oluşturuluyor, adı değişiyor, siliniyor; kareler kalıyor.
- Yerler ekleniyor, çıkarılıyor, taşınıyor, bütün sıra veriliyor; aynı kare birçok yerde olabiliyor; bir
  yerin sesi kapatılıyor.
- Karesi silinen yer "silindi" gösteriyor, agent onu çıkarana ya da başka kareye çevirene kadar.
- Bir edit'te en çok 5000 yer, bir projede en çok 200 edit.

<a id="v1-21"></a>
### v1-21 — Export: videonun yapılması

*([1. adım, Exports](../research/2026-11-03-yeni-editor-v1-1-ozellik-envanteri.md);
[2. adım, Export](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md);
[4. adım, Export](../research/2026-11-03-yeni-editor-v1-4-depo.md);
[7. adım, Export](../research/2026-11-03-yeni-editor-v1-7-uretim-ve-kuyruk.md))*

**Kabul koşulu:**
- Bir edit tek bir birleşik videoya çevriliyor; önce ne çıkacağı gösterilebiliyor; engel varsa başlamıyor
  ve yerleri sayıyor.
- Dosyalar Drive'da `exports/` altında, ad kuralına uyan kendi klasöründe, fotoğraflarıyla; video
  oynuyor. Export testleri bu makinede gerçek ffmpeg'le. Uyarı görseli queen-editor'dan veri olarak
  alınır.
- 7. adımın ffmpeg tuzaklarının her biri testle; belleği klip sayısıyla büyümüyor.

<a id="v1-38"></a>
### v1-38 — Export: iptal, geri alma ve sınırlar

*([4. adım, Export](../research/2026-11-03-yeni-editor-v1-4-depo.md);
[7. adım, Export](../research/2026-11-03-yeni-editor-v1-7-uretim-ve-kuyruk.md))*

[v1-21](#v1-21)'den bölündü *(kullanıcı, 6 Kasım)*.

**Kabul koşulu:**
- Süren export iptal ediliyor, yarıda kalan export yazdıklarını geri alıyor; süren bir export'un
  kullandığı kare silinmiyor.
- Proje silmek süren export'u durduruyor ve klasörünü çöpe atıyor.
- Colab başına bir export (`export_running`); Drive'da yer yetmezse `storage_low`, Colab'ın diskinde
  yer yetmezse başlamıyor.
- Başka Colab'ın yaptığı export'un `/wait`'i hemen dönüyor ve iptal yolunu söylüyor.

<a id="v1-22"></a>
### v1-22 — MCP adaptörü

*([8. adım, Agent tarafı](../research/2026-11-03-yeni-editor-v1-8-agent-tarafi.md);
[10. adım, Harness'lar](../research/2026-11-03-yeni-editor-v1-10-barindirma.md))*

**Kabul koşulu:**
- Adaptör tek bir tool sunuyor; agent çağrıların listesini veriyor, liste ilk hatada duruyor ve cevap
  neyin yapıldığını, neyin yapılmadığını söylüyor.
- `retry` son listeyi aynı anahtarlarla gönderiyor, hiçbir şey iki kez yapılmıyor; bir listede tek
  `/wait`; proje silmek gönderilmiyor.
- Core'un adresi sohbetin klasöründeki `.queen-studio.json`'dan okunuyor ve her listede bizim core'umuz
  olduğu doğrulanıyor; değilse adres ve kullanıcıya sorulacağı söyleniyor.
- Claude Code için ayarı depoda; Claude Code'un adaptörü sohbetin klasöründe başlattığı denendi.
  Testler gerçek bir MCP oturumunda.
- Bir listede en çok 25 çağrı ve bir süre sınırı; metin cevabı bir boy sınırında. Sınır aşılınca
  adaptör boyu söyleyen bir hata veriyor, sessizce kesmiyor.

<a id="v1-23"></a>
### v1-23 — Resimler resim olarak gider

*([8. adım, Resimler](../research/2026-11-03-yeni-editor-v1-8-agent-tarafi.md);
[12. adım, Mutlaka sıkı test edilenler](../research/2026-11-03-yeni-editor-v1-12-test-stratejisi.md))*

**Kabul koşulu:**
- Cevabı resim olan çağrı agent'a MCP resim parçası olarak gidiyor; video gönderilmiyor, türü ve boyutu
  söyleniyor.
- Gerçek MCP oturumundaki test, bir metin parçasında resim baytı ya da base64 görünürse düşüyor; API'nin
  hiçbir JSON cevabında base64 yok.
- Resim alamayan harness'ta adaptör resmi göndermiyor ve bunu söylüyor.
- Claude Code'da elle: küçük bir fotoğraf bağlamı birkaç yüz token büyütüyor.
- Bir listede en çok 8 resim, en çok 2'si tam boyda.

*(Kullanıcı, 5 Kasım — "burası özellikle sıkı test edilsin, çünkü core özellik bu ve burası yanlış olursa
acayip performans düşüşü olur".)*

<a id="v1-24"></a>
### v1-24 — Agent senaryoları

*([13. adım, Doğrulama](../research/2026-11-03-yeni-editor-v1-13-yapim-plani.md))*

**Kabul koşulu:**
- `evals/` altındaki senaryolarda gerçek Claude Code, günlük kullanılan modelle ve bizim adaptörümüzle,
  taklit ComfyUI'li bir core'a karşı bir işi bitiriyor: proje, 4 fotoğraf, bir video, edit, export.
- Her koşuda işin bitip bitmediği, çağrı ve token sayısı, resimlerin resim olarak gidip gitmediği
  kaydediliyor; sayılar kayıtlı sınırların altında, kötüleşen sayı koşuyu düşürüyor.
- Komutu CLAUDE.md'de.

<a id="v1-25"></a>
### v1-25 — Başlatıcı ve notebook

*([10. adım, Barındırma](../research/2026-11-03-yeni-editor-v1-10-barindirma.md);
[12. adım, Başlatıcı](../research/2026-11-03-yeni-editor-v1-12-test-stratejisi.md))*

**Kabul koşulu:**
- Notebook `queen-studio/` içinde, queen-editor'ınki gibi; koşu boyunca koşunun dalını, sonra `main`'i
  çeker. ComfyUI'yi ve eklentilerini kuruyor, core'u başlatıyor; Drive izni Colab'ın giriş
  penceresiyle, Secrets core'a ortamdan gidiyor. Model indirmiyor, model seçimi sunmuyor.
- Tünelin adresi yalnız Pro'da basılıyor; ücretsiz katmanda core'a Colab CLI'la ulaşılıyor, bir kez T4'te
  açılıp `GET /api/health` cevap verdi.

<a id="v1-39"></a>
### v1-39 — Log'un Drive'a gitmesi ve boştayken sıfır çağrı

*([10. adım, Barındırma](../research/2026-11-03-yeni-editor-v1-10-barindirma.md))*

[v1-25](#v1-25)'ten bölündü *(kullanıcı, 6 Kasım)*.

**Kabul koşulu:**
- [v1-3](#v1-3)'ten beri diske yazılan log notebook'un çıktısında da görünüyor; 5 dakikada bir ve
  kapanırken Drive'a yeni bir parça gidiyor. Log dosyası sınırsız büyümüyor.
- İstek, iş ve yeni log yokken Drive'a hiç çağrı gitmiyor; testle.

<a id="v1-26"></a>
### v1-26 — ComfyUI'nin Colab ölçümleri

*([10. adım, Colab'da ölçülecekler](../research/2026-11-03-yeni-editor-v1-10-barindirma.md))*

**Kabul koşulu:**
- Ücretsiz T4'te, Colab CLI'la, 10. adımın ComfyUI ölçümleri yapıldı; model geçişi ve A100'deki
  ölçümler son maddeye kalır.
- Sonuçlar depoda kayıtlı; kodun dayandığı sayılar onunla tutuyor, testle.
- Tutmayan ölçüm varsa tasarım düzeltildi ve ilgili adıma yazıldı.

<a id="v1-27"></a>
### v1-27 — Colab testleri

*([12. adım, Katmanlar](../research/2026-11-03-yeni-editor-v1-12-test-stratejisi.md);
[13. adım, Kabul koşulları](../research/2026-11-03-yeni-editor-v1-13-yapim-plani.md))*

**Kabul koşulu:**
- Ücretsiz T4'te Colab CLI'la koşan suite yeşil: gerçek ComfyUI'yle fotoğraf, model indirme, export,
  gerçek Drive'a karşı depo sözleşmesi. Üretilen fotoğrafa bakıldı.
- Komutu CLAUDE.md'de; yalnız deneme hesabıyla.

<a id="v1-40"></a>
### v1-40 — Colab'da dayanıklılık, gerçek Drive'la

*([12. adım, Katmanlar](../research/2026-11-03-yeni-editor-v1-12-test-stratejisi.md);
[4. adım, Dayanıklılık](../research/2026-11-03-yeni-editor-v1-4-depo.md))*

[v1-27](#v1-27)'den bölündü *(kullanıcı, 6 Kasım)*.

**Kabul koşulu:**
- Bir kez gerçek Drive'la: core yeniden başlasa, cevap kaybolsa ya da Colab kapansa da kuyruk kaldığı
  yerden sürüyor; iki core aynı projeyi sırayla kullanıyor ve `resume` kuyruğu birinden ötekine
  geçiriyor.
- Yalnız deneme hesabıyla, ücretsiz katmanda.

<a id="v1-28"></a>
### v1-28 — UI tasarımı: dil, projeler ve kareler, örnek veriyle

*([9. adım, UI](../research/2026-11-03-yeni-editor-v1-9-ui.md);
[13. adım, Tasarımcı subagent](../research/2026-11-03-yeni-editor-v1-13-yapim-plani.md);
[5. adım, UI'da TypeScript](../research/2026-11-03-yeni-editor-v1-5-backend-yigini.md))*

v1'in ekranları iki maddede: bu madde tasarım dilini (renkler, yazılar, ortak parçalar) ve ilk
ekranları kurar, [v1-41](#v1-41) kalanları aynı parçalarla yapar; ekranlar böylece tutarlı kalır
*(kullanıcı, 6 Kasım — bölmek için "Yes, all 8")*. Akış: tasarımcı → tasarım reviewer'ı → reviewer →
QA → ana agent → commit. Ekranlar [v1-3](#v1-3)'ün yer tutucu sayfasının yerine geçer.

**Kabul koşulu:**
- Tasarım dili ve ortak parçalar gerçek UI kodunda (React, TypeScript) var; ekranlar: projeler; bir
  projenin kareleri sırasıyla, fotoğrafları, videoları ve durumları. Nasıl görüneceğine tasarımcı
  karar veriyor.
- Ekranlar örnek veriyle çalışıyor, core'a bağlı değil; istek, yoklama ve hata yakalama yok.
- Örnek veri core'un OpenAPI'sinden çıkan türlerle yazılı; core'da olmayan bir alanı gösteren ekran
  derlenmiyor.
- Ekranların davranışı (durumlar, onaylar, boş ve hata görünümleri) önce düşen bir testle başladı.
- Tasarım reviewer'ı deneyime baktı: kısa UX kontrol listesi ve 9. adımın yapabildiklerinin dışına
  çıkılmadığı. Reviewer kodu her kod maddesindeki gibi okudu. QA ekranları örnek veriye karşı
  Playwright'la denedi.

<a id="v1-41"></a>
### v1-41 — UI tasarımı: kuyruk, agent, bildirim, silmek ve edit'ler

*([9. adım, UI, Birden çok Colab ve Bildirim](../research/2026-11-03-yeni-editor-v1-9-ui.md))*

[v1-28](#v1-28)'den bölündü *(kullanıcı, 6 Kasım)*; onun tasarım dilini ve ortak parçalarını kullanır,
yenisini yalnız gerekince ekler. Akış v1-28'inki gibi.

**Kabul koşulu:**
- Ekranlar: kuyruk, onu bu Colab'ın mı başka bir Colab'ın mı çalıştırdığı, kendiliğinden durduysa
  nedeni, Pause ve Resume butonları; agent'ın ne yaptığı ve şu an ne yaptığı; bildirim; kare, video ve
  proje silmek, onayla; edit'leri export almadan izlemek.
- [v1-28](#v1-28)'in son dört koşulu bu ekranlar için de: örnek veri, OpenAPI türleri, önce düşen
  test, tasarım reviewer'ı, reviewer ve QA.

<a id="v1-29"></a>
### v1-29 — UI bağlantısı: projeler ve kareler

*([9. adım, UI](../research/2026-11-03-yeni-editor-v1-9-ui.md);
[4. adım, Başka Colab'ın yaptığını görmek ve Değerlendirme 9](../research/2026-11-03-yeni-editor-v1-4-depo.md);
[12. adım, Uçtan uca](../research/2026-11-03-yeni-editor-v1-12-test-stratejisi.md))*

**Kabul koşulu:**
- Projeler ve kare ekranları örnek veri yerine core'un endpoint'lerinden okuyor; görünüş
  [v1-28](#v1-28)'deki gibi kalıyor.
- Ekran kendiliğinden güncelleniyor; başka bir Colab'daki değişiklik birkaç saniye geriden geliyor.
- Ekranın ne sıklıkla yokladığı ve kaç istek yaptığı spec'te sayılı ve testle sınanıyor; UI'ın
  tazelemesi Drive kotasının en büyük kalemi (4. adım), reviewer bu maliyete bakıyor.
- Core bu makinede taklitlerle açılıyor, yazılı Playwright suite'i ona karşı koşuyor.

<a id="v1-30"></a>
### v1-30 — UI bağlantısı: kuyruk ve agent'ın yaptığı

*([9. adım, UI, Birden çok Colab ve Bildirim](../research/2026-11-03-yeni-editor-v1-9-ui.md))*

**Kabul koşulu:**
- Kuyruk, onu kimin çalıştırdığı, kendiliğinden durma nedeni ve agent'ın ne yaptığı core'dan geliyor;
  görünüş [v1-41](#v1-41)'deki gibi kalıyor.
- Pause ve Resume butonları agent'ın kullandığı `pause` ve `resume`'u çağırıyor.
- Kuyruk bitince ya da durunca tarayıcı bildirimi geliyor.
- Yoklama ve istek sayısı [v1-29](#v1-29)'deki gibi sayılı ve sınanıyor.

<a id="v1-31"></a>
### v1-31 — UI bağlantısı: silmek ve edit'leri izlemek

*([9. adım, UI](../research/2026-11-03-yeni-editor-v1-9-ui.md))*

**Kabul koşulu:**
- Kare ve video ekrandan, onayla siliniyor; proje yalnız ekrandan, bir onayla.
- Reddedilen silmede ekran core'un sözünü gösteriyor.
- Edit'ler export almadan izlenebiliyor.
- Görünüş [v1-41](#v1-41)'deki gibi kalıyor.

*(Kullanıcı, 5 Kasım — "agent'lar proje silemesin".)*

<a id="v1-32"></a>
### v1-32 — Pro'da tek deneme, kullanıcıyla

*([13. adım, Roadmap ve Kabul koşulları](../research/2026-11-03-yeni-editor-v1-13-yapim-plani.md))*

Her şey ücretsiz katmanda yeşil olduktan sonra.

**Kabul koşulu:**
- Pro'da gerçek modellerle Claude Code tünelden bağlanıp proje → fotoğraflar → video → edit → export'u
  tek başına bitiriyor; kullanıcı yalnız Colab'ın adresini veriyor. Export'a gözle bakıldı.
- Model geçişi ve A100'de arkada indirmenin üretimi yavaşlatması ölçüldü.
- 13. adımın on bir Kabul koşulunun her biri denendi, sonucu burada yazılı.
- Pro bir sorun bulduysa düzeltme önce ücretsiz katmanda denendi.

<a id="v1-33"></a>
### v1-33 — DeepSeek harness'ı, kullanıcıyla

*([10. adım, Harness'lar](../research/2026-11-03-yeni-editor-v1-10-barindirma.md);
[8. adım](../research/2026-11-03-yeni-editor-v1-8-agent-tarafi.md))*

Son madde; kullanıcıyla birlikte yapılır *(kullanıcı, 6 Kasım)*. Harness'ı ve DeepSeek hesabını
kullanıcı bu maddede kurar; kurulumda atlandı *(kullanıcı, 6 Kasım — "harnessı ben en son adımda
kuracağım, sen bu adımı atla, son adıma ekle, user ile yapılacak yaz")*. DeepSeek'in kendi harness'ı
`dsh` (`@deepseek-ai/dsh`) komut satırından, tıklamasız koşabiliyor; resim gören model `deepseek-flash`.

**Kabul koşulu:**
- Hangi DeepSeek harness'ının kullanılacağı ve anahtarı kullanıcıyla seçildi.
- MCP adaptörü o harness'ta çalışıyor: adaptörü sohbetin klasöründe başlatıyor, agent bir işi
  bitiriyor.
- Agent senaryoları DeepSeek harness'ıyla da koştu; sonuçları `evals/`'te Claude Code'unkilerin
  yanında *(kullanıcı, 6 Kasım)*.
- Harness resim parçasını modele veriyorsa resimler resim olarak gidiyor; vermiyorsa adaptör resim
  göndermiyor ve bunu söylüyor, hiçbir resim metin olarak gitmiyor.

---

## Kabul koşulları nerede gösterilir

Roadmap ancak [13. adımın Kabul koşullarının](../research/2026-11-03-yeni-editor-v1-13-yapim-plani.md)
hepsi tutunca biter; ana agent sonda hepsine kendisi bakar, v1-32 de onları dener.

| Koşul | Maddeler |
|---|---|
| 1. Agent işi tek başına bitirir | v1-32 |
| 2. Resimler resim olarak gider | v1-23, v1-32 |
| 3. Hiçbir şey iki kez yapılmaz ya da kaybolmaz | v1-10, v1-11 (`creates.json`), v1-17, v1-18, v1-19, v1-38, v1-22 (`retry`), v1-40 |
| 4. Kuyruk kendiliğinden durunca nedenini söyler | v1-18 |
| 5. Gerçek Drive'da çalışır | v1-4, v1-8, v1-9, v1-26, v1-27 |
| 6. Maliyet ve hız bütçede | işlem ekleyen her madde, v1-24, v1-39, v1-29, v1-30 |
| 7. İki Colab aynı projeyi sırayla kullanır | v1-10, v1-19, v1-40 |
| 8. Kullanıcı UI'ı onaylar | v1-28, v1-41, v1-29, v1-30, v1-31, v1-32 |
| 9. Kullanıcı export'u onaylar | v1-21, v1-27, v1-32 |
| 10. Bütün suite'ler yeşil | her madde; `main`'den önce bütün araçlar |
| 11. Şirket hesabına hiçbir test dokunmadı | v1-1, v1-4, v1-8, v1-9, v1-25, v1-26, v1-27, v1-40 |

---

## Nasıl yürür ve notlar

**Kaynak:** tasarım belgeleri — [adımlar](../research/2026-11-03-yeni-editor-v1-tasarim-adimlar.md),
[1](../research/2026-11-03-yeni-editor-v1-1-ozellik-envanteri.md),
[2](../research/2026-11-03-yeni-editor-v1-2-alan-modeli.md),
[4](../research/2026-11-03-yeni-editor-v1-4-depo.md),
[5](../research/2026-11-03-yeni-editor-v1-5-backend-yigini.md),
[6](../research/2026-11-03-yeni-editor-v1-6-endpoint-sozlesmesi.md),
[7](../research/2026-11-03-yeni-editor-v1-7-uretim-ve-kuyruk.md),
[8](../research/2026-11-03-yeni-editor-v1-8-agent-tarafi.md),
[9](../research/2026-11-03-yeni-editor-v1-9-ui.md),
[10](../research/2026-11-03-yeni-editor-v1-10-barindirma.md),
[11](../research/2026-11-03-yeni-editor-v1-11-kod-standardi.md),
[12](../research/2026-11-03-yeni-editor-v1-12-test-stratejisi.md),
[13](../research/2026-11-03-yeni-editor-v1-13-yapim-plani.md). Belgelerdeki "yeni editör" bu araçtır;
3. adım boştur (v1 queen-editor'ın projelerini açmaz).
[Sonraya kalanlar](../research/2026-11-03-yeni-editor-v1-sonraya-kalanlar.md) bu koşuya girmez.

- **Ad:** şimdilik `queen-studio`; kendini kanıtlarsa `queen-editor` olur ve onun sonraki sürümü olarak
  yerine geçer, o zamana kadar queen-editor yerinde kalır. queen-editor'dan kod alınmaz; davranışı,
  kuralları ve verisi (modellerin listesi, ComfyUI grafları, uyarı görseli) alınır *(13. adım; kullanıcı,
  6 Kasım)*.
- **Maddeler:** belgelerdeki kararlar kullanıcıyla konuşularak verildi; onlardan çıkan maddeler
  `ALIGNED` doğar ve dayandığı adımı gösterir *(13. adım; kullanıcı, 6 Kasım)*. Bir madde ne istendiğini
  ve nasıl görüleceğini söyler; nasıl yapılacağını coder spec'inde, kodu ve dayandığı adımı okuyarak
  kendi yargısıyla yazar.
- **Numaralar:** `v1-1`…`v1-41`, koşu gerçek numaralarını verene kadar. `v1-34`…`v1-41` büyük maddelerin
  bölünmesinden; tablodaki yerleri, bölündükleri maddenin hemen altı, yürüme sırasıdır *(kullanıcı,
  6 Kasım)*. Sayaçta en yüksek numara Queen
  Editor v11.1'in 524'ü.
- **Ekrandaki sürüm:** CLAUDE.md'nin "ilk madde ekrandaki sürümü artırır" kuralı ilk ekranla tutar:
  [v1-3](#v1-3) ekranı ilk kez açar, yalnız "Queen Studio V1" yazan bir yer tutucu sayfayla; ilk madde
  kurulumdur. Tasarlanan ekranlar sonda onun yerine geçer.
- **Bağımlılık:** sonra yapılan bir parçaya dayanan madde onu taklitle ya da port üzerinden kurulan
  veriyle sınar. Ör. [v1-5](#v1-5), [v1-6](#v1-6) ve [v1-10](#v1-10) port üzerinden ya da yalnız testte
  açılan bir adresle; [v1-12](#v1-12) ve [v1-13](#v1-13) kareleri bellek içi adaptörle kurar. Sonraki
  endpoint maddeleri öncekilerin kurallarını alır.
- **Kapsam:** bir madde dayandığı adım bölümlerinin her kuralını kapsar, burada sayılmasa da. Her madde
  4. adımın Dayanıklılık tablosunun kendi parçalarına düşen satırlarını sınar.
- **Sıra:** maddeler tablodaki sırayla, tek tek yürür; worktree açılmaz (makine 16 GB, tek tarayıcı,
  tek deneme Colab'ı).
- **Koşu durmaz:** ilk maddeden sonra kullanıcıya yalnız son iki maddede gidilir: Pro denemesi ve
  DeepSeek harness'ı *(kullanıcı, 6 Kasım)*.
  Tek istisna, geri alınamayan ya da geri alması çok zor ve uzun olan bir karardır; koşu yalnız onun
  için durur ve kullanıcıya sorulur *(kullanıcı, 6 Kasım)*. Yolda çıkan öbür kararları ana agent kendi
  yargısıyla verir; tutmayan bir ölçümde de tasarımı düzeltip geçer. Her kararı gerekçesiyle
  [kararlar belgesine](2026-11-06-queen-studio-v1-kararlar.md) yazar, değişen adımı da düzeltir;
  kullanıcıyla sonda o belgenin üstünden geçilir.
- **Yolda bulunan iş:** v1'in gerektirdiği `v1-43`'ten başlayarak madde olur ve kararlar
  belgesine yazılır; gerisi `queen-studio/BACKLOG.md`'ye.
- **Tasarımdan sapmak serbesttir:** kodu yazan agent bir şeyi tasarımdan ya da kurallardan farklı
  yapmanın daha doğru olduğunu görürse ana agent'a söyler; bazı şeyler ancak kod yazılırken görülür.
  Ana agent artısını ve eksisini tartar, uygunsa değiştirir, değişen adımı düzeltir ve sapmayı —
  nerede, neyden neye, neden — kararlar belgesinin "Sapmalar" bölümüne yazar *(kullanıcı, 6 Kasım)*.
  Kullanıcı sonda nerede sapıldığını oradan görür.
- **Kurulum, ölçüm ve deneme maddeleri** ([v1-1](#v1-1), Drive ölçümleri [v1-4](#v1-4), ComfyUI
  ölçümleri [v1-26](#v1-26), Colab testleri [v1-27](#v1-27), Pro denemesi [v1-32](#v1-32), DeepSeek harness'ı [v1-33](#v1-33)) ana agent'ın
  kendisinindir, kısa bir spec'le; QA yalnız davranış değişirse gelir.
- **Suite'ler:** bir madde yalnız queen-studio'nun suite'lerini koşar; bütün araçların suite'leri
  `main`'e birleşmeden önce bir kez koşar.
- **UI en sonda:** core ve MCP adaptörü bittikten sonra, Pro denemesinden önce; ekranların gösterdiği
  her şey o zaman vardır. Bir ekranı tasarlamak ve core'a bağlamak hep iki ayrı maddedir *(kullanıcı,
  6 Kasım)*; tasarımcı ve tasarım reviewer'ı [v1-2](#v1-2)'de yazılır.
- **Tasarım maddesi:** tasarımcı → tasarım reviewer'ı → reviewer → QA → ana agent → commit; ekranlar
  gerçek UI kodunda, OpenAPI türleriyle yazılı örnek veriyle, bağlantısız. Reviewer tasarımcının kodunu
  her kod maddesindeki gibi okur; CLAUDE.md'nin "her değişiklik reviewer'dan geçer" kuralının istisnası
  yoktur.
- **Bağlantı maddesi:** coder → reviewer → QA → ana agent → commit; örnek veri gerçek endpoint'lerle
  değişir, görünüş kalır, yoklama ve istek sayısı burada.
- **Maliyet:** işlem ekleyen her madde o işlemin Drive çağrısı sayısını 4. adımın tablosuyla tam
  eşitlikle sınar ([12. adım](../research/2026-11-03-yeni-editor-v1-12-test-stratejisi.md)).
- **Agent senaryoları:** [v1-24](#v1-24)'ten sonra API'ye, `GET /api`'ye, hatalara ya da adaptöre dokunan
  her maddeden sonra koşar; bir sayı kötüleşirse madde geri döner.
- **Hesap:** testler, ölçümler ve Colab CLI yalnız deneme hesabıyla; şirket hesabı ve ücretli katman
  yalnız son maddede, kullanıcıyla.
- **Arşiv:** koşu bitince roadmap ve kararlar belgesi, `2026-11-03-yeni-editor-v1-*` araştırmalarıyla
  birlikte `docs/arsiv/`'e taşınır (CLAUDE.md).
