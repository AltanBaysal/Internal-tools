# v14 · Görev 4 — Video panelinde Üretim modu seçicisi · **test turu**

**Kaynak:** [Yol haritası v14, 4. madde](../plans/2026-08-20-queen-editor-v14-roadmap.md) ·
[2. maddenin uygulama turu](2026-08-21-queen-editor-v14-gorev-2-uretim-modu-uygulama-design.md)

Bu tur yalnız testleri yazar. Takım kırmızı biter ve kırmızı commit edilir; kodu ikinci tur yazar.

## Bu turun sınırı

**İçeride:** panelde mod satırının doğması, açılıştaki değeri, seçilen modun kuyruğa ulaşması —
panelden uca kadar bütün zincir.

**Dışarıda:** ardışıklık kuralı (5. madde), moda göre değişen cümleler (6. madde), galeri rozeti
(7.), detay sayfası (8, 9). Bu turdan sonra üç mod da her koşulda seçilebilir olacak; ardışık
olmayan seçimle bağlama seçilirse motor hedefsiz kalan kareyi 2. maddedeki kuralla dışarıda
bırakıyor. Görünür eksik, planlı eksik.

## Kararlar

**1. Üç modun Türkçe adı ön yüzde, ayrı bir dosyada.** `features/photo_generation/production_modes.js`:
sıralı bir liste, her satırda kimlik ve etiket. Panelin içinde durmuyor, çünkü aynı üç adı 8. madde
detayın bilgi satırında, 9. madde oradaki seçicide okuyacak — bir sözlüğü ilk okuyanın evinde
tutmak, ikinci okuyan geldiğinde onu oradan çekmek demek.

Kimlik motorun (`domain/production_mode.py`), etiket ekranın. İkisini aynı dosyada tutmak, ekrandaki
adı değiştirenin plan dosyasına yazılan kelimeyi de değiştirmesi demekti.

**2. Satır Kapsam ile Varyant arasında.** Mod, ne üretileceğine karar vermenin parçası; sayının
değil kapsamın tarafında duruyor.

**3. Seçenekler Kapsam'ın satırlarıyla aynı biçimde.** Sağdaki sayı hücresi olmadan: bir modun
sayacak şeyi yok. `ScopeRow`'a boş bir sayı geçmek yerine kendi satırı (`ModeRow`) doğuyor —
eksik bir argümanla "sayı yok"u anlatmak, okuyucuya karar bıraktırırdı.

**4. Ses panelinde satır hiç doğmuyor, ama çağrı biçimi tek.** Panel modu bir durum değişkeninde
tutuyor ve her zaman gönderiyor; ses paneli hep `standard` gönderiyor. İki panelin iki ayrı çağrı
biçimi olması, sunucunun bir isteği nereden geldiğine göre ayırt etmesini gerektirirdi.

**5. Uçta anahtar yoksa `standard`.** Kutuyu tanımayan bir istemci her zaman istediği şeyi istemiş
oluyor — varyant sayısının aldığı okumanın aynısı. `InvalidMode` 400 ve `field: "mode"` ile dönüyor,
çünkü ekranın hata alanını boyaması bu ada bakıyor.

## Zincir

`LayerPanel.onQueue(files, variants, mode)` → `SidePanel` → `useGeneration.queueLayer(kind, files,
variants, mode)` → `api.queueLayer` gövdesine `mode` → `POST .../layers/<kind>` →
`queue_layer(mode=...)`.

## Yazılacak testler

### `frontend/src/features/photo_generation/LayerPanel.test.jsx`

| # | Test | Ne diyor |
|---|---|---|
| 1 | `offers the three ways a video can be made` | Üç etiket ekranda |
| 2 | `opens on the plain one` | Standart seçili, diğer ikisi değil |
| 3 | `stands between the scope and the variant count` | DOM sırası |
| 4 | `sends the mode that was picked` | `onQueue(null, 1, "loop")` |
| 5 | `sends the plain mode when nobody touched the row` | `onQueue(null, 1, "standard")` |
| 6 | `never offers a mode -- a sound ends nowhere` | Ses panelinde ne satır ne seçenek var |
| 7 | `still sends the plain mode, so the server reads one call shape` | Ses de `standard` gönderiyor |

Var olan üç gönderme testi de üçüncü argümanı bekler hâle geliyor: çağrı biçimi değişiyor, ve
biçimi iki ayrı yerde iki türlü yazmak onun tek olmadığını söylemek olurdu.

### `frontend/src/shared/api.test.js`

| # | Test | Ne diyor |
|---|---|---|
| 8 | `carries the production mode into the queue request` | Gövdede `files`, `variants`, `mode` |

### `backend/tests/test_photo_routes.py`

| # | Test | Ne diyor |
|---|---|---|
| 9 | `test_the_videos_endpoint_carries_the_production_mode` | Mod plan satırına iniyor |
| 10 | `test_a_layer_queued_with_no_mode_is_a_plain_one` | Anahtarsız istek `standard` |
| 11 | `test_the_videos_endpoint_refuses_a_mode_nobody_knows` | 400 + `field: "mode"` |
| 12 | `test_a_sound_cannot_be_asked_to_end_anywhere` | 400 + `field: "mode"` |

## Bitti sayılır

`npm test --prefix queen-editor/frontend` on testte kırmızı (yedi yeni + üç değişen; ikisi aynı
dosyada), `python -m pytest queen-editor -q` üç testte kırmızı. 10. test **yeşil doğuyor**:
`queue_layer`'ın varsayılanı bugün de `standard`, ve o varsayılanın kaybolmaması da bu maddenin işi.
