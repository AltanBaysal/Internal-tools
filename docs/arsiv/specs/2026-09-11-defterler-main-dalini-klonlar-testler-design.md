# Defterler `main` dalını klonlar — TEST turu spec'i

**Kaynak:** `main` üzerindeki iki defterin CONFIG hücresi. Bu belge onlardan çıkar, tersi değil.

## Problem

`main`'deki her iki defter de kendi feature dalını klonluyor:

| Defter | `BRANCH` | O iş `main`'e indi mi |
|---|---|---|
| `queen-agent/queenagent.ipynb` | `feat/queenagent-v8` | indi (`356d605` merge commit'i) |
| `queen-editor/queeneditor.ipynb` | `feat/v6` | indi (üç grafik de `main`'de) |

İkisi de bir deneme turu için değiştirilmiş ve tur kapanınca geri alınmamış. Defterler bugün
çalışıyor, çünkü dallar hâlâ duruyor; silindikleri gün klon hücresi git'in "remote branch not found"
cümlesiyle düşer ve o cümle satırın ne zaman eskidiğini söylemez. Daha kötüsü: kullanıcı `main`'in
defterini açtığında `main`'in kodunu değil, o dalın kodunu servis eder.

queen-agent'ta dalı tutan bir muhafız var (`backend/tests/test_notebook.py`), ama sabiti de
`feat/queenagent-v8` olduğu için takım yeşil — iki yer birlikte eskidi. queen-editor'de dalı tutan
hiçbir test yok.

## Bu turun kapsamı

Kırmızı bırakılacak testler. Defterlere ve koda **dokunulmaz** — onlar bir sonraki turun işi.

### A — queen-agent: muhafızın sabiti

**A1.** `test_notebook.py`'deki `BRANCH` sabiti `"main"` olur.

Mevcut iki test bundan kendiliğinden kırmızıya döner:
- `test_the_notebook_clones_the_branch_this_run_is_tried_on` — defter `main`'i klonlamıyor.
- `test_no_other_branch_name_is_left_lying_in_the_notebook` — defterde `feat/queenagent-v8` duruyor.

Yeni test yazılmaz: sorulacak soru zaten sorulmuş, yanlış cevap doğru sayılıyordu.

### B — queen-editor: muhafızın eşi

Yeni dosya, yalnız bu soruyu soran: defter hangi dalı klonluyor.

**B1.** Defter `BRANCH       = "main"` satırını taşır.
**B2.** Defterin hiçbir hücresinde başka bir `feat/...` dal adı kalmamıştır.

İkisi de düşer: defterde `BRANCH       = "feat/v6"` yazıyor.

### Nereye yazılır

queen-editor'ün mevcut defter testi dosyası `test_notebook_installs_the_producer_groups.py` — adı
üreticileri vaat ediyor, dal onun işi değil. Dal muhafızı kendi dosyasında durur:
`queen-editor/backend/tests/test_notebook_clones_its_branch.py`.

O dosya tek yardımcı taşır (`_source()` — bütün hücrelerin kaynağı, JSON olarak ayrıştırılmış).
Komşu dosyanın üç yardımcısı kopyalanmaz: bu iki soru hücre ayırt etmiyor, ikisi de metnin tamamına
bakıyor.

## Bilerek yapılmayan

- **`main`'deyken `feat/` adını düşüren test yok.** Seçim 1 buydu: delik açık kalıyor — bir sonraki
  turun unutulan geri dönüşü yine sessiz geçecek. Muhafızlar satırın *ne olduğunu* tutuyor, *ne
  zaman yanlış olduğunu* değil.
- **Dal adı iki yerde kalıyor** (sabit + defter) — ikisinin ayrıldığı an testin düştüğü an, ve
  kopyanın bedeli bu yüzden ödeniyor.
- Testler metin okuyor, defteri çalıştırmıyor: Colab hücresi pytest içinde çalışmaz. Bu muhafızın
  işi, dal adının sessizce eskimesini engellemek.
