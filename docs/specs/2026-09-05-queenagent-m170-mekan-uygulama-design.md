# Madde 170 · uygulama turu — mekân yönetimi

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m170-mekan-testler-design.md).
Commit `dd8870b` 17 vak'ayı çiviledi.

---

## İki dal, üç tanım, üç satır

### `_frames_naming` — mekân dalı

Kadroya hiç bakmıyor: `frame.get("location") == key`. Karakter ve kıyafet `cast_of` üstünden
geçiyor, mekân onun yanından.

### `_renamed_in_frames` — mekân dalı

Alanı yazıyor: `frame["location"] = moving`. Şekil belirsizliği yok, tek dize.

**Bu iki dal, kalıbın gerçekten kalıp olduğunun ölçüsü:** üçüncü kaynak gövdeyi esnetmedi, iki
`if` aldı. `_add_entry`, `_update_entry` ve `_remove_entry` bu maddede **hiç değişmiyor**.

### Fiil satırı zaten yerinde

`_STILL_USED_IN["locations"]` 169'da yazıldı. Bu madde onu çalıştıran ilk yer, ve bir şey
değiştirmiyor.

## Araç tanımları

Üç tanım, kıyafetin üçünün ardında. Açıklamaların taşıdığı fark:

- **Mekânın içinde insan yok.** Kim orada olduğu karenin işi, ve bir mekân girdisine kişi yazmak
  onu her karede o kişiyle birlikte çizdirir.
- **Bir karenin tek mekânı var** — silme reddi bunu söylüyor: *is still the place in frames*.
- **Sayı yok**, kalite etiketi yok. İkisi de başka yerin.

## `modes.py` ve `run_tool`

Üç ad, üç dal, `"locations"` ile.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **Beklenen: 17 kırmızının 17'si de yeşil**, `queen-agent` tarafında **758 yeşil** *(741 + 17)*.
3. Karakter ve kıyafet testleri yeşil kalmalı. Düşerse yeni dal ötekileri kesmiştir.
4. Öteki üç takım rakamlarını korur. `dist` derlenmez.

## Kayda geçen: queen-editor'ün ön yüzü ikinci kez flake verdi

169'da `LayerPlayer`, burada `PhotoDetail` — ikisi de 5000ms tavanını yükten aştı, ikisi de birebir
tekrar koşuda yeşil geldi *(591)*. Bu koşu queen-editor'e hiç dokunmuyor.

**İki kere olması bir örüntü:** o takımın ağır testleri bu makinede tavana yakın koşuyor. Bir madde
açılmadı — ama üçüncü kez olursa açılmalı, ve konusu tavan değil o testlerin neden bu kadar
sürdüğü olmalı.
