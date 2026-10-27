# Madde 500 · Eski belgeler ve roadmap'ler arşive — tasarım

**Tarih:** 27 Ekim 2026 · **Madde:** [v11 yol haritası](../roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-5),
500 · v11-5 · **Dal:** `feat/queen-editor-v11`

## Ne ve neden

Kullanıcı, 26 Ekim — "ee bu belgeyi arayacak claude code böyle yaparsan queen editor roadmapine
eklemeyi ve düzeltemeyi belgleri ve eski roadmpaleri arşive almayı". `4403108a` `docs/` kökündeki on
çalışma notunu sildi ve onlara giden linkleri düz yazıya çevirdi; okuyan, o belgeyi arar ve bulamaz.
Bu madde notları geri getirir, biten her şeyi tek bir arşive taşır ve her linki yeni yere göre
düzeltir. Yalnız belgeler değişir; kod ve testler değişmez.

## Kurallar (roadmap'ten)

- Tek arşiv: `docs/arsiv/`, içinde `roadmaps/`, `specs/`, `plans/`, `research/`, `design-needs/`,
  `notlar/`. Arşivin içi `docs/`'un düzenini aynen tekrarlar, bu yüzden iki arşiv belgesi arasındaki
  göreli link (`../roadmaps/…` bir spec'ten) değişmez; değişen, arşivle dışarısı arasındaki linkler.
- "Biten": açık iki roadmap — Queen Editor v11 ve QueenAgent v12 — dışındaki her roadmap, ve onların
  işlerinin belgeleri *(Claude'un kararı, kullanıcı 27 Ekim — "sen karar ver")*.

## Ne kalır, ne gider

**Kalan** — `docs/roadmaps/`: açık iki roadmap. `docs/specs/` ve `docs/plans/`: bu koşunun işleri,
496–501 (bugün 496–500'ün belgeleri var; QueenAgent v12'nin henüz spec'i yok). `docs/research/` ve
`docs/design-needs/`: hiçbir şey; git boş klasör tutmadığı için klasörler de kalkar, bir sonraki
belge onları yeniden açar. 482'nin Qwen araştırması da gider: bitmiş v10'un belgesi, ve açık 499'un
spec'inin linklediği öteki v10 belgeleri gibi arşivden okunur (reviewer, 27 Ekim).

**Arşive giden** — öteki her şey: 20 roadmap, 960 spec, 878 plan, 23 research dosyası
(`2026-08-14-mira-ara/` klasörü ve bir `.json` örneği dahil), 2 design-needs belgesi. Taşıma
`git mv`'yle yapılır, git yeniden adlandırma görür.

**Geri gelen on not** — `git show 4403108a^:<yol>` ile `docs/arsiv/notlar/`'a: arayüz brifi, AI yolu
haritası, istek nasıl atılıyor, akış tasarımı, skill kararları (karar defteri), skill problemleri,
promptlar, metin düzeltmeleri, modele giden metinler, v8 test listesi. `4403108a`'nın düz yazıya
çevirdiği 31 link (20 belgede) aynı commit'in tersiyle geri gelir, sonra yeni yere göre düzeltilir.

## Bir roadmap'e bağlanamayan belgeler

Bir belge, roadmap'i ona link veriyorsa ya da adındaki `m<numara>` o aracın bir roadmap'inin
maddesiyse o roadmap'indir; bir plan da spec'ine bağlıdır. Böyle bağlanamayan 389 belge var. Hepsi
24 Ekim'den önce yazıldı ve açık hiçbir iş onları kullanmıyor; bu yüzden **kararım: hepsi arşive.**
Bugünkü kural ("biten" = açık iki roadmap'in dışı) onları zaten kapsıyor; liste yalnız ne olduklarını
gösterir.

| Aile | Sayı | Ne |
|---|---|---|
| `2026-07-17…24` — `wan22-*`, `t2v-*`, `nova-3dcg-*`, `arbuzai-*` | 22 | Roadmap'lerden önceki collab-toolbox defterleri |
| `queen-editor-b1…b5`, `-bagimsizlik`, `-bolum6…14` | 19 | Queen Editor v1'in "Bölüm"leri; roadmap'in tablosu bölüm adıyla sayıyor, link vermiyor |
| `queen-editor-v4-madde-*` | 4 | Queen Editor v2'nin maddeleri, eski adlandırma |
| `queen-editor-v5…v14-gorev-*`, `-v14-colab-turu` | 247 | Ortak numaradan önceki görev listeleri |
| `queen-editor-hata-karti`, `-kapanmis-yuva`, `-rapor-yenilemeyi-asmasin` | 12 | Aynı dönemin (14 Ağustos) düzeltmeleri |
| `mira-faz-*` (15), `research/2026-08-14-mira-ara/` (3) | 18 | QueenAgent v1, o günkü adıyla Mira |
| `queenagent-m63`, `-m137`, `-port-model-parametresi` | 12 | QueenAgent v4–v6 dönemi; numarası roadmap'te madde başlığı değil |
| `queen-editor-m138…m147` | 28 | Queen Editor'ün QueenAgent v6 roadmap'inde koşan maddeleri |
| `queen-tools`, `frontend-vite-8`, `defter-adi`, `python-requirements`, `test-paralelligi`, `defterler-main-dalini-klonlar`, `madde-309`, `queenagent-v9-tasarim-ihtiyaclari` | 24 | Roadmap dışı tek seferlik işler |
| research: `h3-referans-prompt-bulgulari`, `video-baglam`, `video-kisa-kurallar` | 3 | Biten işlerin araştırmaları |

`2026-08-09-queen-tools-design.md`'yi collab-toolbox'ın README'si "gerekçe" diye gösteriyor; arşive
gider ve README'nin linki yeni yere döner.

## Linkler

Bir betik her Markdown dosyasındaki her göreli linki eski yerinden çözer; hedefi taşınıyorsa ya da
dosyanın kendisi taşınıyorsa linki yeni yerden yeniden yazar, `#anchor` korunur. Etiketi yolun
kendisi olan bir link (`[docs/research/…json](…)`) etiketiyle birlikte döner. Kod bloğunun ve
satır içi kodun içindeki örnekler link sayılmaz. Kod, notebook ve kural dosyalarından `docs/`'a giden
göreli linkler de aynı geçişte düzelir (BACKLOG'lar, CODE-STANDARD'lar, README'ler, collab-toolbox'ın
bir `instructions.md`'si). Hiçbir kod ya da test `docs/` altındaki bir dosyayı okumuyor (tarandı).

**Önceden kırık linkler** (111) düzeltilmez: hedefleri silinmiş kod dosyaları
(`services/xai/client.py`, `stream_answer.py`, `queenagent/FOUNDATION.md`…), `tmp/`'deki eski
taslaklar, collab-toolbox README'sinde iki eski defter, ve v6 roadmap'inde bir başlığın eski
anchor'ı. Yeni bir hedef tahmin olurdu. Taşınan bir belgedeki böyle bir link yine de yazıldığı yere
gösterir: `../../queen-agent/…` arşivden `../../../queen-agent/…` olur, yani aynı eksik dosyayı adlandırır.
Repo dışına, tasarımcının `queen-design` klasörüne giden iki link de aynı klasöre göstermeye devam eder.

## Kontrol

Bir link denetçisi (`tmp/`'de, iş bitince silinir) repodaki her `.md`'nin her göreli linkini ve
`#anchor`'ını çözer, çözülmeyeni listeler. Taşımadan önce koşar (taban) ve sonra koşar; sonraki
liste tabandakilerden fazlasını içermez.

## Maliyet ve risk

Çalışma anında hiçbir şey değişmez. Risk yalnız kırık link: denetçi onu yakalar. Taşınan bir belge
içeriğiyle değil yalnız linkleriyle değiştiği için git onu yeniden adlandırma olarak görür.

## Bitti sayılır

`docs/` altındaki beş klasörde yalnız açık işlerin belgeleri duruyor, gerisi `docs/arsiv/`'de; on
not `docs/arsiv/notlar/`'da ve düz yazıya çevrilmiş linkler yine link; denetçinin sonraki listesi
tabandakilerden başka kırık link göstermiyor; dört takım yeşil.
