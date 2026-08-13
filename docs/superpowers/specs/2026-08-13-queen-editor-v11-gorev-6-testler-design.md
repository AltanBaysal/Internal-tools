# v11 Görev 6 — LLM açıklamaları kalkar: TEST döngüsü (tasarım)

**Tarih:** 2026-08-13 · **Araç:** queen-editor · **Dal:** `feat/queen-editor-v3`
**Yol haritası:** [v11](../plans/2026-08-13-queen-editor-v11-roadmap.md) · **Döngü:** 1/2 (testler)

Bu spec **yalnız testleri** tanımlıyor. Kod bu döngüde değişmiyor.

## Hangi davranış sınanıyor

Video ve ses panellerinin altında bir açıklama duruyor: *"Video prompt'u otomatik: LLM her fotonun
kendi prompt'undan yazar. Detayda okunur, düzenlenir."* ve sesin aynısı. Kullanıcı ikisinin de
kalkmasını istedi (2026-08-13).

Gerekçesi paneli kuranın değil kullananın: cümle bir kere okunuyor, sonra her panel açılışında yer
kaplıyor. Bilgi kaybolmuyor — prompt'un kendisi karenin detay sayfasında görünüyor ve orada
*"üretim sırası gelince LLM yazacak"* yazıyor, yani söylenecek yerde söyleniyor.

**İkisi birden**, çünkü iki panel tek bileşen ve tasarım birebir aynı olmalarını istiyor; birini
bırakmak onları görünür şekilde ayırırdı.

## Vakalar

| # | Vaka | Beklenen |
|---|---|---|
| K1 | Video paneli açık | Ekranda LLM'den söz eden cümle yok |
| K2 | Ses paneli açık | Ekranda LLM'den söz eden cümle yok |

Mevcut *"says who writes the prompt, since it never asks for one"* testi K1'e dönüşüyor: aynı
cümleyi arayan bir iddia, artık olmadığını arayan bir iddiaya. Sesin böyle bir testi hiç yoktu —
K2 onu da yazıya döküyor, yoksa ses paneli sessizce eski hâlinde kalabilirdi.

## Kapsam dışı

- **Detay sayfasındaki cümle** (*"üretim sırası gelince LLM yazacak"*): orası prompt'un okunduğu
  yer, açıklama oraya ait ve kalıyor.
- Panelin geri kalanı: model adı, kapsam satırları, varyant kutusu, süre notu, düğme.

## Kırmızı commit

İki test; ikisi de düşer. Commit mesajı bunu söyler.

## Bitti sayılır

`npm test --prefix queen-editor/frontend` iki düşen test gösteriyor ve ikisi de "bulunmaması gereken
cümle bulundu" diye düşüyor.
