# Queen Editor v5 · Görev 20 — Ses üret paneli · Tasarım

**Tarih:** 2026-08-12 · **Dal:** `feat/queen-editor-v3` ·
**Yol haritası:** [roadmap v5](../plans/2026-08-12-queen-editor-v5-roadmap.md) — Blok 6, Görev 20 ·
**Kaynak maddeler:** [tasarım v3 farkları](../research/2026-08-11-queen-editor-tasarim-v3-farklari.md)
30, 31 · madde 7'nin son adımı · **Tür:** arka uç + ön yüz.

## Neden

Video yolu bitti (Blok 5). Ses aynı yolun bir adım darı: kare **videoluysa** ve sesi yoksa ses
üretilebilir. Tasarım paneli için tek cümle kuruyor — "video panelinin birebir aynısı" — yani bu
görevin işi yeni bir ekran icat etmek değil, var olanı ikinci bir katmana açmak.

## Ne olacak

Şeritte dalga ikonu ve **"Ses üret"** paneli doğar: model "MMAudio v2", kapsam satırı "Videosu olup
sesi olmayan kareler", varyant kutusu, dalga ikonlu buton, onay kartı "6 ses kuyruğa eklendi", boş
kapsam cümlesi "Videosu olup sesi olmayan kare yok — üretilecek bir şey yok."

## Kararlar

### 1. Tek panel, iki katman

Video paneli ile ses paneli **aynı bileşen** olur (`LayerPanel`); farkları bir sözlükte durur:
başlık, model adı, kapsam satırının adı, buton ikonu, onay ve boş kapsam cümleleri. Sebep tasarımın
kendi cümlesi ("birebir aynısı") ve QueuePanel'de zaten kurulmuş kalıp: katmanın sözcükleri bir
tabloda, davranış tek yerde.

Kopyala-yapıştır bir `AudioPanel` iki dosyayı ayrı ayrı bozulur hâle getirirdi — üçüncü katman da
yok, yani genelleme spekülasyon değil, bugünkü ikinci kullanım.

### 2. Kapsam kuralı katmanın kendi cümlesi

- **Video:** fotosu inmiş, videosu olmayan kareler.
- **Ses:** fotosu inmiş, **videosu olan**, sesi olmayan kareler.

Videosuz kare ses kapsamına hiç girmez (madde 31) — seçilmiş olsa bile. Video tarafında "seçim
videolu kareyi de alır" kuralı vardı (kopya doğsun diye); seste karşılığı "seçim **videosuz** kareyi
almaz", çünkü sesin üstüne bineceği bir video yok. Zaten `layers.can_produce` bunu domain'de
söylüyor.

Seçim, sesi **olan** kareyi alır: o zaman ses kopya kare olarak doğar — video tarafındaki kuralın
aynısı.

### 3. Kopya kare üretilen katmanın **altındaki** her şeyi taşır

Madde 102: "varyant, üretilen katmana kadarını taşır — video varyantında foto + video olur ama ses
gelmez; ses varyantında üçü birden olur."

Görev 15'in kopyası yalnız foto satırıyla doğuyordu, çünkü üretilen katman videoydu. Kural genelleşir:
kopya, üretilecek katmanın **altındaki** bütün katmanların satırlarını kaynağınkileri göstererek
alır. Ses kopyası foto + video paylaşır, kendi sesini üretir.

### 4. Sunucu tarafında tek use case

`queue_videos` → `queue_layer(kind)`. Kapsam, iş türü ve kopyanın taşıdığı katmanlar hep aynı
kuralın parametreleri. Uç nokta da katmanı adıyla alır: `POST /api/projects/<proje>/layers/<kind>`;
video için bugünkü `/videos` yolu **kaldırılır**, çünkü onu çağıran tek şey bizim kendi ekranımız.

### 5. Ses üreticisi yok, kuyruk bekler

Bu görevde ses işleri kuyruğa girer ama üretici yoktur: motor "ses üreticisi bekleniyor" der ve
kuyruk orada durur (Görev 13'ün hâli). Panelin kurulum kartı da üreticiler listesinden gelen
`audio` satırına bakar — Görev 12'de tanımlı, modelleri MMAudio.

## Nasıl görülür

1. Şeritte dalga ikonu var; panel "Ses üret" başlığıyla açılıyor.
2. Videosuz projede kapsam sayısı 0 ve "Videosu olup sesi olmayan kare yok — üretilecek bir şey yok."
3. Videolu karelere ses işi kuyruğa giriyor, kuyruk panelinde "ses" kartı beliriyor.
4. Varyant 2 istenince biri kareye, biri kopyaya; kopya kaynağın fotoğrafını **ve videosunu**
   paylaşıyor.

## Testler

**Arka uç:** ses kapsamı videosuz kareyi almaz · sesi olan kare yalnız seçimle kapsama girer ·
ses işi `type: audio` ile planlanır · ses kopyası foto ve video satırlarıyla doğar · video kopyası
hâlâ yalnız foto satırıyla doğar · uç nokta katman adını yol üzerinden alır · bilinmeyen katman 404.

**Ön yüz:** panel ses sözcükleriyle açılıyor (başlık, model, kapsam, onay, boş hâl) · kapsam sayısı
videolu-sessiz kareleri sayıyor · gönderim katmanı taşıyor · video paneli bugünkü metinleriyle
çalışmaya devam ediyor.

## Kapsam dışı

- **Ses prompt'u** — Görev 21.
- **Sesin üretilmesi ve videoya bindirilmesi** — Görev 22.
- **Galeride ses rozeti** — Görev 22.

## Riskler

- **Uç noktanın yolu değişiyor.** `/videos` gidiyor, `/layers/video` geliyor. Tek çağıran ekranın
  kendisi ve o da aynı commit'te değişiyor; eski sekme açık kalırsa 404 alır ve yenilenince düzelir.
