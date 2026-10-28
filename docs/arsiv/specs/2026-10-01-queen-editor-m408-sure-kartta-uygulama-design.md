# Madde 408 — Süre kartta görünür, uygulama turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 6 · **Parça:** 408 · v8-2b · **Tur:** 2/2 — kırmızı testleri yeşile
çeviren kod. **Testler:** [m408 test turu](2026-10-01-queen-editor-m408-sure-kartta-testler-design.md).

**Kullanıcıdan gereken — yok.** Kararlar test spec'inde; buradakiler kodun nasıl yazılacağı.

## Seçilen yol

Döngü, üreticiyi çağırmadan hemen önce, kayda `createdAt` yazan duvar saatini (`now`) bir kez daha
okur ve durum raporuna `startedAt` olarak koyar. Ekran bu anı yoklamayla alır; geçen süreyi kendi
saatiyle, saniyede bir yeniden çizen küçük bir bileşende sayar. Kaydedilen süre 405'in kartından
okunur.

Bırakılan yollar:
- **Geçen süreyi sunucuda hesaplamak** (`/api/status` her yoklamada `clock() - started`) — iki makinenin
  saati tutmasa da doğru olurdu, ama durum raporuna bir saat ve bir hesap ekler, ekran da yine iki
  yoklama arasında kendisi saymak zorunda kalırdı. Colab ve kullanıcının makinesi ağ saatine bağlı;
  kalan fark saniyeler, `m:ss`'de görünmez. Ekran sıfırın altına inmez.
- **Monotonik `clock`'u raporlamak** — süreç içinde anlamlı, tarayıcıda hiçbir şey ifade etmez.
- **Yeni bir duvar saati parametresi** — `now` zaten döngünün duvar saati ve testlerde zaten sahte.
  Saniye hassasiyeti (`isoformat(timespec="seconds")`) canlı sayaca bitişte en çok bir saniye fazla
  saydırabilir; katman bitince kaydedilen sayı yerini alır.
- **Sayacı sayfa düzeyinde bir interval'la tutmak** — her saniye bütün sayfayı yeniden çizerdi;
  yazılmakta olan prompt kutusu da onunla. Sayaç kendi bileşeninde, yalnız kendini çizer.

## Parçalar

### 1. Döngü — `domain/run_loop.py`

- Her turun ilerleme raporu `"startedAt": None` taşır (adı `progress`): rapor bir öncekine katılıyor,
  yazılmayan alan eskisini taşırdı.
- Üretim kolunda, `started = clock()`'tan hemen önce: `runner.report({**progress, "startedAt": now()})`.
  İlerleme yeniden gönderilir, böylece her rapor kendi başına tam okunur (son raporun `pending`'ine
  bakan bekçi testi de onu bekliyor).
- Yeniden deneme turu baştan döner: ilk rapor anı sıfırlar, deneme kendi anını yazar.

### 2. Durum çizimi — `frame_status.jsx`

- `clock(seconds)` — `m:ss`, aşağı yuvarlar, sıfırın altına inmez.
- `LiveClock({ since })` — `since`'ten bu yana geçen süreyi yazar, `since` varken saniyede bir kendini
  yeniden çizer; `since` yoksa `0:00`.
- `Pill`'e `below`: verilirse etiket iki satır olur — üstte nokta ve kelimeler, altında `below`;
  `flexDirection: column`, `whiteSpace: nowrap`.
- `StatusPill`'e `since`: yalnız `running`'de ve `since` varken `below={<LiveClock since={since} />}`.
  `StatusPills` durum nesnesinin `since`'ini geçirir.

### 3. Kanca — `useGeneration.js`

`startedAt = current ? job.startedAt || null : null` — bu projenin koşan işinin anı, yoksa `null`.
Döndürülür.

### 4. Galeri — `Gallery.jsx`, `ProjectScreen.jsx`

`Gallery`'ye `startedAt` prop'u; `statusOf` koşan katmanın durumuna `since: startedAt` koyar.
`ProjectScreen` kancadan alıp geçirir. Karenin sayfasının sahnesindeki köşe etiketi `since` almaz: canlı
süre o sayfada sağ sütunda.

### 5. Karenin sayfası — `PhotoDetail.jsx`

`productionTime(state, seconds, since)` açık sekmenin katmanı için ne yazılacağını verir ya da `null`:
`running` → accent, nabız noktası ve `LiveClock`; `pending` → *"henüz başlamadı"*, `--ink-3`; `done` ve
kayıtlı sayı → `clock(seconds)`; geri kalan her şey → `null`. Değer `data-time` taşıyan öğede. `info`
grubunda, *Sıra*'dan sonra `Field label="Üretim süresi"` — yalnız değer varsa.

## Bilinçli olarak yapılmayan

- Dist kurulmaz (koordinatör birleştirmede kurar).
- Kaydedilmiş süre galeride gösterilmez — tasarım yalnız canlıyı istiyor.
- Sahnedeki *"üretiliyor"* kutusu ve köşe etiketi değişmez.

## Bitti sayılır

Dört satır yeşil.
