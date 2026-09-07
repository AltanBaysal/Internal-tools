# Madde 192 · test turu — dosyalar tazelenir, hem liste hem detay

**Kaynağı:** [v8 yol haritası](../plans/2026-09-06-queenagent-v8-roadmap.md), Madde 192.

---

## Bugün ne oluyor

İki yer var ve ikisi de bayat kalıyor, ama farklı sebeplerden:

- **Liste** yalnız `file` çerçevesi geldiğinde tazeleniyor. `useChat`'in `announce.current?.()`
  çağrısı `frame.event === "file"` dalında duruyor *(`useChat.js`)*, ve App onu
  `reloadFiles() + reloadProjects()`'e bağlıyor. Dosyayı doğuran şey bir `file` çerçevesi değilse
  — kullanıcı Drive'a elle bir şey koyduysa — liste hiç kımıldamıyor.
- **Detay** hiç tazelenmiyor. `useFile`'ın okuma effect'i `[path]`'e bağlı, ve `path` yalnız
  *hangi* dosyanın açık olduğu değişince değişiyor. Aynı dosyanın **içeriği** değişince hiçbir şey
  değişmiyor: ekranda dosyanın açıldığı andaki hâli kalıyor.

İkincisi ağır olan: liste bayatlayınca bir ad gizlenir, detay bayatlayınca **yanlış içerik**
gösterilir.

## Ne kurulacak

**Tek bir eylem — `refresh` — ikisini birden yapar**, ve iki yerden çağrılır: tur bitince
kendiliğinden, ve bir düğmeyle elle. Yol haritasının cümlesi bunu söylüyor: *"Düğme her ikisini
turdan bağımsız yapar."* İki ayrı eylem olsaydı kullanıcı hangisine basacağını seçmek zorunda
kalırdı, ve seçim onun sorusu değil.

### 1 · `useFile` bir `reload` kazanır

Açık dosyanın yolunu yeniden okur ve `file`'ı **boşaltmadan** değiştirir. İlk okuma `setFile(null)`
ile başlıyor, çünkü orada gösterilecek bir şey henüz yok; tazelemede ekranda duran bir metin var ve
onu bir kare için silmek göz kırpması olur.

- Açık dosya yoksa hiçbir şey sormaz — `path` yok, istek de yok.
- Tazelerken 404 dönerse dosya **gitmiş** sayılır: açıkken silinmiş olabilir.

### 2 · `useChat` bir `onTurnEnd` kazanır

`send`'in `finally`'sinde çağrılır — **kimin ekranı olduğuna bakılmaksızın**. `file` çerçevesinin
her ekran için duyurulmasıyla aynı gerekçe: turun yazdığı şey diske yazıldı, kimin baktığından
bağımsız olarak. Turun nasıl bittiği de fark etmez; hata da bir bitiştir ve diske o ana kadar
yazılan yazılmıştır.

`onFileCreated` yerinde kalıyor ve adı doğru kalıyor: o **bir dosya doğdu** demek, bu **tur bitti**.

### 3 · Düğme üç yerde, tek isimle

Ekranda **hiçbir zaman ikisi birden olmuyor**, çünkü iki yüzey birbirini kapatıyor: rayda belge
listenin yerine geçiyor, proje ekranında panel açılınca dosya sütunu kayboluyor. Yani kullanıcı
her an tam bir düğme görüyor.

| Yer | Yüzey | Ne zaman görünür |
|---|---|---|
| `FilePanel`'in başlığı | detay | bir dosya açıkken *(her iki ekranda)* |
| `FileRail`'in açık listesi | liste | sohbet ekranında ray açıkken |
| `ProjectScreen`'in dosya sütunu | liste | proje ekranında panel kapalıyken |

Katlanmış rayda düğme yok: orada liste de yok, şerit yalnız bir etiket ile sayı. Açan tıklama
düğmeyi de getiriyor.

**Adı üçünde de `Refresh`**, çünkü üçü de aynı şeyi yapıyor. İkon `↻` — evin işaret düğmeleri
zaten `×`, `←`, `‹`/`›`.

**Meşgul hâli yok, ve bilerek.** `Download`'un *preparing…*'i var çünkü ürettiği şey ekranın
dışında; tazeleme yerinde değişiyor, ve değişen içerik geri bildirimin kendisi. `useList.reload`
da `loading`'i geri açmıyor — satırlar yerinde değişiyor, iskelet dönmüyor.

## Testler

### `useFile.test.jsx`

`Host` bir `refresh` düğmesi kazanır *(`reading.reload()`)*.

1. **tazelemek dosyayı yeniden okur** — açılır, sunucunun cevabı değişir, basılır, yeni metin görünür.
2. **tazelerken panel boşalmıyor** — ikinci okuma askıdayken eski metin hâlâ ekranda.
3. **açık dosya yokken tazelemek hiçbir şey sormaz** — hiç istek gitmez. *Boş geçmez:* yolu
   koşulsuz okuyan bir gerçekleme `files/null`'a bir istek atardı.
4. **açıkken silinen dosya tazelemede yok diye işaretlenir** — 404, `missing`.

### `FilePanel.test.jsx`

5. **başlıkta `Refresh` var ve basınca sorar** — `onRefresh` çağrılır.
6. **`Refresh` koşarken hiçbir şey söylemiyor** — düğme kapanmıyor, dönen bir şey yok.

### `FileRail.test.jsx`

7. **açık liste `Refresh` taşır** — basılır, çağrılır.
8. **katlanmış şeritte `Refresh` yok** — 7 onu açık listede bulduğu için boş geçmiyor.
9. **belge açıkken `Refresh` panelin, ve tek** — ray listesini panele bıraktığı için ikisi bir arada
   olmuyor.

### `ProjectScreen.test.jsx`

10. **dosya sütunu `Refresh` taşır**.
11. **panel açıkken düğme panele geçer** — ekranda tek `Refresh` kalır.

### `App.test.jsx` — kablolama

12. **tur bitince liste tazelenir** — akışta `file` çerçevesi **yok**, yalnız `chat` ve `done`;
    `/files` POST'tan sonra bir ad döndürmeye başlar. Tur bitince ad rayda görünür. *Bugün kırmızı:*
    `file` çerçevesi olmadan listeyi tazeleyen hiçbir şey yok.
13. **tur bitince açık dosya yeniden okunur** — `plan.md` açıkken tur koşar, `/files/plan.md` yeni
    metin döndürür, ekranda yenisi görünür. *Bugün kırmızı:* `useFile` yalnız `path` değişince okur.
14. **düğme turdan bağımsız sorar** — hiç tur koşmadan `Refresh`'e basılır, yeni dosya listede
    belirir.

## Kırmızının nasıl görüleceği

Dört sabit test satırı, sırayla, birebir. Kırmızı `queen-agent` ön yüzünde: `useFile` dört testte
`reading.reload is not a function` diye patlıyor, altı `Refresh` testi düğmeyi bulamıyor, ve
`App`'in açık paneli tur bittikten sonra hâlâ *the first draft*'ta duruyor. Arka uç ve
`queen-editor` kımıldamıyor — 884 ve 739/591 yerinde.

8 numara bugün de yeşil, ve bilerek: yokluğu ölçüyor. Onu anlamlı kılan 7 — düğmeyi açık listede
bulan test kırmızı olduğu sürece, katlanmış şeritte olmaması bir kural, bir tesadüf değil.

Uygulama turu ayrı bir spec'le gelir, ve `dist` onunla aynı commit'e girer.
