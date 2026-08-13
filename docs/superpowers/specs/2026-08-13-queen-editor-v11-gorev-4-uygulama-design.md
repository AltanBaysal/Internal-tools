# v11 Görev 4 — seçim kalkınca halkalar da kalkar: İMPLEMENTASYON döngüsü (tasarım)

**Tarih:** 2026-08-13 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v11](../plans/2026-08-13-queen-editor-v11-roadmap.md) · **Döngü:** 2/2
**Testler:** [test spec'i](2026-08-13-queen-editor-v11-gorev-4-testler-design.md) ·
commit `29848c8` (iki test kırmızı)

## Karar: mod bir durum değil, seçimin kendisi

Galeride bugün iki durum var — `selected` (hangi kareler) ve `selecting` (mod açık mı) — ve ikisi
ayrı ayrı güncelleniyor. Hata da tam olarak bu: `toggle` modu açıyor, ama seçimi boşaltmak kapatmıyor.
İki değerin ayrı yaşadığı her yerde ayrışabilirler, ve bir kez ayrıştıklarında ekranda çelişki
görünüyor — çubuk yok, halkalar var.

`selecting` **türetiliyor**: `selected.length > 0`. İkinci durum siliniyor.

Kural olarak bakıldığında zaten böyleydi: çubuk `selecting && selected.length > 0` diye çiziliyordu,
yani iki koşuldan biri gereksizdi. Şimdi tek koşul kalıyor ve hata yazılamaz hâle geliyor — birbirine
düşecek iki değer yok.

## Bedeli, açıkça

Son kareyi bırakınca mod bittiği için, karo tıklamak yine fotoğrafı açar. Bugün o tık seçime devam
ederdi. Seçime devam etmenin yolu halkaya tıklamak — halka fare gelince zaten beliriyor, ve
"Vazgeç"ten sonra da tek yol buydu.

Son kareyi bırakan tıkta yanlışlıkla fotoğrafın açılmaması ayrıca korunuyor: bağlantının kendi
işleyicisi `selecting` hâlâ açıkken çalışıyor, dolayısıyla o tık yalnız bırakır, gezinmez.

## Değişen yerler

| Dosya | Ne olacak |
|---|---|
| `.../photo_generation/Gallery.jsx` | `selecting` durumu silinir, `selected`'tan türetilir; `toggle` ve `closeSelection` sadeleşir |
| `queen-editor/frontend/dist/` | yeniden derlenir (aynı commit) |

Çubuğun koşulu `selecting && selected.length > 0` idi; artık ikisi aynı şey, biri kalıyor.

## Kapsam dışı

- Halkanın köşesi (Görev 5), silme akışı, Esc, sürükleme.
- CSS: `.qe-tile--selecting .qe-check` kuralı olduğu gibi kalıyor; değişen, sınıfın ne zaman
  yazıldığı.

## Bitti sayılır

`npm test --prefix queen-editor/frontend` → 318 geçen, 0 düşen. Dört testin hiçbiri değiştirilmemiş,
`dist/` aynı commit'te yeniden derlenmiş olur.
