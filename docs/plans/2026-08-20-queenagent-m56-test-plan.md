# Madde 56 · Tur 1 (test) — Plan

**Tasarım:** [2026-08-20-queenagent-m56-test-design.md](../specs/2026-08-20-queenagent-m56-test-design.md)
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`

---

## Dosya

`queen-agent/backend/tests/test_notebook.py` — Madde 55'in yardımcılarının altına eklenir. Yeni
dosya açılmaz: aynı defteri okuyan iki dosya, iki `_source` demek olurdu.

Hücre işareti: `CLONE = "# === Clone ==="`.

## Testler

1. **`test_the_clone_deletes_and_starts_again`** — `shutil.rmtree` var, `git pull` **yok**.
   Harcanabilir bir ağaç, tek davranış.

2. **`test_the_token_never_reaches_the_shell`** — defterde hiç `shell=True` yok. Kabuğa giren bir
   URL kabuk geçmişine ve log satırlarına düşer.

3. **`test_the_clone_url_is_never_printed`** — `clone_url` bir `print` ya da f-string çıktısının
   içinde geçmiyor. Token'ı taşıyan tek dize o.

4. **`test_a_failed_clone_shows_git_own_words_masked`** — hata yolunda git'in stderr'i basılıyor ve
   bir maskeleme fonksiyonundan geçiyor.

5. **`test_flask_is_installed_rather_than_assumed`** — `pip install` satırında `flask` geçiyor.

6. **`test_the_built_frontend_is_looked_for_after_the_clone`** — klon hücresinde
   `frontend/dist/index.html` aranıyor ve bulunamazsa duruluyor.

7. **`test_the_clone_cell_refuses_to_run_before_config`** — `assert "CLONE_DIR" in globals()`.

## Beklenen kırmızı

**Yedisi de.** Klon hücresi henüz yok.

### İlk yazımın kusuru, ve düzeltilmesi

Testler önce şöyleydi: 2 yalnız `shell=True` **yokluğunu**, 3 yalnız basılan satırların içinde
`clone_url` **geçmediğini** soruyordu. İkisi de doğuştan yeşildi — biri defterde `subprocess` hiç
olmadığı için, diğeri boş bir hücrede dönecek satır olmadığı için.

Plana "yanlış sebeple yeşil" diye not düşülmüştü. **Bu yeterli değil.** Doğuştan yeşil bir test,
düşebildiğini kanıtlamamış bir iddiadır; kuralı uygulamak değil, etrafından dolaşmaktır.

Her ikisine de bugün düşen bir **olumlu** iddia eklendi:
- 2 artık klonun bir argüman listesiyle çalıştırıldığını da soruyor — yokluk iddiası onun yanında
  duruyor.
- 3 artık hücrenin bir şey **söylemesini** de şart koşuyor; boş listenin üstünden atlayıp geçmiyor.

Kural olarak: bir yokluk iddiası tek başına test değildir, yanına o hücrenin yaptığı işi soran bir
iddia gerekir.

## Bu turda yapılmayan

Deftere dokunulmaz.
