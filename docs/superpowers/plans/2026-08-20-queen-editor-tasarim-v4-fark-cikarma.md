# Tasarım v4 Fark Çıkarma — Uygulama Planı

> **Ajanla çalışanlar için:** ZORUNLU ALT-BECERİ — bu plan `superpowers:subagent-driven-development`
> ya da `superpowers:executing-plans` ile görev görev uygulanır. Adımlar takip için kutucuk (`- [ ]`)
> biçimindedir. Kod üretmediği için TDD döngüsü yoktur; her görev bir **kabul denetimi** ile kapanır.

**Hedef:** claude.ai/design'daki "Queen Editor Basit v4" ile bugün çalışan uygulama arasındaki
farkları üç bağımsız yolla çıkarıp çakıştırmak ve tek bir Türkçe md'ye dökmek.

**Yaklaşım:** Üç alt-ajan, üç ayrı kaynağa demirleyerek aynı anda ve birbirini görmeden tam fark
listesi çıkarır; her biri bulgularını ilerledikçe repodaki kendi dosyasına yazar. Ana oturum üç
listeyi çakıştırır, güven damgası atar, zayıf sinyalleri elle doğrular ve belgeyi yazar. Hiçbir görev
kod değiştirmez.

**Araçlar:** DesignSync (tasarım projesi, salt okunur) · Read/Grep (repo) · Agent (üç yol)

**Tasarım belgesi:**
[2026-08-20-queen-editor-tasarim-v4-fark-cikarma-design.md](../specs/2026-08-20-queen-editor-tasarim-v4-fark-cikarma-design.md)

## Global kısıtlar

Her görevin gereksinimleri bu bölümü içerir.

- **Çıktı belgesinde kod dili geçmez.** Dosya adı, uç nokta, bileşen adı, veri dosyası, katman adı —
  hiçbiri. Yalnızca kullanıcının gördüğü davranış ve görünüm. Kaynağı okumak serbesttir; **yazmak
  yasaktır.**
- **Tasarım dosyaları hiçbir yere kaydedilmez** — ne repoya, ne geçici klasöre. Ara çıktı
  dosyalarına giren şey **bulgudur**; tasarım kaynağının kendisi, alıntısı ya da özeti değil.
- **Tasarım projesine yazılmaz.** DesignSync yalnız `get_project`, `list_files`, `get_file` ile
  kullanılır; `finalize_plan`, `write_files`, `delete_files`, `register_assets` **çağrılmaz**.
- **Kod değiştirilmez.** Bu turda tek satır kod yazılmaz.
- **Belge karar vermez.** Çelişki işaretlenir, hangisinin kazanacağı söylenmez.
- **Üçlü isim çakışması:** "v4" üç ayrı şeyin adı — **tasarım v4** (karşılaştırdığımız şey),
  **roadmap v4** (repodaki 8 Ağustos yol haritası, bitti) ve `feat/queen-editor-v4` (dal adı). Her
  yerde tam ad yazılır; yalın "v4" hiçbir yerde kullanılmaz. Repo tarafına roadmap numarası
  **atanmaz**, "bugünkü uygulama" denir.
- **Katman kuralı:** `HANDOFF.md` üst üste binmiş katmanlardan oluşur. Geçerlilik sırası
  **v3.5 > v3.4 > v3.3 > v3.2 > v3.1 > v3 > v2 > v1**. Üstü çizili (`~~…~~`) metin **ölüdür**, bulgu
  üretmez.
- **Geri alma kuralı:** `DEGISIKLIK-GUNLUGU.md` denenip vazgeçilenleri de kaydeder. "Kaldırıldı",
  "vazgeçildi", "reddedildi", "geri alındı" diyen her madde **yalnız son hâliyle** geçerlidir; ara
  aşama bulgu üretmez.
- **Terminoloji tasarımdan alınır:** **kare** = içerik birimi (foto + video + ses), **fotoğraf** =
  yalnız foto katmanı. Tasarım v4'ün getirdiği ikinci küme: **üretim modu** ve üç değeri —
  **standart**, **loop**, **sonrakine bağla**.
- **Dil:** her ara çıktı ve nihai belge Türkçe.
- **Tasarım projesi:** `ff9837f9-94c5-4843-9d14-7bda150e8425` ("Copy of Queen Editor"). Geçmiş
  turların projesi (`efad1f83-…`) **hiç açılmaz**.
- **Bugünkü uygulama:** `queen-editor/` — arayüz `queen-editor/frontend/src/`, davranış kuralları
  `queen-editor/backend/`, yazılı tarif `queen-editor/FOUNDATION.md` ve `queen-editor/BACKLOG.md`.
- **Kapsam dışı tasarım kaynakları:** `screenshots/` · `direction-e.jsx` · v1, v2, v3 zincirleri ·
  eski `app.jsx` hattı (`app.jsx`, `simple-app.jsx`, `simple-screens.jsx`) ·
  `Queen Editor Wireframes*.html` · `.design-canvas.state.json` · `.thumbnail`.

## Bulgu biçimi

Üç yol da bulgularını **aynı biçimde** yazar; çakıştırma buna dayanır. Aşağıdaki blok, üç görev
metnine de **aynen** kopyalanır.

```
### <kısa başlık>
- **Tür:** eklenecek | değişecek | düzeltilecek | öksüz
- **Etiket:** davranış | görsel
- **Alan:** Projeler | Proje ekranı ve panel şeridi | Fotoğraf üret | Video üret | Ses üret |
            Kuyruk | Üreticiler ve kurulum | Galeri | Seçim barı ve toplu eylemler |
            Detay sayfası | Export ekranı | Adlandırma ve kimlik | Uygulama geneli
- **Bugün:** <tek cümle — bugünkü uygulamada ne olunca ne oluyor>
- **Tasarım v4'te:** <tek cümle — ne olunca ne olacak>
- **Not:** (varsa) tasarım söylemiyor
- **Dayanak:** <bu bulguyu nereden çıkardın — kaynağın adı, tek cümle>
```

Tür seçimi:

| Tür | Ne zaman |
|---|---|
| `eklenecek` | bugün hiç karşılığı yok |
| `değişecek` | karşılığı var, farklı |
| `düzeltilecek` | bugün **kendi tarifine göre** zaten yanlış |
| `öksüz` | bugün var, tasarım v4'te karşılığı yok |

Biçim kuralları:

- `Bugün` ve `Tasarım v4'te` satırları **geçiş** anlatır, duruş değil. "Duraklat butonu var"
  yanlıştır; "Duraklat'a basınca çalışan kare bitirilir, arada *Duraklatılıyor…* görünür, sonra
  bekleyen sayısı 7'den 8'e çıkar" doğrudur.
- Bugün hiç karşılığı yoksa `Bugün` satırı tam olarak **"bugün yok"**tur; uydurulmuş karşılık
  aranmaz.
- `düzeltilecek` türünde `Tasarım v4'te` satırı yerine **`Tarifi neydi:`** yazılır — bu bir tasarım
  v4 farkı değil, uygulamanın kendi tarifinden sapmasıdır.
- `öksüz` türünde `Tasarım v4'te` satırı **"karşılığı yok"**tur. Bilerek mi kaldırıldı, tasarım mı
  atladı — **karar verilmez**, yalnız işaretlenir.
- Tasarımın cevaplamadığı bir konu `Not: tasarım söylemiyor` alır; uydurulmaz.

## `düzeltilecek` türünün tabanı

Taban = `HANDOFF.md`'nin hâlâ geçerli katmanları + `queen-editor/FOUNDATION.md` +
`queen-editor/BACKLOG.md`. Üstü çizilmemiş ve sonraki katmanca ezilmemiş her kural bir tariftir.
Yol 2 bu tabanı göremez, dolayısıyla o türde bulgu üretemez — **bu türde tavan 2/3'tür.**

## Dosya yapısı

| Dosya | Sorumluluğu |
|---|---|
| `docs/superpowers/research/2026-08-20-v4-ara/yol-1-anlati.md` | Yol 1 · İş A — ham fark listesi. Ajan **ilerledikçe** yazar |
| `docs/superpowers/research/2026-08-20-v4-ara/yol-1-brif-celiskisi.md` | Yol 1 · İş B — brifin geri alınan kararları |
| `docs/superpowers/research/2026-08-20-v4-ara/yol-2-tasarim-kaynagi.md` | Yol 2'nin ham bulgu listesi |
| `docs/superpowers/research/2026-08-20-v4-ara/yol-3-ters-yon.md` | Yol 3'ün ham bulgu listesi (İş A + İş B) |
| `docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md` | **Tek çıktı.** 5 bölümlük fark belgesi (Görev 5'te oluşturulur) |

Başka dosya oluşturulmaz veya değiştirilmez.

**Ara klasörün ömrü:** `2026-08-20-v4-ara/` commit **edilmez**. Kullanıcı çakıştırmadan önce ham
listeleri okuyabilsin diye repoda durur; Görev 6'da, kullanıcı onayıyla silinir.

---

## Görev 1: Üç yolu aynı anda koş

**Çıktı:** birbirini görmemiş üç tam fark listesi ve bir brif çelişkisi listesi, dört ayrı dosyada.

**Arayüz:**
- Üretir: `yol-1-anlati.md`, `yol-1-brif-celiskisi.md`, `yol-2-tasarim-kaynagi.md`,
  `yol-3-ters-yon.md` — fark listeleri yukarıdaki **Bulgu biçimi**nde.
- Her ajan ayrıca kısa bir **kapanış raporu** döndürür: kaç bulgu yazdı, hangi alanları taradı,
  atladığı/emin olamadığı yer kaldı mı. Bulgular dönüş değerinde değil, dosyadadır.

- [ ] **Adım 1: Ara klasörü aç**

Üç ajan da kendi dosyasını bu klasöre yazacak; klasör yoksa ilk yazma çağrısı ajanı boşa düşürür.

```powershell
New-Item -ItemType Directory -Force docs/superpowers/research/2026-08-20-v4-ara
```

- [ ] **Adım 2: Yol 1'in görev metni**

Ajan tipi `general-purpose`, etiket `yol-1-anlati`. Metin şudur — `<BULGU BİÇİMİ BLOĞU>` yazan yere
bu planın **Bulgu biçimi** bölümü (kod bloğu + tür tablosu + biçim kuralları) aynen kopyalanır.

```
Sen "Yol 1 · Anlatı" yolusun. İki işin var. İş A: tasarımın yazılı belgelerindeki her kararı tek
tek alıp bugün çalışan uygulamada karşılığını bulmak ve fark varsa yazmak. İş B: kullanıcının
20 Ağustos brifinde verdiği kararlardan tasarımın geri aldıklarını çıkarmak.

ARAÇ: DesignSync. Şemasını yüklemek için önce ToolSearch'ü "select:DesignSync" sorgusuyla çağır.
Proje: ff9837f9-94c5-4843-9d14-7bda150e8425

ÇEKECEĞİN TASARIM DOSYALARI — yalnız bu dördü:
  HANDOFF.md, EKRAN-NOTLARI.md, DEGISIKLIK-GUNLUGU.md, CLAUDE.md

KESİN YASAK: wireframe kaynağına dokunma. Queen Editor Basit v4.html, simple-app-v4.jsx,
simple-screens-v4.jsx, export-designs-v4.jsx, wireframe-kit.jsx, tweaks-panel.jsx,
design-canvas.jsx, styles.css — hiçbirini çekme. Senin değerin yalnız yazılı kararlardan
yürümenden geliyor; çizime bakarsan Yol 2'nin kopyası olursun ve çıktın geçersiz sayılır.
Çağrıların kayda geçiyor; ihlal görünür.
screenshots/, direction-e.jsx, eski sürüm zincirleri (v1/v2/v3, app.jsx, simple-app.jsx,
simple-screens.jsx, Queen Editor Wireframes*.html) de kapsam dışı — çekme.
Yazma çağrısı yapma: finalize_plan, write_files, delete_files, register_assets yok.
Çektiğin tasarım içeriğini hiçbir dosyaya kaydetme — dosyaya yalnız BULGU yazılır.

BUGÜNKÜ UYGULAMA — Read ve Grep ile oku:
  queen-editor/frontend/src/ (arayüz) · queen-editor/backend/ (davranış kuralları)
  queen-editor/FOUNDATION.md ve queen-editor/BACKLOG.md (uygulamanın yazılı tarifi)

İKİ GEÇERSİZLİK KURALI — bunlar olmadan geçersiz kılınmış kararları bulgu diye yazarsın:
1. KATMAN KURALI. HANDOFF.md üst üste binmiş katmanlardan oluşuyor. Geçerlilik sırası
   v3.5 > v3.4 > v3.3 > v3.2 > v3.1 > v3 > v2 > v1. Sonraki bölüm önceki bölümle çeliştiğinde
   sonraki geçerlidir. Üstü çizili (~~…~~) metin ÖLÜDÜR; ondan bulgu üretme.
2. GERİ ALMA KURALI. DEGISIKLIK-GUNLUGU.md denenip vazgeçilenleri de kaydediyor. "Kaldırıldı",
   "vazgeçildi", "reddedildi", "geri alındı" diyen her madde YALNIZ SON HÂLİYLE geçerlidir.
   Örnek: kart üstündeki mod şeridi eklenip tamamen kaldırılmış — "kartın üstünde mod şeridi
   olacak" diye bulgu yazmak hatadır. Ara aşama bulgu üretmez.

İŞ A — YÜRÜYÜŞ:
- HANDOFF.md'deki her kararı tek tek al; v3.3, v3.4 ve v3.5 bölümlerini atlamadan tara.
- Şu bölümleri de tara, atlama:
  · "Kural olarak yazılanlar (ekran çizilmedi)" — ekranda görünmeyen ama bağlayıcı kararlar.
  · "Değişmeyenler" — tasarım "değişmedi" diyor olabilir ama uygulama oradan sapmış olabilir;
    o zaman bulgu "değişecek" değil, "düzeltilecek" türündedir.
  · "Karara bağlananlar".
  · "Görsel dil" — renk rolleri, tipografi, etiket biçimi, ölçü.
- EKRAN-NOTLARI.md'yi ekran ekran yürü (01 proje listesi → 19 export). Bu dosya v4 turunda
  wireframe kartlarından buraya taşındı; ekranların ayrıntısı orada.
- DEGISIKLIK-GUNLUGU.md'nin v4 bölümündeki her maddeyi bir karar say.
- CLAUDE.md'deki yıkıcı eylem butonu standardını da bir karar say.
- Her karar için bugünkü uygulamaya bak, ne yaptığını öğren, farkı yaz.

DÜZELTİLECEK TÜRÜNÜN TABANI: HANDOFF.md'nin hâlâ geçerli katmanları + FOUNDATION.md + BACKLOG.md.
Üstü çizilmemiş ve sonraki katmanca ezilmemiş her kural bir tariftir; uygulama ondan sapmışsa bu
bir tasarımcı kararı değil, bir hatadır.

KAPSAM: davranış VE görsel. Renk, boşluk, tipografi, ikon, ölçü dahil. Her bulguya "davranış" ya da
"görsel" etiketi koy.

TERMİNOLOJİ — tasarımın kendi sözcükleri: "kare" = içerik birimi (foto + video + ses),
"fotoğraf" = yalnız foto katmanı. Tasarım v4'ün ikinci kümesi: "üretim modu" ve üç değeri —
"standart", "loop", "sonrakine bağla". Karıştırma.

ÜÇLÜ İSİM ÇAKIŞMASI: "v4" üç ayrı şeyin adı — tasarım v4 (senin baktığın), roadmap v4 (repodaki
8 Ağustos yol haritası, bitti geçti) ve feat/queen-editor-v4 (dal adı). Her yerde tam ad yaz;
yalın "v4" kullanma. Repo tarafına roadmap numarası atama, "bugünkü uygulama" de.

<BULGU BİÇİMİ BLOĞU>

İŞ B — BRİF ÇELİŞKİSİ (ayrı dosyaya):
Şu iki repo belgesini oku:
  docs/2026-08-20-queen-editor-arayuz-brifi.md
  docs/superpowers/plans/2026-08-20-queen-editor-istekler.md
Brifteki her "Karar verildi" maddesini tek tek al ve tasarımın ne yaptığına bak. Tasarım o kararı
uygulamışsa YAZMA. Uygulamamış, değiştirmiş ya da geri almışsa yaz. Bilinen bir örnek: brif
"mod seçimi kartın üstünde yapılır, kart ikonla gösterir" diyor; tasarım bunu deneyip kaldırmış ve
seçimi üretim paneline taşımış. Başka örnekler de var, hepsini ara.

Biçim — İş A'dan farklı, kısa:
### <brifin maddesi>
- **Brif ne dedi:** <tek cümle>
- **Tasarım ne yaptı:** <tek cümle>
- **Tasarımın gerekçesi:** <tasarımın kendi yazdığı gerekçe; yoksa "gerekçe yazılmamış">

KARAR VERME. Hangisinin doğru olduğunu söyleme, "brif haklıydı" ya da "tasarım haklı" yazma.
Bu liste kullanıcının kendi kararını gözden geçirmesi için var.

NEREYE YAZACAKSIN — en önemli kural:
İş A'yı docs/superpowers/research/2026-08-20-v4-ara/yol-1-anlati.md dosyasına,
İş B'yi docs/superpowers/research/2026-08-20-v4-ara/yol-1-brif-celiskisi.md dosyasına yaz.
İkisini de İLERLEDİKÇE yaz. Sonda toplu yazma: yarıda kesilirsen emeğin tümüyle gider. Her birkaç
bulguda bir dosyayı güncelle.
Bu klasördeki diğer dosyaları (yol-2-*.md, yol-3-*.md) AÇMA ve OKUMA. Onlar öteki iki yolun
listesi; okursan körlük bozulur ve üç yollu yöntemin anlamı kalmaz.
Dönüş değerin bulgu listesi DEĞİL, kısa bir kapanış raporudur: İş A'da kaç bulgu, İş B'de kaç
madde yazdın, hangi alanları taradın, atladığın ya da emin olamadığın yer kaldı mı.

KURALLAR:
- Bulgular geçiş anlatır, duruş değil.
- Çıktında kod dili geçmesin: dosya adı, uç nokta, bileşen adı, katman adı yok. Kaynağı okursun ama
  yazdığın şey kullanıcının gördüğü davranıştır.
- Karar verme. Çelişki görürsen iki ifadeyi de yaz, hangisinin doğru olduğunu söyleme.
- Tasarımın cevaplamadığı bir şeye rastlarsan "tasarım söylemiyor" notu koy. Uydurma, tahmin etme.
- Türkçe yaz.
```

- [ ] **Adım 3: Yol 2'nin görev metni**

Ajan tipi `general-purpose`, etiket `yol-2-tasarim-kaynagi`.

```
Sen "Yol 2 · Tasarım kaynağı" yolusun. Görevin: tasarım v4 wireframe'inin kendisinden envanter
çıkarıp bugünkü uygulamanın envanteriyle karşılaştırmak.

ARAÇ: DesignSync. Şemasını yüklemek için önce ToolSearch'ü "select:DesignSync" sorgusuyla çağır.
Proje: ff9837f9-94c5-4843-9d14-7bda150e8425

ÇEKECEĞİN DOSYALAR — yalnız bunlar:
  Queen Editor Basit v4.html, simple-app-v4.jsx, simple-screens-v4.jsx, export-designs-v4.jsx,
  wireframe-kit.jsx, tweaks-panel.jsx, design-canvas.jsx, styles.css

KESİN YASAK: HANDOFF.md, EKRAN-NOTLARI.md, DEGISIKLIK-GUNLUGU.md ve CLAUDE.md dosyalarını ÇEKME.
Bu yolun tüm değeri, tasarımın yazılı anlatısını hiç görmemiş olmandan geliyor — anlatıyı okursan
Yol 1'in kopyası olursun ve çıktın geçersiz sayılır. Çağrıların kayda geçiyor; ihlal görünür.
screenshots/, direction-e.jsx ve eski sürüm zincirlerini (v1/v2/v3, app.jsx, simple-app.jsx,
simple-screens.jsx, Queen Editor Wireframes*.html) de çekme; başka ya da geçersiz kılınmış
tasarımlara aitler.
Yazma çağrısı yapma: finalize_plan, write_files, delete_files, register_assets yok.
Çektiğin tasarım içeriğini hiçbir dosyaya kaydetme — dosyaya yalnız BULGU yazılır.

BU TURDA SENİN İŞİN DAHA ZOR VE DAHA DEĞERLİ: v4 turunda wireframe kartlarındaki bütün açıklama
yazıları kaldırıldı ve ayrı bir dosyaya taşındı. Yani kaynak artık kendini anlatmıyor; ne yaptığı
yalnız çizimden ve durum makinesinden okunuyor. Yazıya hiç geçmemiş ayrıntıları görecek tek yol
sensin.

YÜRÜYÜŞ:
1. v4 wireframe'inden envanter çıkar: hangi ekran, hangi bölge, hangi kontrol, hangi durum,
   durumlar arası hangi geçiş, hangi metin, hangi boş hâl, hangi renk/boşluk/ikon.
   Wireframe React kaynağıdır; durum makinesi orada yazılıdır — oku ve geçişi anlat.
   Ekran adlarını ve sıralarını kaynağın kendisinden çıkar; ekran listesi 01'den 19'a kadar gider.
2. Aynı envanteri bugünkü uygulamadan çıkar: queen-editor/frontend/src/ (arayüz) ve
   queen-editor/backend/ (davranış kuralları). Read ve Grep ile oku.
3. İki envanteri satır satır karşılaştır. Her farkı yaz.

BU YOLUN ÖZEL YAKALADIĞI ŞEY: yazıya hiç geçmemiş olanlar — buton etiketlerinin tam metni, ara
durumlar, boş hâller, hata hâlleri, sayaçların biçimi, kutuların ölçüsü, bloklar arası boşluk.
Bunları özellikle ara.

KAPSAM: davranış VE görsel. Renk, boşluk, tipografi, ikon, ölçü dahil. Her bulguya "davranış" ya da
"görsel" etiketi koy.

TERMİNOLOJİ — tasarımın kendi sözcükleri: "kare" = içerik birimi (foto + video + ses),
"fotoğraf" = yalnız foto katmanı. Tasarım v4'ün ikinci kümesi: "üretim modu" ve üç değeri —
"standart", "loop", "sonrakine bağla". Karıştırma.

ÜÇLÜ İSİM ÇAKIŞMASI: "v4" üç ayrı şeyin adı — tasarım v4 (senin baktığın), roadmap v4 (repodaki
8 Ağustos yol haritası, bitti geçti) ve feat/queen-editor-v4 (dal adı). Her yerde tam ad yaz;
yalın "v4" kullanma. Repo tarafına roadmap numarası atama, "bugünkü uygulama" de.

<BULGU BİÇİMİ BLOĞU>

NOT: "düzeltilecek" türünü sen kullanamazsın — o tür bugünkü uygulamanın kendi yazılı tarifinden
sapmasını gösterir, sen ise o tarifi (tasarımın kural metnini) hiç görmüyorsun. Senin türlerin:
eklenecek, değişecek, öksüz.

NEREYE YAZACAKSIN — en önemli kural:
Bulgularını docs/superpowers/research/2026-08-20-v4-ara/yol-2-tasarim-kaynagi.md dosyasına,
İLERLEDİKÇE yaz. Sonda toplu yazma: yarıda kesilirsen emeğin tümüyle gider.
Bu klasördeki diğer dosyaları (yol-1-*.md, yol-3-*.md) AÇMA ve OKUMA.
Dönüş değerin bulgu listesi DEĞİL, kısa bir kapanış raporudur: kaç bulgu yazdın, hangi ekranları
taradın, atladığın ya da emin olamadığın yer kaldı mı.

KURALLAR:
- Bulgular geçiş anlatır, duruş değil.
- Çıktında kod dili geçmesin: dosya adı, uç nokta, bileşen adı, katman adı yok.
- Karar verme. Çelişki görürsen iki ifadeyi de yaz.
- Türkçe yaz.
```

- [ ] **Adım 4: Yol 3'ün görev metni**

Ajan tipi `general-purpose`, etiket `yol-3-ters-yon`.

```
Sen "Yol 3 · Ters yön" yolusun. Diğer iki yol tasarımdan uygulamaya yürüyor; sen ters yönden,
uygulamadan tasarıma yürüyeceksin. Senin kovan iki şeyi veriyor: tasarımda karşılığı olmayan
davranışlar (öksüzler) ve uygulamanın kendi tarifini tutturamadığı yerler.

ARAÇ: DesignSync. Şemasını yüklemek için önce ToolSearch'ü "select:DesignSync" sorgusuyla çağır.
Proje: ff9837f9-94c5-4843-9d14-7bda150e8425
Tasarım tarafının v4'ü sana tümüyle serbest: HANDOFF.md, EKRAN-NOTLARI.md, DEGISIKLIK-GUNLUGU.md,
CLAUDE.md ve v4 wireframe zinciri (Queen Editor Basit v4.html, simple-app-v4.jsx,
simple-screens-v4.jsx, export-designs-v4.jsx, wireframe-kit.jsx, tweaks-panel.jsx,
design-canvas.jsx, styles.css).
KAPSAM DIŞI — çekme: screenshots/, direction-e.jsx ve ESKİ SÜRÜM ZİNCİRLERİ (v1, v2, v3
dosyaları, app.jsx, simple-app.jsx, simple-screens.jsx, Queen Editor Wireframes*.html). Eski
zincirler geçersiz kılınmış tasarımdır; okursan ölü kuralı bulgu diye yazarsın.
Yazma çağrısı yapma: finalize_plan, write_files, delete_files, register_assets yok.
Çektiğin tasarım içeriğini hiçbir dosyaya kaydetme — dosyaya yalnız BULGU yazılır.

İKİ GEÇERSİZLİK KURALI:
1. KATMAN KURALI. HANDOFF.md katmanlı. Geçerlilik sırası v3.5 > v3.4 > v3.3 > v3.2 > v3.1 > v3 >
   v2 > v1. Üstü çizili (~~…~~) metin ÖLÜDÜR.
2. GERİ ALMA KURALI. DEGISIKLIK-GUNLUGU.md denenip vazgeçilenleri de kaydediyor. "Kaldırıldı",
   "vazgeçildi", "reddedildi", "geri alındı" diyen madde YALNIZ SON HÂLİYLE geçerlidir.

YÜRÜYÜŞ — iki ayrı işin var:

İŞ A — fark çıkarma:
1. Bugünkü uygulamanın davranış envanterini çıkar: her ekran, her bölge, her kontrol, her durum,
   her geçiş, her metin, her görsel kural. Kaynak: queen-editor/frontend/src/ ve
   queen-editor/backend/.
2. Envanterdeki her maddeyi tasarım v4'te ara ve üç kovadan birine at:
   · Karşılığı var, aynı  → değişmiyor, YAZMA.
   · Karşılığı var, farklı → "değişecek" türüyle yaz.
   · Karşılığı YOK        → "öksüz" türüyle yaz. Ya tasarım v4'te bilerek kaldırıldı, ya tasarım
                            atladı. HANGİSİ OLDUĞUNA KARAR VERME, sadece işaretle.
3. Kapanış taraması: envanterin bugünden başladığı için, tasarım v4'te tamamen yeni olup uygulamada
   hiç tutamağı olmayan bir şeyi kaçırmış olabilirsin. Sonda tek bir tarama yap: "tasarım v4'te
   dokunulmuş olup envanterimde hiç görünmeyen bir yer kaldı mı?" Bulduğunu "eklenecek" türüyle
   ekle.

İŞ B — sadakat denetimi:
Envanterdeki her madde için ikinci bir soru sor: "uygulama BUGÜN hedeflediği tarifi tutturmuş mu?"
Bu sorunun tabanı HANDOFF.md'nin hâlâ geçerli katmanları + queen-editor/FOUNDATION.md +
queen-editor/BACKLOG.md'dir. Üstü çizilmemiş ve sonraki katmanca ezilmemiş her kural bir tariftir.
Bu soruyu tasarım v4'ün dokunmadığı yerlerde de sor; tüm uygulama denetlenir.
Uygulama kendi tarifini tutturamamışsa bu bir tasarım v4 farkı DEĞİL, bir hatadır: "düzeltilecek"
türüyle yaz ve "Tasarım v4'te" satırı yerine "Tarifi neydi:" yaz.

İŞ A ile İŞ B'nin bulguları AYNI dosyaya, aynı biçimde girer — türleri ("değişecek"/"öksüz" ile
"düzeltilecek") onları zaten ayırıyor. Ama iki iddiayı tek bulguda birleştirme: "bugün yanlış" ile
"tasarım v4'te değişecek" farklı iki şeydir, ayrı bulgular olur.

UYARI: kaynağın ne dediğini yaz, çalışma zamanı hakkında tahmin yürütme. "Kod yanlış" ile "kod
doğru ama çalışırken patlıyor" ayrımını kaynağa bakarak yapamazsın.

KAPSAM: davranış VE görsel. Renk, boşluk, tipografi, ikon, ölçü dahil. Her bulguya "davranış" ya da
"görsel" etiketi koy.

TERMİNOLOJİ — tasarımın kendi sözcükleri: "kare" = içerik birimi (foto + video + ses),
"fotoğraf" = yalnız foto katmanı. Tasarım v4'ün ikinci kümesi: "üretim modu" ve üç değeri —
"standart", "loop", "sonrakine bağla". Karıştırma.

ÜÇLÜ İSİM ÇAKIŞMASI: "v4" üç ayrı şeyin adı — tasarım v4 (senin baktığın), roadmap v4 (repodaki
8 Ağustos yol haritası, bitti geçti) ve feat/queen-editor-v4 (dal adı). Her yerde tam ad yaz;
yalın "v4" kullanma. Repo tarafına roadmap numarası atama, "bugünkü uygulama" de.

<BULGU BİÇİMİ BLOĞU>

NEREYE YAZACAKSIN — en önemli kural:
Bulgularını docs/superpowers/research/2026-08-20-v4-ara/yol-3-ters-yon.md dosyasına, İLERLEDİKÇE
yaz. Sonda toplu yazma: yarıda kesilirsen emeğin tümüyle gider.
Bu klasördeki diğer dosyaları (yol-1-*.md, yol-2-*.md) AÇMA ve OKUMA.
Dönüş değerin bulgu listesi DEĞİL, kısa bir kapanış raporudur: kaç bulgu yazdın, hangi ekranları
taradın, İŞ A ve İŞ B'den kaçar bulgu çıktı, atladığın yer kaldı mı.

KURALLAR:
- Bulgular geçiş anlatır, duruş değil.
- Çıktında kod dili geçmesin: dosya adı, uç nokta, bileşen adı, katman adı yok.
- Karar verme. Çelişki görürsen iki ifadeyi de yaz.
- Tasarımın cevaplamadığı bir şeye rastlarsan "tasarım söylemiyor" notu koy.
- Türkçe yaz.
```

- [ ] **Adım 5: Üçünü tek mesajda gönder**

Üç `Agent` çağrısı **aynı mesajda** yapılır ki paralel koşsunlar. Hepsi `general-purpose` tipinde.

Beklerken **hiçbir şey yapma** — üç listeyi görmeden çakıştırmaya başlanamaz.

- [ ] **Adım 6: Kabul denetimi — biçim**

Dört dosya için ayrı ayrı kontrol et (`yol-1-brif-celiskisi.md` yalnız son üç satıra tabidir):

| Kontrol | Kabul ölçütü |
|---|---|
| Dosya var mı | Dört dosya da yazılmış, boş değil |
| Bulgu biçimi | Her bulguda Tür, Etiket, Alan, Bugün, Tasarım v4'te (ya da Tarifi neydi), Dayanak satırları var |
| Tür kullanımı | Türler tanımlı dörtlüden; Yol 2'de `düzeltilecek` yok |
| Geçiş kuralı | `Bugün` ve `Tasarım v4'te` satırları "ne olunca ne olur" anlatıyor, "şu var" demiyor |
| Alan adları | Alanlar tanımlı on üçlüden; "Seçim barı ve toplu eylemler" kullanılmış |
| Ölü metin | Geri alınmış kararlardan (kart üstü mod şeridi, ikon rozetler, space-between, grup başlıkları) bulgu üretilmemiş |
| Kod dili | Çıktıda dosya adı, uç nokta, bileşen adı geçmiyor |
| Karar vermeme | Hiçbir bulguda "doğrusu şu olmalı" demiyor |
| Kapsam | Hem `davranış` hem `görsel` etiketli bulgular var |
| Dil | Türkçe |

Bir dosya ölçütü tutturamıyorsa o yolu yeniden koşturma — eksik ölçütü ajana `SendMessage` ile
bildir; bağlamı yerinde durduğu için düzeltmesi ucuzdur.

- [ ] **Adım 7: Kabul denetimi — Yol 2'nin körlüğü**

Yol 2'nin çağrı kaydına bak. `HANDOFF.md`, `EKRAN-NOTLARI.md`, `DEGISIKLIK-GUNLUGU.md` ya da
`CLAUDE.md` çektiyse **o yolun çıktısı geçersizdir**; dosyasını sil, ajanı sıfırdan yeniden koş,
yasağı görev metninde bir kez daha vurgula. Bu denetim atlanamaz — üç yollu yöntemin tek kırılgan
noktası burasıdır.

- [ ] **Adım 8: Kabul denetimi — Yol 1'in körlüğü ve kapsam dışı kaynaklar**

Yol 1'in çağrı kaydında wireframe zincirinden (`Queen Editor Basit v4.html`, `simple-app-v4.jsx`,
`simple-screens-v4.jsx`, `export-designs-v4.jsx`, `wireframe-kit.jsx`, `tweaks-panel.jsx`,
`design-canvas.jsx`, `styles.css`) bir dosya varsa aynı işlem: çıktı geçersiz, yol yeniden koşar.

Üç yolun kaydında da `screenshots/`, `direction-e.jsx` ya da eski sürüm zincirleri çekilmiş mi diye
bak; çekilmişse o kaynaktan çıkan bulgular düşer.

- [ ] **Adım 9: Kabul denetimi — körlük, öteki yön**

Üç ajanın da çağrı kaydında `2026-08-20-v4-ara/` altındaki **başka** bir dosyayı okuma girişimi var
mı? Varsa o yolun çıktısı kirlenmiştir; hangi noktadan sonra yazdığını tespit et ve o kısmı at.

- [ ] **Adım 10: Kullanıcıya ara durum bildir**

Dört dosyanın yolunu kullanıcıya ver, okumak isterse okusun. Bu adımda **commit yok** — ara klasör
commit edilmez.

---

## Görev 2: Çakıştırma ve güven derecelendirmesi

**Çıktı:** tek birleşik fark tablosu; her satırda hangi yolların gördüğü ve güven damgası.

**Arayüz:**
- Tüketir: Görev 1'in üç fark dosyası (`yol-1-anlati.md`, `yol-2-tasarim-kaynagi.md`,
  `yol-3-ters-yon.md`).
- Üretir: birleşik tablo — satır başına `başlık · tür · etiket · alan · bugün · tasarım v4'te ·
  Y1 · Y2 · Y3 · damga`.

Bu görevi **ana oturum yapar, alt-ajan değil.** Üç listeyi birden gören tek yer burasıdır; bir
alt-ajana verilirse körlük düzeninin anlamı kalmaz.

- [ ] **Adım 1: Normalize et**

Aynı farkın üç farklı cümlesini tek satıra indir. Birleştirme kararı **elle** verilir; otomatik
başlık eşlemesi farklı iki bulguyu tek satıra ezer. İki bulgunun aynı olup olmadığına karar verirken
ölçüt `Bugün` ve `Tasarım v4'te` satırlarının **aynı geçişi** anlatıp anlatmadığıdır — başlık
benzerliği değil.

Tür çakışırsa: aynı geçişi anlatan iki bulgudan biri `değişecek`, öteki `düzeltilecek` diyorsa bu
bir birleştirme değil, **çelişkidir** (Adım 3).

- [ ] **Adım 2: Damgala**

| Kaç yol gördü | Damga | Ne yapılır |
|---|---|---|
| 3/3 | kesin | listeye girer |
| 2/3 | güçlü | listeye girer |
| 1/3 | zayıf sinyal | Görev 3'e devredilir |

Yol 2'nin `düzeltilecek` üretemediğini hesaba kat: bu türde tavan 2/3'tür, 2/3 damgası orada
"kesin"in karşılığıdır.

- [ ] **Adım 3: Çelişkileri ayır**

İki yol aynı konuda farklı şey söylüyorsa satır **çelişki** damgası alır ve **her iki ifade de**
yazılır. Hangisinin doğru olduğu söylenmez. Bu satırlar Görev 3'te elle doğrulanır.

- [ ] **Adım 4: `tasarım söylemiyor` notlu maddeleri ayır**

Bu notu taşıyan maddeler ana listeden çıkarılıp kendi listelerine alınır — belgenin 4. bölümünü
besleyecekler. `öksüz` türü ayrılmaz; spec tek düz liste diyor, öksüzler tür sütunuyla ana listede
durur.

- [ ] **Adım 5: Üç sayım tablosunu çıkar**

Belgenin künyesine girecek üç tablo burada hazırlanır:

1. **Yol × üretim** — her yolun ham bulgu sayısı, taradığı alanlar, atladığını söylediği yer.
   Kaynağı: ajanların kapanış raporları + dosyalardaki bulgu sayımı.
2. **Damga dağılımı** — kesin / güçlü / zayıf sinyal / çelişki sayıları.
3. **Tür × yol matrisi** — satırlar `eklenecek`, `değişecek`, `düzeltilecek`, `öksüz`; sütunlar
   Y1, Y2, Y3; hücrede o türü o yolun kaç kez yakaladığı.

- [ ] **Adım 6: Kabul denetimi**

| Kontrol | Kabul ölçütü |
|---|---|
| Kayıp yok | Giriş sayısı = birleşik tablodaki satır + birleştirmelerde eritilen tekrar + 4. bölüme ayrılanlar |
| Matris boşluğu | Yol 2'nin `görsel` etiketli bulgusu var; Yol 3'ün `öksüz` sütunu boş değil |

Matriste boş sütun görülürse o yol işini yapmamıştır: `SendMessage` ile eksik taramayı bildir ve o
sütunu doldurmasını iste.

Bu görevde commit yok.

---

## Görev 3: Zayıf sinyalleri ve çelişkileri elle doğrula

**Çıktı:** her zayıf sinyal için "doğrulandı" ya da "doğrulanamadı" kararı.

**Arayüz:**
- Tüketir: Görev 2'nin 1/3 damgalı satırları ve çelişki satırları.
- Üretir: aynı satırlar, `elle doğrulandı` ya da `doğrulanamadı` notuyla.

- [ ] **Adım 1: Her zayıf sinyali kaynağına kadar takip et**

Bulgunun `Dayanak` satırındaki kaynağa dön ve iddiayı doğrula. Tasarım tarafıysa DesignSync ile oku;
uygulama tarafıysa `queen-editor/` altında Read/Grep ile oku.

Zayıf sinyal **beklenen** bir sonuçtur, kusur değil: her yolun özel yakaladığı bir sınıf var
(Yol 1 gerekçeler, Yol 2 yazıya geçmemiş ayrıntılar, Yol 3 öksüzler), o sınıftaki bulguyu tek
başına görmesi normaldir.

- [ ] **Adım 2: Sonucu işle**

- Doğrulandıysa → ana listeye girer, yanına **"elle doğrulandı"** notu düşülür.
- Doğrulanamadıysa → **atılmaz**; listede `zayıf sinyal` damgasıyla durur. Sessizce silmek yöntemin
  amacını bozar.

- [ ] **Adım 3: Çelişkileri doğrula**

Çelişkili satırlarda **iki ifadeyi de** kaynağına kadar takip et. Amaç hangisinin doğru olduğuna
karar vermek değil — çelişkinin gerçek mi yoksa bir yolun okuma hatası mı olduğunu anlamak. Okuma
hatasıysa düzelt; gerçek çelişkiyse belgeye çelişki olarak girer, iki ifadeyle birlikte.

İki geçersizlik kuralı burada bir kez daha işletilir: çelişki `HANDOFF.md`'nin iki farklı
katmanından geliyorsa çelişki değildir (sonraki geçerli, önceki ölü); değişiklik günlüğündeki bir
ara aşamadan geliyorsa da çelişki değildir (son hâl geçerli).

- [ ] **Adım 4: Kabul denetimi**

Hiçbir zayıf sinyal "silindi" durumunda kalmamalı: her biri ya "elle doğrulandı" notuyla ya
`zayıf sinyal` damgasıyla listede.

Bu görevde commit yok.

---

## Görev 4: Brif çelişkisi bölümünü hazırla

**Çıktı:** belgenin 3. bölümünü besleyecek liste.

**Arayüz:**
- Tüketir: `yol-1-brif-celiskisi.md`; [arayüz brifi](../../2026-08-20-queen-editor-arayuz-brifi.md);
  [istek listesi](2026-08-20-queen-editor-istekler.md).
- Üretir: `brifin kararı · tasarımın yerine koyduğu · tasarımın gerekçesi` üçlüsünden oluşan liste.

- [ ] **Adım 1: Yol 1'in listesini doğrula**

Her madde için brife dön ve kararın gerçekten orada yazdığını gör. Brifte "karar sende" denen bir
konu **çelişki değildir** — tasarımcıya bırakılmış bir soruya tasarımın cevap vermesi beklenen
şeydir; o maddeleri listeden çıkar.

Çelişki sayılan tek şey: brifin **"Karar verildi"** dediği bir maddede tasarımın başka bir şey
yapmış olması.

- [ ] **Adım 2: Gerekçeleri kaynağına bağla**

Tasarımın gerekçesi `DEGISIKLIK-GUNLUGU.md`'de yazılıysa aynen aktarılır. Yazılmamışsa satır
"gerekçe yazılmamış" der; **gerekçe uydurulmaz.**

- [ ] **Adım 3: Kabul denetimi**

| Kontrol | Kabul ölçütü |
|---|---|
| Karar vermeme | Hiçbir satırda "brif haklıydı", "tasarım haklı", "doğrusu şu" geçmiyor |
| Kaynak | Her satırdaki brif kararı brifte gerçekten var |
| Kapsam | "Karar sende" maddeleri listede yok |

Bu görevde commit yok.

---

## Görev 5: Belgeyi yaz

**Çıktı:** `docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md`

**Dosyalar:**
- Oluştur: `docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md`

**Arayüz:**
- Tüketir: Görev 2, 3 ve 4'ün çıktıları.

- [ ] **Adım 1: 5 bölümü sırayla yaz**

| # | Bölüm | Kaynağı |
|---|---|---|
| 0 | Başlık notu | üçlü isim çakışması · iki geçersizlik kuralı · bugünkü tabanın durumu · yöntem ve üç sayım tablosu |
| 1 | Özet | tasarım v4 tek paragrafta ne getiriyor |
| 2 | **Fark listesi** | Görev 2'nin birleşik tablosu + Görev 3'ün notları |
| 3 | Brif ne dedi, tasarım ne yaptı | Görev 4'ün listesi |
| 4 | Tasarımın cevaplamadıkları | Görev 2 Adım 4'ün listesi |

- [ ] **Adım 2: 0. bölümün notunu tam yaz**

Dört bilgiyi taşımalı:
1. **Üçlü isim çakışması.** "v4" üç ayrı şeyin adı: tasarım v4, roadmap v4 (repodaki 8 Ağustos yol
   haritası, bitti), `feat/queen-editor-v4` (dal). Öncüllerdeki gibi bir roadmap eşlemesi **yok** —
   tasarım v4'ün repo karşılığı henüz yazılmadı.
2. **İki geçersizlik kuralı.** Katman kuralı (v3.5 > v3.4 > v3.3 > v3.2 > v3.1 > v3 > v2 > v1, üstü
   çizili ölü) ve geri alma kuralı (denenip vazgeçilen ara aşama bulgu üretmez).
3. **Bugünkü tabanın durumu.** Tasarım v3 karşılaştırmasından bu yana repo roadmap v5'ten v13'e
   ilerledi; 20 Ağustos istek listesinin hiçbir maddesi henüz uygulanmadı. Tarama tam kapsamlıdır.
4. **Yöntem ve üç sayım tablosu.** Görev 2 Adım 5'in çıktısı, üç yolun neye demirlendiğini anlatan
   kısa bir tabloyla birlikte.

- [ ] **Adım 3: 2. bölümü tek düz liste olarak yaz**

Numaralandırma **kesintisiz** tektir (1, 2, 3…); harf önekli kod yok. Alt başlıklar yalnız
okunabilirlik için alan alandır ve numarayı sıfırlamaz. Alan sırası:

Projeler · Proje ekranı ve panel şeridi · Fotoğraf üret · Video üret · Ses üret · Kuyruk ·
Üreticiler ve kurulum · Galeri · Seçim barı ve toplu eylemler · Detay sayfası · Export ekranı ·
Adlandırma ve kimlik · Uygulama geneli

Her madde: *ne · tür · davranış/görsel · bugün → tasarım v4'te · Y1/Y2/Y3 · damga*.

- [ ] **Adım 4: İki satır kuralını uygula**

Her maddede *bugün ne oluyor* → *tasarım v4'te ne olacak*. Geçiş cümlesi, duruş değil. Bugün
karşılığı yoksa ilk satır **"bugün yok"**.

- [ ] **Adım 5: `düzeltilecek` maddelerinin ayrımını koru**

Bu maddeler tasarım v4 farkı değildir; bugünkü uygulamanın kendi tarifinden sapmalarıdır. Tür sütunu
bunu zaten söylüyor, ama 2. bölümün başına bir cümle koy: "bugün yanlış" ile "tasarım v4'te
değişecek" farklı iki iddiadır ve tür sütunu onları ayırır.

- [ ] **Adım 6: 3. bölümü karar vermeden yaz**

Her madde üç satır: brifin kararı, tasarımın yerine koyduğu, tasarımın gerekçesi. Bölümün başına tek
cümle: bu maddeler repo ile tasarım arasındaki fark değildir — ikisinde de karşılığı yoktur; burada
durmalarının sebebi kullanıcının kendi verdiği kararların tasarımca geri alınmış olmasıdır.

---

## Görev 6: Belge öz-denetimi, teslim ve temizlik

- [ ] **Adım 1: Kod dili taraması**

Belgede dosya uzantısı (`.py`, `.jsx`, `.json`), yol ayracı (`/`), uç nokta (`/api/`), bileşen adı
ya da katman adı geçiyor mu? Geçiyorsa davranış cümlesine çevir.

İstisna: belgenin künyesi — kendi başlığındaki yol ve ilgili belgelere verdiği bağlantılar.

- [ ] **Adım 2: Karar taraması**

Belge hiçbir yerde "doğrusu şu", "şöyle olmalı", "tasarım kazanmalı" demiyor olmalı. 3. bölüm
özellikle denetlenir: orada karar vermek en kolay yer.

- [ ] **Adım 3: Bütünlük taraması**

Görev 1'in dört dosyasındaki her madde belgenin bir bölümünde karşılığını buluyor mu? Bulmuyorsa
kaybolmuş demektir — bul ve yerleştir.

- [ ] **Adım 4: Kapsam taraması**

Dört tür de (`eklenecek`, `değişecek`, `düzeltilecek`, `öksüz`) listede temsil ediliyor mu? Hiç
`görsel` etiketli madde yoksa görsel dil taranmamış demektir; geri dön.

- [ ] **Adım 5: Ölü metin taraması**

Belgede geri alınmış kararlardan üretilmiş madde var mı? Bilinen tuzaklar: kart üstündeki mod
şeridi, ikon rozetler (metin rozetler geçerli), detay panelinde space-between, grup başlıkları,
panelin altındaki prompt açıklama satırları, ses sekmesindeki üretim modu satırı. Bunlardan biri
"tasarım istiyor" diye yazılmışsa **çıkar**.

- [ ] **Adım 6: Kullanıcıya sun**

Belgeyi kullanıcıya bildir ve incelemesini iste. **Commit etme** — kullanıcı okuyup onaylamadan
commit yok.

- [ ] **Adım 7: Ara klasörü sil**

Kullanıcı belgeyi onayladıktan **sonra** `docs/superpowers/research/2026-08-20-v4-ara/` klasörünü
sil. Silmeden önce kullanıcıya sor — ham listeleri saklamak isteyebilir. Kendiliğinden silme.

- [ ] **Adım 8: Commit**

Yalnız çıktı belgesi ve plan commit edilir; ara klasör commit edilmez.

```
git add docs/superpowers/research/2026-08-20-queen-editor-tasarim-v4-farklari.md
git add docs/superpowers/plans/2026-08-20-queen-editor-tasarim-v4-fark-cikarma.md
git commit -m 'docs(queen-editor): tasarim v4 ile bugunku uygulamanin farklari'
```

Mesajda **çift tırnak yok** — PowerShell'de çift tırnak parantezle birleşince mesajı bölüyor ve git
parçaları pathspec sanıyor.
