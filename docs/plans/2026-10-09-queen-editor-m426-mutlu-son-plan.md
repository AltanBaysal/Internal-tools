# Madde 426 — Videoda mutlu son, plan

> **Koşum:** bu oturumda, ana klasörde, görev görev. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** Video panelinde projeye kaydedilen bir *Mutlu son* düğmesi; açıkken H3 videosu HMCumshot
v1.0 LoRA'sıyla, 0.7'de üretilir ve Queen AI'ın talimatı sonu anlatır; notebook LoRA'yı indirir.

**Yaklaşım:** Test önce, her katmanda: kırmızı görülür, sonra kod. Uzunluğun (422, 424) yolu izlenir:
kendi dosyası, kendi kapısı, işin plan satırında taşınır, döngü üreticiye ve yazara verir.

**Araçlar:** pytest, vitest, vite build.

**Spec:** [m426](../specs/2026-10-09-queen-editor-m426-mutlu-son-design.md)

## Her yere geçerli kurallar

- Yorumlar ve docstring'ler İngilizce, ve yalnız bugün doğru olanı söyler; kullanıcıya giden cümleler
  Türkçe.
- Dört satır CLAUDE.md'deki gibi, **teker teker** — makine 16 GB. `skip` / `xfail` yok.
- Yol haritasına dokunulmaz; grafik dosyalarına dokunulmaz.

---

## Görev 1: Ayarın kendisi — kapı, dosya, kural

- [ ] **Kırmızı:** `backend/tests/test_happy_ending.py` — kapının testleri (varsayılan kapalı, yazılan
  geri gelir, `happy_ending.json`'da ve başka dosyada değil, `bool` dışı 400 ve dosya yazılmaz,
  bilinmeyen proje 404 ve klasör açılmaz, okunamayan dosya kapalı). Modüller testin içinde import
  edilir, `test_video_length.py`'deki gibi.
- [ ] `domain/happy_ending.py`, `data/happy_ending_store.py`, `domain/usecases/happy_ending.py`,
  `presentation/happy_ending_routes.py`; `domain/ports.py`'ye `HappyEndingStore`.

## Görev 2: İşin taşıdığı — kuyruk kapıları ve Tekrar dene

- [ ] **Kırmızı:** `test_happy_ending.py`'ye: Kareden (varyantlar dahil), Referanstan, Yeniden üret
  açıkken `happyEnding: True`, kapalıyken alan yok; ses ve foto taşımaz; Tekrar dene açıkken satırı
  yeniden yazar, kapanınca alan çıkar, değişmediyse plan aynı; uzunluk ve düğme birlikte değişince tek
  satır; `retry_failed` hepsine.
- [ ] `domain/video_settings.py` (`HAPPY_ENDING`, `carried`, `as_set_now`); `video_length.py`'den
  `carried` ve `at_length_now` çıkar.
- [ ] `queue_layer`, `queue_references`, `regenerate`, `retry_frame`, `retry_failed`: `ending=None`,
  `video_settings`'i çağırır.

## Görev 3: Döngü — üreticiye ve yazara

- [ ] **Kırmızı:** `test_happy_ending.py`'ye: düğmesi açık iş üreticiye `happy_ending=True`, kapalı
  `False`; yazara da; bekleyen iş eklendiği düğmeyle. Sahte üreticinin (`test_photo_usecases.FakeGenerator`)
  `happy_ending`'i kaydetmesi.
- [ ] Testlerdeki her sahte `generate` ve `write` imzasına `happy_ending=False` (sed: `references=(),
  seconds=None)` → `references=(), seconds=None, happy_ending=False)`, ve `scene="")` →
  `scene="", happy_ending=False)`).
- [ ] `run_loop.py`: `happy` okunur, `write(…, happy_ending=happy)` ve `generate(…, happy_ending=happy)`.
  `ports.py`: iki imza ve belgeleri.
- [ ] `ComfyPhotoGenerator`, `MMAudioGenerator`: `happy_ending=False` alır, belgesi neden.

## Görev 4: H3 üreticisi — LoRA yığını

- [ ] **Kırmızı:** `test_comfy_h3_video_generator.py`: sevkiyattaki grafiklerle, üç kipte, açıkken
  yığının adlı yuvaları `[Motion Booster 0.7, HMCumshot 0.7]` ve HMCumshot `on`; kapalıyken gönderilen
  yığın dizesi dosyadakinin aynısı; boş yuvası olmayan grafikte Türkçe hata; yığın düğümü olmayan
  grafikte açık iş Türkçe hatayla düşer, kapalı iş bugünkü gibi geçer.
- [ ] `comfy_h3_video_generator.py`: `STACK_NODE`, `HAPPY_ENDING_LORA`, `HAPPY_ENDING_STRENGTH`,
  `_with_happy_ending`; `generate` ve `_from_pool` açıkken çağırır; modül belgesi.
- [ ] `test_producer_contract.py`: foto ve ses üreticisi `happy_ending`'i alır; gerçek döngü düğmesi
  açık işi gerçek H3'e verir ve koşu biter.

## Görev 5: Queen AI'ın talimatı

- [ ] **Kırmızı:** `test_video_prompt_writer.py`: açıkken standart, loop, bağlı modda talimat +
  `HAPPY_ENDING_RULE` + suffix; kapalıyken bugünkü; parça dokuyu ve sesi açıkça istiyor, uzunluk
  söylemiyor, `cumshot`'u tetik kelimesi gibi başa koydurmuyor; ses yazarı `happy_ending`'i alır ve
  görmezden gelir.
- [ ] `prompt_writer.py`: `HAPPY_ENDING_RULE` ve yorumu; `H3VideoPromptWriter.write` ve
  `AudioPromptWriter.write` imzası.

## Görev 6: Bağlama, grup, notebook

- [ ] **Kırmızı:** `test_composition_root.py` (kapı açık; `main._happy_ending` kapının yazdığını
  okuyor), `test_producers.py` (`H3_FILES`'a satır), `test_notebook_installs_the_producer_groups.py`
  (`CIVITAI_H3`'te `(3329529, LORA, "HMCumshot_V1.0.safetensors",` satırı; dosya `MIRRORLESS`'ta değil).
- [ ] `main.py`: store, partial, beş kapıya `ending=`, blueprint. `model_groups.py`: satır ve yorumu.
  `queeneditor.ipynb`: `CIVITAI_H3`'e satır (JSON'u Python'la, hücrenin kaynağı satır satır).

## Görev 7: Frontend

- [ ] **Kırmızı:** `api.test.js` (`getHappyEnding`, `saveHappyEnding`); `LayerPanel.test.jsx` (yeni
  `describe`: blok uzunluğun altında, segment Kapalı · Açık, varsayılan kapalı, kaydedilen açılır,
  basış hemen ve yazılır, sekme değişince yerinde, yazılamazsa kırmızı kart ve geri döner, ses
  panelinde yok, model okunmadan yok, cümleler *"8 sn, mutlu son."*); mevcut başlık listeleri
  *"Mutlu son"*'u da sayar. `PhotoDetail.test.jsx` (iki not açıkken *"8 sn, mutlu son."*);
  `ProjectScreen.test.jsx` mock'una `getHappyEnding`.
- [ ] `api.js`; `useVideoLength.js` → `useVideoSettings.js` (`git mv`), fabrika ve iki kanca ve
  `videoSaid`; `LayerPanel.jsx`; `PhotoDetail.jsx`.
- [ ] `npm run build --prefix queen-editor/frontend`.

## Görev 8: Koş

- [ ] Dört satır, teker teker, depo kökünden. Sonuç satırları rapora.
