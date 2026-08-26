# Madde 79 — Gönder düğmesi cevap akarken durdurmaya döner · **test turu**

**Tarih:** 2026-08-26 · **Branch:** `feat/queenagent-v5` ·
**Kaynak:** [v5 yol haritası](../plans/2026-08-25-queenagent-v5-roadmap.md), Madde 79 ·
**Tur:** ikiden birincisi — bu belge yalnız **testleri** tarif eder.

---

## Ne kanıtlanacak

Madde 67 durdurmayı getirdi ve çalışıyor. Ayrı bir düğme olması beğenilmedi *(kullanıcı,
26 Ağustos)*: cevap akarken gönderilecek bir şey yok, yani gönder düğmesi zaten ölü duruyor ve
yanına ikinci bir düğme geliyor.

İki iddia:

1. Cevap akarken yazma kutusunda **tek bir eylem düğmesi** var ve durdurmayı söylüyor.
2. Durdurmanın kendisi **değişmiyor** — 67'nin arka ucu, yarım metni saklaması, kendiliğinden
   yeniden başlamaması aynen duruyor.

İkincisi bu maddenin bütün riski. Görünen şeyi değiştirirken çalışan şeyi bozmamak, ve bunu
söyleyen testlerin zaten var olması.

## Düğme kimin

Bugün gönder düğmesi `Composer`'ın içinde, durdurma düğmesi ise dışarıdan `foot` olarak
geliyor — yani aynı satırda duran iki düğmenin sahibi iki ayrı yer.

Düğme `Composer`'a kalıyor, çünkü düğme zaten onun. İki durumu olan bir kontrolün iki durumu da
aynı yerde yaşar; ikisini iki sahibe bölmek, "hangisi görünür" sorusunu üçüncü bir yere taşırdı.

`Composer` iki şey öğreniyor: **bir cevap akıyor mu**, ve **durdurulmak istenirse ne çağrılacak**.

## Karara bağlananlar

**Akarken düğme her zaman basılabilir.** Boş taslak gönderimi engelliyor; durdurmayı engellemesi
saçma olurdu — durdurulacak şey taslak değil, akan cevap.

**Vurgu kalıyor.** CODE-STANDARD'ın kuralı *"vurgu birincil eylemi işaretler ve başka hiçbir şeyi"*.
Cevap akarken elde olan tek eylem durdurmak, yani o an birincil eylem odur. Vurguyu düşürmek kuralı
korumak değil, kuralı yanlış okumak olurdu. 67'nin *"kırmızı değil"* kararı duruyor: durdurmak
yıkıcı bir iş değil.

**Yazma kutusu ve Enter dokunulmuyor** *(bilerek)*. Bu madde düğme hakkında. Akarken yazmaya devam
etmek ve Enter'ın ne yapacağı ayrı bir davranış sorusu, ve bugünkü cevabı değişmiyor.

**Ayrı `Stop` düğmesi ve `.stop` stili siliniyor.** İkinci bir yol bırakmak, aynı işi iki yerden
yapılabilir kılardı.

## Yazılacak testler

### `Composer.test.jsx` — dört test

Bir cevap akarken düğme durdurmayı söylüyor. Akarken taslak boş olsa da basılabiliyor ve basınca
kendisine verilen yol çağrılıyor. Akarken basmak mesaj **göndermiyor** — iki iş tek düğmede, ve
yanlış olanı çalışırsa kullanıcı yazmadığı bir şeyi göndermiş olur. Akmıyorken hiçbir şey
değişmiyor: düğme eylem adını söylüyor ve boş taslakta kapalı.

### `ChatScreen.test.jsx` — bir yeni, iki duran

**Yeni:** cevap akarken yazma kutusunun altı `Skills`, model ve **tek** bir eylem düğmesi taşıyor,
ve o düğme durdurmayı söylüyor. Dördüncü bir düğme yok. Bu maddenin tek cümlelik kanıtı.

**Duranlar:** *"akan cevap durdurulabiliyor"* ve *"boştayken durdurulacak bir şey yok"* aynen
kalıyor. İkisi de düğmeyi adıyla arıyor, sahibini değil — yani davranışı soruyorlar, yerini değil,
ve bu maddeden sonra da doğru cevabı almalılar. **Değişmeden yeşil kalmaları bu maddenin
kanıtı**: görünen değişti, çalışan değişmedi.

## Kapsam dışı

Durdurmanın arka ucu · yarım metnin saklanması · kendiliğinden yeniden başlamama *(hepsi 67, ve
hepsi duruyor)* · akarken yazmaya devam etmek · Enter'ın akarken ne yapacağı · proje ekranının
yazma kutusu *(orada akan bir cevap yok — sohbet henüz doğmamış)*.

## Nasıl kırmızı görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**Ayrı ayrı koşulur** — aynı anda koşturulduklarında vitest bu makinede zaman aşımına düşüyor.

Arka uca dokunulmuyor: bugünkü iki kırmızısı defterin dalı ve öyle kalıyor.

Yeni ad doğmuyor: `Composer` iki prop kazanıyor, ve React tanımadığı prop'u sessizce yok sayar.
