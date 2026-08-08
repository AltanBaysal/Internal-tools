# Queen Editor v4 · Madde 2 — Panel üçe ayrılır

**Tarih:** 2026-08-08 · **Yol haritası:**
[v4 Madde 2](../plans/2026-08-08-queen-editor-v4-roadmap.md) · **Kapsadığı kodlar:** P1, P2, P3,
P28, P29 · **Katman:** yalnız ön yüz

## Amaç

Sağ sütun tek bir yüzey olmaktan çıkıp **üç panel + bir ikon şeridi** oluyor. Bu maddenin işi
yalnız **iskelet**: şerit, panel geçişi, başlıklar ve genişlik. Panellerin içeriği sonraki
maddelerde yazılıyor.

Bugün durum bilgisi (ilerleme, duraklama, durma, bitiş, yarım kalma) formun hemen altında duruyor.
Tasarımda formun altında **hiçbir durum kartı yok**; hepsi kuyruk panelinde. Bu madde o blokları
**taşıyor** — içeriklerine dokunmuyor, çünkü Madde 4 onları zaten baştan yazacak ve şimdi yeniden
yazmak aynı kartı iki turda elden geçirmek olur.

## Kapsam

**İçinde:** ikon şeridi ve panel geçişi; üç panelin başlığı; sağ sütunun 368 piksele çıkması; durum
bloklarının kuyruk paneline taşınması; bugün iki iş yapan `GeneratePanel`'in üçe bölünmesi.

**Dışında:** formun kendi değişiklikleri — buton adı, kilidin kalkması, yeşil onay kartı (Madde 3);
kuyruk panelinin yeni dili — tek sayı, canlı nokta, Duraklat, Kuyruğu boşalt (Madde 4); agent
panelinin içeriği (tasarım bilerek boş bırakıyor).

---

## 1 · Sağ sütunun yapısı

Şerit **panelin sağ kenarında** durur — tasarımın sözü bu, yani ekranın en sağ kenarındaki dikey
çubuk şerittir, panel onun solunda kalır.

| Parça | Genişlik |
|---|---|
| Panel gövdesi | 320 px (bugünkü değer, değişmiyor) |
| İkon şeridi | 48 px |
| **Toplam sağ sütun** | **368 px** |

Şerit yukarıdan aşağı üç ikon taşır. **Aktif ikon vurgu rengindedir ve sağında dikey bir çizgi
belirir**; aktif olmayanlar soluk yazı renginde durur. Şeridin solunda panelle arasında bugünkü
ince ayırıcı çizgi kalır.

İleride yeni bir panel eklemek şeride bir ikon eklemek demektir — bileşen bunu üç eleman varsayarak
değil, bir liste üzerinden çizerek yapar.

## 2 · Üç panel ve başlıkları

| Sıra | Panel | Başlık | İçeriği |
|---|---|---|---|
| 1 | Üretime ekle | `ÜRETİME EKLE` | Prompt listesi, negatif, varyant, ana buton |
| 2 | Kuyruğu takip et | `KUYRUĞU TAKİP ET` | Bugünkü durum blokları, taşınmış hâliyle |
| 3 | AI agent | `AI AGENT` | Ortada tek satır: "Agent buradan çalışacak." |

Başlıklar panelin var olan alan etiketleriyle **aynı dilde** yazılır: küçük punto, büyük harf,
harf aralıklı, soluk yazı rengi. Ayrı bir tipografi icat edilmez.

## 3 · Hangi panel açık

Açılışta **Üretime ekle** paneli açıktır. Panel yalnız şeritteki ikona basılarak değişir; bu
maddede kendiliğinden geçiş yoktur.

Gerekçe: tasarımda ekleme onayı (yeşil "kuyruğa eklendi" kartı) form panelinin **kendi içinde**
duruyor, yani kullanıcı ekledikten sonra panel değiştirmek zorunda değil. Kendiliğinden geçiş bu
yüzden gerekmiyor.

Hangi panelin açık olduğu sağ sütunun kendi bilgisidir; proje ekranına ya da sunucuya taşınmaz.

## 4 · Ne taşınıyor, ne taşınmıyor

Bugün form panelinin altındaki dört blok — yarım kalan koşu, duraklatılmış koşu, akan koşu
(ilerleme kartı + Durdur), boşta hâli (Üret butonu + bitiş/hata/önizleme kartları) — ikiye ayrılır:

- **Ana buton** (Üret / Devam et / Kaldığı yerden devam et) ve **alan hataları** form panelinde
  kalır.
- **Durum kartları** kuyruk paneline geçer: ilerleme kartı, duraklatıldı kartı, durdu kartı,
  tamamlandı kartı, bağlantı hatası kartı ve "başka projede üretim sürüyor" satırı.

> **Geçiş dönemi, bilerek.** Bu bölünme sonrası ana buton bir panelde, sonucun kartı başka
> panelde durur. Tasarımın son hâli bu değil (Madde 4'te Duraklat/Devam et kuyruk paneline
> geçiyor, Madde 3'te ekleme onayı form paneline yerleşiyor); ama ikisi de kendi maddesinin işi ve
> kullanıcı testi zaten en sonda.

## 5 · İkonlar

Tasarım şeridin **davranışını ve ölçüsünü** yazıyor, üç panelin **adını** veriyor; ikon
çizimlerini vermiyor. Üç ikon bu yüzden bizim kodumuzda çizilir — `vendor/` birebir kopya olduğu
için oraya yeni ikon eklenmez. Çizimler var olan ikon dilini izler: 14×14 kutu, `currentColor`,
1.4–1.6 kalınlıkta çizgi, yuvarlatılmış uç.

| Panel | İkon |
|---|---|
| Üretime ekle | artı |
| Kuyruğu takip et | üst üste üç yatay çizgi (liste) |
| AI agent | konuşma balonu |

## 6 · Dosya bölünmesi

`GeneratePanel.jsx` bugün 250 satır ve iki iş yapıyor: formu çiziyor **ve** koşunun bütün
durumlarını anlatıyor. Bu maddede bölünüyor — kural gereği ("bağlamda rahat tutulamayacak kadar
büyüyen dosya çok iş yapıyordur"), ve zaten panel ayrımı tam bu sınırdan geçiyor.

| Dosya | İşi |
|---|---|
| `SidePanel.jsx` (yeni) | Sağ sütun: şerit, hangi panelin açık olduğu, başlık |
| `GeneratePanel.jsx` | Yalnız form ve ana buton |
| `QueuePanel.jsx` (yeni) | Yalnız durum kartları |
| `AgentPanel.jsx` (yeni) | Boş panel |

`ProjectScreen.jsx` artık `GeneratePanel` değil `SidePanel` çiziyor ve aynı özellikleri ona
veriyor.

## 7 · Testler

`npm test` (vitest + jsdom). Yeni ve değişen testler:

**Şerit**
- Üç ikon çıkıyor ve her birinin erişilebilir adı panelin adı.
- Açılışta form paneli görünüyor, kuyruk paneli görünmüyor.
- Kuyruk ikonuna basınca kuyruk paneli görünüyor, form paneli kayboluyor.
- Aktif ikon vurgu rengini taşıyor (sınıf ya da `aria-current` ile), diğerleri taşımıyor.

**Panellerin işi ayrık**
- Akan koşuda ilerleme kartı **form panelinde çıkmıyor**, kuyruk panelinde çıkıyor.
- Alan hatası (format hatası) form panelinde, kutunun altında kalıyor.
- Agent paneli tek satırlık metnini gösteriyor.

**Taşınan davranış bozulmuyor**
- `GeneratePanel.test.jsx`'in bugünkü durum senaryoları `QueuePanel.test.jsx`'e taşınır ve aynı
  cümleleri doğrular; formla ilgili olanlar yerinde kalır.

## 8 · Kabul kriteri

`npm test` yeşil, `pytest` yeşil (arka uca dokunulmuyor) ve şu üç cümle testlerle kanıtlanmış:

1. Sağ sütunda üç ikon var, basınca panel değişiyor ve aktif ikon işaretli.
2. Akan bir koşuda ilerleme kartı form panelinde değil, kuyruk panelinde.
3. Agent paneli açılıyor ve bilerek boş.

Ön yüz değiştiği için `npm run build` koşulur ve üretilen `dist/` aynı commit'e girer.
