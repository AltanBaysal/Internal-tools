# Madde 480 · Değiştiren araçlar için izin kapısı — tasarım

**Tarih:** 20 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-20-queen-editor-v10-roadmap.md),
480 · v10-7b · **Dal:** `feat/queen-editor-v10` · **Kurallar:** queen-editor
[FOUNDATION](../../../queen-editor/FOUNDATION.md) · [CODE-STANDARD](../../../queen-editor/CODE-STANDARD.md)

## Kullanıcıdan gereken

Hiçbir şey. Madde 20 Ekim'de hizalandı. Tasarımın üç açık sorusu ana ajana soruldu, ana ajan 20 Ekim'de
üçünde de önerileni seçti (aşağıda, "Bu maddenin kararları").

## Ne, neden

Kullanıcının sözü: *"izni bu arada agetnın insiyatifine bırakmicaz her seferinde ui bunu yapmak
istiyorum evetr hayır şeklinde çıkıcak maneıl ben butona basıcam"*; *"ajan izin oalyını bilem zorunda
değil ajan değiştirmey çalışınca aekran izin çıksın ben kabul edeyim veya reddeyim"*; *"claudde var
böyle bir şey auto da gerkemyiro ama maneul mode gibi üşün"*.

- **İzin uygulamanın.** Ajan izin diye bir şeyin olduğunu bilmez: hiçbir aracın açıklaması, talimatın
  hiçbir cümlesi izinden söz etmez. Bir aracın değiştiren mi okuyan mı olduğunu aracın kendi kodu
  söyler.
- **Okuyan araçlar izinsiz çalışır.** Bugünkü üçü (`read_frame`, `look_at_frame`, `check_frame`)
  okur; hiçbiri izin sormaz.
- **Değiştiren her çağrı** ekranda bir kart açar: ne değişeceği yazılı, altında **İzin ver** ve
  **Reddet**. İzin ver'de araç çalışır. Reddet'te hiçbir şey değişmez, ve ajana kullanıcının
  reddettiği söylenir.
- **Otomatik izin modu yok.** Her değişiklik kendi kartıyla sorulur; bir cevap bir sonrakinin yerine
  geçmez.
- **Bu madde yalnız kapıyı kurar.** Kapıdan geçen ilk araç 481'in düzeltmesi. 480'de üretimde
  değiştiren bir araç yok; kapı testlerde sahte bir araçla, `fix_frame`, kanıtlanır.

## Bugün — koddan okunanlar

- **Döngü** (`domain/usecases/answer_question.py`): her araç çağrısından önce durdurmaya bakar,
  `run_tool(...)`'dan `(adım, iş)` alır, adım varsa öncekini bitirip yenisini yazar, sonra işi
  çalıştırır.
- **Koşucu** (`runner.py`): çalışan ajanlar süreçte, bellekte durur; diske yazılmaz. Yeniden başlama
  her koşuyu bitirir, soru sonuçsuz kalır. Durdurma kilit altında koşuyu bitmiş işaretler ve
  "stopped" yazar; koşunun bundan sonra yazdığı hiçbir yere düşmez.
- **Kayıt** (`chats.jsonl`): soru, adım, adımın bitişi, cevap, hata, durdurma — eklenerek yazılır.
- **Ekran** (`useAgentChat.js`): bir ajan çalışırken saniyede bir `GET /chats/working`'e, açık sohbet
  çalışıyorsa sohbetin kendisine bakar. Yeniden yüklemede önce `/working`, sonra sohbet okunur.

## Ne değişir

### 1. Kapı aracın özelliği (`domain/tools.py`)

`run_tool(ask, frames, picture, project, call)` artık `(adım, iş, değişiklik)` döner. **Değişiklik**,
çağrının neyi değiştireceğinin ekrana giden Türkçe tarifidir, ve yalnız işi bir şey yazan çağrıda
vardır. Okuyan çağrı ve ıska (bilinmeyen araç, olmayan kare) `None` döner: değişecek bir şey yoksa
sorulacak bir şey de yoksa. Bugünkü üç araç `None` döner.

Ayrı bir "değiştiren araçlar" listesi yok: işaret, aracın kendi döndürdüğü değişikliktir. İki ayrı
kaynak (bir ad listesi ve bir tarif) birbirini tutmayabilirdi.

### 2. Değişikliğin biçimi — 481 doldurur

```json
{"title": "3 numaralı kare düzeltilecek",
 "details": [
   {"label": "Prompt", "before": "<eski prompt>", "after": "<yeni prompt>"},
   {"label": "Negatif prompt", "before": "<eski>", "after": "<yeni>"},
   {"label": "Fotoğraf", "text": "Eski fotoğraf silinecek; yenisi aynı yerde üretilecek."}
 ]}
```

- `title`: ne değişeceği, kare numarasıyla — 481 numarayı başlığa yazar.
- `details`: sırayla; her biri ya `{label, before, after}` — bir alan neydi, ne olacak —, ya
  `{label, text}` — bir cümle, ör. eski fotoğrafın silineceği.

Ekran yalnız bunu çizer, içini yorumlamaz; kural backend'de kalır (FOUNDATION, karar 4).

**481 için not — değiştiren bir işin sözleşmesi** *(reviewer, 20 Ekim; `run_tool`'un docstring'inde
de yazılı)*: değiştiren bir çağrının işi, kullanıcı cevap verince çalışır — belki dakikalar sonra,
galeri o arada değişmişken. Bu yüzden iş, tarif yazıldığı andaki hâle güvenmez:

- kareyi diskte onu adlandıran şeyle — kimliğiyle (`P1_0` gibi) — bulur, galerideki numarasıyla asla;
- kare artık `change`'in `before`'larının tarif ettiği gibi değilse hiçbir şeyi değiştirmez ve modele
  bunu söyler.

### 3. Döngü (`answer_question.py`)

Her araç çağrısında sırayla:

1. `run.stopped()` — bugünkü gibi.
2. `run_tool` → `(adım, iş, değişiklik)`.
3. Adım ya da değişiklik varsa önceki adım bitirilir. Değişiklik için bitirmek doğrudur: model bu
   çağrıyı, önceki adımın getirdiğini okuyarak yaptı. Böylece kullanıcı karar verirken ekranda sürüp
   giden tek şey karttır.
4. Değişiklik varsa `run.permit(değişiklik)` — kullanıcının cevabını bekler.
   - **İzin ver** (`True`): devam.
   - **Reddet** (`False`): modele araç cevabı olarak *"The user rejected this change, so nothing was
     changed."* döner; adım yazılmaz, iş çalışmaz, sıradaki çağrıya geçilir.
   - **Durdurma** (`False` ve `run.stopped()`): soru biter; ne iş çalışır ne yeni tur gider.
5. Adım varsa yazılır. Sonra `run.stopped()` bir kez daha sorulur: İzin ver'den sonra, iş başlamadan
   gelen bir durdurma değişikliği yapılmamış bırakır *(reviewer, 20 Ekim)*. Durdurulmamışsa iş
   çalışır — bugünkü gibi.

Reddedilen bir çağrıdan sonra sıradaki çağrı önceki adımı yeniden bitirir: kayda bir `stepDone`
satırı fazladan düşer, katlama onu değiştirmez (zaten bitmiş adım bitmiş kalır). Bunu önlemek döngüde
ayrı bir durum değişkeni isterdi; bedeli ret başına bir ekleme.

### 4. Bekleme (`runner.py`)

- `_Run.permit(değişiklik)` koşucunun `_permit`'ine gider. Kilit altında: koşu bitmişse hemen `False`
  (durdurulmuş bir koşu bir şey sormaz). Değilse değişiklik koşuya konur,
  `asking = {"id": <sayı>, "change": <değişiklik>}`, ve koşucunun kilidi üstündeki bir
  `threading.Condition`'da beklenir: `while run.asking is not None and not run.over: wait()`. Bekleme
  uyurken kilidi bırakır.
- `reply(project, chat_id, id, allow)` kilit altında: sohbetin koşusu **tam bu sayıdaki**
  değişikliği bekliyorsa cevabı koyar, `asking`'i boşaltır, `notify_all()` ile uyandırır ve `True`
  döner; değilse hiçbir şeye dokunmadan `False`.
- `stop` bugünkü işine ek olarak `asking`'i boşaltır ve `notify_all()` çağırır: uyanan koşu bittiğini
  görür, ve bu bir rettir.
- `_permit` uyanınca `allowed and not over` döner: İzin ver'den hemen sonra, koşu kilidi geri almadan
  gelen bir durdurma kazanır.
- `now(project)`: `{"working", "asking"}` tek bir kilit tutuşunda — iki liste hiçbir an birbirini
  tutmamazlık etmez. `asking`'in her öğesi `{"chat", "id", "change"}`, sohbete göre.
- **Sayılar saatten başlar** *(reviewer, 20 Ekim)*: sayaç `time.time_ns() // 1000`'den, yani
  mikrosaniyeden başlar; yeniden başlamadan önce açık kalmış bir sayfa yeni bir değişikliği eski bir
  sayıyla adlandıramaz. Nanosaniye değil, çünkü sayfa sayıyı bir JavaScript sayısı olarak okur, ve o
  ancak 2⁵³'e (≈ 9,0 × 10¹⁵) kadar tam; nanosaniye bugün ≈ 1,8 × 10¹⁸, yuvarlanıp geri gelir ve hiçbir
  cevap tutmazdı. Mikrosaniye ≈ 1,8 × 10¹⁵. Bir test sayıyı bu sınıra bağlar.
- **Zaman aşımı yok.** Cevaplanmamış bir kart cevaplanana ya da Durdur'a basılana kadar bekler; panel
  kapanabilir, sayfa yeniden yüklenebilir.

**Neden sayı:** 481'de bir tur birden çok kare için düzeltme çağrısı taşıyabilir. Bir kare izin
alınca işi çalışır ve bir sonraki kare birkaç saniye içinde sorulur. Sayı olmasaydı, ikinci bir
tıklama ya da sunucunun gerisinde kalmış bir sayfa (ikinci sekme) bir sonraki, kimsenin görmediği
değişikliğe izin verebilirdi — FOUNDATION'ın 1. ilkesine aykırı. Sayı uymazsa cevap reddedilir.

### 5. Kapılar (`presentation/routes.py`, `usecases/chats.py`)

- **`GET /api/projects/<p>/chats/working`** artık `{"working": [1, 2], "asking": [{"chat": 1, "id": 7,
  "change": {...}}]}` döner. Ekran ona zaten saniyede bir bakıyor; kart ek bir istek olmadan gelir.
- **`POST /api/projects/<p>/chats/<id>/permission`**, gövde `{"id": 7, "allow": true}`:
  - proje yoksa `404 {"error": "Proje yok: <p>"}`, klasör açılmaz;
  - `id` tam sayı değilse (`true` dahil) ya da `allow` `true`/`false` değilse
    `400 {"error": "İzin cevabı geçersiz."}`;
  - sohbetin ajanı bu değişikliği beklemiyorsa — cevaplanmış, durdurulmuş, hiç sorulmamış, başka bir
    sayı, olmayan bir sohbet — `409 {"error": "Bu değişiklik artık izin beklemiyor."}`, hiçbir şey
    çalışmaz;
  - yoksa `200` ve `/working`'in cevabı, cevaptan sonraki hâliyle: ekran kartı hemen kaldırır.
- Kapı sohbet kaydını okumaz: neyin beklendiğini yalnız koşu bilir, olmayan bir sohbet "bekleyen bir
  şey yok" demektir.

### 6. Ekran (`useAgentChat.js`, `AgentPanel.jsx`, `api.js`, `app.css`)

- `workingChats` `/working`'in bütün gövdesini döner; kanca `working` ile birlikte `asking`'i tutar.
  `workingChats`'in iki çağıranı (açılış ve yoklama) ikisini birden alır.
- Açık sohbetin ajanı çalışıyor ve bir değişiklik bekliyorsa canlı sorunun adımlarının altında, "Çalışıyor…"
  satırının yerinde kart: başlık, her detay — etiket, altında **Eski** soluk ve **Yeni**, ya da cümle —,
  sağda **Reddet** ve **İzin ver**.
- Basınca `answerPermission(project, chat, id, allow)`; cevap yoldayken iki düğme de kapalı, yani bir
  basış bir cevap. Cevap gelince kart kalkar ve satır "Çalışıyor…"ya döner; izin verildiyse ajanın
  yazdığı adım bir sonraki bakışta gelir.
- Cevap ulaşmazsa ya da `409` dönerse kart kalır, düğmeler yeniden açılır ve sunucunun (ya da ağın)
  cümlesi bir hata kartında görünür. Bir sonraki iyi bakış bu cümleyi geri alır — başarısız bir
  bakışınki gibi (`lookClears`) —, ve artık beklemeyen bir kartı da kaldırır.
- Kart yalnız canlı, son soruya verilir.
- **■ (Durdur)** kartın yanında kalır: basınca değişiklik reddedilir, soru durur, kart kalkar,
  "Durduruldu" yazar.
- Kart yalnız kendi sohbetinin altında çizilir.
- Yerini şimdilik Claude koydu; tasarımcının tasarımı gelince düzeltilir. `dist` yeniden kuruldu.

## Yeniden yükleme ve yeniden başlama

- **Sayfa yeniden yüklenir ya da panel kapanıp açılırsa:** koşu sunucuda sürüyor ve kart koşunun
  üstünde. Açılış önce `/working`'i okur, kart ondan gelir — aynı sayıyla, aynı cevaplanabilir hâlde.
- **Sunucu yeniden başlarsa:** bekleyen koşu, kartıyla birlikte biter. İş hiç çalışmadı, yani hiçbir şey
  değişmedi. Soru bugünkü gibi sonuçsuz kalır; kayıtta karttan bir iz yok, çünkü kart hiç diske
  yazılmadı.

**Neden yalnız bellekte** *(ana ajan, 20 Ekim)*: kart, çalışan bir koşunun durumudur, ve koşucu
çalışan her şeyi bellekte tutar — yeniden başlamadan sonra cevaplanabilecek bir koşu yok. Diske
yazılsaydı kayıt yeni bir satır türü, katlamaya yeni bir öğe ve yeniden başlamadan sonra düğmesiz,
ölü bir kart çizimi isterdi. Bedeli: sohbette "İzin verildi" / "Reddedildi" diye bir satır kalmaz. Ne
olduğunu ajanın cevabı söyler, izin verilen değişikliği de 481'in adımı ("… düzeltti").

## Maliyet

Koddan sayıldı, ölçülmedi.

| İşlem | Disk (Drive) | Ağ |
|---|---|---|
| `GET /working` (saniyede bir, ajan çalışırken) | bugünkü gibi 1 stat (proje var mı); `asking` bellekten | yok |
| `POST /permission` | 1 stat (proje var mı); kayıt okunmaz | yok |
| Kapı (soruluş) | önceki adımın bitişi — adım başlarken zaten yazılacaktı | yok |
| Ret | modele bir araç cevabı; sıradaki çağrıda fazladan bir `stepDone` eklemesi (ret başına 1) | yok |
| Bekleme | yok: bir `Condition`'da uyuyan bir iş parçacığı | yok |

Hepsi O(1); proje, sohbet ya da kare sayısıyla büyümez. `now(project)` bellekteki koşuları gezer,
O(çalışan koşu).

## Ne kaybolabilir, ne bozulabilir

- **İzinden önce hiçbir şey yazılmaz.** Değiştiren iş yalnız İzin ver'den sonra çalışır; Reddet'te,
  durdurmada, yeniden başlamada hiç çalışmaz.
- **İki basış, iki sekme:** cevap değişikliğin sayısını taşır; sayı uymazsa `409` ve hiçbir şey
  çalışmaz. Ekranda cevap yoldayken düğmeler kapalı.
- **İzin ver'den sonra gelen durdurma:** iş başlamadan geldiyse — `_permit` uyanmadan ya da adım
  yazılırken — iş çalışmaz. İş başladıktan sonra geldiyse iş bitirilir — kullanıcı izin vermişti, ve
  havadaki bir iş bugün de kesilmez; yazdıkları sohbete düşmez.
- **Bekleyen bir koşu** sohbetini meşgul tutar: o sohbete yeni soru sorulamaz, cevaplanana ya da
  durdurulana kadar. Öteki sohbetler etkilenmez.
- **URL'den gelen değerler:** sohbet numarası Flask'ın `int` çeviricisinden, gövdedeki `id` tam sayı
  denetiminden geçer; hiçbiri yola ya da dosya adına girmez. Gizli bir değer yok.

## Bu maddenin kararları

1. **`run_tool` `(adım, iş, değişiklik)` döner;** işaret aracın kendi değişikliği, ayrı bir liste
   yok *(ana ajan, 20 Ekim)*.
2. **Bekleme koşucuda, bir sayıyla;** sayı uymayan cevap `409` *(ana ajan, 20 Ekim)*. Bekleme
   koşucunun kilidi üstünde bir `Condition`, sayılar saatten, mikrosaniyede; `{working, asking}` tek
   tutuşta `now()` *(reviewer, 20 Ekim)*.
3. **Durdurma bir ret;** zaman aşımı yok *(ana ajan, 20 Ekim)*.
4. **Kart yalnız bellekte**, diske yazılmaz *(ana ajan, 20 Ekim — seçenek a)*.
5. **Ekran kartı `/working`'den alır,** `{"working", "asking"}` *(ana ajan, 20 Ekim — seçenek a)*.
6. **Reddet'te modele İngilizce:** *"The user rejected this change, so nothing was changed."* —
   kullanıcının "kullanıcı reddetti"sinin anlamı, her araç cevabının dilinde *(ana ajan, 20 Ekim —
   seçenek a)*.
7. **Sahte değiştiren araç yalnız testlerde,** pytest'in `monkeypatch`'iyle döngünün `run_tool`'unun
   önüne konur; `TOOLS`'a girmez.

## Sınırlar

- Üretimde değiştiren bir araç yok; kart bugün gerçek ekranda görünmez. Ekrandaki kontrol 481'in
  QA'sında yapılır; bu maddede vitest kartı sahte bir sunucuyla dener.
- **Sahipsiz bekleme** *(reviewer, 20 Ekim)*: bir koşu beklerken projesi yeniden adlandırılır ya da
  silinirse koşu beklemeye devam eder. Koşu eski adla tutulur: yeni adın ekranı kartı görmez, ve eski
  adın kapıları — `/permission` da `/stop` da — proje artık olmadığı için `404` döner, yani ne
  cevaplanabilir ne durdurulabilir. İş parçacığı süreç bitene kadar uyur; bir yeniden başlama onu,
  hiçbir şeyi değiştirmeden bitirir. Hiçbir şey yazılmaz, eski klasör geri gelmez. Yeni addaki sohbet
  meşgul görünmez, ona yeni soru sorulabilir.
- Talimat (`prompt.py`) değişmez: ajan izni bilmez.
- Kayıt (`chats.jsonl`) ve şeması değişmez.
- Notebook değişmez.

## Bitti sayılır

1. Testler gösteriyor ki:
   - `test_agent_answer.py`: değişiklik adımdan önce soruluyor, önceki adım bitmiş; İzin ver'de adım
     yazılıyor ve iş çalışıyor; Reddet'te iş çalışmıyor, adım yazılmıyor, modele ret cümlesi dönüyor
     ve turun sıradaki çağrısı çalışıyor; soru sırasında durdurma hiçbir şeyi çalıştırmıyor ve yeni
     tur göndermiyor; İzin ver'den sonra, iş başlamadan gelen durdurma işi çalıştırmıyor; bir turun
     iki değişikliği ayrı ayrı soruluyor; okuyan üç araç izin sormuyor.
   - `test_agent_runner.py`: koşu cevabı bekliyor ve alıyor (izin, ret); başka bir sayıya, başka bir
     sohbete ya da projeye verilen cevap hiçbir şeyi uyandırmıyor; ikinci cevap reddediliyor;
     soru yokken cevap reddediliyor; bekleyişte durdurma bir ret ve "stopped" yazılıyor; durdurulmuş
     koşu sormuyor; her değişikliğin kendi sayısı var ve `now` yalnız projenin sohbetlerini veriyor;
     sayı JavaScript'in tam okuduğu sınırın altında; her bekleyen iş parçacığı test bitmeden bitiyor.
   - `test_agent_routes.py`: gerçek kayıt, koşucu ve döngüyle kart `/working`'de; yeniden yüklemede
     orada; İzin ver'de iş çalışıyor ve adım kayıtta; Reddet'te çalışmıyor; durdurma hiçbir şeyi
     çalıştırmıyor; eski sayıya ve ikinci cevaba `409`; bozuk gövdeye `400`; olmayan projeye `404` ve
     klasör açılmıyor; disk hatası sistemin cümlesiyle `503`.
   - `test_composition_root.py`: `main.py` yeni kapıyı asıyor.
   - `AgentPanel.test.jsx`: yeniden yüklemede kart, başlık ve detaylarla, "Çalışıyor…"nun yerinde;
     bir bakışta beliriyor; İzin ver ve Reddet sayıyla gidiyor ve kart hemen kalkıyor; izin sonrası
     adım geliyor; cevap yoldayken düğmeler kapalı; `409`'da sunucunun cümlesi, ve bir sonraki bakış
     kartı da cümleyi de kaldırıyor; ağ yokken kart kalıyor, düğmeler açılıyor, cümle görünüyor ve ağ
     dönünce aynı değişiklik cevaplanabiliyor; ■ kartı kaldırıyor; kart yalnız kendi sohbetinde.
2. İki satır yeşil: `python -m pytest queen-editor -q` ve `npm test --prefix queen-editor/frontend`.
3. `npm run build --prefix queen-editor/frontend` ile `dist` yeniden kurulmuş.
4. Ekranda gerçek bir değiştiren araçla kart: 481'in QA'sında.
