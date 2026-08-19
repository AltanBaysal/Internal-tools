# Madde 39 — Shot düşer, frame gelir · Test Turu Planı

**Tasarım belgesi:** [2026-08-19-queenagent-m39-kare-testler-design.md](../specs/2026-08-19-queenagent-m39-kare-testler-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

Bu plan **yalnız testleri** yazar. Kaynak dosyalara dokunulmaz.

---

## Adım 1 — `test_build_prompts.py`

- `_shot` → `_frame`, `_structure`'ın anahtarı `shots` → `frames`, test adlarındaki "shot" → "frame".
- Hata satırı iddiaları `"shot 1"` → `"frame 1"`.
- `test_the_output_is_named_after_the_source` örneği `intro-frames.json` → `intro-frames.py`.
- **Yeni:** `test_an_old_structure_still_reads_its_list_from_shots` — listesi `"shots"` altında olan
  yapı aynı promptları verir.
- **Yeni:** `test_a_structure_carrying_both_lists_uses_frames` — ikisi varsa `frames` kazanır.

## Adım 2 — `test_skills.py`

- `ALL_SKILLS`: `split-into-shots` → `split-into-frames`, `verify-shots` → `verify-prompts`.
- `instruction_for("verify-shots")` geçen her test yeni adı kullanır.
- Şema testinin alan listesi `shots` → `frames`.
- Senaryo yönergesinin "shot list'in alanına girme" testi artık "frame" arar.
- **Yeni:** `test_no_instruction_says_shot_any_more` — bütün yönergelerde kelime aranır, hiçbirinde
  geçmez *(süpürge)*.
- **Yeni:** `test_the_old_skill_names_carry_nothing` — `split-into-shots` ve `verify-shots` boş
  dize döner.
- **Yeni:** `test_the_structured_instruction_names_the_structure_file_after_frames` —
  `intro-frames.json` yönergede geçer.
- **Yeni:** `test_verify_talks_about_prompts_rather_than_frames` — denetleyen yönerge "prompts"
  üzerinden konuşur.

## Adım 3 — `test_tools.py` ve `test_stream_answer.py`

- `test_tools.py`: `build_prompts` tarifinin "shot" geçen iddiası "frame" olur.
- `test_stream_answer.py`: `STRUCTURE` sabitinin anahtarı `frames`; dosya adları `shots.json` →
  `frames.json`, beklenen çıktı `frames.py`.

## Adım 4 — Ön uç

- `skills.test.js` — kimlik listesi yeni adlarla; menü satırının cümlesi.
- `SkillPicker.test.jsx` · `ChatScreen.test.jsx` · `App.test.jsx` — kimlikler ve görünen adlar.
- `FilePanel.test.jsx` — `shots.json` sabiti `frames.json`, içindeki alan `"frames"`.

## Adım 5 — Kırmızıyı gör

İki komut da koşulur. Düşmesi beklenenler: yeniden adlandırılan her iddia, eski kimliklerin boş
dönmesi, süpürge testi, yeni alan adını arayan testler. Geçmesi beklenen: eski `"shots"` okuması.

Bu listede olmayan bir test düşerse sebebi anlaşılmadan devam edilmez.

## Adım 6 — Kırmızı commit

`skip` yok, `xfail` yok. Commit mesajı çift tırnak taşımaz.

---

## Kapanış denetimi

- `git status` yalnız test dosyalarını gösteriyor.
- `grep shot` kaynak dosyalarda hâlâ dolu — uygulama turu onu boşaltacak.
