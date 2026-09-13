# Madde 210 · QueenAgent'ın dalları — test turunun planı

**Spec:** [test turu](../specs/2026-09-13-queen-editor-m210-queenagent-dallari-testler-design.md) ·
**Madde:** [v5 yol haritası](../roadmaps/2026-09-11-queen-editor-v5-roadmap.md)

Bu tur **yalnız testleri** koyar. v2 ile v3'ün birleşmesi, v8'in dal satırı ve v7'nin ikinci dalı
uygulama turunda düzelir.

## Adımlar

**1 · `_roadmaps()` iki tool'a açılır.** Bugün `*queen-editor-v*-roadmap.md` süzüyor; `*-roadmap.md`
olur ve dosya adını `SHAPE` ile çözüp *(tool, sürüm)* döndürür. `NAMED` sabiti kalkar — `SHAPE` zaten
hem tool'u hem sürümü veriyor, ve iki ayrı yerden ad çözmek ikisinin ayrışması demek.

Dönen şey `(ad, tool, sürüm)` üçlüsü olsun; üç çivi de aynı listeden okusun.

**2 · `_branch_in_header()` yerine `_declared_branch()`.** Eski helper ilk 8 satırda
`feat/queen-editor-v(\d+)` arıyordu. Yenisi:

- dosyadaki **ilk** `**Branch:**` / `**Dal:**` / `**Koşu dalı:**` satırını bulur *(birleştirilmiş
  belgeler etiketi her `Koşu N` bölümünde tekrar ediyor — ilk olan belgenin kendisinindir)*;
- o satırdaki **ilk** `` `feat/…` `` ya da `` `fix/…` `` backtick'li adı döndürür *(queen-agent v1'in
  5. satırındaki `fix/mira`, adın değişmesini anlatan notun içinde — etikete bakmayan bir okuma onu
  dal sanar)*;
- etiket yoksa `None`.

Satır sonundaki ikinci dal okunmaz: ya *"üzerinden açıldı"* ya da sürümün yayıldığı ikinci daldır, ve
ikisi de sahiplenme değildir.

**3 · Üç çivi yazılır**, eski `test_the_name_says_the_branch_the_roadmap_ran_on`'un yerine:

| Test | Ne diyor | Beklenen |
|---|---|---|
| `test_every_roadmap_says_which_branch_it_ran_on` | her belge bir dal veriyor | **kırmızı** — v8 |
| `test_no_branch_is_claimed_by_two_roadmaps` | dal → belge eşlemesi bire bir | **kırmızı** — `fix/mira` |
| `test_a_numbered_branch_agrees_with_the_name` | dal adındaki `v<N>` ile dosya adındaki aynı | yeşil |

Üçüncüsü dal adının sonundaki `v(\d+)` ile bakar. `feat/queenagent-v7.5` gibi ondalıklı bir ad birinci
dal olarak hiç geçmiyor, ama geçerse muaf sayılır — `7.5` bir dosya adında duramaz, ve orada tutulacak
bir çelişki yok. Numara taşımayan dallar *(`fix/mira`, `feat/queenagent-colab`)* muaf.

**4 · `test_one_version_has_one_roadmap` tool'a göre gruplanır.** Bugün yalnız queen-editor'ün
numaralarını sayıyor; `(tool, sürüm)` çiftine bakar olur. Yeşil kalır — QueenAgent'ta aynı numarayı
iki belge taşımıyor, iki belge aynı **dalı** taşıyor, ki o 2 numaralı çivinin işi.

**5 · Takım koşulur** ve kırmızı **gözle okunur**: iki test düşecek, mesajları v8'i ve `fix/mira`'yı
adıyla söyleyecek. Başka bir test düşerse okuma yanlıştır, belge değil — çivi düzelir.

```
python -m pytest queen-editor -q
npm test --prefix queen-editor/frontend
python -m pytest queen-agent -q
npm test --prefix queen-agent/frontend
```

**6 · Kırmızı commit'lenir.** Belgelere bu turda dokunulmuyor.

## Değişen dosya

`queen-editor/backend/tests/test_version_record.py` — modül başlığı da büyüyor: dosya artık tek
tool'un değil, kaydın kendisinin sorusunu soruyor.
