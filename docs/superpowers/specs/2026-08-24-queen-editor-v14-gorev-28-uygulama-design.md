# v14 Görev 28 — Galerinin indirme sırası: İMPLEMENTASYON döngüsü tasarımı

**Tarih:** 2026-08-24 · **Kaynak:** [test spec'i](2026-08-24-queen-editor-v14-gorev-28-testler-design.md)
**Yol haritası:** [v14](../plans/2026-08-20-queen-editor-v14-roadmap.md) madde 28

## Kırmızı testlerin istediği

Önceki commit yedi testi kırmızı bıraktı.

| # | Test | Ne istiyor |
|---|---|---|
| K1 | `shares one queue of a single slot for the gallery` | Paylaşılan kuyruğun tavanı 1 |
| K2 | `asks even where the browser could tell it is out of sight` | Karo `IntersectionObserver`'a hiç bakmıyor |
| K3 | `shows a plain holder while it waits its turn` | Sırada bekleyen karo `.wf-img` gösteriyor, `.wf-spinner` göstermiyor |
| K4 | `shows a turning holder while the picture is coming` | İzin almış karo `.wf-spinner` gösteriyor |
| K5 | `keeps the picture out of sight until it arrives` | Fotoğraf gelene kadar `<img>`'in `display`'i `none` |
| K6 | `leaves a quiet holder where a picture never arrived` | Hata sonrası kutu kalıyor, halka gidiyor, fotoğraf görünmüyor |
| K7 | `frees its slot when the picture takes too long` | 30000 ms sonra bilet bırakılıyor |

Yanlarında yeşil doğan on bir bekçi var; onların da yeşil kalması şart.

## Değişen üç dosya

### 1 · `shared/image_queue.js` — bir sayı ve gerekçesi

```js
// One at a time, in the order the tiles were built. Every tile is its own request through the same
// tunnel and the status poll shares it, so a ceiling is what keeps the API's request from waiting
// behind a project's worth of photos. One rather than more: on a full gallery the difference is
// seconds, and a pipe with one thing in it is the pipe nobody has to reason about.
const GALLERY_SLOTS = 1;
```

Modülün gövdesi değişmiyor. Bugünkü yorum sayıyı *"yoklama on saniyelik iptale takılıyordu"* diye
gerekçelendiriyor; o tıkanma tünelin UDP'sindendi ve 24 Ağustos'ta düzeldi — depo kuralı gereği
yorum bugüne uyduruluyor.

### 2 · `features/photo_generation/TileImage.jsx` — üç kapı ikiye

Silinenler: `IntersectionObserver` kurulumu ve etkisi, `MARGIN`, `near` durumu, gözlemcisi olmayan
tarayıcı kolu, `picture` ref'i.

Girenler: `state` (`waiting` / `here` / `gone`), süre etkisi, tutucu, gizli `<img>`.

```jsx
// How long a tile waits for its picture before it lets the queue move on. An img download has no
// timeout of its own -- the ten second abort in api.js belongs to fetch -- so a request that hangs
// answers neither load nor error, and with one slot that is the whole gallery stopped behind it.
// Judgement rather than measurement: long enough that a slow photo is never given up on early.
const PATIENCE = 30000;

const HIDDEN = { display: "none" };
```

Gövdesi:

```jsx
const [held] = useState(() => shownPictures.has(url));
const [granted, setGranted] = useState(held);
const [state, setState] = useState(held ? "here" : "waiting");

useEffect(() => {
  if (held) return undefined;
  ticket.current = imageQueue.ask(() => setGranted(true));
  return () => ticket.current.done();
}, [held]);

useEffect(() => {
  if (!granted || state !== "waiting") return undefined;
  const timer = setTimeout(() => ticket.current?.done(), PATIENCE);
  return () => clearTimeout(timer);
}, [granted, state]);
```

Çizimi:

```jsx
{state !== "here" && (granted && state === "waiting"
  ? <Rendering style={style} />
  : <div className="wf-img" style={style} />)}
<img alt={file} src={granted ? url : undefined}
     style={state === "here" ? style : HIDDEN}
     onLoad={() => { shownPictures.add(url); settle("here"); }}
     onError={() => settle("gone")}
     {...rest} />
```

**`style` artık ayrı bir prop olarak alınıyor**, `rest`'in içinde değil: hem tutucuya hem fotoğrafa
gerekiyor, ve fotoğraf gizliyken kendi `display`'ini kendisi söylüyor.

**`<img>` her hâlde DOM'da.** Gizli resim de indirilir. Çizilmemesi gereken tek şey `alt` metni ve
onu ortadan kaldıran şey `display: none`.

### 3 · `features/photo_generation/Gallery.jsx` — bir yorum

Bugünkü yorum *"karo yalnız yaklaşınca ister"* diyor; bu artık doğru değil. Yerine kuyruğun bugünkü
işini ve sıranın nereden geldiğini söyleyen bir cümle geçiyor.

## Verilen kararlar

**Tutucu ve halka için bileşen yazılmıyor.** `Rendering` zaten *"kit'in yükleniyor tutucusu,
kelimesiz"*; sade kutu ise `wf-img` sınıfının kendisi. İkisinin arasındaki tek fark halka.

**Üç durum bir değişkende.** `waiting`/`here`/`gone` tek `state`; iki ayrı boolean aynı şeyi
söylerdi ve ikisinin birden doğru olduğu anlamsız bir hâl üretebilirdi.

**Süre `granted` ile başlıyor, `state` ile bitiyor.** Sıradaki karolar için hiç kurulmuyor — yalnız
sloti tutan karo sayılıyor.

**Süre dolunca indirme iptal edilmiyor.** `src` yerinde kalıyor; gelirse fotoğraf çiziliyor. Slot
bırakmak, indirmeyi durdurmak değil.

**Bayt sayısı değişmiyor.** Küçük önizleme, WebP, sanallaştırma — hiçbiri bu maddenin işi değil;
ölçüm baytın sebep olmadığını söyledi.

## Ön yüz derleniyor

`npm run build --prefix queen-editor/frontend` koşuyor ve `dist` **aynı commit'e** giriyor. Depo
kuralı: defter derlemiyor, klonladığını çalıştırıyor — derlenmemiş bir ön yüz değişikliği bitmiş
sayılmıyor.

## Doğrulama

`npm test --prefix queen-editor/frontend` → **553 passed.** Yedi kırmızı yeşile döner, 546 yerinde
kalır. Test dosyalarına dokunulmaz: testi koda uydurmak turun anlamını yok eder.

`python -m pytest queen-editor -q` → **711 passed**, değişmemiş olmalı.

**"Bitti" yargısı Colab turunundur** (madde 30): çok kareli bir projede galerinin baştan sona,
tek tek, gözle görülür hızda dolması ve hiçbir karoda dosya adının yazmaması.

## Kapsam dışı

- **Test dosyaları değişmiyor.**
- **Kuyruğun gövdesi değişmiyor** — FIFO, atlama, bir bilet bir slot aynen duruyor.
- **Video ve ses değişmiyor** — kullanıcı kararı, test spec'inde yazılı.
- **Hız ölçülmüyor.**
