# Madde 55 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-20-queenagent-m55-test-design.md](../specs/2026-08-20-queenagent-m55-test-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Dosya

`queen-agent/backend/tests/test_notebook.py` *(yeni)*

Tek dosya, ve 56-57 de buraya eklenecek: yardımcılar bir kere yazılsın, ve "defter ne diyor"
sorusunun tek bir yeri olsun.

## Yardımcılar

- `NOTEBOOK` — `queen-agent/app.ipynb`, test dosyasının konumundan türetilir.
- `_source()` — bütün hücrelerin kaynağı tek metin.
- `_cell(marker)` — içinde `marker` geçen **ilk** hücrenin kaynağı, yoksa `""`.

İkisi de `json.load` ile ayrıştırır. Ham okumak, kaçırılmış tırnak aramak olurdu.

## Testler

1. **`test_the_notebook_is_there_and_parses`** — dosya var ve JSON olarak açılıyor, en az bir hücre.
   Diğer her testin dayandığı zemin; ayrı sorulmazsa hepsi aynı sebeple ve anlaşılmaz biçimde düşer.

2. **`test_drive_is_mounted_before_anything_else`** — CONFIG hücresinde `drive.mount` var, ve
   ondan önceki satırların hepsi `import`, yorum ya da boş. İzin penceresi ilk saniyede çıkmalı.

3. **`test_the_drive_folder_is_named_once`** — `queenAgent` dizesi defterde **tam bir kere** geçiyor
   ve `DRIVE_FOLDER = "queenAgent"` satırında.

4. **`test_an_unmounted_drive_does_not_pass_quietly`** — kök oluşturulduktan sonra `os.path.isdir`
   ile doğrulanıyor. Mount düşerse yazılanlar Colab'ın yerel diskine gider ve runtime ile ölür.

5. **`test_the_token_comes_from_secrets_not_the_source`** — `userdata.get("GITHUB_TOKEN")` var, ve
   defterde `github_pat_` ya da `ghp_` gibi bir token kalıntısı **yok**.

6. **`test_a_missing_token_says_what_to_do`** — `assert GITHUB_TOKEN` var ve mesajı `Secrets` ile
   `GITHUB_TOKEN` kelimelerini taşıyor.

7. **`test_the_xai_key_is_not_asked_for_here`** — `XAI_API_KEY` defterde hiç geçmiyor. Anahtar
   uygulamanın Settings ekranından giriliyor ve Drive'da kalıyor; bu, queen-editor'den bilerek
   ayrılan yer ve testi yoksa biri eksiklik sanıp ekler.

## Beklenen kırmızı

**Altısı: 1-6.** `app.ipynb` diye bir dosya yok — 1 açıkça onu söyler, 2-6 `_source()` boş metin
döndürdüğü için düşer.

**7 bugün yeşil**, ve bu ilk tahminimin düzeltilmesi: boş metinde `XAI_API_KEY` de geçmiyor, yani
test "sorulmuyor" cevabını yanlış sebeple veriyor.

**Sonradan eklenen not (Madde 56'da öğrenildi):** doğuştan yeşil bir test, düşebildiğini
kanıtlamamış bir iddiadır. 56'da aynı kusurdaki iki test, yanlarına o hücrenin **yaptığı işi** soran
birer iddia eklenerek kırmızı hâle getirildi.

Bu test için aynısı yapılamıyor: kural saf bir yokluk — "xAI anahtarı defterde hiç sorulmasın" — ve
karşılığı olan olumlu bir iş yok. Böyle bir şey TDD kırmızısı değil, **kilit**tir: bugün bir şey
kanıtlamaz, yarın birinin queen-editor'e bakıp "burada eksik kalmış" diye eklemesini durdurur.
Kilit olduğu burada yazılı, ki kırmızı görülmüş gibi sayılmasın.

## Bu turda yapılmayan

`app.ipynb` yazılmaz.
