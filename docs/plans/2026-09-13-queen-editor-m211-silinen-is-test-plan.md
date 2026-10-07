# Madde 211 · Silinen işin satırı kalıyor — test turunun planı

**Spec:** [test turu](../specs/2026-09-13-queen-editor-m211-silinen-is-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar.

## Hâl gerçek çağrılarla kurulur

Plandaki iş satırı elle yazılmıyor. Satırın biçimi `queue_layer`'ın kendi işi
*(`_job`: `id`, `type`, `number`, `variant`, ve modun eklediği `mode`)*, ve onu testte kopyalamak aynı
şeyi iki yerden tanımlamak olurdu — biri değiştiğinde öteki eskir.

Onun yerine kullanıcının yaptığı sıra koşuluyor:

```
ask(video, mode=standard)   →  plana satır düşer, video üretilir
remove_layer(video)         →  hücre kapanır, satır planda kalır
ask(video, mode=loop)       →  kırmızı burada
```

`ask_again` yardımcısı zaten var *(1607. satır)*; modu da geçebilmesi için bir `mode` argümanı
alacak — var olan çağrıları etkilemeyecek biçimde, varsayılanı bugünkü davranış.

## Adımlar

**1 · Dört çivi eklenir**, `test_a_video_pulled_out_of_the_queue_can_be_asked_for_again`'in yanına —
komşuları aynı sorunun öteki yüzü, ve 14 Ağustos'un çivileri de orada duruyor:

| Test | Ne bekler |
|---|---|
| `a video asked for again after it was deleted is made once` | sıra koşulduktan sonra üretici **iki kez** çağrılmış olur *(ilk istek + ikinci istek)*, üç kez değil |
| `the frame owes one video, not one per time it was asked` | `list_frames`'in verdiği karenin `owed` listesi `["video"]` |
| `three rounds still leave one job` | sıra üç kez koşulur, `owed` yine tek |
| `the video that is made is the one last asked for` | ikinci isteğin ürettiği iş `loop` taşır, `standard` değil |

**2 · Takım koşulur.**

```
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

Kırmızı **okunur**, ve okunacak iki şey var: dört yeni çivi düşmeli, ve **14 Ağustos'un üç çivisi
ayakta kalmalı** — `test_a_sound_pulled_out_of_the_queue_can_be_asked_for_again`,
`test_a_video_pulled_out…`, `test_a_deleted_layer_can_be_asked_for_again`. Onlardan biri düşerse
kurulan hâl yanlıştır.

**3 · Kırmızı commit'lenir.**

## Değişen dosya

`queen-editor/backend/tests/test_photo_usecases.py`.
