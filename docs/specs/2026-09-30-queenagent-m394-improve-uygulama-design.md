# Madde 394 — Improve: ayrı bir skill olarak hazır senaryoyu kontrol eder · uygulama turu

**Kaynak:** [yol haritasının 394'ü](../roadmaps/2026-09-25-queen-agent-v9-roadmap.md), ve
[test turunun spec'i](2026-09-30-queenagent-m394-improve-testler-design.md). Test turu kırmızı commit'lendi
(`5e5c73b5`): arka uçta 17, ön uçta 3 test Improve'u bekliyor.

**Kullanıcıdan gereken:** hiçbir şey. Metin kullanıcıyla satır satır yazıldı ve `prompt.py`'de `IMPROVE` olarak
duruyor; seçicideki satırın sözü verildi.

**Kapsam dışı:** `IMPROVE`, `START_A_SCENARIO`, `EDIT_PROMPTS`'un tek kelimesi. Başka bir metin, araç ya da
akış. Yol haritası, BACKLOG, `tmp/`.

## Ne yapılır

1. **Kayıt** — [skills.py](../../queen-agent/backend/features/workspace/domain/skills.py)'de
   `INSTRUCTIONS`'a `"improve": prompt.IMPROVE`, öteki ikisinin arkasına. `instruction_for` değişmez: seçilen
   skill'in metni zaten bu tablodan okunur, ve `stream_answer` onu turun sonuna koyar. Bitti ölçütünün
   *"seçilince modele Improve'un metni gidiyor"* yarısı budur.
2. **Seçicinin satırı** — [skills.js](../../queen-agent/frontend/src/features/workspace/skills.js)'te
   `SKILLS`'e üçüncü ve son satır:
   `{ id: "improve", name: "Improve", detail: "Check a scenario you already have, fix what fails, and write its negative list again." }`.
   `SkillPicker` satırları `SKILLS`'ten kurar; başka bir bileşen değişmez. Kimlik `improve`, arka ucun tablosuyla
   aynı söz — `test_skills.py`'nin `ALL_SKILLS`'i ikisini yan yana tutar.
3. **Yorumlar, yalnız bugün doğru olanı söylesin diye** — üç yer iki skill sayıyor:
   - `prompt.py`'de skill metinlerinin üstündeki *"Two texts since Madde 101"*: üç metin. Improve'un metninin
     Start a scenario'nun adımlarının kopyası olması **neden**iyle yazılır — kullanıcının kararı, var olan bir
     senaryo için ayrı bir skill —, çünkü kopyayı gören bir okur onu hata sanıp birleştirmek ister; bir yorum
     kodun söyleyemediğini söyler.
   - `skills.py`'nin docstring'indeki *"Two texts since Madde 101"*: üç metin.
   - `skills.js`'in başındaki *"Two rows since Madde 101"*: üç satır; Improve'un en sonda durduğu, flow'un
     bitirmek için ikinci bir satıra ihtiyaç bırakmadığı cümlesiyle çelişmesin diye Improve'un o ikinci satır
     olmadığı — var olan bir senaryoda flow'un kontrollerini yeniden koşar —, ve satırın sözünün tasarımınkinden
     neden ayrıldığı: tasarımın yer tutucusu her adımdan sonra bir *evet* istiyordu, Improve'un adımları hiçbir
     onay beklemez. Tasarım QueenAgent'ta görsel şartname (CODE-STANDARD); ondan ayrılan bir söz, geri
     "düzeltilmesin" diye yazılır.
4. **Derleme** — `npm run build --prefix queen-agent/frontend`; `dist` kaynakla **aynı** commit'te
   (FOUNDATION, Karar 3).

Metin sabitleri yorum dışında değişmez; `prompt.py`'nin bu turdaki farkı `IMPROVE`'un kendisi ve bir yorum
paragrafıdır.

## Neden bu kadar

- Kayıt bir sözlük satırı: skill'lerin tamamı böyle bağlanıyor, ve yeni bir katman ya da seçenek gerekmiyor
  (FOUNDATION, İlke 3).
- Sıra: Improve en sonda — yol haritasının bitti ölçütü *"seçicide Edit prompts'tan sonra `Improve` var"*.
  Öndeki iki satırın yeri değişmez.
- Ön uç yalnız bir görünüm (FOUNDATION, Karar 4): satırın sözü ön uçta, metin ve eşleme arka uçta; ikisini
  bağlayan tek şey `improve` kimliği.

## Nasıl görülür

CLAUDE.md'deki dört satır, yazıldığı gibi, paralel; iki `npm` satırı arka planda. Hepsi yeşil: test turunun
kırmızı 17 + 3 testi dahil. Kelime tavanı (1480) gerçek metni tutar; test turundaki el sayımı 1463.

Commit: `prompt.py` (`IMPROVE` ve yorum), `skills.py`, `skills.js`, `dist`, bu spec ve planı. Ön uç testleri
kırmızı commit'te zaten var.

Tarayıcıda bakmak bu turun işi değil — çağıran oturum kendisi bakar; kullanıcı roadmap'in sonunda dener.

Adım adım dökümü [uygulama turunun planında](../plans/2026-09-30-queenagent-m394-improve-uygulama-plan.md).
