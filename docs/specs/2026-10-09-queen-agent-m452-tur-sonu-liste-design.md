# Madde 452 · Proje listesi ve sohbet sırası, konuşunca — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
452 · **Dal:** `feat/queenagent-v10`, ana klasörde, commit ana agent'ın · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Öncesi:** [447](2026-10-09-queen-agent-m447-proje-yonetimi-design.md) (metadata bellekte, son
kullanım sohbetin son mesajı), [450](2026-10-09-queen-agent-m450-arsiv-sirasi-design.md) (listenin her
okunması tek kuyruktan)

## Ne, neden

443'ü deneyen QA'nın bulduğu, bütün projelerde; kullanıcı, 9 Ekim: *"onları da bu roadmap'te çöz"*.
**Bugün** var olan bir sohbette mesaj gönderip projeden çıkınca All projects projeyi eski yerinde ve
eski zamanıyla gösteriyor. **Olacak:** konuşulan proje, projeden çıkınca listede yeni yerinde.

**Sunucu doğru.** Bir mesaj sohbete yazılınca `FileChatStore._write` sohbetin satırını
`projects.json`'ın belleğinde yeniler (`put_chat`); satırın `lastActivity`'si sohbetin açık kolunun
son mesajının anı (`Chat.last_activity`). Projenin son kullanımı bu satırlardan hesaplanır
(`_as_project`'in `last_chat_at`'i), proje listesi (`list_projects`) ve kenar çubuğunun sohbet listesi
(`list_chats`) ona göre dizilir. Yani soru yazıldığı anda sunucunun iki listesi de yeni sırada. Bunu
bugüne kadar yalnız *doğan* bir sohbet için bir test tutuyordu
(`test_talking_in_a_project_renews_its_moment_and_brings_it_up`); var olan sohbet için yenisi
eklenir — *Testler*.

**Eksik olan ekran.** [App.jsx](../../queen-agent/frontend/src/App.jsx) proje listesini, açılıştaki
okumadan sonra, yalnız sohbet doğunca (`onChatBorn`) ve dosya doğunca (`onFileCreated`) yeniden
okuyordu; kenar çubuğunun sohbet listesini yalnız sohbet doğunca. Var olan bir sohbette dosya
yazmayan bir tur ikisine de dokunmuyordu. `useProjects` App'te yaşadığı için All projects'e dönmek de
listeyi okumuyordu.

## Olacak

### 1 · Proje listesi All projects'e girilince okunur — `App.jsx`

Proje listesinin sırası, zamanları ve sayıları yalnız All projects'te görünür; proje içinde listeden
yalnız açık projenin adı okunur (Bar), o da yalnız All projects'te değişir (Rename). Bu yüzden liste
**All projects'e girildiği an** okunur: `route.view` başka bir görünümden `"root"`'a geçince bir kez,
450'nin kuyruğundan (`reloadProjects` = `useProjects`'in `reloadInTurn`'ü).

- **İlk çizimde okumaz:** `useProjects` açılışta kendisi bir kez okur. Önceki görünüm bir `useRef`'te;
  ilk çizimde önceki görünüm şimdiki olduğu için giriş sayılmaz.
- **Kapsadığı:** proje içinde listeyi değiştiren her şey — var olan sohbette tur, tur sürerken
  projeden çıkmak (tur sonra biterse, sunucu soruyu yazdığı anda zaten yeni sıradadır), sürüm
  değiştirmek, sohbet doğması, dosya doğması ve silinmesi.
- **Kalkanlar:** `onChatBorn`'daki ve `onFileCreated`'daki `reloadProjects`. İkisi görünmeyen bir
  ekranı okuyordu — sohbet de dosya da yalnız bir sohbetin içinde doğar. Proje içinde `projects`'i
  okuyan öbür yerler — Bar'ın adı, `project`'in varlığı (*"That project does not exist."*), Escape'in
  ve adlandırma ekranının `projects.length`'i — sayıya, sıraya ya da zamana bakmıyor.
- **Kuyruk:** girişin okuması önünde bekleyen bir düzenlemeyi bekler, ve sonra basılanın listesinin
  üstüne geç gelemez (450).

### 2 · Kenar çubuğunun sohbet listesi, soru sunucuya ulaşan turun sonunda — `useChat.js`, `App.jsx`

Kenar çubuğu sohbetleri aynı anla diziyor (`list_chats`) ve aynı sebeple eski kalıyordu; ana agent'ın
brifingi onu da kontrol etmemi istedi. Kenar çubuğu tur sürerken ekranda olduğu için turun sonunda
okunur.

- `useChat`, `onTurnEnd`'e ilk karenin gelip gelmediğini verir: `ended.current?.(reached)`.
  `reached`'i 449 zaten tutuyor: ilk kare, sorunun diske yazıldığını söyler.
- App'in `onTurnEnd`'i: `refresh()` her zaman — dosya listesi ve açık dosya, *tur nasıl biterse
  bitsin* (Madde 192) —, `reloadProjectChats()` yalnız `reached` ise.
- **Neden `reached`:** ilk kare hiç gelmediyse soru yazılmamıştır, sıra değişmemiştir; ve sunucu ya da
  tünel büyük olasılıkla kapalıdır. Okuma da düşerdi, ve kenar çubuğu elindeki satırları
  *"Couldn't load chats."* ile değiştirirdi (reviewer'ın bulduğu).
- **Turda bir kez, sonunda:** `onTurnEnd` `send`'in `finally`'sinde bir kez çağrılır; akışın hiçbir
  karesi listeyi okumaz. Sona bırakılması da doğru: 440'tan beri Try again başarısız cevabı turun
  başında kayıttan çıkarır, yani son mesaj tur içinde geri de gidebilir.
- **Doğan sohbet:** ilk karedeki `reloadProjectChats` kalır — kenar çubuğu yeni sohbeti tur sürerken
  göstersin diye. Yeni sohbette kenar çubuğu turda iki kez okunur.
- **Projeden çıkılmışsa** `reloadProjectChats` açık proje olmadığı için bir şey istemez (`useList`'in
  `enabled`'ı); başka bir projedeyse onun listesini okur — bir istek, zararsız.

Değişmeyenler: Refresh düğmesi (`refresh`), dosya silmenin `useFiles`'a verilen `reloadProjects`'i
(*Sınırlar*), ve arka uç.

## Her işlemin bedeli

N proje, C projenin sohbet sayısı. Sunucunun disk sayıları 447'nin tablosundan; iki liste de
bellekten, 0 disk işlemi.

| İşlem | Bugün | 452 | Sunucunun diski |
|---|---|---|---|
| Var olan sohbette tur (ilk kare geldi) | turun sonunda sohbet kaydı, dosya listesi, açıksa açık dosya | bugünkü + **1 `GET …/chats`** | eklenen 0 |
| Yeni sohbette tur | ilk karede `GET …/chats` + `GET /api/projects`, sonunda bugünkü gibi | ilk karede yalnız `GET …/chats`; sonunda bugünkü + 1 `GET …/chats` — proje listesi 1 eksik, sohbet listesi 1 fazla | 0 |
| İlk karesi gelmeyen gönderiş | turun sonunda dosya listesi, açıksa açık dosya | aynı: liste okunmaz | 0 |
| Dosya doğması (`file` karesi) | `GET …/files` + `GET /api/projects` | yalnız `GET …/files` | 0 |
| All projects'e girmek | 0 | **1 `GET /api/projects`**, kuyrukta | 0 |
| Açılış | 1 `GET /api/projects` | aynı | 0 |
| Akışın her karesi | liste okunmaz | aynı | 0 |

- Her satır O(1) istek: proje, sohbet ve dosya sayısıyla büyümez. Cevapların boyu O(N) ve O(C) bayt;
  ikisi de ekranda bütün olarak duran listeler.
- Proje içinde geçen bir oturum proje listesini artık hiç okumaz — kaç tur, kaç dosya olursa olsun;
  çıkınca bir kez okunur. Bugün her doğan sohbet ve dosya bir okumaydı.
- Girişin okuması kuyrukta: önünde bir düzenleme varsa onun gidiş-dönüşlerini bekler (450). Bu arada
  All projects eski listeyi çizer, ve liste gelince satırlar yer değiştirebilir.

## Sınırlar

- **Girişte bir an eski sıra.** All projects'e girilince liste, yeni okuma gelene kadar App'in elindeki
  eski hâliyle çizilir; Drive'ın tünelinde bu bir gidiş-dönüş. Bekleme ekranı gösterilmez: açılıştaki
  ilk okumadan farklı olarak elde bir liste var.
- **Pinli proje** pinliler arasındaki yerinde kalır: sıra sunucunun kuralı (pinliler önce, pin
  sırasıyla; Madde 384, `list_projects.py`). "Listenin başında" pinsiz projeler içindir.
- **Girişte okuma düşerse** `useProjects`'in `reload`'u bugünkü gibi `error`'u yazar ve All projects
  hatayı gösterir. Bu, sunucunun gerçekten okunamadığı an; App'in eski listesi o an doğru olmayabilir.
- **Sohbet listesinin kuyruğu yok.** Yeni sohbette ilk karenin okuması sonunkinden geç gelirse eskisi
  çizilir; bu ancak o okumanın bütün turdan uzun sürmesiyle olur. Başka projeye geçince eski projenin
  geç gelen cevabı ve sürüm değiştirmenin kenar çubuğunu eski bırakması ana agent'ın backlog'unda.
- **Dosya silmenin `reloadProjects`'i** (`useFiles(route.projectId, reloadProjects)`) kalır: o da
  görünmeyen bir ekranı okuyor, ama ana agent'ın onayı `onChatBorn` ve `onFileCreated` içindi.
- **İki sekme:** öbür sekme All projects'e girince okur.
- Arka uç değişmez; queen-editor'e dokunulmaz.

## Değişen dosyalar

- `queen-agent/frontend/src/App.jsx` — All projects'e girişte `reloadProjects`; `onChatBorn` ve
  `onFileCreated`'dan `reloadProjects` kalkar; `onTurnEnd` `refresh` ve, `reached` ise,
  `reloadProjectChats`.
- `queen-agent/frontend/src/features/workspace/useChat.js` — `ended.current?.(reached)`.
- `queen-agent/frontend/src/App.test.jsx` — iki yeni test.
- `queen-agent/backend/tests/test_last_activity.py` — yeni test.
- `queen-agent/frontend/dist` yeniden derlenir.

## Testler

**Sunucu (`test_last_activity.py`):** iki proje, eskisinde iki sohbet, hepsi 2000'den — testte
söylenen hiçbir şey onlarla aynı ana düşmesin diye. Eski projenin eski sohbetinde mesaj gönderilince:
proje listede öne geçer, son kullanımı yenilenir, ve sohbet projenin sohbet listesinde öne geçer.

**Ekran (`App.test.jsx`):**

- Var olan bir sohbette tur: akış kareleri gelirken sohbet listesi yeniden okunmaz; tur bitince bir
  kez okunur ve kenar çubuğunda sohbet öne geçer; proje listesi turda hiç okunmaz. Exit project'ten
  sonra All projects'te proje başta, zamanı *just now*, ve liste girişte bir kez okunmuş (toplam 2:
  açılış ve giriş). Değişiklikten önce kırmızı: kenar çubuğu eski sırada kalıyordu.
- İlk karesi gelmeyen gönderiş (bağlantı hatası): hiçbir liste okunmaz, kenar çubuğu satırlarını
  tutar, *"Couldn't load chats."* yok.
- Açılışta liste bir kez okunur: 450'nin testleri (`sent(fetch)` ilk okumayı tek sayıyor) bunu zaten
  tutuyor, değişmeden geçer.

## Bitti sayılır

- Yukarıdaki testler yeşil, dört suite sırayla yeşil, `dist` yeniden derlenmiş.
- Kullanıcının denemesinde: var olan bir sohbette konuşup projeden çıkınca proje listenin başında
  (pinliler dışında), son kullanım zamanı yeni; kenar çubuğunda konuşulan sohbet en üstte.
