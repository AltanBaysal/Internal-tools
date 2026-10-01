# Madde 408 — Süre kartta görünür, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 6 · **Parça:** 408 · v8-2b · **Tur:** 1/2 — yalnız testler, kırmızı
commit'lenir. **Öncesi:** [m405](2026-10-01-queen-editor-m405-uretim-suresi-kaydi-testler-design.md)
süreyi kaydetti; bu parça gösterir.

**Kullanıcıdan gereken — yok.** Madde `ALIGNED`; kararlar yol haritasının tablosunda (408) ve
*v8-2 — Üretim süresi* bölümünde, görünüş tasarımda *(queen-design `queen-editor-v1`, 197 ve 201)*:

- **Karenin sayfası:** sağ sütunda, *Sıra*'nın yanında tek satır **Üretim süresi** — açık sekmenin
  katmanının süresi, katman adı olmadan, `m:ss`. Üretilirken canlı; kuyruktaysa *"henüz başlamadı"*;
  hata alan katmanda ve eski karede alan yok. Bitince kaydedilen süre kalır.
- **Galeri:** yalnız canlı süre — üretilen kutucuğun durum etiketinde ikinci satır: *foto üretiliyor*,
  altında `0:46`. Bitmiş ya da kuyruktaki katmanın kutucukta süresi yok.

## Bugün ne oluyor

405'ten beri `GET /api/projects/<p>/frames`'in her kartı `renderSeconds: {katman: saniye}` taşıyor —
yalnız süresi kaydedilmiş katmanlar. Ekran onu okumuyor. Durum raporu (`/api/status`) `current` ve
`pending` diyor, ama **o katmanın üretiminin ne zaman başladığını** demiyor: sayfa yenilenince canlı
sayacın baştan başlamaması için o anın sunucudan gelmesi gerekiyor.

## Kurallar

1. **Durum raporu modelin başladığı anı söyler:** `startedAt` — döngünün kendi duvar saatinin (`now`,
   kayda `createdAt` yazan saat) üreticinin çağrısından hemen önceki okuması. 405'in süresi aynı yerde
   başlıyor; canlı sayaç ile bitince kalan süre aynı şeyi sayar.
2. **Model çalışmıyorken `startedAt` yok (`null`):** katmanın kaynağı Drive'dan okunurken, prompt
   yazılırken, ve sıradaki işe geçilince. Rapor bir öncekine katılıyor *(runner.report)*: anı
   söylemeyen rapor eskisini taşırdı, o yüzden her işin ilk raporu onu açıkça sıfırlar.
3. **Her deneme kendi anını söyler:** yeniden denenen katmanın sayacı yeni denemeyle baştan başlar —
   405 de yalnız katmanı üreten denemeyi kaydediyor.
4. **Ekran anı sunucudan okur, saymayı kendi yapar:** geçen süre = şimdi − `startedAt`, saniyede bir
   ilerler; sayfa yenilense de aynı sayıdan devam eder. Sıfırın altına inmez (iki makinenin saati
   tutmazsa `0:00`).
5. **`m:ss`:** saniyeler aşağı yuvarlanır — `46.3` → `0:46`, `212.0` → `3:32`.
6. **Karenin sayfasında alan açık sekmenin katmanına göre:**
   - üretiliyor → canlı süre, accent renkte, nabız noktalı; başladığı an henüz gelmediyse `0:00`;
   - kuyrukta → *"henüz başlamadı"*;
   - bitmiş ve süresi kayıtlı → kayıtlı süre, durağan;
   - bitmiş ama süresiz (eski kare, ya da eski kareden kopya), hata almış, ya da hiç olmayan katman →
     alan yok.
   Alan `data-group="info"`'da, *Sıra*'dan hemen sonra; *Ayrıntılar* kapalıyken de görünür.
7. **Galeride yalnız üretilen kutucuk süre taşır,** durum etiketinin ikinci satırında, başladığı an
   geldiyse. Etiket iki satır olunca alt alta dizilir. Kuyruktaki, hata almış ve bitmiş kutucuk süre
   göstermez — kaydı olsa da.
8. **Galeri anı ekranın kancasından alır:** `useGeneration` `startedAt`'ı bu projenin koşan işi için
   verir, başkasının işi için `null`.

## Yazılacak testler

### Backend — `test_photo_usecases.py`

Raporlar bir casus runner'la izlenir: her `report` çağrısı listeye girer ve gerçek runner'a da gider.
`now` sırayla `"t1"`, `"t2"`… döndürür.

1. **Rapor modelin başladığı anı söylüyor, ve sıradaki işe geçince sıfırlıyor** — iki fotoğraf:
   raporların `startedAt`'ı sırayla `[None, "t1", None, "t3"]` (`t2` ilk satırın `createdAt`'ı).
2. **Kaynak okunurken başlangıç yok** — videonun fotoğrafı Drive'dan okunurken birleşik raporda
   `current` videonun işi, `startedAt` `None`.
3. **Prompt yazılırken başlangıç yok** — prompt'suz video; yazar çağrılırken birleşik raporda
   `current` ve `startedAt` `None`.
4. **Yeniden denenen katman her denemede kendi anını söylüyor** — ilk iki deneme düşüyor: üretici her
   çağrıldığında gördüğü `startedAt` `["t1", "t2", "t3"]`.

**Bekçiler — değişmeden yeşil:** `test_progress_reports_name_the_frames_still_waiting` (son raporun
`pending`'i — anı söyleyen rapor da ilerlemeyi taşır), 405'in süre testleri, log satırı testleri,
`test_producer_contract.py`.

### Frontend — `useGeneration.test.jsx`

5. **Koşan işin başladığı anı veriyor** — durum `running`, bu proje, `startedAt` → kanca aynı değeri
   verir.
6. **Başka projenin işi için anı vermiyor** — `startedAt` `null`.

### Frontend — `PhotoDetail.test.jsx`, *the production time (madde 408)*

Saat sahte (`vi.useFakeTimers`, `vi.setSystemTime`); hiçbir test gerçek bir saniye beklemez.

7. **Kayıtlı süre *Sıra*'nın yanında** — `renderSeconds: {photo: 46.3}`: `info` grubunun alanları
   `["Sıra", "Üretim süresi"]`, değer `0:46`, katman adı yok.
8. **Açık sekmenin katmanının süresi** — video sekmesinde `3:32` (212.0), ses sekmesinde `0:19`.
9. **Eski karede alan yok** — süresiz bitmiş kare: `["Sıra"]`.
10. **Hata alan katmanda alan yok** — fotoğrafın süresi var, video kırmızı: video sekmesinde alan yok.
11. **Kuyruktaki katman *"henüz başlamadı"*** — kuyruktaki video sekmesi.
12. **Üretilen katman canlı ilerliyor** — `startedAt` 46 sn önce: `0:46`, accent renk; 2 sn sonra
    `0:48`.
13. **Yeniden yüklenen sayfa aynı sayıdan devam ediyor** — sayfa sıfırdan açılır, `startedAt` 3 dakika
    önce: `3:00`, `0:00` değil.
14. **Başladığı an gelmeden `0:00`** — koşan iş `startedAt`'sız.
15. **Saat geride ise sıfırın altına inmiyor** — `startedAt` 5 sn ileride: `0:00`.
16. **Bitince kayıtlı süre kalıyor** — canlıyken sonraki yoklama katmanı `renderSeconds: 47.2` ile
    bitmiş getirir, iş bitmiş: `0:47`, accent değil.

### Frontend — `Gallery.test.jsx`, *the live time on the tile (madde 408)*

17. **Üretilen kutucuğun etiketinde ikinci satır** — `current` foto, `startedAt` 46 sn önce: etiket
    `foto üretiliyor` ve `0:46`; etiket alt alta (`flexDirection: column`).
18. **Süre canlı ilerliyor** — 1 sn sonra `0:47`.
19. **Başladığı an gelmeden ikinci satır yok** — `startedAt` yok: etiket yalnız `video üretiliyor`.
20. **Bitmiş ve kuyruktaki kutucuk süre göstermiyor** — süresi kayıtlı bitmiş kare ve kuyruktaki video:
    hiçbir yerde `m:ss` yok.

### Frontend — `ProjectScreen.test.jsx`

21. **Galeri koşan işin anını alıyor** — durum `running`, bu proje, `current` `{id, type: "photo"}`,
    `startedAt` 46 sn önce: kutucukta `0:46`.

**Bekçiler — değişmeden yeşil:** galerinin ve karenin sayfasının bugünkü etiket testleri
(`video üretiliyor`, `foto üretiliyor` — anı vermeyen testler tek satır görmeye devam eder),
*Ayrıntılar* testleri (`facts()` süresiz karelerde `["Sıra", …]`).

## Bitti sayılır

Dört test satırı koşulur. `queen-editor` pytest'inde 1–4 kırmızı (raporda `startedAt` yok:
`KeyError`/eşitsizlik). Vitest'te 5–8, 10–18 ve 21 kırmızı — 6 kancanın `undefined`'ı yüzünden, 10
fotoğraf sekmesindeki süre henüz yazılmadığı için. 9, 19, 20 bugün de doğru — alanın ve ikinci satırın
yokluğunu bekliyorlar, yeşil başlarlar ve uygulamada yeşil kalmalılar.
`queen-agent`'ın iki satırı yeşil.
