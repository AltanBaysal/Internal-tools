# Madde 318 — Havuz ortada, kartların yerinde açılıyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.**

## Bugün ne oluyor

Havuz kartların solunda 260 px'lik bir sütun *(ReferencePanel)*, açık başlıyor, `×` ile kapanıp
24 px'lik bir şeride iniyor *(ProjectScreen — `poolOpen`)*. Video panelinin Referanstan sekmesi 317'den
beri `Referanslar` başlığını taşıyor ama altı boş.

Bir de: yan panel video ve ses panellerini **aynı yerde, aynı bileşenle** çiziyor
*(SidePanel — `open === "video" || open === "audio"`)*, yani videodan sese geçmek paneli yeniden
kurmuyor — sekme ve kutular sese taşınıyor, videoya dönünce de Referanstan'da açılıyor. 317'nin
*"panel raydan açılınca Kareden'de başlıyor"* kuralı ve bu maddenin *"başka bir panel açmak kartları
geri getiriyor"* kuralı bu yüzden bugün tutmuyor.

## Kurallar

1. **Sol sütun ve şeridi yok.** Ekran iki parça: orta ve yan panel.
2. **Video paneli Referanstan'dayken orta havuzu gösteriyor; panel yanında açık.** Kareler gizleniyor,
   sökülmüyor — seçimleri ve kaydırma yerleri dönüşte yerinde *(karar: galeri kendi seçimini tutuyor,
   ve sökülse o seçim kaybolurdu)*.
3. **Tek düğme, tek yer — `Referanslar` bloğunda:** havuz görünürken `Referansları kapat` kartları
   getiriyor; kartlar görünürken `Referansları aç` havuzu getiriyor.
4. **`Kareden` kartları getiriyor; `Referanstan` havuzu getiriyor** — düğmeyle kapatılmış olsa da.
5. **Başka bir panel açılınca ya da panel kapanınca kartlar geri geliyor.** Videoya raydan dönülünce
   panel Kareden'de *(317)*, yani kartlar kalıyor.
6. **Havuz bu maddede bugünkü içeriğiyle** *(sıralar, `Ekle`)*; sütunun kendi başlığı ve `×`'i
   gidiyor — kapatmanın tek yeri düğme.

## Adlar

- `LayerPanel` iki prop alıyor: `poolShown` *(bool)* ve `onShowPool(bool)`. Sekme `Referanstan` →
  `onShowPool(true)`, `Kareden` → `onShowPool(false)`, düğme → `onShowPool(!poolShown)`, panel
  sökülünce → `onShowPool(false)`.
- `SidePanel` ikisini geçiriyor, ve `LayerPanel`'e **`key={open}`** veriyor: video ve ses iki ayrı
  panel.
- `ProjectScreen` `poolShown`'u tutuyor.

## Yazılacak testler

### `LayerPanel.test.jsx` — yeni blok *"the pool's one button"*

1. **Referanstan havuzu, Kareden kartları istiyor.**
2. **Havuz görünürken `Referansları kapat` kartları istiyor.**
3. **Kartlar görünürken `Referansları aç` havuzu istiyor.**
4. **Panel sökülünce kartlar isteniyor.**

### `SidePanel.test.jsx`

5. **Ses panelinden sonra video paneli Kareden'de açılıyor.**

### `ProjectScreen.test.jsx` — yeni blok *"the pool opens in place of the cards"*

Kartların görünüp görünmediği boş galerinin cümlesinden okunuyor: `henüz kare yok` gizli bir
kabın içinde mi. Havuzun görünüp görünmediği ilk sırasının başlığından: `Fotoğraflar 0/9`. Her test
kendi proje adını alıyor *(galeri projeye göre hatırlanıyor)*.

6. **Kartların yanında havuz sütunu yok** — ne kapatma ne açma düğmesi, ne havuz; kartlar görünüyor.
7. **Referanstan havuzu ortada açıyor, panel yanında** — havuz var, kartlar gizli, `Video üret`
   başlığı duruyor.
8. **Tek düğme havuzu kapatıp yeniden açıyor.**
9. **Kareden kartları getiriyor; Referanstan düğmeyle kapatılmış havuzu yeniden açıyor.**
10. **Başka bir panel ya da panelin kapanması kartları getiriyor** — ses paneli; videoya dönüş
    Kareden'de; panel raydan kapanınca.

**Değişen:**

- `ProjectScreen.test.jsx` — sahte `api.js`'e `getReferenceSettings` ve `saveReferenceSettings`
  *(317'nin iki fonksiyonu; Referanstan açılınca biri çağrılıyor)*.
- `LayerPanel.test.jsx` — `renderPanel` `poolShown={false}` ve `onShowPool={() => {}}` veriyor.

**Kaldırılan:** `ProjectScreen reference panel` → `opens with the pool beside the cards, and closes
it like an editor does` — sol sütunun kendisini soruyordu, ve sütun bu maddeyle gidiyor. Yerini 6 ve
8 alıyor.

**Bekçi:** `gives the card panel no way to close` — kart panelinin kapanmadığı hâlâ doğru.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor/frontend` vitest'te 1–10 kırmızı, öteki üç satır yeşil.
