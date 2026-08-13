# v11 Görev 3 — duran üretim kuyrukta görünmez: İMPLEMENTASYON döngüsü (tasarım)

**Tarih:** 2026-08-13 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v11](../plans/2026-08-13-queen-editor-v11-roadmap.md) · **Döngü:** 2/2
**Testler:** [test spec'i](2026-08-13-queen-editor-v11-gorev-3-testler-design.md) ·
commit `1577dc3` (beş test kırmızı)

## Bilgi nereden geliyor

"Kuyruk akıyor mu" sorusunun cevabı ekranda zaten hesaplanmış:
`ProjectScreen.jsx`'te `running = job.status === "running" && !busyElsewhere`. Galeriye
geçirilmiyor, hepsi bu. Yeni bir kaynak, yeni bir sorgu, yeni bir durum yok — var olan cevap bir
prop olarak aşağı iniyor.

`busyElsewhere`'in içeride olması önemli: işçi global, komşu projenin partisi akarken bu projenin
kareleri ilerlemiyor. Testlerden biri tam olarak bunu koruyor.

## Kelime kararı nerede verilir

`statusOf` bugün de "bir kare hakkında söylenecek tek şey"i seçen yer: önce üretiliyor, sonra hata,
sonra borç. Borcun hangi kelimeyle söyleneceği de oraya ait — `frame_status.jsx` bir eşleme tablosu
olarak kalıyor, yeni bir satır kazanıyor:

```
pending → "kuyrukta"    (kuyruk akıyor)
waiting → "bekliyor"    (akmıyor)
```

Renk ikisinde de aynı: bekleyen bir kare, akan bir kuyrukta da duran bir kuyrukta da aynı ölçüde
okunmayı hak ediyor. Nokta (`alive`) ikisinde de yok — zaten sadece "üretiliyor" için yanıyor.

## Ad çakışması — bilerek çözülüyor

`Gallery.jsx`'in kare döngüsünde bugün `running` adında bir yerel değişken var ve **başka bir şeyi**
anlatıyor: bu karenin hangi katmanının işlenmekte olduğu. Yeni prop'un adı da `running` (testlerin
çivilediği ad, ve ekrandaki değişkenle aynı isim — iki ucu aynı kelimeyle bağlamak doğru olan).

Yerel değişken `rendering` olarak yeniden adlandırılıyor. Gölgelenmiş bir `running` sessizce
"karenin katmanı" ile "kuyruğun hâli"ni birbirine karıştırırdı ve iki değer de doğru göründüğü için
kimse fark etmezdi.

## Değişen yerler

| Dosya | Ne olacak |
|---|---|
| `.../photo_generation/frame_status.jsx` | `STATE`'e `waiting` satırı; `StatusPill` onu da çizer |
| `.../photo_generation/Gallery.jsx` | `running` prop'u alınır, yerel `running` → `rendering`, `statusOf`'a üçüncü argüman |
| `.../photo_generation/ProjectScreen.jsx` | Galeriye `running` geçirilir |
| `queen-editor/frontend/dist/` | yeniden derlenir (aynı commit) |

## Kapsam dışı

- **Kuyruk paneli**, **borcun kendisi**, **etiketin köşesi** (Görev 5).
- `PhotoDetail`'in kendi kelimeleri: orada kare tek başına açılıyor ve sayfanın kendi cümleleri var;
  test spec'i bu yüzeyi kapsamına almadı.

## Bitti sayılır

`npm test --prefix queen-editor/frontend` → 314 geçen, 0 düşen. Beş testin hiçbiri değiştirilmemiş,
`dist/` aynı commit'te yeniden derlenmiş olur.
