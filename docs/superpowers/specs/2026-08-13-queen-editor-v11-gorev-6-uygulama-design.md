# v11 Görev 6 — LLM açıklamaları kalkar: İMPLEMENTASYON döngüsü (tasarım)

**Tarih:** 2026-08-13 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v11](../plans/2026-08-13-queen-editor-v11-roadmap.md) · **Döngü:** 2/2
**Testler:** [test spec'i](2026-08-13-queen-editor-v11-gorev-6-testler-design.md) ·
commit `008001f` (iki test kırmızı)

## Ne siliniyor

İki `hint` metni (`WORDS.video`, `WORDS.audio`) ve panelin sonundaki onları çizen `<Note>`. Metinle
birlikte onu tutan eleman da gidiyor — boş bir `<Note>` bırakmak, sonradan biri metni geri koysun
diye açık kapı bırakmak olurdu.

`marginTop: "auto"` o elemandaydı ve içeriği panelin dibine itiyordu. Onunla birlikte gidiyor: panel
zaten yukarıdan aşağı akan bir sütun, ve dibe itilecek bir şey kalmıyor.

## Kaybolan bilgi kaybolmuyor

Prompt'un dil modeli tarafından yazılacağı, prompt'un okunduğu yerde — karenin detay sayfasında —
söylenmeye devam ediyor: boş prompt kutusu *"üretim sırası gelince LLM yazacak"* diyor. Panelin
görevi kuyruğa iş eklemek; kimin ne yazdığı orada bir kez okunup sonra sürekli yer kaplayan bir
dipnottu.

## Değişen yerler

| Dosya | Ne olacak |
|---|---|
| `.../photo_generation/LayerPanel.jsx` | iki `hint` satırı ve onları çizen `<Note>` silinir |
| `queen-editor/frontend/dist/` | yeniden derlenir (aynı commit) |

## Kapsam dışı

- Detay sayfasının cümlesi: kalıyor.
- Panelin geri kalanı: model adı, kapsam, varyant, süre notu, düğme — hiçbiri değişmiyor.

## Bitti sayılır

`npm test --prefix queen-editor/frontend` → 323 geçen, 0 düşen; `dist/` aynı commit'te yeniden
derlenmiş olur.
