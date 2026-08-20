# Queen Editor — Tasarım v4 fark çıkarma · Tasarım

**Tarih:** 2026-08-20 · **Branch:** `feat/queen-editor-v4` · **Durum:** açık
**Öncülü:** [tasarım v3 fark çıkarma](2026-08-11-queen-editor-tasarim-v3-fark-cikarma-design.md) — yöntem
oradan taşındı, farkları aşağıda işaretli.

---

## Amaç

claude.ai/design'daki tasarım projesinin **"Basit v4"** sürümü ile **bugün çalışan uygulama**
arasındaki farkları çıkarmak. Tek çıktı bir Türkçe md: **düz bir liste** — nerede farklılar, ne
eklenecek, ne düzeltilecek, her maddeyi hangi yol buldu.

Bu belge farkın *kendisini* değil, farkı **nasıl çıkaracağımızı** tarif eder.

## Üçlü isim çakışması — belgenin başına not düşülür

Bu turda "v4" üç ayrı şeyin adı:

| Ad | Ne | Durumu |
|---|---|---|
| **tasarım v4** | tasarım projesindeki "Basit v4" | bu turun karşılaştırdığı şey |
| **roadmap v4** | repodaki 8 Ağustos yol haritası | bitti, geçti — bu turla ilgisi yok |
| `feat/queen-editor-v4` | bugünkü dal | yalnız dal adı |

Belge boyunca hep tam ad yazılır; yalın "v4" hiçbir yerde geçmez.

Öncüllerde eşleme vardı (tasarım v2 = roadmap v3, tasarım v3 = roadmap v5). **Bu turda eşleme
yapılmaz:** tasarım v4'ün repo karşılığı henüz yazılmadı — bu turun ürünü onu yazmayı mümkün kılacak.
Repo tarafı belge boyunca "bugünkü uygulama" diye anılır.

## Kaynak projenin değişmesi — öncülden ilk fark

Geçmiş iki tur `efad1f83-69d3-4e07-89fa-3783839c81c3` ("Queen Editor") üstünde koştu. Tasarım v4
başka bir projede: **`ff9837f9-94c5-4843-9d14-7bda150e8425` ("Copy of Queen Editor")**. Kopya proje
v1'den v4'e bütün zinciri taşıyor. Bu turun tek tasarım kaynağı odur; eski proje **hiç açılmaz.**

## Bugünkü uygulamanın durumu — belgeye not düşülür

Tasarım v3 karşılaştırmasından (11 Ağustos) bu yana repo dokuz tur ilerledi: roadmap v5'ten v13'e.
Yani iki taraf da yerinden oynadı — tasarım kendi yolunda, uygulama kendi yolunda. **Tarama tam
kapsamlıdır**, yalnız v4'ün getirdikleriyle sınırlı değil: bu dokuz turda sessizce açılmış sapmalar
ancak baştan sona bakılırsa görünür.

20 Ağustos istek listesinin hiçbir maddesi henüz uygulanmadı: o tarihten bu yana `queen-editor/`
altında yalnız belge ve düzen dosyaları değişti, arayüz ve davranış kaynağına dokunulmadı. Yani
listedeki yedi arayüz maddesi bu turda **tümüyle fark olarak** çıkacak.

## Kapsam sınırı — çıktı belgesine ne girmez

Çıktı belgesinde **kod diline ait hiçbir şey geçmez**: dosya adı, uç nokta, bileşen adı, katman adı —
hiçbiri. Yalnızca kullanıcının gördüğü davranış yazılır. Kaynağı okumak serbesttir; **yazmak
yasaktır.**

**Görsel dil kapsam içidir** — renk, boşluk, tipografi, ikon, ölçü. Ayrı bölüme çekilmez; aynı
listede `görsel` etiketiyle durur.

**Belge karar vermez.** Çelişkiyi işaretler, hangisinin kazanacağını söylemez.

**Terminoloji tasarımın kendisinden alınır:** **kare** = içerik birimi (foto + video + ses),
**fotoğraf** = yalnız foto katmanı. Tasarım v4'ün getirdiği ikinci sözcük kümesi: **üretim modu** ve
üç değeri — **standart**, **loop**, **sonrakine bağla**.

## Kaynaklar

**Tasarım tarafı** — proje `ff9837f9-94c5-4843-9d14-7bda150e8425`, DesignSync ile **salt okunur**.
`finalize_plan`, `write_files`, `delete_files`, `register_assets` çağrılmaz. Tasarım dosyaları
**hiçbir yere kaydedilmez** — ne repoya, ne geçici klasöre.

| Dosya | Ne taşır |
|---|---|
| `HANDOFF.md` | katmanlı kural metni: v1'den **v3.5**'e kadar bütün bölümler |
| `EKRAN-NOTLARI.md` | ekran ekran notlar (01 proje listesi → 19 export) — v4'te wireframe kartlarından buraya taşındı |
| `DEGISIKLIK-GUNLUGU.md` | neyin ne zaman değiştiği; **geri alınan kararlar burada kayıtlı** |
| `CLAUDE.md` | yıkıcı eylem butonu standardı |
| `Queen Editor Basit v4.html` | v4 giriş noktası |
| `simple-app-v4.jsx`, `simple-screens-v4.jsx`, `export-designs-v4.jsx` | v4 ekranları, durumları, Export ekranı |
| `wireframe-kit.jsx`, `tweaks-panel.jsx`, `design-canvas.jsx`, `styles.css` | ortak altyapı |

**Kapsam dışı:** `screenshots/` · `direction-e.jsx` · v1, v2 ve v3 zincirleri · eski `app.jsx`
hattı · `Queen Editor Wireframes*.html`. Gerekçe iki türlü: `screenshots/` ve `direction-e.jsx` ayrı
bir görsel yön çalışması; eski sürüm zincirleri ise **geçersiz kılınmış tasarımdır** — v3 wireframe'i
bugünün tarifi değil, dünün tarifidir ve okunursa ölü kural bulgu diye yazılır.

**Uygulama tarafı** — repodaki `queen-editor/`. Bugünkü davranışın tek kaynağı burasıdır. Yazılı
tarif tarafı: `queen-editor/FOUNDATION.md` ve `queen-editor/BACKLOG.md`.

**Brif çelişkisi bölümü için** — [arayüz brifi](../../2026-08-20-queen-editor-arayuz-brifi.md) ve
[istek listesi](../plans/2026-08-20-queen-editor-istekler.md).

## İki geçersizlik kuralı — biri öncülden, biri yeni

Bu turda "yazıda duruyor ama ölü" iki ayrı biçimde karşımıza çıkıyor. İkisi de uygulanmazsa ajanlar
geçersiz kılınmış kararları bulgu diye yazar.

**1 · Katman kuralı (öncülden taşındı).** `HANDOFF.md` üst üste binmiş katmanlardan oluşuyor ve v4
turu üç katman daha ekledi (v3.3 üretim modu ve rozet dili, v3.4 toplu katman silme, v3.5 yeniden
üret formunda mod seçimi).

**Geçerlilik sırası: v3.5 > v3.4 > v3.3 > v3.2 > v3.1 > v3 > v2 > v1. Üstü çizili (`~~…~~`) metin
ölüdür.**

**2 · Geri alma kuralı (bu turda yeni).** Değişiklik günlüğü yalnız eklenenleri değil, **denenip
vazgeçilenleri** de kaydediyor: kart üstündeki mod şeridi eklenip tamamen kaldırıldı, rozetler metin
→ ikon → yine metin diye üç aşamadan geçti, detay panelinde space-between denenip bırakıldı, grup
başlıkları eklenip silindi. Günlükte "kaldırıldı", "vazgeçildi", "reddedildi" diyen her madde
**yalnız son hâliyle** geçerlidir; ara aşama bulgu üretmez.

Bu turun en olası hatası budur ve üç yolun da görev metninde ayrıca uyarılır.

## `düzeltilecek` türünün tabanı

Bu tür "tasarım v4 farkı değil, uygulama **kendi tarifini** bugün tutturamamış" demektir. Öncülde
taban tasarım v2'ydi; uygulama o günden beri dokuz tur kendi spec'leriyle ilerlediği için taban
yeniden tanımlanıyor:

**Taban = `HANDOFF.md`'nin hâlâ geçerli katmanları + `queen-editor/FOUNDATION.md` +
`queen-editor/BACKLOG.md`.**

Kural metni katmanlı olduğu için eski ama geçersiz kılınmamış kararlar hâlâ oradadır — uygulamanın
tarifi büyük ölçüde o dosyanın içinde duruyor. Üstü çizilmemiş ve sonraki katmanca ezilmemiş her
kural bir tariftir; uygulama ondan sapmışsa bu bir tasarımcı kararı değil, bir hatadır.

**Sonucu:** Yol 2 bu tabanı hiç görmediği için o türde bulgu üretemez. **`düzeltilecek` maddelerinde
tavan 2/3'tür** ve orada 2/3, "kesin"in karşılığıdır.

---

## Üç yol

Üç yol, üç ayrı kaynağa demirler. Her biri **tek başına tam liste** çıkarabilecek yetkinliktedir —
biri diğerinin parçası değil, sağlamasıdır. Üçü ayrı alt-ajanda, **aynı anda** koşar ve **hiçbiri
diğerinin çıktısını görmez.**

| | Yol 1 · **Anlatı** | Yol 2 · **Tasarım kaynağı** | Yol 3 · **Ters yön** |
|---|---|---|---|
| Demir | tasarımın *yazısı* | v4 wireframe'inin *kendisi* | bugünkü uygulamanın *kendisi* |
| Yön | tasarım → uygulama | tasarım → uygulama | uygulama → tasarım |
| Özel yakaladığı | kararların gerekçesi, ekranı çizilmemiş kurallar | yazıya geçmemiş her şey — etiketler, ara durumlar, boş hâller, ölçüler | öksüz davranışlar, bugün zaten yanlış olanlar |
| Kör noktası | tasarımcının yazmadığı | "neden"i bilmez | bugün hiç tutamağı olmayan yepyeni şey |

**Körlük erişim biçimiyle sağlanır, dileğe bırakılmaz:**

| Yol | Tasarım tarafına nasıl erişir |
|---|---|
| Yol 1 | **DesignSync'i hiç çağırmaz.** Dört yazılı belge görev metninde hazır verilir; wireframe kaynağına erişimi yok |
| Yol 2 | DesignSync'i **kendisi çağırır**, yalnız v4 wireframe zinciri için. Yazılı belgelerden herhangi birini çekmesi yasak — ihlal çağrı kaydında görünür ve o yolun çıktısı geçersiz sayılır |
| Yol 3 | DesignSync'i kendisi çağırır, tasarım tarafının tamamı serbesttir |

Körlüğün karşılığı ölçülmüş bir kazançtır: tasarım v3 turunda 108 maddenin **34'ünü tek bir yol**
yakaladı. Belgenin üçte biri, yolların birbirinden farklı yerde durmasından geldi.

### Yol 1 · Anlatı

**İş A — fark çıkarma.** Yazılı her kararı tek tek alır → bugünkü uygulamada karşılığını arar → fark
varsa yazar. Katman kuralı ve geri alma kuralı uygulanır. Kural metninin "Kural olarak yazılanlar",
"Değişmeyenler", "Karara bağlananlar" ve "Görsel dil" bölümleri de taranır, atlanmaz — "değişmedi"
diyen bir bölüm, uygulama oradan sapmışsa `düzeltilecek` üretir.

**İş B — brif çelişkisi.** 20 Ağustos brifindeki her "karar verildi" maddesini alır, tasarımın ne
yaptığına bakar. Tasarım kararı geri almışsa üç şeyi yazar: brif ne demişti, tasarım yerine ne koydu,
tasarım hangi gerekçeyi yazdı. Bu maddeler fark listesine karışmaz; ayrı bölüme gider ve **karar
verilmez** — kullanıcının görmesi için oradadır.

İş A ile İş B ayrı dosyalara yazılır; ikisi ayrı sorudur ve ayrı bölümleri besler.

### Yol 2 · Tasarım kaynağı

v4 wireframe'inden envanter çıkarır — hangi ekran, hangi bölge, hangi kontrol, hangi durum, durumlar
arası hangi geçiş, hangi metin, hangi boş hâl, hangi renk/boşluk/ikon. Aynı envanteri bugünkü
uygulamadan çıkarır. Satır satır karşılaştırır.

Bu yolun özel değeri: v4 turunda **wireframe kartlarındaki bütün açıklama yazıları kaldırıldı** ve
ayrı bir dosyaya taşındı. Yani kaynak artık kendini anlatmıyor; ne yaptığı yalnız çizimden okunuyor.
Yazıya hiç geçmemiş ayrıntıları görecek tek yol budur.

### Yol 3 · Ters yön

**İş A — fark çıkarma.** Bugünkü uygulamanın davranış envanterini çıkarır, her maddeyi tasarım v4'te
arar: karşılığı var-aynı (yazılmaz) · karşılığı var-farklı (`değişecek`) · karşılığı yok (`öksüz`).
Kapanış taraması: tasarım v4'te dokunulmuş olup envanterinde hiç görünmeyen yer kaldı mı?

**İş B — sadakat denetimi.** Uygulama bugün hedeflediği tarifi tutturmuş mu? Tabanı yukarıda tanımlı.
Tutturamadığı yerler `düzeltilecek` tipiyle aynı dosyaya girer. İki iddia tek bulguda birleştirilmez:
"bugün yanlış" ile "tasarım v4'te değişecek" farklı iki şeydir.

---

## Ortak kurallar

1. **Bulgu geçiş olarak yazılır, duruş olarak değil.** "Duraklat butonu var" yetersiz; "Duraklat'a
   basınca çalışan kare bitirilir, arada *Duraklatılıyor…* görünür, sonra bekleyen sayısı 7'den 8'e
   çıkar" doğrudur.
2. **Her bulgu iki satırdır:** *bugün ne oluyor* → *tasarım v4'te ne olacak*. Bugün hiç karşılığı
   yoksa ilk satır **"bugün yok"**tur; uydurulmuş karşılık aranmaz.
3. **Her bulgunun bir türü vardır:** `eklenecek` (bugün yok) · `değişecek` (var, farklı) ·
   `düzeltilecek` (bugün tarifine göre zaten yanlış) · `öksüz` (bugün var, tasarımda yok).
4. **Her bulgu `davranış` ya da `görsel` etiketi alır.**
5. **Kod dili yok.**
6. **Karar verilmez.** Çelişkide iki ifade de yazılır.
7. **"Tasarım söylemiyor" notu:** cevabı yoksa madde bu notu alır; uydurulmaz.
8. Belge ve tüm ara çıktılar **Türkçe**.

## Ara çıktılar repoya yazılır

Her yol bulgularını **ilerledikçe** kendi dosyasına yazar. Sebep: yarıda kesilen alt-ajan hiçbir şey
döndürmez, emek tümüyle gider. Körlük bozulmaz — her ajan yalnız kendi dosyasına yazar,
ötekilerinkini okumaz.

| Dosya | Ne |
|---|---|
| `docs/superpowers/research/2026-08-20-v4-ara/yol-1-anlati.md` | Yol 1 · İş A |
| `docs/superpowers/research/2026-08-20-v4-ara/yol-1-brif-celiskisi.md` | Yol 1 · İş B |
| `docs/superpowers/research/2026-08-20-v4-ara/yol-2-tasarim-kaynagi.md` | Yol 2 |
| `docs/superpowers/research/2026-08-20-v4-ara/yol-3-ters-yon.md` | Yol 3 · İş A + İş B |

Yer repodur, geçici klasör değil: kullanıcı üç yolun ne bulduğunu çakıştırmadan **önce** görebilsin,
bir yolun yoldan çıktığını fark edebilsin diye.

**Bu dosyalar commit edilmez.** Çıktı belgesi yazıldıktan ve kullanıcı onayladıktan sonra klasör
silinir; silme kullanıcıya sorularak yapılır, kendiliğinden değil.

Bu, "tasarım dosyaları hiçbir yere kaydedilmez" kuralıyla çelişmez: dosyalara giren şey **bulgudur** —
kullanıcının gördüğü davranışı anlatan cümle. Tasarım kaynağının kendisi, alıntısı ya da özeti oraya
yazılmaz.

## Sağlama — çakıştırma

Çakıştırmayı alt-ajan değil, ana oturum yapar; üç listeyi de gören tek yer burasıdır. Aynı farkın üç
ayrı cümlesi tek satıra indirilir; birleştirme kararı **elle** verilir. Ölçüt başlık benzerliği değil,
`Bugün` ve `Tasarım v4'te` satırlarının **aynı geçişi** anlatıp anlatmadığıdır.

| Kaç yol | Damga | Ne yapılır |
|---|---|---|
| 3/3 | kesin | listeye girer |
| 2/3 | güçlü | listeye girer |
| 1/3 | zayıf sinyal | kaynağa dönülür, elle doğrulanır |

Doğrulanan zayıf sinyal "elle doğrulandı" notuyla girer; doğrulanamayan **atılmaz**, listede o
damgayla durur. İki yol aynı konuda farklı şey söylüyorsa madde **çelişki** damgası alır ve her iki
ifade de yazılır — hangisinin doğru olduğu söylenmez.

Zayıf sinyal bir kusur değil, beklenen sonuçtur: her yolun özel yakaladığı bir sınıf var, o sınıftaki
bulguyu tek başına görmesi normaldir.

## Yöntemin kendi sayımı — belgeye girer

Öncülde künyede tek tablo vardı; bu turda **üç tablo** girer. İlk ikisi okura yöntemin ne ürettiğini
söyler, üçüncüsü yöntemi denetler.

| # | Tablo | Ne gösterir |
|---|---|---|
| 1 | Yol × üretim | her yol kaç ham bulgu yazdı, hangi alanları taradı, neyi atladı |
| 2 | Damga dağılımı | kaç madde kesin / güçlü / zayıf sinyal / çelişki |
| 3 | Tür × yol matrisi | hangi türü hangi yol kaç kez yakaladı |

Üçüncüsü yöntemin öz-denetimidir: Yol 2'nin `görsel` sütunu boşsa kaynağı yeterince taramamıştır,
Yol 3'ün `öksüz` sütunu boşsa ters yön çalışmamıştır. Boş sütun görülürse o yol yeniden koşturulur.

Fark listesinde ayrıca **her maddenin kendi satırında** onu hangi yolların gördüğü durur (`Y1 Y2 Y3`).

## Çıktı belgesinin iskeleti

Tek düz liste. Alt başlıklar yalnız okunabilirlik için alan alandır; numaralandırma **kesintisiz**
tektir (1, 2, 3…), harf önekli kod yok.

| # | Bölüm | İçerik |
|---|---|---|
| 0 | Başlık notu | üçlü isim çakışması · iki geçersizlik kuralı · bugünkü tabanın durumu · yöntem ve üç sayım tablosu |
| 1 | Özet | tasarım v4 tek paragrafta ne getiriyor |
| 2 | **Fark listesi** | tek liste; her madde: ne · tür · davranış/görsel · bugün → tasarım v4'te · Y1/Y2/Y3 · damga |
| 3 | **Brif ne dedi, tasarım ne yaptı** | geri alınan kararlar: brifin kararı · tasarımın yerine koyduğu · tasarımın gerekçesi. Karar yok |
| 4 | Tasarımın cevaplamadıkları | "tasarım söylemiyor" notlu maddeler |

2. bölümün alan başlıkları, sırasıyla: Projeler · Proje ekranı ve panel şeridi · Fotoğraf üret ·
Video üret · Ses üret · Kuyruk · Üreticiler ve kurulum · Galeri · **Seçim barı ve toplu eylemler** ·
Detay sayfası · Export ekranı · Adlandırma ve kimlik · Uygulama geneli.

Seçim barı öncülde yoktu; tasarım v4'ün getirdiği toplu taşıma, kart kopyalama ve toplu katman silme
işleri hep orada toplandığı için kendi alanı oldu.

**Yer:** `docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md`

## Kapsam dışı

- Kod değişikliği — bu tur tek satır kod yazmaz.
- Sıradaki yol haritasının yazılması; çelişkilerin ve brif geri almalarının karara bağlanması.
- Tasarım projesine yazma; tasarım dosyalarının herhangi bir yere kaydedilmesi.
- `screenshots/`, `direction-e.jsx`, v1/v2/v3 zincirleri, eski `app.jsx` hattı.
- **queen-tools çarpışması bölümü.** Öncülde vardı; tasarım v4 Export'a dokunmuyor — değişiklik
  günlüğünde Export ekranı için yalnız iki açıklama bloğunun kaldırıldığı yazıyor. Bir fark yine de
  Export'a değerse normal listeye girer.

## Karara bağlananlar

- **Tarama tam kapsamlıdır.** Yalnız 20 Ağustos brifindeki yedi madde değil, tasarımın ve uygulamanın
  tamamı taranır. Gerekçe: iki taraf da son karşılaştırmadan beri kaydı, ve tasarım brif dışında da
  çok şey değiştirdi (rozet dili, seçim modu, toplu katman silme, detay panelinin yeniden düzeni).
- **Üç yol kör koşar** — öncüldeki düzenin aynısı. Erişimi paylaştırma ve sıra dayatma seçenekleri
  tartışıldı ve bırakıldı: körlük 108 maddenin 34'ünü üreten şeydi.
- **Brif çelişkisi kendi bölümüne girer**, fark listesine karışmaz. Gerekçe: bunlar repo↔tasarım farkı
  değil — repoda ikisinin de karşılığı yok. Kullanıcının kendi verdiği kararların tasarımca geri
  alınmış olması, uygulamaya geçmeden görülmesi gereken tek madde sınıfıdır.
- **`düzeltilecek` tabanı yeniden tanımlandı:** kural metninin hâlâ geçerli katmanları + repodaki
  `FOUNDATION.md` ve `BACKLOG.md`. Öncüldeki "tasarım v2" tabanı dokuz tur sonra geçersiz.
- **Eski sürüm zincirleri kapsam dışı**, Yol 3 için bile. Öncülde Yol 3'e v2 karşılıkları açıktı;
  bu turda açılmıyor, çünkü v3 wireframe'i artık tarif değil, geçersiz kılınmış tasarımdır.
- **Geri alma kuralı zorunlu.** Değişiklik günlüğü denenip vazgeçilenleri kaydediyor; ara aşama bulgu
  üretmez.
- **Ayrı bir uygulama planı yazılır.** Bu spec üç yolun neye demirlendiğini ve çıktının ne olacağını
  söylüyor; ama iki şeyi söylemiyor: bulgunun **satır yapısı** (çakıştırma buna dayanır) ve **kabul
  denetimleri** — özellikle "Yol 2 gerçekten kör kaldı mı" denetimi, yöntemin tek kırılgan yeri.
  İkisi de planda durur.

## Açık soru

Yok.
