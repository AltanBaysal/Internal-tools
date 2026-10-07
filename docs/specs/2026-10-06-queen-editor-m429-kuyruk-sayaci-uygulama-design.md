# Madde 429 — Kuyruğun sayacı her işi bir kez sayar, uygulama turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 429 · **Tur:** 2/2 — kod.
**Üstüne kurulduğu:** [m429 test turu](2026-10-06-queen-editor-m429-kuyruk-sayaci-testler-design.md) —
sebep, kurallar ve beş kırmızı orada.

## Kanıtlanan sebep, kısaca

`queue.counts` planın her satırını bir iş sayıyor; motor ise planı (kare, katman) başına en son
satırına indirip okuyor (`_latest_per_frame`, madde 211). Aynı iş için ikinci satır yazılınca —
düşürülüp yeniden istenen katman, ya da 422'den beri yeni uzunlukla Tekrar dene — sayılar o iş için
bir fazla. Test turunun beş kırmızısı tam bunu gösterdi: her sayı planın satır sayısıydı.

## Yaklaşımlar

- **Seçilen — sayaç, motorun kuralından geçmiş planı sayar.** `_latest_per_frame` satırları kare
  ve katman başına tutar; `counts` saymadan önce planı ondan geçirir. Bir işin ne olduğu tek yerde,
  ve motorla sayaç onu aynı okur. `open_jobs` onu tip tip çağırdığı için orada hiçbir şey
  değişmez.
- **Elenen — `counts`'ta tipleri tek tek dolaşmak** (`open_jobs` gibi `ORDER` üstünden): tip
  döngüsü ikinci kez yazılır, ve `ORDER`'da olmayan bir tipin satırı sayıdan düşer — bugün olmayan
  bir durum için kimsenin istemediği bir değişiklik.
- **Elenen — tekilleştirmeyi `run_loop`'un `summary`'sinde ve raporunda yapmak:** iki çağıran,
  ve kural kuyruğun dışında; `counts`'un kendisi yine satır sayar.
- **Elenen — planı düzeltmek, ikinci satırı yazmamak:** plan ne istendiğinin kaydı *(madde 211'in
  kararı)*, ve 422'nin Tekrar dene'si yeni uzunluğu o satırda taşıyor.

## Değişen

Yalnız [queue.py](../../queen-editor/backend/features/photo_generation/domain/queue.py):

- **`_latest_per_frame`** — anahtar `job["id"]` yerine `(job["id"], type_of(job))`. Belgesi bir
  satır kare ve katman başına der, ve neden: bütün planı okuyan biri — sayaç — bir karenin
  fotoğrafını ve videosunu ayrı tutmalı. Adı kalır: `video_length.py`'nin belgesi onu bu adla anıyor.
- **`counts`** — saymadan önce `jobs = _latest_per_frame(jobs)`. Belgesi neden olduğunu söyler:
  motor her işi bir kez, en son satırından yapar (madde 429).

Ekran, plan, motor, kapılar değişmez; `counts`'un imzası ve dört anahtarı aynı. `failures`'ta bir iş,
en son satırının plandaki yerinde durur; ekran sunucunun `failures`'ını bugün okumuyor — kırmızı
kartı galerinin karelerinden sayıyor *(useGeneration.js)*.

## Doğrulama

Dört satır. Test turunun beş kırmızısı yeşile döner; öteki her şey yeşil kalır.
