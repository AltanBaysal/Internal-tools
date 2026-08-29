# Madde 131 · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-08-29-queenagent-m131-satir-numarasi-uygulama-design.md](../specs/2026-08-29-queenagent-m131-satir-numarasi-uygulama-design.md)

## A. `tools.py`: `numbered()` doğar; `read_file` onu kullanır, `outcome` ham satırları saymaya devam eder.

## B. `tools.py`: `edit_file`'ın açıklaması numaraların atılacağını söyler.

## C. `stream_answer.py`: `_boxed`'ın dosya blokları numaralı, şema bloğu ham.

## D. İki komut koşuldu. Beş kırmızı döndü, beş bekçi yeşil kaldı — ama üç test daha kırıldı.

`test_creating_over_a_name_that_is_taken_writes_nothing`,
`test_a_plan_is_written_under_a_name_that_says_it_is_one` ve `test_writing_a_plan_again_replaces_it`
diskte ne yazdığını **`read_file` üzerinden** soruyorlardı, ve araç artık numaralı bir görünüm
döndürüyor. Üçünün de konusu okuma değil — biri `create_file`'ın üstüne yazmaması, ikisi planın
adı ve değiştirilmesi. Üçü de store'a doğrudan soracak şekilde düzeltildi *(`files.read`)*, yani
zayıflatılmadılar: sordukları şeyi artık aracın biçiminden geçmeden soruyorlar.

**Bu üçü test turunda görülmeliydi.** Kaçtılar çünkü tur, davranışı değişen yerleri aradı ve
`read_file`'ı bir yardımcı gibi kullanan yerleri taramadı. Kayıt burada duruyor.

## E. İki komut yeniden koşuldu: 612 yeşil, defter çifti bilinen kırmızı, frontend 568 yeşil.

## F. Yeşil commit.

## Bilerek yapılmayanlar: şema branch'i, `_edit`'in eşleşmesi, disk şeması, `dist` (ön yüz değişmiyor).
