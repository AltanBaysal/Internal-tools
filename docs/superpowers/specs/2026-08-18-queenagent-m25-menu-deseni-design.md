# Madde 25 — Menü deseni · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 25](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 36, 67, 68 · karar 11 · `HANDOFF.md` §6, §9
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 0 · Kaynak düzeltmesi

Yol haritası bu maddeye **fark 35** ve **karar 4**'ü de yazmış. İkisi de buraya ait değil:

- **fark 35** model düğmesinin composer içindeki yeri; onu çözen **karar 1**'dir (sağ alt: Skills ·
  model · Send) ve ikisi de **Madde 26**'nın işidir. Madde 26 fark 35'i saymıyor — kaybolmasın diye
  buraya yazıldı.
- **karar 4** sohbet yeniden adlandırmanın kalkması; menülerle ilgisi yok. Yazım hatası kabul edildi.

Bu maddenin gerçek kaynağı: fark 36 (kutunun ekrana sığması), fark 67 (Esc sırası), fark 68 (dışa
tıklama), karar 11 (azami yükseklik + kendi içinde kayma).

---

## 1 · Tek menü, üç çağıran

Bugün uygulamada tek bir açılır menü var: kenar çubuğu satırının ⋯ menüsü (`RowMenu`). Madde 26 model
menüsünü, Madde 27 Skills menüsünü getirecek. Üçü **aynı kutu** olacak, o yüzden kutu burada ortak
hâline getiriliyor ve adı da öyle oluyor: `RowMenu` → `Menu`, `.row-menu` → `.menu`.

Ortak olan: konum, azami yükseklik, yakalayıcı, öğe biçimi. **Genişlik ortak değil** — satır menüsü
176px (`HANDOFF.md` §6), composer menüleri kendi ölçülerini 26 ve 27'de getirir. Kutu genişliği
dayatmıyor.

---

## 2 · Nereye açılır (fark 36, karar 11)

Sözleşmenin iki hâli çelişiyordu; karar 11 ikisini de reddetti. Kural:

| | Kural |
|---|---|
| Yatay | tetikleyicisine **sağdan** hizalanır; pencereden taşarsa içeri çekilir |
| Dikey | tetikleyicinin **altına** açılır; sığmıyorsa **çevrilmez, yukarı kaydırılır** |
| Yükseklik | azami yüksekliği vardır ve aşarsa **kendi içinde kayar** |

Çevirme yok, çünkü karar 11 çevirmeyi gerektiren durumun hiç oluşmadığını söylüyor: composer her boyda
ekranın altına sabit, üstünde her zaman ekran var. Geriye kalan tek iş sığdırmak.

Hesap **saf bir işlev** olarak `shared/menuPlacement.js`'te duruyor: dikdörtgen alır, sayı verir.
jsdom'un yerleşim motoru olmadığı için aritmetiği ancak böyle kanıtlanabilir; bileşen o sayıları
uygular.

**Sayılar:** tetikleyiciyle arası 6px, pencere kenarına en fazla 8px yaklaşır, azami yükseklik
**320px**. Üçü de tasarımdan gelmiyor — karar 11 "azami yükseklik olsun" diyor, sayıyı vermiyor. 320,
dört satırlık model menüsünün (açıklamalarıyla) sığdığı, kısa bir pencerede ise kaymaya düştüğü
yükseklik. Madde 35 gözü üstlenir.

---

## 3 · Dışa tıklama bir yakalayıcıdır (fark 68)

Bugün menü `document`'e bir `mousedown` dinleyicisi asıyor. Tasarım ekranı kaplayan **görünmez bir
yakalayıcı** istiyor ve ikisi aynı şey değil:

| | Dinleyici (bugün) | Yakalayıcı (tasarım) |
|---|---|---|
| Menü kapanır | evet | evet |
| Tıklama altındakine de ulaşır | **evet** | hayır |

Yani bugün menü açıkken bir düğmeye basmak hem menüyü kapatıyor hem düğmeye basıyor. Yakalayıcıyla
ilk tıklama yalnız menüyü kapatıyor. Tasarımın istediği bu; onay kutusunun karartısı da zaten böyle
çalışıyor — uygulamada tek bir "dışarı tıkladın" dili oluyor.

Yakalayıcının ekranı kapladığı **CSS kilidiyle** kanıtlanıyor (`position: fixed; inset: 0`); jsdom
geometriyi bilmediği için "altındakine ulaşmadı" bir birim testiyle dürüstçe yazılamaz. Madde 35 gözü.

---

## 4 · Esc sırası (fark 67)

Tasarımın sırası: proje ⋯ menüsü → onay kutusu → Skills → model → açık panel.

Bugün App'in **tek** dinleyicisinde bu sıranın var olan üçü duruyor (⋯ → onay → panel) ve doğru.
Skills ile model menüleri henüz doğmadı; **olmayan bir şey sıraya yazılmaz.** Madde 26 model
menüsünü, Madde 27 Skills'i sıraya kendi maddesinde ekler — sıra korunur, zincir tek yerde kalır.

⌘K'nın bağlandığı bir şey kalmaması (fark 67'nin öteki yarısı) Faz 1'de kapandı; testi duruyor.

---

## 5 · Katman denetimi

Yeni: `shared/menuPlacement.js` (saf, React yok, DOM yok — `shared/`'ın kuralına uyar).
Değişen: `Menu.jsx` (`RowMenu.jsx`'ten ad değiştirdi), `Sidebar.jsx` (tetikleyiciyi menüye verir),
`workspace.css`. App'in durumu değişmiyor: menünün **nereye** asıldığı bir sunum ayrıntısı, o yüzden
tetikleyici Sidebar'ın kendi ref'inde durur, App'e çıkmaz.

---

## 6 · Kabul ölçütü

1. Menü tetikleyicisine sağdan hizalanır.
2. Pencereden taşacaksa içeri çekilir; altına sığmıyorsa yukarı kayar, çevrilmez.
3. Azami yüksekliği vardır ve aşarsa kendi içinde kayar.
4. Ekranı kaplayan görünmez bir yakalayıcı dışa tıklamayı yakalar ve menüyü kapatır.
5. Menü klavyeyi kendine almaz; Esc App'in tek dinleyicisinde kalır.
6. Kutunun adı ortaktır (`Menu`, `.menu`) ve genişlik dayatmaz.

## 7 · Risk

6/8/320 tasarımdan gelmiyor. Yakalayıcının gerçekten yakaladığı ve menünün kısa pencerede taşmadığı
gözle Madde 35'te doğrulanır.
