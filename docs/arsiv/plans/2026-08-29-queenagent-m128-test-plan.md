# Madde 128 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-29-queenagent-m128-add-frames-testler-design.md](../specs/2026-08-29-queenagent-m128-add-frames-testler-design.md)
**Bu tur yalnız test dosyalarına dokunur.**
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

## A. `test_tools.py`: aracın işi, iki sayısı, ve dört reddi — on iki test.

## B. `test_tools.py`: `test_every_tool_is_declared_to_the_model` sekizinci aracı sayar.

## C. `test_skills.py`: prompt+ kareleri `edit_file` ile değil araçla ekler, beşerli ritim kalır.

## D. İki komut koşuldu: **12 kırmızı**, frontend 568 yeşil, defter çifti bilinen kırmızı.

## E. Kırmızı commit.

## İki test bugün yanlış sebepten geçiyor

`test_add_frames_leaves_the_maps_alone` ve `test_add_frames_brings_no_file_into_being` yeşil
doğdular, ama bekçi oldukları için değil: araç yokken `run_tool` *"there is no tool called"*
diyor, hiçbir şey yazılmıyor, dolayısıyla haritalar da bozulmuyor ve doğan dosya da yok. İkisi de
anlamını **ancak kod inince** kazanıyor — o yüzden burada yazılı: uygulama turunda yeşil kalmaları
bir şey kanıtlıyor, bugün kalmaları kanıtlamıyor.

## Bilerek yapılmayanlar: `skip`/`xfail` yok; kod ellenmez; kare silme ve araya sokma yok.
