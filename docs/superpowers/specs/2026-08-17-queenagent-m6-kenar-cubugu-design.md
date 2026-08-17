# Madde 6 — Kenar çubuğu kuralı ve logo · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 6](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynaklar:** fark 2, 8, 9 · **karar 6, 15** · `HANDOFF.md` §2, §7
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queenagent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queenagent/CODE-STANDARD.md)

---

## 0 · Kaynak düzeltmesi ve karara bağlanan bir teknik nokta

Yol haritası bu maddeyi *"karar 15, 18"* ile etiketliyor. **Karar 18 Beceriler'i konu alıyor** ve
arayüz ayağı Madde 27'ye ait; buradaki logo kararı **karar 6**'dır: *"Logo karesi kalkıyor — yerine
bir şey konmuyor."*

**Sorulmayan, mevcut kuraldan türetilen tek teknik nokta: boş sohbet ekranının adresi.** Karar 15
"New chat" basınca **bulunulan projede** yeni bir sohbetin açılmasını istiyor, yol haritası da bunu
*"boş bir sohbet ekranı"* diye tarif ediyor. Ama bir sohbet **ilk mesajıyla doğuyor** (`start_chat`:
*"there is no empty chat"*), yani basıldığı anda sunucuda yaratılacak bir şey yok. İki okuma vardı:
adressiz geçici bir hâl, ya da kendi adresi olan bir taslak ekranı.

**Karar: `/p/<pid>/c/new`.** Sebebi bir tercih değil, repoda yazılı bir kural: `useRoute`'un kendi
sözleşmesi *"the address bar is the source of truth for which screen is open, so a reload does not
lose the user's place"*. Adressiz bir hâl bu kuralı bozar — sayfa yenilenince kullanıcı yazmakta
olduğu boş sohbetten atılır. `new` bir sohbet kimliği olamaz, çünkü kimlikleri sunucu `c` + uuid
olarak üretir; çakışma yok.

İlk mesaj gönderilince bugünkü yol aynen işler: `POST /api/projects/<pid>/chats` sohbeti doğurur ve
adres gerçek kimliğe döner. Bu geçiş **`replaceState`** ile olur — Madde 3'te açılan çatalla aynı
gerekçe: taslak adresi geçmişte bırakmak, geri tuşunu artık var olmayan bir taslağa götürür.

---

## 1 · Ne çalışır

### 1.1 · Kenar çubuğu proje seçiliyken ve seçili değilken

| Bölüm | Proje seçili | Proje seçili değil |
|---|---|---|
| Kelime markası | var | var |
| "New chat" | var | **yok** |
| "Projects" başlığı + "+" + liste | var | var |
| "Recent chats" | var | **yok** (başlığıyla birlikte) |

"Proje seçili değil" hâli pratikte yalnız **hiç proje yokken** görülür: Madde 3'ün çatalı proje
varken kullanıcıyı zaten bir projeye indiriyor. Yine de kural `route.projectId`'ye bağlanır, proje
sayısına değil — karar 15 böyle diyor ve doğrusu da bu: koşul "sohbet nereye düşecek" sorusudur,
"proje var mı" sorusu değil.

Madde 3'te konan geçici kural (`projects.length > 0` ise "New chat" çizilir) bununla değişir.

### 1.2 · "Recent chats" artık projenin sohbetleridir

Bölüm **yalnız bulunulan projenin** sohbetlerini, **en çok 8** tanesini listeler. Bu, çalışma alanı
genelinde son sohbetler diye bir kavramın kalmaması demektir:

- `GET /api/chats` uç noktası ve `list_recent_chats` use case'i **ölür** — tek çağıranı buydu.
- Ön yüzde `useRecentChats` ölür; kenar çubuğu `useProjectChats`'in zaten okuduğu diziyi alır.

Böylece **aynı soruya iki yerden cevap verilmesi de biter**: proje ekranındaki sohbet listesiyle
kenar çubuğundaki liste artık tek bir diziden çiziliyor. `useChatLists.js`'teki *"Two lists, two
questions"* yorumu artık doğru değil ve düzeltilir.

**8 sınırı ön yüzdedir, sunucuda değil.** Sunucu projenin sohbetlerini olduğu gibi veriyor; proje
ekranı hepsini gösteriyor, kenar çubuğu ilk 8'ini. Sunucuya sınır koymak, aynı listeyi iki farklı
uzunlukta isteyen iki ekran için iki uç nokta demek olurdu.

### 1.3 · "New chat" boş bir sohbet ekranı açar

Basınca adres `/p/<pid>/c/new` olur. O ekran:

- sohbet başlığı yerine **"New chat"** yazar, `← proje adı` başlığı yerinde durur,
- mesaj listesi boştur — "bulunamadı" değil, henüz hiçbir şey söylenmemiş bir sohbet,
- composer çalışır; ilk gönderim sohbeti doğurur ve adres gerçek kimliğe **değiştirilir**,
- dosya rayı projenin dosyalarını normal şekilde gösterir.

`useChat` bu adreste sunucuya **hiç sormaz**: sorulacak bir kimlik yok.

### 1.4 · Logo karesi gider

`sidebar__mark` ve CSS'i gider; tepede yalnız serif kelime markası kalır. Yerine bir şey konmaz
(karar 6).

---

## 2 · Ne kalmıyor / ne kalıyor

**Ölür:** `GET /api/chats`, `list_recent_chats`, `useRecentChats`, `sidebar__mark`,
Madde 3'ün geçici `openNewChat` bağı.

**Kalır:** `GET /api/projects/<pid>/chats`, `useProjectChats`, proje ekranının kendi sohbet listesi
(sınırsız), sohbet ekranının `← proje adı` başlığı.

---

## 3 · Katman denetimi

Bir use case ve bir rota siliniyor, yeni bir görünüm hâli (`c/new`) ekleniyor. Görünüm kararı
`useRoute`'ta ve `App.jsx`'te duruyor — hangi ekranın çizileceği bileşim kökünün sorusu.
`presentation → domain ← data → services` değişmiyor; üç yasak zorlanmıyor. Yeni bir uç nokta, yeni
bir port, yeni bir servis yok.

---

## 4 · Kabul ölçütü

1. Proje seçiliyken kenar çubuğunda "New chat" ve "Recent chats" vardır; seçili değilken ikisi de
   yoktur (başlıklarıyla birlikte).
2. "Recent chats" yalnız o projenin sohbetlerini listeler ve en çok 8 satır çizer.
3. "New chat" adresi `/p/<pid>/c/new` yapar; ekran boş bir sohbettir ve sunucuya sohbet sorulmaz.
4. Boş sohbette ilk mesaj gönderilince sohbet doğar ve adres gerçek kimliğe **replace** ile geçer.
5. `GET /api/chats` **404** döner ve `list_recent_chats` import edilemez.
6. Kenar çubuğunun tepesinde logo karesi yoktur.

## 5 · Risk

`/p/<pid>/c/new`'in `useChat`'e sızması: kanca bu kimliği gerçek sanıp sunucuya sorarsa ekran "That
chat does not exist." der. Kural tek yerde durur — `App.jsx` `useChat`'e `new` yerine `null` geçer —
ve testi bunu tutar.
