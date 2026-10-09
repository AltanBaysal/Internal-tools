# Madde 94 — Tek skill kalır, beşi silinir · **uygulama turu**

**Tarih:** 2026-08-27 · **Branch:** `feat/queenagent-v5` ·
**Test turu:** [testler tasarımı](2026-08-27-queenagent-m94-tek-skill-testler-design.md) · kırmızı commit `5173366`
**Tur:** ikiden ikincisi — bu belge **yalnız kodu** tarif eder. Yeni test yazılmaz.

---

## İki dosya

`domain/skills.py` ve `features/workspace/skills.js`. Başka hiçbir şey açılmıyor.

Seçicinin kendisi, `skill` alanı, kaydın `skill`'i, `stream_answer`'ın yönergeyi sona koyuşu:
hepsi olduğu gibi kalıyor. Bu madde bir liste kısaltıyor, bir yol değiştirmiyor.

## `skills.py`

Beş sabit ve `INSTRUCTIONS`'ın beş satırı gidiyor:

| Sabit | Anahtar |
|---|---|
| `CREATE_SCENARIO` | `create-scenario` |
| `CREATE_CHARACTER_PROMPT` | `create-character-prompt` |
| `SPLIT_INTO_FRAMES` | `split-into-frames` |
| `GENERATE_PROMPTS` | `generate-prompts` |
| `VERIFY_PROMPTS` | `verify-prompts` |

`RULEBOOK` ve `GENERATE_PROMPTS_PLUS` **tek kelimesi değişmeden** kalıyor. `instruction_for` da:
bilinmeyen ada boş dönmesi zaten silinen adların yeni yolu.

### Yalan olan iki yorum

Bir yorum yalnız bugün doğru olanı söyler, ve bu ikisi bugün doğru olmaktan çıkıyor.

`RULEBOOK`'un üstündeki *"One text, two readers"* — ikinci okuyucu gitti. Yerine geçen, aynı şeyi
söyleyen ama sayısı doğru olan cümle: metin tek, uygulandığı an kurma anı, ve kural kitabının ayrı
bir sabit kalmasının sebebi artık iki okuyucu değil — kuralların yönergenin gövdesinden ayrı
durması, hangi cümlenin bir kural olduğunu tek yerde gösteriyor.

Modül docstring'indeki *"the two skills that produce those say so in as many words"* — tek metin.

### Docstring'e giren cümle

Dosya artık bir listeyi değil bir metni taşıyor, ve bunun neden böyle olduğu koddan okunmaz:

```
One text since Madde 94. Five others stood here and were deleted: what they said about how to work
now sits in prompt.py, where it holds whatever is selected, and what they said about their own task
either lives in the text below or went with them on purpose. The picker still exists and still has
an empty state -- having no skill selected is ordinary, and the list will grow again.
```

## `skills.js`

`SKILLS` beş satırını bırakıyor. Kalan satır — id, ad, alt satır — değişmiyor.

Üstündeki yorum *"The six skills, settled with the user on 2026-08-18"* diyor ve artık altı değil.
Yerine geçen, tarihi koruyup sayıyı düzelten ve bir satırın niye kaldığını söyleyen bir yorum: menü
boş değil çünkü skill seçmemek olağan bir hâl ve tek satırlık bir liste bile iki durum taşıyor.

`skillName`'in `?? id` kolu duruyor, ve ilk gerçek kullanıcısını buluyor: silinen bir adı taşıyan
eski bir kayıt açıldığında düğme boş kalmıyor, id'yi yazıyor.

## Dokuz kırmızının hangi silmeyle yeşile döndüğü

| Test | Karşılığı |
|---|---|
| `test_a_deleted_skill_carries_nothing` × 5 | `INSTRUCTIONS`'tan beş satır |
| `test_only_one_skill_is_offered` | aynı beş satır |
| `test_the_rulebook_has_one_reader_now` | `VERIFY_PROMPTS`'un kendisi |
| `the one skill left is the one that builds` | `SKILLS`'ten beş satır |
| `a deleted skill keeps its id on the screen` | aynı beş satır — `skillName` `?? id` koluna düşüyor |

## Yeşil kalması gerekenler

`generate-prompts-plus` ve `RULEBOOK`'un bütün testleri: iki metnin tek kelimesi değişmiyor.
`test_no_instruction_calls_a_frame_a_shot` tek metin üzerinde dönüyor ve o metin zaten temiz.
Ön yüzde seçicinin, iki ekranın ve `App`'in bütün testleri: hiçbiri açılmıyor.

## Nasıl yeşil görülür

```
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**İki kırmızı bu maddenin değildir:** `test_notebook`'un ikisi.

`dist` **derleniyor**: `skills.js` bir ön yüz kaynağı, ve CLAUDE.md derlenmiş çıktının kaynakla aynı
commit'te inmesini istiyor — defter tarafında derlenmeyen bir değişiklik görülmez.

## Bilerek yapılmayanlar

- **Yeni test yazılmaz.**
- **`prompt.py` açılmaz** — 73 bitti, taban olduğu gibi kalıyor.
- **`GENERATE_PROMPTS_PLUS` düzenlenmez** — kullanıcı kararı, 27 Ağustos: kalan metin bugünkü
  hâliyle kalıyor.
- **Seçici sökülmez.**
- **Eski kayıtlar dönüştürülmez** — diskteki `skill` alanı olduğu gibi kalıyor ve okunmaya devam
  ediyor; artık kimsenin tanımadığı bir ad taşıyor, o kadar.
