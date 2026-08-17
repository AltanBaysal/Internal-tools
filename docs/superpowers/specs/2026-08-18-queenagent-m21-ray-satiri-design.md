# Madde 21 — Ray satırı ve zemin · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 21](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 45'in satır yarısı, 52, 57 · `HANDOFF.md` §2, §3
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 1 · Raydaki satırın tek işi dosyayı açmak (fark 52)

Bugün raydaki satır proje ekranındakiyle birebir aynı: üstüne gelince "×" beliriyor ve buradan
silinen dosya için rayın içinde bir hata satırı çıkıyor.

Tasarımda ray satırı yalnız **çip, ad ve ikincil satır** taşıyor; silme **proje ekranındaki listede**
kalıyor.

**Ray artık `deleting`'i hiç almıyor.** Silemeyen bir liste silme hatası da üretemez; Madde 19'da
şeridin yerine koyduğum hata satırı proje ekranında kalıyor, rayda konusuz.

`FileRow` iki ekranı da çizmeye devam ediyor: silme düğmesi `onDelete` verilince beliriyor, ray
vermiyor. Aynı satırı iki kez yazmak, iki ekranın satırının bir daha asla aynı görünmemesi demek
olurdu.

---

## 2 · Rayın kendi zemini (fark 57)

Bugün rayın zemini yok, tuvali gösteriyor ve onu ayıran tek şey soldaki çizgi. Tasarımda ray kendi
zeminini alıyor (`#FBF9F5`) ve dar pencerede sohbetin altına indiğinde de aynı zeminle iniyor.

Zemin **`.rail`'e** yazılıyor, dolayısıyla katlı hâl ve dar pencere onu kendiliğinden taşıyor.

---

## 3 · Açık dosyanın satırı (fark 45'in satır yarısı)

Okunan dosyanın satırı `#EFEBE4` zeminle seçili duruyor, hover `#F0ECE5`.

`FileRow` bir `selected` özelliği alıyor; hangi satırın seçili olduğunu **çağıran** biliyor, satır
değil.

---

## 4 · Açık soru: fark 53 yol haritasında yok

**Bu maddenin görülebilirliği eksik bir maddeye bağlı.** fark 45'in satır yarısı "okunan dosyanın ray
satırı seçili görünür" diyor — ama bugün ray bir dosya açılınca **listeyi hiç çizmiyor**, yerine
paneli çiziyor. Yani seçili satırın ekranda görüneceği bir an yok.

Bunu çözen fark **53** ("dosya açılınca ray listesinin yerinde kalması"): ray genişlerken satırlar
yerinde kalıyor. **fark 53 yol haritasının hiçbir maddesinde geçmiyor** — arama yaptım, Madde 21 de
22 de 23 de onu saymıyor.

Bu maddede **seçili satır kuralı yazılıyor ve bileşen düzeyinde sınanıyor**; ekranda görüneceği an
fark 53 bir maddeye yerleştiğinde geliyor. Kullanıcıya nereye konacağı soruluyor, çünkü tasarımın
vermediği bir ölçü gerektiriyor: ray 560px'e genişlerken bu genişliğin liste ile okuyucu arasında
nasıl bölüneceğini `HANDOFF.md` söylemiyor.

---

## 5 · Katman denetimi

`FileRow.jsx` (seçili hâl), `FileRail.jsx` (silme ve hata gitti), `workspace.css`. Arka uç yok.

---

## 6 · Kabul ölçütü

1. Rayda "×" yok; proje ekranındaki listede var.
2. Rayda silme hatası satırı yok.
3. Rayın kendi zemini `#FBF9F5`.
4. `selected` verilen satır `#EFEBE4` zemin alır.
5. Satırın hover'ı `#F0ECE5`.

## 7 · Risk

Seçili satır bu maddede ekranda görünmüyor; kuralı taşıyan tek şey bileşen testi. fark 53 gelene
kadar bu bir kilit, davranış değil.
