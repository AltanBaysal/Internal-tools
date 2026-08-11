# Queen Editor — Tasarım v3 fark çıkarma · Tasarım

**Tarih:** 2026-08-11 · **Branch:** `feat/mira-v1` · **Durum:** açık
**Öncülü:** [tasarım v2 fark çıkarma](2026-08-08-queen-editor-tasarim-v2-fark-cikarma-design.md) — yöntem
oradan taşındı, farkları aşağıda işaretli.

---

## Amaç

claude.ai/design'daki **Queen Editor** projesinin **"Basit v3"** sürümü ile **bugün çalışan uygulama**
arasındaki farkları çıkarmak. Tek çıktı bir Türkçe md: **düz bir liste** — nerede farklılar, ne
eklenecek, ne düzeltilecek, her maddeyi hangi yol buldu.

Bu belge farkın *kendisini* değil, farkı **nasıl çıkaracağımızı** tarif eder.

## İsim çakışması — belgenin başına not düşülür

Tasarım projesindeki **"Basit v2"** repodaki **roadmap v4**'e karşılık geliyordu; dolayısıyla
**tasarım v3 = roadmap v5**. Belge boyunca ikisi tam adıyla anılır, yalın "v3" kullanılmaz.

## Bugünkü uygulamanın durumu — belgeye not düşülür

Roadmap v4'ün Madde 1-11'i uygulandı ve push edildi; Madde 12 (Colab turu) **yüzeysel** koşuldu —
kullanıcı Colab'da denedi, düzgün duruyordu, detaylı tur yapılmadı. Yani taban, testleri yeşil ama
uçtan uca doğrulanmamış koddur. Fark listesi kaynak okumaya dayandığı için bu onu geçersiz kılmaz;
"düzeltilecek" tipli maddelerde "kod yanlış" ile "kod doğru, Colab'da patlıyor" ayrımı yapılamaz.

## Kapsam sınırı — çıktı belgesine ne girmez

Çıktı belgesinde **kod diline ait hiçbir şey geçmez**: dosya adı, uç nokta, bileşen adı, katman adı —
hiçbiri. Yalnızca kullanıcının gördüğü davranış yazılır. Kaynağı okumak serbesttir; **yazmak
yasaktır.**

**Görsel dil kapsam içidir** — renk, boşluk, tipografi, ikon, ölçü. Ama v2 turundan farklı olarak
ayrı bölüme çekilmez: aynı listede `görsel` etiketiyle durur.

**Belge karar vermez.** Çelişkiyi işaretler, hangisinin kazanacağını söylemez.

**Terminoloji tasarımın kendisinden alınır:** **kare** = içerik birimi (foto + video + ses),
**fotoğraf** = yalnız foto katmanı.

## Kaynaklar

**Tasarım tarafı** — proje `efad1f83-69d3-4e07-89fa-3783839c81c3`, DesignSync ile **salt okunur**.
`finalize_plan`, `write_files`, `delete_files` çağrılmaz. Tasarım dosyaları **hiçbir yere
kaydedilmez** — ne repoya, ne geçici klasöre.

| Dosya | Ne taşır |
|---|---|
| `HANDOFF.md` | v1 anlatısı + v2 bölümü + **v3 · v3.1 · v3.2** bölümleri |
| `CLAUDE.md` | yıkıcı eylem butonu standardı |
| `Queen Editor Basit v3.html` | v3 giriş noktası |
| `simple-app-v3.jsx`, `simple-screens-v3.jsx`, `export-designs-v3.jsx` | v3 ekranları, durumları, Export ekranı |
| `wireframe-kit.jsx`, `tweaks-panel.jsx`, `design-canvas.jsx`, `styles.css` | ortak altyapı |
| `Queen Editor Basit v2.html`, `simple-app-v2.jsx`, `simple-screens-v2.jsx` | v2 karşılıkları — yalnız Yol 3'e açık |

**Kapsam dışı:** `screenshots/` ve `direction-e.jsx` — v3 giriş noktası `direction-e`'yi
zincirlemiyor, ayrı bir görsel yön çalışması.

**Uygulama tarafı** — repodaki `queen-editor/`. Bugünkü davranışın tek kaynağı burasıdır.

**Çarpışma bölümü için** — `collab-toolbox/queen-tools/` ve
[queen-tools tasarımı](2026-08-09-queen-tools-design.md).

## Öncelik kuralı — v2'de yoktu, burada zorunlu

`HANDOFF.md` üst üste binmiş katmanlardan oluşuyor; v3.1 ve v3.2 kendi içlerinde "önceki bölümlerle
çelişen her yerde bu bölüm geçerlidir" diyor ve metinde üstü çizili satırlar var.

**Geçerlilik sırası: v3.2 > v3.1 > v3 > v2 > v1. Üstü çizili (`~~…~~`) metin ölüdür.**

Bu kural olmadan yazıya demirlenen yol, zaten geçersiz kılınmış kuralları bulgu diye yazar.

---

## Üç yol

Üç yol, üç ayrı kaynağa demirler. Her biri **tek başına tam liste** çıkarabilecek yetkinliktedir —
biri diğerinin parçası değil, sağlamasıdır. Üçü ayrı alt-ajanda, **aynı anda** koşar ve **hiçbiri
diğerinin çıktısını görmez.**

| | Yol 1 · **Anlatı** | Yol 2 · **Tasarım kaynağı** | Yol 3 · **Ters yön** |
|---|---|---|---|
| Demir | tasarımın *yazısı* | v3 wireframe'inin *kendisi* | bugünkü uygulamanın *kendisi* |
| Yön | tasarım → uygulama | tasarım → uygulama | uygulama → tasarım |
| Özel yakaladığı | kararların gerekçesi, ekranı çizilmemiş kurallar | yazıya geçmemiş her şey — etiketler, ara durumlar, boş hâller | öksüz davranışlar, bugün zaten yanlış olanlar |
| Kör noktası | tasarımcının yazmadığı | "neden"i bilmez | bugün hiç tutamağı olmayan yepyeni şey |

**Bu turda Yol 3 en değerli yol.** Bugünkü uygulama ≈ tasarım v2 olduğu için Yol 3'ün "karşılığı var,
farklı" kovası doğrudan v2→v3 deltasıdır — yani roadmap v4'te bilerek uygulanmış kararlardan
hangilerinin yerinden edildiği.

**Körlük erişim biçimiyle sağlanır, dileğe bırakılmaz:**

| Yol | Tasarım tarafına nasıl erişir |
|---|---|
| Yol 1 | **DesignSync'i hiç çağırmaz.** İki yazılı belge görev metninde hazır verilir; wireframe kaynağına erişimi yok |
| Yol 2 | DesignSync'i **kendisi çağırır**, yalnız v3 wireframe zinciri için. `HANDOFF.md` ve `CLAUDE.md` çekmesi yasak — ihlal çağrı kaydında görünür ve o yolun çıktısı geçersiz sayılır |
| Yol 3 | DesignSync'i kendisi çağırır, tasarım tarafının tamamı serbesttir |

### Yol 1 · Anlatı
Yazılı her kararı tek tek alır → bugünkü uygulamada karşılığını arar → fark varsa yazar. Öncelik
kuralı uygulanır. `HANDOFF.md`'nin "Kural olarak yazılanlar", "Değişmeyenler", "Karara bağlananlar"
ve "Görsel dil" bölümleri de taranır, atlanmaz.

### Yol 2 · Tasarım kaynağı
v3 wireframe'inden envanter çıkarır — hangi ekran, hangi bölge, hangi kontrol, hangi durum, durumlar
arası hangi geçiş, hangi metin. Aynı envanteri bugünkü uygulamadan çıkarır. Satır satır karşılaştırır.

### Yol 3 · Ters yön
Bugünkü uygulamanın davranış envanterini çıkarır, her maddeyi tasarım v3'te arar: karşılığı var-aynı
(yazılmaz) · karşılığı var-farklı (`değişecek`) · karşılığı yok (`öksüz`). Ayrıca **sadakat
denetimi**: uygulama, bugün hedeflediği tarifi (tasarım v2) tutturmuş mu? Tutturamadığı yerler
`düzeltilecek` tipiyle aynı listeye girer. Kapanış taraması: tasarım v3'te dokunulmuş olup
envanterinde hiç görünmeyen yer kaldı mı?

---

## Ortak kurallar

1. **Bulgu geçiş olarak yazılır, duruş olarak değil.** "Duraklat butonu var" yetersiz; "Duraklat'a
   basınca çalışan kare bitirilir, arada *Duraklatılıyor…* görünür, sonra bekleyen sayısı 7'den 8'e
   çıkar" doğrudur.
2. **Her bulgu iki satırdır:** *bugün ne oluyor* → *tasarım v3'te ne olacak*. Bugün hiç karşılığı
   yoksa ilk satır **"bugün yok"**tur; uydurulmuş karşılık aranmaz.
3. **Her bulgunun bir türü vardır:** `eklenecek` (bugün yok) · `değişecek` (var, farklı) ·
   `düzeltilecek` (bugün tarifine göre zaten yanlış) · `öksüz` (bugün var, tasarımda yok).
4. **Her bulgu `davranış` ya da `görsel` etiketi alır.**
5. **Kod dili yok.**
6. **Karar verilmez.** Çelişkide iki ifade de yazılır.
7. **"Tasarım söylemiyor" etiketi:** cevabı yoksa madde bu etiketi alır; uydurulmaz.
8. Belge ve tüm ara çıktılar **Türkçe**.

## Ara çıktılar repoya yazılır — v2'de yoktu

Her yol bulgularını **ilerledikçe** kendi dosyasına yazar. Sebep: yarıda kesilen alt-ajan hiçbir şey
döndürmez, emek tümüyle gider; v3'ün yüzeyi v2'nin birkaç katı. Körlük bozulmaz — her ajan yalnız
kendi dosyasına yazar, ötekilerinkini okumaz.

**Yer repodur, geçici klasör değil:**

| Dosya |
|---|
| `docs/superpowers/research/2026-08-11-v3-ara/yol-1-anlati.md` |
| `docs/superpowers/research/2026-08-11-v3-ara/yol-2-tasarim-kaynagi.md` |
| `docs/superpowers/research/2026-08-11-v3-ara/yol-3-ters-yon.md` |

Sebep: geçici klasör kullanıcının açıp okuyamadığı, denetleyemediği bir yer. Ham listeler repoda
dururken kullanıcı üç yolun ne bulduğunu çakıştırmadan **önce** görebilir, bir yolun yoldan çıktığını
fark edebilir.

**Bu üç dosya commit edilmez.** Çıktı belgesi yazıldıktan sonra klasör silinir; silme kullanıcının
onayıyla yapılır, kendiliğinden değil.

Bu, "tasarım dosyaları hiçbir yere kaydedilmez" kuralıyla çelişmez: dosyalara giren şey **bulgudur**
— kullanıcının gördüğü davranışı anlatan cümle. Tasarım kaynağının kendisi, alıntısı ya da özeti
oraya yazılmaz.

## Sağlama — çakıştırma

Çakıştırmayı alt-ajan değil, ben yaparım; üç listeyi de gören tek yer burasıdır. Aynı farkın üç ayrı
cümlesi tek satıra indirilir; birleştirme kararı elle verilir.

| Kaç yol | Damga | Ne yapılır |
|---|---|---|
| 3/3 | kesin | listeye girer |
| 2/3 | güçlü | listeye girer |
| 1/3 | zayıf sinyal | kaynağa dönülür, elle doğrulanır |

Doğrulanan zayıf sinyal "elle doğrulandı" notuyla girer; doğrulanamayan **atılmaz**, listede o damgayla
durur. İki yol aynı konuda farklı şey söylüyorsa madde "çelişki" damgası alır ve **her iki ifade de**
yazılır.

## Çıktı belgesinin iskeleti

Tek düz liste. Alt başlıklar yalnız okunabilirlik için alan alandır; numaralandırma **kesintisiz**
tektir (1, 2, 3…), harf önekli kod yok.

| # | Bölüm | İçerik |
|---|---|---|
| 0 | Başlık notu | tasarım v3 = roadmap v5 · öncelik kuralı · bugünkü tabanın durumu |
| 1 | Özet | tasarım v3 tek paragrafta ne getiriyor |
| 2 | **Fark listesi** | tek liste; her madde: ne · tür · davranış/görsel · bugün → tasarım · Y1/Y2/Y3 · damga. Alan başlıkları: Projeler · Proje ekranı ve panel şeridi · Fotoğraf üret · Video üret · Ses üret · Kuyruk · Üreticiler ve kurulum · Galeri · Detay sayfası · Export ekranı · Adlandırma ve kimlik · Uygulama geneli |
| 3 | queen-tools çarpışması | v3.2 JSON export'u kaldırıyor, `prompt_converter` onu okuyor; `photo_to_video` v3'ün içeri aldığı işi yapıyor — karar yok |
| 4 | Tasarımın cevaplamadıkları | AI agent panelinin hâlâ boş oluşu dahil |

**Yer:** `docs/superpowers/research/2026-08-11-queen-editor-tasarim-v3-farklari.md`

## Kapsam dışı

- Kod değişikliği — bu tur tek satır kod yazmaz.
- Roadmap v5'in yazılması; çelişkilerin karara bağlanması.
- Tasarım projesine yazma; tasarım dosyalarının herhangi bir yere kaydedilmesi.
- `screenshots/` ve `direction-e.jsx`.

## Karara bağlananlar

- Çıktı **tek düz listedir**; ayrı "sapma bölümü", ayrı "görsel dil bölümü", ayrı "geri alınanlar
  bölümü" yok — hepsi tür ve etiket sütunlarıyla aynı listede durur.
- Sadakat denetimi tabanı **tasarım v2 tarifidir**: soru "uygulama bugün hedeflediği tarifi tutturmuş
  mu?" — böylece `düzeltilecek` gerçek hatayı, `değişecek` tasarımcı kararını gösterir.
- Kapsam tam: video, ses, üreticiler/kurulum, Export ekranı, yeni adlandırma — hepsi girer.
- queen-tools çarpışması belgeye kendi bölümünde girer.
- Öncelik kuralı zorunlu; üstü çizili metin ölüdür.
- Üç yol aynı anda, birbirini görmeden koşar; her biri çıktısını kendi dosyasına yazar. Bu dosyalar
  repodadır — kullanıcı çakıştırmadan önce ham listeleri okuyabilsin diye. Commit edilmezler ve iş
  bitince kullanıcı onayıyla silinirler.
- Ayrı bir uygulama planı **yazılır**. Bu spec üç yolun neye demirlendiğini ve çıktının ne olacağını
  söylüyor; ama iki şeyi söylemiyor: bulgunun **satır yapısı** (çakıştırma buna dayanır) ve **kabul
  denetimleri** — özellikle "Yol 2 gerçekten kör kaldı mı" denetimi, yöntemin tek kırılgan yeri.
  İkisi de planda durur.

## Açık soru

Yok.
