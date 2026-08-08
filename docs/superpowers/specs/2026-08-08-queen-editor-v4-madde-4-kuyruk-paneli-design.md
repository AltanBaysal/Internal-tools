# Queen Editor v4 · Madde 4 — Kuyruk paneli

**Tarih:** 2026-08-08 · **Yol haritası:**
[v4 Madde 4](../plans/2026-08-08-queen-editor-v4-roadmap.md) · **Kapsadığı kodlar:** P14, P16-P25,
P27 · **sapmalar:** yarım kalan koşunun kartının başka konuşması, hatalı bitişte yeşil kartın
çıkmaması · **Katman:** yalnız ön yüz

## Amaç

Madde 2'nin taşıdığı durum kartları burada tasarımın diline geçiyor: **tek kart, tek sayı, tek
buton.** İlerleme yüzdesi, çubuk, "şimdi üretilen" satırı ve paydalı sayaç kalkıyor.

## 1 · Altı hâl, tek iskelet

Panel her zaman aynı üç parçadan oluşur: **durum satırı** (canlı nokta + başlık), **kalan kare
sayısı**, **tek buton**. Hangi hâlde ne yazdığı:

| Hâl | Nokta | Başlık | Sayı | Buton |
|---|---|---|---|---|
| Üretiliyor | mor, yanıp söner | Üretiliyor | `N` **kare bekliyor** | Duraklat |
| Duraklatılıyor… | mor, hâlâ yanıp söner | Duraklatılıyor… | `N` kare bekliyor | pasif "Duraklatılıyor…" |
| Duraklatıldı | soluk gri, sabit | Duraklatıldı | `N` kare bekliyor | Devam et |
| Üretim durdu | kırmızı, sabit | Üretim durdu | `N` kare bekliyor (kırmızı) | Kaldığı yerden devam et |
| Kuyruk tamamlandı | yeşil, sabit | Kuyruk tamamlandı | — | yok |
| Kuyruk boş | en soluk gri, sabit | Kuyruk boş | — | yok |

**Payda yok.** Tek dürüst sayı "kaç kare bekliyor"dur; kuyruğa ekledikçe toplam büyüdüğü için
paydalı sayaç her eklemede geriye sıçrardı.

**Bitiş kartı** yeşil ve tek cümle: "20 kare üretildi". Hatalı kare varsa aynı cümlenin içinde
kırmızıyla söylenir: "20 kare üretildi, 3 hatalı". Bu, bugünkü iki sapmayı da kapatıyor — hatalı
kareyle biten koşu artık kırmızı "yarım kaldı" kartı göstermiyor, yeşil kartı gösteriyor.

**Duraklatılmış hâlde kalan sayı bir fazladır**, çünkü kesilen kare kuyruğa geri döner (fark
belgesi 8.1 kararı: Duraklat çalışan kareyi keser). Ayrıca bir şey yapmak gerekmiyor — kesilen kare
günlüğe satır yazmadığı için zaten açık kalıyor ve sayıya dahil oluyor.

**Yarım kalan koşu** (oturum ölmüş, sunucu sebebi bilmiyor) "Üretim durdu" hâlini kullanır; bugünkü
"Üretim yarım kaldı — 17/48 tamamlandı" cümlesi kalkar. Teknik sebep satırı yalnız sunucu biliyorsa
yazılır.

## 2 · Görsel dil

- **Canlı nokta:** 7 piksel çapında, durum başlığının solunda. Akarken mor ve yaklaşık 1,2 saniyelik
  döngüyle sönüp yanar; duraklatılırken hâlâ atar; duraklatılınca sabitlenip soluk griye döner;
  durunca kırmızı, bitince yeşil, kuyruk boşken en soluk gri.
- **Sayı:** 26 punto tek rakam, yanında 13 punto normal yazıyla "kare bekliyor". Sayı normalde en
  açık yazı renginde; üretim durunca kırmızı.
- **Kalkanlar:** 5 piksellik mor ilerleme çubuğu, yüzde, "şimdi: …" satırı, paydalı sayaç.

## 3 · Hatalı kareye gitmek

Hatalı kare varsa kartın altında altı çizili kırmızı bir satır durur: **"3 kare üretilemedi —
galeride göster"**. Tıklanınca galerideki ilk hatalı kare görünür alana kaydırılır.

Kaydırma işini panel yapmaz, haber verir: panel `onShowFailures` çağırır, proje ekranı karenin
kutusunu bulup görünür alana getirir. Panelin galerinin yapısını bilmesi gerekmiyor.

## 4 · Duraklat ve Kuyruğu boşalt

**Duraklat** artık *Durdur* değil. Basınca buton pasifleşip "Duraklatılıyor…" der ve nokta hâlâ
atar; sunucu onaylayınca "Duraklatıldı"ya geçilir. Sunucudaki uç nokta aynı (`/api/stop`), değişen
yalnız kelimeler ve ara durumun görünürlüğü.

**Kuyruğu boşalt** ayrı bir buton olarak, yalnız **duraklatılmış ve durmuş** hâllerde görünür —
kuyruk akarken yoktur, önce duraklatmak gerekir. Onay sorar:

> **Kuyruk boşaltılsın mı?**
> Bekleyen 8 kare üretilmeden kuyruktan çıkar. Üretilmiş fotoğraflar galeride kalır.
> — Vazgeç / **Boşalt**

"Geri alınamaz" **denmez**: dosya silinmiyor, aynı prompt yeniden eklenebilir.

Buton yıkıcı eylem standardını kullanır — dolgusuz, kırmızı çerçeve, kırmızı metin, solunda çöp
ikonu. Panel butonu yeni olduğu için baştan öyle çizilir; onay penceresinin son butonu **paylaşılan
bileşendir**, dolayısıyla onu değiştirmek uygulama genelinde değiştirmek demektir ve burada
yapılır. Yani N1'in "dolu kırmızı buton hiçbir yerde yok" yarısı bu maddede kapanıyor; Madde 6'ya
kalan, galerideki ve karttaki silme butonlarının aynı dile girmesi.

**Boşalttıktan sonra** panel "Kuyruk boş" hâline döner; yeşil "tamamlandı" kartı **gösterilmez** —
o kart yalnız doğal bitişin onayıdır.

## 5 · "Kuyruk boş" hâli

Kuyrukta iş yokken ve anlatılacak bir koşu da yokken panel şunu gösterir: en soluk noktayla
**"Kuyruk boş"** ve altında **"Üretime ekle panelinden kare gönder."** Hiçbir buton yoktur.

## 6 · Bağlantı kartı

Bağlantı koptuğunda panel bugünkü davranışını korur — kart çıkar ve durum bilgisi soluklaşır — ama
metni yeni sayaç diline çevrilir: *"Sunucuya ulaşılamıyor — son bilinen: 17/48"* yerine
**"Sunucuya ulaşılamıyor — son bilinen: 12 kare bekliyor"**. Payda kalktığı için eski cümlenin
dayanağı kalmadı.

## 7 · Testler

`npm test`. Altı hâlin her biri için bir test, artı:

- Akan kuyrukta payda, yüzde, ilerleme çubuğu ve "şimdi:" satırı **yok**.
- Duraklat'a basınca buton pasifleşip "Duraklatılıyor…" diyor.
- Kuyruğu boşalt akan kuyrukta **yok**, duraklatılmışta ve durmuşta **var**.
- Boşalt onayı bekleyen kare sayısını yazıyor ve "geri alınamaz" demiyor.
- Hatalı kare satırı tıklanınca `onShowFailures` çağrılıyor.
- Bitiş kartı hatalı sayısını aynı cümlede söylüyor.
- Bağlantı kartı yeni sayaç dilini kullanıyor.

## 8 · Kabul kriteri

`npm test` ve `pytest` yeşil, `npm run build` koşuldu, `dist/` aynı commit'te. Üç cümle
kanıtlanmış:

1. Panel tek sayı gösteriyor — payda, yüzde ve çubuk hiçbir hâlde yok.
2. Kuyruğu boşalt yalnız duraklatılmış/durmuş kuyrukta çıkıyor ve onay soruyor.
3. Hatalı kareyle biten koşu yeşil kartı gösteriyor, hatalı sayısını aynı cümlede söylüyor.
