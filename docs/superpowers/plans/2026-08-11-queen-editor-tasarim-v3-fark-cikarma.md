# Tasarım v3 Fark Çıkarma — Uygulama Planı

> **Ajanla çalışanlar için:** Bu plan görev görev uygulanır. Adımlar takip için kutucuk (`- [ ]`)
> biçimindedir. Kod üretmediği için TDD döngüsü yoktur; her görev bir **kabul denetimi** ile kapanır.

**Hedef:** claude.ai/design'daki "Queen Editor Basit v3" ile bugün çalışan uygulama arasındaki
farkları üç bağımsız yolla çıkarıp çakıştırmak ve tek bir Türkçe md'ye dökmek.

**Yaklaşım:** Üç alt-ajan, üç ayrı kaynağa demirleyerek aynı anda ve birbirini görmeden tam fark
listesi çıkarır; her biri bulgularını ilerledikçe repodaki kendi dosyasına yazar. Ana oturum üç
listeyi çakıştırır, güven damgası atar, zayıf sinyalleri elle doğrular ve belgeyi yazar. Hiçbir görev
kod değiştirmez.

**Araçlar:** DesignSync (tasarım projesi, salt okunur) · Read/Grep (repo) · Agent (üç yol)

**Tasarım belgesi:**
[2026-08-11-queen-editor-tasarim-v3-fark-cikarma-design.md](../specs/2026-08-11-queen-editor-tasarim-v3-fark-cikarma-design.md)

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
- **İsim çakışması:** tasarımın "Basit v3"ü repodaki **roadmap v5**'e karşılık gelir. Her yerde
  "tasarım v3" ve "roadmap v5" diye tam yazılır; yalın "v3" kullanılmaz.
- **Öncelik kuralı:** `HANDOFF.md` üst üste binmiş katmanlardan oluşur. Geçerlilik sırası
  **v3.2 > v3.1 > v3 > v2 > v1**. Üstü çizili (`~~…~~`) metin **ölüdür**, bulgu üretmez.
- **Terminoloji tasarımdan alınır:** **kare** = içerik birimi (foto + video + ses), **fotoğraf** =
  yalnız foto katmanı.
- **Dil:** her ara çıktı ve nihai belge Türkçe.
- **Tasarım projesi:** `efad1f83-69d3-4e07-89fa-3783839c81c3` ("Queen Editor").
- **Bugünkü uygulama:** `queen-editor/` — arayüz `queen-editor/frontend/src/`, davranış kuralları
  `queen-editor/backend/`.
- **Kapsam dışı kaynaklar:** `screenshots/` ve `direction-e.jsx`. v3 giriş noktası `direction-e`'yi
  zincirlemiyor; ayrı bir görsel yön çalışmasıdır.

## Bulgu biçimi

Üç yol da bulgularını **aynı biçimde** yazar; çakıştırma buna dayanır.

```
### <kısa başlık>
- **Tür:** eklenecek | değişecek | düzeltilecek | öksüz
- **Etiket:** davranış | görsel
- **Alan:** Projeler | Proje ekranı ve panel şeridi | Fotoğraf üret | Video üret | Ses üret |
            Kuyruk | Üreticiler ve kurulum | Galeri | Detay sayfası | Export ekranı |
            Adlandırma ve kimlik | Uygulama geneli
- **Bugün:** <tek cümle — bugünkü uygulamada ne olunca ne oluyor>
- **Tasarım v3'te:** <tek cümle — ne olunca ne olacak>
- **Not:** (varsa) tasarım söylemiyor
- **Dayanak:** <bu bulguyu nereden çıkardın — kaynağın adı, tek cümle>
```

Tür seçimi:

| Tür | Ne zaman |
|---|---|
| `eklenecek` | bugün hiç karşılığı yok |
| `değişecek` | karşılığı var, farklı |
| `düzeltilecek` | bugün **kendi tarifine göre** zaten yanlış |
| `öksüz` | bugün var, tasarım v3'te karşılığı yok |

Biçim kuralları:

- `Bugün` ve `Tasarım v3'te` satırları **geçiş** anlatır, duruş değil. "Duraklat butonu var"
  yanlıştır; "Duraklat'a basınca çalışan kare bitirilir, arada *Duraklatılıyor…* görünür, sonra
  bekleyen sayısı 7'den 8'e çıkar" doğrudur.
- Bugün hiç karşılığı yoksa `Bugün` satırı tam olarak **"bugün yok"**tur; uydurulmuş karşılık
  aranmaz.
- `düzeltilecek` türünde `Tasarım v3'te` satırı yerine **`Tarifi neydi:`** yazılır — bu bir v3 farkı
  değil, bugünün kendi tarifinden (tasarım v2) sapmasıdır.
- `öksüz` türünde `Tasarım v3'te` satırı **"karşılığı yok"**tur. Bilerek mi kaldırıldı, tasarım mı
  atladı — **karar verilmez**, yalnız işaretlenir.
- Tasarımın cevaplamadığı bir konu `Not: tasarım söylemiyor` alır; uydurulmaz.

## Dosya yapısı

| Dosya | Sorumluluğu |
|---|---|
| `docs/superpowers/research/2026-08-11-v3-ara/yol-1-anlati.md` | Yol 1'in ham bulgu listesi. Ajan **ilerledikçe** yazar |
| `docs/superpowers/research/2026-08-11-v3-ara/yol-2-tasarim-kaynagi.md` | Yol 2'nin ham bulgu listesi |
| `docs/superpowers/research/2026-08-11-v3-ara/yol-3-ters-yon.md` | Yol 3'ün ham bulgu listesi |
| `docs/superpowers/research/2026-08-11-queen-editor-tasarim-v3-farklari.md` | **Tek çıktı.** 5 bölümlük fark belgesi (Görev 5'te oluşturulur) |

Başka dosya oluşturulmaz veya değiştirilmez.

**Ara klasörün ömrü:** `2026-08-11-v3-ara/` commit **edilmez**. Kullanıcı çakıştırmadan önce ham
listeleri okuyabilsin diye repoda durur; Görev 6'da, kullanıcı onayıyla silinir.

---

## Görev 1: Üç yolu aynı anda koş

**Çıktı:** birbirini görmemiş üç tam fark listesi, üç ayrı dosyada.

**Arayüz:**
- Üretir: `yol-1-anlati.md`, `yol-2-tasarim-kaynagi.md`, `yol-3-ters-yon.md` — hepsi yukarıdaki
  **Bulgu biçimi**nde.
- Her ajan ayrıca kısa bir **kapanış raporu** döndürür: kaç bulgu yazdı, hangi alanları taradı,
  atladığı/emin olamadığı yer kaldı mı. Bulgular dönüş değerinde değil, dosyadadır.

- [ ] **Adım 1: Ara klasörü aç**

`docs/superpowers/research/2026-08-11-v3-ara/` klasörünü oluştur. Üç ajan da kendi dosyasını bu
klasöre yazacak; klasör yoksa ilk yazma çağrısı ajanı boşa düşürür.

- [ ] **Adım 2: Yol 1'in görev metnini hazırla**

Yol 1 DesignSync'i **hiç çağırmaz**; okuyacağı iki yazılı belgeyi görev metninin içinde hazır bulur.
Bu iki belgenin tam metni (`HANDOFF.md` ve tasarım projesinin `CLAUDE.md`'si) DesignSync ile o an
çekilip prompt'a yapıştırılır. **Metinleri bu plana yazma** — global kısıt tasarım dosyalarının
repoya kaydedilmesini yasaklıyor ve plan repoda duruyor.

Görev metni şu gövdeyi kullanır:

```
Sen "Yol 1 · Anlatı" yolusun. Görevin: aşağıda tam metni verilen iki tasarım belgesindeki her
yazılı kararı tek tek alıp, bugün çalışan uygulamada karşılığını bulmak ve fark varsa yazmak.

KAYNAĞIN — yalnız bunlar:
1. Aşağıda verilen HANDOFF.md tam metni.
2. Aşağıda verilen tasarım CLAUDE.md tam metni.
3. Bugünkü uygulamanın kaynağı: queen-editor/frontend/src/ (arayüz) ve queen-editor/backend/
   (davranış kuralları). Read ve Grep ile oku.

YASAK: DesignSync aracını çağırma. Wireframe kaynağına (simple-screens-v3.jsx, simple-app-v3.jsx,
export-designs-v3.jsx, styles.css vb.) erişmeye çalışma. Senin değerin yalnız yazılı kararlardan
yürümenden geliyor.

ÖNCELİK KURALI — bu kural olmadan geçersiz kılınmış kuralları bulgu diye yazarsın:
HANDOFF.md üst üste binmiş katmanlardan oluşuyor. Geçerlilik sırası v3.2 > v3.1 > v3 > v2 > v1.
Sonraki bölüm önceki bölümle çeliştiğinde sonraki geçerlidir. Üstü çizili (~~…~~) metin ÖLÜDÜR;
ondan bulgu üretme.

YÜRÜYÜŞ:
- HANDOFF.md'nin v3, v3.1 ve v3.2 bölümlerindeki her kararı tek tek al.
- Şu bölümleri de tara, atlama:
  · "Kural olarak yazılanlar (ekran çizilmedi)" — ekranda görünmeyen ama bağlayıcı kararlar.
  · "Değişmeyenler" — tasarım "değişmedi" diyor olabilir ama uygulama oradan sapmış olabilir;
    o zaman bulgu "değişecek" değil, "düzeltilecek" türündedir.
  · "Karara bağlananlar".
  · "Görsel dil" — renk rolleri, tipografi, etiket biçimi, ölçü.
- Her karar için bugünkü uygulamaya bak, ne yaptığını öğren, farkı yaz.
- Tasarım CLAUDE.md'sindeki yıkıcı eylem butonu standardını da bir karar say.

KAPSAM: davranış VE görsel. Renk, boşluk, tipografi, ikon, ölçü dahil. Her bulguya "davranış" ya da
"görsel" etiketi koy.

TERMİNOLOJİ — tasarımın kendi sözcükleri: "kare" = içerik birimi (foto + video + ses),
"fotoğraf" = yalnız foto katmanı. İkisini karıştırma.

<bulgu biçimi bloğu buraya aynen kopyalanır — tür tablosu ve biçim kuralları dahil>

NEREYE YAZACAKSIN — en önemli kural:
Bulgularını docs/superpowers/research/2026-08-11-v3-ara/yol-1-anlati.md dosyasına, İLERLEDİKÇE
yaz. Sonda toplu yazma: yarıda kesilirsen emeğin tümüyle gider. Her birkaç bulguda bir dosyayı
güncelle.
Bu klasördeki diğer dosyaları (yol-2-*.md, yol-3-*.md) AÇMA ve OKUMA. Onlar öteki iki yolun
listesi; okursan körlük bozulur ve üç yollu yöntemin anlamı kalmaz.
Dönüş değerin bulgu listesi DEĞİL, kısa bir kapanış raporudur: kaç bulgu yazdın, hangi alanları
taradın, atladığın ya da emin olamadığın yer kaldı mı.

KURALLAR:
- Bulgular geçiş anlatır, duruş değil.
- Çıktında kod dili geçmesin: dosya adı, uç nokta, bileşen adı, katman adı yok. Kaynağı okursun ama
  yazdığın şey kullanıcının gördüğü davranıştır.
- Karar verme. Çelişki görürsen iki ifadeyi de yaz, hangisinin doğru olduğunu söyleme.
- Tasarımın cevaplamadığı bir şeye rastlarsan "tasarım söylemiyor" notu koy. Uydurma, tahmin etme.
- Tasarımın "Basit v3"ü repodaki roadmap v5'e karşılık gelir; ikisini de tam adıyla yaz, yalın "v3"
  kullanma.
- Türkçe yaz.

--- HANDOFF.md TAM METNİ ---
<buraya yapıştırılır>

--- TASARIM CLAUDE.md TAM METNİ ---
<buraya yapıştırılır>
```

- [ ] **Adım 3: Yol 2'nin görev metnini hazırla**

```
Sen "Yol 2 · Tasarım kaynağı" yolusun. Görevin: tasarım v3 wireframe'inin kendisinden envanter
çıkarıp bugünkü uygulamanın envanteriyle karşılaştırmak.

ARAÇ: DesignSync. Şemasını yüklemek için önce ToolSearch'ü "select:DesignSync" sorgusuyla çağır.
Proje: efad1f83-69d3-4e07-89fa-3783839c81c3

ÇEKECEĞİN DOSYALAR — yalnız bunlar:
  Queen Editor Basit v3.html, simple-app-v3.jsx, simple-screens-v3.jsx, export-designs-v3.jsx,
  wireframe-kit.jsx, tweaks-panel.jsx, design-canvas.jsx, styles.css

KESİN YASAK: HANDOFF.md ve CLAUDE.md dosyalarını ÇEKME. Bu yolun tüm değeri, tasarımın yazılı
anlatısını hiç görmemiş olmandan geliyor — anlatıyı okursan Yol 1'in kopyası olursun ve çıktın
geçersiz sayılır. Çağrıların kayda geçiyor; ihlal görünür.
screenshots/ klasörünü ve direction-e.jsx dosyasını da çekme; başka bir tasarım yönüne aitler.
Ayrıca yazma çağrısı yapma: finalize_plan, write_files, delete_files, register_assets yok.
Çektiğin tasarım içeriğini hiçbir dosyaya kaydetme — dosyaya yalnız BULGU yazılır.

YÜRÜYÜŞ:
1. v3 wireframe'inden envanter çıkar: hangi ekran, hangi bölge, hangi kontrol, hangi durum,
   durumlar arası hangi geçiş, hangi metin, hangi boş hâl, hangi renk/boşluk/ikon.
   Wireframe React kaynağıdır; durum makinesi orada yazılıdır — oku ve geçişi anlat.
2. Aynı envanteri bugünkü uygulamadan çıkar: queen-editor/frontend/src/ (arayüz) ve
   queen-editor/backend/ (davranış kuralları). Read ve Grep ile oku.
3. İki envanteri satır satır karşılaştır. Her farkı yaz.

BU YOLUN ÖZEL YAKALADIĞI ŞEY: yazıya hiç geçmemiş olanlar — buton etiketlerinin tam metni, ara
durumlar, boş hâller, hata hâlleri, sayaçların biçimi. Bunları özellikle ara.

KAPSAM: davranış VE görsel. Renk, boşluk, tipografi, ikon, ölçü dahil. Her bulguya "davranış" ya da
"görsel" etiketi koy.

TERMİNOLOJİ — tasarımın kendi sözcükleri: "kare" = içerik birimi (foto + video + ses),
"fotoğraf" = yalnız foto katmanı. İkisini karıştırma.

<bulgu biçimi bloğu buraya aynen kopyalanır — tür tablosu ve biçim kuralları dahil>

NOT: "düzeltilecek" türünü sen kullanamazsın — o tür bugünkü uygulamanın kendi tarifinden (tasarım
v2) sapmasını gösterir, sen ise v2'yi hiç görmüyorsun. Senin türlerin: eklenecek, değişecek, öksüz.

NEREYE YAZACAKSIN — en önemli kural:
Bulgularını docs/superpowers/research/2026-08-11-v3-ara/yol-2-tasarim-kaynagi.md dosyasına,
İLERLEDİKÇE yaz. Sonda toplu yazma: yarıda kesilirsen emeğin tümüyle gider.
Bu klasördeki diğer dosyaları (yol-1-*.md, yol-3-*.md) AÇMA ve OKUMA.
Dönüş değerin bulgu listesi DEĞİL, kısa bir kapanış raporudur: kaç bulgu yazdın, hangi ekranları
taradın, atladığın ya da emin olamadığın yer kaldı mı.

KURALLAR:
- Bulgular geçiş anlatır, duruş değil.
- Çıktında kod dili geçmesin: dosya adı, uç nokta, bileşen adı, katman adı yok.
- Karar verme. Çelişki görürsen iki ifadeyi de yaz.
- Tasarımın "Basit v3"ü repodaki roadmap v5'e karşılık gelir; ikisini de tam adıyla yaz.
- Türkçe yaz.
```

- [ ] **Adım 4: Yol 3'ün görev metnini hazırla**

```
Sen "Yol 3 · Ters yön" yolusun. Diğer iki yol tasarımdan uygulamaya yürüyor; sen ters yönden,
uygulamadan tasarıma yürüyeceksin. Bu turda en değerli yol sensin: bugünkü uygulama kabaca tasarım
v2'nin karşılığı, dolayısıyla senin "karşılığı var ama farklı" kovan doğrudan v2'den v3'e neyin
değiştiğini veriyor.

ARAÇ: DesignSync. Şemasını yüklemek için önce ToolSearch'ü "select:DesignSync" sorgusuyla çağır.
Proje: efad1f83-69d3-4e07-89fa-3783839c81c3
Tasarım tarafının tamamı sana serbest: HANDOFF.md, CLAUDE.md, v3 wireframe zinciri, v2 karşılıkları.
Tek istisna: screenshots/ klasörü ve direction-e.jsx kaynak değildir — başka bir tasarım yönüne
aitler, çekme.
Yazma çağrısı yapma (finalize_plan, write_files, delete_files, register_assets). Çektiğin tasarım
içeriğini hiçbir dosyaya kaydetme — dosyaya yalnız BULGU yazılır.

ÖNCELİK KURALI: HANDOFF.md üst üste binmiş katmanlardan oluşuyor. Geçerlilik sırası
v3.2 > v3.1 > v3 > v2 > v1. Üstü çizili (~~…~~) metin ÖLÜDÜR; ondan bulgu üretme.

YÜRÜYÜŞ — iki ayrı işin var:

İŞ A — fark çıkarma:
1. Bugünkü uygulamanın davranış envanterini çıkar: her ekran, her bölge, her kontrol, her durum,
   her geçiş, her metin, her görsel kural. Kaynak: queen-editor/frontend/src/ ve
   queen-editor/backend/.
2. Envanterdeki her maddeyi tasarım v3'te ara ve üç kovadan birine at:
   · Karşılığı var, aynı  → değişmiyor, YAZMA.
   · Karşılığı var, farklı → "değişecek" türüyle yaz.
   · Karşılığı YOK        → "öksüz" türüyle yaz. Ya tasarım v3'te bilerek kaldırıldı, ya tasarım
                            atladı. HANGİSİ OLDUĞUNA KARAR VERME, sadece işaretle.
3. Kapanış taraması: envanterin bugünden başladığı için, tasarım v3'te tamamen yeni olup uygulamada
   hiç tutamağı olmayan bir şeyi kaçırmış olabilirsin. Sonda tek bir tarama yap: "tasarım v3'te
   dokunulmuş olup envanterimde hiç görünmeyen bir yer kaldı mı?" Bulduğunu "eklenecek" türüyle
   ekle.

İŞ B — sadakat denetimi:
Envanterdeki her madde için ikinci bir soru sor: "uygulama BUGÜN hedeflediği tarifi tutturmuş mu?"
Bu sorunun tabanı tasarım v3 DEĞİL, tasarım v2'dir — uygulama v2'yi hedefleyerek yazıldı. Bu soruyu
tasarım v3'ün dokunmadığı yerlerde de sor; tüm uygulama denetlenir.
Uygulama kendi tarifini tutturamamışsa bu bir v3 farkı DEĞİL, bir hatadır: "düzeltilecek" türüyle
yaz ve "Tasarım v3'te" satırı yerine "Tarifi neydi:" yaz.

İŞ A ile İŞ B'nin bulguları AYNI dosyaya, aynı biçimde girer — türleri ("değişecek"/"öksüz" ile
"düzeltilecek") onları zaten ayırıyor. Ama iki iddiayı tek bulguda birleştirme: "bugün yanlış" ile
"v3'te değişecek" farklı iki şeydir, ayrı bulgular olur.

UYARI — bugünkü tabanın durumu: uygulamanın son turu (roadmap v4) yalnız yüzeysel denendi. Yani
"düzeltilecek" bulgularında "kod yanlış" ile "kod doğru ama çalışırken patlıyor" ayrımını YAPAMAZSIN.
Kaynağın ne dediğini yaz, çalışma zamanı hakkında tahmin yürütme.

KAPSAM: davranış VE görsel. Renk, boşluk, tipografi, ikon, ölçü dahil. Her bulguya "davranış" ya da
"görsel" etiketi koy.

TERMİNOLOJİ — tasarımın kendi sözcükleri: "kare" = içerik birimi (foto + video + ses),
"fotoğraf" = yalnız foto katmanı. İkisini karıştırma.

<bulgu biçimi bloğu buraya aynen kopyalanır — tür tablosu ve biçim kuralları dahil>

NEREYE YAZACAKSIN — en önemli kural:
Bulgularını docs/superpowers/research/2026-08-11-v3-ara/yol-3-ters-yon.md dosyasına, İLERLEDİKÇE
yaz. Sonda toplu yazma: yarıda kesilirsen emeğin tümüyle gider.
Bu klasördeki diğer dosyaları (yol-1-*.md, yol-2-*.md) AÇMA ve OKUMA.
Dönüş değerin bulgu listesi DEĞİL, kısa bir kapanış raporudur: kaç bulgu yazdın, hangi ekranları
taradın, İŞ A ve İŞ B'den kaçar bulgu çıktı, atladığın yer kaldı mı.

KURALLAR:
- Bulgular geçiş anlatır, duruş değil.
- Çıktında kod dili geçmesin: dosya adı, uç nokta, bileşen adı, katman adı yok.
- Karar verme. Çelişki görürsen iki ifadeyi de yaz.
- Tasarımın cevaplamadığı bir şeye rastlarsan "tasarım söylemiyor" notu koy.
- Tasarımın "Basit v3"ü repodaki roadmap v5'e karşılık gelir; ikisini de tam adıyla yaz.
- Türkçe yaz.
```

- [ ] **Adım 5: Üçünü tek mesajda gönder**

Üç `Agent` çağrısı **aynı mesajda** yapılır ki paralel koşsunlar. Hepsi `general-purpose` tipinde.
Etiketler: `yol-1-anlati`, `yol-2-tasarim-kaynagi`, `yol-3-ters-yon`.

Beklerken **hiçbir şey yapma** — üç listeyi görmeden çakıştırmaya başlanamaz.

- [ ] **Adım 6: Kabul denetimi — biçim**

Her üç dosya için ayrı ayrı kontrol et:

| Kontrol | Kabul ölçütü |
|---|---|
| Dosya var mı | Üç dosya da yazılmış, boş değil |
| Bulgu biçimi | Her bulguda Tür, Etiket, Alan, Bugün, Tasarım v3'te (ya da Tarifi neydi), Dayanak satırları var |
| Tür kullanımı | Türler tanımlı dörtlüden; Yol 2'de `düzeltilecek` yok |
| Geçiş kuralı | `Bugün` ve `Tasarım v3'te` satırları "ne olunca ne olur" anlatıyor, "şu var" demiyor |
| Kod dili | Çıktıda dosya adı, uç nokta, bileşen adı geçmiyor |
| Karar vermeme | Hiçbir bulguda "doğrusu şu olmalı" demiyor |
| Kapsam | Hem `davranış` hem `görsel` etiketli bulgular var |
| Dil | Türkçe |

Bir dosya ölçütü tutturamıyorsa o yolu yeniden koşturma — eksik ölçütü ajana `SendMessage` ile
bildir; bağlamı yerinde durduğu için düzeltmesi ucuzdur.

- [ ] **Adım 7: Kabul denetimi — Yol 2'nin körlüğü**

Yol 2'nin çağrı kaydına bak. `HANDOFF.md` ya da `CLAUDE.md` çektiyse **o yolun çıktısı geçersizdir**;
dosyasını sil, ajanı sıfırdan yeniden koş, yasağı görev metninde bir kez daha vurgula. Bu denetim
atlanamaz — üç yollu yöntemin tek kırılgan noktası burasıdır.

Aynı kayıtta `screenshots/` ve `direction-e.jsx` çekilmiş mi diye de bak; çekilmişse o bulgular
kaynağı kapsam dışı olduğu için düşer.

- [ ] **Adım 8: Kabul denetimi — körlük, öteki yön**

Üç ajanın da çağrı kaydında `2026-08-11-v3-ara/` altındaki **başka** bir dosyayı okuma girişimi var
mı? Varsa o yolun çıktısı kirlenmiştir; hangi noktadan sonra yazdığını tespit et ve o kısmı at.

- [ ] **Adım 9: Kullanıcıya ara durum bildir**

Üç dosyanın yolunu kullanıcıya ver, okumak isterse okusun. Ham listeler repoda durduğu için
çakıştırmadan önce bakabilir. Bu adımda **commit yok** — ara klasör commit edilmez.

---

## Görev 2: Çakıştırma ve güven derecelendirmesi

**Çıktı:** tek birleşik fark tablosu; her satırda hangi yolların gördüğü ve güven damgası.

**Arayüz:**
- Tüketir: Görev 1'in üç dosyası.
- Üretir: birleşik tablo — satır başına `başlık · tür · etiket · alan · bugün · tasarım v3'te ·
  Y1 · Y2 · Y3 · damga`.

Bu görevi **ana oturum yapar, alt-ajan değil.** Üç listeyi birden gören tek yer burasıdır; bir
alt-ajana verilirse körlük düzeninin anlamı kalmaz.

- [ ] **Adım 1: Normalize et**

Aynı farkın üç farklı cümlesini tek satıra indir. Birleştirme kararı **elle** verilir; otomatik
başlık eşlemesi farklı iki bulguyu tek satıra ezer. İki bulgunun aynı olup olmadığına karar verirken
ölçüt `Bugün` ve `Tasarım v3'te` satırlarının **aynı geçişi** anlatıp anlatmadığıdır — başlık
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

- [ ] **Adım 5: Kabul denetimi**

Üç listenin hiçbir maddesi kaybolmamış olmalı. Giriş sayısı = birleşik tablodaki satır sayısı +
birleştirmelerde eritilen tekrar sayısı + 4. bölüme ayrılanlar. Sayı tutmuyorsa kaybolan maddeyi
bul.

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

Öncelik kuralı burada bir kez daha işletilir: çelişki `HANDOFF.md`'nin iki farklı katmanından
geliyorsa çelişki değildir — v3.2 > v3.1 > v3 > v2 > v1 sırasıyla sonraki geçerlidir, önceki ölüdür.

- [ ] **Adım 4: Kabul denetimi**

Hiçbir zayıf sinyal "silindi" durumunda kalmamalı: her biri ya "elle doğrulandı" notuyla ya
`zayıf sinyal` damgasıyla listede.

Bu görevde commit yok.

---

## Görev 4: queen-tools çarpışması

**Çıktı:** belgenin 3. bölümünü besleyecek çarpışma tablosu.

**Arayüz:**
- Tüketir: Görev 3 sonrası birleşik liste; `collab-toolbox/queen-tools/`;
  `docs/superpowers/specs/2026-08-09-queen-tools-design.md`.
- Üretir: `konu · queen-tools bugün neye dayanıyor · tasarım v3 ne getiriyor` tablosu.

`queen-tools`, Queen Editor'ın Export dosyasını okuyan ayrı bir zincirdir. Tasarım v3 Export'a
dokunduğu ve video üretimini uygulamanın içine aldığı için bu zincir kırılabilir; belge bunu
işaretler, **karar vermez**.

- [ ] **Adım 1: queen-tools'un Queen Editor'dan ne beklediğini çıkar**

Oku: `collab-toolbox/queen-tools/prompt_converter.ipynb`, `collab-toolbox/queen-tools/photo_to_video.ipynb`
ve `docs/superpowers/specs/2026-08-09-queen-tools-design.md`. Sorular: Export dosyasının hangi
alanlarını okuyor, hangi sırayı bekliyor, hangi adı bekliyor.

- [ ] **Adım 2: Birleşik listenin Export ve video maddeleriyle karşılaştır**

Bilinen adaylar — ama tarama bunlarla sınırlı değil:

| Konu | Bakılacak |
|---|---|
| Export biçimi | tasarım v3.2 JSON export'u kaldırıyor; `prompt_converter` onu okuyor |
| Video üretimi | tasarım v3 videoyu uygulamanın içine alıyor; `photo_to_video` aynı işi dışarıda yapıyor |
| Adlandırma | tasarım v3'ün yeni adları (kare/fotoğraf) queen-tools'un beklediği adlarla tutuyor mu |

- [ ] **Adım 3: Kabul denetimi**

Tabloda hiçbir satırda "doğrusu şu", "queen-tools güncellenmeli" cümlesi olmamalı. Bu bölüm yalnız
iki tarafın ne beklediğini yan yana koyar.

Bu görevde commit yok.

---

## Görev 5: Belgeyi yaz

**Çıktı:** `docs/superpowers/research/2026-08-11-queen-editor-tasarim-v3-farklari.md`

**Dosyalar:**
- Oluştur: `docs/superpowers/research/2026-08-11-queen-editor-tasarim-v3-farklari.md`

**Arayüz:**
- Tüketir: Görev 2, 3 ve 4'ün çıktıları.

- [ ] **Adım 1: 5 bölümü sırayla yaz**

| # | Bölüm | Kaynağı |
|---|---|---|
| 0 | Başlık notu | isim çakışması · öncelik kuralı · bugünkü tabanın durumu |
| 1 | Özet | tasarım v3 tek paragrafta ne getiriyor |
| 2 | **Fark listesi** | Görev 2'nin birleşik tablosu + Görev 3'ün notları |
| 3 | queen-tools çarpışması | Görev 4'ün tablosu |
| 4 | Tasarımın cevaplamadıkları | Görev 2 Adım 4'ün listesi + AI agent panelinin hâlâ boş oluşu |

- [ ] **Adım 2: 0. bölümün notunu tam yaz**

Üç bilgiyi taşımalı:
1. Tasarım projesinin "Basit v3" sürümü, repodaki **roadmap v5**'e karşılık gelir; repodaki spec
   numaralarıyla karıştırılmamalı. (Tasarım v2 = roadmap v4 idi.)
2. Öncelik kuralı: v3.2 > v3.1 > v3 > v2 > v1; üstü çizili metin ölüdür.
3. Bugünkü taban: roadmap v4'ün Madde 1-11'i uygulandı ve push edildi; Madde 12 (Colab turu)
   yüzeysel koşuldu. Yani `düzeltilecek` tipli maddelerde "kod yanlış" ile "kod doğru, çalışırken
   patlıyor" ayrımı yapılamaz.

- [ ] **Adım 3: 2. bölümü tek düz liste olarak yaz**

Numaralandırma **kesintisiz** tektir (1, 2, 3…); harf önekli kod yok. Alt başlıklar yalnız
okunabilirlik için alan alandır ve numarayı sıfırlamaz. Alan sırası:

Projeler · Proje ekranı ve panel şeridi · Fotoğraf üret · Video üret · Ses üret · Kuyruk ·
Üreticiler ve kurulum · Galeri · Detay sayfası · Export ekranı · Adlandırma ve kimlik ·
Uygulama geneli

Her madde: *ne · tür · davranış/görsel · bugün → tasarım v3'te · Y1/Y2/Y3 · damga*.

- [ ] **Adım 4: İki satır kuralını uygula**

Her maddede *bugün ne oluyor* → *tasarım v3'te ne olacak*. Geçiş cümlesi, duruş değil. Bugün
karşılığı yoksa ilk satır **"bugün yok"**.

- [ ] **Adım 5: `düzeltilecek` maddelerinin ayrımını koru**

Bu maddeler v3 farkı değildir; bugünkü uygulamanın kendi tarifinden sapmalarıdır. Tür sütunu bunu
zaten söylüyor, ama 2. bölümün başına bir cümle koy: "bugün yanlış" ile "v3'te değişecek" farklı iki
iddiadır ve tür sütunu onları ayırır.

---

## Görev 6: Belge öz-denetimi, teslim ve temizlik

- [ ] **Adım 1: Kod dili taraması**

Belgede dosya uzantısı (`.py`, `.jsx`, `.json`), yol ayracı (`/`), uç nokta (`/api/`), bileşen adı
ya da katman adı geçiyor mu? Geçiyorsa davranış cümlesine çevir.

İstisna: belgenin künyesi — kendi başlığındaki yol ve ilgili belgelere verdiği bağlantılar. Bir de
3. bölüm: queen-tools çarpışması iki aracın adını anmak zorunda, araç adları kod dili sayılmaz.

- [ ] **Adım 2: Karar taraması**

Belge hiçbir yerde "doğrusu şu", "şöyle olmalı", "tasarım kazanmalı" demiyor olmalı. Diyorsa çıkar.

- [ ] **Adım 3: Bütünlük taraması**

Görev 1'in üç dosyasındaki her madde belgenin bir bölümünde karşılığını buluyor mu? Bulmuyorsa
kaybolmuş demektir — bul ve yerleştir.

- [ ] **Adım 4: Kapsam taraması**

Dört tür de (`eklenecek`, `değişecek`, `düzeltilecek`, `öksüz`) listede temsil ediliyor mu? Hiç
`görsel` etiketli madde yoksa görsel dil taranmamış demektir; geri dön.

- [ ] **Adım 5: Kullanıcıya sun**

Belgeyi kullanıcıya bildir ve incelemesini iste. **Commit etme** — kullanıcı okuyup onaylamadan
commit yok.

- [ ] **Adım 6: Ara klasörü sil**

Kullanıcı belgeyi onayladıktan **sonra** `docs/superpowers/research/2026-08-11-v3-ara/` klasörünü
sil. Silmeden önce kullanıcıya sor — ham listeleri saklamak isteyebilir. Kendiliğinden silme.

- [ ] **Adım 7: Commit**

Yalnız çıktı belgesi commit edilir; ara klasör commit edilmez.

```
git add docs/superpowers/research/2026-08-11-queen-editor-tasarim-v3-farklari.md
git add docs/superpowers/specs/2026-08-11-queen-editor-tasarim-v3-fark-cikarma-design.md
git add docs/superpowers/plans/2026-08-11-queen-editor-tasarim-v3-fark-cikarma.md
git commit -m 'docs(queen-editor): tasarim v3 ile bugunku uygulamanin farklari'
```

Mesajda **çift tırnak yok** — PowerShell'de çift tırnak parantezle birleşince mesajı bölüyor ve git
parçaları pathspec sanıyor.
