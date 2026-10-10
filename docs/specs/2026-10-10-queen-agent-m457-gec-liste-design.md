# Madde 457 · Geç gelen liste başka bir projenin kenar çubuğuna çizilmez — tasarım

**Tarih:** 10 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
457 · **Dal:** `feat/queenagent-v10`, ana klasörde, commit ana agent'ın · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Öncesi:** [452](2026-10-09-queen-agent-m452-tur-sonu-liste-design.md) (turun sonunda kenar çubuğu
okunur; *Sınırlar*'ında bu hata backlog'a yazıldı)

## Ne, neden

452'nin reviewer'ının bulduğu, backlog'dan; kullanıcı, 10 Ekim: *"ilk yukarıdaki 3 hatayı çöz"*.
**Bugün** [useList.js](../../queen-agent/frontend/src/shared/useList.js) gelen cevabın hangi okumaya
ait olduğuna bakmıyor. A projesinin sohbet listesi okunurken kullanıcı projeden çıkıp B'yi açar, ve
A'nın cevabı B'ninkinden sonra gelirse, `setItems` onu B'nin cevabının üstüne yazar: B'nin kenar
çubuğunda A'nın sohbetleri durur, birine tıklamak *"chat missing"* der. **Olacak:** yolu artık geçerli
olmayan cevap yok sayılır; ekran açık projenin listesini çizer.

Aynı hatanın ikinci bir penceresi var, geç cevap olmadan da: hook yol değişince elindeki satırları
bırakmıyordu. B açıldığı an, B'nin cevabı gelene kadar — tünelde bir gidiş-dönüş — kenar çubuğu A'nın
sohbetlerini, dosya paneli A'nın dosyalarını gösteriyordu; birine tıklamak yine *"chat missing"*.
Maddenin *bitti* satırı (*"B'nin kenar çubuğunda yalnız B'nin sohbetleri var"*) ikisini birden ister;
reviewer'ın bulduğu, ana agent'ın kararı: ikisi de 457'de kapanır.

## useList'i kullananlar

`useList`'in iki kullanıcısı var, ikisi de aynı yarışa açık, ikisi de `App.jsx`'te `route.projectId`'ye
bağlı:

- `useProjectChats` (`useChatLists.js`) — kenar çubuğunun sohbetleri, `/api/projects/<id>/chats`.
- `useFiles` (`useFiles.js`) — dosya paneli, `/api/projects/<id>/files`. A'nın dosyaları B'nin
  panelinde dururdu; birine tıklamak B'de olmayan bir dosyayı açmaya çalışırdı.

Kural `useList`'in içine yazılır, ikisi de onu alır. `useFile` (açık dosya) ve `OpenProject` kendi
okumalarını zaten bu kuralla yapıyor (`current`/`cancelled`, `left`) ve `useList`'i kullanmıyor;
dokunulmaz.

## Olacak

### 1 · Cevap, ait olduğu yolla tutulur — `useList.js`

Hook'un üç hâli — `items`, `loading`, `error` — iki hâle iner, ikisi de yoluyla birlikte:

- `answer = { path, items }` — son kabul edilen cevap ve hangi yolun cevabı olduğu. Başlangıçta
  `{ path: null, items: [] }`.
- `failure = { path, message }` ya da `null` — son kabul edilen düşüş ve hangi yolunki.

Döndürülenler çizimde, şimdiki yoldan hesaplanır:

- `items`: `answer.path === path` ise `answer.items`, değilse `[]`. Yol değiştiği çizimde eski yolun
  satırları artık verilmez — effect'in yeni okumayı başlatmasını beklemeden.
- `error`: `failure.path === path` ise `failure.message`, değilse `null`. A'nın hatası da B'ye
  taşınmaz.
- `loading`: `enabled && !answered && !error` — sorulmuş, ne cevaplanmış ne düşmüş bir yol.
  `useState(enabled)` ve `finally`'deki `setLoading(false)` kalkar: bekleme bir durum değil, iki
  durumdan okunan bir sonuç.

**Düşüş cevap sayılmaz.** Reviewer'ın önerdiği biçimde `.catch` de "cevaplanan yolu" yazıyordu; bu iki
yerde yanlış çizer, bu yüzden düşüş `answer`'a dokunmaz, kendi yoluyla `failure`'a yazılır:

- B'nin ilk okuması düşerse `answer` hâlâ A'nın: `items` `[]`, `error` B'nin. "Cevaplandı" diye
  işaretlenseydi `items` A'nın satırları olurdu — kenar çubuğu hata varken satır çizmiyor, ama dosya
  paneli hatanın altında A'nın dosyalarını çizerdi (`FileList` `!loading && files.length`).
- O düşüşten sonra Try again: `setFailure(null)`, yol cevapsız, `loading` yine doğru — kenar çubuğu
  bekleme süresince *"No chats yet."* demez.
- Aynı yolun bir yeniden okuması düşerse `answer` o yolun: satırlar yerinde durur, hata yanında —
  bugünkü gibi (*"a reload that fails leaves the list that was already there"*).

### 2 · Her okumanın bir sırası var

Hook bir `useRef` sayaç tutar. `reload` her çağrıldığında — `enabled` yanlışken de — sayacı bir
artırır ve kendi numarasını alır; cevabı ya da düşüşü, numarası sayacın şimdiki değeriyse yazılır.

- **Başka bir yol:** yolla tutmak zaten A'nın geç cevabını B'de çizmez, ama B'nin cevabının *üstüne*
  yazılmasını engellemez — A'nın geç cevabı `answer`'ı `{ path: A }` yapıp B'nin cevabını silerdi, ve B
  yeniden bekleme gösterirdi. Sayaç onu yazdırmaz.
- **Aynı yolun eski okuması:** yeni sohbette ilk karenin okuması ve turun sonundaki (452), ya da Try
  again ile turun sonu üst üste — önce istenenin cevabı sonra gelirse yenisinin sırasını ezmez. İkisi
  de aynı yolun cevabı olduğu için bunu yalnız sayaç ayırır. 452'nin *Sınırlar*'ında kalan durum bu.
- **Kapalı hook:** açık proje yokken (All projects) istek atılmaz ama sayaç artar; A'dan çıkınca A'nın
  yoldaki cevabı yazılmaz. `answer` kapalıyken silinmez: A'dan çıkıp yine A açılırsa elde A'nın kendi
  son cevabı var (`answer.path === path`), ve o yeniden okunurken ekranda durur — *Sınırlar*.
- Yeni bir okuma `setFailure(null)` ile başlar, bugünkü `setError(null)` gibi. `reload`'un döndürdüğü
  söz değişmez: `useFiles`'ın `remove`'u (`await reload()`) ve App'in `refresh`'i bugünkü gibi bekler.

### 3 · Kenar çubuğu bekler — `useChatLists.js`, `App.jsx`, `Sidebar.jsx`

- `useProjectChats` `loadingChats: projectId ? loading : false` da döndürür; App onu Sidebar'a
  `loading` olarak verir.
- Sidebar'ın `.sidebar__chats`'i `loading` iken — hata yokken — boş kalır: satır yok, *"No chats
  yet."* yok, eşleşme cümlesi yok; Enter bir şey açmaz. `loading`, projenin elde kendi cevabı
  olmadığı aralıktır: başka bir projeden gelindiğinde, ya da ilk okuması düşmüş bir listenin Try
  again'inde. Projenin kendi son cevabı eldeyse `loading` yanlıştır ve o satırlar durur. Tasarımın kenar çubuğunda bekleme hâli yok
  (`DESIGN-STANDARD.md`, *Sidebar*: yalnız satırlar, `sidebar__empty` ve okunamama hâli), bu yüzden
  spinner da yok. New chat, Search chats ve katlama düğmesi yerinde.
- Hata önce gelir: `error` varsa okunamama kartı, `loading` ne olursa olsun (hook ikisini birden
  vermez).
- `useChatLists.js`'in `readChats` yorumu yeniden yazılır: hook artık eski projenin satırlarını
  tutmuyor; `OpenProject`'in ayrı okuması, bir cevaba bakıp bir kez atılan adım olduğu için — en yeni
  sohbete git, ya da taslağa, ve kullanıcı çıktıysa hiçbir yere — duruyor. Bir proje açılırken sohbet
  listesinin iki kez okunması zaten backlog'da; dokunulmaz.

### 4 · Dosya paneli bekler — `FileRail.jsx`'te yalnız sayı

`useFiles` `loadingFiles: loading`'i zaten veriyor, `FileList` `loading` iken spinner'ını çizer ve
satırları da boş cümlesini de çizmez. Bugün `loading` yalnız ilk okumada doğruydu; 457'den sonra elde
kendi cevabı olmayan her projenin okumasında doğru, ve panel o aralıkta spinner'ını gösterir; App
testi bunu görür.

Tek eksik başlığın sayısıydı (QA'nın bulduğu): `rail__count` `files.length`'ten okunuyor, ve spinner
dönerken *0* diyordu — proje dosyasız demek. `loading` iken başlık sayı çizmez; açık, katlı ve
genişlik yüzünden katlı üç başlıkta da. `rail__label` `flex: 1` olduğu için başlığın düzeni sayısız da
aynı.

## Her işlemin bedeli

| İşlem | Bugün | 457 |
|---|---|---|
| Bir listenin okunması | 1 `GET` | aynı, 1 `GET` |
| Proje değişince | yeni yol için 1 `GET` | aynı |
| Eski okumanın cevabı | ekrana yazılır | bir sayı karşılaştırması, yazılmaz |
| Her çizim | — | iki dize karşılaştırması |

Yeni istek yok, yeni disk işlemi yok. Proje, sohbet ve dosya sayısıyla büyüyen bir şey eklenmez. Eski
okuma iptal edilmez (`AbortController` yok): istek zaten yolda, cevabı ağdan iner ve atılır —
sunucuyu da tüneli de bugünkü kadar yorar, fazlasını değil.

## Sınırlar

- **Başka bir projenin satırları hiç çizilmez; projenin kendi son cevabı yeniden okunurken durur.**
  Kural bu, bilerek seçilmiş (hook testi tutuyor). Elde başka bir projenin listesi varken açılan
  projenin kenar çubuğunun satır yeri boş, dosya panelinde spinner, kendi listesi gelene kadar —
  tünelde bir gidiş-dönüş; boş yer yanlış bir satırdan ve *"No chats yet."*'ten iyi. Elde projenin
  kendi son cevabı varsa — tur sonu, Refresh, ya da All projects'e çıkıp en son okunan projeye geri
  dönmek — o satırlar yeni okuma gelene kadar durur, beklenmez, ve Enter ya da tıklama onlardan birini
  açabilir. Onlar bu projenin satırları; bir gidiş-dönüşten eski olabilirler, başka bir projeninki
  olamazlar. Yalnız ilk okuması düşmüş bir listenin Try again'i bekler, çünkü elde o projenin hiçbir
  satırı yok.
- **Eski okuma iptal edilmez** — yukarıda, *bedel*.
- **`OpenProject`'in ayrı okuması** kalır (backlog'da).
- **Sunucu, `useFile`, `OpenProject`, `useProjects`, `useFiles`** değişmez; queen-editor'e
  dokunulmaz.

## Değişen dosyalar

- `queen-agent/frontend/src/shared/useList.js` — `answer` ve `failure` yollarıyla, sayaç; `loading`
  hesaplanır.
- `queen-agent/frontend/src/features/workspace/useChatLists.js` — `loadingChats`; `readChats`'in
  yorumu.
- `queen-agent/frontend/src/features/workspace/Sidebar.jsx` — `loading` iken satır yeri boş; yorum.
- `queen-agent/frontend/src/App.jsx` — `loadingChats` Sidebar'a.
- `queen-agent/frontend/src/features/workspace/FileRail.jsx` — `loading` iken başlıkta sayı yok.
- Testler: `useList.test.jsx`, `Sidebar.test.jsx`, `FileRail.test.jsx`, `App.test.jsx`.
- `queen-agent/frontend/dist` yeniden derlenir.

## Testler

**Hook (`useList.test.jsx`)** — cevapları test elle, istediği sırada bırakır:

- A okunurken yol B'ye geçer; B'nin cevabı gelir, sonra A'nınki: liste B'nin.
- A okunurken yol B'ye geçer; B'nin cevabı gelir, sonra A'nın okuması düşer: hata yok, liste B'nin.
- A okunurken yol B'ye geçer, A'nın cevabı gelir, B'ninki daha yolda: hâlâ yükleniyor, liste boş; B
  gelince yerleşir.
- A cevaplanır, yol B'ye geçer, B yolda: satır yok, yükleniyor; B gelince B'nin satırları.
- A cevaplanır, hook kapanır, yine A açılır, okuması yolda: A'nın son satırları, beklemiyor; yeni
  cevap gelince onun satırları. Bugünkü davranışı tutar — seçildiğini söylemek için.
- A cevaplanır, yol B'ye geçer, B'nin ilk okuması düşer: hata B'nin, yerleşmiş, satır yok.
- İlk okuması düşen liste yeniden istenince hata gider ve yine yükleniyor.
- Aynı yol iki kez okunur; ikincisinin cevabı önce, birincininki sonra gelir: liste ikincinin.
- Bugünkü altı test değişmeden geçer.

**Kenar çubuğu (`Sidebar.test.jsx`):** `loading` iken ne satır ne *"No chats yet."*; Search chats
yerinde.

**Dosya paneli (`FileRail.test.jsx`):** spinner dönerken başlıkta sayı yok — açık, katlı, genişlik
yüzünden katlı.

**Ekran (`App.test.jsx`):**

- A'nın sohbet listesi bekletilir; Exit project, B açılır, B'nin sohbetleri kenar çubuğunda; sonra
  A'nın cevabı bırakılır: kenar çubuğunda yalnız B'nin sohbetleri.
- A'nın sohbetleri ve dosyası gelir; Exit project, B açılır, B'nin sohbetleri ve dosyaları bekletilir:
  kenar çubuğunda satır yok, *"No chats yet."* yok; B'nin sohbetleri gelince yalnız onlar, ve dosya
  panelinde A'nın dosyası yok, spinner var.

Hepsi değişiklikten önceki kodla (HEAD'in `useList.js`, `useChatLists.js`, `Sidebar.jsx`,
`App.jsx`'i, sayı testi için o anki `FileRail.jsx`) kırmızı görüldü, sonra yeşil — kendi son cevabını
tutan hook testi dışında: o var olan davranışı tutar, ilk koşuşta yeşildi.

## Bitti sayılır

- Yukarıdaki testler yeşil, dört suite sırayla yeşil, `dist` yeniden derlenmiş.
- Kullanıcının denemesinde: A'nın listesi gecikirken B'ye geçilince B'nin kenar çubuğunda yalnız B'nin
  sohbetleri var, ve A'nın geç gelen cevabı onu değiştirmiyor; B açılırken A'nın hiçbir sohbeti ya da
  dosyası görünmüyor.
