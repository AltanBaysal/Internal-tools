# Madde 229 · Model listesi ComfyUI'ye gitmeyecek — uygulama turunun tasarımı

**Tarih:** 17 Eylül 2026 · **Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md) ·
**Testler:** [test turu](2026-09-17-queen-editor-m229-model-listesi-testler-design.md)

## Kullanıcıdan gereken

Test turundakiyle aynı: bir sonraki yalnız-video açılışında `flask.log`'daki `/api/models` satırı.
Maddeyi beklemiyor.

## Ne değişiyor

Test turunun çividiği davranış tek bir kesintiyle geliyor: **checkpoint sorusu uygulamadan tamamen
çıkıyor.** Katman katman:

| Katman | Dosya | Değişiklik |
|---|---|---|
| domain | `usecases/list_models.py` | `list_models(chosen)`: yalnız tarifler, `generator` yok |
| domain | `ports.py` | `PhotoGenerator.models` gider |
| data | `comfy_photo_generator.py` | `models()` gider |
| service | `comfy/client.py` | `checkpoints()` gider |
| presentation | `routes.py` | `/api/models`'in `try/except`'i ve 502'si gider: çağrılan şey artık bir dosyaya bile gitmiyor |
| kök | `main.py` | `partial(list_models, config.PHOTO_RECIPES)` |
| kök | `config.py` | `PHOTO_RECIPES` yorumu: boş liste artık "fotoğraf kurulmadı" demek, "ComfyUI'ye sor" değil |

`recipes.py`'nin belgesi değişmiyor: *"hangi tarifin kurulu olduğu diske sorulamaz"* diyor, ve bu hâlâ
doğru.

**Neden sessiz bir boş liste yeterli:** yalnız video için açılan defterde fotoğraf üreticisi kurulu
değil, ve panelin `InstallCard`'ı bunu zaten söylüyor. Bu turda ön yüze dokunulmuyor.

## Seçilmeyen yol

Yerel çalıştırma için checkpoint sorusunu **yalnız tarif yokken** tutmak. Bu yol bugünkü hatanın ta
kendisi, ve uygulamanın yerelde koştuğu bir kullanım yok *(FOUNDATION, karar 1)*.
