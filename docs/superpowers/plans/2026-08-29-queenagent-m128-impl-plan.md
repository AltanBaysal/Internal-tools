# Madde 128 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-29-queenagent-m128-add-frames-uygulama-design.md](../specs/2026-08-29-queenagent-m128-add-frames-uygulama-design.md)

## A. `tools.py`: `add_frames` tanımı `TOOL_SPECS`'e, `edit_file`'ın hemen ardına.

## B. `tools.py`: `run_tool` dalı ve `_add_frames` — beş kontrol, sonra ekleme ve yazım.

## C. `modes.py`: edit kipi sormadan koşar; ask ve plan kapıyı tutar.

## D. `skills.py`: prompt+ kareleri `add_frames` ile ekler, beşerli ritim kalır, disk cümlesi düşer.

## E. İki komut koşuldu: on üç kırmızı döndü, ama bir test daha kırıldı — ve haklıydı.

`test_the_structured_instruction_writes_the_skeleton_then_batches_of_five`, prompt+ metninde
`edit_file`'ın anılmasını istiyor. Kaldırdığım cümle o adı geçiren **tek** yermiş: metin
düzenlemeyi *"an edit to the frame"* diye anlatıyor, aracını söylemeden. Yani 128'in kare ekleme
cümlesini araca çevirmek, 113'ün düzenleme yolunu aracsız bırakıyordu.

Düzeltme cümleyi kısaltmadı, netleştirdi: *"A complaint about a prompt is **edit_file on** the
frame it came from... or **on** the map entry it names."* Artık düzenleme yolu da aracını adıyla
söylüyor — eskiden söylemiyordu. Test bir gerileme yakaladı, ve yakaladığı şey benim
kaldırdığımdan daha eskiydi.

## F. İki komut yeniden koşuldu: 632 yeşil, frontend 568 yeşil, defter çifti bilinen kırmızı.

## G. Yeşil commit, ardından okuma kopyası.

## Bilerek yapılmayanlar: `WRITES_FILES` (kart çıkmıyor), şema doğrulaması, ön yüz, `dist`.
