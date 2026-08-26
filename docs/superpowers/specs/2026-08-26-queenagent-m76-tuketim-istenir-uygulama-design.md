# Madde 76 — Token gerçekten görünür · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [test turu spec'i](2026-08-26-queenagent-m76-tuketim-istenir-testler-design.md) ·
**Testler:** `f8f0e1b` — bu maddeden iki kırmızı *(defterin iki kırmızısı ayrı)*.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder. Test yazılmaz.

---

## İki satır kod, üç yalan

Değişen davranış iki yere sığıyor. Onların yanında, artık doğru olmayan üç yorum var ve bu turda
düzeliyorlar — CODE-STANDARD'ın kuralı: *çelişkide yorum koda uydurulur.*

### 1. İstek sayıyı istiyor

`XaiClient.stream`, gövdeye `stream` bayrağını koyduğu yerde `stream_options`'ı da koyuyor. İkisi
aynı cümlede doğuyor çünkü ikisi aynı kararın parçası: **bu bir akış, ve akışın sonunda hesabı
istiyoruz.**

`complete` dokunulmuyor. Ortak `_request` gövdesine konsaydı akmayan istek de taşırdı, ve
desteklemeyen bir uç nokta bunu 400 ile reddeder.

### 2. Boş kare konuşmayan kare sayılıyor

`_spoken`, `choices`'ı listenin ilk elemanı olduğu varsayımıyla okuyor. Kapanış karesinde o liste
boş. Okuma, **boş listeyi de bir boşluk sayacak** hâle geliyor — bugün boş `delta`'yı saydığı gibi.

Bu satır sayıyı kurtarmıyor; **cevabı** kurtarıyor. Bugünkü hâliyle o kare `IndexError` atıyor,
`stream_answer` onu `EngineFailed`'a çeviriyor ve turun tamamı çöpe gidiyor — söylenen her kelime
dahil.

### 3. Üç yorum düzeliyor

| Nerede | Bugün ne diyor | Neden yanlış |
|---|---|---|
| `client.py` → `_spent` docstring | "servis her karede söylüyor, o yüzden kapanıştan değil karelerden okunuyor" | Yalnız kapanışta söylüyor, ve ancak istenirse |
| `ports.py` → `Engine.stream` | "birden çok kez söyleyebilir, her biri koşan toplam" | Bir kez söylüyor |
| `stream_answer.py` → toplama yorumu | "tur içinde motor koşan toplamı tekrarlıyor" | Tekrarlamıyor; tek bir sayı geliyor |

## Kod değişmeyen yer: toplama kuralı

*Tur içinde en sonuncu geçerli, turlar arasında toplanır* kuralı **aynen kalıyor**, ve bu bilinçli:

- **Tur içinde en sonuncu** — bugün zaten tek bir sayı geliyor, yani kural boşta çalışıyor. Ama
  servis yarın kümülatif dizisine dönerse doğru cevabı vermeye devam ediyor. Kaldırmak, kazancı
  olmayan bir kırılganlık alışverişi olurdu.
- **Turlar arasında toplanır** — hâlâ tam olarak gerekli. On altı turluk bir cevap on altı ayrı
  akış, on altı ayrı kapanış karesi, on altı ayrı fatura.
- **Durdurmadan önce katlanıyor** — hâlâ doğru. Pratikte nadiren bir şey yakalıyor, ama yakaladığı
  şey gerçekten ödenmiş.

Değişen yalnız bu kuralın **gerekçesi**, ve gerekçe yorumda yazılı.

## Kapsam dışı

Ön yüz *(çiziyor, testleri yeşil)* · 68'in spec'lerinin geriye dönük düzeltilmesi *(o günün kaydı;
düzeltme yol haritasında ve bu iki spec'te)* · `stream_options` reddedilirse yedek bir yol
*(referans destekliyor; reddederse hata servisin kendi sözleriyle geliyor — tahmin edilmiş bir sebep
basılmıyor)* · defterin dalı *(kullanıcının denemesi bitince `main`'e döner)*.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Arka uçta **2 failed, 432 passed** — kalan iki kırmızı defterin dalı, bu maddenin değil. Ön yüzde
**489**, dokunulmadığı için değişmiyor.

`dist` derlenmiyor: ön yüz kaynağında tek satır değişmiyor.
