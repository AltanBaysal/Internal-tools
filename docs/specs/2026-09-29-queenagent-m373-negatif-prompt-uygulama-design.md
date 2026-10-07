# Madde 373 (v9-8e) — Negatif prompt — uygulama

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 373 · v9-8e.
**Testler:** [testler spec'i](2026-09-29-queenagent-m373-negatif-prompt-testler-design.md), kırmızı commit
`d0dd9b6b`. Bu spec yalnız o testlerin istediğini yazar.

**Kullanıcıdan gereken:** yok.

## Modele giden metin

### `prompt.THE_CHECKS` — Check 3'ten sonra, kapanıştan önce yeni blok

```
Check 4 -- the negative prompt
- Write one negative prompt for the scenario from its cast as it stands, and give it whole to write_negative: it is rewritten, never added to.
- It keeps one character's features off another, but it works on the whole picture, so never write a character's own feature: dark skin in it turned the man white.
- Write the opposite of that feature instead, in words only its owner fits: pale male, white man for a dark-skinned man. Where that cannot be done, leave it out: the entries keep a feature on its owner.
- It changes no frame. Show the list and wait for their yes.
```

Kullanıcının dersleri sırayla: liste bütün resme işler, kişiye değil *(negatif kişiye özel çalışmaz)*;
karakterin kendi özelliği girmez, örnek kullanıcının yaşadığı *(koyu ten → adam beyaz çıktı)*; yerine
sahibine özel karşıt etiketler *(`pale male`, `white man`)*; yapılamıyorsa yazılmaz, çünkü özelliği
sahibinde tutan pozitif taraf, girdilerdir *(asıl çözüm pozitif tarafta)*. "Yeniden yazılır, eklenmez"
374 içindir: kadro değişince liste kadronun o anki hâlinden baştan yazılır.

### Kapanış

- Önce: `When the checks are done, close by naming the file and saying it is ready.`
- Sonra: `When the checks are done, close by naming the prompt file and the negative file, and saying
  they are ready.`

Arkasındaki cümle (`Do not print the prompts back, offer nothing, and ask nothing: this is the last
word.`) aynı kalır.

### Yeni araç açıklamaları

- `WRITE_NEGATIVE`:
  ```
  Write a scenario's negative prompt into a text file of its own, beside the prompt list.
  - One list for the whole scenario. The file holds the tags and nothing else, so the user can copy it whole.
  - The file is named after the structure, and each call replaces what it wrote last time: give the whole list.
  ```
- `WRITE_NEGATIVE_TAGS`: `The whole negative prompt, as comma-separated tags.`
- `file` parametresi mevcut `THE_STRUCTURES_FILE`'ı kullanır.

## Kod

1. **`build_prompts.py`:** `negative_name(source)` → `<kök>-negative.txt`. Kök `prompts_name` ile
   ortak bir `_stem`'den gelir, ki iki dosya aynı adın yanında dursun.
2. **`tools.py`:**
   - `TOOL_SPECS`'e `build_prompts`'tan sonra `write_negative` (`file`, `tags`, ikisi de zorunlu).
   - `WRITES_FILES`'a `write_negative` — sohbet dosya kartı çizer.
   - `run_tool` → `_write_negative`: yapı dosyası okunamazsa `There is no file by that name.`; etiketler
     boşsa `A negative prompt needs tags.` (`Refused`); yoksa `negative_name(source)`'a etiketleri,
     baştaki ve sondaki boşluk alınmış hâliyle yazar — üstüne yazarak. Cevap `Wrote <dosya>.`,
     `created` dosya, `target` yapı, `outcome` `Written`.
   - `run_tool` docstring'indeki araç sayısı güncellenir ("other eighteen").
3. **`modes.py`:** edit modunun listesine `write_negative`, gerekçesiyle.
4. **`prompt.py`:** `THE_CHECKS`'in docstring'i 373'ün yerini anlatan cümle yerine Check 4'ün
   gerekçesini taşır.

## Tavan

Akış ~1015 kelime (1025 tavan), Improve ~672 (700 tavan). Tavan testi kırmızı commit'te 1025'e çıktı.

## Dokunulmayanlar

Frontend (dosya paneli her dosyayı gösterir, Copy dosyanın tamamını kopyalar), `dist`, queen-editor,
Edit prompts *(374)*.
