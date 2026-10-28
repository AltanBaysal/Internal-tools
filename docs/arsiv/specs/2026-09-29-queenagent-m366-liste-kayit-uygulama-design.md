# Madde 366 (v9-7a) — Liste yeni biçimde çıkar: uygulama

**Madde:** [QueenAgent v9](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), 366 · v9-7a.
**Testler:** [testler spec'i](2026-09-29-queenagent-m366-liste-kayit-testler-design.md), kırmızı
commit `60fe9e35`.

## Yaklaşımlar

1. **`build_prompts` kayıt döndürür** *(seçilen)*. Karelerin listesini — `frames`, eski dosyada
   `shots` — okuyan tek yer zaten o; sahne karenin öteki alanlarıyla aynı döngüde okunur. Değişen tek
   satır, karenin eklendiği satır.
2. `_build` (tools.py) sahneleri kendisi toplar, prompt'larla yan yana koyar. Reddedildi: karelerin
   listesini ikinci bir yer okur, ve `shots` yedeği orada da yazılmak zorunda kalır — FOUNDATION'ın
   5. ilkesi ve CODE-STANDARD'ın "hiçbir dosya ötekinin cevabını tekrarlamaz"ı aynı şeyi söylüyor.
3. Yeni bir `build_list` fonksiyonu `build_prompts`'u sarar. Reddedildi: kimsenin istemediği bir parça
   daha; `build_prompts`'un tek çağıranı `_build`.

## Değişenler

**`queen-agent/backend/features/workspace/domain/build_prompts.py`**

- `build_prompts` her kare için `{"scene": frame.get("scene", ""), "photo": <bugünkü prompt>}`
  döndürür. Sahne yazıldığı gibi gider; yoksa boş.
- `render_module(records)` her kaydı dört satırla yazar: `{`, `"scene": """…""",`,
  `"photo": """…""",`, `},` — değerler bugünkü `_quoted` ile kaçırılır, yani tırnak ve ters bölü
  iki alanda da güvende.
- Modülün ve iki fonksiyonun docstring'leri bugünkü hâle göre düzelir ("strings" artık doğru değil).

**`queen-agent/backend/features/workspace/domain/tools.py`** — `_build` değişmez: kayıt sayısı kare
sayısı, cevap yine `Wrote N prompts to x.py.`

**`queen-agent/backend/features/workspace/domain/prompt.py`** — modele giden tek değişiklik,
`BUILD_PROMPTS`'un ilk satırı:

- Önce: `Build the prompt list from a structure file.`
- Sonra: `Build the prompt list from a structure file: for each frame, its scene sentence and its prompt.`

Skill metinleri (Start a scenario, Edit prompts) değişmez; kelime tavanlarına dokunulmaz.

## Dokunulmayanlar

- Frontend: dosya panelinin `Copy`'si dosyanın tamamını kopyalar *(Madde 193)*; `dist` yok.
- queen-editor: listeyi okumak v8-3a'nın işi.
- Negatif liste: v9-8e.

## Queen Editor v8-3a ile uyum

Dosya `PROMPTS = [` ile başlar; queen-editor'ün okuyucusu `PROMPTS =`'yi atıp `ast.literal_eval`
yapıyor, ve sözlük de bir literal. v8-3a'nın beklediği "her kare iki alanlı bir kayıt — `scene` ve
`photo`" tam bu. Bugünkü okuyucu bu listeye "Format hatası" der — roadmap bunu biliyor: v8-3a önce
main'e girer.
