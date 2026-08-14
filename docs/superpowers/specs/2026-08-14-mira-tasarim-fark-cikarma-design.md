# Mira — Yeni Tasarımla Fark Çıkarma · Tasarım Belgesi

**Tarih:** 2026-08-14 · **Durum:** kullanıcı incelemesi bekliyor

**Hedef:** claude.ai/design'daki Mira tasarımının yeni sürümü ile bugün repoda çalışan uygulama
arasındaki farkları üç bağımsız yolla çıkarmak, çakıştırmak ve tek bir Türkçe belgeye dökmek.
Belgenin cevapladığı soru: **repoda neyin güncellenmesi gerekiyor.**

**Bu tur kod değiştirmez.** Tek çıktısı bir belgedir; sıralama, öncelik ve yol haritası ayrı bir
turun işidir.

---

## 1 · Neden üç yol

Tek bir ajan tasarımı okuyup repoya baksa çıkan liste, o ajanın hangi kaynağa daha çok baktığına
göre eğrilir: çizime bakan yazılı kuralları, yazıya bakan çizilmemiş ayrıntıları kaçırır. Üç ajan
**aynı anda, birbirini görmeden** koşar; her biri farklı bir kaynağa demirler ve farklı bir yönden
yürür. Sonra listeler çakıştırılır: aynı farkı kaç yolun gördüğü, o farkın ne kadar sağlam olduğunu
söyler.

Yöntemin tek kırılgan yeri **körlüktür.** İki yol aynı kaynağı okursa üç yol değil iki yol koşmuş
oluruz ve örtüşme damgası yalan söyler. Bu yüzden körlük ajanın çağrı kaydından denetlenir, ihlal
eden yolun çıktısı geçersiz sayılır.

## 2 · Kaynaklar ve rolleri

### Tasarım tarafı

Proje `3c06e399-3b83-48b1-b186-26e56747823d` ("Mira AI tasarımı istemi") — v1'i doğuran projenin
aynısı, içeriği yenilenmiş. Dosyaların **rolleri ayrıdır**; bu ayrım üç yolun kesimini belirler:

| Dosya | Rolü | Çelişkide |
|---|---|---|
| `HANDOFF.md` | **Davranış sözleşmesi.** Tek katman; kendi deyişiyle "bugünkü davranışı anlatır, eski spec'i değil" | **kazanır** |
| `QueenAgent Handoff.dc.html` | Aynı sözleşmenin sayfa hâli | kazanır |
| `QueenAgent.dc.html` | **Çalışan prototip.** Bağlayıcı olan **görüntüsüdür, kodu değil** | kaybeder |
| `QueenAgent Frames.dc.html` | Ekran tuvali. Referans | kaybeder |

`support.js` claude.ai/design'ın üretilmiş çalışma zamanıdır ve `.thumbnail` bir önizlemedir;
ikisi de tasarım kaynağı değildir, hiçbir yol onları okumaz.

### Repo tarafı

- **Bugünkü uygulama:** `mira/frontend/src/` (arayüz) ve `mira/backend/` (davranış kuralları).
- **Bugünün tarifi:** `docs/superpowers/specs/2026-08-09-mira-v1-design.md` ve
  `docs/superpowers/plans/2026-08-09-mira-v1-roadmap.md`. Uygulama bunları hedefleyerek yazıldı;
  sadakat denetiminin tabanı budur, yeni tasarım değil.

## 3 · Üç yol

| | Yol 1 · Tasarımdan repoya | Yol 2 · Repodan tasarıma | Yol 3 · Handoff'tan repoya |
|---|---|---|---|
| **Okuduğu tasarım** | `QueenAgent.dc.html` + `QueenAgent Frames.dc.html` | hepsi | `HANDOFF.md` + `QueenAgent Handoff.dc.html` |
| **Yasağı** | handoff'un iki hâline de bakamaz | — | prototipe ve karelere bakamaz |
| **Yönü** | tasarım → uygulama | uygulama → tasarım | yazı → uygulama |
| **Birimi** | çizilmiş bir ekran öğesi | bugün var olan bir davranış | yazılmış bir kural |
| **Yakaladığı** | yazıya hiç geçmemiş olan: etiket metinleri, ara hâller, boş ve hata hâlleri, sayaç biçimleri, renk ve boşluk | öksüzler ve bugünün kendi tarifinden sapmaları | çizilmemiş ama bağlayıcı kurallar, gerekçeler, durum tanımları, klavye |
| **Kullanabildiği türler** | `eklenecek`, `değişecek`, `öksüz` | dördü de | `eklenecek`, `değişecek`, `öksüz` |

**Yol 1 ile Yol 3 birbirine kördür; bağımsızlıkları kaynaktan gelir. Yol 2 ikisini de görebilir;
bağımsızlığı ters yönden gelir.** Yol 2'ye kısıt koymak onu zayıflatır, çünkü envanteri bugünden
başlar — tasarımda ne olduğunu bilmeden "karşılığı yok" diyemez.

### Yol 1 · Tasarımdan repoya

Prototipten ve karelerden bir envanter çıkarır: hangi ekran, hangi bölge, hangi kontrol, hangi
durum, durumlar arası hangi geçiş, hangi metin, hangi boş hâl, hangi renk ve boşluk. Aynı envanteri
bugünkü uygulamadan çıkarır ve satır satır çakıştırır.

Prototipin **kodu bağlayıcı değildir** — sahte motorlu ve tek parçadır. Bulgu, prototipin nasıl
yazıldığından değil, ekranda ne göründüğünden çıkar.

### Yol 2 · Repodan tasarıma

İki ayrı iş yapar; **envanteri bir kez çıkarır, iki farklı tabana karşı sorgular.**

- **İŞ A — fark:** envanterdeki her maddeyi tasarımda arar. Karşılığı varsa ve aynıysa yazmaz;
  farklıysa `değişecek`; yoksa `öksüz`. Sonda tek bir kapanış taraması: "tasarımda dokunulmuş olup
  envanterimde hiç görünmeyen yer kaldı mı?" — bulduğu `eklenecek` olur.
- **İŞ B — sadakat:** aynı maddeleri Mira v1 tasarım belgesine ve yol haritasına karşı sorgular:
  "uygulama bugün **kendi tarifini** tutturmuş mu?" Tutturmamışsa bu bir tasarım farkı değil, bir
  hatadır: `düzeltilecek` türüyle ve `Tarifi neydi:` satırıyla yazılır.

İŞ B, yeni tasarımın hiç dokunmadığı yerlerde de sorulur; tüm uygulama denetlenir. İki iddia asla
tek bulguda birleşmez — "bugün yanlış" ile "tasarımda değişecek" ayrı satırlardır.

**Öksüzde karar verilmez.** Tasarımdan bilerek mi kaldırıldı, tasarım mı atladı — yalnız işaretlenir.

### Yol 3 · Handoff'tan repoya

Handoff'taki her yazılı kararı tek tek alır ve bugünkü uygulamada karşılığını arar. Özellikle taradığı
yerler: element kuralları, sekiz durumun tanımı (`idle` · `sending` · `typing` · `generating` ·
`error` · `loading` · `downloading` · `offline`), klavye ve erişilebilirlik, görsel dil, ve ekrana
çizilmemiş olup kural olarak yazılmış her şey.

## 4 · Ortak repo yüzeyi

**Üç yol da aynı yüzeyi tarar.** Biri backend'e bakıp öteki bakmazsa "1/3 zayıf sinyal" damgası
gerçekte "öteki ikisi oraya hiç bakmadı" demektir ve çakıştırma anlamını yitirir.

| Ne sorulur | Nerede okunur |
|---|---|
| Ekranlar, bölgeler, kontroller, metinler, boş ve yükleniyor ve hata hâlleri | `mira/frontend/src/features/workspace/` |
| Görsel dil: renk rolleri, boşluk, tipografi, yarıçap, geçiş süreleri | `workspace.css`, `shared/app.css` |
| İstemci davranışı: hangi eylem neyi tetikler, akış nasıl güncellenir, çevrimdışıda ne olur | `use*.js` kancaları, `shared/sse.js`, `shared/useRoute.js`, `shared/useOnline.js` |
| Kurallar: dosya kime ait, sohbet nasıl başlar, silme ve geri alma ne yapar, arama neyi bulur | `backend/features/workspace/domain/usecases/` |
| Ajan döngüsü: üç araç, cevabın dosyaya dönüşmesi, sistem yönergesi | `domain/prompt.py`, `domain/tools.py`, `data/xai_engine.py` |
| Adlandırma ve ad çakışması | `domain/naming.py` |
| Kullanıcının gördüğü hata dili | `domain/errors.py`, `presentation/routes.py` |

Testler kaynak sayılmaz: `*.test.jsx` ve `backend/tests/` **niyeti** anlatır, davranışı değil. Bir
belirsizliği çözmek için okunabilir, ama bir bulgunun dayanağı olamaz. `node_modules/`, `dist/`,
`.pytest_cache/` kapsam dışıdır.

## 5 · Bulgu biçimi

Üç yol da **aynı biçimde** yazar; çakıştırma buna dayanır.

```
### <kısa başlık>
- **Tür:** eklenecek | değişecek | düzeltilecek | öksüz
- **Etiket:** davranış | görsel
- **Alan:** <aşağıdaki listeden>
- **Bugün:** <tek cümle — bugünkü uygulamada ne olunca ne oluyor>
- **Yeni tasarımda:** <tek cümle — ne olunca ne olacak>
- **Not:** (varsa) tasarım söylemiyor
- **Dayanak:** <bu bulgu nereden çıktı — kaynağın adı, tek cümle>
```

| Tür | Ne zaman |
|---|---|
| `eklenecek` | bugün hiç karşılığı yok |
| `değişecek` | karşılığı var, farklı |
| `düzeltilecek` | bugün **kendi tarifine göre** zaten yanlış |
| `öksüz` | bugün var, yeni tasarımda karşılığı yok |

**Alanlar:** Kenar çubuğu · Home · Proje ekranı · Sohbet ekranı · Composer ve model seçici ·
Cevap akışı ve Markdown · Dosya rayı ve paneli · Dosya okuma · Yıkıcı eylemler ve geri alma ·
Boş hâller · Arama · Ajan döngüsü · Adlandırma ve kimlik · Durumlar ve hata ·
Klavye ve erişilebilirlik · Duyarlı yerleşim · Görsel dil · Uygulama geneli

Biçim kuralları:

- **Geçiş yazılır, duruş değil.** "Search butonu var" yanlıştır; "⌘K'ya basınca arama açılır, taslak
  varken Esc önce aramayı kapatır" doğrudur. İki yolun cümlesi ancak aynı geçişi anlatırsa eşleşir.
- Bugün hiç karşılığı yoksa `Bugün` satırı tam olarak **"bugün yok"**tur; uydurulmuş karşılık aranmaz.
- `düzeltilecek` türünde `Yeni tasarımda` satırı yerine **`Tarifi neydi:`** yazılır.
- `öksüz` türünde `Yeni tasarımda` satırı **"karşılığı yok"**tur.
- Tasarımın cevaplamadığı konu `Not: tasarım söylemiyor` alır; uydurulmaz.
- **Arayüz metinleri İngilizce alıntılanır, çevrilmez.** Belgenin dili Türkçedir ama Mira'nın arayüzü
  bilerek İngilizcedir; "New chat" bulgusunu "Yeni sohbet" diye yazmak hem tasarımı kaynak olmaktan
  çıkarır hem de çakıştırmayı bozar.

## 6 · Çakıştırma ve güven

Bu iş **ana oturumda** yapılır, alt-ajanda değil: üç listeyi birden gören tek yer orasıdır.

**Normalize.** Aynı farkın üç farklı cümlesi tek satıra iner. Birleştirme elle karar verilir; ölçüt
`Bugün` ve `Yeni tasarımda` satırlarının **aynı geçişi** anlatması, başlık benzerliği değil.

**Damga.**

| Kaç yol gördü | Damga | Ne olur |
|---|---|---|
| 3/3 | kesin | listeye girer |
| 2/3 | güçlü | listeye girer |
| 1/3 | zayıf sinyal | elle doğrulanır |

**`düzeltilecek` damgalanmaz.** Bu türü yalnız Yol 2 üretebilir, dolayısıyla tavanı 1/3'tür; örtüşme
onun hakkında hiçbir şey söylemez. Bu türdeki her bulgu istisnasız elle doğrulanır.

**Zayıf sinyal kusur değildir.** Her yolun yapısal olarak tek başına gördüğü bir sınıf vardır — Yol
1'in etiket metinleri, Yol 3'ün klavye kuralları, Yol 2'nin öksüzleri. Elle doğrulama, bulgunun
`Dayanak` satırındaki kaynağa dönüp iddiayı sınamaktır. Doğrulanırsa "elle doğrulandı" notuyla ana
listeye girer; doğrulanamazsa **silinmez**, `zayıf sinyal` damgasıyla listede durur.

**Çelişki.** İki yol aynı konuda farklı şey söylüyorsa satır `çelişki` damgası alır ve **iki ifade de**
yazılır. Önce çelişkinin gerçek mi yoksa bir yolun okuma hatası mı olduğu araştırılır. Gerçekse:
handoff ile prototip çelişiyorsa **handoff kazanır** ve bu belgeye not düşülür — bu bir karar değil,
tasarımın kendi öncelik kuralıdır.

## 7 · Çıktı belgesi

Üç yol ham bulgularını `docs/superpowers/research/2026-08-14-mira-ara/` altındaki kendi dosyalarına
yazar; bu klasör geçicidir ve commit edilmez. Turun tek kalıcı çıktısı
`docs/superpowers/research/2026-08-14-mira-tasarim-farklari.md`, dört bölüm:

| # | Bölüm | Kaynağı |
|---|---|---|
| 0 | Başlık notu | sürüm adlandırması (tasarım v2 / Mira v1) · ürün adı değişikliği · bugünkü tabanın durumu · dil kuralı |
| 1 | Özet | yeni tasarım tek paragrafta ne getiriyor |
| 2 | **Fark listesi** | çakıştırılmış tablo + elle doğrulama notları |
| 3 | Repo belgeleri çarpışması | yeni tasarımın `CLAUDE.md`'nin Mira bölümü, `mira/FOUNDATION.md`, `mira/CODE-STANDARD.md` ve v1 tasarım belgesiyle çeliştiği yerler |
| 4 | Tasarımın cevaplamadıkları | `tasarım söylemiyor` notlu maddeler |

**2. bölüm tek düz numaralandırmadır** (1, 2, 3…); alt başlıklar yalnız okunabilirlik içindir ve
numarayı sıfırlamaz. Her madde: *ne · tür · davranış/görsel · bugün → yeni tasarımda · Y1/Y2/Y3 ·
damga*.

**3. bölümü ana oturum çıkarır, ajanlar değil.** Üç yol da uygulamaya bakar, repo belgelerine değil;
karıştırılırsa "belge şöyle diyor" ile "kod şöyle yapıyor" aynı listede erir. Bu bölüm de karar
vermez, yalnız iki metni yan yana koyar.

## 8 · Kısıtlar

- **Çıktıda kod dili geçmez.** Dosya adı, uç nokta, bileşen adı, katman adı — hiçbiri. Yalnız
  kullanıcının gördüğü davranış ve görünüm. Kaynağı okumak serbesttir, **yazmak yasaktır.**
  İstisna: belgenin künyesi, ilgili belgelere verdiği bağlantılar ve 3. bölümdeki belge adları.
- **Tasarım içeriği hiçbir dosyaya kaydedilmez** — ne repoya, ne geçici klasöre. Dosyaya giren şey
  **bulgudur**; tasarım kaynağının kendisi, alıntısı ya da özeti değil.
- **Tasarım projesine yazılmaz.** Salt okuma çağrıları dışında hiçbir çağrı yapılmaz.
- **Kod değiştirilmez.** Bu turda tek satır kod yazılmaz.
- **Belge karar vermez.** Çelişki işaretlenir; hangisinin uygulanacağı söylenmez, maddeler sıralanmaz.
- **Çalışma zamanı hakkında tahmin yürütülmez.** Ajanlar kaynağın ne dediğini yazar; "çalışırken
  patlıyor mu" sorusunun cevabı bu turda yoktur.
- **İlerledikçe yazılır.** Her ajan bulgusunu kendi ara dosyasına yaza yaza ilerler; sonda toplu
  yazmaz, çünkü yarıda kesilen ajanın emeği tümüyle gider. Ajanın dönüş değeri bulgu listesi değil,
  kısa bir kapanış raporudur.
- **Ara dosyalar commit edilmez.** Kullanıcı çakıştırmadan önce ham listeleri okuyabilsin diye repoda
  durur, sonunda kullanıcı onayıyla silinir.
- **Dil:** her ara çıktı ve nihai belge Türkçe; arayüz metinleri İngilizce alıntılanır.

## 9 · Kabul ölçütleri

Üç ara dosyanın her biri için:

| Kontrol | Ölçüt |
|---|---|
| Dosya | yazılmış ve boş değil |
| Biçim | her bulguda Tür, Etiket, Alan, Bugün, Yeni tasarımda (ya da Tarifi neydi), Dayanak var |
| Tür | tanımlı dörtlüden; Yol 1 ve Yol 3'te `düzeltilecek` yok |
| Geçiş | `Bugün` ve `Yeni tasarımda` satırları "ne olunca ne olur" anlatıyor |
| Kod dili | dosya adı, uç nokta, bileşen adı geçmiyor |
| Karar | hiçbir bulguda "doğrusu şu olmalı" yok |
| Kapsam | hem `davranış` hem `görsel` etiketli bulgular var |
| Dil | Türkçe; arayüz etiketleri İngilizce ve olduğu gibi |

**Körlük denetimi — atlanamaz.** Yol 1'in çağrı kaydında handoff, Yol 3'ünkinde prototip ya da
kareler görünüyorsa o yolun çıktısı geçersizdir: dosyası silinir, ajan sıfırdan koşar, yasak görev
metninde bir kez daha vurgulanır. Üç ajandan herhangi biri ara klasördeki **başka** bir yolun
dosyasını okumaya çalıştıysa o yolun çıktısı kirlenmiştir; okumadan sonra yazdığı kısım atılır.

**Bütünlük denetimi.** Üç listenin hiçbir maddesi kaybolmamalı: giriş sayısı = birleşik tablodaki
satır + birleştirmelerde eriyen tekrar + 4. bölüme ayrılan.

## 10 · Kapsam dışı

- **Sıralama ve yol haritası.** Belge ne yapılacağını değil, neyin farklı olduğunu söyler.
- **Mimari ve katmanlama denetimi.** `mira/CODE-STANDARD.md` ihlalleri bu turun konusu değil.
- **queen-editor ve collab-toolbox.** Mira'nın onlara bağımlılığı yok; hiçbir yol oraya bakmaz.
- **`support.js`** ve tasarım projesindeki terk edilmiş yön denemeleri, eski sürüm dosyaları,
  ekran görüntüleri.

## 11 · Linke bakıldı — kapanan maddeler

- **Proje aynı proje.** İçeriği yenilenmiş, dosyalar `QueenAgent*` adıyla yeniden yazılmış ve yanına
  ayrı bir `HANDOFF.md` gelmiş. Terk edilmiş ya da ölü tasarım dosyası yok.
- **Handoff tek katman.** Üst üste binmiş sürüm yok; belge kendini "bugünkü davranışı anlatır, eski
  spec'i değil" diye tanımlıyor. Öncelik kuralı **düşer**. Ama sözleşmenin iki hâli var (markdown ve
  sayfa); Yol 3 ikisini de okur, çelişirlerse **ikisini de yazar** ve karar vermez.
- **Sürüm adlandırması.** Tasarım kendini **"v2 (post road-map)"** olarak adlandırıyor; repo tarafı
  **Mira v1**. Belgede her yerde "tasarım v2" ve "Mira v1" **tam** yazılır; yalın "v1"/"v2"
  kullanılmaz.
- **Ürün adı değişmiş: Mira → QueenAgent.** Tasarımın getirdiği en geniş dokunuşlu farktır: klasör
  adından `CLAUDE.md`'deki bölüm başlığına, `FOUNDATION.md` ve `CODE-STANDARD.md`'den arayüzdeki
  sözcük markasına kadar her yere değer. Fark listesine *Adlandırma ve kimlik* alanında girer ve
  belgenin 3. bölümünü besler.
- **Belgenin 0. bölümü** bu dört maddeyi künye olarak taşır.
