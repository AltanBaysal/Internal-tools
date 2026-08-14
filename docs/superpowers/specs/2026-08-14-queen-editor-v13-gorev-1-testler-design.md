# v13 Görev 1 — Galeri resimleri sunucuyu aç bırakıyor: TEST döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v13](../plans/2026-08-14-queen-editor-v13-roadmap.md) · **Döngü:** 1/2
**Bu döngüde mantık yazılmıyor** — testler, ve testlerin koşabilmesi için boş iskelet. Takım kırmızı
commit'leniyor.

## Ne biliyoruz

Kullanıcı v12'yi Colab'da çalıştırdı, galeriyi açtı ve şunu gördü:

```
Sunucuya ulaşılamadı — bağlantıyı kontrol et.
Zaman aşımı (10 sn)
```

İkinci satır belirleyici: bu bir HTTP hatası değil. Sunucu bir şey **döndürmedi** — istek on saniye
cevapsız kaldı ve `request()` onu kesti.

## Sebep

Cevapsız kalan isteğin kendi işi ağır değil. `/api/frames` fotoğraflara hiç bakmıyor: proje
klasöründeki üç metin dosyasını okuyor (`photos.jsonl`, `plan.json`, `order.json`) ve bunların en
büyüğü damgasıyla önbellekte tutuluyor. Onbinlerce satır bile on saniye etmez.

Ağır olan, isteğin **beklediği şey**. Galerideki her karo tünelden geçen ayrı bir istek, ve aynı
anda kaçının uçtuğunu sınırlayan hiçbir şey yok. Poll'un isteği onların arasına düşüyor.

**Ne kadar eminiz:** çekişmenin hangi mekanizma olduğunu ölçmedik — bu spec yazılırken Colab
kapalıydı. İki aday var ve ikisi de aynı belirtiyi verir:

| Aday | Ne oluyor | DevTools'ta nasıl görünür |
|---|---|---|
| Bağlantı sırası (HTTP/1.1) | Tarayıcı host başına ~6 bağlantı açar; hepsi resimdeyse API isteği **gönderilmeden** bekler | `Stalled` / `Queueing` büyük |
| Bant doygunluğu (HTTP/2) | Slot sınırı yoktur, her istek hemen gider; ama tam boy fotoğraflar hattı doldurunca API cevabının birkaç kilobaytı sürünür | `TTFB` / `Content Download` büyük |

Seçilen çözüm ikisinde de doğru: ikisinin de sebebi *aynı anda uçan çok sayıda büyük istek*, ve
ikisi de aynı tavanla düşer. Tavandan sonra hata sürerse ölçüm ilk iş olur — spec bunu saklamıyor.

Üçüncü bir ihtimal de duruyor: ikisi de değilse tavan işe yaramaz. Bu yüzden "bitti sayılır" birim
testlerine değil, koşuyu kapatacak Colab turuna bağlı.

## Testler bunu neden kaçırdı

Bu görev bir gerileme değil — kaçırılan bir davranış yok, çünkü **sorulacak bir davranış hiç
yoktu**. Bugüne kadar "aynı anda kaç karo resmi uçuyor" sorusunun kodda bir karşılığı yok: `<img>`
doğrudan `src` alıyor ve gerisini tarayıcı biliyor. Test edilecek bir karar bulunmadığı için test de
yok.

Dersi v12'nin dersiyle aynı yerden geliyor: kırılma yine **dikişte**. Her parça kendi başına doğru —
`/api/frames` hızlı, önbellek çalışıyor, karolar lazy iniyor — ama hiçbiri diğerinin yanında ne
kadar yer kapladığını bilmiyor. Bu görev o boşluğa bir karar koyuyor, ve karar konduğu anda test
edilebilir hâle geliyor.

## Hangi davranış doğru sayılacak

**Kuyruk bir tavan tutar.** Aynı anda en fazla iki karo resmi uçar. Üçüncü isteyen, biri bitene
kadar bekler. Serbest kalan slot **en uzun bekleyene** gider.

**Bir slot her hâlde geri verilir.** Resim indiğinde, inemediğinde, karo ekrandan kalktığında ve
karo sırasını beklerken uzaklaştığında. Hiçbir yol slotu asılı bırakmaz — bozuk tek bir dosya
galerinin geri kalanını rehin alamaz.

**Bir karo ancak ekrana yaklaşınca sıraya girer.** Bugünkü `loading="lazy"` davranışının aynısı.
Bunun sebebi kuyruğun kendisi: bütün karolar baştan sıraya girseydi, aşağı kaydırıldığında ekrandaki
karolar hiç bakılmamış yüzlerce karonun arkasında beklerdi — tavan, lazy-load'un bugün kazandırdığı
şeyi geri vermiş olurdu.

**Gözlemcisi olmayan tarayıcıda galeri yine çalışır.** `IntersectionObserver` yoksa karo "görünür"
sayılır ve normal sıraya girer. Bu bir konfor değil, bir koruma: `new IntersectionObserver` yokken
çağrılırsa galeri komple çöker. jsdom'da da gözlemci yok, dolayısıyla mevcut `Gallery.test.jsx`
takımını ayakta tutan şey tam olarak bu kural.

**Kuyruğun kuralları DOM bilmez.** Tavan, sıra ve slot iadesi saf bir modülde yaşar; karo yalnız
protokolü uygular — sor, verilince çiz, bitince bırak. Ayrımın sebebi test edilebilirlik: kuralların
hiçbiri tarayıcıya muhtaç değil, dolayısıyla hiçbiri tarayıcı taklidiyle sınanmasın.

## Yazılacak testler

### `frontend/src/shared/image_queue.test.js` — saf, DOM yok

Testler `createQueue(limit)` ile kendi kuyruklarını kurar; uygulamanın paylaştığı örnek ayrı.

1. **`grants the first askers up to the limit`** — iki isteyen anında slot alır.
2. **`makes an asker past the limit wait`** — üçüncü isteyen slot almaz.
3. **`hands a freed slot to the asker that has waited longest`** — biri bırakır, sıradaki ilk
   bekleyen alır; sonraki değil.
4. **`skips an asker that gave up and grants the one behind it`** — sırasını beklerken vazgeçen hiç
   çağrılmaz, **ve arkasındaki çağrılır**. İkinci yarısı olmadan bu test kuyruğun tıkanmadığını
   söylemiyor.
5. **`frees one slot however many times done is called`** — aynı bilet iki kez bırakılırsa bir slot
   açılır. Yükledikten sonra unmount olan karo tam olarak bunu yapıyor.
6. **`keeps a freed slot for the next asker when no one is waiting`** — boşta bırakılan slot kaybolmaz.

### `frontend/src/features/photo_generation/TileImage.test.jsx`

Kuyruğun kuralları yukarıda sınandığı için burada sınanan şey **protokol**: karo kuyrukla doğru
konuşuyor mu. Testler `shared/image_queue.js`'i sahte bir kuyrukla değiştirir (isteyenleri kaydeder,
slotu testin istediği anda verir) ve `IntersectionObserver`'ı global olarak besler — jsdom ikisini
de sağlamıyor, ve repo bu yöntemi zaten kullanıyor (`vi.stubGlobal("fetch", …)`, clipboard,
`video.duration`).

7. **`draws no picture before the tile comes near`** — gözlemci daha "yaklaştın" demeden `src` yok.
8. **`asks for the picture once the tile comes near`** — yaklaşınca kuyruğa tam bir kez sorulur.
9. **`draws no picture until the queue grants a slot`** — sorulmuş ama verilmemişken `src` yok.
10. **`frees its slot once the picture has loaded`** — `load` olayı slotu bırakır.
11. **`frees its slot when the picture fails`** — `error` olayı da bırakır; bozuk dosya slot tutmaz.
12. **`frees its slot when the tile leaves before its turn`** — slot almadan uzaklaşan sıradan düşer.
13. **`frees its slot when the tile is taken off the screen`** — unmount bırakır.
14. **`draws the picture at once when the browser has no observer`** — gözlemci yokken karo görünür
    sayılır ve normal sıraya girer.

## İskelet

Testlerin koşabilmesi için iki dosya yalnız imzalarıyla açılır. İçlerinde tek bir kural, sayı veya
koşul yoktur — miras alınacak bir zihin modeli yok, yalnız isimler var:

```js
// shared/image_queue.js
export function createQueue(limit) {
  return { ask: () => ({ done: () => {} }) };
}
export const imageQueue = createQueue(2);
```

```jsx
// features/photo_generation/TileImage.jsx
export function TileImage({ project, file, ...rest }) {
  return <img alt={file} {...rest} />;
}
```

`Gallery.jsx` bu döngüde **hiç değişmiyor**; `TileImage` yazılıyor ama henüz kullanılmıyor.

## Kırmızı ne olacak

| Test | Nasıl düşüyor |
|---|---|
| 1, 2, 3, 6 | `ask` kimseye slot vermiyor — beklenen çağrı hiç gelmiyor |
| 4 | vazgeçen çağrılmıyor (doğru), ama arkasındaki de çağrılmıyor — testin ikinci yarısı düşüyor |
| 5 | iki bırakıştan sonra tek slot açılması bekleniyor, hiç açılmıyor |
| 8 | kuyruğa hiç sorulmuyor |
| 10, 11, 12, 13 | bırakma hiç çağrılmıyor |
| 14 | gözlemcisiz hâlde `src` yazılmıyor |

**On iki kırmızı.** İki test iskeletle tesadüfen yeşil geçiyor ve bilerek kalıyorlar:

| Test | Neden bugün yeşil | Neden yine de yazılıyor |
|---|---|---|
| 7 (yaklaşmadan resim yok) | iskelet zaten `src` yazmıyor | Düzeltmeden sonra bekçi: tavan konarken lazy davranışının düşmediğini garanti eder |
| 9 (slot verilmeden resim yok) | aynı sebep | Tavanın gerçekten tavan olduğunu söyleyen tek test — o olmadan "hep çiz" de testleri geçerdi |

## Kapsam dışı

- **`Gallery.jsx`'in `<TileImage>`'a geçmesi.** İmplementasyon döngüsünün işi.
- **Küçük önizleme.** Hâlâ tasarım bekliyor; tavan onun yerine geçmiyor.
- **Detay sayfası, video ve ses.** Kuyruk yalnız galeri karolarını kapsıyor: tıkayan yer orası, ve
  akış yapan medyanın "yükleme bitti" anı `<img>`'deki kadar net değil.
- **`loading="lazy"` özniteliğinin akıbeti.** `src`'yi kuyruk verdiğinde o öznitelik ikinci bir kapı
  olur ve karo zaten ekrana yaklaşmışken bir şey eklemez; kalıp kalmayacağı implementasyon
  döngüsünün kararı. Buradaki testlerin hiçbiri özniteliğe bakmıyor — davranışa bakıyorlar.
- **Çekişmenin hangi mekanizma olduğu.** jsdom söyleyemez; Colab turu söyler.
- **On saniyelik kesme değeri.**

## Bitti sayılır

`npm test --prefix queen-editor/frontend` on iki düşen test veriyor, hepsi kuyruk tavanı ve slot
iadesiyle ilgili; geri kalan takım — `Gallery.test.jsx` dahil — yeşil. Commit kırmızı gidiyor ve
mesajı bunu söylüyor.
