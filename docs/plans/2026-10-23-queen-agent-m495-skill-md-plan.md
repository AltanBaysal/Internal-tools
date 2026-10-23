# Madde 495 · Altı model metni `.md` dosyalarına — plan

**Spec:** [m495 tasarımı](../specs/2026-10-23-queen-agent-m495-skill-md-design.md) · **Koşu planı:**
[495](2026-10-23-495-skill-md.md) · **Dal:** `feat/queenagent-v11`, ana klasörde · **Eski değerler:**
`c1fdff97`

Durak 1 onaylandı (kullanıcı, 23 Ekim — *"düzelt, önerilerin kabul edildi"*): Seçenek A, seçicinin
adları, CLAUDE.md satırı, CODE-STANDARD'ın iki cümlesi ve belgeler cümlesinin yeri.

## Adımlar

- [x] 1. **Bayt kontrolü önce:** `tmp/m495-bytes.py` — `c1fdff97`'deki `prompt.py`'den altı değeri `ast`
  ile alır; yeni modülün dört skill sabiti, `skills.INSTRUCTIONS` ve `GUIDES` ile karşılaştırır; her
  `.md`'nin ham baytlarını `eski + "\n"` ile; CRLF kopyayı `prompt._read` ile. Taşımadan önce çalıştırılır:
  dosyalar yok, kırmızı.
- [x] 2. **Testler önce (kırmızı):**
  - `test_prompt.py`: her metin kendi dosyası (klasörde tam altı `.md`; `instruction_for(id)` ve
    `GUIDES[ad]` dosyanın okunmuşuna eşit); okunan metnin biçimi (`\r` yok, BOM yok, `strip`'e eşit);
    dört skill adı `prompt.py`'de bir çağrıyla atanıyor (`ast`); eski yer korumasına `SDXL_GUIDE`,
    `KREA_GUIDE`.
  - `test_retired_provider.py`: `skills/` içindeki `.md`'ler taranır; taban: yürüyüşte `sdxl-edit.md`.
  - `test_skills.py`: `test_the_checks_are_written_in_the_flow_itself` `GUIDES`'ın değerlerini de yürür.
  - `python -m pytest queen-agent -q` — yeni testler kırmızı.
- [x] 3. **Altı `.md`** `queen-agent/backend/features/workspace/skills/`'te, Write ile, eski değer + `\n`.
- [x] 4. **`domain/prompt.py`:** `Path`, `_SKILLS`, `_read`; dört skill sabiti `_read(...)`; `SDXL_GUIDE` ve
  `KREA_GUIDE` kalkar, `GUIDES` adlarla okunur; docstring, belgeler bloğunun cümlesi (Karar 2). Üç
  yorum bloğunun geri kalanı kelimesi kelimesine yerinde.
- [x] 5. **Docstring'ler:** `domain/skills.py`, `data/file_file_store.py`, `tests/test_composition.py:74`.
- [x] 6. **Belgeler:** `CODE-STANDARD.md` — domain istisnası; belgeler cümlesi yeni sözüyle ve yeni yerinde.
  `CLAUDE.md` — onaylanan satır, 431 paragrafının arkasında.
- [x] 7. **Bayt kontrolü yeşil:** `python tmp/m495-bytes.py` — altı *eşit*, CRLF *eşit*.
- [x] 8. **Dört suite, tek tek, PowerShell'den:** `python -m pytest queen-agent -q`,
  `npm test --prefix queen-agent/frontend`, `python -m pytest queen-editor -q`,
  `npm test --prefix queen-editor/frontend`. Ön yüz değişmediği için `dist` kurulmaz.
- [x] 9. Rapor ana ajana: değişen dosyalar, bayt kontrolünün sonucu ve yolu, suite'ler. Stage ve commit
  yok.
