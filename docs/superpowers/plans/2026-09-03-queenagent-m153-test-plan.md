# Madde 153 — Test turu planı

**Kaynak:** [tasarım](../specs/2026-09-03-queenagent-m153-numara-testler-design.md) ·
**Tur:** test *(kırmızı commit'lenir)*

Yalnız testler. `tools.py`'ye dokunulmuyor.

---

## 1. `test_tools.py` — numaranın kendisi

- **`test_a_new_frame_carries_its_number`** — eklenen kare `frame: 3` taşıyor.
- **`test_the_frames_that_were_there_get_numbered_too`** — numarasız bir dosyaya kare eklenince
  üçü birden 1, 2, 3 oluyor. Damganın **hepsine** basıldığını söyleyen test.
- **`test_a_second_add_numbers_them_all_again`** — iki kez eklenince numaralar 1'den 4'e gidiyor;
  damga her yazışta yeniden basılıyor.
- **`test_the_number_leads_the_frame`** — `frame` nesnenin ilk anahtarı. Dosyayı açan kişi için.

## 2. `test_tools.py` — cevap

- **`test_add_frames_says_which_number_the_frame_got`** — `Added frame 3 to scene.json.`
- Bugünkü `test_add_frames_says_what_it_added_and_how_many_there_are_now` bunun yerini alıyor:
  cümle tek sayıya iniyor, çünkü boşluk olmadığı için adres ile sayı aynı şey.
- **`test_calling_add_frames_twice_puts_the_frames_in_twice`** — ikinci cevabın `frame 4` demesiyle
  aynı şeyi ölçmeye devam ediyor.

## 3. `test_tools.py` — modelin yazamaması

- **`test_the_model_cannot_write_the_number_itself`** — `frame=9` gönderimi tanınmayan alan olarak
  reddediliyor, dosya değişmiyor. **Bugün de yeşil**; işi 153'ten sonra da kapalı kaldığını tutmak.

## 4. `test_build_prompts.py` — numara prompta girmiyor

- **`test_a_frames_number_never_reaches_the_prompt`** — numaralı bir kare, numarasızla aynı promptu
  kuruyor.

## 5. Koş, kırmızıyı gör, commit'le

```
python -m pytest queen-agent -q
```

Kırmızı: 1. ve 2. adım. 3. ve 4. adım yeşil — biri kırmızıya düşerse numara sızmış demektir.

Diğer üç satır ardışık koşulur.

`test(m153): …`
