# v14 · Görev 27 — Kuyruk panelinin görsel hizalaması · **uygulama turu**

**Kaynak:** [test turu spec'i](2026-08-21-queen-editor-v14-gorev-27-kuyruk-hizalamasi-testler-design.md) ·
commit `c342b0a` (on bir test, onu kırmızı) · tasarım v4 fark listesi 41–47.

Kırmızı duran on test ne istiyorsa o yazılıyor. Tek dosya: `QueuePanel.jsx`.

## Tür kartı — başlık ve sayı

**Başlığın ayracı tire.** `·` → `—`, ve üçüncü bir hâl doğuyor:

```
alive   → "Foto — üretiliyor"
missing → "Ses — bekliyor"
sırada  → "Video — sırada"
```

"Bekliyor" 25. maddenin üstünde duruyor: kart üreticisinin kurulu olup olmadığını zaten biliyor.
"Sırada" bir sıranın geleceğini söylüyor; bu türün sırası makineye bir şey inmeden gelemez.

**Büyük sayı vurgu rengini bırakıyor.** Çalışan türünki `--ink`, geri kalanınki `--ink-3`. Vurgu
başlık satırında, noktanın yanında kalıyor. Üç kartın üç sayısı aynı yüksek sesle yazılınca panel
tek bir sayaca dönüşüyordu ve hangisinin kıpırdadığını söylemiyordu.

Ayraç yalnız **durum** satırında değişiyor. Hata kartının "2 foto · 1 video" dökümünde `·`
kalıyor: orası bir liste, bu bir durum.

## Koşu kartı — duraklatılırken ve bitince

**Duraklatılıyor.** Nokta atmaya devam ediyor — motor hâlâ dönüyor — ama vurgu renginden `--ink-3`'e
düşüyor; başlık da öyle. Vurgu "iş akıyor" demek, ve akış artık kesiliyor.

**Tamamlandı.** Başlık yeşil kalıyor, altındaki "n kare üretildi" `--ink-3`'e iniyor. İyi haberi
başlık taşıyor; sayı bir olgu, ikinci bir duyuru değil.

## Hata kartı

**Yazı "Tekrar dene".** "Hepsini" düşüyor.

**Kart yalnız kuyruk tamamlandığında doğuyor.** Bugün akarken de, duraklamışken de, durmuşken de
çiziliyor. Hâlâ büyüyen bir toplam toplam değil, ve kırmızı kareler galeride kendi "Tekrar dene"
düğmeleriyle zaten duruyor.

**Bedeli:** durmuş ya da duraklatılmış bir koşunun hataları panelde görünmüyor. Tasarımın "yalnız"
sözü bunu kapsıyor; farkın kendi *bugün* listesi duraklamış hâli de şikâyet ediyor.

## Boşaltma beklerken de var

`canClear`'a bekleme hâli ekleniyor. Koşulun kendisi değişmiyor: boşaltmak ancak ortada render
edilen bir kare yokken güvenli — bir işin satırı henüz kayda düşmemişken kuyruktan çekmek onu
işçinin altından almak olur. Kuyruk üreticisini beklerken motorun elinde iş yok.

## Ne değişmiyor

- **Ham çıktı kutusu** (fark 50) ve **onayın "kare" sözcüğü** (fark 48) — 47 ve 48. kararlar.
- **Bekleme kartının cümlesi ve kuyruğun kendiliğinden sürmesi** (fark 37) — 26. madde.
- **Motor.** Python takımı 709.

## Bitti sayılır

Dört komut da yeşil: 384 / 474 / 709 / 547. Derlenmiş çıktı aynı commit'e giriyor.
