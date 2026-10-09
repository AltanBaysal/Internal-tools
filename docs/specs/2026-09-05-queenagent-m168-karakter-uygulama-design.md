# Madde 168 · uygulama turu — karakter yönetimi

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m168-karakter-testler-design.md).
Commit `0bb5fc4` 31 vak'ayı çiviledi; bu tur onları yeşile çevirir.

---

## `build_prompts.py` — `_worn` açılıyor

`_worn` → **`cast_of`**, ve adı ne yaptığını söylüyor: bir karenin kadrosunu `(ad, kıyafetler)`
çiftleri olarak veriyor. İki çağrı yeri güncelleniyor. Docstring'ine bir cümle giriyor: artık
`tools.py` de okuyor, yani bu iki şeklin *(harita biçimi ve eski düz ad listesi)* tek okuyucusu
olmak bir sözleşme.

## `tools.py` — üç araç, üç ortak fonksiyon

### `_opened(file_store, project_id, args)`

`(source, structure, refused)`. Dört satırlık açılış tek yerde; `refused` doluysa çağıran onu
olduğu gibi döndürüyor. `_add_frames`'in bugün satır satır yaptığı şey, adı olan bir yere taşınıyor
— ama `_add_frames`'e **dokunulmuyor**: o 173'te ölüyor ve ölmeden önce dokunmak iki kere iş.

### `_entry_tools` — üçünün ortak gövdesi

`which` bir parametre *(`"characters"`)*, çünkü 169 ve 170 aynı gövdeyi `"outfits"` ve
`"locations"` ile çağıracak. Tekil hâli `which[:-1]` ile türetiliyor: *character*, *outfit*,
*location*. Bir cümlenin üç kopyası, ilk değişiklikte üç ayrı cümle olurdu.

**Kareye dokunan iki parça bugün yalnız karakteri biliyor:**

- `_frames_naming(frames, which, key)` — hangi kareler bu adı anıyor. Karakter için `cast_of`'un
  adları; kıyafet ve mekân 169 ile 170'te kendi dallarını ve kendi testlerini getiriyor.
- `_rename_in_frames(frames, which, key, moving)` — kaç kare izledi.

**Bugün yazılmayan dallar bilerek yazılmıyor:** testleri olmayan kod, iki turun ayrılma sebebinin
kendisi.

### Cevap cümleleri

| Durum | Cümle |
|---|---|
| Eklendi | *Added {key} to {which}.* |
| Metin değişti | *Changed {key} in {which}; {n} frames name it.* |
| Ad değişti | *Renamed {key} to {new} in {which}; {n} frames followed.* |
| İkisi birden | *Renamed {key} to {new} in {which} and changed its text; {n} frames followed.* |
| Silindi | *Removed {key} from {which}.* |

Kaç karenin adı andığı her cevapta: modelin bir düzenlemenin nereye gittiğini dosyayı geri okumadan
öğrendiği yer.

## `modes.py`

`_WITHOUT_ASKING[EDIT]`'e üç ad. Ask ve plan soruyor — bir yeniden adlandırma buradaki en geniş
düzenleme, haritayı ve onu anan bütün kareleri birden değiştiriyor.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **Beklenen: 31 kırmızının 31'i de yeşil**, `queen-agent` tarafında **727 yeşil** *(696 + 31)*.
3. `test_edit_mode_asks_for_nothing` ve `test_every_tool_is_declared_to_the_model` yeşil kalmalı:
   araç, kip satırı ve liste aynı turda gidiyor.
4. Öteki üç takım rakamlarını korur. `dist` derlenmez.
