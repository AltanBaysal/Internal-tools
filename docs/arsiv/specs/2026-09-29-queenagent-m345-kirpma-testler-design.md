# Madde 345 — Sohbet baştan kırpılabilir · test turu

**Kaynak:** [yol haritasının 345'i](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md) — v9-1b;
kararları *v9-1 — Sohbet sınırı*: 28 Eylül'ün *aynı sohbette devam*'ı, ve 29 Eylül'ün notları
(`Continue here` onay istemez ve geri alınmaz; kırpılmış sohbet yeniden dolunca bildirim yine çıkar;
kırpmadan sonra çember modele hâlâ gideni okur). Tasarım: queen-design `queen-agent-v3`,
`BEHAVIOUR.md`'nin *Full chat* ve *Trimmed chat* bölümleri, `data.js`'in `trimOf`'u.

**Kullanıcıdan gereken:** hiçbir şey. Aşağıdaki kararlar teknik; davranış yol haritasında ve
tasarımda yazılı.

## Bugün

Sohbetin ölçüsü açık satırdaki bütün mesajların metni (`chat_size`, Madde 337), ve modele de açık
satırın bütün mesajları gidiyor (`_conversation`). Dolan sohbetin tek yolu yeni sohbet; aynı
sohbette sürmenin yolu yok.

## Olacak

**Sunucu bir sohbeti baştan kırpabilir.** Kırpılmış bir sohbette en eski mesajlar modele gitmez ve
ölçüye girmez; diskte ve ekranda kalır. Özet yok. Düğme (`Continue here`) v9-1c'nin, çizgi v9-1d'nin;
bu madde onlara iki şey bırakır: kırpmayı isteyecekleri bir kapı, ve kırpılan kısmın nerede bittiğini
söyleyen bir alan.

**Kırpma kuralı** — tasarımın `trimOf`'u, sunucunun ölçüsüyle:

- **Bütün turlar düşer:** kesim yalnız bir sorunun önüne düşer, soruyla cevabının arasına hiç.
  Modele giden konuşma bir soruyla başlar.
- **Baştan, kalan 10.000'i geçmeyene kadar:** kesim, ondan sonrası 10.000'i geçmeyen ilk sorudadır.
  Ölçü 337'ninki (harf × 3 ÷ 10).
- **Son tur ne kadar ağırsa kalır:** hiçbir kesim 10.000'e indiremiyorsa kesim son sorudadır; sohbet
  hiçbir zaman boş gönderilmez.

**Kırpma yalnız dolu sohbette.** Dolmamış sohbetin kırpılması reddedilir: seçenek yalnız sohbet
dolunca var *(kullanıcı kararı, 28 Eylül)*, ve kural sunucuda (FOUNDATION, Karar 4). Onay istemez,
geri alınmaz *(29 Eylül)*.

**Kırpılmış sohbet yeniden dolabilir:** ölçü kesimden sonrasını sayar, sohbet büyüdükçe o da büyür;
50.000'e gelince sohbet yine doludur, ve yine kırpılabilir. Yeni kesim öncekinin ilerisindedir.

**Kesim nerede tutulur — kırpıldığı anda satırın son mesajında.** Üç yol vardı:

1. **Satırın son mesajı, kesimin sayısını taşır** — seçilen. `Message.trimmed`: bu mesaj yazıldığında
   satırın baştan kaç mesajı modele gitmez oldu. Satırın kesimi, o satırdaki kesim taşıyan son
   mesajınki. Tasarımın işaretiyle aynı yerde — `Continue here`'in işaretlediği, sohbeti dolduran
   cevap — ve sürümlerle kendiliğinden doğru davranır: o mesajdan sonra açılan bir sürüm onu önünde
   taşır ve kırpılmış kalır; o mesajdan önce kesilen bir sürüm onu taşımaz ve kırpılmamıştır, çünkü
   hiç dolmadı *(tasarım, BEHAVIOUR.md: "Where that line stops short of the answer Continue here
   marked, nothing on it is trimmed, since it never filled")*. Kesim bir kez, kırpıldığı anda
   hesaplanır ve yazılır; okunurken yeniden hesaplanmaz.
2. **Sohbetin kökünde bir sayı** — sürümler ayrı satırlar; bir sayı hangisinin olduğunu bilemez, ve
   her sürüme miras kuralı gerekir.
3. **Kendi dosyası** (`chats/<id>.trim` gibi) — sohbetin silinişi, çöpü ve sürümleri ikinci bir dosyayı
   da taşımak zorunda kalır. CODE-STANDARD'ın sorusu: `chats/<id>.json` *bu konuşmada ne söylendi ve
   neyle cevap veriyor* diye cevaplıyor; modelin konuşmayı nereden okuduğu o sorunun parçası.
   Tablonun *Written when* sütununa *Continue here* eklenir, uygulama turunda.

**Kapı:** `POST /api/projects/<p>/chats/<c>/trim`. Dolu sohbette açık satırı kırpar ve `{}` döner —
tarayıcı sohbeti yine `get_chat`'ten okur, `version` kapısı gibi. Dolmamış sohbet `400`
`{"error": "this chat is not full"}`; olmayan sohbet `404` `{"error": "chat not found"}`.

**Kayıt:** `/chats/<id>` her zaman `trimmed` taşır — açık satırın baştan kaç mesajı modele gitmez;
kırpılmamış sohbette 0. Tasarımdaki adla. `messages` bütün satırı vermeye devam eder, `context.sent`
yalnız gideni ölçer.

**Diskte:** mesajın `"trimmed": N`'i yalnız sıfır değilse yazılır — öteki alanların kuralı; eski
sohbetler göç istemeden 0 okunur.

## Testler ne tutar

**`test_chat.py`** — alanın kuralı:

| # | Ne |
|---|---|
| 1 | Kırpılmamış sohbet açık satırının hepsini gönderir: `sent_from` 0, `sent_messages` satırın kendisi |
| 2 | Kesim taşıyan mesaj, satırın baştan o kadar mesajını göndermez; ölçü yalnız kalanı sayar |
| 3 | Satırda iki kesim varsa sonuncusu geçer |
| 4 | Kesimi taşıyan mesajdan önce ayrılan sürüm kırpılmamıştır; o mesajdan sonra ayrılan kırpılmış kalır |
| 5 | Kırpılmış sohbet yeniden 50.000'e gelince yine doludur |
| 6 | `TRIM_KEEPS` 10.000 |
| 7 | `trim_point`: bütün turlar baştan düşer, kalan 10.000'i geçmeyene kadar — on yedi 3.000'lik turda kesim 28'de, kalan 9.000 |
| 8 | `trim_point`: kesim cevabın önüne düşmez; son tur 10.000'den ağırsa kesim son sorudadır |

**`test_chats_api.py`** — kapı ve kayıt:

| # | Ne |
|---|---|
| 9 | Dolu sohbet kırpılır: kapı `200 {}`; kayıtta `trimmed` 16, bütün mesajlar duruyor, `context.sent` 10.000'in altında |
| 10 | Kırpılmış sohbet yeniden tur alır: yeni cümle kabul edilir ve cevaplanır |
| 11 | Dolmamış sohbet kırpılmaz: `400 {"error": "this chat is not full"}`, kayıt değişmez |
| 12 | Olmayan sohbet: `404 {"error": "chat not found"}` |
| 13 | Kırpılmamış sohbetin kaydı `trimmed: 0` taşır |

**`test_stream_answer.py`:**

| # | Ne |
|---|---|
| 14 | Kırpılmış sohbette modele yalnız kesimden sonraki mesajlar gider |

**`test_file_chat_store.py`:**

| # | Ne |
|---|---|
| 15 | Mesajın kesimi diske gidip gelir, `"trimmed": N` olarak yazılır |
| 16 | Kesim taşımayan mesaj alanı yazmaz; alan olmadan yazılmış mesaj 0 okunur |

## Tutmaz

- **Düğmeyi ve çizgiyi:** v9-1c ve v9-1d'nin. Ön uca dokunulmaz.
- **Açılan dosyalar kutusunu:** kutu mesaj değil (337), ve kırpma onu değiştirmez.

## Nasıl görülür

CLAUDE.md'deki dört satır. `python -m pytest queen-agent -q` yeni testlerde kırmızı verir; öteki üç
satır yeşil kalır. Kırmızı hâliyle commit edilir.

Adım adım dökümü [test turunun planında](../plans/2026-09-29-queenagent-m345-kirpma-testler-plan.md).
