# prompt-chat — Çalışma Alanı (Tasarım)

**Ekliyor:** [ilk spec](2026-08-08-prompt-chat-design.md),
[sohbet listesi](2026-08-08-prompt-chat-sohbet-listesi-design.md),
[skill'ler](2026-08-08-prompt-chat-skills-design.md). Hiçbirinin kararını geri almaz.

**Öncesine geçiyor:** [agent iskeleti](2026-08-08-prompt-chat-agent-iskeleti-design.md). Projeler,
dosyalar, dosya ağacı ve düzenleyici oradan **buraya taşındı**; o belge artık yalnız döngü, araçlar
ve modlar. Sıra bilerek böyle: agent'ın yazacağı zemin, o yazmadan önce kurulup denenir.

## Amaç

Skill'ler geldi, ama iş hâlâ tek yerde birikiyor — sohbetin kendisinde. Uzun bir çıktı (bir senaryo,
bir plan) sohbet kapandığında bulunması zor bir metin yığınına dönüşüyor; tekrar kullanmanın tek
yolu yukarı kaydırıp kopyalamak.

Bu sürüm işe kendi yerini veriyor: **proje** ve içindeki **dosyalar**. Dosyayı sen yazarsın,
`@adı` ile sohbete çağırırsın, üstünde konuşursun, düzeltirsin.

**Agent yok, araç yok, döngü yok.** Hiçbir kod dosyaya yazmıyor — yazan tek şey senin klavyen. Bu
bilinçli: dosyaya yazmanın yolu `write_file` aracıdır ve o araç bir sonraki turun konusu. Kestirme
bir "cevabı kaydet" düğmesi koymak, aynı işi iki farklı yoldan yapılır hâle getirirdi.

## Ne çalışır

1. **Proje aç.** Sol kolon iki kademe olur: projeler, her projenin altında dosyaları ve sohbetleri.
2. **Dosya yaz.** "+ Yeni dosya" ad sorar; dosya sağda açılır ve yazdığın anda kaydedilir. Metin
   ham gösterilir — markdown biçimlenmez, çünkü biçimlemek bir markdown kütüphanesi demek ve bu
   uygulamanın hiç bağımlılığı yok. Yazdığın şeyi olduğu gibi görürsün.
3. **`@adı` ile çağır.** Mesajın herhangi bir yerinde `@sahneler.md` yazınca o dosyanın içeriği
   isteğe girer. `@` yazınca projenin dosyaları listelenir.
4. **Dosyalar sohbete değil projeye ait.** Sohbet ağırlaşınca yenisini açarsın, dosyalar durur.
5. **Dışarı çıkar.** Her dosyada Kopyala ve İndir.

## Ekran

```
┌─ PROJELER ─────────┬──────────────────────────┬────────────────────────┐
│ ▸ Yaz kampanyası   │  Sen                     │  sahneler.md    ⤓ ⧉ ✕ │
│ ▾ Kış çekimi       │  @sahneler.md 3'ü POV yap│ ────────────────────── │
│    ─ dosyalar ─    │                          │ ## 1. Kapıda           │
│      plan.md       │  Grok                    │ Geniş açı, kar…        │
│      sahneler.md ◂ │  3. sahneyi şöyle…       │                        │
│    ─ sohbetler ─   │                          │ ## 2. Şömine           │
│      ilk konuşma   │                          │ …                      │
│      prompt turu ◂ │                          │                        │
│ + Yeni proje       │  [yaz…]          Gönder  │                        │
│ ⚙ Ayarlar          │                          │                        │
└────────────────────┴──────────────────────────┴────────────────────────┘
```

Dosya kapalıyken sağ sütun yoktur, sohbet tam genişliktedir. Tasarım dili bugünkü `app.css`'in
token'ları — yeni renk, yeni yazı tipi girmez.

Başlıktaki üç işaret **indir · kopyala · kapat**'tır. **Silme ağaçtan yapılır**: dosya satırının
sağında bir `×`, sohbet satırlarındaki gibi — böylece silmek için dosyayı açmak gerekmez ve iki
liste aynı davranır.

## Veri

Bugünkü dört `localStorage` anahtarı yediye çıkar:

| Anahtar | İçerik |
|---|---|
| `projects` | `[{ id, name }]` |
| `files` | `[{ id, projectId, name, content }]` |
| `chats` | `[{ id, projectId, messages, draft }]` |
| `active_project` · `active_chat` · `active_file` | açık olanların `id`'si; `active_file` `null` olabilir |
| `xai_key` · `xai_model` | değişmez |

`id` üretimi bugünkü kuralla aynı — `max + 1`, saat yok, rastgelelik yok — böylece saf katman
stub'sız test edilebilir kalır.

Mesaj şekli bir alan daha kazanır, `skill` ile aynı mantıkta:

```js
{ role: "user", content: "@sahneler.md 3'ü POV yap", files: ["sahneler.md"] }
```

`files` yoksa mesaj bugünkü gibi davranır. **Dosya içeriği mesajda saklanmaz**, yalnız adı.

### Boş hâl

Bugünkü kural — *"hiç sohbet yoksa bir tane aç, açık olan silinirse başkasına geç"* — projeye de
uygulanır: proje yoksa **"Genel"** açılır, açık proje silinirse kalanların ilkine geçilir. Ekranda
projesiz ya da sohbetsiz bir an yoktur, ve bu her kullanım yerinde korunmak yerine tek yerde
onarılır.

`projectId`'si olmayan bir sohbet ilk projeye ait sayılır. Bu bir göç değil, tek satırlık bir
varsayılan: bugün tarayıcıda duran sohbetler deneme, taşınacak bir şey yok.

### Proje değişince

`active_chat` ve `active_file` başka bir projenin içindekini gösteriyor olabilir, o yüzden proje
değiştirmek ikisini de tazeler:

- **Açık sohbet** o projenin ilk sohbeti olur; hiç sohbeti yoksa bir tane açılır.
- **Açık dosya kapanır** — sağ sütun gider, sohbet tam genişliğe döner. Başka projenin dosyasını
  açık bırakmak, hangi projede olduğunu belirsizleştirirdi.

Aynı onarım "boş hâl" kuralıyla tek yerde yapılır; her kullanım yerinde ayrıca korunmaz.

## `@dosya` nasıl gider

Üç ayrı temsil, `/skill`'deki kalıbın aynısı:

| | İçerik |
|---|---|
| **Saklanan** | `{ role: "user", content: "@sahneler.md 3'ü POV yap", files: ["sahneler.md"] }` |
| **Ekranda** | yazdığın cümle, `@sahneler.md` dahil, olduğu gibi |
| **xAI'a giden** | dosyanın içeriği bir blok hâlinde, ardından senin cümlen |

Giden metnin biçimi:

```
`@sahneler.md` dosyasının içeriği:
---
## 1. Kapıda
…
---

@sahneler.md 3'ü POV yap
```

**Bir dosya konuşmada en fazla bir kez açılır.** Gönderirken mesajlar baştan taranır; bir dosyanın
içeriği **ilk anıldığı** mesajda tam hâliyle girer, sonraki anışlarda yalnız `@adı` kalır. Böylece
maliyet dosya sayısıyla artar, anış sayısıyla değil — ve içerik her zaman günceldir, çünkü açılım
gönderme anında yapılır.

Bir mesajda hem skill hem dosya varsa sıra şudur: **skill gövdesi → dosya blokları → senin metnin.**
Talimat önce gelir, malzeme sonra, istek en sonda.

Silinmiş bir dosyaya atıf yapan eski mesaj, **içeriksiz** gider — `@adı` metinde kalır, blok
eklenmez. Çökme yok, uyarı yok: silinen bir dosya eski bir sohbeti gönderilemez hâle getirmemeli.

Açılımı yapan yer yine `toRequestBody`. İmza dördüncü bir liste alır:
`toRequestBody(messages, model, skills = [], files = [])`. Saf bir fonksiyon, testi ağsız.

### `@` listesi

`/` listesiyle aynı davranış, tek farkı yeri: `/` yalnız mesajın başında geçerlidir, `@` her yerde.

Kural tek cümle: taslak boşluklardan bölünür, **son parça** `@` ile başlıyorsa geri kalanı arama
metnidir ve liste açılır. Seçince o parça `@adı ` ile değiştirilir. Cümlenin ortasında yazarken de
çalışır, çünkü yazarken son parça zaten yazdığın parçadır.

Bilinen sınır: liste yalnız **metnin sonuna** yazarken açılır. İmleci geri götürüp cümlenin
ortasına `@` eklersen liste çıkmaz — adı elle yazman gerekir, ki o da çalışır. İmleç konumunu
izlemek bu kazanç için fazla makine.

**Eşleşme tam addır, uzantı dahil**: `@plan` bir şey açmaz, `@plan.md` açar. Listeden seçmek tam
adı yazdığı için normal kullanımda bu görünmez.

Bir mesajda birden fazla dosya anıldığında bloklar **metinde göründükleri sırayla** dizilir.

## Silme

| Ne | Nasıl sorulur |
|---|---|
| Sohbet | bugünkü onay, aynen |
| Dosya | onay: dosyanın adı |
| Proje | onay, **ne kaybedileceğini sayarak**: "Kış çekimi — 4 dosya ve 2 sohbet silinecek" |

Projeyi silmek dosyalarını da götürür ve geri alınamaz; onayın sayı söylemesinin sebebi bu.

## Saklama sınırı

`localStorage` ~5 MB ve artık içinde elle yazılmış dosyalar da var. Ayarlar panelinde **kullanılan
alan** göstergesi olur, ve kota hatası sessizce yutulmaz: tarayıcının kendi mesajı ekrana basılır,
üstüne ne yapılacağı yazar (dosyaları indir, eski projeyi sil).

IndexedDB'ye geçmiyoruz: `usePersisted.js`'i asenkron yapmak her ekrana bir yükleniyor durumu
ekler, kanıtlanmamış bir sorun için gerçek bir karmaşıklık. **Ne zaman dönülür:** gösterge düzenli
olarak %70'i geçiyorsa, ya da biri kota hatası yediyse.

## Hatalar

| Durum | Ne olur |
|---|---|
| Aynı adda ikinci dosya | Oluşturulmaz; ad kutusunun altında "bu adda bir dosya var" |
| `@olmayan.md` yazıldı | Mesaj **gider** — `@` serbest metinde de geçebildiği için her `@` bir çağrı sayılamaz; eşleşmeyen ad sıradan metindir |
| Kota doldu | Tarayıcının `QuotaExceededError` metni aynen, üstüne ne yapılacağı |
| HTTP hatası | bugünkü `formatHttpError` |

`@`'in bilinmeyen adda **hata vermemesi**, `/`'ten ayrıldığı yer: `/plan-yazma` mesajın başında
duran bir komuttur, `@` ise cümlenin içinde geçen bir sözcük olabilir (`@herkes`, bir e-posta).
Çağrı sayılması için eşleşen bir dosya gerekir.

## Kapsam dışı

Hepsi [agent iskeleti spec'ine](2026-08-08-prompt-chat-agent-iskeleti-design.md) ait:

- **Agent döngüsü, araçlar** (`write_file`, `edit_file`, `read_file`, `list_files`)
- **Modlar** — Claude Code'daki gibi ask / edit
- **Geri alma** — bu turda yazan tek kişi sensin, agent'ın ezeceği bir şey yok
- **Tur tavanı, durdurma, token satırı**

Bu sürümde olmayan, sonra bakılacaklar:
- **Cevabı dosyaya kaydeden düğme** — dosyaya yazmanın yolu `write_file` aracıdır; ikinci bir yol
  açmak aynı işi iki mekanizmaya bölerdi
- **Yeniden adlandırma** — ad değişince eski mesajlardaki `@eski-ad` karşılıksız kalır ve o mesajlar
  sessizce içeriksiz gider
- **Klasörler, dosya taşıma, projeler arası taşıma**
- **Dosya arama** — düz bir listede birkaç dosya var

## Kararlar

| Karar | Gerekçe |
|---|---|
| Çalışma alanı döngüden **önce** | Agent'ın yazacağı zemin, o yazmadan önce denenip düzeltilir; sonraki tur yalnız döngü olur |
| Dosya projeye ait, sohbete değil | Sohbet ağırlaşınca temiz sayfayla devam edebilmek gerek; dosya sohbete bağlıysa bu imkânsız |
| Dosyaya yazan tek şey klavyen | `write_file` aracı sonraki turun konusu; kestirme bir kaydet düğmesi aynı işi iki yola bölerdi |
| `@` metnin her yerinde, `/` yalnız başta | "@x.md dosyasındaki 3. sahneyi düzelt" doğal bir cümle; skill çağırmak ise komuttur |
| Bir dosya konuşmada bir kez açılır | Maliyet dosya sayısıyla artsın, anış sayısıyla değil |
| İçerik saklanmaz, gönderirken açılır | Kayıt şişmez; dosyayı düzeltince eski mesajlar da yeni hâli taşır |
| Eşleşmeyen `@` sessizce metin sayılır | `@` sıradan yazıda geçer; her `@`'i çağrı saymak yanlış alarm üretirdi |
| Yeniden adlandırma yok | Eski mesajların atıfları sessizce boşa düşerdi |
| Geri alma yok | Yazan tek kişi sensin; agent gelince gelir |

## Doğrulama

**Önce bozmadığımızı kanıtla.**

1. **Eski davranış:** hiç proje/dosya açmadan sıradan bir mesaj at → cevap gelir, ekran bugünküyle
   aynıdır.
2. **Skill'ler:** `/plan-yazma bir şey` → etiket görünür, cevap adım listesi gelir.
3. **Kalıcılık:** sayfayı yenile → sohbetler, anahtar, model yerinde.

**Sonra yeniyi dene.**

4. **Proje:** "+ Yeni proje" → ad sorar, açılır; ikinci proje aç, aralarında geçiş yap.
5. **Dosya:** "+ Yeni dosya" → `plan` yaz → `plan.md` olarak açılır; sağda bir şeyler yaz, başka
   dosyaya geç, geri dön → yazdığın durur.
6. **Ayrım:** ikinci projeye geç → ilk projenin dosyaları görünmez.
7. **`@` listesi:** yazı kutusuna `@` yaz → projenin dosyaları listelenir; cümlenin **ortasında**
   `@` yaz → yine listelenir.
8. **Çağırma:** `@plan.md ilk maddeyi açıkla` → cevap dosyanın içeriğini bilerek gelir.
9. **Bir kez açılma:** aynı dosyayı iki mesajda an, ağ isteğine bak → içerik yalnız ilkinde.
10. **Güncellik:** dosyayı düzenle, sonra `@` ile tekrar an → model yeni hâli görür.
11. **Eşleşmeyen:** `@olmayan.md bir şey` gönder → istek gider, `@olmayan.md` düz metin sayılır.
12. **Silme:** projeyi sil → onay kaç dosya ve kaç sohbet gideceğini söyler.
13. **Sohbet ayrımı:** aynı projede ikinci sohbet aç → dosyalar orada da görünür, geçmiş ayrıdır.
14. **Testler:** `npm test` yeşil, sayı bugünkü 120'nin üstünde.
