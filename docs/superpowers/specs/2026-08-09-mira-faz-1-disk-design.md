# Mira — Faz 1: Disk (Madde 2-3)

**Tarih:** 2026-08-09 · **Branch:** `feat/queen-editor-v2`
**Üst belgeler:** [tasarım dokümanı v1](2026-08-09-mira-v1-design.md) ·
[yol haritası](../plans/2026-08-09-mira-v1-roadmap.md) ·
[Faz 0](2026-08-09-mira-faz-0-iskelet-design.md)

Faz 1 uygulamanın **gerçeğini** kurar: diskteki düzen ve onu okuyup yazan katmanlar. Görünür bir
ekran üretmez; ürettiği şey, sonraki on üç fazın üstüne bina edileceği zemindir.

**Kapsam:** `store/` servisi (Madde 2) · `workspace` feature'ının proje oluşturma ve listeleme
yeteneği, uç noktalarıyla birlikte (Madde 3).
**Kapsam dışı:** yeniden adlandırma (Faz 3) · proje silme (tasarımda hiç yok) · sohbet, dosya, arama.

---

## 1 · `store/` servisi (Madde 2)

Tek işi vardır: **tek bir kökün altında dosya taşımak.** Proje, sohbet, dosya kavramlarının hiçbirini
bilmez; JSON'u da bilmez — o bir şema kararıdır ve `data/` katmanının işidir. Servis metin ve dizin
seviyesinde konuşur.

### Arayüz

| İşlem | Ne yapar |
|---|---|
| `read_text(rel)` | Dosyanın içeriğini döndürür |
| `write_text(rel, text)` | Yazar; ara dizinleri kendisi açar |
| `list_dir(rel)` | Dizindeki adları döndürür; **dizin yoksa boş liste** |
| `exists(rel)` | Var mı |
| `mtime(rel)` | Son değişiklik zamanı |
| `move(src_rel, dst_rel)` | Taşır; hedefin ara dizinlerini açar |

**`list_dir` olmayan dizinde patlamaz, boş döner.** Gerekçe: uygulamanın her ekranı "henüz hiçbir şey
yok" hâliyle başlıyor — kök ilk açılışta boş, yeni projenin `files/` dizini boş. Bunu her çağıran
yerde `exists` ile korumak, aynı kararı onlarca yere kopyalamak olurdu.

`read_text` olmayan dosyada **patlar**. Farkın sebebi: boş bir dizin normal bir durumdur, olmayan bir
dosyayı okumak ise çağıranın hatasıdır ve sessizce boş metin döndürmek o hatayı gizler.

### Yol güvenliği

Kök **hapishanedir**. Reddedilenler: `..` içeren yol · mutlak yol · sürücü harfi (`C:\…`). Reddediş
sessiz değildir, hata fırlatır.

Gerekçe iki katmanlıdır. Bugün yollar bizim kodumuzdan geliyor, yani kural bir hatayı yakalar. Faz
8'de **modelin ürettiği ad** dosya yoluna dönüşecek; o gün bu kural bir hatayı değil, bir saldırıyı
yakalar. Kuralı bugünden koymak, o günü ayrı bir işe dönüştürmemek içindir.

**Kök yoksa yazma anında oluşturulur.** Uygulama açılışta kök dizini kurmaz: kullanıcı hiç proje
kurmadan uygulamayı kapatırsa diskte hiçbir iz kalmaz.

## 2 · Proje (Madde 3)

### `project.json`

| Alan | Ne |
|---|---|
| `name` | Ekranlarda görünen ad |
| `desc` | Kart ve proje ekranındaki açıklama |
| `hue` | Renk noktasının tonu (0-359) |
| `createdAt` | Oluşturulma anı (ISO 8601) |

Dizin adı **id**'dir; `project.json` içinde ayrıca tutulmaz — dizin zaten o cevabı veriyor.

### Id

Id **opak ve değişmezdir**: kullanıcı adı değiştirdiğinde dizin taşınmaz, hiçbir bağlantı kırılmaz.
Addan türetilmez, çünkü ad değişebilir ve Türkçe/boşluklu/eğik çizgili olabilir.

Biçim: `p` + 12 haneli onaltılık. Dosya sisteminde her yerde geçerli, çakışması pratikte imkânsız.

### Sıra

Liste **oluşturulma sırasına göre eskiden yeniye** döner. Gerekçe: prototip yeni projeyi dizinin
sonuna ekliyor ve tasarımın sidebar'ı ile Home kartları aynı sırayı gösteriyor. Sıranın kaynağı
`createdAt`'tir — dizin listesinin alfabetik sırası değil, çünkü id opak.

**`createdAt` neden dosyada duruyor?** "Hiçbir dosya başkasının cevabını tekrarlamaz" kuralı aynı
cevabın iki yerde durmasını yasaklar; burada tek yer var. Dizin mtime'ı bu soruyu **cevaplayamaz**,
çünkü projenin içine ilk sohbet yazıldığı anda değişir — yani oluşturulma değil, son dokunma zamanını
söyler.

### Oluşturma

Prototip **ad sormaz**: butona basılır, proje `New project` adıyla ve
`Click to add a description.` açıklamasıyla doğar, kullanıcı sonra yeniden adlandırır. Aynısı
yapılır. Sonucu: **oluşturmada ad doğrulaması yoktur** — doğrulanacak bir kullanıcı girdisi yok.
Yeniden adlandırmanın kuralı Faz 3'ün işidir.

`hue` oluşturma anında atanır ve **saklanır**: mevcut proje sayısı × 47, mod 360. Prototipin formülü
budur; saklanmasının sebebi, sonradan silme/ekleme olduğunda kartın renginin değişmemesidir.

### İki proje aynı anda kurulursa

Id çakışırsa yazma **reddedilir**, üstüne yazılmaz. Tek kullanıcılı yerel bir uygulamada bu neredeyse
imkânsızdır, ama "kullanıcının emeği kutsaldır" ilkesi sessiz üzerine yazmayı hiçbir olasılıkta kabul
etmez.

## 3 · Katmanlar

| Katman | Dosya | Sorumluluk |
|---|---|---|
| domain | `project.py` | `Project` veri sınıfı — id, name, desc, hue, createdAt |
| domain | `ports.py` | `ProjectStore` protokolü: `create`, `list_all` |
| domain | `usecases/create_project.py` | Yeni projenin adı, açıklaması, tonu ve id'si burada kararlaşır |
| domain | `usecases/list_projects.py` | Sırayı burası uygular |
| data | `file_project_store.py` | `ProjectStore`'u `store/` üzerinden gerçekler; `project.json` şemasını **yalnız burası** bilir |
| presentation | `routes.py` | `GET /api/projects`, `POST /api/projects` |

**domain hiçbir dış şey ithal etmez** — ne `flask`, ne `os`, ne dosya adı. Id üretimi ve "şimdi"
domain'in kararıdır ama kaynağı değildir: ikisi de use case'e **parametre olarak** geçer, böylece test
sahte bir saat ve sabit bir id ile çalışır, gerçek saniye beklemez.

Uç noktalar:

| Uç nokta | Girdi | Çıktı |
|---|---|---|
| `GET /api/projects` | — | Projelerin listesi, oluşturulma sırasına göre |
| `POST /api/projects` | — | Yeni proje |

`POST` gövde almaz: oluşturmada kullanıcıdan gelen hiçbir alan yok.

## 4 · Testler

Domain ve use case testleri **sahte port** ile çalışır — disk yok. `store/` ve `data/` testleri
`tmp_path` ile gerçek dosya sistemine yazar, ama kullanıcının kökünü hiç görmez.

Kanıtlanacak cümleler:

1. Kök dışına çıkan yol reddediliyor (`..`, mutlak yol, sürücü harfi).
2. Olmayan dizin listelendiğinde boş dönüyor; olmayan dosya okunduğunda patlıyor.
3. Taşınan dosya içeriğini koruyor ve eski yerinde kalmıyor.
4. Kurulan proje diskte `project.json` olarak duruyor ve sunucu yeniden kurulunca aynı listeyle
   dönüyor.
5. Liste oluşturulma sırasına göre geliyor — id'nin alfabetik sırasına göre değil.
6. Var olan bir id'nin üstüne yazılmıyor.
7. `hue` proje sayısına göre atanıyor ve saklanıyor.
8. `GET /api/projects` boş kökte boş liste döndürüyor, patlamıyor.

## 5 · Kabul kriteri

- `pytest` yeşil; yukarıdaki sekiz cümlenin her biri bir teste karşılık geliyor.
- `npm test` yeşil (bu fazda ön yüz değişmiyor).
- `GET /api/projects` gerçek bir kökte çalışıyor ve boş kökü boş liste olarak bildiriyor.

## 6 · Bu fazda karara bağlanmayanlar

Sohbet ve dosya dizinleri (`chats/`, `files/`, `trash/`) bu fazda **oluşturulmaz**. Proje dizini
yalnız `project.json` ile doğar; alt dizinler ilk gerçek içerikleri yazıldığında açılır. Gerekçe: boş
bir `files/` dizini "burada bir şey vardı" izlenimi verir ve hiçbir soruya cevap vermez.
