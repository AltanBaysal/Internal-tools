# Mira — Tasarım Dokümanı v1

**Tarih:** 2026-08-09 · **Branch:** `feat/queen-editor-v2` · **Durum:** yol haritası yazılmayı bekliyor

**Kaynaklar.** Ürünün kaynağı claude.ai/design'daki **"Mira AI tasarımı istemi"** projesidir
(`3c06e399-3b83-48b1-b186-26e56747823d`). İçindeki üç dosyanın rolü ayrıdır ve bu belge boyunca
ayrı anılır:

| Dosya | Rolü |
|---|---|
| `Mira Handoff.dc.html` | **Davranış sözleşmesi.** Yapı, çekirdek döngü, element kuralları, sekiz durum, klavye/erişilebilirlik, görsel dil. Çelişkide bu kazanır. |
| `Mira.dc.html` | **Çalışan prototip.** Ekranların ve veri modelinin somut hâli — ama sahte motorlu ve tek parça. Bağlayıcı olan görüntüsüdür, kodu değil. |
| `Mira Frames.dc.html` | 14 kareli ekran tuvali. Referans. |

`support.js` claude.ai/design'ın üretilmiş çalışma zamanıdır (`x-dc` şablonu + `DCLogic` → React);
ürüne girmez.

---

## 1 · Mira nedir

Küçük bir AI çalışma alanı. Bir **proje** iki kardeş koleksiyon tutar: **sohbetler** ve **dosyalar**.
Sohbetler dosya üretir; **dosya projeye aittir, sohbete değil**. Kullanıcı dosya yüklemez — okur.

Amaç alanı serbesttir: kullanıcı bir şey ister, Mira cevabı yazar ve uygun gördüğünde cevabı projeye
bir dosya olarak kaydeder. Hiçbir üretim hattına bağlı değildir.

## 2 · Kararlar

Bu belgeyi doğuran kararlar, veriliş sırasıyla:

| Karar | Sonucu |
|---|---|
| Genel amaçlı AI çalışma alanı | İçerik alanı serbest, `collab-toolbox`/`queen-editor` ile hiçbir bağ yok |
| **Yerel makinede** çalışır, veri **diskte** | Colab yok, tunnel yok, Drive yok, `dist/` commit zorunluluğu yok |
| Motor **xAI Grok** | Uzak API; GPU gerekmiyor — yerel kararının asıl gerekçesi bu |
| **Model karar verir**, her cevap dosya üretmez | Tasarımda olmayan tek yeni hâl: dosyasız cevap |
| **Agentic döngü** | Model gerekirse bakar, okur, yazar; hepsi tek "Send"in içinde |
| Arayüz dili **İngilizce** | queen-editor'ün Türkçe kuralı Mira'ya taşınmaz |
| Proje yapısı queen-editor'ün yapısı | Katman kuralları miras; tasarım aracının ürettiği kod bağlayıcı değil |
| Home'dan ilk mesaj | Proje **ve** sohbet otomatik açılır |
| Selamlama | Sadece "Hi" — kullanıcı adı diye bir ayar yok |
| Ad çakışması | Üstüne yazılmaz, sonuna sayı eklenir |
| v1'e alınan açık maddeler | Gerçek streaming · sohbet silmede onay · dosya yeniden adlandırma · 1100px altı |

## 3 · Repodaki yeri ve kimliği

`mira/` monorepo'nun **üçüncü aracıdır**; `CLAUDE.md`'ye kendi bölümü gelir. Kendi `FOUNDATION.md` ve
`CODE-STANDARD.md` dosyalarını taşır. Bunlar queen-editor'ünkinden türetilir, ama **dört kararı
düşer** — Colab, cloudflared tunnel, Google Drive, ComfyUI — ve yerlerine ikisi gelir: *yerel süreç +
disk* ve *xAI Grok*. Değişmeden geçen ilkeler: kullanıcının emeği kutsaldır, gerçek diskte durur,
correctness > simplicity > generality > performance, kod yeniden üretilebilirlik için yazılır.

**queen-editor'e hiçbir bağımlılığı yoktur.** Ondan miras alınan şey kod değil, iki belgenin
kendisidir: katman kuralları, dil ayrımı, test disiplini.

**Bir kural bilerek ayrışıyor.** queen-editor "kullanıcının gördüğü arayüz Türkçe" der; Mira'nın
arayüzü **İngilizce**dir, çünkü tasarımın bütün metinleri İngilizce yazılmıştır ve çevirmek tasarımı
kaynak olmaktan çıkarır. Yorum, docstring, test adı ve commit mesajı zaten İngilizce olduğu için
Mira'nın içinde tek dil vardır. `mira/CODE-STANDARD.md` bunu açıkça yazar ki komşu aracın kuralı
yanlışlıkla buraya taşınmasın. Bu belge ve yol haritası **Türkçe**dir — repodaki bütün superpowers
belgeleri gibi.

## 4 · Yığın ve katmanlar

Arka uç **Flask** (sync), ön yüz **React 18** (Vite ile derlenir). Bağımlılık yönü queen-editor'ünkiyle
aynıdır: `presentation → domain ← data → services`. Yasaklar istisnasız: `feature ↛ feature`,
`service ↛ feature`, `service ↛ service`. Somut sınıflar yalnız kompozisyon kökünde bağlanır.

### Tek feature: `workspace`

Bu bir tercih değil, yasağın sonucudur. Proje, sohbet, dosya ve mesaj ayrı feature'lar olamaz, çünkü
**bir cevabın dosya yazması üçüne aynı anda dokunur** — ayırmak `feature ↛ feature` yasağını daha ilk
maddede kırardı. Dördü tek bir bütündür. Arama da workspace'in bir use case'idir, ayrı bir feature
değil.

Yeni bir sınırlı bağlam çıkarsa (paylaşım, kimlik) ikinci feature o zaman açılır. Bugün yoktur.

### İki servis

- **`store/`** — tek kök altında oku / yaz / listele / taşı. Proje, sohbet, dosya kavramlarının
  hiçbirini bilmez. Kök dışına çıkan yol reddedilir.
- **`xai/`** — Grok HTTP taşıması: istek, SSE akışı, araç çağrısının çözülmesi. Prompt bilmez, dosya
  bilmez, hangi aracın ne yaptığını bilmez.

### Ön yüz

`frontend/src/` altında aynı feature-first şekil: `features/<name>/` (bileşenler + veri erişimi),
`shared/` (fetch sarmalayıcı, uygulama CSS'i). **`vendor/` klasörü yoktur** — queen-editor'de tasarım
projesinden birebir gelen dosyalar vardı; Mira'nın prototipi tek parça bir DC bileşenidir, satır içi
stillidir ve `style-hover` gibi DC'ye özel öznitelikler kullanır. Kopyalanacak bir bileşen dosyası
yok. Bu yüzden **tasarım görsel şartnamedir, kaynak kod değildir**: React'i biz yazarız, tasarımın
rengine, tipografisine, ölçülerine ve davranışına sadık kalarak.

Derleme yerelde çalıştığı için `dist/` commit etme zorunluluğu yoktur.

## 5 · Diskteki gerçek

İlke aynen geçerlidir: *gerçek diskte durur, süreç hafızası atılabilir.* Kök tek bir yerde adlanır —
`MIRA_ROOT` ortam değişkeni — ve repo dışındadır.

```
<MIRA_ROOT>/
  <project-id>/
    project.json          name · desc · hue · createdAt
    chats/<chat-id>.json  title · createdAt · messages[]
    files/<name>.md       dosyanın kendisi
    trash/<name>.md       silinmiş dosya
```

`messages[]` her elemanı: `role` (`user` | `ai`) · `at` (saat damgası) · `text` · isteğe bağlı `file`
(üretilen dosyanın adı).

Ekranlarda görünen "2h ago" gibi göreli zamanlar hiçbir yerde alan olarak tutulmaz: sohbetinki kendi
json'ının, dosyanınki kendi dosyasının mtime'ından gelir. Proje kartındaki "N chats · M files" de
dizin sayımıdır. Aynı kuralın devamı — hiçbir dosya başkasının cevabını tekrarlamaz.

Bu düzenin üç sonucu var, üçü de bedava geliyor:

**Dosya listesi için ayrı bir kayıt dosyası yoktur.** Dizin listesinin kendisi cevaptır: ad = dosya
adı, "2h ago" = mtime, sıra = mtime'a göre yeniden. queen-editor'ün *"hiçbir dosya başkasının cevabını
bayrak olarak tekrarlamaz"* kuralı burada bir dosyayı tamamen ortadan kaldırıyor.

**Silme = `trash/`'e taşımadır, Undo = geri taşımadır.** mtime taşımada korunduğu için dosya kendi
eski yerine döner — handoff'un "Undo restores the file to its original position" cümlesi ek kod
istemeden karşılanır.

**Arama dosya içeriğinde çalışır**, çünkü içerik gerçekten diskte durur.

Prototipin `file.from = chatId` alanı **yazılmaz**: handoff "no go to source chat link" der, alan
hiçbir ekranda kullanılmaz.

## 6 · Cevap üretme akışı

Tek uç nokta, tek akış. Sıra şudur:

1. Kullanıcı mesajı **önce diske yazılır**. Bağlantı ölse bile kaybolmaz; tasarımın hata hâli de
   "the user message stays" der.
2. Grok'a araçlarla birlikte gidilir.
3. Cevap SSE ile tarayıcıya akar.

### Agentic döngü

Tek atış yeterli değildir: model dosya listesini görmeden hangisini okuyacağını bilemez, okumadan da
içeriğine dayanan bir cevap yazamaz. Tek atışta bunu yapmanın tek yolu bütün dosyaları her istekte
peşin göndermek olurdu — pahalı ve gereksiz.

Döngü: kullanıcı mesajı → Grok *"`list_files` çağır"* → sunucu çalıştırır, sonucu geri verir → Grok
*"`read_file` çağır"* → sunucu çalıştırır → Grok *"`create_file` çağır"* → sunucu diske yazar → Grok
son cevabı yazar → döngü kapanır. Hepsi **tek bir "Send"in içinde**, kullanıcı için tek bir cevap.

Üç kural döngüyü güvenli tutar:

- **Tur sınırı vardır.** Model sonsuza kadar araç çağıramaz; sabit bir üst sınırda döngü kesilir ve
  model elindekiyle cevap verir. Sayı Madde 17'nin spec'inde belirlenir.
- **Araçları sunucu çalıştırır.** Model yalnız "şunu çağır" der; neyin okunacağı, nereye yazılacağı ve
  kök dışına çıkılamayacağı sunucunun kararıdır.
- **Ekranda tek bir şey değişir.** Model dosyalara bakarken üç nokta yanıp söner; yalnız `create_file`
  kesikli "creating file…" kartını doğurur.

### Ekrandaki karşılıkları

| Sunucudan gelen | Ekranda |
|---|---|
| metin parçası | üç nokta söner, cevap yazılmaya başlar |
| `list_files` / `read_file` çağrısı | ekran değişmez |
| `create_file` çağrısı | kesikli "creating file…" kartı; dosya yazılınca yerini dolu dosya kartına bırakır |

Model hiç `create_file` çağırmazsa dosya doğmaz, cevap tek başına kalır.

### Hata

Akış ölürse kullanıcı mesajı yerinde durur, sıcak tonlu hata kartı ve **Try again** çıkar. Yarım kalan
metin kaydedilmez: yarım cevabı kalıcı kılmak tasarımın "cevap ya vardır ya yoktur" diline aykırıdır.
Hata metni sunucunun/servisin **gerçek çıktısını** taşır, uydurulmuş tek bir sebep değil.

### Grok bağlantısı

Anahtar ortam değişkeninden okunur, model adı ayar dosyasında tek satırdır. **Uç nokta adresi, model
id'si ve akış/araç alan adları Madde 13'ün planında xAI dokümanından doğrulanır** — bu belge onları
ezberden sabitlemez.

## 7 · Ekranlar

Ölçüler ve davranış handoff'un 1. ve 3. bölümlerindedir; burada yalnız iskelet:

- **Sidebar (280px, sabit).** Search · New chat · Projects (en fazla %40 yükseklik, kendi içinde
  kayar) · Recent chats (kalanı doldurur, her sohbeti gösterir). Profil satırı yok.
- **Home.** Selamlama · composer · üç öneri · proje kartları. Composer'ın mono etiketi hedef projeyi
  yazar.
- **Proje.** Başlık (yeniden adlandırılır) · açıklama · composer · iki sütunlu ızgara: solda sohbetler,
  sağda proje dosyaları (320px).
- **Sohbet.** Breadcrumb · mesaj sütunu · composer · sağda kalıcı 320px dosya rayı.
- **Dosya okuma.** Asla ayrı bir ekran değildir. Sohbette ray 320 → 560px genişler; proje ekranında
  560px'lik panel yandan açılır ve ızgara tek sütuna iner.

**Görsel dil.** `#F7F5F1` zemin · `#EFEBE4` sidebar · `#FFFDFA` yüzey · `#B5623C` tek vurgu ·
`#22201D` mürekkep. Newsreader başlık, DM Sans gövde, DM Mono etiket/sayı/zaman. Yarıçaplar: 8px
kontrol, 12–14px kart, 20px hap. Hareket yalnız opaklık geçişleri (180–220ms) ve rayın genişlik
geçişidir (220ms); yerleşmiş bir elemanı yana kaydıran hiçbir şey yok.

**Klavye.** ⌘K/Ctrl+K aramayı açar-kapar · Esc önce aramayı, sonra açık dosya panelini kapatır, asla
geri gitmez · Enter gönderir, Shift+Enter satır atlar, taslak boşken pasiftir · odak halkası 2px
`#B5623C`, 2px boşlukla.

**Sekiz durum:** idle · sending · typing · generating · error · loading · downloading · offline.
Tanımları handoff'un 4. bölümündedir.

## 8 · Tasarımla çelişkiler ve verilen kararlar

Prototiple handoff'un ayrıldığı ve tasarımın hiç konuşmadığı yerler. Bir dahaki karşılaştırmada
"atlanmış" sanılmasınlar diye buradalar.

| Konu | Karar |
|---|---|
| Undo dosyayı nereye koyar | **Handoff kazanır:** eski yerine. Prototip listenin başına koyuyordu; `trash/` düzeni mtime'ı koruduğu için doğrusu kendiliğinden geliyor |
| Her cevap dosya üretir mi | **Hayır** — model karar verir. Tasarıma eklenen tek yeni hâl: dosyasız cevap |
| Dosya yeniden adlandırma | Handoff'ta "açık madde"; **v1'e alındı** |
| `file.from` alanı | **Yazılmaz** — hiçbir ekranda kullanılmıyor, handoff kaynak sohbet bağlantısını yasaklıyor |
| Hiç proje yokken Home'dan mesaj | Prototip `projects[0]`'a gönderiyor ve proje yoksa çöker; **proje ve sohbet otomatik açılır** |
| Kullanıcı adı | Prototipte "Hi, Alex" bir prop; **sadece "Hi"**, ayar yok |
| Proje silme | Tasarımda **hiç yok** — eklenmez |
| Prototipin kodu | Bağlayıcı değil; tasarım görsel şartnamedir |

## 9 · Kapsam dışı

Dosya sürümleme (v1/v2 + diff) · dosya listesini sıralama ve filtreleme · dosya yükleme (tasarımın
kararı: kullanıcı okur, yüklemez) · paylaşım · kimlik ve çok kullanıcı · proje silme.

## 10 · Yol haritasının şekli

15 faz, 32 madde. Her madde tek bir görülür çıktıya sahiptir, bir öncekinin üstüne biner ve tek başına
spec → plan → TDD ile kapanır. Maddelerin içeriği yol haritası belgesinde açılır.

| Faz | Ne | Madde |
|---|---|---|
| 0 | İskelet | 1 · uygulama ayağa kalkar |
| 1 | Disk (arka uç) | 2 · store servisi · 3 · proje oluştur/listele |
| 2 | Kabuk | 4 · sidebar iskeleti · 5 · Home + proje kartları |
| 3 | Proje ekranı | 6 · proje ekranı · 7 · yeniden adlandırma |
| 4 | Composer ve sohbet kaydı | 8 · composer davranışı · 9 · sohbet oluşur |
| 5 | Sohbet ekranı | 10 · sohbet ekranı · 11 · otomatik proje+sohbet · 12 · sohbet listeleri |
| 6 | Grok | 13 · bağlantı servisi · 14 · cevap gelir |
| 7 | Akış | 15 · cevap akar (SSE) · 16 · hata hâli + Try again |
| 8 | Ajan döngüsü | 17 · döngü + `list_files` · 18 · `read_file` · 19 · `create_file` |
| 9 | Dosya görünür | 20 · kesikli kart → dosya kartı · 21 · sohbetteki ray |
| 10 | Okuma | 22 · panel (sohbet) · 23 · panel (proje) · 24 · Download |
| 11 | Silme | 25 · dosya silme + Undo · 26 · sohbet silme (onaylı) |
| 12 | Yeniden adlandırma | 27 · sohbet ve dosya adı |
| 13 | Arama | 28 · ⌘K |
| 14 | Durumlar ve cila | 29 · skeleton · 30 · çevrimdışı · 31 · 1100px altı · 32 · uçtan uca tur |

**Neden bu sıra.** Disk her ekranın çizdiği gerçektir, o yüzden önce gelir. Sohbet → akış → dosya
sırası her maddeyi bir öncekini görünür kılan şeye bağlar. Ray dosyadan sonradır, çünkü gösterecek
dosya olmadan boş bir vaattir. Silme, arama ve yeniden adlandırma dosya listesi doğduktan sonra
gelir. 1100px altı en sondadır: düzen yerine oturmadan kırmak aynı işi iki kez yaptırır.

## 11 · Açık sorular

Hepsi ilgili fazın spec'inde karara bağlanır; roadmap bunları beklemez.

| Soru | Nerede kapanır |
|---|---|
| Proje açıklaması düzenlenebilir mi (tasarımda düzenleme yolu yok) | Faz 3 (Madde 7) |
| Ajan tur sınırı kaç olacak | Faz 8 (Madde 17) |
| Ara turlarda ekranda gösterge olacak mı (tasarımda karşılığı yok) | Faz 8 (Madde 17) |
| Grok'un sistem yönergesi ve dosya adı üretme kuralı | Faz 8 (Madde 19) |
| Üretilen dosya `.md` dışına çıkacak mı | Faz 8 (Madde 19) |
| Silinmiş dosyaya bakan mesaj kartı ne gösterir | Faz 9 (Madde 20) |
| Undo şeridinin ömrü (basılana kadar mı, süreli mi) | Faz 11 (Madde 25) |
| Dosya yeniden adlandırılınca mesajdaki kart ne olur | Faz 12 (Madde 27) |
| Uç nokta, model id'si, akış ve araç alan adları | Faz 6 (Madde 13) — xAI dokümanından doğrulanır |

## 12 · Nasıl çalışacağız

Birim **fazdır**, madde değil. Her faz dört adımdan geçer, faz bitmeden sonrakine geçilmez:

1. **Spec** — fazın tasarım dokümanı (`docs/superpowers/specs/`); fazın maddelerine düşen açık sorular
   burada karara bağlanır.
2. **Plan** — uygulama planı (`docs/superpowers/plans/`), madde madde TDD adımlarıyla.
3. **TDD** — önce başarısız test, sonra kod; fazın maddeleri sırayla. Arka uç `pytest` (sahte
   port'larla; ne Grok'a ne diske gerçek erişim), ön yüz `npm test` (vitest + jsdom; `fetch` ve saat
   sahte).
4. **Kapanış** — `pytest` ve `npm test` yeşil.

Commit'ler koşunun sonunda topluca atılır.

**Deneme en sonda, toplu.** Maddeler tek tek elle denenmez; hepsi Madde 32'de bir dalgada denenir.
Bunun sonucu: bir maddenin "nasıl görülür" satırı o maddenin **kabul kriteridir**, sonra yapılacak bir
tur değil — testler o satırı kanıtlamalıdır.
