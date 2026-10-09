# Madde 339 — Proje sabitlenir ve arşivlenir, sunucu · test turu

**Kaynak:** [yol haritasının 339'u (v9-2b)](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md); kararları
v9-2'de, tasarımı queen-design'ın `queen-agent-v3` dalında 135 ve 167.

**Kullanıcıdan gereken:** hiçbir şey. Madde yalnız sunucuya dokunuyor; ekranı v9-2q (menü) ve v9-2t
(arşiv) kuracak.

## Ne kanıtlanacak

Sunucu bir projeyi sabitliyor, bırakıyor, arşive alıyor ve geri getiriyor; proje listesi her
projenin sabitli ve arşivde olup olmadığını söylüyor; ve ikisi de uygulama yeniden açılınca kalıyor.

## Nerede saklanır — kural ne diyor

CODE-STANDARD'ın tablosuna göre `project.json` yalnız *proje ne adında ve ne zamandan beri* sorusunu
cevaplar, ve oluşturulunca ya da yeniden adlandırılınca yazılır. Sabitli mi, arşivde mi başka iki
soru, ve başka anlarda yazılıyor: biri Pin'e basınca, öteki Archive'a basınca. Kural, yeni bir soru
için yeni bir dosya ister. Üç yol düşünüldü:

1. **`project.json`'a iki alan** — kural bunu açıkça yasaklıyor: dosya başka bir anda, başka bir soru
   için yeniden yazılır.
2. **İkisi için tek bir dosya** (`shelf.json` gibi) — yine iki soru, iki ayrı anda yazılan tek dosya.
3. **Her soru için bir işaret dosyası (seçilen):** projenin klasöründe `pinned` ve `archived`. Dosya
   varsa cevap evet, yoksa hayır; içi boş. Sabitlemek dosyayı yazar, bırakmak siler; arşiv de öyle.
   Dosya listesi zaten böyle çalışıyor: cevap klasörün kendisi, ve an dosyanın mtime'ı. `pinned`'ın
   mtime'ı projenin ne zamandan beri sabitli olduğunu söyler — v9-2j'ye ya da v9-2t'ye sabitlenenlerin
   sırası gerekirse, cevap diskte hazır, ve bu madde onu listeye koymaz.

İki soru birbirinden bağımsız: **arşiv sabitlemeye dokunmaz.** Arşivlenen sabitli proje sabitli
kalır, ve arşivden dönünce sabitlenenlerin arasındaki eski yerinde durur — tasarımın *Undo*'sunun
istediği de bu *(BEHAVIOUR.md, All projects)*. Arşivden dönen projenin sabitlemesini bırakıp
bırakmamak v9-2t'nin kararı; sunucu ikisini de yapabiliyor.

Aynı cevabı ikinci kez istemek bir şey değiştirmez: sabitli projeyi yeniden sabitlemek `pinned`'ı
yeniden yazmaz, yani sabitlendiği an kaymaz; sabitli olmayanı bırakmak hata vermez.

## Kapı

Yeni bir adres yok. Proje zaten `PATCH /api/projects/<id>` ile düzenleniyor, ve o kapı "gönderilmeyen
aynı kalır" diye çalışıyor: gövdeye `pinned` ya da `archived` (`true`/`false`) gelir. Ön uçta
`useProjects`'in `editProject(id, changes)`'i v9-2q ve v9-2t için yeterli; cevap düzenlenmiş satır.

Proje JSON'ı iki alan kazanır, her yerde — liste, oluşturma, düzenleme: `"pinned"` ve `"archived"`,
ikisi de her zaman var. **Arşivdeki proje listeden çıkmaz**: satır arşivde olduğunu söyler, hangi
sekmede görüneceğine ekran karar verir. Liste sırası bu maddede değişmez; sırayı v9-2j kuruyor, ve
aynı listenin cevabına yazacak.

## Testler ne tutar

**Yeni dosya `queen-agent/backend/tests/test_pin_archive.py`:**

| # | Katman | Ne |
|---|---|---|
| 1 | depo | Yeni proje ne sabitli ne arşivde |
| 2 | depo | Sabitlemek yeni bir depo örneğinde de duruyor; bırakınca gidiyor |
| 3 | depo | Arşiv yeni bir depo örneğinde de duruyor; geri getirince gidiyor |
| 4 | depo | Her cevap kendi dosyası: `pinned` ve `archived` klasörde beliriyor ve siliniyor |
| 5 | depo | Sabitleyip arşivlemek `project.json`'a dokunmuyor — metni aynı |
| 6 | depo | İkinci kez sabitlemek `pinned`'ın anını değiştirmiyor; sabitli olmayanı bırakmak hata vermiyor |
| 7 | depo | Arşiv sabitlemeye dokunmuyor |
| 8 | use case | Yalnız `pinned`/`archived` gelince `project.json` yeniden yazılmıyor (sahte port, `replace` çağrılmıyor) |
| 9 | use case | Bilinmeyen proje sabitlenemiyor: `ProjectNotFound` |
| 10 | API | `PATCH` sabitliyor ve bırakıyor; cevap satırı söylüyor |
| 11 | API | `PATCH` arşive alıyor ve geri getiriyor; arşivdeki proje listede, `archived: true` ile |
| 12 | API | Liste her projenin ikisini de söylüyor, ve yeni bir uygulamada da aynı |
| 13 | belge | CODE-STANDARD'ın tablosunda `pinned` ve `archived` satırları var |

Bilinmeyen proje için API'de ayrı bir test yok: kapı bugün de 404 veriyor, yani böyle bir test
kırmızı turda da yeşil kalır ve bir şey kanıtlamaz; kuralı 9 tutuyor.

**Değişen test:** `test_projects_api.py`'deki `test_the_answer_carries_neither_a_description_nor_a_colour`
satırın alan kümesini tutuyor; küme `pinned` ve `archived`'la genişler. Testin asıl söylediği —
açıklama ve renk yok — aynı kalır.

Depo testleri gerçek `Store`'la `tmp_path`'te; use case testleri CODE-STANDARD'ın dediği gibi sahte
portla. Dosya adları testte düz yazılır (`"pinned"`, `"archived"`): testin tuttuğu şey diskteki biçim,
ve kırmızı turda henüz olmayan bir sabiti içe aktarmak dosyanın bütün testlerini toplanamaz yapardı.

## Tutmadıkları

- **Sıra ve son kullanım** — v9-2j.
- **Ekran** — v9-2q ve v9-2t; ön uç bu maddede değişmez, `dist` derlenmez.
- **Değerin biçimi:** `true`/`false` dışında bir değer için ayrı bir ret yazılmıyor; kapıyı yalnız bizim
  ön ucumuz çağırıyor, ve o boolean gönderiyor.

## Nasıl görülür

CLAUDE.md'deki dört satır. `python -m pytest queen-agent -q` yeni dosyanın testlerinde ve değişen
testte kırmızı verir; queen-editor'ün arka ucu 377'nin bilinen iki kırmızısıyla kalır; iki ön uç
yeşil. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m339-sabitle-arsivle-testler-plan.md).
