# QueenAgent — modele giden her metin

**İlk yazımı:** 28 Ağustos 2026 · **Son eşleme:** 4 Eylül 2026 *(v6 ve v7 koşuları: Madde 150–165,
artı üç adlandırma düzeltmesi. Bu kopya `feat/v7` dalının hâli.)*

**Yaşayan asılları kodda** — `prompt.py`, `tools.py`, `skills.py`, `permission.py`,
`context_box.py`, `stream_answer.py` — ve kod değişirse doğru olan onlardır, bu belge değil. Belge
bir kopya taşıyor ve kopya bayatlar; **§2'nin araç sayısı** ile `TOOL_SPECS`'in uzunluğu birbirini
tutmuyorsa inanılacak olan kod.

> ⚠️ **Dört metin bilerek koddan ileride.** §3.1'in `SYSTEM_PROMPT`'u ve §3.9'un `read_file`,
> `create_file`, `write_plan` açıklamaları **taslak** — üzerinde konuşuldu, koda henüz geçmedi. Bu
> belge o dört metnin **hedefi**, ve kod belge oturduktan sonra tek koşuda buraya getirilecek.
> Geri kalan her metin bugünkü kodla birebir.

**Belge üç bölüm.** Yapıyı öğrenmek isteyen §1'i okur ve tek satır İngilizce metin görmez; hangi
araç ne yapıyor diye bakan §2'ye gider; modele **ne dendiğini** okuyacak olan §3'ü baştan sona
okur. Metinler yalnız §3'te.

---

# §1 · İstek nasıl yapılanıyor

Uygulamada modele giden **yalnız iki** istek şekli var, ve ikisi hiçbir şeyi paylaşmıyor — bu yüzden
aşağıda yan yana değil, **ayrı ayrı** anlatılıyorlar. Ortak bir katmanları olmadığı için karşılaştırma
her satırda "öteki bunu almıyor" demekten ibaret kalıyordu.

> **İki kelime, iki ölçek.** Bir **tur**, kullanıcının bir mesajına verilen tek cevap. O turun içinde
> en fazla **16 raund** var, ve her raund modele atılan ayrı bir istek — `MAX_ROUNDS = 16` raundu
> sayar, turu değil. Belge boyunca "tur" hep cevabın tamamı, "raund" hep tek bir istek.

```mermaid
flowchart TB
    subgraph A["ANA AJAN RAUNDU · stream_answer → engine.stream"]
        direction TB
        A1["<b>1 · SYSTEM_PROMPT</b><br/>system · prompt.py<br/>QueenAgent kim, nasıl çalışır<br/><i>_for_xai en başa koyar</i>"]
        A2["<b>2 · Konuşma</b><br/>user / assistant<br/>sohbetin tamamı + bu turun araç çağrıları"]
        A3["<b>3 · Dosya adları</b><br/>system · _named<br/>projede ne var, tek satır"]
        A4["<b>4 · Bağlam kabı</b><br/>system · _boxed<br/>okunmuş son 5 dosyanın <i>o anki</i> içeriği<br/><i>yalnız okunmuş dosya varsa</i>"]
        A5["<b>5 · Skill metni</b><br/>system · skills.py<br/><i>yalnız skill seçiliyse</i>"]
        A6["<b>6 · LAST_ROUND</b><br/>system · prompt.py<br/><i>yalnız 16. raundda</i>"]
        A1 --> A2 --> A3 --> A4 --> A5 --> A6
    end
    subgraph B["KARE İSTEĞİ · write_frame_prompt → engine.write_once"]
        direction TB
        B1["<b>1 · WRITE_FRAME_SYSTEM_PROMPT</b><br/>system · tools.py<br/>promptu nasıl yazacağı, ve <b>yalnız o</b>"]
        B2["<b>2 · Haritalar + sahne</b><br/>user<br/>karakterler, kıyafetler, mekânlar JSON<br/>+ o karenin tek cümlesi"]
        B1 --> B2
    end
    A -.->|"tools: 17 araç<br/><i>son raund hariç</i>"| T["<b>tools alanı</b><br/>mesaj değil, isteğin ayrı alanı"]
    B -.->|"araç yok"| N["—"]
```

## A · Ana ajan raundu — `stream_answer` → `engine.stream`

*Sohbetin kendisi. Sırayı `stream_answer.py`'nin `_asked`'ı kuruyor; `SYSTEM_PROMPT`'u en başa
koyan `xai_engine.py`'nin `_for_xai`'si.*

| # | Katman | Ne zaman girer | Metni |
|---|---|---|---|
| 1 | Taban yönerge | Her raundda, en başta | §3.1 |
| 2 | Konuşma geçmişi | Her raundda — bu turun araç çağrıları da içinde, **ama yalnız tur boyunca** | *(metin değil, kaydın kendisi)* |
| 3 | Dosya adları | Her raundda, diskten taze | §3.2 |
| 4 | Bağlam kabı | Yalnız okunmuş dosya varsa | §3.3 |
| 5 | Skill metni | Yalnız skill seçiliyse — ve **en sonda** | §3.4 |
| 6 | Son raund bildirimi | Yalnız **16.** raundda | §3.5 |

- **`tools` alanı:** 17 araç, son raund hariç. Mesaj metnine yapıştırılmıyor — isteğin ayrı bir alanı.
- **Kaç kere gider:** raundda bir, turda en fazla on altı.
- **Hangi model:** turun kendi modeli, `_current_model`.

### 1 · Taban yönerge

`prompt.py`'nin `SYSTEM_PROMPT`'u. Her kipte, her skill'de, her raundda, en başta — ve isteğin
değişmeyen başı olduğu için sağlayıcının önbelleğe aldığı önek de bu.

**Dört araç adıyla anılıyor** — `read_file`, `create_file`, `edit_file`, `write_plan`. Kaynak
doküman *("Provide extremely detailed descriptions. This is by far the most important factor in tool
performance.")* asıl kaldıracın aracın kendi açıklaması olduğunu söylüyor, ama adı anmayı
yasaklamıyor: bir **seçimi yönlendirmek** için prose'da ad vermeyi açıkça öneriyor. Bölüşüm o:
**tanım detayı taşır, taban işaret eder.**

4 Eylül'de dört ad tabandan çıkarıldı ve aynı gün geri kondu *(kullanıcı: "geri getirelim, AI böyle
daha kolay anlıyor")*. Aradan kalıcı olan şey **araç açıklamalarının kalınlaşması** oldu.

**Bunun bedeli açık: aynı şey iki yerde yazılı.** Bilerek — biri işaret, öteki detay — ama drift
riski gerçek. Kapatan bekçi: **tabanda anılan her araç adı `TOOL_SPECS`'te var mı** diye bakan bir
test. Silinen bir araç adı tabanda kalırsa m127'nin `list_files` hatası aynen tekrarlanır, ve o hata
bir denemeye mal olmuştu.

### 2 · Konuşma

`stream_answer.py`'nin `_conversation`'ı · Kaydın tamamı, `{"role", "content"}` çiftleri olarak.
Diskte roller `user` ve `ai`; `_for_xai` ikincisini `assistant`'a çeviriyor.

**Tur içinde büyüyor, tur bitince kayboluyor.** Her raund iki şey ekliyor: modelin `tool_calls`
taşıyan mesajı, ve her çağrı için aracın cevabı *(`role: tool`)*. Büyümek zorunda — model bir araç
istedi, cevabı aynı listede dönmezse bir sonraki raund çağrının olduğunu bilemez ve aynı aracı
yeniden çağırır.

Ama bu liste **yalnız o cevaba ait**, ve diske hiç yazılmıyor *(`stream_answer.py:180`'in kendi
yorumu: "Local to this answer and never written to the chat")*. Tur bitince kayda giren tek şey **bir
`ai` mesajı**: modelin söylediklerinin birleşmiş hâli, yanında da adım kartları *(araç adı, hedef
dosya, sonuç kelimesi)*. `_conversation` bir sonraki turda yalnız `role` ve `text` okuyor — kartlar
isteğe geri girmiyor. **Yani on altı raundluk araç trafiği turla birlikte buharlaşıyor.**

Sohbetin freni `CONTEXT_CEILING = 50_000`: son raundun boyu bunu geçen bir sohbet yeni tur almıyor.

### 3 · Dosya adları

`stream_answer.py`'nin `_named`'i · Madde 127. Her raundda diskten yeniden okunuyor, yani tur
ortasında doğan dosya bir sonraki raundda görünüyor. **Bu satır olduğu için modelin "neler var" diye
soracağı bir araca gerek kalmadı** — `list_files` o gün silindi.

### 4 · Bağlam kabı

`stream_answer.py`'nin `_boxed`'ı ve `context_box.py` · Madde 129. Sohbetin `read_file` ile açtığı
**son 5 dosya**. Kap **ad** tutuyor, içerik değil: her istekte diskten okunuyor, dolayısıyla hep
güncel — modelin kendi yazdığını geri okumasının sebebi böylece kalkıyor. Turlar arası yaşıyor.
Okunmuş hiçbir dosya yoksa kap hiç gönderilmiyor. Bulunamayan bir ad sessizce atlanıyor.

Madde 131'den beri bloklar **satır numaralı** — `read_file` neyi nasıl gösteriyorsa kapta da öyle,
çünkü kap geldiğinden beri modelin dosyaya baktığı yer burası ve iki ayrı biçim, çapanın hangisine
uyacağını seçtirirdi.

> ⚠️ **Ölçülmemiş bedel.** Bu kap **her raundda** gidiyor. 40 karelik bir yapı dosyası kabaca 15 KB
> ≈ 4–5 bin jeton, ve dosya bir kez okunduktan sonra sohbetin geri kalanında her raund yeniden
> biniyor. Hata değil — 129 donmuş kopyanın bayatlamasını çözerken bunu seçti — ama o gün yapı
> dosyaları küçüktü; artık sahne, prompt ve numara taşıyorlar. **Turda biriken tek şey bu**, araç
> trafiği değil. Colab denemesinde damgadaki gerçek rakama bakılacak.

### 5 · Skill metni

`skills.py` · Madde 93'ten beri konuşmanın içinde değil, isteğin **sonunda** ayrı bir system mesajı.
Turun skill'i **en yeni kullanıcı mesajınınki**, ve tur boyunca değişmiyor. Skill seçili değilse bu
katman hiç yok — **sıradan hâl bu**. İki metin var; beş tanesi Madde 94'te silindi, söyledikleri
tabana taşındı.

### 6 · Son raund bildirimi

`prompt.py`'nin `LAST_ROUND`'u · Madde 137. **Yalnız 16. raundda**, her şeyin en sonunda. O raunda
araç da verilmiyor — söylenmekle kalsa bu bir rica olurdu.

> **Adı yanıltmasın: bu her turun son raundu değil, 16.'sı.** Sıradan bir tur ikinci ya da üçüncü
> raundda biter — model araç istemeyi bırakır, döngü kırılır — ve **gerçekte sonuncu olan o raund
> hiçbir bildirim almaz.** Sebebi şu: *bir raundun sonuncu olduğu ancak bittikten sonra anlaşılıyor.*
> Kod bunu modelin araç istemeden cevap vermesinden öğreniyor, ve o anda istek çoktan gitmiş oluyor.
> **Önceden sonuncu olduğu bilinen tek raund 16.** — onu sonuncu yapan model değil, tavan. Kullanıcı
> durdurduğunda ve `plan` kipinde `write_plan` turu kapattığında da gitmiyor. Yani bir kapanış
> merasimi değil, **bütçenin bittiğini söyleyen uyarı**.

## B · Kare isteği — `write_frame_prompt` → `engine.write_once`

*Bir aracın içinden çıkan, sohbetten habersiz istek. `tools.py`'nin `_write_frame_prompt`'u atıyor,
ve `xai_engine.py`'nin `write_once`'ı `_for_xai`'yi **bilerek** atlıyor.*

| # | Katman | Ne zaman girer | Metni |
|---|---|---|---|
| 1 | `WRITE_FRAME_SYSTEM_PROMPT` | Her istekte — tek sistem mesajı | §3.6 |
| 2 | Haritalar + sahne | Her istekte — tek kullanıcı mesajı | §3.7 |

- **`tools` alanı yok.** Bu isteğin çağırabileceği bir araç yok; cevabı JSON, araç çağrısı değil.
- **Kaç kere gider:** kare başına bir, bir çağrıda en fazla yüz.
- **Hangi model:** turun modeli. `stream_answer` `_current_model`'ı `run_tool`'a, o da `write_once`'a
  geçiriyor — **ayrı olan model değil isteğin kendisi**: sohbetsiz, araçsız, tek işi olan bir soru.

**İsteğin tamamı iki satır:**

```python
[{"role": "system", "content": WRITE_FRAME_SYSTEM_PROMPT},
 {"role": "user",   "content": f"{maps}\n\nScene: {frame['scene']}"}]
```

**Neden döngü, tek bir istek değil:** ana ajanda 16 raund demek, her raundda bütün sohbet geçmişini
yeniden göndermek demek — 40 kare oraya sığmazdı, ve kare başına düşen dikkat senaryo büyüdükçe
azalırdı. Buradaki istek yalnız talimat + haritalar + bir cümle taşıyor.

**Almadığı şey uygulamanın `SYSTEM_PROMPT`'u**, ve bu bilerek: o metin projesi, dosyaları ve araçları
olan bir sohbet asistanını anlatıyor — bu çağrının olmadığı her şeyi. Onun yerine kendi personası
duruyor.

**Nasıl akıyor:** ilk istek **tek başına** gider ve sağlayıcının ön ek önbelleğini ısıtır *(hepsi
birden uçsa hiçbiri önbelleği sıcak bulmazdı)*, sonra **kalanın hepsi birden** *(Madde 165)*. Eskiden
beşerli dalgalar hâlindeydi; beşin gerekçesi artık bu uygulamada olmayan bir sağlayıcının ölçümüydü.
Bir çağrıda en fazla **100** istek. Tekrar deneme yok: düşen istek boş kalan bir kare, ve o kare
cevapta sayılıyor.

**Cevabından beklenen:** yalnız JSON — `characters`, `location`, `action`, `camera`. Ayrıştırılamayan
ya da haritaların bilmediği bir ad taşıyan cevap **o kareyi boş bırakıyor**, komşularına dokunmadan.
Araç yalnız boşları doldurduğu için **tekrar çağırmak zaten tekrar denemek**.

### Ana ajana dönen rapor

Yüz isteğin sonucu ana ajana **tek cümle** olarak dönüyor — kareler tek tek değil, sayılarla
*(metni §3.10'da)*.

- **Söylemediği şey: hangi karelerin düştüğü.** Yalnız kaç tane. Kodun kendi gerekçesi *"modelin
  ihtiyacı olan şey sayı"* — araç zaten yalnız boşları doldurduğu için modelin yapacağı tek şey
  yeniden çağırmak, ve bunun için numaraya ihtiyacı yok. Numara isteyen taraf **kullanıcı**, ve o
  dosyayı zaten görüyor.
- **Fatura da dönüyor:** yüz alt isteğin harcaması turun hesabına ekleniyor, yani damgada görünüyor.
  Uygulamada **para harcayan tek araç** bu.

## Sıra neden böyle

**Sabit olan başta, değişen sonda.** Dikkat bir bağlamın iki ucunda en yüksek ve ortada üçte birden
fazla düşüyor; ön ek önbelleği ise başın hiç değişmemesini istiyor. `SYSTEM_PROMPT` her istekte
aynı, skill metni raunddan raunda aynı ama sohbete göre değişiyor, `LAST_ROUND` on altı raundun
yalnız birinde var. Sıra bu ölçüye göre dizilmiş.

**Dosya adları ve kap ortada duruyor:** konuşmanın arkasında, çünkü bu turda doğan bir dosyanın bir
sonraki raundda görülmesi gerekiyor; skill metninin önünde, çünkü son söz Madde 93'te ona verildi.

**Her raund baştan kurulur.** Liste büyüyor — her raund modelin söylediğini ve araçların cevabını
ekliyor — o yüzden skill metni her raundda **yeniden** sona ekleniyor. Bir kez konuşmanın içine
konsaydı ikinci raunddan itibaren arkada kalırdı.

## Tur ortasında konuşmaya ne giriyor

Raund arasında modele iki şey dönüyor, ve ikisi de konuşmanın içine `role: tool` olarak giriyor:

- **Araç cevabı** — her çağrının sonucu, tek bir cümle *(metinleri §3.10)*. `build_prompts`'ın
  derlediği promptlar hiç geri basılmıyor *(Madde 130)*: cevap dosyanın adı, içeriği değil. Tek
  istisna `build_character_prompts` — o bir bakış, ve bakışın cevabı dosyanın adıysa model onu
  okumaya geri gider.
- **Red metni** — kullanıcı izin vermediğinde, çağrının cevabı olarak *(metni §3.11)*.

---

# §2 · Araçlar

*`tools.py`'nin `TOOL_SPECS`'i · **17 araç.** Bunlar mesaj metnine yapıştırılmıyor: istek iki parça —
`messages` *(§1'in katmanları)* ve `tools` — ve bu liste ikincisi.*

**Madde 99'dan beri hepsi her kipte gidiyor.** Kip *(`ask` · `plan` · `edit`)* hangilerinin
**sormadan** koşacağını söylüyor, hangilerinin gönderileceğini değil — `modes.py`. Tek istisna son
raund: cevabı okuyacak raund kalmadığı için araç verilmiyor.

Model `description` alanını okuyor; `parameters` vereceği argümanların şeması. **İkisinin de metni
§3.9'da** — burada yalnız ne yaptıkları, hangi alanları aldıkları ve hangi kipte sormadan
koştukları.

*Aşağıdaki gruplama **bu belgenin**, isteğin değil — okunsun diye. Kayıttaki sıra `TOOL_SPECS`'in
sırası, ve bir anlam taşımıyor.*

**Sütunlar:** `Kural` = açıklamasının sonuna `SDXL_PROMPT_RULES` *(§3.8)* ekleniyor mu ·
`Sormadan` = hangi kipte izin sorulmadan koşuyor.

## Dosyalar

| Araç | Ne yapar | Parametreler | Kural | Sormadan |
|---|---|---|---|---|
| `read_file` | Bir dosyayı okur; cevabı satır numaralı içeriğin kendisi | `name` ✓ | — | **hepsi** |
| `create_file` | Yeni bir belge yazar; var olan adı reddeder | `name` ✓ · `content` ✓ | — | `edit` |
| `edit_file` | Var olan bir dosyanın bir parçasını değiştirir | `name` ✓ · `old` ✓ · `new` ✓ · `replace_all` | — | `edit` |

*`create_file` ile `edit_file` bir **yapı dosyasına** dokunmayı reddediyor *(Madde 151)*. `edit_file`'ın
tek istisnası dosyanın JSON olarak okunamaması — o hâlde yapısal araçların hepsi düşer ve metin
düzenlemek doğru araçtır. `create_file`'ın `name` örneğinde `.json` yok, bilerek: uzantıyı öneren bir
örnek modeli kapalı bir kapıya gönderirdi.*

## Yapı dosyası — doğurmak ve haritalar

| Araç | Ne yapar | Parametreler | Kural | Sormadan |
|---|---|---|---|---|
| `create_structure` | Senaryonun boş JSON'unu açar — karakter, kıyafet, mekân, kare hepsi boş | `file` ✓ | — | `edit` |
| `set_character` | Karakter haritasına bir giriş yazar; `new_name` ile yeniden adlandırır | `file` ✓ · `name` ✓ · `tags` · `new_name` | ✓ | `edit` |
| `set_outfit` | Kıyafet haritası, aynı kural | `file` ✓ · `name` ✓ · `tags` · `new_name` | ✓ | `edit` |
| `set_location` | Mekân haritası, aynı kural | `file` ✓ · `name` ✓ · `tags` · `new_name` | ✓ | `edit` |

*Üç `set_` aracı **tek bir gövdeyi** paylaşıyor *(`_set_entry`)*, ve Madde 163'ten beri aynı cümleyle
reddediyor: yeni bir ad `tags` ister, var olan bir adda verilen değişir ve verilmeyen durur. Model
tarafında üç ayrı araç olmalarının sebebi, üçünün **farklı bir kural** öğretmesi — kıyafetin "bir
girdi bir kişiyi giydirir" kuralı karakterde anlamsız.*

*Yeniden adlandırma ayrı bir araç değil, `set_`'in parametresi *(Madde 161)*: yeniden adlandırma
karakterin kendi girdisi üstünde bir eylem, ve o adı anan **her kare** onunla birlikte değişiyor.*

## Yapı dosyası — silmek

| Araç | Ne yapar | Parametreler | Kural | Sormadan |
|---|---|---|---|---|
| `remove_character` | Karakteri haritadan siler; onu anan kare varsa reddeder ve numaralarını söyler | `file` ✓ · `name` ✓ | — | `edit` |
| `remove_outfit` | Kıyafet, aynısı | `file` ✓ · `name` ✓ | — | `edit` |
| `remove_location` | Mekân, aynısı | `file` ✓ · `name` ✓ | — | `edit` |
| `remove_frame` | Bir kareyi numarasıyla siler; kalanlar 1'den yeniden numaralanır | `file` ✓ · `frame` ✓ *(`integer`)* | — | `edit` |

*Silme, çağrıyı yeniden yapmanın geri alamadığı **tek** değişiklik — Madde 157'nin gerekçesi bu, ve
sessiz başarı burada hiç yok: olmayan bir adı silmek de reddediliyor.*

## Kareler

| Araç | Ne yapar | Parametreler | Kural | Sormadan |
|---|---|---|---|---|
| `add_scene` | Cümle başına bir kare açar; kare cümleden başka hiçbir şey taşımaz | `file` ✓ · `scenes` ✓ *(string dizisi)* | — | `edit` |
| `write_frame_prompt` | Sahnesi olup promptu olmayan her kareyi **kendi isteğiyle** yazar *(§1.B)* | `file` ✓ | — | `edit` |
| `update_frame` | Yazılmış bir karenin **verilen** alanlarını değiştirir | `file` ✓ · `frame` ✓ · `scene` · `characters` · `location` · `action` · `camera` | ✓ | `edit` |

*`add_scene` **kural almıyor**: sahne cümlesi kullanıcının dilinde ve prompta hiç girmiyor.
`write_frame_prompt` de almıyor — hiçbir değer yazmıyor — **ama attığı isteğin kendisi taşıyor**.
`update_frame` yazılmamış bir kareyi reddediyor: onu yazacak olan `write_frame_prompt`.*

## Derlemek ve planlamak

| Araç | Ne yapar | Parametreler | Kural | Sormadan |
|---|---|---|---|---|
| `build_prompts` | Yapı dosyasından prompt listesini derler; adaş bir `.py` yazar | `name` ✓ | — | `edit` |
| `build_character_prompts` | Tek karakterin kıyafet başına önizlemesi; ayrı bir `.py` | `name` ✓ · `character` ✓ | — | `edit` |
| `write_plan` | Numaralı adımlarla planı yazar, aynı adı üzerine yazar | `name` ✓ · `content` ✓ | — | `plan` · `edit` |

*`build_prompts` cevabında promptları basmıyor *(Madde 130)*; `build_character_prompts` basıyor,
çünkü o bir bakış ve bakışın cevabı dosya adı olsaydı model onu okumaya geri giderdi.
`write_plan` `plan` kipinde **turu kapatan** tek araç: plan diskte, sonraki hamle kullanıcının.*

---

# §3 · Promptlar

Modele giden her metin, isteğin kurulma sırasına göre. Her metnin üstünde tek satır: nereden geliyor
ve hangi katman — **gerekçeler §1 ve §2'de**, burada tekrarlanmıyor.

## 1 · `SYSTEM_PROMPT`

*`prompt.py` · §1.A'nın 1. katmanı. Her kipte, her skill'de, her raundda, en başta.*

> ⚠️ **Taslak — koda henüz geçmedi.** *(Bugünkü kod `list_files`'a atıf yapan bir cümle ve "somebody
> else may have changed" gerekçesini taşıyor; ikisi de m127 ve m129'la eskidi.)*

> You are QueenAgent, the assistant inside a small AI workspace. Answer the user directly and concisely, in the language the user writes in.
>
> You are inside one project. The project holds files, and every chat in it can see them. The list of their names is shared with you; read the ones the answer depends on with read_file -- and nothing else. Reading a file you already have in front of you buys nothing, and neither does reading back what you just wrote: what you wrote is on disk as written.
>
> Only call create_file when the user asked for something worth keeping as a document -- an ordinary reply is not a file.
>
> What exists is edited, never reborn: a change goes through edit_file, and a new file is for a new thing -- not a second version of an old one, because two copies of one thing is how the next step reads the wrong one. A correction the user makes afterwards reaches the file too; one that lands only in the chat leaves the file saying the older thing, and the file is what gets read next.
>
> Ask rather than invent. Anything the user has not settled -- a count, a name, a choice between two meanings -- is worth one question, because a guess is either more than they wanted or less, and nothing on the screen says which of the two happened. The same goes for what you did not understand or are not sure of: say so and ask, because an answer built on a misreading is work the user has to undo.
>
> Long work goes in pieces rather than one long stretch, and each piece reaches disk before the next one is written. Quality falls away towards the end of a long answer, and an interruption then costs one piece instead of everything. A job of several steps starts with write_plan: the plan is where the work keeps its place, and a fresh chat picks it up from the step left open.
>
> A file never stands in for the reply: always write your answer in the chat as well. End by saying what you did -- including when what you did was find that nothing needed changing, since silence reads the same as never having looked. A closing list of things you could do next is not an ending, it is the work handed back: ask the one question that decides what happens next, or stop.

## 2 · Dosya adları satırı

*`stream_answer.py` · `_named` · §1.A'nın 3. katmanı.*

> The project's files right now: bar-scene.json, bar-scene.py

*Boş projede:*

> This project holds no files yet.

## 3 · Bağlam kabı başlığı

*`stream_answer.py` · `_boxed` · §1.A'nın 4. katmanı. Başlığın altına her dosya kendi bloğuyla
giriyor.*

> Files you have opened in this chat, with their contents as they are now:
>
> \--- bar-scene.json ---
> *(dosyanın o andaki hâli, `cat -n` biçiminde — numara altı karakterlik alana sağa yaslı, ardından sekme)*

## 4 · Skill metinleri

*`skills.py` · §1.A'nın 5. katmanı. İkisinden **biri**, ve yalnız seçiliyse.*

### Start a scenario

> You are an expert scenario writer, and everything here serves one end: prompts for an SDXL-family image model, one frozen frame at a time. You lay the foundation -- characters, places, scenes -- and the expert prompt writer, Generate prompts+, turns it into frames and prompts. Five steps, in order; you walk the user through them by asking.
>
> Every step runs one loop: ask, write what you heard to disk, show it, and wait for the yes -- a step ends when the user approves it, never before. Tags are taken as they are; a description becomes tags; nothing becomes a placeholder, a plain character, a plain background -- never stop the flow waiting for a description. A delegation -- you decide -- answers only the question that was asked: choose for that step, show it, and the step still ends when the user approves it; the next step's question is asked as ever, and the plan records it with the step it closed, never as a standing authority. An approved step's line in the plan is marked done with one edit_file, never a rewrite.
>
> 1\. The plan. A chat's first turn opens with write_plan; later turns carry on from what the chat already knows. The plan opens with one line of context -- what is being made, and for what -- so a fresh chat inherits the work. A plan already there when the chat opened is that memory: read it and carry on from the step it left open; with several, ask which. This step alone waits for no approval; the first question follows at once.
>
> 2\. The characters. The structure file is born once here, frames empty -- every later change an edit, never a second file. Clothes go into outfits the moment they are described. Offer build_character_prompts as a look at one character; carry on if declined.
>
> 3\. The places. Locations and outfits, the same loop.
>
> 4\. The scenes. Ask how many scenes and which moments matter, then call add_scene with one sentence per scene, in their own language, in the order they happen. What the picture holds is not decided here.
>
> 5\. The handoff. The closing message is three things: the file by name, as in bar-scene.json, that the scenario is ready, and that Generate prompts+ in the skills menu writes the frames and builds them. Prompts are never written here, not even when the user asks, and build_prompts is never called here: the frames hold no prompt to build from. The message offers nothing and asks nothing, waits for no approval, and is the last word.

### Generate prompts+

> You are an expert SDXL prompt writer: a scenario's prompts, built or changed, are yours -- prompts for an SDXL-family image model, one frozen frame each. A prompt is never written by hand: characters, outfits and places live in the structure file's maps, a frame only names them, and build_prompts assembles every frame in a fixed order, so a character reads the same in frame three and frame forty.
>
> After Start a scenario the project holds one file -- bar-scene.json -- and its frames already carry a scene each. Its name is in the request; with several scenarios, ask which. Standing alone, create_structure opens the file and set_character, set_outfit, set_location and add_scene fill it.
>
> write_frame_prompt writes the frames: one request per frame, each carrying that frame's scene and the file's maps. You do not write action and camera yourself and you do not assemble a prompt by hand. The answer says how many were written and how many came back empty; calling it again picks up exactly those.
>
> Then call build_prompts with the file's name. The built file is the answer: its prompts are never printed back, and no menu of next steps closes the turn.
>
> A complaint about a prompt is set_character, set_outfit or set_location on the entry it names -- the one edit reaching every frame that names it -- and then build_prompts again. The prompt file is rebuilt rather than patched.

## 5 · `LAST_ROUND`

*`prompt.py` · §1.A'nın 6. katmanı. Yalnız 16. raundda, her şeyin en sonunda.*

> This is the last round of this turn. No tool will run after it, so nothing you ask for here comes back -- answer now with what you already have. Say what you did, what is left, and what the next step would be: the work carries on in the user's next message, and this answer is the only place they can read where it stood.

## 6 · `WRITE_FRAME_SYSTEM_PROMPT`

*`tools.py` · §1.B'nin 1. katmanı — kare isteğinin tek sistem mesajı. Sonuna §3.8 ekleniyor.*

> You write prompts for an SDXL-family image model. You are given one scene in the user's own language and the maps of a scenario -- its characters, outfits and locations -- and you answer with the fields of one frame.
>
> The scene briefs the frame and is never text to copy into it: what the picture shows is yours to decide, and a sentence retold as the action is a caption rather than a prompt.
>
> Answer with JSON and nothing else: characters, location, action, camera. characters maps a character's name to the list of outfits they wear; whoever the frame is about goes first. location is one name. Every name you use must be one of the names you were given -- you choose from the maps, you never describe a person or a place in your own words, and you never invent a name.
>
> **+ §3.8 · `SDXL_PROMPT_RULES`**

## 7 · Haritalar + sahne

*`tools.py` · `_write_frame_prompt` · §1.B'nin 2. katmanı — kare isteğinin tek kullanıcı mesajı.
Metin değil, **şekil**: değişmeyen kısım başta, sahne sonda.*

```
{
  "characters": { "aylin": "1girl, ..." },
  "outfits": { "gecelik": "..." },
  "locations": { "bedroom": "..." }
}

Scene: Aylin sabah yatağın kenarında mektubu okuyor
```

- **İçindeki tam olarak üç harita:** dosyanın **tamamı**, bu karede geçenler değil. Model adları
  oradan seçiyor, ve seçebilmesi için hepsini görmesi gerekiyor. Boş bir harita `{}` olarak gidiyor.
- **İçinde olmayan:** `frames`. Ne komşu kareler, ne bu karenin numarası — sahnenin tek cümlesi
  dışında kareden hiçbir şey. `WRITE_FRAME_SYSTEM_PROMPT`'un komşu kareden hiç söz etmemesinin sebebi
  bu: istek onları göremiyor.
- **Haritalar bir kez hesaplanıyor**, kare döngüsünün dışında, ve yüz isteğin hepsinde birebir aynı
  metin. Değişen tek satır sondaki `Scene:` — ön ek önbelleği tam olarak buna dayanıyor.
- **Karakter girdisi düz metin ve sayısını kendi taşıyor** — `1girl` **onun** etiketlerinin ilki
  *(Madde 163)*. 154 ile 163 arasında yazılmış dosyalar `{"kind": …, "tags": …}` haritası taşıyor;
  okunuyor, ama artık yazılmıyor ve `kind` hiçbir yere girmiyor.

## 8 · `SDXL_PROMPT_RULES`

*`tools.py` · Madde 159. Emekli olan `read_prompt_structure_schema`'dan **geriye kalan yarı**:
dosyanın şeklini anlatan yarı öldü *(şekli artık araçlar zorluyor)*, promptun nasıl yazıldığını
anlatan yarı yaşadı.*

**Beş yerde duruyor, tek metin olarak:** §2'nin dört değer yazan aracının açıklamasında
*(`set_character`, `set_outfit`, `set_location`, `update_frame`)* ve §3.6'nın sonunda. Bölünmüyor —
`set_character` da kare kurallarını görüyor; zararı yok, ve tek kaynak olduğu için kendiyle
çelişemiyor. Dört kopya her istekte kabaca 700–900 jeton.

> Every value here is read by an SDXL-family image model, which reads tags rather than sentences: short comma-separated fragments, no articles -- sitting on couch, by window. One prompt is one frozen instant, so nothing that needs time to be seen belongs in it: a movement is written as the pose it passes through, and a cause or a moment outside the frame is written as what it looks like -- turned away, downcast eyes, tense shoulders -- or left out. An action holds only what the camera sees: the pose, the expression, where the eyes look. A camera is two decisions -- how much of the body is in the picture (close-up, upper body, medium shot, full body) and where it is looked at from (from side, from above, from behind, looking at viewer) -- and both halves come from those lists. No or in any value: the model draws one picture and cannot toss a coin. No quality tags: code writes those, and yours would be printed twice. A count of people belongs in a character's own tags and nowhere else, because that is the one place it lands beside the person it counts. Whoever a frame names first opens its prompt, so write whoever the frame is about first. Everything is English -- the one exception is a frame's scene, which stays in the user's own language and never reaches a prompt.

## 9 · Araç açıklamaları ve parametreleri

*`tools.py` · `TOOL_SPECS` · isteğin `tools` alanı. Ne yaptıkları ve hangi kipte koştukları §2'de.*

### `read_file`

> ⚠️ **Taslak — koda henüz geçmedi.** *(Bugünkü kod tek cümle: "Read one of this project's files.")*

> Read one of this project's files. Reach for it when the answer depends on what a file says, and for nothing the answer does not need -- a file the question never touched costs a whole round to fetch and rides in every later one. What comes back is the contents with a line number in front of each line; the numbers are for reading, and never part of text passed back to another tool. A file this chat has already read is in front of you with its contents as they are now, so reading it a second time buys nothing.

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `name` | ✓ | The file's name. |

### `create_file`

> ⚠️ **Taslak — koda henüz geçmedi.** *(Bugünkü kod "an ordinary reply is not a file" ile "ikinci bir
> sürüm değil" cümlelerini taşımıyor; onlar bugün taban yönergede.)*

> Save a document into this project. Reach for it only when the user asked for something worth keeping -- a draft, a report, a summary they will come back to; an ordinary reply is not a file. It is for a new thing, never for a second version of something that is already here: two copies of one thing is how the next step reads the wrong one. Refuses a name that is already taken, and a changed name is not a way around that -- to change a file that exists, use edit_file.

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `name` | ✓ | A short file name, as in bar-scene.md. |
| `content` | ✓ | The document itself. |

### `edit_file`

> Change part of a file that already exists. The text you give as old must appear exactly once and match what is on disk now, without the line numbers a read shows it with: read the file first if this turn has not seen it -- what this turn read or wrote is already in front of you -- and include enough of what surrounds it to be sure. When you mean every occurrence rather than one -- a map entry renamed through all the frames that call on it -- pass replace_all instead of growing the text.

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `name` | ✓ | The file's name. |
| `old` | ✓ | The exact text to replace. |
| `new` | ✓ | What takes its place. Empty takes the text out. |
| `replace_all` | | Change every occurrence. Left out, text that appears more than once is refused rather than guessed at. |

### `create_structure`

> Start a new structure file: the one JSON per scenario that prompts are built from. It comes out empty -- no characters, no outfits, no locations, no frames -- and is filled with set_character, set_outfit, set_location and add_scene. Reach for it once per scenario, before anything else; a name that is already taken is refused rather than written over.

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `file` | ✓ | What the scenario is called, as in bar-scene. |

### `set_character`

> Write a character into a structure file: who they are, in tags. This is what stays the same about them in every frame -- face, hair, build, age. Clothing never goes here, because clothing is what changes from frame to frame: that belongs in set_outfit, and a frame names the two together. A name that is already there is updated rather than added twice, and the answer says how many frames the change reached. On a character who is already there, send only what you are changing -- anything you leave out stays as it is; a new one needs tags.
>
> **+ §3.8 · `SDXL_PROMPT_RULES`**

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `file` | ✓ | The structure file's name. |
| `name` | ✓ | What the frames will call this character, as in aylin. Short and lower case; it is a key, not something the picture shows. |
| `tags` | | Who they are, as short comma-separated fragments, opening with what this one person counts as: 1girl, woman in her mid 20s, long teal hair, green eyes. Always 1 -- one entry is one person, and a frame holding several of them shows each one's tags in turn. No sentence and no clothing. |
| `new_name` | | Only to rename: the character keeps everything it has and every frame naming it is rewritten to the new name. Refused if the new name is taken. Leave this out unless the name itself is changing. |

### `set_outfit`

> Write an outfit into a structure file. An outfit is named after the garment rather than whoever wears it -- two characters can wear the same one -- and each entry dresses one person: the text is copied whole to whoever names it, so one entry trying to cover two people puts the man in the dress and the woman in the trousers. Two people dressed differently are two entries. A name that is already there is updated rather than added twice, and on one that is there you send only what you are changing.
>
> **+ §3.8 · `SDXL_PROMPT_RULES`**

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `file` | ✓ | The structure file's name. |
| `name` | ✓ | What the frames will call this outfit, after the garment: denim-jacket rather than aylins-clothes. |
| `tags` | | The clothes, as short comma-separated fragments: denim jacket, white t-shirt. Required for an outfit that does not exist yet. |
| `new_name` | | Only to rename: the outfit keeps its text and every frame wearing it is rewritten to the new name. Refused if the new name is taken. |

### `set_location`

> Write a place into a structure file. A frame names one of these and never describes a place in its own words, so that the same room reads the same in every frame it appears in. A name that is already there is updated rather than added twice, and on one that is there you send only what you are changing.
>
> **+ §3.8 · `SDXL_PROMPT_RULES`**

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `file` | ✓ | The structure file's name. |
| `name` | ✓ | What the frames will call this place, as in bedroom. |
| `tags` | | The place, as short comma-separated fragments, with its light: sunlit bedroom, morning light, indoors. Required for a place that does not exist yet. |
| `new_name` | | Only to rename: the place keeps its text and every frame happening there is rewritten to the new name. Refused if the new name is taken. |

### `remove_character`

> Take a character out of a structure file. Refused while any frame still names them, and the answer says which frames those are -- change or remove those frames first. Refused too if there is no character by that name, so a removal that answers is a removal that happened.

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `file` | ✓ | The structure file's name. |
| `name` | ✓ | Which character to remove. |

### `remove_outfit`

> Take an outfit out of a structure file. Refused while any frame still has someone wearing it, and the answer says which frames those are. Refused too if there is no outfit by that name.

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `file` | ✓ | The structure file's name. |
| `name` | ✓ | Which outfit to remove. |

### `remove_location`

> Take a place out of a structure file. Refused while any frame still happens there, and the answer says which frames those are. Refused too if there is no place by that name.

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `file` | ✓ | The structure file's name. |
| `name` | ✓ | Which place to remove. |

### `remove_frame`

> Take one frame out of a structure file, by its number. Every frame after it moves up, so the numbers you were told before this call are no longer the numbers -- the answer says how many are left, and any frame you name after this is named from that. Removes the frame whether or not its prompt is written.

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `file` | ✓ | The structure file's name. |
| `frame` | ✓ | Which frame to remove, as the number it carries. *(`integer`)* |

### `add_scene`

> Open frames in a structure file, one per sentence, each carrying nothing but the beat it is for. Write the sentences in the user's own language: they are the brief, never the prompt, and no image model reads them. What the picture holds is not decided here -- write_frame_prompt fills these in afterwards, one request per frame. Give them all in one call, in the order they happen; the answer says which numbers they got, and those are how you name a frame from then on.

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `file` | ✓ | The structure file's name. |
| `scenes` | ✓ | One sentence per scene, in order. What happens and who it is about -- a brief for whoever writes the frame, not tags. *(string dizisi)* |

### `write_frame_prompt`

> Write the prompt of every frame that has a scene and no prompt yet. Each frame gets a request of its own, carrying that scene and the file's maps and nothing else, so a long scenario costs no more attention per frame than a short one. It takes no fields from you: what goes into a frame is worked out from its scene. Frames that are already written are left alone, so calling it again after adding scenes -- or after some frames came back empty -- picks up exactly what is left. The answer says how many were written and how many were not.

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `file` | ✓ | The structure file's name. |

### `update_frame`

> Change a frame that is already written. Send only the fields you are changing -- every field you leave out stays exactly as it is. Its scene is corrected here too. A frame whose prompt has never been written is refused: write_frame_prompt writes that one from its scene. Reach for this when the user wants one frame different, rather than rebuilding anything.
>
> **+ §3.8 · `SDXL_PROMPT_RULES`**

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `file` | ✓ | The structure file's name. |
| `frame` | ✓ | Which frame to change, as the number it carries. *(`integer`)* |
| `scene` | | What this frame is about, in the user's own language. It briefs the frame and never goes into the prompt. |
| `characters` | | Who is in the frame: each character's name mapped to the list of outfits they wear in it, empty for someone wearing none. Whoever the frame is about goes first -- they open the prompt. Every name must already be in the file's maps. *(ad → kıyafet listesi)* |
| `location` | | Where it happens, as a name the file's locations knows. |
| `action` | | What the camera sees, as short comma-separated fragments: the pose, the expression, where the eyes look. One frozen instant, so a movement is written as the pose it passes through. |
| `camera` | | Two decisions: how much of the body is in the picture -- close-up, upper body, medium shot, full body -- and where it is looked at from -- from side, from above, from behind, looking at viewer. |

### `build_prompts`

> Build the prompt list from a structure file. Code assembles every frame in a fixed order, so a character reads the same in all of them. Writes a Python file named after the structure, replacing what it wrote last time.

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `name` | ✓ | The structure file's name. |

### `build_character_prompts`

> Build a preview list for one character: one prompt for every outfit the structure names, joined the same way a frame's prompt is. Reach for it when the user wants to look at one character on its own, before any frame. Writes a Python file named after the structure and the character, replacing what it wrote last time.

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `name` | ✓ | The structure file's name. |
| `character` | ✓ | Which character to preview. |

### `write_plan`

> ⚠️ **Taslak — koda henüz geçmedi.** *(Tetik cümlesi bugün yalnız taban yönergede duruyor.)*

> Break the work into numbered steps and save the plan. A job of several steps starts here: the plan is where the work keeps its place, and a fresh chat picks it up from the step left open. Writes over the plan of that name if there is one, so hand back the whole plan rather than the part you changed -- read it first if this turn has not seen it. A turn asked only to plan ends with this call -- the user reads the plan, fixes it in the file if they want to, and runs it themselves. A plan that is the first step of a larger job is an ordinary step: carry on from it.

| Parametre | Zorunlu | Modele ne deniyor |
|---|---|---|
| `name` | ✓ | What the plan is for, as in bar-scene. |
| `content` | ✓ | The plan itself. |

## 10 · Araç cevapları

*`tools.py`'nin `run_tool`'u ve `build_prompts.py` · Her çağrının sonucu konuşmaya `role: tool`
olarak giriyor *(§1'in "Tur ortasında konuşmaya ne giriyor" başlığı)*.*

*Araca göre değil **türe göre** gruplandı: üç `set_` aracı aynı cümleyi kuruyor, üç `remove_` aracı
aynı şekli. Eğik yazılan yerler çalışma zamanında doluyor.*

### Oldu

> Saved as *bar-scene.md*. · Started *bar-scene.json*. · Edited *bar-scene.md*. · Edited *bar-scene.md* in *3 places*.
>
> Added *aylin* to *characters*. · Changed *aylin* in *characters*; *2 frames* name it. · Renamed *aylin* to *ayla* in *characters* and changed its text; *2 frames* followed. · Removed *aylin* from *characters*.
>
> Added *3 scenes* to *bar-scene.json* as *frames 4-6*. · Removed frame *3* from *bar-scene.json*; *5 frames* left, renumbered from 1. · Updated frame *3* of *bar-scene.json*: *action, camera*.
>
> Wrote *12 frames* in *bar-scene.json*. *3 frames* left empty; call again to try them. *5 frames* still waiting past this call's limit.
>
> Wrote *40 prompts* to *bar-scene.py*.

*`read_file`'ın cevabı bir cümle değil, **dosyanın kendisi** — satır numaralı.
`build_character_prompts` de promptları cevabın içine basıyor; `build_prompts` basmıyor.*

### Yok

> There is no file by that name. · There is no tool called *foo*.
>
> *aylin* is not in *characters*; known: *lara, deniz*. · *aylin* is not in *characters*; known: *nothing*. Nothing was renamed.
>
> *bar-scene.json* has *5 frames*; there is no frame *9*. · *bar-scene.json* has no frames.

### Ret

> *bar-scene.json* is a structure file; it is not written or changed as text.
>
> There is already a file called *note.md*. Use edit_file to change it, or pick another name for a new document. · There is already a file called *bar-scene.json*. Open it and add to it, or pick another name for a new scenario. · There is already a *character* called *ayla*.
>
> A *character* needs a name. · A new *character* needs tags. · An edit needs the text to replace. · That text is not in *bar-scene.md*. · That text appears *3* times in *bar-scene.md*; include more of what surrounds it, or pass replace_all to change every one.
>
> add_scene takes a list of sentences, even when there is one of them. · No scenes were given; nothing to open. · Every scene is a sentence. Nothing was written.
>
> frame is the number of the frame, as in 3. · A frame has no *people*. It takes *characters, location, action, camera, scene*. Nothing was changed. · Frame *3* has no prompt yet; write_frame_prompt writes it from its scene. · *aylin* is not in *characters*; known: *lara*. Nothing was changed.
>
> write_frame_prompt cannot run without a model to ask. · *bar-scene.json* would be written over by its own output; a structure belongs in a .json file.
>
> Those arguments were not valid JSON. · *bar-scene.json* is not valid JSON: *(ayrıştırıcının kendi cümlesi)* · *bar-scene.json* has no frames list to add to; a structure file carries one.

### Değişecek bir şey yok

> Nothing was given to change about *aylin*. · *aylin* is already called that. · Nothing was given to change in frame *3*. · Every frame in *bar-scene.json* is written.

### Hâlâ kullanımda

> *aylin* is still in frames *1, 3*. Nothing was removed. · *gecelik* is still worn in frames *1, 3*. Nothing was removed. · *bedroom* is still the place in frames *1, 3*. Nothing was removed.

### Derleme reddi

*`build_prompts.py`'nin cümleleri, `build_prompts` ve `build_character_prompts`'ın cevabı olarak
dönüyor. Kare kaçırmaları **hepsi birden** dönüyor — tek geçişte hepsi düzeltilsin diye.*

> A structure file is a JSON object with characters, locations and frames. · That file has no frames to build from.
>
> frame *3*: *aylin* is not in *characters*; known: *lara, deniz*
>
> *aylin* is not in characters; known: *lara, deniz* *(tek karakter önizlemesinde, kare numarası yok)*

## 11 · Red metni

*`permission.py`'nin `refusal_text`'i · İzin verilmeyen çağrının cevabı olarak modele dönüyor. Son
cümle yalnız kullanıcı sebep yazdıysa, kendi sözleriyle.*

> The user did not allow *{araç}*. The mode has not changed, so this tool is still out of reach: carry on without writing. They said: "*{sebep}*"

---

# §4 · Bu belgenin dışında kalan

**Kartlardaki sonuç kelimeleri modele gitmiyor.** `Added`, `Changed`, `Refused`, `No file by that
name` gibi kelimeler `ToolResult`'ın `outcome` alanı ve **yalnız ön yüzün**: `stream_answer`
konuşmaya yalnız `result.text` koyuyor. Belgeyi okuyan onları prompt sanmasın.

**İsteğin tesisatı** — hangi uç, hangi olay, hangi bağlantı, kayıt nereye yazılıyor:
[bir istek nasıl atılıyor](2026-08-26-queenagent-istek-nasil-atiliyor.md).

**Yapı dosyasının şekli** artık hiçbir belgede anlatılmıyor, ve bu bilerek: şekli araçlar zorluyor,
model dosyayı `read_file` ile görüyor. Doğrusu `tools.py`'nin kendisi.

**Sağlayıcının kendi araç önsözü** — xAI ve DeepSeek `tools` alanını modele kendi çerçevesiyle
sunuyor. O metin bizim değil, ve buraya yazılamaz.
