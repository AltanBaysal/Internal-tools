# Madde 290 · Ekran açılışta koşan export'u görecek — uygulama turunun tasarımı

**Tarih:** 2026-09-21 · **Madde:** [v6 yol haritası](../roadmaps/2026-09-21-queen-editor-v6-roadmap.md) ·
**Test turu:** [tasarımı](2026-09-21-queen-editor-m290-yenilemeye-dayanan-ekran-testler-design.md)

## Kullanıcıdan gereken

Hiçbir şey; tek soru test turunda soruldu ve cevaplandı.

## Çivilenmiş olguların istediği kod

**Tek bir efekt**, `[project]`'e bağlı: açılışta `getExportState(project)` çağrılıyor, ve gelen
cevaptan **yalnız meşgul modlar** `runs`'a yazılıyor.

```
koşanlar = cevaptaki modlardan busy(...) olanlar
koşan varsa → setRuns(koşanlar)
```

**Boşsa hiçbir şey yazılmıyor**, `setRuns` bile çağrılmıyor. Sebebi tek kelimeyle *yarış*: açılışta
sorulan soru, kullanıcı düğmeye bastıktan sonra cevaplanabilir, ve boş bir cevabın basışın iyimser
satırını silmesi gerekmiyor.

**Süzgeç yalnız açılışta.** Basıştan sonraki okumalar *(hem `begin`'in kendi okuması hem yoklama)*
cevabı olduğu gibi alıyor — orada `done` bu koşunun sonucudur, geçmişten bir kalıntı değil.

## Değişmeyen

- **Yoklama.** `going`'e bakıyor, ve `going` artık açılıştaki benimsemeyle de doğru olabiliyor —
  fazladan tek satır yok.
- **`busy()`.** 287'de yazıldı, burada ikinci kez kullanılıyor.
- **409'un etiketi** *(kullanıcı: "sadece şunu çöz")*.

## Bunun getirdiği

Sayfa yenilendiğinde ekran kaldığı yerden devam ediyor: düğme adımını söylüyor, biten adımların
süreleri yerinde, ve basılamıyor. **Kullanıcının gördüğü kırmızı kart da ortadan kalkıyor**, çünkü
basılacak düğme kalmıyor.

**Bedeli:** ekran her açılışta bir istek daha atıyor.

## Bu turda değişen

- `frontend/src/features/photo_generation/ExportScreen.jsx`: açılıştaki okuma.
- `frontend/dist/`: yeniden build.
