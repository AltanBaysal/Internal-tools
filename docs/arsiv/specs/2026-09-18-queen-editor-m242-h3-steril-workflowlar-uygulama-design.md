# Madde 242 · H3'ün iki API workflow'u steril — uygulama turunun tasarımı

**Tarih:** 18 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** yok *(kullanıcı kararı — sebebi maddede)*

## Kullanıcıdan gereken

Hiçbir şey. İki export'u kullanıcı 213'ün denemesinde aldı, temizliğin listesi onunla align olundu.

## Dayandığı kurallar

- [FOUNDATION 8](../../../queen-editor/FOUNDATION.md) ve [CODE-STANDARD § Independence](../../../queen-editor/CODE-STANDARD.md):
  grafik queen-editor'ün kendi dosyası olarak `queen-editor/` altına kopyalanır; collab-toolbox'taki
  bir kopyayı okumak yasak. WAN'ın iki dosyası da orada: `workflow_video_api.json`,
  `workflow_video_first_last_api.json`.
- Emsal WAN'ın dosyaları: pozitif prompt `""`, resim yer tutucusu `example.png`.

## Tasarım

**Kaynak:** repo kökünde commit'lenmemiş iki export. Aynı grafik, yalnız mod ve seed farklı.

| Kaynak | Mod | Hedef |
|---|---|---|
| `workflow (1).json` | I2VA | `queen-editor/workflow_video_h3_api.json` |
| `workflow.json` | FL2VA | `queen-editor/workflow_video_h3_first_last_api.json` |

**Değişen alanlar — yalnız Director node'u (`2730`):**

1. **Prompt boş.** Metin dört yerde duruyor: `inputs.prompt`, `timeline_data`'nın
   `builder_state.simple_prompt`'u ve `resolved_prompt`'u, ve `inputs.builder_state`'in
   `simple_prompt`'u. Dördü de `""`. `dynv2` de gidiyor: onu 243'ün prompt yazarı yazıyor.
2. **Resim `example.png`.** `timeline_data`'daki her öğenin `value`'su `05.png` → `example.png`.
3. **Yalnız I2VA'da, tek resim.** Timeline'ın ikinci öğesi (son kare) çıkıyor, ilki kalıyor
   (slot 0, başlangıç 0). Bu biçim arayüzün ürettiği FL2VA öğesinden alındı; tek resimli I2VA hâli
   ComfyUI'de koşmadı, koşusu roadmap'in sonundaki denemede.
4. **Yalnız I2VA'da, `builder_state` `I2VA`.** Pill çevrilerek alındığı için iki yerde
   (`timeline_data` içinde ve `inputs.builder_state`'te) `"mode":"FL2VA"` duruyor; ikisi de `I2VA`.

**Dokunulmayan:** öteki bütün node'lar ve ayarlar — 4 sn, 512×768, 24 fps, DaSiWa hybrid turbo,
euler 8 adım, shift 6/3, yalnız Motion Booster 0.7. Seed geçmişi ve test resminin ölçüleri
(`source_width/height`) içerik değil ve 243'te üstlerine yazılıyor.

**Kökteki ham export'lar** hedefe taşınıp orada temizlenir, yani kökte kalmaz.

## Doğrulama

Test yok. İki dosya okunur: `05.png`, `dynv2` ve prompt'un herhangi bir cümlesi kalmamış; JSON
geçerli; I2VA'da timeline'da tek öğe var. queen-editor'ün takımı koşar ve yeşil kalır — bu turda hiçbir
kod dosyayı okumuyor, okuyan 243.

## Bu turda değişen

`queen-editor/workflow_video_h3_api.json` ve `workflow_video_h3_first_last_api.json` (yeni). Ve yol
haritasında 242'nin işareti.
