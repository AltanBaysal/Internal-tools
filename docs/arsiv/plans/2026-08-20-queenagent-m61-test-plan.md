# Madde 61 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-20-queenagent-m61-test-design.md](../specs/2026-08-20-queenagent-m61-test-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Değişiklik

`queen-agent/backend/tests/test_notebook.py` — `NOTEBOOK` sabitindeki dosya adı
`"app.ipynb"` → `"queenagent.ipynb"`. Dosyanın başındaki docstring de yeni adı anıyor.

Yeni test **eklenmiyor**. Adın doğruluğunu tutan şey zaten var: `test_the_notebook_is_there_and_parses`
dosyanın orada olduğunu soruyor, ve sabit değişince o soru yeni ada soruluyor.

## Beklenen kırmızı

**Yirmi iki defter testinin yirmi biri.** Hepsi aynı dosyayı okuyor; sabit yeni adı gösterince
hiçbiri dosyayı bulamıyor. *(Plan önce "on beşin on beşi" diyordu — testler yanlış sayılmıştı.)*

Bu kadar çok testin tek satırdan düşmesi doğru: adlandırma bütün defter testlerinin dayandığı
zemin, ve zemin kayınca hepsinin bunu söylemesi gerekiyor. `test_the_notebook_is_there_and_parses`
sebebi açıkça yazıyor, diğerleri boş metin üzerinden düşüyor — o test tam bunun için ayrı duruyordu.

**Düşmeyen bir tane var:** `test_the_xai_key_is_not_asked_for_here`. Boş metinde `XAI_API_KEY` de
geçmiyor, yani yine yanlış sebeple yeşil. Bu, Madde 55'te **kilit** olduğunu söylediğimiz testin
kanıtı: saf bir yokluk iddiası zemin kayınca bile düşmüyor, çünkü hiçbir zaman bir şeyin varlığına
dayanmıyordu.

## Bu turda yapılmayan

Dosya yeniden adlandırılmaz. Roadmap'e dokunulmaz.
