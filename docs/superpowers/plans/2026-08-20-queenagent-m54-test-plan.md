# Madde 54 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-20-queenagent-m54-test-design.md](../specs/2026-08-20-queenagent-m54-test-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Dosya

`queen-agent/backend/tests/test_dist_is_committed.py` *(yeni)*

Diğer testlerin yanında duruyor çünkü `pytest queen-agent` onu oradan topluyor. Bir alt sistemi
değil depoyu sınıyor; docstring'i bunu söyler, yoksa yanlış yerde durduğu sanılır.

## Yardımcılar

- `_tracked(path)` — `git ls-files --error-unmatch <path>`, çıkış kodu 0 ise git taşıyor.
  `--error-unmatch` "taşınmıyor"u sıfırdan farklı bir çıkışa çeviriyor, yani sessiz boş cevap yok.
- `_listed(path)` — `git ls-files <dizin>`, taşınan yolların listesi.

İkisi de depo kökünden çalışır; kök, test dosyasının konumundan dört dizin yukarısı.

## Testler

1. **`test_the_built_frontend_is_in_the_repo`**
   `dist/index.html` git tarafından taşınıyor mu. Mesaj Türkçe ve ne yapılacağını söyler.

2. **`test_the_page_asks_for_files_that_were_committed_with_it`**
   `index.html` okunur, `src="/assets/…"` ve `href="/assets/…"` yolları çıkarılır, her biri
   `dist/assets` altında taşınanlar kümesinde aranır. Hiç yol bulunamazsa bu da bir hata: derleme
   bozuk demektir, ve boş bir listeyi "hepsi tamam" saymak testi sessizce işe yaramaz kılar.

## Beklenen kırmızı

**İkisi de kırmızı.** Bugün [queen-agent/.gitignore](../../../queen-agent/.gitignore) `frontend/dist/`
diyerek kökün kuralını pekiştiriyor, yani git hiçbirini taşımıyor.

İkinci test, birincinin düzeltilmesiyle kendiliğinden yeşile dönmez: `dist` yok sayıldığı sürece
`assets` listesi de boş gelir, ve sayfanın istediği iki dosya eksik olarak raporlanır.

## Bu turda yapılmayan

`npm run build` çalıştırılmaz ve `.gitignore`'a dokunulmaz — ikisi de Tur 2'nin işi. Bu tur yalnız
soruyu kurar; cevabı bir sonraki verir.

**Dikkat:** `index.html` şu an çalışma ağacında **yok** (sökme sırasında silindi). İkinci test onu
okumaya çalışıp `FileNotFoundError` ile düşer — bu da bir kırmızıdır ama beklenen kırmızı değil.
O yüzden testler yazılmadan önce bir kere derlenir; derlemek `dist`'i commit'lemek değildir, ve
testin sorduğu soru commit hakkında olduğu için kırmızı korunur.
