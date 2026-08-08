# prompt-chat — Agent İskeleti (Tasarım)

**Ekliyor:** [ilk spec](2026-08-08-prompt-chat-design.md) ve
[sohbet listesi](2026-08-08-prompt-chat-sohbet-listesi-design.md) — bugünkü davranışı onlar tarif
eder, bu belge üstüne kurar. İkisinin hiçbir kararını geri almaz.

**Devamı:** hikâye / sahne / prompt skill'lerinin **metni** ayrı bir spec. Bu belge onların
çalışacağı zemini tarif eder, içeriklerini değil.

## Amaç

Bugün prompt-chat düz bir sohbet: yazarsın, cevap gelir, kopyalarsın. Hedef aynı uygulamanın
**dosya yazan bir agent**'a dönüşmesi — Claude Code'un çalıştığı gibi: ne istediğini söylersin,
`.md` dosyalarını agent kendisi oluşturur ve günceller; sen okur, elle düzeltir, "şurası yanlış"
dersin.

Asıl kullanım üçlü bir iş: **hikâye → sahneler → sahne başına prompt.** Ama bu sıra **koda
gömülmez.** Kodda `if adım == 2` yoktur; sırayı skill'lerin metni ve dosyaların o anki hâli
belirler. "Sahneleri POV isteyecektim, anlamamışsın" dendiğinde agent geri döner, sahneleri
günceller, prompt'ları yeniler — yeni bir ekran ya da yeni bir kod yolu gerekmeden. Sınırı kod değil
talimat koyar; iskeletin işi o talimatı taşıyabilmek.

## Ne çalışır

1. **Proje aç.** Sol kolon iki kademe olur: projeler, her projenin altında dosyaları ve sohbetleri.
   Dosyalar projeye aittir, sohbete değil — sohbet ağırlaşınca aynı projede yenisini açarsın,
   bağlam temizlenir, dosyalar seninle gelir.
2. **Agent dosya yazar.** Mesaj attığında Grok'a araçlar da gider; model "şu dosyayı yaz" derse
   uygulama yazar ve sonucu modele geri verir, model işi bitene kadar bu döner. Her araç çağrısı
   sohbette bir kart olarak görünür — ne okuduğu, ne yazdığı, dosyanın yeni hâli.
3. **Dosyayı okursun ve elle düzeltirsin.** Dosyaya tıklayınca ana alan ikiye bölünür: solda
   sohbet, sağda dosya. Dosya düzenlenebilir; yazdığın anda kaydedilir.
4. **Modu seçersin.** Gönder düğmesinin yanında üç mod: **Plan** (agent yazamaz), **Onaylı**
   (yazmadan önce sorar), **Serbest** (sormadan yazar). Mod sohbete aittir ve hatırlanır.
5. **Geri alırsın.** Her dosya bir önceki hâlini saklar; dosyanın başındaki **Geri al** tek tıkla
   ona döner.
6. **Skill çağırırsın — ya da agent kendisi çağırır.** `prompt-chat/skills/` altındaki her `.md` bir
   skill. Agent hepsinin adını ve bir cümlelik tarifini görür, uygun olanın tam metnini kendisi
   ister. Sen `/hikaye` yazarak zorlayabilirsin.
7. **Dosyaları dışarı çıkarırsın.** Her dosyada Kopyala ve İndir; projede "hepsini indir".
8. **Ne harcadığını görürsün, ve durdurabilirsin.** Döngü dönerken Gönder'in yerinde `tur 3/20 ·
   durdur` yazar; bitince tek satır kalır: kaç tur döndü, kaç token girdi ve çıktı, neden bitti.

## Ekran

```
┌─ PROJELER ─────────┬──────────────────────────┬────────────────────────┐
│ ▸ Yaz kampanyası   │  Sen                     │  sahneler.md    ⤓ ⧉ ↺ ✕│
│ ▾ Kış çekimi       │  sahneleri POV yap       │ ────────────────────── │
│    ─ dosyalar ─    │                          │ ## 1. Kapıda           │
│      sorular.md    │  Grok                    │ Kamera onun gözünden…  │
│      hikaye.md     │  ┌ sahneler.md okundu ─┐ │                        │
│      sahneler.md ◂ │  └─────────────────────┘ │ ## 2. Şömine           │
│    ─ sohbetler ─   │  ┌ sahneler.md yazıldı ┐ │ …                      │
│      ilk konuşma   │  │ 8 sahne · +142 −118 │ │                        │
│      prompt turu ◂ │  └─────────────────────┘ │                        │
│                    │  Hepsini POV'a çevirdim. │                        │
│ + Yeni proje       │                          │                        │
│ ⚙ Ayarlar          │  [yaz…]  Serbest ▾  Gön. │                        │
└────────────────────┴──────────────────────────┴────────────────────────┘
```

Dosya kapalıyken sağ sütun yoktur, sohbet tam genişliktedir. Döngü dönerken alt satırdaki **Gön.**
düğmesinin yerini `tur 3/20 · durdur` alır. Tasarım dili bugünkü `app.css`'in token'ları — yeni
renk, yeni yazı tipi girmez.

## Veri

Bugünkü dört `localStorage` anahtarı sekize çıkar; şekilleri değişir:

| Anahtar | İçerik |
|---|---|
| `projects` | `[{ id, name }]` |
| `files` | `[{ id, projectId, name, content, previous }]` |
| `chats` | `[{ id, projectId, messages, draft, mode }]` |
| `active_project` | açık projenin `id`'si |
| `active_chat` | açık sohbetin `id`'si |
| `active_file` | açık dosyanın `id`'si, ya da `null` |
| `xai_key` · `xai_model` | değişmez |

`id` üretimi bugünkü kuralla aynı — `max + 1`, saat yok, rastgelelik yok — böylece saf katman
stub'sız test edilebilir kalır.

`previous` tek adımlık geri almadır: `null` ise geri alınacak bir şey yok. Neden tek adım: daha
derin bir geçmiş ikinci bir gerçek kaynağı olur ve saklama alanını yer. Derin geçmişe ihtiyaç
duyulmuyor çünkü **her yazma sohbette kart olarak duruyor** — tarih sohbetin kendisi.

**`previous`'ı yalnız agent yazar.** Elle düzenleme ona dokunmaz. Yoksa editöre yazdığın her harf
`previous`'ı tazeler ve **Geri al** "bir harf öncesi"ne dönen işe yaramaz bir düğmeye dönerdi. Kural
tek cümleyle: Geri al her zaman *agent'ın son yazmasından önceki hâle* döner — o hâl senin elle
yazdığın metinse, geri gelen odur.

### Boş hâl

Bugünkü kural — *"hiç sohbet yoksa bir tane aç, açık sohbet silinirse başkasına geç"* — aynen
projeye de uygulanır: proje yoksa **"Genel"** adında bir tane açılır, açık proje silinirse kalanların
ilkine geçilir. Ekranda projesiz ya da sohbetsiz bir an yoktur, ve bu her kullanım yerinde
korunmak yerine tek yerde onarılır.

"Genel" sıradan bir projedir — adı değiştirilebilir, silinebilir, ayrıcalığı yok. Hızlı sorunun da
yeri orasıdır: "grok şunu çevir" demek için proje açmak gerekmez.

**Eski veri taşınmaz.** Bugün tarayıcıda duran sohbetler denemeydi; yeni şekle uymayan bir kayıt
bulunursa boş hâle düşülür — `usePersistedJson`'ın bozuk JSON'da yaptığının aynısı.

### Silme

| Ne silinir | Nasıl sorulur |
|---|---|
| Sohbet | bugünkü onay, aynen |
| Dosya | onay: dosyanın adı |
| Proje | onay, **ne kaybedileceğini sayarak**: "Kış çekimi — 4 dosya ve 2 sohbet silinecek" |

Projeyi silmek dosyalarını da götürür ve geri alınamaz; onay kutusunun sayı söylemesinin sebebi bu.
Dosya silmenin geri alması yoktur — `previous` dosyayla beraber gider.

### Proje adı

"+ Yeni proje" adı sorar; boş bırakılırsa **"Yeni proje"** olur. Ad sonradan değiştirilebilir.
Sohbet başlığının aksine ad **saklanır**, türetilmez: bir projenin adı içeriğinden çıkmaz, onu
kuran kişi koyar.

**Mesaj şekli genişler.** Bugün `{role, content}`. Araçlar için xAI'ın (OpenAI uyumlu) şekli gerekir:

| Rol | Alanlar | Ekranda |
|---|---|---|
| `user` | `content` | bugünkü gibi |
| `assistant` | `content` ve/veya `tool_calls` | metin balonu ve/veya araç kartları |
| `tool` | `tool_call_id`, `content` | çağrının kartına gömülür, ayrı satır değil |
| `error` | `content` | bugünkü gibi — ekranda kalır, istekte gitmez |

`toRequestBody` bugün `user`/`assistant` dışını eliyor. Artık `tool` da geçer ve `assistant`'ın
`tool_calls`'u korunur; elenen tek rol `error` olarak kalır. Bu saf bir fonksiyon ve testi buradadır.

## Agent döngüsü

```
gonder(metin):
  mesajlar += {user, metin}
  tur = 0
  while tur < 20 and not durduruldu:
    cevap = sendChat({key, model, mesajlar, tools: moda_gore, system, signal})
    mesajlar += cevap                       # assistant, tool_calls olabilir
    if cevap.tool_calls yok: dur
    her cagri icin:
      if durduruldu: dur
      sonuc = calistir(cagri)               # onaylı modda önce sorar
      mesajlar += {tool, cagri.id, sonuc}
    tur += 1
  sohbete kapanis satiri duser: kac tur, kac token, neden bitti
```

### İki fren: biri insanın, biri otomatik

**Durdur düğmesi.** Döngü dönerken Gönder'in yeri **Durdur** olur ve yanında kaçıncı turda olduğu
yazar: `tur 3/20 · durdur`. Basıldığı anda düğme kapanır — sunucudan cevap beklenmez; bu, Queen
Editor'ın üretim durdurmasındaki davranışın aynısı. Uçan istek `AbortController` ile kesilir, döngü
bir sonraki tura girmez.

Durdurmanın kaydettiği asıl şey **sonraki turlar**: uçmakta olan istek zaten üretilmiş sayılır, ama
peşinden gelecek 17 tur gelmez.

**Yirmi tur tavanı.** Sen bakmadığında çalışan fren. Model `read_file`'ı kendi kendine tekrarlayıp
duruyorsa insan müdahalesi olmadan da durur.

Tavan bir **duvar değil, kontrol noktası**: takıldığında kapanış satırının yanında **Devam et**
durur, basarsan döngü kaldığı yerden 20 tur daha döner. Sebebi, sayının doğru olmak zorunda
kalmaması — sekiz dosya yazan bir iş okumalarla 18 tura yaklaşır, ve "kaç olmalı" sorusunu doğru
cevaplamak mümkün değil. Kontrol noktası her iki hatayı da zararsız kılar: uzun iş yarıda kalmaz,
kaçak döngü de senin onayın olmadan devam edemez. Anthropic'in kendi tavsiyesi de bu aralıkta
(`maxTurns` için önerilen 20-30), ama orada takılmak işi bitirir; burada sana sorar.

İkisi de aynı yere varır ve **yazılanları bozmaz**: dosyalar yazıldıkça kaydedilir, turun sonunda
toplu yazma yoktur — yarıda kesilen bir tur, o ana kadar yazılmış dosyaları yerinde bırakır.
Kapanış satırı hangi frenin çalıştığını söyler: `durduruldu` mu, `20 turda bitmedi` mi, yoksa model
kendi mi bitirdi.

Turun numarasının ekranda olmasının sebebi tam da bu: kaçak bir döngü "bir şeyler oluyor"dan
`tur 9/20`'ye dönüşür — ne olduğunu görürsün, sonra durdurursun.

### Bağlam: sıkıştırma yok, dosyalar var

Her tur konuşmanın tamamını yeniden gönderir; uzayan sohbet pahalılaşır ve sonunda modelin bağlam
sınırına dayanır. Claude Code bunu **sıkıştırarak** çözüyor — eski geçmişi özetleyip yer açıyor.
Burada sıkıştırma yok, ve gerekmiyor:

**Aynı projede yeni sohbet açmak, bağlamı temizlemenin yoludur.** Konuşma sıfırdan başlar, dosyalar
yerinde durur. Agent sistem mesajında dosya *adlarını* görür ve hangisi lazımsa onu okur — beş
dosyadan ikisini. Yani iş konuşmada değil dosyalarda biriktiği için, konuşmayı atmak bir şey
kaybettirmez.

Bu, "dosya projeye ait, sohbete değil" kararının asıl karşılığıdır: sadece rahatlık değil, **bağlam
yönetiminin kendisi**. Sıkıştırma bir mekanizma olarak yerine geçmez, çünkü özet kayıp demektir;
dosya kayıpsızdır ve istendiğinde tam hâliyle okunur.

Pratik kural, ekranda da yazar: *sohbet ağırlaştıysa yeni sohbet aç — dosyalar seninle gelir.*

Sistem mesajı her turda şunları taşır: proje adı, **dosya adları** (içerikleri değil), skill'lerin
adı + tarifi, aktif mod. İçerik istenirse okunur — bağlamı küçük tutan şey bu.

**Turun bedeli görünür.** Döngü, her cevabın `usage` alanını toplar ve bitince sohbete tek satır
düşer: `3 tur · 38.4k girdi · 2.1k çıktı`. Sebebi: agent turu düz mesajın on katı olabilir, çünkü
model her araç çağrısından sonra konuşmanın tamamıyla yeniden çağrılıyor. Bu satır olmadan "Grok
pahalı mı" sorusu tahmine kalır; bu satırla ölçüme dayanır. Toplam saklanmaz — satır sohbetin
kaydında zaten duruyor.

## Araçlar

| Araç | Ne yapar | Plan | Onaylı | Serbest |
|---|---|---|---|---|
| `list_files` | proje dosyalarının adları | ✓ | ✓ | ✓ |
| `read_file(name)` | dosyanın içeriği | ✓ | ✓ | ✓ |
| `load_skill(name)` | skill'in tam metni | ✓ | ✓ | ✓ |
| `write_file(name, content)` | oluşturur ya da tamamını değiştirir | — | sorar | yazar |
| `edit_file(name, find, replace)` | tek parçayı değiştirir | — | sorar | yazar |

**Plan modunda yazma araçları listeye hiç konmaz.** Modelden "yapma" diye rica edilmez; çağıracak
bir şey bulamaz. Reddetmekten daha sağlam.

`edit_file` uzun bir dosyanın tamamını yeniden yazdırmamak için var — sekiz sahnenin birini
değiştirmek için sekizini birden göndermek hem pahalı hem de diğer yedisini bozma riski. `find`
dosyada **tam olarak bir kez** geçmelidir; geçmiyor ya da birden çok geçiyorsa araç hata döner ve
hata modele aynen verilir (kaç kez bulundu, dosya kaç karakter) — model düzeltip yeniden dener.

**Silme aracı yoktur.** Dosyayı insan siler, ekrandan, onaylayarak. Gerekçe: silme geri alınamaz tek
işlem ve bunu bir modele vermek için henüz bir sebep yok. İhtiyaç doğarsa eklenir.

## Modlar

Mod sohbet başınadır, `chats` içinde saklanır, konuşmanın ortasında değiştirilebilir.

- **Plan** — okur, konuşur, yazamaz. "Ne yapsak" turu; senaryoyu beğenmediğinde önce burada plan
  yaparsın.
- **Onaylı** (varsayılan) — `write_file`/`edit_file` çağrısı geldiğinde döngü durur, sohbette kart
  çıkar: dosya adı, yeni içerik, **Onayla / Reddet**. Reddedersen araç sonucu olarak modele
  "kullanıcı reddetti" gider ve döngü devam eder — model tepki verebilir, iş yarıda kopmaz.
- **Serbest** — çağrı anında uygulanır.

Varsayılan **Onaylı**: yeni gelen biri agent'ın ne yaptığını görerek öğrenir, sonra kendi hızına
göre gevşetir.

## Skill'ler

`prompt-chat/skills/*.md`, her biri frontmatter + talimat:

```markdown
---
name: hikaye
description: Bir çekim için hikâye yazar; eksikleri önce sorular.md üzerinden toplar.
---

(talimat metni — agent'ın okuyacağı şey)
```

Build sırasında Vite bunları uygulamanın içine gömer (`import.meta.glob(..., { query: "?raw",
eager: true })`). Böylece **backend olmadan** repodaki dosyalar okunabilir ve `git pull` yapan
ekipteki herkes aynı skill'i alır — FOUNDATION'ın "git teslim kanalıdır" kararıyla aynı çizgi.

Agent sistem mesajında yalnız `name` + `description` görür; tam metni `load_skill` ile ister. İki
kademeli olmasının sebebi bağlam: on skill'in tam metnini her mesajda taşımak, hiçbirini
kullanmadığın turlarda da parasını ödemek demek.

`/hikaye` yazmak sihir değil, şeker: uygulama mesajın sonuna "(hikaye skill'ini kullan)" ekler,
model `load_skill`'i kendisi çağırır. Tek mekanizma, iki giriş.

## Hatalar

Bugünkü kural aynen sürer — **servisin kendi sözü aktarılır, sebep uydurulmaz.** Genişleyen tarafı:

| Nerede | Ekranda |
|---|---|
| HTTP hatası | `HTTP <kod> — <gövde>` (bugünkü `formatHttpError`) |
| Araç hatası (dosya yok, `find` eşleşmedi) | araç kartında, hem ekranda hem modele giden metin aynı |
| Döngü bitti (kendi bitti / durduruldu / 20 tur aşıldı) | kapanış satırı: kaç tur, kaç token, hangi sebep |
| `localStorage` doldu | tarayıcının `QuotaExceededError` metni aynen, üstüne ne yapılacağı: dosyaları indir, eski projeyi sil |

## Saklama sınırı — bilerek verilen taviz

`localStorage` ~5 MB. Agent sohbetleri (araç çağrıları + sonuçları) bu alanın büyük kısmını yiyecek;
dosyalar yanlarında küçük kalır. Kaba hesap: bir proje ≈ 400 KB, yani onlu sayıda proje sığar.

**Karar: v1 `localStorage`'da kalır**, iki emniyetle:
1. Ayarlar panelinde **kullanılan alan** göstergesi — dolmak sürpriz olmaz, yaklaşırken görünür.
2. Kota hatası **sessizce yutulmaz**: tarayıcının mesajı ekrana basılır.

Gerekçe: IndexedDB'ye geçmek `usePersisted.js`'i asenkron yapar, bu da her ekrana bir yükleniyor
durumu ekler — kanıtlanmamış bir sorun için gerçek bir karmaşıklık. Kaçış yolu zaten var: dosyalar
indirilebiliyor. **Ne zaman dönülür:** gösterge düzenli olarak %70'i geçiyorsa, ya da biri kota
hatası yediyse. O gün dosyalar IndexedDB'ye taşınır (kullanıcının emeği), sohbetler
`localStorage`'da kalır (yenilenebilir kayıt) ve FOUNDATION'ın 4. kararı buna göre yazılır.

## Katmanlar ve test

Bugünkü üç katman kuralı korunur: saf → io → render, `fetch` yalnız `api.js`'te, `localStorage`
yalnız `usePersisted.js`'te.

| Katman | Yeni dosya | Sorumluluk |
|---|---|---|
| saf | `agent.js` | bir model cevabına bakıp sıradaki adımı söyler; ağ bilmez |
| saf | `tools.js` | araç çağrısı + dosya listesi → yeni dosya listesi (ya da hata metni) |
| saf | `skills.js` | frontmatter ayrıştırma, ad/tarif listesi |
| saf | `storage.js` | mevcut; proje işlemleri eklenir |
| io | `api.js` | mevcut; `tools`, `system` ve `signal` (iptal) taşır |
| io | `useAgent.js` | döngüyü çevirir: api'yi çağırır, `tools.js`'i uygular, onayı bekler, durdurmayı dinler |
| render | `FileTree.jsx` · `FileView.jsx` · `ToolCard.jsx` | mevcut `Sidebar`/`Message`'ın yanına |

Asıl kazanç şurada: **döngünün kendisi saf.** "Model iki dosya yazma çağırdı, ikincisi reddedildi,
sonra bitirdi" senaryosu ağsız, tarayıcısız, milisaniyede test edilir. `useAgent.js`'in testi
`vi.stubGlobal("fetch", …)` ile bugünkü idiomu sürdürür.

## Kapsam dışı

- **Hikâye / sahne / prompt skill'lerinin metni** — sıradaki spec. Bu sürüm bir örnek skill ile
  gelir (`ornek.md`), iskeletin çalıştığını göstermeye yeter.
- **Dosya silme aracı** — insan siler.
- **Klasör hiyerarşisi** — proje içi düz liste. Alt klasör ihtiyacı doğmadı.
- **Çok adımlı geri alma** — tek adım + sohbetteki kayıt.
- **Paylaşım, senkronizasyon, sunucu** — hâlâ yok; herkes kendi kopyasını çalıştırır.
- **Görsel üretim / Queen Editor bağlantısı** — çıktı elle kopyalanır, bağlantı kurulmaz.
- **Sohbet başına ayrı model / system prompt** — tek model alanı, bugünkü gibi.

## Kararlar

| Karar | Gerekçe |
|---|---|
| Dosyalar tarayıcıda durur, diskte değil | `showDirectoryPicker` yalnız Chrome/Edge'de var; ekipteki herkesin tarayıcısında çalışması daha değerli. Bedeli indirme adımı |
| Dosya projeye ait, sohbete değil | Konuşma uzayınca temiz sohbetle devam edebilmek gerek; dosya sohbete bağlıysa bu imkânsız |
| Sırayı skill belirler, kod değil | İstenen esneklik bu: "sahneler POV olacaktı" demek yeni bir kod yolu değil, yeni bir cümle olmalı |
| Modlar (Plan / Onaylı / Serbest) | Tek bir davranış ya güvenliği ya kullanılabilirliği kaybediyordu; seçimi kullanana bırakmak ikisini de veriyor |
| Silme aracı yok | Geri alınamayan tek işlem; modele vermek için sebep yok |
| Skill'ler repoda, uygulamada değil | Ekipte tek sürüm; `git pull` iyileşmeyi dağıtır |
| Tek adımlık geri alma | Derin geçmiş ikinci bir gerçek kaynağı; sohbet zaten tarihi tutuyor |
| Araç adları İngilizce | Kodun bir parçası — CODE-STANDARD'ın dil kuralı |
| Elle düzenleme açık | Kullanıcının istediği esneklik; iki yazarın bedeli modlar ve geri alma ile ödeniyor |
| Tur başına token satırı, toplam yok | Model değiştirme kararı ölçüye dayansın; toplamı saklamak veri modeline alan ekler, satır zaten sohbette duruyor |
| İki fren: Durdur düğmesi **ve** 20 tur tavanı | Tavan sen bakmazken, düğme bakarken korur — biri diğerinin yerine geçmez. Tur numarasının ekranda olması, kaçak döngüyü görünür kılar |
| Tavan duvar değil, **Devam et**'li kontrol noktası | "Kaç tur olmalı" sorusunun doğru cevabı yok; kontrol noktası hem az hem çok tahmini zararsız kılar |
| Bağlam sıkıştırması yok — yerine yeni sohbet | Özet kayıptır; dosya kayıpsız. İş dosyalarda biriktiği için konuşmayı atmak bir şey kaybettirmez |

## Doğrulama

1. **Boş projede** "bana `deneme.md` diye bir dosya yaz, içinde üç madde olsun" → dosya ağacında
   çıkar, tıklayınca içeriği görünür.
2. **Onaylı modda** aynı istek → önce kart çıkar, **Reddet** dersen dosya oluşmaz ve agent bunu
   bilerek cevap verir.
3. **Plan modunda** aynı istek → dosya oluşmaz; agent ne yapacağını anlatır (yazamadığı için değil,
   aracı olmadığı için).
4. **Elle düzenleme:** dosyayı aç, bir satır yaz, sohbete dön, agent'a "dosyayı oku" de → senin
   yazdığın satırı görür.
5. **Geri alma:** agent dosyanın üstüne yazsın, **Geri al** → önceki hâl geri gelir.
6. **`edit_file` hatası:** dosyada olmayan bir metni değiştirmesini iste → araç kartında gerçek hata
   görünür, agent kendi düzeltir.
7. **Skill:** `/ornek` yaz → agent `load_skill` çağırır, kart görünür, talimata göre davranır.
8. **Sohbet ayrımı:** aynı projede ikinci sohbet aç → dosyalar orada da görünür, sohbet geçmişi
   ayrıdır.
9. **Kalıcılık:** sayfayı yenile → projeler, dosyalar, sohbetler, mod ve açık dosya yerinde.
10. **Bedel satırı:** araç çağıran bir tur ile hiç araç çağırmayan bir turu karşılaştır — token
    sayıları belirgin şekilde farklı olmalı, yoksa `usage` toplanmıyordur.
11. **Durdurma:** çok dosyalı bir iş başlat ("beş sahne için beş ayrı dosya yaz"), ikinci dosya
    yazılırken **durdur** — düğme anında kapanmalı, üçüncü dosya oluşmamalı, ilk ikisi yerinde
    kalmalı, kapanış satırı `durduruldu` demeli.
12. **Testler:** `npm test` yeşil, sayı bugünkü 69'un üstünde.
