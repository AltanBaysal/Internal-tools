# Queen Editor v5 · Görev 28 — Export ekranı iskeleti · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 8, Görev 28 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
85, 86, 87, 88, 95 · **Tür:** arka uç + ön yüz.

## Neden

Bugünkü Export bir indirme bağlantısı: basınca ekranda hiçbir şey olmadan bir JSON iniyor ve
içinde fotoğraf adlarıyla prompt'lar var. Uygulama artık video üretiyor; export edilecek şey o
videolar, ve tasarım bunun için dördüncü bir ekran istiyor.

## Ne olacak

App bar'daki Export dosya indirmez, kendi ekranını açar: proje adı, çerçeveli özet kartı (kaç video
· toplam süre · nereye yazılacağı) ve altında yan yana iki mor buton. Hiç video yoksa kart
yönlendirmeye döner ve butonlar pasifleşir. JSON export tamamen kalkar.

## Kararlar

### 1. Dördüncü ekran, kendi adresinde

`/projects/<proje>/export`. Yönlendirici üçüncü bir yol tanır; ekranın kendi app bar'ı olur —
ortada "düğün · Export", sağda "← Galeriye dön" — ve sayfa 560 piksel genişlikte ortalanır.

Adres olması bilinçli: geri tuşu galeriye döner, yenilemek ekranı kaybettirmez ve export ekranı
galeriden ayrı bir yer olduğunu adresiyle de söyler.

### 2. Özet sunucunun cevabı, ekranın hesabı değil

Yeni use case `export_summary` galeriyi okur ve üç şey söyler: kaç kare video taşıyor, bunların
toplam süresi kaç saniye, ve export'un yazılacağı klasör. Ekran yalnız biçimlendirir.

Sebep: "hangi kareler videolu" sorusunun cevabı galerinin kendi cevabıyla aynı olmak zorunda —
ekranda ikinci bir sayım, bir gün galeriyle ayrışacak ikinci bir doğru olurdu.

### 3. Süre sabit uzunluktan çıkar

Bu sürümde video süresi seçilemiyor; graf sabit uzunlukta üretiyor. Toplam süre bu yüzden
`video sayısı × VIDEO_SECONDS` ile bulunur. Sabit alan adıyla domain'de durur ve tasarımın kendi
örneğiyle uyuşur: "22 video · 1:50 dk" → video başına 5 saniye.

Dosyayı ölçmek (ffprobe) bu sürümde yapılmaz: her video için bir süreç açmak, henüz hiçbir şey
üretmemiş bir özet için pahalı — ve süre zaten sabit.

### 4. Ekranın kendisi onay adımı (madde 88)

Butona basınca "emin misin?" penceresi çıkmaz; vazgeçmek "Galeriye dön" demektir. Önizleme ve video
listesi konmaz.

### 5. Video yokken ekran yönlendirmedir (madde 95)

Kart "Export edilecek video yok" ve altında "Hiçbir karenin videosu yok — önce Video üret panelinden
video üret." der. Kırmızı değil, hata görünümü değil: yapılacak iş söylenir. İki buton pasif kalır.

### 6. JSON export ölür

`GET /api/projects/<p>/export` ve `export_project` use case'i kalkar; yerine
`GET /api/projects/<p>/export/summary` gelir. Yarısı kalmış bir indirme bağlantısı bırakmak, iki
export kavramı taşımak olurdu.

## Nasıl görülür

1. Videolu projede Export'a bas → dördüncü ekran; kartta "3 video export edilecek · 0:15 dk" ve
   altında yazılacak klasörün yolu.
2. Videosuz projede aynı buton → "Export edilecek video yok" ve iki pasif buton.
3. "← Galeriye dön" galeriye döner; hiçbir yerde onay penceresi çıkmaz.

## Testler

**Arka uç:** özet videolu kareleri sayar · süre sayı × sabit · videosuz projede sıfır · klasör yolu
proje klasörünün altındaki export · bilinmeyen proje 404 · eski export ucu artık yok.

**Ön yüz:** app bar'daki Export ekrana götürür (indirme bağlantısı değil) · ekran adı ve özeti
yazar · süre m:ss biçiminde · iki buton yan yana ve mor · video yokken yönlendirme metni ve iki
pasif buton · "Galeriye dön" galeriye gider.

## Kapsam dışı

- **Uyarı satırları ve pasiflik kuralları** — Görev 29 (maddeler 89, 90, 91).
- **Export'un koşması, ilerleme, hata ve çıkış onayı** — Görev 30 (92, 93, 94, 96). Bu görevde
  butonlar duruyor ama basmak bir şey başlatmıyor; ekran onay adımı olarak tamam, koşusu sonraki
  görevin.
