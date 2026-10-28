# Madde 216 · Varsayılan mod Loop — uygulama turunun tasarımı

**Tarih:** 13 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)
**Test turu:** [tasarım](2026-09-13-queen-editor-m216-varsayilan-loop-testler-design.md) ·
[plan](../plans/2026-09-13-queen-editor-m216-varsayilan-loop-test-plan.md) · kırmızı `d3e1313`

## Kırmızının istediği

Sekiz beklenti, tek bir satırın peşinde: `useState(STANDARD)`. İkisi seçicinin kendisini soruyor
*(Loop işaretli açılsın, dokunulmadan gönderilen iş `loop` taşısın)*, altısı ise butonun altındaki
tahmin cümlesini — o cümle zaten moda göre konuşuyor, yani varsayılan değişince kendiliğinden
değişiyor.

## Varsayılan katmana sorar

```
const [mode, setMode] = useState(layer === "video" ? LOOP : STANDARD);
```

Düz `useState(LOOP)` **ses panelini kırardı**: mod durumu iki panelde de tutuluyor, istek iki panelden
de aynı biçimde çıkıyor, ve sunucu ses işine Standart'tan başka bir mod verilirse reddediyor
*([production_mode.validate](../../../queen-editor/backend/features/photo_generation/domain/production_mode.py))*.
O red ekrana da ulaşmıyor — kullanıcı yalnız sesin üretilmediğini görürdü.

Katman zaten panelin ilk satırında okunuyor *(`WORDS[layer]`)*, yani sorulan şey yeni bir bilgi
değil. `LOOP` de zaten içeri alınmış durumda.

## İki yorum eskiyor

- **`LayerPanel.jsx`**, mod durumunun başındaki not: bugün yalnız *"satırı niye ses paneli
  çizmiyor"*u anlatıyor. Artık aynı yerde ikinci bir sebep var — varsayılanın katmana sorma sebebi —
  ve o sebep sunucunun reddi.
- **`production_modes.js`**, listenin başındaki not: *"Standart başta, çünkü panelin açıldığı yer
  orası."* Artık değil. Sıra değişmiyor — değişen, sıranın gerekçesi: Standart en yalın olduğu için
  başta duruyor, varsayılan olduğu için değil.

İkisi de **yanlış** hâle geldiği için düzeliyor; depo kuralı bunu böyle istiyor — bir yorum yalnız
bugün doğru olanı söyler.

## Dokunulmayanlar

Seçeneklerin kendisi, sıraları, bağlamanın kapanma kuralı, tahmin cümlesinin şablonları, ve detay
sayfasındaki *Yeni mod* kutusu *(varsayılanı `null` — o videonun kendi modu)*.

## Değişen

[LayerPanel.jsx](../../../queen-editor/frontend/src/features/photo_generation/LayerPanel.jsx),
[production_modes.js](../../../queen-editor/frontend/src/features/photo_generation/production_modes.js)
*(yalnız yorum)*, ve `dist`.
