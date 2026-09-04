# Madde 3 — Home kalkar, açılış ilk projeye iner · Tasarım Belgesi

**Tarih:** 2026-08-17 · **Branch:** `fix/mira` · **Madde:** [yol haritası Madde 3](../plans/2026-08-15-queenagent-v2-roadmap.md)
**Kaynaklar:** fark 12, 16, 17, 19 · karar 14 · `HANDOFF.md` §2, §6, §7, §8 · bu koşuda alınan karar (aşağıda)
**Bağlayıcı belgeler:** [FOUNDATION.md](../../../queen-agent/FOUNDATION.md) · [CODE-STANDARD.md](../../../queen-agent/CODE-STANDARD.md)

---

## 0 · Bu maddede sorulan soru ve verilen cevap

Yol haritası bu maddeye iki açık soruyla geliyordu: **açılış ekranı** (tasarım ilk projeye iniyor —
fark 12) ve **Home'a dönüş yolu** (kelime markası mı, başka bir şey mi). İkincisi bir boşluktan
doğuyordu: tasarımın gösterdiği tek dönüş yolu "New chat", **karar 15** ile projeye bağlanıyor ve
Madde 6'da kapanıyor — yerine bir şey konmazsa Home'a hiç ulaşılamaz.

Kullanıcıya soruldu. **Karar:**

> Proje seçilmeden sohbet olmasın. Proje varsa her zaman ilk proje seçili gelsin, yoksa Home'a
> düşsün — ve o sayfanın kendisi "projen yok, bir tane oluştur" sayfası olsun.

Bunun sonucu: **Home diye görülecek bir ekran kalmıyor.** `/` bir ekran değil, bir çataldır. Kart
ızgarası proje varken hiç görünmeyeceği için tümüyle gider; "Home'a dönüş yolu" sorusu da kendiliğinden
düşer, çünkü dönülecek bir yer yoktur.

Bu tasarımdan bilinçli bir sapmadır ve tek yerde sapar: `HANDOFF.md` §2 Home'u "Composer + Projects
grid" diye tarif ediyor. Composer'ı zaten **karar 14** kaldırmıştı (tasarım mesajın hangi projeye
düşeceğini hiçbir yerde söylemiyor); geriye kalan ızgarayı da bu karar kaldırıyor. Tasarımın diğer üç
Home değinmesi bu kararla çelişmez, konusuz kalır: §6'nın "Home if none are left" cümlesi artık boş
hâl ekranını gösterir, §8'in "single-column project grid on Home" satırının ızgarası yoktur.

**Konusuz kalan fark maddeleri:** 15 (sayaçların tekil hâli — sayaç kalmıyor), 16 (selamlama
başlığı), 17 (üç öneri hapı), 19 (Home sütununun üst boşluğu 14vh→18vh — sütun kalmıyor). Madde 33'ün
"< 780px'de Home kartları tek sütuna iner" ayağı da düşer. **Fark 12 harfiyen alınır.**

---

## 1 · Ne çalışır

### 1.1 · `/` bir çataldır

Proje listesi geldikten sonra:

| Durum | Ne olur |
|---|---|
| Proje listesi henüz gelmedi | Hiçbir şey çizilmez — karar verilecek veri yok |
| Liste geldi, en az bir proje var | **Listedeki ilk projeye** inilir, adres `/p/<id>` olur |
| Liste geldi, hiç proje yok | "No projects yet" ekranı çizilir |
| Liste gelemedi (hata) | Boş hâl ekranı, ama başlık yerine sunucunun hata cümlesi |

**"İlk proje" = `projects[0]`**, yani `GET /api/projects`'in verdiği sıranın ilki. Sunucu projeleri
eskiden yeniye sıralıyor ve kenar çubuğu da aynı diziyi aynı sırayla çiziyor — dolayısıyla "ilk
proje", kullanıcının gördüğü listenin **en üst satırıdır**. Yeni bir kavram doğmaz.

**Adres `pushState` ile değil `replaceState` ile değişir.** `/` bir yer değil, bir çataldır; geçmişte
durursa geri tuşu kullanıcıyı çatala geri atar ve çatal onu hemen ileri iter — geri tuşu çalışmaz
hâle gelir.

**Yükleniyorken hiçbir şey çizilmemesinin sebebi:** boş liste ile "liste henüz gelmedi" aynı şeye
benziyor. Boş hâl ekranını yükleme sırasında çizmek, projesi olan kullanıcıya her açılışta bir anlık
"No projects yet" göstermek demektir.

**Hata hâlinin ayrı tutulmasının sebebi:** `GET /api/projects` 500 dönerse proje **sayısı bilinmiyor**
demektir, "sıfır" demek değil. Ekran bunu "No projects yet" diye okursa kullanıcıyı projelerini
silinmiş sanmaya iter. Bu yüzden hata varken ekranda sunucunun kendi cümlesi durur ve "New project"
düğmesi çizilmez. *(Repo kuralı: hata mesajında sebep uydurulmaz — sunucunun sözleri olduğu gibi
yazılır.)*

### 1.2 · Boş hâl ekranı

Tasarımın kendi sözleri (`HANDOFF.md` §7 ve prototipin boş hâl dalı):

- Serif **34px** başlık: `No projects yet`
- Altında tek cümle: `Chats live inside a project, and the files they create stay there. Create a project to start.`
- Tek **dolu vurgu** düğmesi: `+ New project`
- Ne composer, ne ızgara, ne illüstrasyon. Ekranın tamamında ortalanmış tek bir blok.

Düğmeye basmak proje kurar (ad sorulmaz, "New project" doğar) ve kurulan projeye iner — zaten
gidilecek başka yer yoktur.

### 1.3 · Kenar çubuğu

Hiç proje yokken "New chat" **gizlenir** (pasifleştirilmez) — `HANDOFF.md` §7'nin kuralı. Kuralın
tamamı ("proje seçili değilken de gizlenir", "Recent chats yalnız proje seçiliyken") **Madde 6'nın**
işidir; bu madde yalnız sıfır-proje ayağını kapatır, çünkü boş hâl ekranı onsuz ölü bir denetim
taşır.

---

## 2 · Ne silinir

### 2.1 · Ön yüz

| Dosya | Ne olur |
|---|---|
| `features/workspace/HomeScreen.jsx` | **Silinir.** Yerine `NoProjectsScreen.jsx` gelir |
| `features/workspace/HomeScreen.test.jsx` | **Silinir.** Yerine `NoProjectsScreen.test.jsx` |
| `features/workspace/ProjectCard.jsx` | **Silinir** — tek kullanıcısı Home ızgarasıydı |
| `features/workspace/ProjectCard.test.jsx` | **Silinir** (varsa) |
| `App.jsx` | `sendFromHome` ve `goHome` gider; `home` görünümünün yerine çatal gelir |
| `useChatLists.js` | `startChatInNewProject` gider |
| `shared/useRoute.js` | `parsePath`'in `home` görünümü kalır (adres hâlâ `/` olabilir); `navigate` ikinci bir `replace` seçeneği alır |
| `workspace.css` | `.home`, `.home__column`, `.home__greeting`, `.home__head`, `.home__section`, `.home__error`, `.home__grid`, `.card*` kuralları gider; yerine boş hâl kuralları gelir |
| `Skeleton.jsx` | `card` çeşidi kullanılmaz hâle gelir → çeşit ve CSS'i gider |

`ProjectDot` **kalır** — kenar çubuğu satırları onu kullanıyor. `Composer` **kalır** — proje ve
sohbet ekranları onu kullanıyor. `ghost` düğme sınıfı **kalır** — proje ekranı kullanıyor.

### 2.2 · Arka uç

| Dosya | Ne olur |
|---|---|
| `presentation/routes.py` | `POST /api/chats` uç noktası gider |
| `domain/usecases/start_chat_in_new_project.py` | **Silinir** |

`GET /api/chats` (Recent chats) **kalır** — onun kaderi Madde 6'nın konusu.

`start_chat_in_new_project` dört test dosyasında **kurulum kolaylığı** olarak kullanılıyor
(`test_append_message`, `test_delete`, `test_rename`, `test_stream_answer`). Silindiğinde bu dosyalar
aynı işi `create_project` + `start_chat` ile kurar — kullanıcının göreceği hiçbir davranış değişmez,
yalnız testlerin iskelesi değişir.

---

## 3 · Katman denetimi

Yeni dosya: `frontend/src/features/workspace/NoProjectsScreen.jsx` — ön yüzde `features/workspace/`,
doğru yer (ekran bileşeni, projeye ait bir yetenek).

Silinenlerin hepsi kendi katmanında: `domain/usecases/` bir use case kaybeder, `presentation/` bir uç
nokta kaybeder. **Bağımlılık yönü değişmez:** `presentation → domain ← data → services` aynen durur;
`start_chat_in_new_project`'in `create_project`, `edit_project` ve `start_chat`'i çağırması use
case→use case bir bağdı, o da onunla gider. Yeni bağ doğmaz. `feature ↛ feature`, `service ↛ feature`,
`service ↛ service` yasakları bu maddede hiç zorlanmıyor — tek özellik `workspace` ve hiçbir servis
dokunulmuyor.

Çatal mantığı `App.jsx`'te durur: hangi ekranın çizileceği bileşim kökünün sorusudur, bir ekranın
kendi sorusu değil.

---

## 4 · Kabul ölçütü

1. Sıfır projeyle açılışta "No projects yet", tek cümle ve "+ New project" görünür; yazı kutusu,
   kart ızgarası, selamlama yoktur.
2. En az bir projeyle açılışta ekranda **ilk projenin** ekranı vardır ve adres `/p/<ilk>`'tir.
3. `/` geçmişe yazılmaz: çataldan geçtikten sonra geri tuşu kullanıcıyı çatala geri atmaz.
4. Liste yüklenirken ne boş hâl ekranı ne ızgara çizilir.
5. `GET /api/projects` hata verirse ekranda sunucunun cümlesi durur, "No projects yet" durmaz.
6. `POST /api/chats` artık **405** döner — 404 değil: `GET /api/chats` (Recent chats) aynı adreste
   duruyor, dolayısıyla adres tanınır ama yöntem tanınmaz.
7. Boş hâl ekranındayken kenar çubuğunda "New chat" yoktur.

## 5 · Risk

**En büyük risk kart ızgarasının geri dönüşünün pahalı olması.** Kart bileşeni, sayaçları ve ızgara
CSS'i bu maddede siliniyor; geri istenirse yeniden yazılır. Karar kullanıcıya bu cümleyle sorulmuş ve
bilerek verilmiştir.

**İkinci risk açılış çatalının döngüye girmesi:** çatal yalnız `route.view === "home"` iken ve liste
gelmişken çalışır, `replaceState` ile bir kez adres değiştirir. Proje silme sonrası `/`'a dönüş
Madde 18'in konusudur; bu maddede o yol hiç kurulmuyor.
