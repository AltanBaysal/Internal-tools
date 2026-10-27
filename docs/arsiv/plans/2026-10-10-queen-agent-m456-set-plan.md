# Madde 456 — karakter, kıyafet ve mekânda tek bir `set`, plan

> **Koşum:** ana klasörde, `feat/queenagent-v10` dalında, **commit'lenmeden** ve hiçbir şey stage
> edilmeden — modele giden metni ana agent okur, commit onundur. Adımlar `- [ ]` ile işaretlenir.

**Hedef:** üç map'in her biri için `set_X` ve `remove_X`; 17 tool 14'e iner.

**Yaklaşım:** önce testler yeni tool'ları, cevapları ve maliyeti ister, kırmızı görülür; sonra kod.
Dosyalar Edit ile değişir.

**Spec:** [m456](../specs/2026-10-10-queen-agent-m456-set-design.md)

## Her yere geçerli kurallar

- Metinler ve cevaplar ana agent'ın verdiği gibi, harfi harfine.
- `TOOL_SPECS` ve `run_tool` elle yazılı kalır; tablo ya da ad ayıklama yok.
- `_opened`, `_saved`, `_article`, `_unknown`, `_frames_naming`, `_renamed_in_frames`, `_outfit_renamed`
  değişmez.
- Frame tool'ları, `remove_X`, skill metinleri, frontend, `dist`, queen-editor dokunulmaz.
- Geçici dosyalar `tmp/`'de. `git add`, commit, stash yok.

---

## Görev 1: Testler — kırmızı

- [ ] `test_tools.py`, giriş bölümü (karakter, kıyafet, mekân): `add_X` / `update_X` testleri `set_X`
  testleriyle değişir — Added (adlarla, *nothing*), Changed (numaralar, eski metin, *none*), Renamed
  (frame'ler izler; düz liste ve kısa biçim), Renamed + metin, olmayan ada `new_name`, tag'siz yeni ad,
  aynı tag'ler, `new_name == name`, dolu yeni ad, dict olmayan map, ad yok, boş tag metni siler, öbür
  map'ler aynı kalır.
- [ ] Maliyet testi: `file_store`'u sayan sarmalayıcı; başarı `["read", "write"]`, ret `["read"]`, aynı
  tag'ler `["read"]`.
- [ ] Dosya düzeyindeki retler `(set_X, remove_X)` üzerinden; şema testi `set_X` için
  `{file, name, tags, new_name}` / `{file, name}`, `remove_X` için `{file, name}`.
- [ ] `SHUT` ve kapı testinin cümlesi *"the set_, add_, update_ and remove_ tools"*.
- [ ] Tool listesinin eşitliği 14 adla; `building_again` testi `set_character`'la.
- [ ] Metin testleri `SET_X*`'e: sayı, solo, kıyafet, kategoriler, kıyafetin adı (`SET_OUTFIT`), mekânda
  kimse yok, anatomi yok (`set_X`'in açıklamaları); `SETTING_AN_ENTRY` üç `SET_X`'in sonunda.
- [ ] `EDIT_FILE`'da *"Renaming an entry"* yok.
- [ ] `test_modes.py`: `WRITES`'ta `set_X`.
- [ ] `python -m pytest queen-agent/backend/tests/test_tools.py queen-agent/backend/tests/test_modes.py -q`
  — kırmızı.

## Görev 2: Kod — yeşil

- [ ] `prompt.py`: `SETTING_AN_ENTRY` ortak bölüme; `AN_ENTRYS_NEW_TAGS` ve `AN_ENTRYS_NEW_NAME` yeni
  metinleriyle, docstring *"every set_ tool's"*; dokuz `SET_X*`; on sekiz `ADD_X*` / `UPDATE_X*` gider;
  `EDIT_FILE`'ın son cümlesi gider; SDXL bölümünün yorumu ve *"Six tools"*.
- [ ] `tools.py`: üç `set_X` spec'i, altı add / update spec'i gider; `run_tool`'da üç `set_X` dalı;
  `_set_entry`; `_add_entry` ve `_update_entry` gider; `_shut`'ın cümlesi; `_remove_entry`'nin docstring'i.
- [ ] `modes.py`: Edit'in listesi.
- [ ] Aynı iki dosya — yeşil. Repo'da `add_character|update_character|ADD_CHARACTER|UPDATE_CHARACTER`
  (ve öbür ikisi) için grep: yalnız `docs/`'ta.

## Görev 3: Ölçüm ve dört suite

- [ ] `tmp/m456_size.py` ile sabit başın boyu; spec'in tablosuna yazılır.
- [ ] `python -m pytest queen-agent -q`; `npm test --prefix queen-agent/frontend`;
  `python -m pytest queen-editor -q`; `npm test --prefix queen-editor/frontend` — birer birer.
- [ ] `git status`: yalnız spec, plan, `prompt.py`, `tools.py`, `modes.py`, `test_tools.py`,
  `test_modes.py`.
