# Madde 515 · Ses düğmesi her videoda — plan

**Madde:** [v11 yol haritası](../arsiv/roadmaps/2026-10-24-queen-editor-v11-roadmap.md#v11-14), 515 · v11-14 ·
**Spec:** [2026-10-29-queen-editor-m515-ses-dugmesi-her-videoda-design.md](../specs/2026-10-29-queen-editor-m515-ses-dugmesi-her-videoda-design.md)

Test önce: testler yeni kuralı söyler (kırmızı), sonra kod (yeşil).

## 1. Sunucu testleri — `backend/tests/test_mute.py`

- Kapının yardımcısı `sounded` → `videos_on(root, *frames, failed=(), sound=())`: her kareye bir video,
  `failed`'dakiler kırmızı, `sound`'dakilere bir de eski ses.
- Kapı: ses katmanı olmayan videoda `PUT true` 200; eski sesli karede 200; videosu olmayan ve videosu
  kırmızı karede 400 *"Bu karenin videosu yok: …"* ve dosya yok; `PUT false` her durumda.
- Export: `test_a_mark_on_a_video_with_no_sound_changes_nothing` → işaretli sessiz-katmanlı video
  `SESSİZ` kesilir; eski sesli işaretli video da (mevcut test kalır).
- Özet: ses katmanı olmayan işaretli video sayılır; videosu olmayan karedeki işaret sayılmaz.
- Modül docstring'i 515'i de söyler.

## 2. Sunucu kodu

- `domain/mute.py`: `holds_sound`, `silenced`, `require_sound`, `NoSound` çıkar; `require_video`,
  `NoVideo` girer; docstring.
- `domain/usecases/mute.py`: `require_video`; docstring.
- `presentation/mute_routes.py`: `NoVideo`.
- `domain/usecases/run_export.py`: mute import'u çıkar; `_audio_of` kendi kontrolüyle; `_write`
  `frame["id"] in muted`.
- `domain/usecases/export_summary.py`: mute import'u çıkar; `muted` üyelikle sayılır; yorum.
- `python -m pytest queen-editor -q`.

## 3. Ekran

- Testler önce, `PhotoDetail.test.jsx`, 510'un bloğu: "sesi olmayan videoda yok" ve "sesi kırmızı
  videoda yok" testleri tersine döner (düğme var); yeni: ses katmanı olmayan videoda kapat/aç ve sessiz
  oynama; videosu kırmızı karede düğme yok. Bloğun başlık yorumu 515'i söyler.
- `PhotoDetail.jsx`: `sounded` → `landed = stateOf("video") === "done"`; yorum.
- `LayerPlayer.jsx`: yalnız `onMute` yorumu.
- `npm test --prefix queen-editor/frontend`, sonra `npm run build --prefix queen-editor/frontend`.

## 4. Belgeler

- 510'un spec'i: düğmenin kimde çıktığını ve `mute.py`'nin bugünkü halini söyleyen yerler 515'e göre
  düzelir; başına 515'e bir bağlantı.
