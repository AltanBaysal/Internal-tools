# Madde 481 · Ajan karışan kareleri düzeltir — plan

**Spec:** [2026-10-20-queen-editor-m481-mixup-fix-design.md](../specs/2026-10-20-queen-editor-m481-mixup-fix-design.md)
· **Dal:** `feat/queen-editor-v10` · Test önce (TDD).

## 1. Fotoğraf özelliği: `fix_photo`

1. `backend/tests/test_fix_photo.py` — önce testler (spec, "Bitti sayılır" 1). Sahteler
   `test_photo_usecases`'ten. Kırmızı.
2. `backend/features/photo_generation/domain/copy_frame.py`: `made_by` — fotoğrafı yapan plan satırı,
   kopya karede kaynağınınki.
3. `backend/features/photo_generation/domain/usecases/fix_photo.py`:
   - galeri okuması ve izlenen alanlarla bayatlık kontrolü (`changed`);
   - açık işlerde bu kareye bağlı bir video varsa `linked`, hiçbir şey yazılmaz;
   - `made_by` ve madde 99'un kimliği (`_born`);
   - sırasıyla plan ekleme, sıra yazma, `files_to_unlink` ile silme ve `deleted` satırları;
   - `run_queue`, `Busy` → `waiting`.

   Yeşil.

## 2. Ajan: `fix_frame`

1. `backend/tests/test_agent_answer.py`:
   - `Project`'e `fix` sahtesi, `answering` onu geçiriyor;
   - kartlarda `negative`; `FRAME_2` negatifi taşıyor;
   - sistem mesajı ve dört araç için testler güncelleniyor;
   - 480'in sahte `fix_frame` fikstürü yeni imzayla;
   - düzeltme testleri ekleniyor.

   Kırmızı.
2. `backend/features/agent/domain/prompt.py`:
   - `INSTRUCTION`: Context, Rules ve *Fixing mix-ups*;
   - `READ_FRAME`'e negatif; `FIX_FRAME`, `THE_PROMPT`, `THE_NEGATIVE`;
   - `FIX_RULES`, QueenAgent'tan kopya; `MIXUP_RULES`'un yorumu.
3. `backend/features/agent/domain/tools.py`:
   - `_tool` metin argümanları alıyor; `TOOLS`'a `fix_frame`;
   - `card(whole=True)`'ya `negative`;
   - `_has_video`, `_unfixable`, `_fix`; `FIX_TOLD`, `FIX_NEEDS_WORDS`, `PHOTO_GOES`;
   - `run_tool` `fix`'i alıyor ve argümanları bir kez ayrıştırıyor.
4. `backend/features/agent/domain/usecases/answer_question.py`:
   - `fix` argümanı;
   - sistem mesajı `INSTRUCTION + MIXUP_RULES + FIX_RULES + SYSTEM_PROMPT_SUFFIX`.

   Yeşil.

## 3. Kablolama

1. `backend/tests/test_agent_routes.py`: `app_over`'a `_no_fix`; sahte `fix_frame` fikstürü yeni
   imzayla.
2. `backend/tests/test_composition_root.py`: dört aracın adı; yeni uçtan uca düzeltme testi (koşucunun
   `start`'ı tutulur, ComfyUI'a bir şey gitmez). Kırmızı.
3. `backend/main.py`: `_agent`'a `partial(fix_photo, …)`, kuyruğun öteki yollarıyla aynı nesnelerle.
   Yeşil.

## 4. Ekran: galeri düzeltmeyi izler (QA'dan sonra, spec karar 7)

1. Önce testler, kırmızı:
   - `frontend/src/features/photo_generation/useGeneration.test.jsx`: `follow`;
   - `frontend/src/features/agent/AgentPanel.test.jsx`: `onChanged` — adım bitince, sıradaki
     değişikliğe geçince, durdurulunca; Reddet'te, `409`'da, başka sohbette ve başka projede değil —
     ve iki yanda "(boş)";
   - `frontend/src/features/photo_generation/ProjectScreen.test.jsx`: ajanın kapıları sahte api'ye
     eklenir, ve İzin ver'den sonra galeri okunup üretim izleniyor.
2. `useGeneration.js`: `follow` (açılışın `poll`'u) döner.
3. `ProjectScreen.jsx` → `SidePanel.jsx` (`onAgentChanged`) → `AgentPanel.jsx` (`onChanged`) →
   `useAgentChat.js` (varsayılan `onChanged` yalnız orada): İzin ver'de değişikliğin adımının yeri,
   projesiyle tutulur; sohbet onu bitmiş ya da soruyu bitmiş gösterince `onChanged` bir kez.
4. `AgentPanel.jsx`: boş "Eski" ve "Yeni" değer "(boş)".
5. Yeşil; `npm run build --prefix queen-editor/frontend`.

## 5. Doğrulama

1. `python -m pytest queen-editor -q`
2. `npm test --prefix queen-editor/frontend`
