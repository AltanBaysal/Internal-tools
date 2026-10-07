# Madde 346 — Projenin son kullanıldığı an, ve listenin sırası, sunucu · test turu

**Kaynak:** [yol haritasının 346'sı (v9-2j)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); kararları
v9-2'de, tasarımı queen-design'ın `queen-agent-v3` dalında 135 ve 167. 339'un üstüne kurulur
([339'un test spec'i](2026-09-29-queenagent-m339-sabitle-arsivle-testler-design.md)): proje `pinned`
ve `archived` dosyalarını taşıyor, ve liste ikisini söylüyor.

**Kullanıcıdan gereken:** hiçbir şey. Madde yalnız sunucuya dokunuyor; `2h ago`'yu All projects
(v9-2n) yazacak.

## Ne kanıtlanacak

Sunucunun proje listesi her projenin son kullanıldığı anı veriyor; önce sabitlenenler, sonra en son
kullanılan; ve bir projede sohbet edilince o an yenileniyor.

## "Kullanıldı" ne demek — kural ne diyor

Maddenin mimari notu bağlayıcı: an saklanmaz, sohbetlerden okunur. CODE-STANDARD'a göre hiçbir dosya
ötekinin cevabını tekrarlamaz, ve dosya listesinin `2h ago`'su zaten dosyanın mtime'ı. Üç yol
düşünüldü:

1. **`project.json`'a ya da ayrı bir dosyaya bir an yazmak** — madde bunu açıkça yasaklıyor: sohbet
   dosyası o anı zaten söylüyor, ikinci kopya eskir.
2. **Sohbetlerin içindeki son mesajın anı** (`Chat.last_activity`) — doğru bir cevap, ama sohbetin
   şemasını bilen tek yer `FileChatStore`; projenin deposu onu okuyamaz. An use case'te, sohbet
   deposundan hesaplanmalıydı — ve o zaman oluşturma ve düzenleme kapılarının cevabı da sohbet deposunu
   istemeye başlar, yoksa aynı satır listede bir, `PATCH`'in cevabında başka söyler. Her projenin her
   sohbeti her listelemede JSON olarak okunur.
3. **Sohbet dosyalarının en yenisinin mtime'ı (seçilen).** Sohbet dosyası tam da sohbet edilince
   yazılıyor: kullanıcının mesajı cevaptan önce diske yazılıyor, cevap bitince yeniden; yeni bir sürüme
   geçmek de onu yeniden yazıyor. Yani "bu projede en son ne zaman sohbet edildi" sorusunun cevabı
   `chats/` klasöründe hazır, dosya listesinin kendi `2h ago`'suyla aynı yoldan. Projenin deposu
   sohbetleri zaten sayıyor; yalnız mtime'larına bakar, şemaya dokunmaz. Proje satırını kuran tek yer
   o olduğu için liste, oluşturma ve düzenleme aynı cevabı verir.

**Sohbeti olmayan proje** oluşturulduğu anda kullanılmış sayılır: `createdAt`. Tasarımın `data.js`'i
de böyle sayıyor (`lastActivityOf`: son mesaj, yoksa projenin doğuşu), ve yeni açılan bir proje en
son kullanılanlar arasında en üstte durur — kullanıcı onu az önce açtı.

## Sıra

Bir kural, o yüzden sunucunun *(FOUNDATION, Karar 4)*; bugünkü `list_projects` en eskiyi öne alıyor, ve
bu kural onun yerini alır.

- **Önce sabitlenenler, sabitlendikleri sırayla** — ilk sabitlenen en üstte. Maddenin satırı
  sabitlenenlerin kendi aralarındaki sırayı söylemiyor; tasarım söylüyor: `data.js`'in
  `allProjects`'i *"Pinned (in the order they were pinned)"*, ve BEHAVIOUR.md'nin *Undo*'su
  *"pinned by its old order"*. 339 bunun için `pinned`'ın mtime'ını sabitlendiği an bıraktı ve ikinci
  sabitlemede kaydırmıyor; an diskte hazır.
- **Sonra ötekiler, en son kullanılan en üstte.**
- Eşitlikte id — sıra hiç sallanmasın, `list_chats` gibi.
- **Arşivdeki proje listede kalır ve aynı kurala uyar** (339): hangi sekmede görüneceğine ekran karar
  verir.

## Kapı

Yeni adres yok. Proje JSON'ı bir alan kazanır, her yerde — liste, oluşturma, düzenleme:
`"lastActivity"`, ISO 8601, sohbetin satırındaki `lastActivity` ile aynı adda ve biçimde. Sabitlendiği
an JSON'a çıkmaz: sırayı sunucu veriyor, ekranın ona ihtiyacı yok.

## Testler ne tutar

**Yeni dosya `queen-agent/backend/tests/test_last_activity.py`:**

| # | Katman | Ne |
|---|---|---|
| 1 | alan | `Project`'in son kullanımı sohbeti yoksa doğduğu an, varsa en son yazılan sohbetin anı |
| 2 | depo | Sohbeti olmayan projenin son kullanımı `createdAt` |
| 3 | depo | Sohbeti olan projenin son kullanımı en yeni sohbet dosyasının mtime'ı, ISO olarak; ve an saklanmıyor: okunduktan sonra projenin klasöründe `chats` ve `project.json` dışında bir şey yok, `project.json` aynı |
| 4 | depo | Sabitlenen projenin sabitlendiği an `pinned`'ın mtime'ı; sabitli olmayanın boş |
| 5 | use case | Sabitlenenler önde sabitlendikleri sırayla, sonra en son kullanılan; sohbeti olmayan doğduğu anla sıraya girer. Id'ler ve doğuş anları sırayı açıklamayacak şekilde seçilir |
| 6 | API | Liste her projenin `lastActivity`'sini söylüyor; yeni projede `createdAt`'e eşit |
| 7 | API | Bir projede sohbet edilince anı yenileniyor ve liste onu öne alıyor |
| 8 | API | Sabitlenen proje, sabitli olmayan daha yenilerin önüne geçiyor |

"An saklanmıyor" 3'ün içinde, ayrı bir test değil: tek başına kırmızı turda da yeşil kalırdı, ve bir şey
kanıtlamazdı.

Depo testleri gerçek `Store`'la `tmp_path`'te, anlar `os.utime`'la elle konur — saat beklenmez. Use
case testi CODE-STANDARD'ın dediği gibi sahte portla. API testinde iki proje depoya geçmişte bir
`createdAt`'le yazılır (2000 yılı): böylece sohbetin mtime'ı ile öteki projenin doğuşu aynı
milisaniyeye düşüp sıra şansa kalmaz.

`Project`'in yeni alanları: `last_chat_at` (en yeni sohbet dosyasının anı, sohbet yoksa boş) ve
`pinned_at` (sabitlendiği an, sabitli değilse boş). `last_activity` ve `pinned` bunlardan okunur; bir
cevabın iki kopyası olmasın diye `pinned` artık alan değil.

**Değişen testler:**

- `test_project_usecases.py`'deki `test_projects_come_back_oldest_first` silinir: tuttuğu kural bu
  maddeyle kalkıyor, yerini 5 alıyor.
- `test_projects_api.py`'deki `test_the_answer_carries_neither_a_description_nor_a_colour` satırın
  alan kümesini tutuyor; küme `lastActivity`'yle genişler. Asıl söylediği aynı kalır.

## Tutmadıkları

- **Ekran** — `2h ago`'yu yazmak v9-2n'nin; ön uç bu maddede değişmez, `dist` derlenmez.
- **Sohbetin kendi `lastActivity`'si** değişmiyor; `list_chats` aynı.
- **Sabitlendiği anın JSON'a çıkması** — gerekmiyor, yukarıda.

## Nasıl görülür

CLAUDE.md'deki dört satır. `python -m pytest queen-agent -q` yeni dosyanın testlerinde ve değişen
testte kırmızı verir; queen-editor'ün iki süiti ve queen-agent'ın ön ucu yeşil kalır. Kırmızı hâliyle
commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m346-son-kullanim-sira-testler-plan.md).
