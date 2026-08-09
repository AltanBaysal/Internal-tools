# Mira — Faz 2: Kabuk (Madde 4-5)

**Tarih:** 2026-08-09 · **Branch:** `feat/mira-v1`
**Üst belgeler:** [tasarım dokümanı v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) ·
[Faz 1](2026-08-09-mira-faz-1-disk-design.md)

Faz 2 uygulamanın ilk gerçek ekranlarını kurar: sabit sidebar (Madde 4) ve Home — selamlama, composer
kabuğu, öneriler ve proje kartları (Madde 5). Faz 1'in uç noktaları ilk kez bir insan tarafından
görülür.

**Kapsam:** ön yüz mimarisi (yönlendirme, veri erişimi, bileşen yerleşimi) · sidebar · Home ·
`New project`'in gerçekten proje kurması · kartlardaki sayılar.
**Kapsam dışı:** composer'ın gönderme davranışı (Madde 8) · proje ekranı (Madde 6) · yeniden
adlandırma (Madde 7) · iskelet yükleme göstergesi (Madde 29).

---

## 1 · Üç mimari karar

Faz 2 ön yüzün ilk kodu olduğu için üç karar burada verilir ve on ekranı birden bağlar.

### 1.1 Adres çubuğu gerçek — History API, kütüphane yok

Görünen ekran **URL'den** okunur: `/` Home, `/p/<id>` proje, `/p/<id>/c/<id>` sohbet.

Gerekçe üç katmanlı:

- **Yenileme yeri kaybetmemeli.** Uygulama gün boyu açık duran yerel bir araç; sekme yenilenince
  Home'a düşmek, açık sohbeti elle bulmak demek.
- **Faz 0 bunu zaten varsayıyor.** Sunucu `/p/...` gibi derin yolları `index.html`'e düşürüyor ve bir
  test bunu çiviliyor. Durum-yalnız bir ön yüzde o testin doğruladığı davranışı hiçbir şey
  kullanmazdı.
- **Faz 13 buna muhtaç.** ⌘K sonucu "şu projeye git" diyor; gidilecek yerin bir adresi olması, o
  atlamayı tek satıra indiriyor.

**Kütüphane eklenmiyor.** İhtiyaç üç kalıptan ibaret; `history.pushState` + `popstate` dinleyicisi
yaklaşık otuz satır. Bir yönlendirme kütüphanesi bu kadar iş için taşınacak bir bağımlılık değil.

### 1.2 Veri erişimi tek yerden

`shared/api.js` tek bir `fetch` sarmalayıcısı verir: `getJson(path)` ve `postJson(path, body)`.
Sunucu hata döndürürse **fırlatır**; hiçbir çağıran yeri kendi başına `resp.ok` kontrol etmez.
Bileşenler `fetch`'i doğrudan çağırmaz.

Testlerde `fetch` sahtelenir (`vi.stubGlobal`); hiçbir test ağ görmez, hiçbir test gerçek saniye
beklemez.

### 1.3 Sayılar sunucudan gelir

Proje kartı "N chats · M files" yazar. Bu sayılar **ön yüzde hesaplanmaz ve sabitlenmez**: uç nokta
`chats` ve `files` sayılarını döndürür. Bugün ikisi de sıfır — henüz sohbet ve dosya yok — ama sıfırı
tarayıcıya yazmak, testin doğrulayacağı bir kuralı ön yüze taşımak olurdu.

Bedeli neredeyse yok: `store.list_dir` olmayan dizinde boş liste döndürüyor (Faz 1 kararı), yani
sayım "dizin var mı" sorusu bile sormadan çalışıyor. Faz 5 ve Faz 9 alt dizinleri doldurdukça aynı
kod gerçek sayıları vermeye başlar.

Sayılar `Project`'in alanı olur ama **diske yazılmaz**: `project.json` şeması değişmez, sayım her
listelemede dizinden gelir. Türetilmiş bir cevabı saklamak, "hiçbir dosya başkasının cevabını
tekrarlamaz" kuralını kırardı.

## 2 · Bileşen yerleşimi

```
frontend/src/
  App.jsx                     route'a göre ekranı seçer
  shared/
    app.css                   (Faz 0)
    api.js                    getJson / postJson
    useRoute.js               History API sarmalayıcısı
  features/workspace/
    useProjects.js            listeyi çeker, yeni proje kurar
    Sidebar.jsx               280px sabit sütun
    HomeScreen.jsx            selamlama, composer kabuğu, öneriler, kartlar
    ProjectCard.jsx           tek kart
    ProjectDot.jsx            renk noktası
```

Her dosya tek iş yapar ve tek başına okunabilir. `App.jsx` yalnız hangi ekranın çizileceğini bilir;
veri çekmeyi `useProjects` yapar, çizmeyi ekran bileşenleri yapar.

## 3 · Sidebar (Madde 4)

Sabit **280px**, zemin `--sidebar`, sağında `--line` çizgisi. Yukarıdan aşağı:

| Bölüm | Davranış |
|---|---|
| Logo | 22px yuvarlatılmış vurgu karesi + `Mira` (Newsreader 21px) |
| **Search** | Kutu görünümlü buton, sağında `⌘K` mono etiketi. **Bu fazda hiçbir şey açmaz** (Madde 28) |
| **New chat** | Vurgu renkli dolu buton. Home'a döner — sohbet mesaj atılınca doğar, butona basınca değil |
| **Projects** | Başlık + `+`. En fazla **%40 yükseklik**, kendi içinde kayar |
| **Recent chats** | Başlık. Kalan yüksekliği doldurur ve kayar. Bu fazda **boş** |

Profil satırı yoktur — tasarımın açık kararı.

Projects listesi boşken **başlık ve `+` yerinde durur**; bölüm gizlenmez. Gerekçe: gizlenen bölüm,
kullanıcının proje kurabileceğini de gizler.

## 4 · Home (Madde 5)

Ortalanmış, en fazla 720px genişlik, üstten `14vh` boşluk, `riseIn` ile açılır.

**Selamlama:** `Hi` — Newsreader 42px. Kullanıcı adı yoktur; prototipin `userName` prop'u ürüne
girmez.

**Composer kabuğu:** `--surface` zeminli kutu, üç satırlık metin alanı, altında **Send** butonu. Bu
fazda **yalnız görüntü**: metin alanına yazılabilir ama yazılan hiçbir şeyi etkilemez, buton
`disabled` ve pasif görünümünde (`#E5DFD5` zemin, `cursor: not-allowed`) sabit durur. Taslağın butonu
canlandırması Madde 8'in kuralı, gönderme işinin kendisi Faz 5'in.

**Mono hedef etiketi bu fazda yoktur.** Tasarımda composer'ın altında hedef projeyi yazan bir satır
var (`project: Thesis research`), ama Home'dan gönderilen mesajın hedefi **Madde 11'de** karara
bağlanıyor — proje ve sohbet otomatik açılıyor. Hedef belli değilken o satıra bir şey yazmak, Madde
11'in kararını bugünden ve yanlış yerden vermek olurdu. Etiket hedefiyle birlikte gelir.

Buton bu fazda **bilerek** hep pasif: "boş taslak → pasif buton" bir kuraldır ve kuralın yeri Madde
8'dir. Faz 2'nin yarım bir kopyasını yazmak, aynı kararı iki yerde bırakırdı.

**Öneriler:** üç hap butonu. Bu fazda çizilirler; taslağı doldurma davranışı Madde 8'de gelir.

**Projects başlığı + New project:** buton `POST /api/projects` çağırır. Dönen proje **hem sidebar'da
hem kartlarda** anında görünür — iki liste tek kaynaktan beslenir, ayrı ayrı çekilmez.

**Proje kurulduktan sonra Home'da kalınır.** Prototip yeni projenin ekranına atlıyor; o ekran Faz
3'te yazılıyor, yani bu fazda atlamak kullanıcıyı boş bir kabuğa düşürürdü — üstelik maddenin kabul
kriteri tam da "proje iki listede birden belirdi" cümlesi, ve atlayınca o cümle görülemez. Yeni
projenin ekranına gitmek Madde 6'da, ekran var olduğunda bağlanır.

**Kartlar:** iki sütun. Her kartta renk noktası, ad, açıklama ve mono meta satırı
(`N chats · M files`). Tekil/çoğul doğru yazılır (`1 chat`, `2 chats`).

**Hiç proje yokken** ızgara boş kalır. Bu fazda öğretici bir boş metin **yoktur**: Home'un boşluğu
zaten composer ve `New project` ile dolu, üçüncü bir çağrı gürültü olur. (Boş durum metni, boşluğun
tek başına anlamsız kaldığı yerlerde var — proje ekranının dosya listesi, Madde 6.)

## 5 · Renk noktası

Tasarımın formülü: `oklch(0.72 0.09 <hue>)`. `hue` projeyle birlikte saklanıyor (Faz 1), yani bir
proje silinip eklendiğinde komşularının rengi değişmez.

Sidebar'da 9px, kartta 9px — ikisi de `--radius`'un üçte biri kadar yuvarlatılır, tasarımın
`size / 3` kuralı.

## 6 · Yükleme ve hata

Liste gelene kadar ekran **boş** durur; iskelet bloklar Madde 29'un işi ve bütün ekranlar bittikten
sonra tek elden yazılır — şimdi eklemek onu iki kez yapmak olur.

Liste çekilemezse tek satırlık bir hata metni çıkar ve `New project` çalışmaya devam eder. Sunucunun
gerçek çıktısı gösterilir; uydurulmuş bir sebep yazılmaz.

## 7 · Testler

Ön yüz testleri jsdom'da, `fetch` sahte. Kanıtlanacak cümleler:

1. Sidebar iki bölüm başlığını da hiç proje yokken çiziyor.
2. Sunucudan gelen projeler hem sidebar'da hem kartlarda görünüyor.
3. `New project` sunucuya `POST` atıyor ve dönen proje listeye **yeniden çekmeden** ekleniyor.
4. Kart meta satırı tekil/çoğulu doğru yazıyor.
5. Liste çekilemezse hata satırı çıkıyor ve uygulama çökmüyor.
6. `/p/<id>` adresiyle açılınca Home çizilmiyor (route okunuyor).
7. `New chat`'e basınca adres `/` oluyor.

Arka uç tarafında:

8. `GET /api/projects` her projeye `chats` ve `files` sayısını ekliyor; alt dizinler yokken sayı
   sıfır ve çağrı patlamıyor.
9. Sayılar `project.json`'a **yazılmıyor**.

## 8 · Kabul kriteri

- `python -m pytest` yeşil (8. ve 9. cümleler dahil).
- `npm test` yeşil (1-7).
- `npm run build` sonrası uygulama açılıyor: sidebar tasarımdaki gibi duruyor, `New project` proje
  kuruyor, kart ve sidebar satırı aynı anda beliriyor, sayfa yenilenince proje duruyor.

## 9 · Bu fazda karara bağlanmayanlar

Proje ekranının kendisi (Madde 6) ve karta tıklamanın oraya götürmesi Faz 3'ün işi. Bu fazda karta
tıklamak adresi `/p/<id>` yapar; o adreste çizilecek ekran Faz 3'te gelir ve o zamana kadar boş bir
kabuk görünür.
