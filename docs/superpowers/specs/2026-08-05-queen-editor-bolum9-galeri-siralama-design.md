# Queen Editor — Bölüm 9: Galeri sıralama

**Tarih:** 2026-08-05 · **Yol haritası:** [2026-08-03-queen-editor-v2-roadmap.md](../plans/2026-08-03-queen-editor-v2-roadmap.md) Bölüm 9
**Tasarım kaynağı:** claude.ai/design projesi `Queen Editor` → `Queen Editor Basit v1.html`
(<https://claude.ai/design/p/efad1f83-69d3-4e07-89fa-3783839c81c3>) — dosyalar repoya kopyalanmaz,
her ihtiyaçta taze çekilir. Bu bölümün detayları oradan okundu (rozet, sürükleme görünümü,
bırakma yuvası).

## Ne çalışır

Kullanıcı galeriyi elle sıralar: bir kareyi basılı tutup sürükler, bıraktığı yere yerleşir, sıra
numaraları güncellenir. Sıra kalıcıdır — sayfa yenilenince, oturum ölüp dönünce aynı sırada durur.
Yeni üretilen fotoğraflar elle kurulmuş sıranın **en üstüne** düşer; eski sıra bozulmaz.

Bu bölüm Bölüm 10'un (Export) temeli: export dosyasının satır sırası bu sıradır.

## Kapsam dışı

- **Export** (Bölüm 10) — sıra burada kurulur, dosyaya orada yazılır.
- **Silmenin sıraya etkisi** (Bölüm 12) — silme henüz yok; kaydın dışında kalan ad sessizce düşer
  (aşağıdaki uzlaştırma kuralı bunu zaten karşılıyor).
- **Foto detay sayfası** (Bölüm 11) — kareye tıklama davranışı değişmez, bugünkü gibi ham dosyayı
  yeni sekmede açar.
- **Dokunmatik sürükleme ve klavyeyle sıralama** — araç masaüstünde, tek kullanıcıyla çalışıyor;
  HTML5 sürükle-bırak klavyeyle erişilebilir değildir, bu bilinçli bir sınırdır.
- **Çoklu seçim sürükleme** — seçim modu Bölüm 12'de geliyor; tek kare sürüklenir.

## 1. Sıra nerede saklanır — dördüncü dosya

Proje klasöründe bugün üç dosya var (CODE-STANDARD §Separation of concerns): `settings.json`,
`plan.json`, `photos.jsonl`. Sıra bunların hiçbirine ait değil:

| Soru | Dosya | Yazan | Ömür |
|---|---|---|---|
| Panel ne göstersin | settings | Üret'e basış | üretimde üzerine yazılır |
| Bu koşu hangi kareleri istedi | plan | koşu başı | koşu başına bir kez |
| Hangi fotoğraflar var, neyden üretildi | photo record | her fotoğraf indikçe | kalıcı, **yalnız eklenir** |
| **Galeri hangi sırayla göstersin** | **order** (yeni) | **kullanıcının bıraktığı an** | **her sürüklemede baştan yazılır** |

Standardın kuralı bunu zaten söylüyor: "dördüncü soruyu cevaplayan alan dördüncü dosyayı ister."
Sırayı `photos.jsonl`'a alan olarak eklemek iki kuralı birden bozardı — kayıt **yalnız-ekleme**dir
(yarım kalan oturum en fazla son satırı kaybetsin diye), sıra ise her sürüklemede tüm dosyanın
yeniden yazılmasını gerektirirdi; bir sürükleme bütün üretim izini riske atamaz.

**Dosya:** `order.json` → `{"order": ["11_d.png", "11_c.png", …]}` — sadece dosya adları, galeri
sırasıyla. Bir ad kayıtta yoksa (silinmiş foto, elle bozulmuş dosya) sessizce düşer; dosya yoksa
ya da okunamıyorsa "elle sıra yok" demektir.

## 2. Uzlaştırma kuralı (tek yerde, domain'de)

`list_photos` artık kaydı ve sırayı birleştirir. Kural üç satır:

1. Kayıtta olup sırada **olmayan** fotoğraflar en üste gelir, kendi aralarında kaydın sırasıyla
   (en yeni önce) — "yeni üretilenler en üstte" bundan doğar, ayrı bir mekanizma yok.
2. Sırada geçen adlar, verildikleri sırayla onların altına dizilir.
3. Sırada olup kayıtta olmayan ad yok sayılır.

Sonuç her zaman kaydın kendisiyle aynı kümedir: sıra dosyası bir fotoğrafı ne yaratabilir ne
gizleyebilir. Bu, bozuk/eski bir `order.json`'ın galeriyi boşaltmasını imkânsız kılar.

## 3. Sunucu arayüzü

| Uç | Ne yapar |
|---|---|
| `GET /api/projects/<p>/photos` | değişmez — ama artık **galeri sırasıyla** döner (§2) |
| `PUT /api/projects/<p>/order` | gövde `{"order": [dosya adları]}`; kaydeder ve **saklanan** listeyi döner |

`PUT`'un kuralları:

- Gövde liste değilse ya da içinde metin olmayan öğe varsa **400** + Türkçe mesaj
  (`"Sıra listesi metin dizisi olmalı."`).
- Proje yoksa **404** (mevcut `ProjectMissing` deseni).
- Kayıtta olmayan adlar **kaydedilmeden önce süzülür** — sunucu kendi gerçeğine göre temizler,
  istemcinin bayat listesi dosyayı kirletemez.
- Cevap saklanan listedir; istemci ne kaydedildiğini görür, tahmin etmez.

Sunucu sırayı **doğrulamaz** (eksik ad hata değildir): eksik kalan fotoğraf bir sonraki okumada
§2.1 ile zaten en üste düşer. Yani iki sekme aynı anda sürüklerse son yazan kazanır, kimse
fotoğraf kaybetmez.

## 4. Ekranda ne değişir

Tasarımdan birebir (kaynak: `simple-screens.jsx`):

**Sıra rozeti** — her karenin fotoğrafının **sağ üstünde**, hep görünür (hover'a bağlı değil):
`Mono size={10}`, `position:absolute; top:6; right:6`, zemin `rgba(10,8,7,.75)`, renk
`var(--ink-2)`, `padding:"2px 6px"`, `borderRadius:3`, `zIndex:1`. İçerik ham sıra numarasıdır
(1'den başlar, sıfır dolgusu ve önek yok). Numara konumdan türer, saklanmaz — bırakınca kendiliğinden
güncellenir.

**Tutamak yok.** Tasarımın kitinde bir tutamak öğesi (`wf-grip`) tanımlı ama galeride
kullanılmamış; sürükleme **karenin tamamından** başlar. Tasarımın kendi notu: "basılı tut +
sürükle → sıralama başlar · bırakınca numaralar güncellenir".

**Sürüklenen kare** — `transform: rotate(-3deg) scale(1.04) translate(14px, -10px)`,
`filter: drop-shadow(0 12px 24px rgba(0,0,0,.55))`, `zIndex:5`.

**Bırakma yuvası** — hedef hücrede kare bir yer tutucu: `2px dashed var(--accent)`,
`borderRadius:4`, zemin `var(--bg-3)`, altında dosya adı satırının yerini koruyan görünmez bir
satır (ızgara hizası kaymasın diye).

**Üretim sürerken sıralama serbesttir** — galeri Bölüm 7'de zaten kilitlenmiyor. O anda üretilen
kare (spinner) sürüklenemez ve rozet almaz: henüz kayıtta yoktur, sırası da yoktur.

## 5. Sürükleme akışı (istemci)

1. Kare üzerinde sürükleme başlar → o kare "sürüklenen" görünümünü alır.
2. Başka bir karenin üstüne gelince → o konuma bırakma yuvası çizilir, sürüklenen kare akıştan
   çıkar (yerinde boşluk kalmaz).
3. Bırakınca → yeni sıra **hemen ekranda uygulanır** (iyimser güncelleme), aynı anda `PUT` gider.
4. `PUT` başarılıysa iş biter. Başarısızsa: mevcut durum-hatası kartı çıkar
   ("Sıra kaydedilemedi") ve galeri sunucunun gerçeğine geri döner — ekran kaydedilmemiş bir sırayı
   kaydedilmiş gibi göstermez.
5. **Kaydetme uçarken gelen poll cevapları uygulanmaz.** Üretim sürerken galeri 2 saniyede bir
   yenileniyor; kaydetme penceresinde gelen eski listenin sırayı geri sektirmesi ekranın
   titremesi olurdu. Kaydetme bitince normal yenileme sürer.

## 6. Doğrulama

1. 6 fotoğraflı projede 5. kareyi 1. sıraya sürükle → rozetler 1..6 yeniden numaralanır; sayfayı
   yenile → aynı sıra durur.
2. Üret (yeni 4 foto) → yeniler en üstte, elle kurulmuş sıra altında bozulmadan durur.
3. Üretim sürerken sürükle → sıra tutar, poll geri sektirmez.
4. Sunucuyu kapat, sürükle → "Sıra kaydedilemedi" kartı çıkar, galeri eski sırasına döner.
5. `order.json`'ı elle boz (geçersiz JSON) → galeri kayıt sırasıyla açılır, hata vermez.
6. `order.json`'a olmayan bir ad ekle → galeri etkilenmez, ilk kaydetmede ad düşer.

## Kararlar

- **Sıra ayrı dosyada** (`order.json`) — gerekçe §1; `photos.jsonl` yalnız-ekleme kalır.
- **Uzlaştırma domain'de**, veri katmanında değil: kural test edilebilir kalsın, `order.json`'ın
  biçimini yalnız data katmanı bilsin.
- **Rozet numarası saklanmaz**, konumdan türer — iki gerçek kaynağı olmaz.
- **Tutamak yok, kare sürüklenir** — tasarımın kararı (kitteki `wf-grip` galeride kullanılmamış).
- **HTML5 sürükle-bırak, kütüphane yok** — tasarım bir kütüphane davranışı tarif etmiyor; masaüstü
  tarayıcıda yerel API yetiyor, yeni bağımlılık taşınmaz (FOUNDATION: taşınan her bağımlılığın
  bedeli vardır).
- **İyimser güncelleme + hata dönüşü** — mevcut durum-hatası deseni kullanılır, üçüncü desen doğmaz.
