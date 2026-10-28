# Madde 397 — Kutu QueenAgent'ın yeni listesini okur, test turu

**Koşu:** [Queen Editor v8](../roadmaps/2026-09-25-queen-editor-v8-roadmap.md) · **Dal:**
`feat/queen-editor-v8`, Dalga 1 · **Parça:** 397 · v8-3a · **Tur:** 1/2 — yalnız testler, kırmızı
commit'lenir.

**Kullanıcıdan gereken — yok.** Kararlar yol haritasında, *v8-3 — QueenAgent'ın yeni listesi*.

## Bugün ne oluyor

Fotoğraf panelinin *Prompt listesi* kutusu sunucuya metin olarak gidiyor, ve sunucu onu
`parse_prompts`'la okuyor *(`prompt_list.py`)*: yalnız metin listesi. QueenAgent artık her kare için
iki alanlı bir kayıt yazıyor — `scene` ve `photo`, ikisi de üç tırnakta; biçim QueenAgent'ta
`build_prompts.render_module`'de. Kutu bu listeye `Format hatası — liste okunamadı` diyor.

## Kurallar

1. **Yeni liste kartları açıyor.** Her kayıt bir prompt: `photo` fotoğrafın prompt'u, varyant sayısı
   bugünkü gibi çarpıyor. Negatif listeyle gelmiyor — kart paneldeki negatifle üretiliyor.
2. **Karenin senaryosu kartla kalıyor:** kareler API'si *(`GET /api/projects/<p>/frames`)* her kartta
   `scene` alanını veriyor — kaydın `scene`'i, senaryosu olmayan kartta boş metin. Yalnız okunur: onu
   yazan bir kapı yok, bu turda da açılmıyor. 401 onu buradan okuyacak.
3. **Kartın kopyası da aynı senaryoyu taşıyor.** Bir karenin ikinci videosu *(varyant, kopya kare)*,
   *Kopyala*'nın ikizi, *Yeniden üret*'in yeni kelimelerle doğan karesi, ve fotoğrafı silinip videosu
   kalan kart — hepsi aynı karenin resmini taşıyor, ve senaryo o resmin senaryosu. Yol haritası
   "karenin senaryosu kartla birlikte kalır" diyor; 400 her kartın H3 prompt'unu senaryoyu görerek
   yazacak, ve 401 senaryoyu yalnız düz listeden gelen karede *"Bu karenin senaryosu yok"* diye
   gösteriyor.
4. **Eski düz liste bugünkü gibi açılıyor**, ve kartlarının senaryosu yok. Planın satırı bugünkünün
   aynı: `scene` alanı hiç yazılmıyor.
5. **Okunamayan kayıt, okunamayan liste:** iki alandan biri eksik ya da metin değilse, ya da liste
   metinle kaydı karıştırıyorsa, cevap bugünkü tek satır — `Format hatası — liste okunamadı`.
   `photo`'su boş kayıt, düz listenin boş öğesi gibi düşüyor.
6. **Referanstan'ın kutusu değişmiyor.** O kutu video prompt'u okuyor; QueenAgent'ın `photo`'su SDXL
   etiketleri, orada anlamı yok. Madde yalnız fotoğraf panelinin kutusu.

## Yazılacak testler

Testlerin paylaştığı liste, QueenAgent'ın yazdığı biçimde *(`render_module`)* — iki kayıt:

```python
QUEEN_AGENT_LIST = '''PROMPTS = [
    {
        "scene": """Kraliçe tahtında oturuyor; salon boş ve karanlık.""",
        "photo": """score_9_up, 1girl, queen, crown BREAK sitting on a throne, throne room""",
    },
    {
        "scene": """Kraliçe gece bahçede yürüyor, fenerler yanıyor.""",
        "photo": """score_9_up, 1girl, queen BREAK walking, night garden, lanterns""",
    },
]
'''
```

### `test_prompt_list.py` — yeni okuyucu `parse_photo_list`

Fotoğraf panelinin okuyuşu: bir girdi listesi, her girdi `{"prompt": …, "scene": …}`; düz listenin
girdisinde `scene` yok. `parse_prompts` Referanstan için bugünkü gibi kalıyor. Testler fonksiyonu
modülün üstünden çağırıyor *(`prompt_list.parse_photo_list`)*: kırmızı koşuda eksik bir isim
toplamayı durdurmasın, her test kendi yerinde düşsün.

1. **QueenAgent'ın listesi her kareye fotoğraf prompt'unu ve senaryosunu veriyor** —
   `QUEEN_AGENT_LIST` → iki girdi, `prompt` = `photo`, `scene` = `scene`.
2. **Düz liste bugünkü gibi okunuyor ve senaryo taşımıyor** — `PROMPTS = ["a", "", "b"]` →
   `[{"prompt": "a"}, {"prompt": "b"}]`.
3. **Okunamayan kayıtlı liste aynı tek satırı alıyor** *(parametreli)* — `[{"photo": "a"}]`,
   `[{"scene": "s"}]`, `[{"scene": "s", "photo": 3}]`, `["a", {"scene": "s", "photo": "p"}]`,
   `{"scene": "s", "photo": "p"}` → `Format hatası — liste okunamadı`.
4. **`photo`'su boş kayıt, boş öğe gibi düşüyor** —
   `[{"scene": "s", "photo": "a"}, {"scene": "t", "photo": "  "}]` → `[{"prompt": "a", "scene": "s"}]`.

### `test_photo_routes.py` — gerçek Drive depolarıyla, uçtan uca

5. **QueenAgent'ın listesi kartları açıyor** — `QUEEN_AGENT_LIST`, 1 varyant: 202, `added` 2, üretici
   iki `photo`'yu paneldeki `blurry` negatifiyle alıyor.
6. **Kareler API'si her kartın senaryosunu veriyor** — `P0_0` birinci, `P1_0` ikinci kaydın `scene`'i.
7. **Düz listenin kartının senaryosu boş** — `["a"]` → `P0_0`'ın `scene`'i `""`.
8. **Videonun varyantı kopyalandığı karenin senaryosunu taşıyor** — tek kayıtlı liste, video 2 varyant:
   `P0_1`'in `scene`'i kaydınki.
9. **İkiz kaynağının senaryosunu taşıyor** — `P0_0` kopyalanıyor: `C1_P0_0`'ın `scene`'i kaydınki.
10. **Yeni kelimelerle yeniden üretilen kare senaryoyu taşıyor** — `P0_0`'ın fotoğrafı `başka` ile:
    `P1_0`'ın `scene`'i kaydınki.
11. **Fotoğrafı silinen kart senaryosunu taşıyor** — `P0_0`'a video veriliyor, fotoğraf katmanı
    siliniyor: kalan kartın `scene`'i kaydınki.

**Değişen:** `test_photo_usecases.py` — `plan_frames` artık metin değil girdi alıyor:

- `test_plan_frames_is_prompt_major`: `["ilk", "ikinci"]` yerine
  `[{"prompt": "ilk"}, {"prompt": "ikinci"}]`; beklenen satırlar aynı, `scene` alanı olmadan. Düz
  listenin planının bugünkü gibi kaldığının bekçisi bu.
- `test_a_planned_frame_carries_the_lora_it_was_submitted_under`: `["kraliçe"]` yerine
  `[{"prompt": "kraliçe"}]`.

**Bekçiler:** `test_prompt_list.py`'nin bugünkü testleri *(`parse_prompts`, iki cümle)*;
`test_a_reference_run_reads_the_prompt_list_the_way_the_photo_panel_does` *(Referanstan hâlâ
`gotik kız`'ı reddediyor)*; düz listeyle koşan bütün `start_batch` testleri ve rotalar —
`test_unreadable_prompt_list_returns_400`, `test_a_refused_batch_answers_with_the_error_alone`,
`test_progress_is_reported_before_each_frame` *(koşan işin satırı bugünkünün aynı)*.

**Ekran:** değişmiyor, test yok. Fotoğraf paneli kutuyu metin olarak gönderiyor ve reddi sunucudan
alıyor; senaryoyu gösteren 401.

## Bitti sayılır

Dört test satırı koşulur. `queen-editor` pytest'inde 1–11 ve `test_plan_frames_is_prompt_major`
kırmızı, doğru sebeple: `parse_photo_list` yok, rota yeni listeye `Format hatası` diyor, kartta
`scene` yok, `plan_frames` girdiyi metin sanıyor. Lora testi girdisi değişse de yeşil kalıyor
*(yalnız modele ve loraya bakıyor)*. `queen-agent`'ın iki satırı ve `queen-editor` vitest'i yeşil.
