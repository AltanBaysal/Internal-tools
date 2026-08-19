# Madde 59 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-20-queenagent-m59-test-design.md](../specs/2026-08-20-queenagent-m59-test-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Dosya

`queen-agent/backend/tests/test_store.py` — üç test eklenir, mevcutlara dokunulmaz.

## Testler

**1. `test_a_failed_write_leaves_the_old_file_alone`**
`a.txt`'ye `"body"` yazılır. Sonra `"\ud800"` yazılmaya çalışılır, `UnicodeEncodeError` beklenir.
Ardından `read_text("a.txt")` hâlâ `"body"` vermelidir.

**2. `test_a_failed_write_leaves_nothing_behind`**
Aynı düşen yazmadan sonra kökteki dosya listesi yalnız `a.txt` olmalı — yarım bir geçici dosya
kalmamalı. Başarılı bir yazmadan sonra da aynı liste beklenir, yani kural iki yol için de geçerli.

**3. `test_the_temporary_file_is_written_beside_its_target`**
`os.replace` monkeypatch ile sarılır, aldığı iki yol yakalanır, gerçeği çağrılır. `dirname(src)`
ile `dirname(dst)` eşit olmalı. Sebep tasarımda: `os.replace` dosya sistemi geçemez ve Colab'da kök
Drive, `/tmp` yerel disk.

## Beklenen kırmızı

**1 ve 2 kırmızı.** Bugün `open(..., "w")` dosyayı açar açmaz siliyor: 1'de `a.txt` boş kalır, 2'de
boş bir `a.txt` kalır — aslında 2 bugün de geçebilir, çünkü bugün *fazladan* bir dosya yok.

Bu ayrım önemli: **2 bugün yeşil**, ve kuralı ileriye dönük tutuyor — yarın geçici dosya eklendiğinde
temizlenmezse kırmızıya döner. Yeşil doğduğu planda yazılı olsun ki, kırmızı görülmedi diye
atlandığı sanılmasın.

**3 kırmızı**, çünkü bugün `os.replace` yazma yolunda hiç çağrılmıyor — yakalanan çağrı sayısı sıfır
kalır.

## Bu turda yapılmayan

`store.py`'ye dokunulmaz.
