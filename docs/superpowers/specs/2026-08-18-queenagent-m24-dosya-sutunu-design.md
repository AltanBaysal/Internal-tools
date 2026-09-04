# Madde 24 — Panel açıkken dosya sütunu kalkar · Tasarım Belgesi

**Tarih:** 2026-08-18 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 24](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynak:** fark 61 · `HANDOFF.md` §2, §8
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 1 · Aynı liste iki yerde durmaz

Bugün proje ekranında bir dosya açılınca ızgara tek sütuna iniyor ama dosyalar sütunu **kayboluyor
değil, altına iniyor**: sağda panel dosyayı gösterirken solda aynı listenin kendisi duruyor.

Bundan sonra panel açıkken dosyalar sütunu **hiç çizilmiyor**. Solda kalanlar: başlık satırı,
composer, sohbet listesi.

Izgara yine de tek sütun kuralını taşıyor — tek çocuk kaldığında ikinci ray 320px'lik boş bir şerit
olarak durur ve sohbet sütununu daraltırdı. Modifier kalıyor, **gerekçesi değişiyor**: sütun aşağı
inmiyor, yok.

---

## 2 · Neden sohbet rayında tam tersi oldu

Madde 22'de (fark 53) sohbetin rayı bir dosya açıldığında listesini **bırakmadı**. Burada sütun
kalkıyor. Çelişki değil, iki farklı yüzey:

| | Sohbet rayı | Proje ekranı |
|---|---|---|
| Okuyucu nerede | rayın kendi içinde, genişlemiş hâli | ızgaranın yanında ayrı bir yüzey |
| Liste kalırsa | rayın **tek** listesi, okuyucunun komşusu | ekranda **ikinci** liste, panelin kopyası |

Rayda liste okuyucuya komşudur; proje ekranında liste panelin yanında ikinci bir kopya olur. Kural
tek: aynı liste ekranda iki kere durmaz.

---

## 3 · Sütunla birlikte giden şeyler

- **Silme.** Dosya satırındaki `×` o sütunda; sütun yokken silinecek bir satır da yok. Panel
  kapanınca geri gelir.
- **Silme hatası satırı.** `file-list__error` de o sütunda duruyor. Panel açıkken bir silme
  başlatılamayacağı için yeni bir hata doğamaz; açılmadan önce doğmuş bir hata ise dosya açılırken
  gider. Kabul ediliyor: bir dosyayı açmak o işten devam etmek değil, ondan sonrasına geçmektir.
- **Madde 21'in seçili satırı.** Proje ekranında okunan dosyanın satırı artık hiç çizilmiyor, o
  yüzden işaretlenecek bir şey de yok. Kural sohbet rayında duruyor (Madde 22) ve orada görünüyor.

Boş liste satırı ("No files yet…") da sütunla gider — sütun yokken öğretecek bir yer yok.

---

## 4 · Katman denetimi

Yalnız `ProjectScreen.jsx` ve `workspace.css`'teki bir yorum. Yeni bileşen, yeni durum, arka uç yok.
Panelin kendisi Madde 23'te bitti.

---

## 5 · Kabul ölçütü

1. Panel açıkken "Files QueenAgent created" başlığı ve altındaki liste çizilmez.
2. Solda başlık satırı, composer ve sohbet listesi kalır.
3. Panel kapanınca sütun geri gelir.
4. Izgara panel açıkken tek sütundur.

## 6 · Risk

Yok. Fark "zayıf sinyal" ama sözleşmenin "ızgara tek sütuna iner" cümlesi elle doğrulanmış ve
ayakta kalan sütunun sohbetler olduğu fark 61'de yazılı.
