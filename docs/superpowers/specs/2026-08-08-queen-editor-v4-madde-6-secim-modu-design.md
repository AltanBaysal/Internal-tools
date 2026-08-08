# Queen Editor v4 · Madde 6 — Seçim modu ve yıkıcı eylem

**Tarih:** 2026-08-08 · **Yol haritası:**
[v4 Madde 6](../plans/2026-08-08-queen-editor-v4-roadmap.md) · **Kapsadığı kodlar:** G6, G7, G8,
G11, N1 · **sapmalar:** seçim çubuğunun 0 seçiliyken durması · çubuğun yüzmemesi · sürüklemenin
basılı tutma eşiği olmadan başlaması · **Katman:** arka uç + ön yüz

## Amaç

Seçim modu **tek mod** oluyor: bekleyen kareler de fotoğraflarla birlikte seçiliyor ve tek hamlede
kuyruktan çıkarılıyor. Bugün halka yalnız fotoğraflarda beliriyor, yani 40 karelik bir kuyruktan 10
kareyi ayıklamanın yolu yok.

## 1 · Halka kimde var

| Kare | Halka | Gerekçe |
|---|---|---|
| Üretilmiş | var | — |
| Bekleyen | var, **birebir aynı görünür** | Farkı kartın kesikli görünümü söyler; ikinci bir işaret gereksiz |
| Hatalı | var | Aşağıda |
| Çalışan | **hiç yok** | Pasif bir halka "neden seçemiyorum?" sorusu doğurur; olmayan halka soru doğurmaz |

"Tümünü seç" çalışan kareyi atlar. Alt çubuktaki sayı tektir, türlere bölünmez: **"4 seçili"**.

**Hatalı kare için karar.** Tasarım hatalı kareden bu bölümde hiç söz etmiyor — üç onay senaryosu
yalnız fotoğraf ve bekleyeni sayıyor. Ama hatalı kare seçilemezse galeriden **hiçbir zaman
çıkarılamaz**, çünkü tek çıkışı olan "Tekrar dene" onu yeniden kuyruğa alır. Bu yüzden hatalı kare
de seçilebilir ve **bekleyenle aynı kovaya** girer: üretilmemiş bir karedir, "bu kareler
üretilmeyecek" cümlesi onun için de doğrudur. Tasarımın boşluğunu doldurduğumuz nokta burası.

## 2 · Onay metni üçe ayrılıyor

| Seçim | Başlık | Alt satır | Buton |
|---|---|---|---|
| Yalnız fotoğraf | "3 fotoğraf silinsin mi?" | "Bu işlem geri alınamaz." | Sil |
| Yalnız üretilmemiş | "3 kare kuyruktan çıkarılsın mı?" | "Bu kareler üretilmeyecek. Galerideki fotoğraflara dokunulmaz." | Çıkar |
| Karışık | "2 fotoğraf silinsin, 2 bekleyen kare kuyruktan çıkarılsın mı?" | "Fotoğraflar kalıcı olarak silinir — bu geri alınamaz. Bekleyen kareler üretilmeden kuyruktan çıkar." | Sil |

Bekleyende **"geri alınamaz" geçmez** — dosya silinmiyor, aynı prompt yeniden eklenebilir.

## 3 · Arka uç: tek kapı, kareye göre davranış

Bugün `POST …/photos/delete` yalnız fotoğrafı tanıyor. Onay tek pencere olduğu için silme de tek
istek olmalı; kareyi ne yapacağına **sunucu** karar verir:

| Karenin durumu | Yapılan |
|---|---|
| `done` | Dosya diskten silinir, günlüğe `deleted` satırı yazılır |
| `pending` / `failed` | Yalnız günlüğe `removed` satırı yazılır — dosya zaten yok |
| Tanınmayan ad | Atlanır, hata değil |

Uç nokta `POST …/frames/delete` olur (Madde 5'te liste `/frames` oldu, silme de aynı adı taşır) ve
cevabı ikisini ayırır: `{"deleted": […], "removed": […]}`. Eski `…/photos/delete` kalkar.

Ekran **iki listeyi birden** galeriden düşürür — ikisi de o kareyi galeriden çıkarır, farkları
yalnız diskte bir dosyanın silinip silinmediğidir. Yalnız `deleted`'ı dinlemek, çıkarılan bekleyen
kareyi ekranda bırakırdı.

**Çalışan kare için ayrı bir bekçi yok.** Arayüz onu seçtirmiyor; yine de bir yarış sonucu
`removed` satırı yazılsa kare render'ı bitince `done` satırını yazar ve son satır geçerli olduğu
için kendini toparlar. Ekstra kilit, kendini çözen bir soruna kilit koymak olurdu.

Numara koruması kendiliğinden çalışır: `removed` ve `deleted` satırları birer dosya adı taşır,
kayıt gördüğü her numarayı ölü tutar.

## 4 · Sürükleme basılı tutmayla başlıyor

*Bugün:* karta basıp hafifçe kaydırınca sürükleme hemen başlıyor, yani sıralamak isteyen de
istemeyen de sürüklüyor.
*Bundan sonra:* kart ancak **250 ms basılı tutulduktan sonra** kaldırılabilir hâle gelir. Tasarım
"basılı tut" diyor ama süre vermiyor; 250 ms bizim seçimimiz — kazara sürüklemeyi keser, bilerek
sürüklemeyi bekletmez.

Bekleyen ve hatalı karede aynı basılı tutma **ipucu** çıkarır: **"üretilince sıralanabilir"**. Kart
kalkmaz. Sıralama görsel bir karardır; görmediğin fotoğrafı prompt metnine bakarak sıralamak kör
iştir.

## 5 · Seçim çubuğu

- Galerinin altında **ortada yüzer** — kaydırılan içeriğe yapışık değil; bugün ancak en aşağı
  kaydırınca görünüyor.
- **En az bir kare seçiliyken** görünür; seçim sıfıra düşünce mod açık kalsa da çubuk kaybolur.
- Listenin sonunda ekstra boşluk kalır ki son satır çubuğun üstünde tam görünsün (bugünkü davranış).

## 6 · Yıkıcı eylem standardı

Onay penceresinin son butonu Madde 4'te zaten standarda geçti. Burada kalan: galerideki **Sil**
butonu ve detay sayfasındaki silme — dolgusuz, kırmızı çerçeve, kırmızı metin, solunda çöp ikonu.
Dolu kırmızı buton uygulamada hiçbir yerde kalmaz.

## 7 · Testler

**Arka uç**
- Üretilmiş kare seçilince dosya siliniyor ve `deleted` satırı yazılıyor.
- Bekleyen kare seçilince dosya silinmiyor, `removed` satırı yazılıyor ve kare kuyruktan çıkıyor.
- Hatalı kare de `removed` alıyor.
- Cevap ikisini ayrı listelerde veriyor; tanınmayan ad atlanıyor.
- Çıkarılan karenin numarası yeniden kullanılmıyor.

**Ön yüz**
- Halka bekleyen karede var, çalışanda yok; "Tümünü seç" çalışanı atlıyor.
- Sayı tek: karışık seçimde "4 seçili".
- Üç onay metni doğru seçiliyor; bekleyende "geri alınamaz" geçmiyor.
- Çubuk seçim sıfırlanınca kayboluyor.
- Kart 250 ms tutulmadan sürüklenemiyor; bekleyende ipucu çıkıyor.

## 8 · Kabul kriteri

`pytest` ve `npm test` yeşil, `npm run build` koşuldu, `dist/` aynı commit'te.

1. Bekleyen kareler seçilip tek hamlede kuyruktan çıkarılıyor, galerideki fotoğraflara dokunulmuyor.
2. Onay metni seçimin içeriğine göre üçe ayrılıyor.
3. Seçim çubuğu yüzüyor ve seçim boşalınca kayboluyor; sürükleme basılı tutmadan başlamıyor.
