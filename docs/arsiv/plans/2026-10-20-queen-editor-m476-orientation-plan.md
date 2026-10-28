# Madde 476 — Üretimin yönü, sunucu, plan

> **Koşum:** bu oturumda, ana klasörde, `feat/queen-editor-v10` dalında, adım adım, test önce (TDD).
> Adımlar `- [ ]` ile işaretlenir. Commit ana ajanın.

**Hedef:** her üretim `yatay` ya da `dikey` taşır, varsayılan `yatay`. Fotoğraf o yönün boyutunda
üretilir. H3 videosu fotoğrafın PNG başlığından yönünü okur; REF2VA kartı satırın yönünü kullanır.

**Spec:** [m476](../specs/2026-10-20-queen-editor-m476-orientation-design.md)

**Araçlar:** pytest, vitest.

## Her yere geçerli kurallar

- Yorumlar ve docstring'ler **İngilizce** yazılır ve yalnız bugün doğru olanı söyler.
- Dosyalar Read / Edit / Write ile değişir. Kabuk yalnız pytest, npm ve git status / diff için.
- İki suite birer birer koşulur.
- Frontend ve notebook değişmez, `dist` yeniden kurulmaz.

---

## Görev 1: `domain/orientation.py`

- [ ] `backend/tests/test_orientation.py`: `of` alanı olmayan satıra `dikey`, olana kendi değerini
  veriyor; `validate` iki değeri geçiriyor, başkasını `InvalidOrientation` ile reddediyor;
  `DEFAULT` `yatay`.
- [ ] Kırmızı → modül → yeşil.

## Görev 2: tablolar ve grafik testi

- [ ] `test_workflow_asset.py`: iki yönde birebir oran, 32 ızgarası, adına uygun şekil, 475'in
  sayıları, dikey tablo grafiklere eşit. %1'lik grafik testi birebir teste dönüşür.
- [ ] Kırmızı → `comfy_photo_generator.SIZES`, `comfy_h3_video_generator.SIZES` → yeşil.

## Görev 3: fotoğraf üreticisi

- [ ] `test_comfy_photo_generator.py`: yatay / dikey `"1"` ve `"11"`'e yazılıyor; `None` dokunmuyor;
  düğüm yoksa adı; `generate_batch` de aynı.
- [ ] Kırmızı → `_graph`'a `orientation` → yeşil. `PICTURE_BYTES`'ın yorumu.

## Görev 4: H3 üreticisi

- [ ] `test_comfy_h3_video_generator.py`: `b"PNG"` yerine gerçek bir PNG başlığı (`png(w, h)`);
  yatay ve dikey kaynak I2VA'da ve FL2VA'da doğru boyutu ve hazır ayarı yazıyor; `orientation`
  kareden yapılan videoda yok sayılıyor; REF2VA satırın yönünü izliyor, `None` grafiğin kendisi;
  PNG olmayan kaynak `frame_level` bir hata.
- [ ] Kırmızı → `_orientation_of`, `_sized`, `NotAPicture` → yeşil.

## Görev 5: port, döngü, varyantlar, ses

- [ ] `test_orientation.py` (kuyruğun sahteleri `test_photo_usecases`'ten): döngü satırın yönünü
  `generate`'e veriyor; alanı olmayan satır `dikey`; iki yönün varyantları ayrı; batch yönü taşıyor.
- [ ] `test_producer_contract.py`: sahte fotoğraf sunucusu grafiğin istediği boyutta bir PNG döner;
  gerçek döngü ve gerçek üreticilerle yatay fotoğraftan yatay, eski satırdan dikey video.
- [ ] Sahte üreticilerin imzası `orientation=None` alır; satırın tam şeklini soran üç testin
  beklediği satıra `orientation` girer.
- [ ] Kırmızı → `ports.py`, `run_loop.py`, `variant_batch.py`, `mmaudio_generator.py` → yeşil.

## Görev 6: kapılar

- [ ] `test_orientation.py`: `plan_frames` / `start_batch` yönü satıra yazıyor, varsayılan `yatay`,
  bilinmeyeni reddediyor; `regenerate` yalnız fotoğrafın satırına; `queue_references` her kartın
  satırına.
- [ ] `test_photo_routes.py`, `test_reference_routes.py`: alan istekten use case'e gidiyor; yoksa
  `yatay`; bilinmeyen değer 400 ve (üretimde ve *Yeniden üret*te) `"field": "orientation"`.
- [ ] Kırmızı → `start_batch.py`, `regenerate.py`, `queue_references.py`, `routes.py`,
  `reference_routes.py` → yeşil. `plan_store.append`'in docstring'i.

## Görev 7: Bitiş

- [ ] `python -m pytest queen-editor -q`, sonra `npm test --prefix queen-editor/frontend`.
- [ ] `git status` / `git diff` ile değişen dosyaları gözden geçir.
