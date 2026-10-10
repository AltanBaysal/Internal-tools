# Madde 463 · Mod sohbetin ayarıdır ve backend'de durur — tasarım

**Tarih:** 10 Ekim 2026 · **Madde:** [v10 yol haritası](../roadmaps/2026-10-05-queen-agent-v10-roadmap.md),
463 · **Dal:** `feat/queenagent-v10`, ana klasörde · **Kurallar:**
[FOUNDATION](../../queen-agent/FOUNDATION.md) · [CODE-STANDARD](../../queen-agent/CODE-STANDARD.md) ·
**Kaynak:** mimarın sohbet tasarımı (`tmp/chat-turn-design.md`), 9. bölümün 4. adımı; 4, 5, 7 ve 8.
bölümler. **Öncesi:** [461](2026-10-10-queen-agent-m461-tur-kendi-basina-design.md) (tur kendi başına),
[462](2026-10-10-queen-agent-m462-ekran-sunucu-durumu-design.md) (ekran sunucunun durumunu çizer).

## Ne, neden

**Bugün** mod (Plan, Ask, Edit) tarayıcıda duruyor: `App.jsx`'in `lastMode`'u, oturum boyunca ve
bütün sohbetler için tek bir değer. Her mesajla ve 462'nin Try again kapısıyla (`{mode}`) gönderiliyor;
`run_turn` onu parametre olarak alıyor ve tur boyunca yalnız kendi kopyasını biliyor. "Allow deyince
Edit'e geç" kuralı iki yerde: `App.jsx` (`setLastMode(EDIT)`) ve `run_turn`'ün yerel `mode = EDIT`'i.
Sayfa yenilenince mod Edit'e dönüyor; başka sekme başka mod gösteriyor; tur sürerken seçilen mod o turu
etkilemiyor.

**Olacak** (kullanıcı — *"ask edit plan vs zaten frontend'de durması mantıklı değil, çünkü dosyalar
backend'de … biz sadece modun bilgisini göndermemiz lazım"*; *"evet her sohbetin kendi ayarı olacak
tabii ki"*):

- Her sohbetin modu `projects.json`'daki satırında durur. Sayfa yenilenince ve başka sekmede aynıdır.
- Tarayıcı yalnız seçileni gönderir: `POST …/chats/<c>/mode {mode}`.
- Süren tur modu her tool çağrısında satırdan okur: tur sürerken seçilen mod bir sonraki çağrıdan
  itibaren geçerlidir.
- Allow'un Edit'e geçirmesi sunucunun kuralıdır.
- Yeni sohbet Edit'le başlar. Taslak, kullanıcının seçtiği modu doğana kadar kendisi tutar ve ilk
  mesajla gönderir.

## Nasıl

### Kayıt — `data/file_project_store.py`

- Sohbet satırı isteğe bağlı bir `mode` alanı kazanır. **Yalnız Edit değilken yazılır**, `pinnedAt` ve
  `archived` gibi: yokluğu sık olan hâldir ve Edit demektir. Eski satırlar ve 448'in taşıdığı projeler
  hiçbir şey istemez, göç yok.
- Bilinmeyen bir değer (elle yazılmış `"mode": 5` gibi) Edit okunur. Dosya bu yüzden reddedilmez: bir
  mod, projeyi açılmaz yapacak kadar önemli değil.
- `chat_mode(proje, sohbet)` → mod ya da satır yoksa `None`; `set_chat_mode(proje, sohbet, mod)` →
  satır varsa `True`. İkisi de bellekte, aynı kilidin altında; değişiklik sıradaki yazıcıya gider.
- **447'nin koduna düzeltme, bu madde için gerekli:** `_put` satırı bütünüyle değiştiriyordu. Mod
  satırda durunca, sohbetin her yazılışı (turun son yazısı, Try again'in düşürmesi, sürüm, kırpma) modu
  silerdi. Artık var olan satırın alanlarını yerinde günceller (`existing.update(row)`), mod kalır.

### Port — `domain/ports.py`

- `ChatStore.mode_of(proje, sohbet) -> str | None` ve `ChatStore.set_mode(proje, sohbet, mod) -> bool`.
  `FileChatStore` ikisini `projects.json`'un tutucusuna sorar, `put_chat` gibi.
- `LiveTurn.asks(tur, bekleme) -> bool`: bu tur, bu soruyu şu an soruyor mu.
- `TurnControl`'e mod **eklenmedi** (ana ajanın onayı): `LiveTurn.mode()`, ya satırın yanında modun
  ikinci bir kopyasını tutmak (POST mode ve Allow ikisini de güncellemeli, kayabilir) ya da store'u
  tutmak (LiveTurns'e store, her tura proje ve sohbet kimliği) demekti. İkisi de aynı bellek okuması
  için yeni parça. `ChatStore`'un mod kapıları GET ve POST mode için zaten gerekli.

### Kurallar — `domain/`

- `modes.py`: `MODES = (PLAN, ASK, EDIT)`, bilinen modlar.
- **`run_turn`** modu parametre almaz. Her tool çağrısında `chat_store.mode_of(proje, sohbet)` okunur
  (bellek), `needs_permission` ve `ends_the_turn` o değerle sorulur. Allow'dan sonraki yerel
  `mode = EDIT` gider: o kural artık `answer_question`'ın.
- **`usecases/pick_mode.py`** (yeni): `pick_mode(chat_store, proje, sohbet, mod)` — bilinmeyen mod
  `UnknownMode`, satırı olmayan sohbet `ChatNotFound`; yoksa satıra yazar ve modu döner. Sohbet
  dosyasına dokunmaz.
- **`usecases/answer_question.py`** (yeni): izin cevabı. Canlı tur yoksa `None`. Cevap Allow ise ve
  turun şu an sorduğu soruyu adlandırıyorsa (`asks`), **önce** sohbetin modu Edit yapılır, **sonra**
  `decide` turu uyandırır. Sıra şart: tersinde, aynı turdaki ikinci çağrı satırı uyanıştan hemen
  sonra, Edit yazılmadan okuyabilir ve aynı soruyu yeniden sorardı. Bayat bir Allow (başka tur, başka
  soru) modu değiştirmez.
- **`advance_chat`**: `mode` yalnız taslak içindir. Bilinmeyen mod `UnknownMode` alır ve sohbet tutulmadan
  reddedilir. Sohbet doğunca, tur başlamadan önce satırına yazılır; boşsa yazılmaz (Edit). Var olan
  sohbete mesajla gelen mod, ve retry'la gelen, yok sayılır: eski bir sekme gönderiyle sohbetin modunu
  değiştiremez.
- `errors.py`: `UnknownMode`.

### Cevaplar — `presentation/routes.py`

- `_chat_state(chat, snapshot, mode)` → sohbet + `status` + `mode` + `turn`. GET chat, gönderme ve
  düzenlemenin 202'si, retry'ın 200/202'si ve 409 bunu verir. Her biri ekrandaki sohbeti bütünüyle
  değiştirir, o yüzden her birinin modu taşıması gerekir. Mod, bu cevabı kuran tek yardımcıda
  (`chat_state`) `chat_store.mode_of`'la okunur (bellek); `read_chat` değişmez.
- `POST …/chats/<c>/mode {mode}` → `200 {mode}`; bilinmeyen mod `400 {"error": "mode must be plan, ask
  or edit"}`; olmayan sohbet `404`. Kayıt yok: mod değişikliği sohbet dosyasını okumaz, gönderecek bir
  kaydı da yoktur.
- `POST …/permission` → `{turn, mode}`, canlı tur yokken de (`{turn: null, mode}`). Satırı olmayan
  sohbet 404.
- Stop ve olay akışı modu **taşımaz**. Snapshot turun hâlidir, sohbetin değil. Ekran turu elindeki
  sohbetin içine koyar, mod yerinde kalır.
- Taslağın ilk mesajında bilinmeyen mod 400 ile, aynı cümleyle reddedilir.

### Ekran — `frontend/src/`

- **`App.jsx`**: `lastMode`, `setLastMode(EDIT)` ve Try again'e giden mod argümanı gider. Gösterilen
  mod taslakta `draftMode`, sohbette `chat.chat.mode`. Seçim taslakta `setDraftMode`'a, sohbette
  `chat.pickMode`'a gider. `draftMode` Edit'le başlar, doğumda ilk mesajla gönderilir ve Edit'e döner
  (`draftSkill` gibi).
- **`useChat.js`**:
  - `pickMode(mode)`: seçim **hemen** çizilir. Bugün seçici tıklamaya anında cevap veriyor; Colab'da
    bir gidiş dönüş sonra değişen etiket bozuk bir düğme gibi okunurdu (ana ajanın kararı). Bunun
    için tek bir parça durum var: `picked = {key, mode}`. Yanında iki ref duruyor: seçimlerin zinciri
    ve en yenisi.
  - **Seçimler sırayla gider:** her seçimin POST'u bir öncekinin cevabından sonra çıkar. Yan yana
    gönderilen iki istek sunucuya ters sırayla varabilirdi; örneğin Edit'ten sonra hızlıca Ask'e
    düzeltmek, sunucuyu Edit'te, ekranı Ask'te bırakabilirdi (reviewer'ın bulgusu). Tıklama sırasıyla
    giden her cevap, geldiği anda sunucunun nerede olduğunu söyler. O yüzden her cevap sohbetin
    `mode`'u olur, ve sonraki bir seçim reddedilirse sunucunun aldığı önceki seçim ekranda kalır. Yolda
    olan en yeni seçim çizilir. Hata kartını yalnız en yeni seçimin reddi yazar.
  - Ekranda zaten duran modu seçmek sunucuya hiçbir şey sormaz. Sunucuda da aynı mod değişiklik
    sayılmaz ve yazıcı uyandırılmaz.
  - `answer` (Allow ya da Deny): kapının cevabındaki `mode`'u sohbete yazar. Allow'dan sonraki Edit
    sunucudan gelir.
  - `send(text, skill, from, mode)`: `mode` yalnız taslağın ilk mesajında gider. `retry` mod göndermez.
- **`modes.js`**: `EDIT` ihracı gider (tek kullanıcısı Allow kuralıydı). `DEFAULT_MODE` kalır: boş
  taslağın çizdiği, ve kaydı henüz gelmemiş sohbette adın düştüğü değer bu. Taslağın ilk mesajı
  modunu gönderdiği için, **tarayıcıda doğan bir sohbetin modunu tarayıcının varsayılanı belirler**.
  Sunucunun varsayılanı (`modes.DEFAULT`) mod göndermeyen istemciler ve eski satırlar içindir. İkisi
  bugün aynı değer, Edit. Biri değişirse öteki de değişmeli; taslak sohbet doğmadan bir değer çizmek
  zorunda olduğu için bu kopya bilerek duruyor.

### Kural dosyası

CODE-STANDARD'ın "`projects.json` yalnız listenin gösterdiğini tutar" cümlesi "ve sohbetin ayarlarını"
diye genişler. Taslağı ana ajanın raporunda; kullanıcıya o götürür.

## Sınırlar

- **Dinleyen ikinci sekme:** tur sürerken başka sekmede seçilen modu, bu sekme canlı görmez. Turun
  sonundaki okumada ya da sekmeye dönünce görür. Olaylar modu taşımaz (yukarıda).
- **Allow ve Stop aynı anda:** `asks` ile `decide` arasında bir Stop inerse, sohbet Edit'te kalır ama
  hiçbir şeye izin verilmemiş olur. Zararsız sayıldı: Allow "çalış" demektir.
- **Allow ve kullanıcının seçimi aynı anda:** ikisi de satıra aynı kilidin altında yazar, son yazan
  kazanır. Allow'dan hemen sonra Ask seçilirse turun kalan çağrıları yeniden sorar. Kullanıcının son
  sözü budur.
- **Tur sürerken seçilen mod:** o anda izin bekleyen ya da koşan çağrıyı etkilemez, bir sonrakinden
  itibaren geçerlidir.
- **Silinen proje:** sohbet tek başına silinmez. Projesi silinmiş sohbetin modu 404 alır. Silmeyle aynı
  anda gelen bir mod değişikliği, çöpe giden `project.json`'a girmeyebilir. Kaybolan şey silinmiş bir
  sohbetin modudur.
- **Çöküş:** mod, `projects.json`'un diğer alanları gibi sıradaki yazıcıyla gider. Sunucu ani ölürse
  henüz yazılmamış bir mod değişikliği kaybolur (FOUNDATION ilke 2'nin kabul ettiği bedel).
- Taslak sayfası yenilenirse seçilen mod Edit'e döner, taslağın skill'i gibi: taslak sunucuda yok.
- **Seçimden önce başlayan tam okuma:** bir seçimden önce başlayıp cevabından sonra inen bir okuma
  (turun sonundaki okuma, sekmeye dönüş) eski modu çizebilir. Ekran bir sonraki okumaya kadar
  (yenileme, sekmeye dönüş, turun sonu) bunu gösterir; sunucu doğru modu tutar. Pencere bir gidiş
  dönüş kadar; koruması bir iki satıra sığmadığı için yazılmadı.
- Elle bilinmeyen bir mod yazılmış satırda Edit seçmek değişiklik sayılmaz. Garip değer başka
  bir mod seçilene kadar durur, ama Edit okunur.

## Maliyet (Drive'da gidiş dönüş)

| İşlem | Önce | Sonra |
|---|---|---|
| Mod seçmek | 0 (yalnız tarayıcı) | sohbet dosyası 0 okuma, 0 yazma; `projects.json` bir sıralı yazı; zaten duran mod: 0 istek |
| Tur sürerken modu okumak | — (parametre) | bellek; tool çağrısı başına projenin satırlarında bir tarama, O(sohbet sayısı) |
| GET chat | 1 okuma (tur yokken) | aynı + bellekte bir mod okuması |
| İzin cevabı | 0 | 0; Allow'da `projects.json` bir sıralı yazı |
| Taslağın ilk mesajı | 0 okuma, 2 yazma | aynı; mod Edit değilse `projects.json` değişikliği aynı sıralı yazıya katılır |

Bütün işlemler projelerin, sohbetlerin ve dosyaların sayısından bağımsız olarak O(1) diske gider.

## Bitti sayılır

- Bir sohbetin modu sayfa yenilenince ve başka sekmede aynı.
- Yeni sohbet Edit'te; taslakta seçilen mod sohbetin modu olarak doğuyor.
- İki sohbet kendi modunu tutuyor.
- Tur sürerken seçilen mod turun bir sonraki tool çağrısında geçerli.
- Allow'dan sonra mod Edit; bayat Allow modu değiştirmiyor.
- Retry mod göndermiyor; var olan sohbete mesajla gelen mod yok sayılıyor.
- `App.jsx`'te `lastMode` ve Allow→Edit kuralı yok; seçici tıklamaya hemen cevap veriyor ve reddedilen
  seçim geri dönüp hata kartını gösteriyor.
- Dört test takımı yeşil. Tek istisna, dist sahnelenene kadar beklenen
  `test_the_page_asks_for_files_that_were_committed_with_it`.
