# Madde 287 · Ekran her adımı adıyla ve süresiyle söyleyecek — test turunun tasarımı

**Tarih:** 21 Eylül 2026 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Kurallar:** [FOUNDATION](../../../queen-editor/FOUNDATION.md) ·
[CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

**Hiçbir şey.** İstek kullanıcının kendi cümlesi *(21 Eylül — "daha açıklayıcı mı yazsak mesajı,
ben de anlarım neyin yavaş olduğunu", "neye zaman harcadığımızı görürüz")*.

## Bugünkü durum, koddan

Ekran export'un durumunu **tek bir alandan** okuyor: `state`. Bugün beş değeri var — `idle`,
`running`, `merging`, `done`, `error` — ve ekran ikisini cümleye çeviriyor
*([ExportScreen.jsx:195](../../../queen-editor/frontend/src/features/photo_generation/ExportScreen.jsx#L195))*:
`merging` → *"Disclaimer ekleniyor…"*, gerisi → *"N / M yazıldı…"*.

**Bugünkü boşluk somut, ve iki tane:**

- **282 bir adım açtı, adı olmayan:** birleştirme bitip dosya Drive'a kopyalanırken `state` hâlâ
  `merging`, yani ekran *"Disclaimer ekleniyor"* diyor. En çok merak edilen adım **yanlış isimle**
  görünüyor.
- **289 bir adım daha açtı:** fotoğraflar artık kendi geçişinde yazılıyor, ve ekran o sırada
  `N/N yazıldı…`'da bekliyor. O maddenin spec'i bu boşluğu adıyla bu maddeye bıraktı.

Ve hiçbir adım **ne kadar sürdüğünü** söylemiyor. 255 adı verdi; bu madde **süreyi** veriyor, ve
fark şu: ad nerede olunduğunu söyler, süre **hangisinin pahalı olduğunu**.

## Tasarım kararı 1: adım `state`'in kendisi, ikinci bir alan değil

`state` zaten *"şu anda hangi adımdayız"* sorusunun cevabı. İki yeni değer ekleniyor:

| `state` | Adım |
|---|---|
| `running` | videolar kesiliyor |
| `photos` | fotoğraflar Drive'a yazılıyor *(yeni)* |
| `merging` | birleştirme + disclaimer *(255'in cümlesi burada)* |
| `saving` | birleşmiş dosya Drive'a kopyalanıyor *(yeni)* |

**İkinci bir `step` alanı açılmıyor:** aynı soruya iki cevap, ikisini birbirine uydurmak zorunda
kalmak demek.

**`merging` yeniden adlandırılmıyor.** Anahtar işin ne olduğunu söylüyor *(birleştirme)*, ekranın
cümlesi ise **süreyi yiyeni** söylüyor *(disclaimer)* — 255'in kararı, ve o karar bu maddede
değişmiyor.

**Bunun getirdiği bir düzeltme var, ve gözden kaçarsa hata olurdu:** `ExportRunner.start` ikinci
koşuyu *"state `running` ya da `merging` ise"* diye reddediyor. Yeni değerlerle bu liste eksik
kalır — yani `photos` evresindeyken **ikinci bir export başlatılabilirdi**. Soru tersine çevriliyor:
**meşgul = dinlenmiyor**, yani `idle`, `done`, `error` dışındaki her şey. Büyüyen bir liste yerine
tamamlayanı.

## Tasarım kararı 2: saati koşucu tutuyor

Süreyi **`ExportRunner` ölçüyor**, `run_export` değil. Sebebi: adımın ne zaman başladığını ve
bittiğini bilen tek şey **durum değişikliği**, ve durumu tutan yer orası. `run_export`'a bu
maddede eklenen tek şey iki `report` satırı.

**Kural tek cümle:** durum değiştiğinde, biten adım — dinlenme durumlarından biri değilse — kendi
süresiyle `steps`'e yazılır. Yeni durum `idle` ise `steps` sıfırlanır: iptal edilen bir koşunun
adımları ekranda durmaz.

**Saat dışarıdan veriliyor** *(`clock`, varsayılanı `time.monotonic`)*, çünkü testin bir saniye
beklemesi kabul edilemez — deponun kuralı. `monotonic`: duvar saati geri alınabilir, geçen süre
alınamaz.

**`steps` bir demet, liste değil.** `state()` her okumada sığ kopya veriyor; paylaşılan bir liste
okuyanın elinde değişebilirdi. Değişmez bir demet bu soruyu tamamen kaldırıyor.

**FOUNDATION 4:** arka uç ölçüyor ve **anahtar + saniye** bildiriyor; hangi cümlenin görüneceği ve
sayının nasıl biçimleneceği ekranın işi.

## Tasarım kararı 3: tekli export de adımlarını söylüyor

Yol haritasının satırı *"tekli export'a dokunulmuyor — orada tek adım var"* diyor. **O gerekçe
289'da doldu:** tekli export de artık önce videoları, sonra fotoğrafları yazıyor. Aynı iki
`report` satırı iki modda da koşuyor, yani:

- Kod **daha basit** — modu soran bir dal yok.
- Ekran **doğru** — tekli export fotoğrafları yazarken *"N/N yazıldı…"* demiyor.

Kullanıcının istediği şey zaten buydu: *"neyin yavaş olduğunu ben de anlarım"*. Mod ayrımı o
isteğe hizmet etmiyordu, yalnız 289'dan önceki dünyayı anlatıyordu.

## Çivilenen olgular

**1 · Birleşik koşu dört adımı sırayla bildiriyor:** `running → photos → merging → saving → done`.

**2 · Biten her adım kendi süresini bırakıyor.** Sahte bir saatle, `steps` bitişte dört girdi:
`{"step": "running", "seconds": …}`, `photos`, `merging`, `saving` — sırasıyla, ve süreler saatin
verdiği farklar.

**3 · Drive'a kopyalama kendi adımı.** 282'nin açtığı boşluk: `merging` bittikten sonra ekran
artık *"Disclaimer ekleniyor"* demiyor.

**4 · Tekli koşu iki adım bildiriyor:** `running`, `photos` — ve `merging`/`saving` hiç yok.

**5 · Yeni durumlar da meşgul sayılıyor.** `photos` evresindeki bir modda ikinci bir export
reddediliyor.

**6 · İptal adımları siliyor.** `idle`'a dönen bir koşunun `steps`'i boş.

**7 · Saat adım başına bir kez okunuyor**, kare başına değil: 22 karelik bir koşuda saat sayısı
adım sayısı kadar.

**8 · Ekran yeni iki durumu kendi cümlesiyle söylüyor:** `photos` → *"Fotoğraflar ekleniyor…"*,
`saving` → *"Drive'a kopyalanıyor…"*, ve ikisinde de düğme basılamıyor.

**9 · Ekran biten adımları adıyla ve süresiyle listeliyor.** Türkçe adlar ve `12,4 sn` gibi
saniyeler — ondalık ayıracı virgül, çünkü okuyan kişi Türkçe okuyor.

**10 · `merging` hâlâ *"Disclaimer ekleniyor…"* diyor** *(255 yerinde)*, ve tekli export'ta o
cümle hiç çıkmıyor *(261 yerinde)*.

## Ayarlanan test

`test_the_state_counts_what_has_been_written` durum sözlüğünün **tamamını** karşılaştırıyor, ve
`steps` yeni bir alan. Testin kendi sorusu *"sayaç ne yazdı"*; cevabı değişmiyor, sözlüğe alan
ekleniyor — o yüzden **ayarlanıyor, silinmiyor**.

## Kapsam dışı, ve bilerek

**Yüzde, ve ffmpeg çıktısını ayrıştırmak.** 255'te sebebiyle reddedildi, ve bu madde ona hiç
girmiyor: adımların etrafına saat koymak, `subprocess.run`'ın bekleme biçimini değiştirmiyor.

**Dakika-saniye biçimi.** `312,7 sn` okunuyor, ve karşılaştırmak için zaten en iyi biçim —
kullanıcının sorusu *"hangisi pahalı"*, *"saat kaç"* değil.
