# Madde 450 · Arşivle Unarchive'ın sırası — tasarım

**Tarih:** 9 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
450 · **Dal:** `feat/queenagent-v10`, ana klasörde, commit ana agent'ın · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Öncesi:** [441](2026-10-09-queen-agent-m441-arsiv-undo-yok-design.md) (Archive satırı hemen
çıkarır), [447](2026-10-09-queen-agent-m447-proje-yonetimi-design.md) (metadata bellekte, tek yazıcı)

## Ne, neden

441'i okuyan reviewer'ın bulduğu, Undo'da da vardı; kullanıcı, 9 Ekim: *"onları da bu roadmap'te
çöz"*. **Olacak:** son basılan kazanır — ekran da, sunucunun yazdığı da son isteği gösterir.

Bugün iki ayrı yerde sıra kayboluyor:

- **Ekran.** [AllProjectsScreen.jsx](../../queen-agent/frontend/src/features/workspace/AllProjectsScreen.jsx)
  Archive'a basılan projeyi cevabı gelene kadar `leaving`'de tutar ve arşivli çizer. Unarchive
  `leaving`'e dokunmaz: arşivin cevabı gelene kadar proje arşivli çizilir, Unarchive önce cevaplasa
  bile.
- **İstekler.** [useProjects.js](../../queen-agent/frontend/src/features/workspace/useProjects.js)'in
  `editProject`'i her basışta hemen bir PATCH, cevabından sonra bir `GET /api/projects` gönderir. İki
  basışın istekleri yan yana yola çıkar; tarayıcı onları ayrı bağlantılardan gönderebilir, ve tünelin
  arkasındaki Flask her isteği kendi iş parçacığında karşılar. Böylece:
  - iki PATCH ters sırayla işlenebilir — Unarchive önce, Archive sonra — ve sunucu, ekranın en son
    istediğinin tersini yazar;
  - PATCH'ler doğru sırada işlense bile, Archive'dan sonra okunan liste Unarchive'dan sonra okunandan
    geç gelebilir ve onun üstüne çizilir: ekran, sunucunun artık tutmadığı bir arşivi gösterir.

Sunucu tarafı doğru: 447'den beri bir PATCH belleği kilidin altında değiştirir, yazıcı belleğin
**o anki** hâlini yazar; sunucu istekleri hangi sırayla alırsa o sırayla uygular. Sırayı bozan, iki
basışın isteklerinin sunucuya hangi sırayla vardığını kimsenin söylememesi.

## Olacak

### 1 · Listenin okunması ve her yazma sunucuya birer birer, sırayla gider — `useProjects.js`

**Kural, tek cümle:** liste bir kez geldikten sonra, listenin her okunması ve projeye her yazma tek bir
kuyruktan geçer. Bir iş, ondan önceki iş geri gelince yola çıkar. Kuyruğa girenler:

- `editProject` (ad, pin, arşiv) — PATCH'i **ve** ardından okunan liste, tek bir iş;
- `removeProject` — DELETE;
- `reloadProjects` — App'in kendi okuması (sohbet doğunca, dosyalar değişince); App ona artık
  kuyruktan geçen hâlini alır.

Girmeyenler: ilk okuma (ondan önce basılacak bir liste yok), onun *Try again*'i (liste okunamamışken
basılacak bir şey yok, ekran hatayı gösteriyor) ve yeni proje (aşağıda, *Sınırlar*).

**Kuyruk — `inTurn.js`:** `inTurn()` bir sıra döner; `queued(task)` işi sıranın sonuna ekler, işin
kendi sözünü (`Promise`) döner, ve sıranın kendisi işin sonucunu beklemekle yetinir
(`last = run.catch(() => {})`). Çağıran işin sonucunu da reddini de alır; reddedilen ya da fırlatan
bir iş sonrakini durdurmaz. Bugün hiçbir iş reddetmiyor — `editProject` ve `removeProject` reddi
`writeError`'a yazar, `reload` okunamayanı `error`'a —; sıra bunu varsaymaz. `useProjects` sırayı
bir kez kurar (`useState(() => inTurn())`), böylece `reloadProjects` de değişmeyen bir fonksiyon
olarak kalır.

- **Sunucu son basışı yazar:** ikinci PATCH, birincinin cevabı geldikten sonra gönderilir; o an
  sunucu birinciyi işlemiş, belleğini değiştirmiştir. İkinci, onun üstüne uygulanır. Yazıcı belleğin
  son hâlini yazar, ve yeniden yüklenince son basılan durur.
- **Ekran son listeyi çizer:** her okuma, kendisinden önceki yazma geri geldikten sonra gider ve
  sonraki yazma ondan sonra; geç gelen eski bir liste yenisinin üstüne çizilemez. Bu, üç yolu kapatır:
  - Archive'ın listesi Unarchive'ınkinden geç gelip projeyi arşivli çizerdi;
  - Exit project'ten sonra süren bir akış bir dosya yazınca App'in `reloadProjects`'i All projects
    açıkken okur (`useChat`'in haberi, `App.jsx`'in `reloadProjects`'i); o liste bir arşivin
    listesinden geç gelip projeyi yeniden Projects'te çizebilirdi;
  - A arşivlenirken B silinirse, A'nın arşivden önce okunmuş bir listesi silmeden sonra gelip B'yi
    yeniden çizebilirdi (441'den önce de vardı; kuyruk, silme dışarıda kalsaydı bu aralığı
    genişletirdi).
- **Neden tek kuyruk, proje başına değil:** her liste bütün projeleri söyler. A'nın pininden sonra
  okunan liste, B'nin arşivinden sonra okunandan geç gelip B'yi arşivsiz çizebilirdi. Bedeli: farklı
  projelerde arka arkaya işler de birbirini bekler; her biri sunucuda O(1) olduğu için bekleme birkaç
  gidiş-dönüş.

Neden ön uçta, sunucuda değil: sunucu iki isteğin hangisinin sonra basıldığını bilemez — bilmesi için
her isteğe bir sıra numarası, sunucuda proje başına son görülen numara gerekirdi: yeni bir alan, yeni
bir durum, iki tarafta kod. Sırayı bilen tarayıcı, ikincisini birincisi bitince göndermekle yetinir.

### 2 · Ekran son basışı gösterir — `AllProjectsScreen.jsx`

`leaving` (Archive'ı bekleyen projelerin listesi) yerini `asked`'e bırakır: proje id'si → **son
basışı** (`{ archived }`), o basışın cevabına kadar. Ekran projeyi sunucunun listesinde yerinde, ama
son basışın istediği gibi — arşivli ya da değil — çizer.

- Her basış (Archive da Unarchive da) kendi kaydını yazar, öncekinin yerine. Cevabı gelince kaydı
  yalnız hâlâ kendisininse siler: önceki bir basışın cevabı, sonraki basışın kaydına dokunmaz. Kaydın
  kime ait olduğunu nesnenin kimliği söyler; sayaç gerekmez.
- Son basışın cevabı geldiğinde sunucunun listesi, kuyruk sayesinde, o basıştan sonra okunmuş
  listedir; proje oradan çizilir — kabul edildiyse istenen yerde, reddedildiyse eski yerinde ve
  sunucunun sözü listenin üstünde (`writeError`, bugünkü gibi).
- **Unarchive da artık hemen çıkarır.** 441, *"Unarchive bugünkü gibi sunucuyu bekler: madde onu
  istemiyor"* demişti. 450'de Unarchive'ın, bekleyen bir arşivi o anda geçmesi gerekiyor; bunun için
  kendi basışını kaydetmesi lazım, ve kaydedince satır hemen Projects'e geçer. Yalnız bir arşiv
  beklerken kaydetmek bir özel durum, bir dal daha olurdu; iki basış aynı yolu izler. Reddedilen
  Unarchive projeyi Archived'a geri getirir, reddedilen Archive gibi.
- **Odak:** Archive'da odak 441'deki gibi devredilir. Unarchive'dan sonra odak 451'in maddesi; burada
  değişmez.
- Beklerken proje sunucunun listesindeki yerinde çizilir, 441'deki gibi: pinli bir proje arşivlenip
  hemen geri alınırsa, cevap gelene kadar Pinned'da durur ve cevapla Recent'e geçer — pinin arşivle
  gitmesi sunucunun kuralı (Madde 384), ekranda kopyası yazılmaz (FOUNDATION, Karar 4).

## Her işlemin bedeli

Sunucu değişmez; sayılar 447'nin tablosundan.

| İşlem | Ağ | Sunucunun diski |
|---|---|---|
| Archive ya da Unarchive basışı | 1 PATCH + 1 `GET /api/projects`, sırayla — bugünkü gibi | istekte 0; yazıcıda 2 (`projects.json.writing` + yerine koymak), O(1) |
| Archive'dan hemen sonra Unarchive | 4 istek, hepsi sırayla — bugün aynı 4, yan yana | istekte 0; yazıcıda en çok 4 — yazıcı ikisini tek yazmada toplayabilir, ve son hâl diskteki metinle aynıysa hiç yazmaz (447'nin kuralı) |
| Proje silmek | 1 DELETE, kuyrukta — bugünkü gibi tek istek | 447'nin tablosundaki gibi, O(1) |
| Liste (`GET /api/projects`) | 1 istek, kuyrukta | bellekten, 0 |

- İstek sayısı değişmez; değişen, sonraki işin isteklerinin öncekinin gidiş-dönüşlerini beklemesi.
  Ekran beklemez: satır basışta yer değiştirir.
- Proje, sohbet ve dosya sayısıyla hiçbir şey büyümez: her basış O(1) istek, sunucuda O(1) disk
  işlemi. Kuyruk bellekte tek bir söz.

## Sınırlar

- **Arka uç değişmez.** İstekleri geldiği sırayla uygulamak zaten doğru; sırayı ön uç verir.
- **Bir sekme.** Kuyruk bir sayfanın içinde. İki sekmede aynı projeye basılırsa sunucu hangisi önce
  gelirse onu önce uygular; o sekmelerin birbirinden haberi yok, bugünkü gibi.
- **Yeni proje kuyruğa girmez.** POST'u ve ardından okunan liste kuyruğun dışında. Bu güvenli: yeni
  proje adlandırma ekranından doğar, ve o ekran All projects'teki her basışla onun arasında durur —
  bir ad yazmak, kuyrukta bekleyenin birkaç gidiş-dönüşünden uzun sürer. Yeni projenin reddi de
  bugünkü gibi adlandırma ekranına gider.
- **Asılı kalan bir istek** kuyruktaki sonraki her işi de bekletir: düzenlemeleri, silmeleri ve
  App'in okumalarını. `fetch`'in kendi zaman aşımı yok; ama kopan bir bağlantı `fetch`'i reddeder,
  ve tünel cevapsız bir isteği kendisi kapatır — o iş reddedilince kuyruk sürer, sonsuza dek
  kilitlenmez.
- queen-editor'e dokunulmaz.

## Değişen dosyalar

- `queen-agent/frontend/src/features/workspace/inTurn.js` — yeni: sıra.
- `queen-agent/frontend/src/features/workspace/useProjects.js` — `editProject`, `removeProject` ve
  dışarı verilen `reloadProjects` sırada.
- `queen-agent/frontend/src/features/workspace/AllProjectsScreen.jsx` — `leaving` yerine `asked`; her
  basış kendi kaydını yazar, cevabında yalnız kendisininkini siler.
- Testler: `inTurn.test.js` (yeni), `AllProjectsScreen.test.jsx`, `App.test.jsx`.
- `queen-agent/frontend/dist` yeniden derlenir.

## Testler

**Sıra (`inTurn.test.js`):** bir iş, öncekinin sonucu gelmeden başlamaz, ve her çağıran kendi işinin
sonucunu alır; reddeden de fırlatan da bir iş çağıranına reddini verir, ve sonraki iş yine koşar.

**Ekran (`AllProjectsScreen.test.jsx`):**

- Archive'ın cevabı gelmeden Unarchive'a basılınca proje o anda Projects'te; arşivin cevabı — arşivli
  liste — gelince de Projects'te; Unarchive'ın cevabıyla sunucunun listesi geçer.
- Tersi: Unarchive'ın cevabı gelmeden Archive'a basılınca proje Archived'da kalır, iki cevaptan sonra
  da.
- Unarchive satırı cevabı beklemeden Archived'dan çıkarır; reddedilirse proje Archived'a döner.
- 441'in testleri değişmeden geçer.

**App (`App.test.jsx`) — sunucusu PATCH'lerin cevabını tutan bir sahte sunucuyla:**

- Archive'dan hemen sonra Unarchive: ilk PATCH'in cevabı gelmeden ikinci PATCH gönderilmez; ikincisi
  birincinin listesinden sonra gider; sonunda proje Projects'te, sunucuda arşivsiz, ve App yeniden
  kurulunca — sayfa yenilenince — yine Projects'te.
- Tersi: arşivli bir projede Unarchive'dan hemen sonra Archive: sonunda Archived'da, yenilenince de.
- Bir arşiv beklerken başka bir projenin silinmesi onaylanınca DELETE, arşivin PATCH'i ve listesi
  geldikten sonra gider; silinen proje yeniden çizilmez, arşivlenen Archived'da.

App'in `reloadProjects`'inin sırada olduğunu App testi ayrıca kurmaz — bunun için bir proje kapandıktan
sonra süren bir akış gerekir —; sıranın kendisini `inTurn.test.js`, bağlamayı `useProjects.js`'in tek
satırı tutar.

## Bitti sayılır

- Yukarıdaki testler yeşil, dört suite sırayla yeşil, `dist` yeniden derlenmiş.
- Kullanıcının denemesinde: Archive'dan hemen sonra Archived'da Unarchive'a basılınca proje Projects'te
  kalıyor, ve sayfa yenilenince de orada; tersi sırada da son basılan duruyor.
