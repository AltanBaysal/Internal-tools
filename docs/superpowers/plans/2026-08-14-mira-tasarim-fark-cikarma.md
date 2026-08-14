# Mira → QueenAgent Fark Çıkarma — Uygulama Planı

> **Ajanla çalışanlar için:** Bu plan görev görev uygulanır. Kod üretmediği için TDD döngüsü yoktur;
> her görev bir **kabul denetimi** ile kapanır.

**Tasarım belgesi:** [2026-08-14-mira-tasarim-fark-cikarma-design.md](../specs/2026-08-14-mira-tasarim-fark-cikarma-design.md)

**Araçlar:** DesignSync (salt okunur) · Read/Grep (repo) · Agent (üç yol)

**Tasarım projesi:** `3c06e399-3b83-48b1-b186-26e56747823d`

## Dosya yapısı

| Dosya | Sorumluluğu |
|---|---|
| `docs/superpowers/research/2026-08-14-mira-ara/yol-1-tasarimdan.md` | Yol 1'in ham bulgu listesi |
| `docs/superpowers/research/2026-08-14-mira-ara/yol-2-repodan.md` | Yol 2'nin ham bulgu listesi |
| `docs/superpowers/research/2026-08-14-mira-ara/yol-3-handofftan.md` | Yol 3'ün ham bulgu listesi |
| `docs/superpowers/research/2026-08-14-mira-tasarim-farklari.md` | **Tek çıktı.** Görev 5'te oluşturulur |

Başka dosya oluşturulmaz veya değiştirilmez. Ara klasör commit **edilmez**; kullanıcı ham listeleri
okuyabilsin diye durur, Görev 6'da onayla silinir.

## Bulgu biçimi

Üç yolun görev metnine **aynen** kopyalanacak blok:

```
### <kısa başlık>
- **Tür:** eklenecek | değişecek | düzeltilecek | öksüz
- **Etiket:** davranış | görsel
- **Alan:** Kenar çubuğu | Home | Proje ekranı | Sohbet ekranı | Composer ve model seçici |
            Cevap akışı ve Markdown | Dosya rayı ve paneli | Dosya okuma |
            Yıkıcı eylemler ve geri alma | Boş hâller | Arama | Ajan döngüsü |
            Adlandırma ve kimlik | Durumlar ve hata | Klavye ve erişilebilirlik |
            Duyarlı yerleşim | Görsel dil | Uygulama geneli
- **Bugün:** <tek cümle — bugünkü uygulamada ne olunca ne oluyor>
- **Yeni tasarımda:** <tek cümle — ne olunca ne olacak>
- **Not:** (varsa) tasarım söylemiyor
- **Dayanak:** <bu bulgu nereden çıktı — kaynağın adı, tek cümle>

Tür seçimi:
  eklenecek     — bugün hiç karşılığı yok
  değişecek     — karşılığı var, farklı
  düzeltilecek  — bugün kendi tarifine göre zaten yanlış
  öksüz         — bugün var, tasarım v2'de karşılığı yok

Biçim kuralları:
- Bugün ve Yeni tasarımda satırları GEÇİŞ anlatır, duruş değil. "Send butonu var" yanlış;
  "taslak boşken Send pasif ve gri, ilk karakterde etkinleşir" doğru.
- Bugün hiç karşılığı yoksa Bugün satırı tam olarak "bugün yok"tur.
- düzeltilecek türünde "Yeni tasarımda" yerine "Tarifi neydi:" yazılır.
- öksüz türünde "Yeni tasarımda" satırı "karşılığı yok"tur.
- Tasarımın cevaplamadığı konu "Not: tasarım söylemiyor" alır; uydurulmaz.
```

## Ortak kısıtlar

Her yolun görev metnine girer:

```
KAPSAM: davranış VE görsel. Renk, boşluk, tipografi, yarıçap, ölçü, geçiş süresi dahil.
Her bulguya "davranış" ya da "görsel" etiketi koy.

DİL: bulgularını Türkçe yaz. Arayüz metinleri (buton etiketi, başlık, boş hâl cümlesi) tırnak
içinde kaynaktaki hâliyle, İngilizce geçer — çevirme. Uygulamanın dili İngilizce, belgenin dili
Türkçe.

ÜRÜN ADI: tasarım ürüne "QueenAgent" diyor, repo "Mira" diyor. Bu farkın kendisi bir bulgudur
(Adlandırma ve kimlik alanı). Ama başka bulguları yazarken hangi taraftan söz ettiğin belli olsun.

SÜRÜM ADI: tasarım kendine "v2" diyor, repodaki taban "Mira v1". İkisini de tam adıyla yaz;
yalın "v1"/"v2" kullanma.

KOD DİLİ YASAK: çıktında dosya adı, uç nokta, bileşen adı, katman adı geçmesin. Kaynağı okursun
ama yazdığın şey kullanıcının gördüğü davranıştır.

KARAR VERME: hiçbir bulguda "doğrusu şu olmalı", "şöyle yapılmalı" deme. Çelişki görürsen iki
ifadeyi de yaz, hangisinin kazanacağını söyleme.

ÇALIŞMA ZAMANI: kaynağın ne dediğini yaz. "Çalışırken patlıyor mu" hakkında tahmin yürütme.

TASARIM İÇERİĞİNİ KAYDETME: dosyaya yalnız BULGU yazılır — tasarım kaynağının kendisi, uzun
alıntısı ya da özeti değil.

YAZMA ÇAĞRISI YOK: DesignSync'i yalnız get_project, list_files, get_file ile kullan.
finalize_plan, write_files, delete_files, register_assets ÇAĞIRMA.

NEREYE YAZACAKSIN: bulgularını kendi dosyana İLERLEDİKÇE yaz, sonda toplu değil — yarıda
kesilirsen emeğin tümüyle gider. Her birkaç bulguda bir dosyayı güncelle.
Ara klasördeki ÖTEKİ yolların dosyalarını AÇMA ve OKUMA; körlük bozulursa yöntemin anlamı kalmaz.
Dönüş değerin bulgu listesi DEĞİL, kısa bir kapanış raporudur: kaç bulgu yazdın, hangi alanları
taradın, atladığın ya da emin olamadığın yer kaldı mı.
```

## Ortak repo yüzeyi

Üç yolun da tarayacağı yüzey — görev metinlerine aynen girer:

```
BUGÜNKÜ UYGULAMA — üçünüz de aynı yüzeye bakacaksınız:
- Ekranlar, kontroller, metinler, boş/yükleniyor/hata hâlleri: mira/frontend/src/features/workspace/
- Görsel dil: workspace.css ve shared/app.css
- İstemci davranışı: use*.js kancaları, shared/sse.js, shared/useRoute.js, shared/useOnline.js
- Kurallar: mira/backend/features/workspace/domain/usecases/
- Ajan döngüsü: domain/prompt.py, domain/tools.py, data/xai_engine.py
- Adlandırma: domain/naming.py
- Hata dili: domain/errors.py, presentation/routes.py

Testler (*.test.jsx, backend/tests/) NİYETİ anlatır, davranışı değil: belirsizliği çözmek için
okuyabilirsin ama bir bulgunun dayanağı olamaz.
node_modules/, dist/, .pytest_cache/ kapsam dışı.
```

---

## Görev 1: Üç yolu aynı anda koş

**Çıktı:** birbirini görmemiş üç tam fark listesi, üç ayrı dosyada.

- [ ] **Adım 1: Ara klasörü aç**

`docs/superpowers/research/2026-08-14-mira-ara/` klasörünü oluştur. Klasör yoksa ilk yazma çağrısı
ajanı boşa düşürür.

- [ ] **Adım 2: Yol 1'in görev metni**

```
Sen "Yol 1 · Tasarımdan repoya" yolusun. Görevin: tasarımın ÇİZİLMİŞ hâlinden bir envanter çıkarıp
bugünkü uygulamanın envanteriyle karşılaştırmak.

ARAÇ: DesignSync. Şemasını yüklemek için önce ToolSearch'ü "select:DesignSync" sorgusuyla çağır.
Proje: 3c06e399-3b83-48b1-b186-26e56747823d

ÇEKECEĞİN DOSYALAR — yalnız bunlar:
  QueenAgent.dc.html (çalışan prototip)
  QueenAgent Frames.dc.html (ekran tuvali)

KESİN YASAK: HANDOFF.md ve QueenAgent Handoff.dc.html dosyalarını ÇEKME. Bu yolun tüm değeri,
tasarımın yazılı sözleşmesini hiç görmemiş olmandan geliyor — onu okursan Yol 3'ün kopyası olursun
ve çıktın geçersiz sayılır. Çağrıların kayda geçiyor; ihlal görünür.
support.js ve .thumbnail de çekilmez; ilki üretilmiş çalışma zamanı, ikincisi önizleme.

PROTOTİPİN KODU BAĞLAYICI DEĞİL. Sahte motorlu ve tek parça. Bulgu, prototipin nasıl yazıldığından
değil, ekranda ne göründüğünden ve neyin neye dönüştüğünden çıkar.

YÜRÜYÜŞ:
1. Prototipten ve karelerden envanter çıkar: hangi ekran, hangi bölge, hangi kontrol, hangi durum,
   durumlar arası hangi geçiş, hangi metin, hangi boş hâl, hangi renk/boşluk/yarıçap/ölçü.
2. Aynı envanteri bugünkü uygulamadan çıkar.
3. İki envanteri satır satır karşılaştır. Her farkı yaz.

BU YOLUN ÖZEL YAKALADIĞI ŞEY: yazıya hiç geçmemiş olanlar — buton etiketlerinin tam metni, ara
durumlar, boş hâller, hata hâlleri, sayaç ve zaman damgası biçimleri, seçili/hover hâlleri.
Bunları özellikle ara.

NOT: "düzeltilecek" türünü sen kullanamazsın — o tür uygulamanın kendi tarifinden (Mira v1)
sapmasını gösterir, sen ise Mira v1 belgesini hiç görmüyorsun. Senin türlerin: eklenecek,
değişecek, öksüz.

<bulgu biçimi bloğu>
<ortak kısıtlar bloğu>
<ortak repo yüzeyi bloğu>

Dosyan: docs/superpowers/research/2026-08-14-mira-ara/yol-1-tasarimdan.md
```

- [ ] **Adım 3: Yol 2'nin görev metni**

```
Sen "Yol 2 · Repodan tasarıma" yolusun. Öteki iki yol tasarımdan uygulamaya yürüyor; sen ters
yönden, uygulamadan tasarıma yürüyeceksin. Tasarım tarafının tamamı sana serbest.

ARAÇ: DesignSync. Şemasını yüklemek için önce ToolSearch'ü "select:DesignSync" sorgusuyla çağır.
Proje: 3c06e399-3b83-48b1-b186-26e56747823d
Serbest dosyalar: HANDOFF.md, QueenAgent Handoff.dc.html, QueenAgent.dc.html,
QueenAgent Frames.dc.html. support.js ve .thumbnail kaynak değildir, çekme.

Tasarımın sözleşmesi TEK KATMANDIR — eski sürüm yoktur, belge bugünkü davranışı anlatır.
Sözleşmenin iki hâli (markdown ve sayfa) çelişirse ikisini de yaz, karar verme.

YÜRÜYÜŞ — iki ayrı işin var. Envanteri BİR KEZ çıkarırsın, iki farklı tabana karşı sorgularsın.

İŞ A — fark çıkarma:
1. Bugünkü uygulamanın envanterini çıkar: her ekran, her bölge, her kontrol, her durum, her geçiş,
   her metin, her görsel kural.
2. Her maddeyi tasarım v2'de ara ve üç kovadan birine at:
   · Karşılığı var, aynı  → YAZMA.
   · Karşılığı var, farklı → "değişecek".
   · Karşılığı YOK        → "öksüz". Bilerek mi kaldırıldı, tasarım mı atladı — KARAR VERME.
3. Kapanış taraması: envanterin bugünden başladığı için, tasarım v2'de tamamen yeni olup uygulamada
   hiç tutamağı olmayan bir şeyi kaçırmış olabilirsin. Sonda tek bir tarama yap ve bulduğunu
   "eklenecek" türüyle ekle.

İŞ B — sadakat denetimi:
Envanterdeki her madde için ikinci bir soru sor: "uygulama BUGÜN hedeflediği tarifi tutturmuş mu?"
Bu sorunun tabanı tasarım v2 DEĞİL, repodaki Mira v1 belgeleridir:
  docs/superpowers/specs/2026-08-09-mira-v1-design.md
  docs/superpowers/plans/2026-08-09-mira-v1-roadmap.md
Bu soruyu tasarım v2'nin dokunmadığı yerlerde de sor; tüm uygulama denetlenir. Uygulama kendi
tarifini tutturamamışsa bu bir tasarım farkı DEĞİL, bir hatadır: "düzeltilecek" türüyle yaz ve
"Yeni tasarımda" satırı yerine "Tarifi neydi:" yaz.

İŞ A ile İŞ B'nin bulguları AYNI dosyaya, aynı biçimde girer — türleri onları zaten ayırıyor. Ama
iki iddiayı tek bulguda BİRLEŞTİRME: "bugün yanlış" ile "tasarım v2'de değişecek" ayrı bulgulardır.

<bulgu biçimi bloğu>
<ortak kısıtlar bloğu>
<ortak repo yüzeyi bloğu>

Dosyan: docs/superpowers/research/2026-08-14-mira-ara/yol-2-repodan.md
Kapanış raporunda İŞ A ve İŞ B'den kaçar bulgu çıktığını ayrı ayrı söyle.
```

- [ ] **Adım 4: Yol 3'ün görev metni**

```
Sen "Yol 3 · Handoff'tan repoya" yolusun. Görevin: tasarımın YAZILI sözleşmesindeki her kararı tek
tek alıp bugünkü uygulamada karşılığını bulmak ve fark varsa yazmak.

ARAÇ: DesignSync. Şemasını yüklemek için önce ToolSearch'ü "select:DesignSync" sorgusuyla çağır.
Proje: 3c06e399-3b83-48b1-b186-26e56747823d

ÇEKECEĞİN DOSYALAR — yalnız bunlar:
  HANDOFF.md
  QueenAgent Handoff.dc.html (aynı sözleşmenin sayfa hâli)

KESİN YASAK: QueenAgent.dc.html ve QueenAgent Frames.dc.html dosyalarını ÇEKME. Bu yolun tüm
değeri, yalnız yazılı kararlardan yürümenden geliyor — çizime bakarsan Yol 1'in kopyası olursun ve
çıktın geçersiz sayılır. Çağrıların kayda geçiyor; ihlal görünür.
support.js ve .thumbnail de çekilmez.

SÖZLEŞME TEK KATMANDIR. Üst üste binmiş sürüm yok; belge kendini "bugünkü davranışı anlatır, eski
spec'i değil" diye tanımlıyor. Eski bir spec arama. Sözleşmenin iki hâli birbiriyle çelişirse
ikisini de yaz, karar verme.

YÜRÜYÜŞ:
- Sözleşmenin her bölümündeki her kararı tek tek al ve bugünkü uygulamada karşılığını ara.
- Şu bölümleri atlamadan tara: zihinsel model · yerleşim ve kaydırma sözleşmesi · çekirdek döngü ·
  Markdown render · model seçici · yıkıcı eylemler · boş hâller · duyarlı yerleşim ·
  klavye ve erişilebilirlik · görsel dil.
- "Deliberately removed" başlıklı bölüm çok değerlidir: orada sayılan her şey bugün uygulamada
  duruyorsa "öksüz" türünde bulgudur. Tek tek kontrol et.
- "Open items" başlıklı bölümdeki maddeler tasarımın kendi açık bıraktıklarıdır. Bugün uygulamada
  karşılığı varsa bunu bir bulgu olarak yaz ve "Not: tasarım söylemiyor" ekle.
- Sözleşmede adı geçip hiçbir yerde tarif edilmemiş bir şey görürsen (örneğin bir menü yalnızca
  klavye sırasında anılıyorsa) bunu "Not: tasarım söylemiyor" ile işaretle.

NOT: "düzeltilecek" türünü sen kullanamazsın — o tür uygulamanın kendi tarifinden (Mira v1)
sapmasını gösterir, sen ise Mira v1 belgesini hiç görmüyorsun. Senin türlerin: eklenecek,
değişecek, öksüz.

<bulgu biçimi bloğu>
<ortak kısıtlar bloğu>
<ortak repo yüzeyi bloğu>

Dosyan: docs/superpowers/research/2026-08-14-mira-ara/yol-3-handofftan.md
```

- [ ] **Adım 5: Üçünü tek mesajda gönder**

Üç `Agent` çağrısı **aynı mesajda** yapılır ki paralel koşsunlar. Hepsi `general-purpose` tipinde.
Etiketler: `yol-1-tasarimdan`, `yol-2-repodan`, `yol-3-handofftan`.

Beklerken hiçbir şey yapma — üç listeyi görmeden çakıştırmaya başlanamaz.

- [ ] **Adım 6: Kabul denetimi — biçim**

| Kontrol | Kabul ölçütü |
|---|---|
| Dosya | Üç dosya da yazılmış, boş değil |
| Biçim | Her bulguda Tür, Etiket, Alan, Bugün, Yeni tasarımda (ya da Tarifi neydi), Dayanak var |
| Tür | Tanımlı dörtlüden; Yol 1 ve Yol 3'te `düzeltilecek` yok |
| Geçiş | `Bugün` ve `Yeni tasarımda` satırları "ne olunca ne olur" anlatıyor |
| Kod dili | Dosya adı, uç nokta, bileşen adı geçmiyor |
| Karar | Hiçbir bulguda "doğrusu şu olmalı" yok |
| Kapsam | Hem `davranış` hem `görsel` etiketli bulgular var |
| Dil | Türkçe; arayüz etiketleri İngilizce ve olduğu gibi |

Ölçütü tutturamayan yolu **yeniden koşturma** — eksiği ajana `SendMessage` ile bildir; bağlamı
yerinde durduğu için düzeltmesi ucuzdur.

- [ ] **Adım 7: Kabul denetimi — körlük**

Bu denetim atlanamaz; üç yollu yöntemin tek kırılgan noktası burasıdır.

| Yol | Çağrı kaydında görünmemesi gereken |
|---|---|
| Yol 1 | `HANDOFF.md`, `QueenAgent Handoff.dc.html` |
| Yol 3 | `QueenAgent.dc.html`, `QueenAgent Frames.dc.html` |
| Üçü de | ara klasördeki başka bir yolun dosyası |

İhlal varsa o yolun çıktısı geçersizdir: dosyasını sil, ajanı sıfırdan koş, yasağı görev metninde
bir kez daha vurgula. Ara klasör ihlalinde ise okumadan sonra yazdığı kısım atılır.

- [ ] **Adım 8: Kullanıcıya ara durum bildir**

Üç dosyanın yolunu ver, okumak isterse okusun. Commit yok.

---

## Görev 2: Çakıştırma ve güven derecelendirmesi

**Çıktı:** tek birleşik fark tablosu; her satırda hangi yolların gördüğü ve güven damgası.

Bu görevi **ana oturum yapar, alt-ajan değil.** Üç listeyi birden gören tek yer burasıdır.

- [ ] **Adım 1: Normalize et**

Aynı farkın üç farklı cümlesini tek satıra indir. Birleştirme **elle** karar verilir; ölçüt `Bugün`
ve `Yeni tasarımda` satırlarının **aynı geçişi** anlatması, başlık benzerliği değil.

- [ ] **Adım 2: Damgala**

| Kaç yol gördü | Damga |
|---|---|
| 3/3 | kesin |
| 2/3 | güçlü |
| 1/3 | zayıf sinyal → Görev 3 |

`düzeltilecek` türü damgalanmaz: yalnız Yol 2 üretebildiği için tavanı 1/3'tür, örtüşme onun
hakkında hiçbir şey söylemez. Bu türdeki her bulgu Görev 3'e gider.

- [ ] **Adım 3: Çelişkileri ayır**

İki yol aynı konuda farklı şey söylüyorsa satır `çelişki` damgası alır ve **iki ifade de** yazılır.

- [ ] **Adım 4: `tasarım söylemiyor` notlu maddeleri ayır**

Bunlar belgenin 4. bölümünü besleyecek. `öksüz` türü ayrılmaz; tür sütunuyla ana listede durur.

- [ ] **Adım 5: Kabul denetimi**

Hiçbir madde kaybolmamalı: giriş sayısı = birleşik tablodaki satır + eriyen tekrar + 4. bölüme
ayrılan.

---

## Görev 3: Zayıf sinyalleri ve çelişkileri elle doğrula

- [ ] **Adım 1: Her zayıf sinyali kaynağına kadar takip et**

`Dayanak` satırındaki kaynağa dön ve iddiayı sına. Tasarım tarafıysa DesignSync ile, uygulama
tarafıysa `mira/` altında Read/Grep ile.

Zayıf sinyal **beklenen** bir sonuçtur: Yol 1 etiket metinlerini, Yol 3 klavye ve kural
ayrıntılarını, Yol 2 öksüzleri tek başına görür.

- [ ] **Adım 2: Sonucu işle**

Doğrulandıysa ana listeye "elle doğrulandı" notuyla girer. Doğrulanamadıysa **atılmaz** —
`zayıf sinyal` damgasıyla listede durur.

- [ ] **Adım 3: Çelişkileri doğrula**

İki ifadeyi de kaynağına kadar takip et. Amaç hangisinin doğru olduğuna karar vermek değil,
çelişkinin gerçek mi yoksa bir yolun okuma hatası mı olduğunu anlamak. Okuma hatasıysa düzelt;
gerçekse belgeye çelişki olarak, iki ifadeyle birlikte girer.

- [ ] **Adım 4: Kabul denetimi**

Hiçbir zayıf sinyal "silindi" durumunda kalmamalı.

---

## Görev 4: Repo belgeleri çarpışması

**Çıktı:** belgenin 3. bölümünü besleyecek çarpışma tablosu.

Bu görevi **ana oturum yapar.** Üç yol da uygulamaya baktı, repo belgelerine değil.

- [ ] **Adım 1: Dört belgeyi tasarım v2'ye karşı oku**

`CLAUDE.md`'nin Mira bölümü · `mira/FOUNDATION.md` · `mira/CODE-STANDARD.md` ·
`docs/superpowers/specs/2026-08-09-mira-v1-design.md`.

- [ ] **Adım 2: Çelişen satırları yan yana koy**

Tablo: *konu · repo belgesi bugün ne diyor · tasarım v2 ne getiriyor*. Bilinen adaylar — tarama
bunlarla sınırlı değil: ürün adı, aramanın varlığı, proje silmenin varlığı, proje açıklaması,
selamlama, model seçimi.

- [ ] **Adım 3: Kabul denetimi**

Tabloda hiçbir satırda "doğrusu şu", "şu belge güncellenmeli" cümlesi olmamalı. Bu bölüm iki metni
yan yana koyar, karar vermez.

---

## Görev 5: Belgeyi yaz

**Çıktı:** `docs/superpowers/research/2026-08-14-mira-tasarim-farklari.md`

- [ ] **Adım 1: Dört bölümü sırayla yaz**

| # | Bölüm | Kaynağı |
|---|---|---|
| 0 | Başlık notu | Görev 5 Adım 2 |
| 1 | Özet | tasarım v2 tek paragrafta ne getiriyor |
| 2 | **Fark listesi** | Görev 2'nin tablosu + Görev 3'ün notları |
| 3 | Repo belgeleri çarpışması | Görev 4'ün tablosu |
| 4 | Tasarımın cevaplamadıkları | Görev 2 Adım 4'ün listesi |

- [ ] **Adım 2: 0. bölümün notunu tam yaz**

Dört bilgiyi taşır: (1) tasarım kendine "v2" diyor, repodaki taban "Mira v1"; (2) ürün adı tasarımda
QueenAgent, repoda Mira; (3) tasarımın sözleşmesi tek katmandır, eski spec aranmaz; (4) belgenin
dili Türkçe, arayüz metinleri kaynaktaki hâliyle İngilizce alıntılanır.

- [ ] **Adım 3: 2. bölümü tek düz liste olarak yaz**

Numaralandırma **kesintisiz** tektir; alt başlıklar yalnız okunabilirlik için alan alandır ve
numarayı sıfırlamaz. Her madde: *ne · tür · davranış/görsel · bugün → tasarım v2'de · Y1/Y2/Y3 ·
damga*.

- [ ] **Adım 4: `düzeltilecek` maddelerinin ayrımını koru**

2. bölümün başına bir cümle: "bugün yanlış" ile "tasarım v2'de değişecek" farklı iki iddiadır ve tür
sütunu onları ayırır.

---

## Görev 6: Öz-denetim, teslim ve temizlik

- [ ] **Adım 1: Kod dili taraması**

Belgede dosya uzantısı, yol ayracı, uç nokta, bileşen adı ya da katman adı geçiyor mu? Geçiyorsa
davranış cümlesine çevir. İstisna: künye, bağlantılar ve 3. bölümdeki belge adları.

- [ ] **Adım 2: Karar taraması**

Belge hiçbir yerde "doğrusu şu", "şöyle olmalı" demiyor olmalı. Diyorsa çıkar.

- [ ] **Adım 3: Bütünlük taraması**

Üç ara dosyadaki her madde belgenin bir bölümünde karşılığını buluyor mu?

- [ ] **Adım 4: Kapsam taraması**

Dört tür de temsil ediliyor mu? Hiç `görsel` etiketli madde yoksa görsel dil taranmamış demektir.

- [ ] **Adım 5: Kullanıcıya sun**

Belgeyi bildir ve incelemesini iste. **Commit etme.**

- [ ] **Adım 6: Ara klasörü sil**

Kullanıcı belgeyi onayladıktan **sonra**, ve silmeden önce sorarak.

- [ ] **Adım 7: Commit**

```
git add docs/superpowers/research/2026-08-14-mira-tasarim-farklari.md
git add docs/superpowers/specs/2026-08-14-mira-tasarim-fark-cikarma-design.md
git add docs/superpowers/plans/2026-08-14-mira-tasarim-fark-cikarma.md
git commit -m 'docs(mira): tasarim v2 ile bugunku uygulamanin farklari'
```

Mesajda **çift tırnak yok** — PowerShell'de mesajı bölüyor.
