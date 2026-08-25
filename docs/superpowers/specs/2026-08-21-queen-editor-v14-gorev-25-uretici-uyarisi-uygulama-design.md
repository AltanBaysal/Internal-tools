# v14 · Görev 25 — Uyarı kendi kartına geçiyor · **uygulama turu**

**Kaynak:** [test turu spec'i](2026-08-21-queen-editor-v14-gorev-25-uretici-uyarisi-testler-design.md) ·
commit `22db8af` (on test, sekizi kırmızı) · tasarım v4 fark listesi 38 · 5. ve 46. kararlar.

Kırmızı duran sekiz test ne istiyorsa o yazılıyor. Üç dosya ön yüzde. Motor açılmıyor.

## Tür kartı bir üretici satırı alıyor

`KindCard` bugün üç şey biliyor: hangi tür, kaç iş, ve motorun elinde olup olmadığı. Dördüncüsü
geliyor — **o türün üretici satırı**, `{ id, name, installed, note }`.

Kart, satırı `installed: false` görünce kendi içine iki şey ekliyor: tasarımın cümlesi
*"Üretici kurulu değil."* ve küçük bir **Kur**. Üretici adı ikinci kez yazılmıyor: kartın kendi
başlığı zaten "Ses · sırada" diyor.

`note` varsa o da aynı kartta okunuyor. Kur hiçbir şey kurmuyor — uygulamanın tek cevabı
*"Bu üretici Colab defterinden kurulur…"* ve o cevap satıra yazılıyor (`useProducers.install`).
Cümlenin düğmenin yanında durması, üretim panellerindeki `InstallCard`'ın da yaptığı şey.

**Soluklaşma üç hâle ayrılıyor.** Bugün iki hâl var: canlı kart vurgulu çerçeve, geri kalan
`opacity: .55`. Üçüncüsü doğuyor — sırasını bekliyor **ama söyleyecek bir şeyi var**. O kart
solmuyor, çünkü `.55`'te yazılmış bir uyarı okunmaz.

```
alive     → borderColor: accent
missing   → (olduğu gibi)
sırada    → opacity: .55
```

## Koşu kartı ikisini de bırakıyor

`waiting` dalından kurulum düğmesi ve `PRODUCER_NAME` sözlüğü çıkıyor; ikisi de tek bir türe ait ve
artık o türün kartında. Dalın geri kalanı — başlık, sayı, devam yolu ve *"Üretici kurulduktan sonra
kuyruğu sen sürdürürsün."* cümlesi — yerinde: onlar koşunun kendi hâli, ve fark 37 (26. madde) o
cümlenin üstüne yazacak.

## `producerReady` panelin içine iniyor

Panel artık satırların kendisini görüyor, dolayısıyla "bu türün üreticisi kurulu mu" sorusunu
kendisi cevaplayabiliyor:

```js
const producerReady = Boolean(waitingFor)
  && (producers || []).some((row) => row.id === waitingFor && row.installed);
```

Aynı cevabı hem satırlarda hem yanında taşınan bir bayrakta tutmak aynı kuralı iki sahipli yapardı.
Bayrak `ProjectScreen`'den ve `SidePanel`'in imzasından çıkıyor.

**Yorum da onunla taşınıyor.** `ProjectScreen`'de o hesabın üstünde duran paragraf iki şey
söylüyordu: 13 Ağustos 2026 kararı — bu ekranda hiçbir şey kendiliğinden başlamaz — ve devam
yolunun neden yalnız üretici geldiğinde gösterildiği. İkisi de artık `QueuePanel`'de, açıkladıkları
düğmenin yanında.

## Ne değişmiyor

- **Motor.** 46. karar; `queue.ORDER` ve sırayı koruyan testler yerinde, Python takımı 709.
- **Koşu kartının `waiting` başlığı ve devam cümlesi** — 26. madde.
- **Tür kartının başlığı ve büyük sayısının rengi** — 27. madde (fark 41, 42).
- **`InstallCard` ve üreticiler paneli** — kendi Kur'ları olduğu gibi.

## Bitti sayılır

Dört komut da yeşil: 384 / 474 / 709 / 541. Derlenmiş çıktı aynı commit'e giriyor.
