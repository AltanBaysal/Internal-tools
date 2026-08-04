# Queen Editor — Bölüm 13: Üretim akışı

**Tarih:** 2026-08-05 · **Yol haritası:** [2026-08-03-queen-editor-v2-roadmap.md](../plans/2026-08-03-queen-editor-v2-roadmap.md) Bölüm 13
**Tasarım kaynağı:** claude.ai/design `Queen Editor Basit v1.html` — `ArtboardS_Generating`,
`ArtboardS_GenPaused`, `ArtboardS_JsonError`.

## Ne çalışır

1. **Durdur = duraklat.** Basınca panel duraklatılmış görünüme geçer: üstte accent **Devam et**,
   altında "Üretim duraklatıldı — 7/48 tamamlandı" kartı, en altta soluk **İptal et**.
   - **Devam et** kalan karelerden sürer — baştan başlamaz.
   - **İptal et** kalan kuyruğu atar; üretilenler kalır, panel hazır durumuna döner.
2. **"Bekliyor" kareleri.** Üretim başlayınca galerinin başına o koşunun **planlanmış ama henüz
   üretilmemiş** kareleri kesikli, soluk "bekliyor" yer tutucuları olarak düşer; o an üretilen kare
   spinner'lı "Çalışıyor" karesidir. Kullanıcı ne olacağını baştan görür.
3. **Format hatası alan hatasıdır.** Üret'e basıldığında sunucu listeyi reddederse prompt kutusunun
   çerçevesi kırmızıya döner ve altında tek satır hata çıkar; **yazmaya başlayınca temizlenir.**

Bölüm 7'de Durdur "bitir" demekti ve nötr bir "Üretim durduruldu" kartı bırakıyordu; bu bölüm o
kartın yerine duraklatılmış görünümü koyar.

## Kapsam dışı

- **Hatalı kare için "Tekrar dene", ölümcül durma kartı ve oturum ölümünden sonra devam** — Bölüm 14.
- Duraklatmanın Drive'a yazılması (sekme kapanınca duraklamış koşuyu geri getirmek) — Bölüm 14'ün
  "sayfa kapanıp proje yeniden açılınca" maddesi.

## 1. Duraklatmanın anlamı — kuyruk durur, süren kare atılır

Tasarım, süren karenin akıbetini yazmıyor; sayıları söylüyor: 7 tamam, **kalan 41**, toplam 48.
Yani duraklandığı anda render edilen kare tamamlanmışlar arasında sayılmıyor. Kararımız bu
aritmetiği izler ve zaten Bölüm 7'de kurulan davranışla aynıdır:

- Duraklat, ComfyUI'daki süren render'ı keser (`/interrupt`); yarım kare **kaydedilmez**.
- O karenin numarası planda **ayrılmış kalır** — numaralar geri kullanılmaz (Bölüm 11 kuralı).
- Devam edildiğinde o kare baştan üretilir. "Kalan kareler" = planın, kayıtta karşılığı olmayan
  satırları.

Böylece duraklatma hiçbir zaman yarım dosya bırakmaz ve devam etmek kayıp üretmez.

## 2. Durum makinesi ve uçlar

| Durum | Ne demek | Panelde |
|---|---|---|
| `idle` | koşu yok | Üret |
| `running` | koşu sürüyor | Durdur + ilerleme kartı |
| `paused` | kullanıcı duraklattı, plan duruyor | Devam et + durum kartı + İptal et |
| `done` | plan bitti | yeşil "✓ tamamlandı" kartı |
| `error` | ölümcül durma | Bölüm 14 |

- `POST /api/stop` → koşuyu duraklatır (bugünkü davranışın adı değişiyor: cevaptaki `status`
  artık `"stopped"` değil **`"paused"`**).
- `POST /api/projects/<p>/resume` → planın kalan karelerinden yeni bir koşu başlatır. Kalan kare
  yoksa **409** ("Devam edilecek kare yok."). Başka proje üretimdeyse 409 (mevcut `Busy`).
- `POST /api/projects/<p>/cancel` → planı temizler, durum `idle` olur. Üretilenlere dokunulmaz.
  Koşu sürerken çağrılırsa 409 — önce duraklatılır (ekran zaten öyle akıyor).

Duraklatılmış durum sunucunun belleğindedir; sekme kapanıp açılınca kaybolur (plan Drive'da
durduğu için üretim kaybolmaz, yalnız ekran `idle` görünür). Bunu kalıcı yapmak Bölüm 14'ün işi.

## 3. "Bekliyor" kareleri

`/api/status` cevabı artık kalan karelerin dosya adlarını da taşır:
`pending: ["13_c.png", "13_d.png", …]` — plan sırasıyla, üretilmiş olanlar çıkarılmış.

Galeri, üretim sürerken (veya duraklatılmışken) **başa** şunları koyar: önce o an üretilen kare
(spinner + "Çalışıyor"), sonra bekleyen kareler; ardından mevcut fotoğraflar. Bekleyen kare
tasarımdaki gibidir: `className="wf-img"`, `borderStyle:"dashed"`, `opacity:.35`, içinde
`Mono size={10}` `var(--ink-3)` "bekliyor"; dosya adı satırı `var(--ink-4)`.

Bekleyen kareler **sıralanamaz ve seçilemez** — henüz yoklar; sıra ve seçim yalnız gerçek
fotoğraflarındır. Duraklatılmışken de görünürler: kuyruğun durduğu, kaybolmadığı görülsün.

## 4. Format hatası

Bugün sunucunun reddi genel durum-hatası kartı olarak çıkıyor. Bu bölümde prompt listesine ait
hatalar **alan hatası** desenine geçer (Bölüm 7 §4'ün ikinci deseni):

- Kutunun çerçevesi `var(--danger)`, hemen altında `Note size={12}` `var(--danger)` tek satır.
- Metin **sunucunun kendi cümlesidir** (ör. "Prompt listesi boş.", "Liste JSON dizisi olmalı.").
  Tasarım burada sabit "Format hatası" yazıyor; biz sunucunun metnini basıyoruz — FOUNDATION'ın
  "sebep uydurulmaz, sunucunun kendi metni gösterilir" kuralı bilinçli sapmanın gerekçesi.
- **Yazmaya başlayınca temizlenir** (tasarımın kuralı). Varyant alanına ait hatalar da aynı
  desendedir; hangi alana ait olduğunu sunucunun 400'ü değil, hatanın hangi alandan doğduğu
  belirler: prompt metni reddedilirse prompt kutusu, varyant sayısı reddedilirse varyant kutusu
  kızarır.
- Liste boşken Üret zaten pasif (bugünkü davranış korunur).

## 5. Doğrulama

1. Üret → galeri başında bekleyen kareler + bir "Çalışıyor" karesi belirir; üretildikçe bekleyenler
   azalır.
2. Durdur → panel duraklatılmış görünüme geçer; kuyruk durur, bekleyen kareler ekranda kalır.
3. Devam et → kaldığı yerden sürer, üretilmiş kareler yeniden üretilmez.
4. İptal et → bekleyen kareler kaybolur, panel Üret'e döner, üretilenler durur.
5. Duraklatıp devam edince duraklama anındaki yarım kare yeniden üretilir ve **aynı numarayı**
   kullanır (plan onu ayırmıştı).
6. Bozuk prompt listesi + Üret → kutu kızarır, altında sunucunun cümlesi; bir harf yaz → temizlenir.
7. Duraklatılmışken galeri sıralama ve silme çalışır; bekleyen kareler sürüklenemez/seçilemez.

## Kararlar

- **Durdur = duraklat**; `stopped` durumu `paused` olur, Bölüm 7'nin nötr kartı kaldırılır.
- **Süren kare atılır ve devam edince baştan üretilir** — tasarımın sayı aritmetiğinin gereği.
- **Kalan kareler plandan hesaplanır** (`plan.json` − kayıt), ayrı bir kuyruk dosyası tutulmaz:
  iki yerde tutulan sıra iki kere yanlış olur.
- **`pending` listesi `/api/status`'ta taşınır** — galeri kuyruğu sunucudan öğrenir, tahmin etmez.
- **Alan hatası sunucunun metnini gösterir**, tasarımın sabit "Format hatası" metni yerine.
- **Duraklatma bellekte kalır** (Drive'a yazılmaz); kalıcılık Bölüm 14'ün işi.
