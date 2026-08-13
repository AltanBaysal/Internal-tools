# v11 Görev 3 — duran üretim kuyrukta görünmez: TEST döngüsü (tasarım)

**Tarih:** 2026-08-13 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v11](../plans/2026-08-13-queen-editor-v11-roadmap.md) · **Döngü:** 1/2 (testler)

Bu spec **yalnız testleri** tanımlıyor. Kod bu döngüde değişmiyor.

## Hangi davranış sınanıyor

Üretim durdu (xAI anahtarı reddedildi, kuyruk kendini durdurdu) ama kareler hâlâ "video kuyrukta"
diyor. Kullanıcının gördüğü: hiçbir şey ilerlemiyor, ekran ilerliyormuş gibi konuşuyor.

Etiketin kaynağı karenin `owed` listesi. **Borç doğru** — kullanıcı "Devam et" derse o videolar
gerçekten üretilecek. Yanlış olan kelime: "kuyrukta" hareket ima ediyor. Galeri kuyruğun akıp
akmadığını **hiç bilmiyor**; ProjectScreen o bilgiyi hesaplıyor
([ProjectScreen.jsx:39](../../../queen-editor/frontend/src/features/photo_generation/ProjectScreen.jsx))
ama galeriye geçirmiyor.

Sınanacak davranış, kullanıcının kararıyla (2026-08-13):

| Kuyruk | Borçlu kare ne diyor |
|---|---|
| bu projede akıyor | `video kuyrukta` |
| durmuş / duraklamış / hiç başlamamış | `video bekliyor` |
| başka projede akıyor | `video bekliyor` — bu projenin kareleri ilerlemiyor |

"Üretiliyor" ve "hata" durumları değişmiyor: biri karenin işlendiğini, öteki düştüğünü söylüyor ve
ikisi de kuyruğun akışından bağımsız.

## Neden mevcut testler bunu kaçırdı

`Gallery.test.jsx` galeriyi elle kuruyor ve kuyruk durumu diye bir şey vermiyor — çünkü bileşen
istemiyor. Beş iddia "kuyrukta" bekliyor ve hepsi geçiyor; galeri hep "kuyrukta" dediği için.
Testler bileşenin bilmediği bir şeyi soramadı, dolayısıyla bilmediğini de fark edemedi.

Bu yüzden bu döngü **beş mevcut iddiayı da yeni sözleşmeye çeviriyor.** Kuyruğun aktığı varsayılan
testler bunu açıkça söyleyecek; söylemeyenler "bekliyor" bekleyecek.

## Vakalar

### A · Galeri — kelime kuyruğun hâline bağlı (`Gallery.test.jsx`)

| # | Vaka | Beklenen |
|---|---|---|
| A1 | Kuyruk akıyor, karenin video borcu var | `video kuyrukta` |
| A2 | Kuyruk akmıyor, aynı kare | `video bekliyor` |
| A3 | Kuyruk akmıyor, karenin foto borcu var | `foto bekliyor` — kural katmana özel değil. Ayrı test yazılmıyor: güncellenen iddialardan biri (yalnız bekleyen karelerin olduğu galeri) tam olarak bunu okuyor |
| A4 | Mevcut beş iddia | Kuyruğun aktığı anlatılan testler `kuyrukta`, ötekiler `bekliyor` |

### B · Ekran — dikişin kendisi (`ProjectScreen.test.jsx`)

| # | Vaka | Beklenen |
|---|---|---|
| B1 | İş bu projede `running` | Kare `video kuyrukta` diyor |
| B2 | İş `error` ile durmuş | Aynı kare `video bekliyor` diyor |
| B3 | İş başka projede `running` | Bu projenin karesi `video bekliyor` diyor |

B3 tek başına bir vaka çünkü "kuyruk akıyor" ile "benim kuyruğum akıyor" farklı şeyler ve ekran
ikisini zaten ayırt ediyor — galeriye hangisinin geçtiği, ancak bu test varsa yanlış geçirilemez.

## Kapsam dışı

- **Kuyruk panelinin ne dediği.** Kullanıcı sorunun karelerin etiketinde olduğunu söyledi; panel
  zaten durduğunu yazıyor ve "Devam et"i sunuyor.
- **Borcun kendisi.** Kare gerçekten borçlu; silinecek bir şey yok, değişen tek şey kelime.
- **Etiketin köşesi.** O Görev 5.

## Kırmızı commit

Beş yeni test (A1 ve A2 galeride, B1–B3 ekranda) ve güncellenen beş iddia — hepsi düşer. Commit
mesajı bunu söyler; `it.fails`/`skip` yok.

## Bitti sayılır

`npm test --prefix queen-editor/frontend` beklenen sayıda düşen test gösteriyor ve düşme sebepleri
"bekliyor bekleniyordu, kuyrukta geldi" (ya da tersi) — hiçbiri eksik prop'tan ya da bulunamayan
elemandan düşmüyor.
