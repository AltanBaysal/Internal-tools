# v12 Görev 2 — Sürükleme: İMPLEMENTASYON döngüsü (tasarım)

**Tarih:** 2026-08-14 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v12](../plans/2026-08-14-queen-editor-v12-roadmap.md) · **Döngü:** 2/2
**Testler:** [test spec'i](2026-08-14-queen-editor-v12-gorev-2-testler-design.md) ·
commit `20f7528` (beş test kırmızı)

## Ne kalkıyor

Basılı tutma mekanizmasının tamamı: `HOLD_MS`, `armed` durumu, `hold` referansı, `press()`,
`release()`, onları çağıran `onMouseDown` / `onMouseUp` / `onMouseLeave`, ve bileşen sökülürken
zamanlayıcıyı temizleyen efekt. Hepsi tek bir amaca hizmet ediyordu — `draggable`'ı sonradan açmak
— ve o amaç tarayıcının çalışma biçimiyle bağdaşmıyor.

Geriye tek satır kalıyor:

```jsx
draggable={!selecting}
```

`onDragEnd` de `release()` çağırmayı bırakıyor; temizleyecek bir şey kalmadı.

## Bunun bir şey kaybettirdiği yer

**Karo metni artık fareyle seçilemiyor.** Sürüklenebilir bir elemanın içindeki yazı seçilemez, yani
karonun altındaki dosya adı da seçilemez olacak. Kabul: galeride yapılan iş sıralamak, dosya adı
kopyalamak değil — ve ad, karenin kendi sayfasında seçilebilir olarak duruyor.

**Kaydırayım derken sıra bozulması** artık tutuşla değil tarayıcının kendi eşiğiyle engelleniyor:
birkaç piksel kımıldamadan sürükleme başlamıyor. Tutuşun asıl derdi buydu.

## Kalan risk, açıkça

Karonun içindeki bağlantı ve resim `draggable={false}` taşıyor — biri URL'yi, öteki resmi
sürüklemesin diye, ve ikisi de gerekli. Tarayıcı sürükleme kaynağını ararken bu ikisini atlayıp
karonun kendisine çıkmalı; standart bunu söylüyor. Colab turunda kart **hâlâ** kalkmıyorsa bir
sonraki şüpheli bu zincirdir, ve o zaman sürüklemenin resimden değil karonun kenarından başlayıp
başlamadığına bakmak ayırt eder.

Burada tarayıcı olmadığı için bu spec bunu çözemiyor; sakladığı da yok.

## Değişen yerler

| Dosya | Ne olacak |
|---|---|
| `.../photo_generation/Gallery.jsx` | tutuş mekanizması silinir, karo hep sürüklenebilir olur |
| `queen-editor/frontend/dist/` | yeniden derlenir (aynı commit) |

## Bitti sayılır

`npm test --prefix queen-editor/frontend` → 324 geçen, 0 düşen; `dist/` aynı commit'te yeniden
derlenmiş olur.
