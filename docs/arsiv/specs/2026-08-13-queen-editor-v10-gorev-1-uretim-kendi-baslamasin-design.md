# Queen Editor v10 · Görev 1 — Üretim kendi kendine başlamasın

**Tarih:** 2026-08-13 · **Koşu dalı:** `feat/queen-editor-v3`
**Kaynak:** [EKSIKLER.md](../../../queen-editor/EKSIKLER.md) — kullanıcının bulgusu:
*"direkt proje açılınca üretim otomatik başlamamalı, ben duraklatılmış gelsin, yarıda kalan varsa
ben basayım başlatmak için."*

## Problem

Bir proje açıldığında ekran kendi kendine üretim başlatıyor. İki yoldan oluyor:

1. **Yarıda kalmış kuyruk.** Oturum ölünce kareler borçlu kalıyor; proje açılınca ekran bunu görüp
   kuyruğu kendisi sürdürüyor ve panele *"uygulama açıldı — kuyruk kaldığı yerden sürüyor"* diye
   bir satır düşüyor.
2. **Üreticisini bekleyen kuyruk.** Kuyruk, başındaki işin üreticisi makinede olmadığı için durmuş
   olabiliyor; o üretici kuruluysa ekran yine kendiliğinden sürdürüyor.

İkisi de kullanıcının istemediği şey: makine, kullanıcı bakmadan çalışmaya başlıyor.

## Karar

**Hiçbir üretim kullanıcı basmadan başlamaz.** İstisnası yok — yarıda kalmış kuyruk da, üreticisini
bekleyen kuyruk da bekler.

Bunun için eklenecek yeni bir ekran yok: kuyruk paneli yarıda kalmış iş için gereken kartı zaten
taşıyor, **"Kaldığı yerden devam et"** düğmesiyle. Kullanıcı onu bugüne kadar hiç görmedi, çünkü
otomatik başlatma ondan önce davranıyordu.

**Hiçbir şey ekrana fırlamıyor** (kullanıcı sorusu): bu kart yalnız Kuyruk panelinin içinde durur.
Uygulama "Fotoğraf üret" paneliyle açılıyor; kuyruğu görmek kullanıcının kendi tıklaması.

## Kartın dili

Yarıda kalmış kuyruk bugün gerçek hatayla aynı kırmızı kartı paylaşıyor: *"Üretim durdu"*. Bu ikisi
aynı şey değil — biri oturumun kapanması, öteki üretimin bozulması. Ayrılıyorlar:

| Durum | Bugün | Sonra |
|---|---|---|
| Oturum kapandı, kare borçlu | kırmızı · "Üretim durdu" | nötr · **"Duraklatıldı"** |
| Aynı kare üç kez başarısız | kırmızı · "Üretim durdu" | değişmiyor |

Düğme ayrı kalıyor: kullanıcının duraklattığı kuyruk "Devam et", yarıda kalmış olan "Kaldığı yerden
devam et" der — biri kaldığı yeri bilerek bırakmıştır, öteki bilmeden.

## Bekleyen kuyruk

Üreticisi kurulu olmadığı için duran kuyruk da artık kendiliğinden sürmez. Ama o kartta bugün
devam düğmesi yok, o yüzden **eklenir** — yoksa kuyruk çıkışsız kalırdı.

Düğme yalnız **üretici gerçekten kuruluyken** görünür. Kurulu değilken sürdürmek, kuyruğu aynı
yerde durdurmaktan başka bir şey yapmazdı; o hâlde kart bugünkü gibi kurulumun nerede yapıldığını
söyler.

Kartın *"Kurulum bitince kuyruk kendiliğinden sürer"* cümlesi de kalkar: artık doğru değil.

## Ne değişmiyor

- Kullanıcının kendi başlattığı üretim, kendi duraklatması, iptali: aynı.
- Kuyruğun diskten okunması: aynı. Yarıda kalan iş kaybolmuyor
  ([FOUNDATION 1](../../../queen-editor/FOUNDATION.md)), yalnız kendiliğinden devam etmiyor.
- Panel yerleşimi, kart yapısı, düğme yerleri: aynı. Eklenen tek şey bekleyen kartın devam düğmesi.

## Test

- Borçlu karesi olan bir proje açılıyor: sunucuya sürdürme isteği **gitmiyor**.
- Üreticisini bekleyen bir kuyruk, üretici kuruluyken açılıyor: yine gitmiyor.
- Yarıda kalmış kuyruk nötr "Duraklatıldı" ile çiziliyor; üç kez başarısız olan kırmızı kalıyor.
- Bekleyen kartta devam düğmesi yalnız üretici kuruluyken var.
- "uygulama açıldı — kuyruk sürüyor" satırı hiçbir yerde çıkmıyor.

## Dokunulan dosyalar

`ProjectScreen.jsx` (iki otomatik başlatma da kalkar), `QueuePanel.jsx` (kartın dili, bekleyen
kartın düğmesi), `SidePanel.jsx` (taşınan prop'lar) ve üçünün testleri.
