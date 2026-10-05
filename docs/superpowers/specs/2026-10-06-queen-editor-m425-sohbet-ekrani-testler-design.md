# Madde 425 — Agent'ın sohbeti ekranda, test turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 425 · v9-4d · **Tur:** 1/2 — yalnız testler.
**Üstüne kurulduğu:** [m417 test turu](2026-10-06-queen-editor-m417-sohbet-kaydi-testler-design.md)
(sohbetlerin kaydı ve kapıları), [m420 test turu](2026-10-06-queen-editor-m420-agent-testler-design.md)
(agent, soru · durdur · çalışanlar kapıları).

**Kullanıcıdan gereken — yok.** Madde hizalı; kararları yol haritasının *Maddelerin kararları → v9-4*
bölümünde. Görünüş ve sözler tasarımcının 207, 208, 210, 211 ve 212'sinden
*(queen-design `queen-editor-v2`; ana klasörün `tmp/queen-design-queen-editor-v2/`'sinde
`projects/queen-editor/sohbet.js`, `kit.css`, `proje-ekrani-tam/`, ve `docs/superpowers/specs/`'teki
`2026-10-05-queen-editor-{sohbet,sohbet-listesi,gonder-durdur,adimlar}-design.md`)*, davranışlar
`BEHAVIOUR.md`'nin *Agent panel* bölümünden. Sunucunun kapıları 417 ve 420'de kuruldu; bu parça onlara
dokunmaz. Ekranın sunucuyu ne sıklıkla okuduğu ve neyi tarayıcıda tuttuğu teknik kararlar, Claude'un.

## Kullanıcının sözü

*"Queen Editore basic agent ekle en basic haliyle"* *(5 Ekim)*. Tasarım turunda: *"Yalnız yenileyince;
projeye özel"*, *"abi projeler arasında kalıcıysak yenileyince de gitmesin, sıfırlamanın yolu yeni
sohbet açmak olur, sohbet sıfırlanmaz"*, *"Evet, yenileyince de kalsın"*, *"Listede kalır, geri
açılır"*, *"1, çalışmaya devam eder"*, *"O an ne yaptığı, tek satır"*, *"Yazılır ama gitmez;
durdurulur"*, *"chat akışı da öyle olsun, yapılan şeyler yok olmak yerine claude code gibi alt alta
sıralanabilir"*, *"Cevabın üstünde açık kalır"*, *"dur dur ve gönder claude code gibi olsun lütfen"*,
*"İki yandan 10px"*.

## Bugün ne oluyor

*"AI agent"* paneli yalnız *"Agent buradan çalışacak."* diyor
*(`frontend/src/features/photo_generation/AgentPanel.jsx`)*. Sunucuda sohbetlerin kaydı (417) ve agent
(420) var: yeni sohbet, liste, sohbeti açmak, soru sormak, durdurmak ve çalışanları söyleyen altı kapı.
Ekran hiçbirini çağırmıyor; `shared/api.js`'te onlara giden bir fonksiyon yok.

## Kurallar

### Panel

1. **Başlık satırı.** Panelin başlığı *"AI agent"* solda; sağ uca dayalı iki küçük düğme: *"Yeni
   sohbet"* ve *"Sohbetler"* — üçü aynı satırda *(208)*. Öteki panellerin başlığı bugünkü gibi.
2. **Altında ya açık sohbet** — konuşma ve kutu — **ya da sohbetler listesi**, konuşmanın yerinde
   *(208)*.

### Açılış

3. **Panel ilk kez açılınca en yeni sohbet açılır** — listenin ilk satırı, yani son sorusu en yeni
   olan *(417'nin listesi)*. Sorulu sohbet yoksa bekleyen boş sohbet açılır: sunucudan istenir
   *(`POST …/chats` — bekleyeni ya da yenisini verir)*.
4. **Panel kapanıp açılınca, kare sayfasına girip dönünce, başka projeye gidip gelince** son açık olan
   sohbet açılır, sunucudan yeniden okunarak: agent o arada çalıştıysa adımları, cevabı ya da hâlâ
   çalıştığı yerde. Liste açıkken kapanan panel listeyle açılır *(208)*. Her projenin açık sohbeti
   kendinin.
5. **Sayfa yenilenince kural 3:** en yeni sohbet açılır — az önce soru sorulan sohbet odur, ve agent'ı
   çalışıyorsa çalışırken görünür.
6. **Okunamayan sohbet** — sunucuya ulaşılamadı, ya da sunucu reddetti — hata kartıyla, isteğin kendi
   sözleriyle *(aşağıda kural 19)*.

### Konuşma

7. **Boş sohbet:** ortada *"Projeyle ilgili bir şey sor."*; kutuda yer tutucu *"Sorunu yaz…"*.
8. **Soru** sağda balon *(`qe-chat-q`)*. **Adımlar** sorunun altında, alt alta, her biri bir satır:
   bitmiş adım durağan noktayla ve sunucunun verdiği *bitti* cümlesiyle (*"2 numaralı kareyi okudu"*),
   süren adım en altta, canlı noktayla (`qe-dot--alive`, `is-live`) ve *sürüyor* cümlesiyle
   (*"2 numaralı kareyi okuyor…"*) *(211)*. Cümleler sunucunun; ekran yazmaz.
9. **"Çalışıyor…"** — sorunun yolda olduğu bekleme, ve agent çalışırken sunucu henüz bir adım
   yazmamışsa: canlı tek satır. Ulaşılamayınca gider *(211)*.
10. **Cevap** solda düz yazı, tek seferde, adımlarının altında *(`qe-chat-a`)*. **Hata** cevabın
    yerinde kart *(`qe-chat-err`)*, metni sunucunun — retse *"Model hata döndü, farklı şekilde
    dene."*, teknik hatada hatanın kendi metni; yeniden dene düğmesi yok. **Durdurulan soru**: bitmiş
    adımlar, sonra *"Durduruldu"* *(`qe-chat-stopped`)*; yarım cevap yok.
11. **Yeniden başlamada yarıda kalan soru** — sonucu yok ve sohbeti çalışanlarda değil: cevapsız
    çizilir; bitmemiş adımı *sürüyor* cümlesiyle ama durağan noktayla, çünkü sürmüyor. Uydurulmuş bir
    mesaj yok *(420'nin 19. kuralı)*.

### Kutu ve düğme

12. **Tek düğme, kutunun içinde sağ altta** *(210, 212)*. Boştayken ↑, erişilebilir adı *"Gönder"*:
    kutu boşsa ya da yalnız boşluksa kapalı. Agent çalışırken ■, adı *"Durdur"*: kutu boş da olsa
    basılır.
13. **Enter gönderir, Shift+Enter göndermez** (satırı tarayıcı kırar). Gönderilen, kutunun yazısı
    baştaki ve sondaki boşluklarıyla kırpılmış hâli *(tasarımın `draft.trim()`'i)*. Kutu boşalır, ve
    düğmeye basınca odak kutuya döner.
14. **Çalışırken yazılır ama gönderilmez:** Enter göndermez, yazı kutuda kalır. **Durdurunca** yazı
    kalır ve ↑ açılır.
15. **Soru yoldayken** soru balon olarak ve altında *"Çalışıyor…"* görünür, düğme ■; o sırada ■'ya
    basmak bir şey yapmaz — durdurulacak agent henüz başlamadı.
16. **Taslak sohbetiyle kalır:** sohbet değişince, liste açılınca, panel kapanınca ve kare sayfasına
    gidip gelince her sohbetin kutusu kendi yazısıyla.

### Durdurmak

17. ■ → `POST …/stop`; dönen sohbet çizilir: bitmiş adımlar ve *"Durduruldu"*, süren adım düşmüş;
    düğme ↑, odak kutuda.

### Hatalar

18. **Sunucunun sözleri kartta.** Hata kartının metni ya agent'ın sonucunun metni (kural 10), ya da
    ekranın isteğinin hatası: istek sunucuya ulaşmadıysa *"Sunucuya ulaşılamadı — bağlantıyı kontrol
    et."*, sunucu reddettiyse onun cümlesi (ör. 409 *"Bu sohbette agent hâlâ çalışıyor."*) —
    `shared/api.js`'in verdiği cümle, kanıtı olmadan.
19. **Ulaşmayan ya da reddedilen soru** balon olarak kalır, altında kart; adım yok. Sunucuda yok,
    çünkü sunucu almadı: ekranda, sohbet bir sonraki basışta yeniden okunana kadar durur.
20. **Okuma hatası** — sohbetin ya da listenin okunamaması, durdurmanın ulaşmaması — aynı kart,
    balonsuz. **Çalışırken yapılan yoklama** ulaşamazsa kart çıkar, ve yoklama sürer; sunucu dönünce
    kart gider ve adımlar kaldığı yerden gelir.

### Liste

21. *"Sohbetler"* listeyi konuşmanın ve kutunun yerine açar, basılı görünür (`is-on`,
    `aria-pressed`); yeniden basılınca kapanır ve açık sohbet geri gelir — sunucudan yeniden okunarak.
22. **Satırlar sunucunun sırasıyla** — son sorusu en yeni olan üstte; boş sohbet listede yok. Her
    satırda ilk soru (tek satıra kesmek CSS'in: `nowrap`, `…`) ve son sorunun tarihi, projeler
    ekranının kartıyla aynı biçimde (`shared/date.js` — *"5 Eki 2026 · 15:48"*). Açık sohbetin satırı
    işaretli (`is-on`). Agent'ı çalışan sohbetin satırında canlı nokta, adı *"Agent çalışıyor"*;
    agent bitince, liste açıkken de, nokta gider.
23. **Boş liste:** *"Henüz sohbet yok."*
24. **Satıra basmak** o sohbeti açar, listeyi kapatır; sohbet kaldığı yerden sürer.
25. **"Yeni sohbet"** bekleyen boş sohbeti ya da yenisini açar *(sunucunun kuralı)*, liste açıksa
    kapatır, imleç kutuda. Arkada çalışan sohbet çalışmaya devam eder; yeni sohbet soru gönderebilir
    — iki sohbet aynı anda çalışır.

### Sunucuyu yoklamak

26. **Yalnız panel açıkken ve bu projede bir agent çalışırken**, saniyede bir (`POLL_MS = 1000`):
    önce `GET …/chats/working`; sonra, konuşma görünüyorsa ve açık sohbet ya bir önceki yoklamada ya
    da şimdi çalışıyorsa, `GET …/chats/<id>`. Çalışanlar boşalınca yoklama durur; panel kapanınca
    durur. Açık sohbet boştayken başka bir sohbet çalışıyorsa açık sohbet yeniden okunmaz.
27. **Önce çalışanlar, sonra sohbet.** Sunucu cevabı yazıp agent'ı çalışanlardan aynı kilit içinde
    çıkarıyor *(420'nin `runner.py`'si)*; bu sırayla okununca *"çalışmıyor"* diyen yoklamanın ardından
    okunan sohbet sonucunu taşır — bitmiş bir soru yarıda kalmış gibi okunmaz. Sohbet açılırken de
    aynı sıra.

### Kaydırma

28. Konuşma en altta biter. Okuyan kullanıcı yukarı kaydırdıysa yeni adım onu aşağı çekmez; en
    alttaysa yeni satırla birlikte iner *(211)*. Gelen cevap konuşmadan uzunsa konuşma o cevabın
    adımlarının başına kayar *(211, 207)*. Soru gönderilince ve bir sohbet açılınca en alta iner.

## İki türlü okunabilen yerler — seçilenler

- **Hangi sohbetin açık olduğu ve taslak nerede tutulur?** Tarayıcının belleğinde, proje başına
  (modülde bir `Map`) — uygulamanın öteki ekran hafızaları gibi *(açık panel, galeri, fotoğraf
  panelinin taslağı; uygulamada `sessionStorage` hiç yok)*. Tasarım ikisini `sessionStorage`'da
  tutuyor; sayfa yenilenince açık sohbet yerine **en yeni sohbet** açılır, ve taslak gider. Seçilen,
  çünkü yeni bir saklama yolu açmıyor, ve sohbetin kendisi sunucuda zaten kalıcı. Tasarımdan farkı:
  yenilemeden önce eski bir sohbet açıksa yenileyince en yenisi açılır; yazılıp gönderilmemiş yazı
  yenilemede kaybolur.
- **Ne sıklıkla yoklanır?** Saniyede bir, yalnız bir agent çalışırken. Tasarımın adımları 1,4 sn'de
  bir; modelin bir turu birkaç saniye. Boştayken hiç yoklanmaz.
- **Soru yoldayken ■?** Görünür ama bir şey yapmaz (kural 15). Durdurma isteği sorudan önce varırsa
  durduracak bir şey bulmaz ve soru yine başlardı.
- **Soru dışındaki isteklerin hatası?** Tasarım yalnız sorunun ulaşmamasını çiziyor; öteki istekler
  aynı kartla, kendi sözleriyle (kural 20). Bir yoklamanın kartı ilk iyi yoklamayla gider.
- **Yarıda kalmış sorunun açık adımı?** *Sürüyor* cümlesi, durağan nokta (kural 11): *bitti* cümlesi
  yalan olurdu, ve adımı düşürmek o sırada ne yaptığını saklardı.
- **Uzun ilk soru listede nasıl kesilir?** CSS'le (tasarımın sınıfları); metin bütün gelir.

## Arayüz — uygulama turunun vereceği

- **`frontend/src/shared/api.js`** — `newChat(project)`, `listChats(project)` → satırlar,
  `openChat(project, chat)`, `askQuestion(project, chat, text)`, `stopAgent(project, chat)`,
  `workingChats(project)` → kimlikler.
- **`frontend/src/features/agent/useAgentChat.js`** — `useAgentChat(project)`: sunucunun sohbetleri,
  çalışanlar, liste, taslak, yoldaki soru, hata, ve basışlar; yoklama burada.
- **`frontend/src/features/agent/AgentPanel.jsx`** — `AgentPanel({ project, heading })`: başlık satırı
  (`heading` + iki düğme), konuşma, kutu, liste; kaydırma ve odak burada.
- **`frontend/src/features/photo_generation/SidePanel.jsx`** — agent panelinde başlığı
  `AgentPanel`'e verir, kendisi çizmez; `photo_generation/AgentPanel.jsx` silinir. Agent kendi
  özelliği: sunucudaki `features/agent/` gibi.
- **`frontend/src/shared/app.css`** — tasarımın `kit.css`'indeki `qe-chat` bloğu.

## Nasıl kanıtlanıyor

Panel, `fetch` yerine konan sahte bir sunucuyla çizilir *(CODE-STANDARD, Tests — `vi.stubGlobal`)*:
sahte sunucu sohbetleri ve çalışanları bellekte tutar, altı kapıya 417 ve 420'nin biçimiyle cevap
verir, ve her isteği not eder. Test sunucunun hâlini değiştirir — bir adım yazar, cevap verir, ağı
düşürür, bir soruyu yolda tutar — ve saati `POLL_MS` kadar ilerletir: ekranın ne gördüğü yoklamadan
gelir. Saat sahte (`vi.useFakeTimers()`), hiçbir test gerçek bir saniye beklemez. Ekran hafızası
modülde olduğu için her test modülü yeniden yükler (`vi.resetModules()` — `SidePanel.test.jsx`'in
yolu): her test bir sayfa yenilemesiyle başlar. Kaydırma jsdom'da ölçülmez; konuşma kutusunun
yüksekliği ve cevabın boyu testte elle verilir.

## Yazılacak testler

### `frontend/src/features/agent/AgentPanel.test.jsx` — yeni

**Açılış**

1. **En yeni sohbet açılır: sorusu, bitmiş adımları, cevabı** — 1 (eski, cevaplı) ve 2 (yeni; iki
   bitmiş adım, cevap): 2'nin sorusu, *"Projeye baktı"*, *"2 numaralı kareyi okudu"*, cevabı; 1'in
   sorusu yok; canlı nokta yok; *Gönder* kapalı. İstekler: liste, çalışanlar, 2. Yeni sohbet istenmez.
2. **Sorulu sohbet yoksa bekleyen boş sohbet açılır** — `POST …/chats`; *"Projeyle ilgili bir şey
   sor."*, *"Sorunu yaz…"*, *Gönder* kapalı.
3. **Yenilemeden sonra en yeni sohbet agent'ı çalışırken gelir** — 1 çalışıyor; bitmiş *"Projeye
   baktı"*, süren *"3 numaralı kareyi okuyor…"*: süren satır `is-live` ve canlı noktalı, en altta;
   düğme *Durdur*.
4. **Yeniden başlamada yarıda kalan soru cevapsız, açık adımı canlı değil** — sonucu yok, çalışanlarda
   değil: *"3 numaralı kareyi okuyor…"* görünür, canlı nokta yok, *"Durduruldu"* yok, düğme *Gönder*;
   saat 5 sn ilerler, yeni istek yok.
5. **Okunamayan sohbet kartla söylenir** — ağ yok: *"Sunucuya ulaşılamadı — bağlantıyı kontrol et."*
   kartı; kutu yok.
6. **Başlık ve iki düğme bir satırda** — verilen başlık, *"Yeni sohbet"*, *"Sohbetler"* aynı
   `qe-chat-head`'de.

**Soru**

7. **Enter gönderir: kutu boşalır, soru balon, agent çalışır** — `POST …/chats/1/questions`, gövde
   `{"text": "Kaç kare var?"}`; kutu boş; balon; canlı *"Çalışıyor…"*; düğme *Durdur*.
8. **Shift+Enter göndermez** — istek yok, tuşun varsayılanı engellenmez.
9. **Kutu boşsa ya da yalnız boşluksa ↑ kapalı** — parametreli: `""`, `"   "`, `"\n"`; `"a"` açık.
10. **↑'ya basmak gönderir, kırpılmış yazıyı, ve odağı kutuya verir** — `"  Kaç kare var?\n"` →
    `"Kaç kare var?"`; odak kutuda.
11. **Soru yoldayken balon ve "Çalışıyor…"; ■ bir şey yapmaz** — sunucu soruyu tutar: balon, canlı
    *"Çalışıyor…"*, *Durdur*; basılır, durdurma isteği gitmez; soru varınca sohbet sunucunun.
12. **Adımlar sorunun altına gelir, süren en altta ve canlı** — sunucu *"Projeye bakıyor…"* yazar →
    bir yoklama → o canlı; *"2 numaralı kareyi okuyor…"* → bir yoklama → satırlar *"Projeye baktı"*,
    *"2 numaralı kareyi okuyor…"*, ikincisi canlı.
13. **Cevap adımlarının altında tek seferde gelir, düğme ↑'ya döner, yoklama durur** — satırlar ikisi
    de bitmiş, cevap `qe-chat-a`, canlı nokta yok, *Gönder*; 5 sn daha, yeni istek yok.
14. **Hata cevabın yerinde kart, sunucunun sözleriyle, yeniden dene yok** — parametreli: ret cümlesi,
    teknik hatanın metni.
15. **Sunucunun almadığı soru balon ve kart, adım yok** — parametreli: ağ yok → *"Sunucuya
    ulaşılamadı — bağlantıyı kontrol et."*; 409 → *"Bu sohbette agent hâlâ çalışıyor."*. Düğme
    *Gönder*.
16. **Çalışırken yazılır ama Enter göndermez** — yazı kutuda, soru isteği yok, düğme *Durdur*.

**Durdurmak**

17. **■ agent'ı durdurur: bitmiş adım kalır, süren düşer, "Durduruldu" eklenir** — kutu boşken
    *Durdur* açık; `POST …/stop`; satırlar yalnız *"Projeye baktı"*, *"Durduruldu"*, cevap yok,
    *Gönder*, odak kutuda.
18. **Çalışırken yazılan yazı durdurunca kalır, ↑ açılır.**

**Geri dönüş**

19. **Panel kapanıp açılınca sohbet agent'ın vardığı yerde, taslağıyla** — panel kapanınca yoklama
    durur (istek yok); sunucu cevap verir; panel açılınca liste istenmeden 1 okunur: cevap orada,
    kutuda taslak.
20. **Başka proje kendi sohbetleriyle açılır** — `düğün`'de 2 açıkken panel kapanır; `kına`'da ilk
    istek `kına`'nın listesi.
21. **Açık sohbet boşken başka sohbet çalışırsa açık sohbet yeniden okunmaz** — 1 çalışıyor, 2 açık:
    yoklamalarda yalnız çalışanlar istenir.
22. **Ulaşamayan yoklama kartla söylenir, sunucu dönünce kart gider** — ağ düşer: kart; ağ döner ve
    sunucu bir adım yazar: kart yok, adım geldi.

**Liste**

23. **"Sohbetler" listeyi konuşmanın yerinde açar: en yeni üstte, ilk soru ve son sorunun tarihi, açık
    olan işaretli** — 1, 2 (açık) ve boş 3: satırlar 2, 1; 3 yok; 2'nin satırı `is-on` ve
    *"5 Eki 2026 · 15:48"*; *Sohbetler* basılı; kutu yok.
24. **Agent'ı çalışan sohbetin satırında canlı nokta, agent bitince gider** — *"Agent çalışıyor"*;
    sunucu cevap verir → bir yoklama → nokta yok.
25. **Boş liste "Henüz sohbet yok." der.**
26. **Satır sohbetini açar, liste kapanır** — 1'in sorusu ve cevabı; *Sohbetler* basılı değil.
27. **"Sohbetler"e yeniden basmak açık sohbeti geri getirir** — sunucudan yeniden okunarak.
28. **Liste açıkken kapanan panel listeyle açılır.**
29. **"Yeni sohbet" boş sohbeti açar, imleç kutuda — listeden de** — `POST …/chats`; liste kapalı.
30. **İki sohbet aynı anda: biri çalışırken yeni sohbet soru sorar** — 1 çalışıyor; yeni sohbet 2;
    soru `POST …/chats/2/questions`; *Durdur*; listede iki satırda da canlı nokta.
31. **Taslak sohbetiyle kalır** — 2'de yazılan, yeni sohbette yok, listeden 2'ye dönünce yerinde.

**Kaydırma**

32. **Yukarı kaydırmış okuyucuyu yeni adım aşağı çekmez.**
33. **En alttaki konuşma yeni adımla iner.**
34. **Uzun cevap adımlarının başından okunur** — cevabın boyu konuşmadan büyük: konuşma adımların
    başında.

### `frontend/src/features/photo_generation/SidePanel.test.jsx` — değişen

35. *Değişir — "opens the agent panel and leaves it deliberately empty":* agent paneli açılınca
    başlık *"AI agent"*, *"Yeni sohbet"* ve *"Sohbetler"* aynı satırda, altında sohbet; *"Agent buradan
    çalışacak."* yok.

## Kırmızı beklenen

- `AgentPanel.test.jsx`: dosya bütün olarak kırmızı — `features/agent/AgentPanel.jsx` yok. Modül her
  testin `beforeEach`'inde yüklense de Vite, `import()`'un yazılı yolunu dosyayı çevirirken çözer; yol
  yokken dosya yüklenemez ve testleri sayılmaz (*"Failed to resolve import"*).
- 35: *"Yeni sohbet"* yok, panel *"Agent buradan çalışacak."* diyor.
- Öteki her şey yeşil; öteki üç satır yeşil.

## Bilinçli olarak yapılmayan

- Sunucuda değişiklik — kapılar 417 ve 420'nin, olduğu gibi. Eksik bir kapı görülmedi.
- `dist` — koşunun birleşmesinde kurulur; yol haritası.
- `sessionStorage` ya da `localStorage`; sohbet silme, yeniden adlandırma, arama; yeniden dene düğmesi;
  Esc ile durdurma; akış (stream); markdown çizimi.
- Şeritte cevap işareti — tasarım istemiyor *(207 — "Panel kapanınca bildirim yok")*.
- Başka bir sekmede başlatılan agent'ı bu sekmenin kendiliğinden görmesi: yoklama, bu sekmenin bildiği
  bir agent çalışırken döner.
