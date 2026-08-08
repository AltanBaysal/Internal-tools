# Tasarım v2 Fark Çıkarma — Uygulama Planı

> **Ajanla çalışanlar için:** Bu plan görev görev uygulanır. Adımlar takip için kutucuk (`- [ ]`)
> biçimindedir. Kod üretmediği için TDD döngüsü yoktur; her görev bir **kabul denetimi** ile kapanır.

**Hedef:** claude.ai/design'daki "Queen Editor Basit v2" ile bugün çalışan uygulama arasındaki UI/UX
farklarını üç bağımsız yolla çıkarıp çakıştırmak ve tek bir Türkçe md'ye dökmek.

**Yaklaşım:** Üç alt-ajan, üç ayrı kaynağa demirleyerek aynı anda ve birbirini görmeden tam fark
listesi çıkarır. Ana oturum listeleri çakıştırır, güven derecesi atar, zayıf sinyalleri elle
doğrular ve belgeyi yazar. Hiçbir görev kod değiştirmez.

**Tasarım belgesi:**
[2026-08-08-queen-editor-tasarim-v2-fark-cikarma-design.md](../specs/2026-08-08-queen-editor-tasarim-v2-fark-cikarma-design.md)

## Genel kısıtlar

Her görevin gereksinimleri bu bölümü içerir.

- **Çıktı belgesinde kod dili geçmez.** Dosya adı, uç nokta, bileşen adı, veri dosyası, katman adı —
  hiçbiri. Yalnızca kullanıcının gördüğü davranış ve görünüm.
- **Tasarım dosyaları hiçbir yere kaydedilmez** — ne repoya, ne scratchpad'e, ne geçici bir klasöre.
  İçerik ya DesignSync'ten okunur ya görev metninde hazır bulunur.
- **Tasarım projesine yazılmaz.** DesignSync yalnız `get_project`, `list_files`, `get_file` ile
  kullanılır; `finalize_plan`, `write_files`, `delete_files`, `register_assets` **çağrılmaz**.
- **Kod değiştirilmez.** Bu turda tek satır kod yazılmaz.
- **Belge karar vermez.** Çelişki işaretlenir, hangisinin kazanacağı söylenmez.
- **İsim çakışması:** tasarımın "v2"si repodaki **roadmap v3**'e karşılık gelir. Her yerde
  "tasarım v2" ve "roadmap v3" diye tam yazılır; yalın "v2" kullanılmaz.
- **Dil:** her ara çıktı ve nihai belge Türkçe.
- **Tasarım projesi:** `efad1f83-69d3-4e07-89fa-3783839c81c3` ("Queen Editor").
- **Bugünkü uygulama:** `queen-editor/` — arayüz `queen-editor/frontend/src/`, davranış kuralları
  `queen-editor/backend/`.

## Bulgu biçimi

Üç yol da bulgularını **aynı biçimde** döndürür; çakıştırma buna dayanır.

```
### <kısa başlık>
- **Tür:** davranış | görsel
- **Yer:** Projeler | Panel | Galeri | Foto detay | Genel
- **Bugün:** <tek cümle — bugünkü uygulama ne yapıyor/nasıl görünüyor>
- **Tasarım v2'de:** <tek cümle — ne yapacak/nasıl görünecek>
- **Etiket:** (varsa) öksüz | sapma | tasarım söylemiyor
- **Dayanak:** <bu bulguyu nereden çıkardın — kaynağın adı, tek cümle>
```

`Bugün` ve `Tasarım v2'de` satırları **geçiş** anlatır, duruş değil. "Duraklat butonu var" yanlıştır;
"Duraklat'a basınca çalışan kare bitirilir, arada *Duraklatılıyor…* görünür, sonra bekleyen sayısı
7'den 8'e çıkar" doğrudur.

`sapma` etiketli bulguda `Tasarım v2'de` satırı yerine `Tasarım ne diyordu:` yazılır — bu bir v2
farkı değil, bugünün tasarımdan sapmasıdır.

## Dosya yapısı

| Dosya | Sorumluluğu |
|---|---|
| `docs/superpowers/research/2026-08-08-queen-editor-tasarim-v2-farklari.md` | **Tek çıktı.** 9 bölümlük fark belgesi (Görev 5'te oluşturulur) |

Başka dosya oluşturulmaz veya değiştirilmez.

---

## Görev 1: Üç yolu aynı anda koş

**Çıktı:** birbirini görmemiş üç tam fark listesi.

**Arayüz:**
- Üretir: Yol 1, Yol 2, Yol 3 listeleri — hepsi yukarıdaki **Bulgu biçimi**nde.

- [ ] **Adım 1: Yol 1'in görev metnini hazırla**

Yol 1 DesignSync'i **hiç çağırmaz**; okuyacağı iki yazılı belgeyi görev metninin içinde hazır bulur.
Bu iki belgenin tam metni (`HANDOFF.md` ve tasarım projesinin `CLAUDE.md`'si) DesignSync ile o an
çekilip prompt'a yapıştırılır. **Metinleri bu plana yazma** — genel kısıt tasarım dosyalarının
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

YASAK: DesignSync aracını çağırma. Wireframe kaynağına (simple-screens-v2.jsx, simple-app-v2.jsx,
styles.css vb.) erişmeye çalışma. Senin değerin yalnız yazılı kararlardan yürümenden geliyor.

YÜRÜYÜŞ:
- HANDOFF.md'nin "v2'de değişenler — sürekli kuyruk" bölümündeki her kararı tek tek al.
- Şu üç bölümü de tara, atlama:
  · "Kural olarak yazılanlar (ekran çizilmedi)" — ekranda görünmeyen ama bağlayıcı kararlar.
  · "Değişmeyenler" — tasarım "değişmedi" diyor olabilir ama uygulama oradan sapmış olabilir;
    o zaman bulgu bir fark değil, "sapma" etiketli olur.
  · "Görsel dil" — renk rolleri, tipografi, etiket biçimi.
- Her karar için bugünkü uygulamaya bak, ne yaptığını öğren, farkı yaz.
- Tasarım CLAUDE.md'sindeki yıkıcı eylem butonu standardını da bir karar say.

KAPSAM: davranış VE görsel. Renk, boşluk, tipografi, ikon, ölçü dahil. Her bulguyu "davranış" ya da
"görsel" diye etiketle.

<bulgu biçimi bloğu buraya aynen kopyalanır>

KURALLAR:
- Bulgular geçiş anlatır, duruş değil.
- Çıktında kod dili geçmesin: dosya adı, uç nokta, bileşen adı, katman adı yok. Kaynağı okursun ama
  yazdığın şey kullanıcının gördüğü davranıştır.
- Karar verme. Çelişki görürsen iki ifadeyi de yaz, hangisinin doğru olduğunu söyleme.
- Tasarımın cevaplamadığı bir şeye rastlarsan "tasarım söylemiyor" etiketi koy. Uydurma, tahmin etme.
- Tasarımın "v2"si repodaki roadmap v3'e karşılık gelir; ikisini de tam adıyla yaz.
- Türkçe yaz.
- Nihai metnin dönüş değeridir; bulgu listesinden başka bir şey yazma, giriş/kapanış cümlesi ekleme.

--- HANDOFF.md TAM METNİ ---
<buraya yapıştırılır>

--- TASARIM CLAUDE.md TAM METNİ ---
<buraya yapıştırılır>
```

- [ ] **Adım 2: Yol 2'nin görev metnini hazırla**

```
Sen "Yol 2 · Tasarım kaynağı" yolusun. Görevin: tasarım v2 wireframe'inin kendisinden envanter
çıkarıp bugünkü uygulamanın envanteriyle karşılaştırmak.

ARAÇ: DesignSync. Şemasını yüklemek için önce ToolSearch'ü "select:DesignSync" sorgusuyla çağır.
Proje: efad1f83-69d3-4e07-89fa-3783839c81c3

ÇEKECEĞİN DOSYALAR — yalnız bunlar:
  Queen Editor Basit v2.html, simple-app-v2.jsx, simple-screens-v2.jsx,
  wireframe-kit.jsx, tweaks-panel.jsx, design-canvas.jsx, styles.css

KESİN YASAK: HANDOFF.md ve CLAUDE.md dosyalarını ÇEKME. Bu yolun tüm değeri, tasarımın yazılı
anlatısını hiç görmemiş olmandan geliyor — anlatıyı okursan Yol 1'in kopyası olursun ve çıktın
geçersiz sayılır. Çağrıların kayda geçiyor; ihlal görünür.
Ayrıca yazma çağrısı yapma: finalize_plan, write_files, delete_files, register_assets yok.
Çektiğin içeriği hiçbir dosyaya kaydetme.

YÜRÜYÜŞ:
1. v2 wireframe'inden envanter çıkar: hangi ekran, hangi bölge, hangi kontrol, hangi durum,
   durumlar arası hangi geçiş, hangi metin, hangi renk/boşluk/ikon.
2. Aynı envanteri bugünkü uygulamadan çıkar: queen-editor/frontend/src/ (arayüz) ve
   queen-editor/backend/ (davranış kuralları). Read ve Grep ile oku.
3. İki envanteri satır satır karşılaştır. Her farkı yaz.

KAPSAM: davranış VE görsel. Renk, boşluk, tipografi, ikon, ölçü dahil. Her bulguyu "davranış" ya da
"görsel" diye etiketle.

<bulgu biçimi bloğu buraya aynen kopyalanır>

KURALLAR:
- Bulgular geçiş anlatır, duruş değil. Wireframe React kaynağı; durum makinesi orada yazılı, oku ve
  geçişi anlat.
- Çıktında kod dili geçmesin: dosya adı, uç nokta, bileşen adı, katman adı yok.
- Karar verme. Çelişki görürsen iki ifadeyi de yaz.
- Tasarımın "v2"si repodaki roadmap v3'e karşılık gelir; ikisini de tam adıyla yaz.
- Türkçe yaz.
- Nihai metnin dönüş değeridir; bulgu listesinden başka bir şey yazma.
```

- [ ] **Adım 3: Yol 3'ün görev metnini hazırla**

```
Sen "Yol 3 · Ters yön" yolusun. Diğer iki yol tasarımdan uygulamaya yürüyor; sen ters yönden,
uygulamadan tasarıma yürüyeceksin.

ARAÇ: DesignSync. Şemasını yüklemek için önce ToolSearch'ü "select:DesignSync" sorgusuyla çağır.
Proje: efad1f83-69d3-4e07-89fa-3783839c81c3
Tasarım tarafının tamamı sana serbest: HANDOFF.md, CLAUDE.md, v2 wireframe zinciri, v1 karşılıkları.
Tek istisna: screenshots/ klasörü ve direction-e.jsx kaynak değildir — başka bir tasarım yönüne
aitler, çekme.
Yazma çağrısı yapma (finalize_plan, write_files, delete_files, register_assets). Çektiğin içeriği
hiçbir dosyaya kaydetme.

YÜRÜYÜŞ — iki ayrı görevin var, çıktıda ikisini karıştırma:

GÖREV A — fark çıkarma:
1. Bugünkü uygulamanın davranış envanterini çıkar: her ekran, her bölge, her kontrol, her durum,
   her geçiş, her metin, her görsel kural. Kaynak: queen-editor/frontend/src/ ve
   queen-editor/backend/.
2. Envanterdeki her maddeyi tasarım v2'de ara ve üç kovadan birine at:
   · Karşılığı var, aynı  → değişmiyor, yazma.
   · Karşılığı var, farklı → fark, yaz.
   · Karşılığı YOK        → "öksüz" etiketiyle yaz. Ya tasarım v2'de bilerek kaldırıldı, ya tasarım
                            atladı. HANGİSİ OLDUĞUNA KARAR VERME, sadece işaretle.
3. Kapanış taraması: envanterin bugünden başladığı için, tasarım v2'de tamamen yeni olup uygulamada
   hiç tutamağı olmayan bir şeyi kaçırmış olabilirsin. Sonda tek bir tarama yap: "tasarım v2'de
   dokunulmuş olup envanterimde hiç görünmeyen bir yer kaldı mı?" Bulduğunu ekle.

GÖREV B — tam sadakat denetimi:
Envanterdeki her madde için ikinci bir soru sor: "tasarım bunu nasıl tarif etmişti, uygulama
gerçekten öyle mi yapıyor?" Bu soruyu tasarım v2'nin DOKUNMADIĞI yerlerde de sor — tüm uygulama
denetlenir. Uygulama tasarımdan sapmışsa bu bir v2 farkı DEĞİL, bir "sapma"dır; "sapma" etiketiyle
yaz ve "Tasarım v2'de" satırı yerine "Tasarım ne diyordu:" yaz.

Görev A ile Görev B'nin çıktıları ayrı iki listedir; birleştirme. "Bugün yanlış" ile "v2'de değişecek"
farklı iki iddiadır.

KAPSAM: davranış VE görsel. Renk, boşluk, tipografi, ikon, ölçü dahil.

<bulgu biçimi bloğu buraya aynen kopyalanır>

KURALLAR:
- Bulgular geçiş anlatır, duruş değil.
- Çıktında kod dili geçmesin: dosya adı, uç nokta, bileşen adı, katman adı yok.
- Karar verme. Çelişki görürsen iki ifadeyi de yaz.
- Tasarımın cevaplamadığı bir şeye rastlarsan "tasarım söylemiyor" etiketi koy.
- Tasarımın "v2"si repodaki roadmap v3'e karşılık gelir; ikisini de tam adıyla yaz.
- Türkçe yaz.
- Nihai metnin dönüş değeridir; iki listeden başka bir şey yazma.
```

- [ ] **Adım 4: Üçünü tek mesajda gönder**

Üç `Agent` çağrısı **aynı mesajda** yapılır ki paralel koşsunlar. Hepsi `general-purpose` tipinde.
Etiketler: `yol-1-anlati`, `yol-2-tasarim-kaynagi`, `yol-3-ters-yon`.

- [ ] **Adım 5: Kabul denetimi — biçim**

Her üç çıktı için ayrı ayrı kontrol et:

| Kontrol | Kabul ölçütü |
|---|---|
| Bulgu biçimi | Her bulguda Tür, Yer, Bugün, Tasarım v2'de, Dayanak satırları var |
| Geçiş kuralı | `Bugün` ve `Tasarım v2'de` satırları "ne olunca ne olur" anlatıyor, "şu var" demiyor |
| Kod dili | Çıktıda dosya adı, uç nokta, bileşen adı geçmiyor |
| Karar vermeme | Hiçbir bulguda "doğrusu şu olmalı" demiyor |
| Kapsam | Hem `davranış` hem `görsel` etiketli bulgular var |
| Dil | Türkçe |

- [ ] **Adım 6: Kabul denetimi — Yol 2'nin körlüğü**

Yol 2'nin çağrı kaydına bak. `HANDOFF.md` ya da `CLAUDE.md` çektiyse **o yolun çıktısı geçersizdir**;
ajanı yeniden koş, yasağı görev metninde bir kez daha vurgula. Bu denetim atlanamaz — üç yollu
yöntemin tek kırılgan noktası burasıdır.

- [ ] **Adım 7: Kabul denetimi — Yol 3'ün iki listesi**

Yol 3'ün çıktısında Görev A ve Görev B listeleri ayrı duruyor mu? Birleşmişse ajandan ayırmasını
iste. Sadakat denetimi ile v2 farkı karışırsa belgenin 3. ve 7. bölümleri ayrılamaz.

Bu görevde commit yok — henüz repoda değişen bir şey yok.

---

## Görev 2: Çakıştırma ve güven derecelendirmesi

**Çıktı:** tek birleşik fark tablosu; her satırda hangi yolların gördüğü ve güven damgası.

**Arayüz:**
- Tüketir: Görev 1'in üç listesi.
- Üretir: birleşik tablo — satır başına `başlık · tür · yer · bugün · tasarım v2'de · Y1 · Y2 · Y3 ·
  damga`; ayrıca öksüz, sapma ve "tasarım söylemiyor" etiketli maddelerin ayrı listeleri.

Bu görevi **ana oturum yapar, alt-ajan değil.** Üç listeyi birden gören tek yer burasıdır; bir
alt-ajana verilirse körlük düzeninin anlamı kalmaz.

- [ ] **Adım 1: Normalize et**

Aynı farkın üç farklı cümlesini tek satıra indir. Birleştirme kararı **elle** verilir; otomatik
başlık eşlemesi farklı iki bulguyu tek satıra ezer. İki bulgunun aynı olup olmadığına karar verirken
ölçüt `Bugün` ve `Tasarım v2'de` satırlarının aynı geçişi anlatıp anlatmadığıdır — başlık benzerliği
değil.

- [ ] **Adım 2: Damgala**

| Kaç yol gördü | Damga | Ne yapılır |
|---|---|---|
| 3/3 | kesin | listeye girer |
| 2/3 | güçlü | listeye girer |
| 1/3 | zayıf sinyal | Görev 3'e devredilir |

- [ ] **Adım 3: Çelişkileri ayır**

İki yol aynı konuda farklı şey söylüyorsa satır "çelişki" damgası alır ve **her iki ifade de**
yazılır. Hangisinin doğru olduğu söylenmez. Bu satırlar Görev 3'te elle doğrulanır.

- [ ] **Adım 4: Etiketli maddeleri ayrı listelere al**

`öksüz`, `sapma`, `tasarım söylemiyor` etiketli maddeler ana tablodan çıkarılıp kendi listelerine
alınır — sırasıyla belgenin 6, 7 ve 9. bölümlerini besleyecekler.

- [ ] **Adım 5: Kabul denetimi**

Üç listenin hiçbir maddesi kaybolmamış olmalı. Giriş sayısı = birleşik tablodaki satır sayısı +
birleştirmelerde eritilen tekrar sayısı + ayrı listelere alınanlar. Sayı tutmuyorsa kaybolan maddeyi
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

- [ ] **Adım 2: Sonucu işle**

- Doğrulandıysa → ana listeye girer, yanına **"elle doğrulandı"** notu düşülür.
- Doğrulanamadıysa → **atılmaz**, belgenin 8. bölümüne düşer. Bir yolun tek başına gördüğü şey çoğu
  zaman o yolun özel yakaladığı sınıftandır; sessizce silmek yöntemin amacını bozar.

- [ ] **Adım 3: Çelişkileri doğrula**

Çelişkili satırlarda **iki ifadeyi de** kaynağına kadar takip et. Amaç hangisinin doğru olduğuna
karar vermek değil — çelişkinin gerçek mi yoksa bir yolun okuma hatası mı olduğunu anlamak. Okuma
hatasıysa düzelt; gerçek çelişkiyse belgeye çelişki olarak girer.

- [ ] **Adım 4: Kabul denetimi**

Hiçbir zayıf sinyal "silindi" durumunda kalmamalı: her biri ya ana listede ya 8. bölümde.

Bu görevde commit yok.

---

## Görev 4: Roadmap v3 çelişki taraması

**Çıktı:** roadmap v3 ile tasarım v2 arasındaki çelişki tablosu.

**Arayüz:**
- Tüketir: Görev 3 sonrası birleşik liste; `docs/superpowers/plans/2026-08-08-queen-editor-v3-roadmap.md`.
- Üretir: `konu · roadmap v3 ne diyor · tasarım v2 ne diyor` tablosu.

- [ ] **Adım 1: Roadmap v3'ü madde madde oku**

`docs/superpowers/plans/2026-08-08-queen-editor-v3-roadmap.md` — özellikle "Bu yol haritasının
çekirdeği: canlı kuyruk" bölümündeki karşılaştırma tablosu ve Madde 2-6.

- [ ] **Adım 2: Her roadmap iddiasını birleşik listeyle karşılaştır**

Roadmap bir davranış iddia ediyor ve tasarım v2 başka bir şey söylüyorsa tabloya satır ekle. Bilinen
adaylar — ama tarama bunlarla sınırlı değil, roadmap baştan sona okunur:

| Konu | Bakılacak |
|---|---|
| Buton adı | roadmap "Sıraya ekle" der; tasarımda ne yazıyor |
| Duraklat / Devam / İptal | roadmap "tamamen kalkar" der; tasarım v2'de karşılığı var mı |
| Seed alanı | roadmap bekleyen kart detayında seed sayar; tasarım ne diyor |
| Sıralama yönü | roadmap bekleyenleri kuyruk sırasında sayar; tasarımın numaralandırma yönü ne |
| Silme sonrası numara | roadmap "numara boşta kalır" der; tasarım ne diyor |
| Kuyruktan çıkarma yolu | roadmap "tek yol bekleyen kartı silmek" der; tasarımda başka yol var mı |

- [ ] **Adım 3: Kabul denetimi**

Tabloda hiçbir satırda "doğrusu şu" cümlesi olmamalı. Belge karar vermez; bu bölüm yalnız iki
belgenin ne dediğini yan yana koyar.

Bu görevde commit yok.

---

## Görev 5: Belgeyi yaz

**Çıktı:** `docs/superpowers/research/2026-08-08-queen-editor-tasarim-v2-farklari.md`

**Dosyalar:**
- Oluştur: `docs/superpowers/research/2026-08-08-queen-editor-tasarim-v2-farklari.md`

**Arayüz:**
- Tüketir: Görev 2-4'ün çıktıları.

- [ ] **Adım 1: 9 bölümü sırayla yaz**

| # | Bölüm | Kaynağı |
|---|---|---|
| 0 | Başlık notu | isim çakışması — tasarım v2 = roadmap v3 |
| 1 | Özet | tasarım v2 tek paragrafta ne getiriyor |
| 2 | Doğrulama tablosu | Görev 2'nin birleşik tablosu + Görev 3'ün notları |
| 3 | Davranış farkları — ekran ekran | `davranış` etiketli maddeler; Projeler · Proje paneli (ikon şeridi, *Üretime ekle*, *Kuyruğu takip et*, *AI agent*) · Galeri · Foto detay · Genel |
| 4 | Görsel dil farkları | `görsel` etiketli maddeler |
| 5 | Roadmap v3 ile çelişkiler | Görev 4'ün tablosu |
| 6 | Öksüz davranışlar | Görev 2 Adım 4'ün `öksüz` listesi |
| 7 | Tasarım sadakati denetimi | Görev 2 Adım 4'ün `sapma` listesi |
| 8 | Zayıf sinyaller ve doğrulanamayanlar | Görev 3'ün `doğrulanamadı` maddeleri |
| 9 | Tasarımın cevaplamadıkları | `tasarım söylemiyor` listesi + "AI agent" panelinin boş oluşu |

- [ ] **Adım 2: 0. bölümün notunu tam yaz**

Şu bilgiyi taşımalı: tasarım projesinin "Basit v2" sürümü, repodaki **roadmap v3**'e karşılık gelir;
repodaki spec numaralarıyla karıştırılmamalı. Tasarımın `HANDOFF.md` belgesi bunu kendi de yazıyor.

- [ ] **Adım 3: 3 ve 4. bölümlerde iki satır kuralını uygula**

Her madde: *bugün ne oluyor* → *tasarım v2'de ne olacak*. Geçiş cümlesi, duruş değil.

- [ ] **Adım 4: 7. bölümün başına ayrım cümlesini koy**

Bu bölümdeki maddeler v2 farkı değildir; bugünkü uygulamanın tasarımdan sapmalarıdır. "Bugün yanlış"
ile "v2'de değişecek" farklı iki iddiadır ve bu belgede ayrı durur.

---

## Görev 6: Belge öz-denetimi ve teslim

- [ ] **Adım 1: Kod dili taraması**

Belgede dosya uzantısı (`.py`, `.jsx`, `.json`), yol ayracı (`/`), uç nokta (`/api/`), bileşen adı
ya da katman adı geçiyor mu? Geçiyorsa davranış cümlesine çevir.

İstisna: belgenin kendi başlığındaki ve ilgili belgelere verdiği bağlantılardaki yollar. Onlar
belgenin gövdesi değil, künyesi.

- [ ] **Adım 2: Karar taraması**

Belge hiçbir yerde "doğrusu şu", "şöyle olmalı", "tasarım kazanmalı" demiyor olmalı. Diyorsa çıkar.

- [ ] **Adım 3: Bütünlük taraması**

Görev 1'in üç listesindeki her madde belgenin bir bölümünde karşılığını buluyor mu? Bulmuyorsa
kaybolmuş demektir — bul ve yerleştir.

- [ ] **Adım 4: Kapsam taraması**

`görsel` etiketli maddeler 4. bölümde mi, gövdeye karışmamış mı? `sapma` etiketliler 7. bölümde mi?

- [ ] **Adım 5: Kullanıcıya sun**

Belgeyi kullanıcıya bildir ve incelemesini iste. **Commit etme** — kullanıcı okuyup onaylamadan
commit yok.
