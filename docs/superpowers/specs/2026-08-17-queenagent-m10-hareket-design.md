# Madde 10 — Hareket bandı · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 10](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynaklar:** fark 76 · sapma 87 · **karar 3** · `HANDOFF.md` §10
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 0 · Kaynak düzeltmesi, ve bir yerde kuralın harfine uyuluyor

Yol haritası bu maddeyi *"karar 6"* ile etiketliyor; karar 6 logo karesini konu alıyor ve Madde 8'de
uygulandı. Buradaki karar **karar 3**:

> **Yazılı kural kazandı:** hareket yalnız 140–220ms'lik saydamlık geçişi, artı rayın 220ms'lik
> genişlik geçişi. Yerleşmiş hiçbir öğe yana ya da yukarı kaymıyor.

**Kuralın kapsamı bir yerde karar gerektiriyor: dönen bekleme göstergesi.** `FilePanel`'in Download
düğmesi hazırlanırken 11px'lik bir çember döndürüyor (`spin`, sonsuz). Bu ne bir saydamlık geçişi ne
rayın genişliği; yerleşmiş bir öğeyi de kaydırmıyor, yerinde dönüyor.

**Karar: gösterge kalkıyor, "preparing…" sözü kalıyor.** Gerekçe kuralın kendi biçimi — "hareket
**yalnız** şunlardan ibarettir" diyen bir cümle, sayılmayan her hareketi dışarıda bırakır; "yana
kaymayan hareket serbesttir" demiyor. Kaldırınca kaybolan bilgi de yok: düğme zaten sözle
"preparing…" diyor ve tıklanamaz durumda.

**Yanıp sönen üç nokta kalıyor.** O bir saydamlık animasyonu (`blink`) ve tasarımın kendi
çekirdek döngüsünde adıyla geçiyor: *"Three blinking dots under a QUEENAGENT · time label."*

---

## 1 · Bugünkü hareket dökümü

| Ne | Bugün | Karara göre |
|---|---|---|
| `riseIn` (saydamlık **+ 6px yukarı süzülme**) | `.screen__column` 350ms, `.empty` 400ms | **Kural dışı iki kez**: hem kayıyor hem bandı aşıyor |
| `slideIn` (yalnız saydamlık, adı yanlış) | 200ms ×2, **250ms** ×1 | biri bandı aşıyor |
| `blink` | sonsuz, saydamlık | kalıyor |
| `spin` | sonsuz, dönme | **kalkıyor** |
| `.rail` genişlik geçişi | 220ms | kalıyor, tam bandın ucunda |

Sapma 87 tam olarak `riseIn`'di: uygulama Mira v1'in kendi kuralından da sapmıştı.

---

## 2 · Ne olacak

**Tek bir saydamlık animasyonu kalıyor: `fadeIn`.** `riseIn` siliniyor, `slideIn` de siliniyor —
ikincisi zaten yalnız saydamlık yapıyordu ama adı yana kayan bir hareketi anlatıyordu ve **yorum ile
kod çelişiyorsa kod düzeltilir, ad da koda dahildir**. Kalan tek ad ne yaptığını söylüyor.

- `.screen__column` → `fadeIn 200ms`
- `.empty` → `fadeIn 200ms`
- `slideIn` kullanan üç yer → `fadeIn`; 250ms olan **200ms**'e iner
- `.spinner` kuralı ve `spin` keyframe'i silinir; `FilePanel` yalnız "preparing…" yazar
- `.rail`'in `transition: width 220ms` kuralı **değişmez**

**Süre neden 200ms:** bant 140–220ms. 200ms bandın içinde, bugün zaten üç yerde kullanılan değer ve
rayın 220ms'siyle çakışmayacak kadar ondan ayrı. Tek bir değer seçmek, "her yüzey kendi süresini
yazar" hâlinin geri gelmesini engelliyor.

**Belge düzeltmesi:** `CODE-STANDARD.md` *"the four keyframes"* diyor; ikiye iniyor (`fadeIn`,
`blink`).

---

## 3 · Katman denetimi

`shared/app.css` (keyframe'ler), `workspace.css` (kullanımlar), `FilePanel.jsx` (gösterge). Yeni
bağ yok. Kural sıkışıyor: bir bileşenin kendi hareketini yazması zaten yasaktı, şimdi yazabileceği
ad da tek.

---

## 4 · Kabul ölçütü

1. `app.css` yalnız iki keyframe tanımlar: `fadeIn`, `blink`. `riseIn`, `slideIn` ve `spin` yoktur.
2. Hiçbir `animation` süresi 220ms'yi aşmaz; hepsi `fadeIn 200ms` (yanıp sönen noktalar hariç).
3. Hiçbir keyframe `transform` kullanmaz.
4. `.rail` genişlik geçişi 220ms'de durur.
5. `FilePanel` hazırlanırken "preparing…" yazar; dönen bir gösterge çizmez.

## 5 · Risk

`spin`'i silmek bir bilgi kaybı gibi görünebilir. Değil: düğmenin sözü ve `disabled` hâli aynı şeyi
söylüyor, ve bunun testi zaten var (`while it downloads the button says preparing and comes back
after`).
