# Madde 326 — Referanstan'dan üretim sunucuda düşmüyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.**

## Bugün ne oluyor

`main.py` havuzun üretim kapısını kurarken `queue_references`'a `references=` veriyor; fonksiyonun
böyle bir parametresi yok, havuzu kuyruğa kendisi bağlıyor. Her basış fonksiyona girmeden
`TypeError` ile 500 dönüyor *(kullanıcının `flask.log`'u, 24 Eylül)*. Kapının kendi testleri onu elle
kuruyor, kullanım durumu testleri fonksiyonu doğrudan çağırıyor — `main.py`'nin bu bağlantısını
okuyan test yok.

## Kural

Kapı `main.py`'nin kurduğu hâliyle çağrılınca kendi cevabını veriyor: var olmayan bir projede
`queue_references`'ın kendi reddi, 404 ve `Proje yok: <ad>`.

## Yazılacak test

### `backend/tests/test_composition_root.py`

1. **Havuzdan üretim kapısı `main.py`'nin kurduğu hâliyle cevap veriyor** — iki video modeliyle
   *(`""` ve `h3`)*: `POST /api/projects/m326-yok/references/produce`, gövde
   `{"prompts": '["a"]', "variants": 1}` → 404, `{"error": "Proje yok: m326-yok"}`. Proje yokluğu
   `queue_references`'ın ilk sorusu; iki modelde de H3 sorusundan önce geliyor. Bugün 500.

Proje yok, çünkü `DRIVE_ROOT` testte Colab'ın yolunu gösteriyor — 317'nin aynı dosyadaki testiyle
aynı yol: dışarıya hiçbir şey yazılmıyor, kuyruk hiç başlamıyor.

**Değişen — yok.** **Bekçiler:** aynı dosyadaki iki test; `test_reference_routes.py`'nin üretim
testleri; `test_reference_usecases.py`.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest'te yeni testin iki hâli kırmızı *(500)*, geri kalan
her şey yeşil.
