# Madde 79 — Gönder düğmesi cevap akarken durdurmaya döner · **uygulama turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [test turu spec'i](2026-08-26-queenagent-m79-gonder-durdurmaya-doner-testler-design.md) ·
**Testler:** `60856ef` — ön yüzde 4 kırmızı.
**Tur:** ikiden ikincisi — bu belge **kodu** tarif eder. Test yazılmaz.

---

## Bir düğme, iki durum

`Composer` iki prop öğreniyor: `running` ve `onStop`. Düğmenin üç şeyi bu ikisine bakıyor:

| | Akmıyorken | Akarken |
|---|---|---|
| Yazısı | `action` (`Send` / `Start`) | `Stop` |
| Kapalı mı | Taslak boşsa evet | Hayır, hiçbir zaman |
| Basınca | `submit` | `onStop` |

`submit`'in kendisine dokunulmuyor. Basma yolu düğmenin üstünde ayrılıyor, içinde değil: `submit`
taslak kurallarının sahibi ve durdurmayı bilmesi gereken bir sebebi yok.

**Enter değişmiyor.** Akarken de gönderiyor, bugün olduğu gibi. Bu madde düğme hakkında; klavyenin
akarken ne yapacağı ayrı bir davranış sorusu ve açılmıyor. *(Test turunun kararı, burada yazılı
kalıyor çünkü koda bakan biri bunu bir eksiklik sanabilir.)*

## Vurgu neden kalıyor

CODE-STANDARD şöyle diyor: *vurgu birincil eylemi işaretler ve başka hiçbir şeyi.* Cevap akarken
elde olan tek eylem durdurmak — o an birincil eylem odur. Vurguyu düşürmek kuralı korumak değil,
kuralı yanlış okumak olurdu.

Bu, Madde 67'nin *"vurgu yok"* kararını **çürütmüyor**: o karar ayrı bir düğme içindi, ve ayrı bir
düğme birincil eylem değil ikinci bir seçenekti. Düğme birleşince durum da değişti.

67'nin *"kırmızı değil"* kararı duruyor ve dokunulmuyor — kendi cevabını kesmek yıkıcı bir iş
değil.

## Silinenler

- `ChatScreen`'in `foot`undaki ayrı `Stop` düğmesi.
- `workspace.css`'teki `.stop` ve `.stop:hover`.

İkinci bir yol bırakmak, aynı işi iki yerden yapılabilir kılardı — ve ikisinden biri bir gün
ötekinden farklı davranırdı.

`ChatScreen`'in `onStop`'u duruyor: artık `Composer`'a geçiyor, `foot`a değil.

## Kapsam dışı

Durdurmanın arka ucu · yarım metnin saklanması · kendiliğinden yeniden başlamama *(hepsi 67 ve
hepsi duruyor — iki testi bilerek dokunulmadan bırakıldı, ve yeşil kalmaları bu maddenin kanıtı)* ·
proje ekranının yazma kutusu *(orada akan bir cevap yok — sohbet henüz doğmamış, yani `running` hiç
gelmiyor)*.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur.** Ön yüzde **502**, hepsi yeşil. Arka uçta **2 failed, 442 passed** — ikisi
defterin dalı, ve bu koşunun sonunda defter `main`'e çevrilince ikisi de yeşile döner.

`dist` **kaynağıyla aynı commit'te** derleniyor.
