# Madde 295 — Kartı sil, implementasyon turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 2/2 — kod, takım yeşile döner.
**Turun testleri:** [m295 test turu](2026-09-21-queen-editor-m295-kart-sil-testler-design.md),
`b25a0f81` ile kırmızı commit'lendi.

**Kullanıcıdan gereken:** yok.

## 1. `remove_frames` — kartın bütün borçları kapanır

Bugün tek satır yazılıyor:

```
record.mark(project, fid, layers.PHOTO, gallery[fid]["file"], queue.REMOVED, now())
```

Yerine kartın **borçlu olduğu her katman** için bir satır: katman `frame["owed"]`'dan okunur — galeri
zaten kuyruğun o karta ne borçlu olduğunu söylüyor, ve ikinci bir hesap ikinci bir doğru olurdu. Dosya
adı `layer_file(slot, fid, ...)`; `remove_layer` düşen işler için bunu zaten böyle yazıyor, ve iki
yerin aynı adı vermesi gerekiyor.

**Borcu olmayan, üretilmemiş bir kart** — mesela işi başka bir yoldan kapanmış olan — bugünkü gibi
fotoğraf yuvasına tek satırla kapanır: `removed` listesi ne döndüğünü söylemeye devam eder, ve
kartın *"hiç üretilmedi"* hâli kayıtta bir iz bırakmadan kalamaz.

## 2. `PhotoDetail` — kartın çıkışı her sekmede

Bugünkü zincir *"sekme başına tek yıkıcı düğme"* *(madde 80)* diye yazılmış. O kural bu maddeyle
**katman sekmeleri için** gevşiyor: dolu bir katman sekmesinde iki düğme yan yana durur —
*"Videoyu sil — kare kalır"* ve *"Kareyi sil"*. İkisi farklı şeye mal oluyor, ve kullanıcının
istediği tam olarak ikincisinin orada olması.

Kartın düğmesi her zaman pencere açar: sekmede duran katman diskte bir dosya, ve kartı silmek onu
götürüyor. Fotoğraf sekmesindeki `ownsItsPhoto` ayrımı orada kalır *(kopya kartın silinmesi diskten
bir şey götürmez)*; katman sekmesinde böyle bir durum yok.

Sıra: **önce katmanın kendi düğmesi, sonra kartınki** — dar olandan geniş olana, ve sayfanın geri
kalanı da böyle okunuyor.

## Değişmeyenler

- Seçim çubuğu: **Sil** zaten kartı her şeyiyle siliyor.
- Bekleyen ve kırmızı sekmelerin bugünkü çıkışları *(Fark 99, Fark 100)* aynen duruyor.
- `handleRemoveLayer`'ın silmeden sonra fotoğraf sekmesine dönmesi bu maddenin işi değil.

## Bitti sayılır

Dört test satırı koşulur ve dördü de yeşil. Frontend değiştiği için `dist` **aynı commit'te**
yeniden üretilir *(CLAUDE.md)*.
