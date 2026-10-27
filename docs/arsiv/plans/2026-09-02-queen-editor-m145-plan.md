# Madde 145 — Plan

**Tasarım:** [2026-09-02-queen-editor-m145-form-sadelesir-design.md](../specs/2026-09-02-queen-editor-m145-form-sadelesir-design.md)
**Dal:** `feat/v6` · **Önceki commit:** `cb6d190`
**Test komutları (değişmez, ikisi de):**
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## Bu madde tek turda koşuldu, ve sebebi kayda geçiyor

CLAUDE.md her işi iki tam tur istiyor — önce yalnız testler, kırmızı commit, sonra kod. Burada
**kullanıcı bilerek başka türlü seçti** *(2 Eylül)*: kendisine üç şık sunuldu, ikinci şıkkı seçti —
*"ikinci turun spec'i ve planı yazılmaz; defteri düzeltip tek yeşil commit"*.

**Kuralın koruduğu sıra yine de korundu:** test önce yazıldı, eski hücreye karşı koşuldu ve
kırmızı görüldü; defter ondan sonra ellendi. Testin kodun körlüğünü miras alması bu yüzden mümkün
değildi. Eksik olan tek şey **kırmızının kendi commit'i** — yani altı ay sonra `git log`'a bakan
biri o kırmızıyı göremeyecek, aşağıdaki kayıttan okuyacak.

## A. Test değişti.

`test_the_form_says_which_model_each_box_installs` silindi — tarif ettiği karar değişti, ve o test
dururken defter değiştirilemezdi.

Yerine `test_the_form_leaves_the_model_section_at_its_heading` geldi; kodu ve gerekçesi tasarımda.
Yeri, aynı ayraca bakan `test_the_form_separates_the_two_groups_of_boxes`'ın hemen altı: biri
ayracın **önde** olduğunu, öteki **arkasında ne kaldığını** söylüyor.

## B. Kırmızı görüldü: **1 kırmızı, 738 yeşil.**

`python -m pytest queen-editor -q`, defter ellenmeden önce:

```
AssertionError: Model bölümü başlıktan ibaret değil: ['#@markdown ---',
'#@markdown ### Fotoğraf modelleri', '#@markdown Hepsi boş gelir — …',
'#@markdown Grubun ortak dosyaları ~2 GiB; …', '#@markdown - **nova3DCG** — 3DCG / 2.5D',
'#@markdown - **novaOrange** — detaylı tenli anime', '#@markdown - **novaAnime** — anime']
Left contains 5 more items
```

Tam beklenen sebep: kuyrukta iki satır yerine yedi var.

## C. CONFIG hücresinin dört `#@markdown` satırı gitti.

Yerine forma çizilmeyen bir yorum: neden gittikleri, ve kutuların neden boş geldiği *(`/content`
runtime ile ölüyor, yani her model her açılışta yeniden iniyor)*.

`PHOTO_*` ve `INSTALL_*` satırlarına dokunulmadı — desen `=` öncesinde tam bir boşluk, `False` ile
`#@param` arasında iki boşluk istiyor, ve hizalama yok.

## D. Koşuldu: **739 yeşil, 0 kırmızı.**

`python -m pytest queen-editor -q` — kırmızı döndü. Toplam yine 739: bir test silindi, bir test
eklendi.

CONFIG hücresini okuyan öteki beş bekçi yeşil kaldı: `test_every_producer_has_a_checkbox_of_its_own`,
`test_every_photo_model_has_a_checkbox_of_its_own`, `test_every_photo_model_comes_switched_off`,
`test_choosing_photo_without_a_model_stops_the_notebook`, `test_the_form_separates_the_two_groups_of_boxes`.

`npm test --prefix queen-editor/frontend` — **28 dosya, 587 yeşil.**

**Takımın söyleyemediği şey duruyor:** satırların gittiği doğrulandı, panelin nasıl göründüğü
değil. Onu yalnız Colab söyler.

## E. Tek commit.

`queeneditor.ipynb`, test dosyası, bu maddenin iki belgesi, ve yol haritasının 144 ile 145 kayıtları.

`dist` derlenmiyor: ön yüz değişmiyor.

## Bilerek yapılmayanlar

**Giriş hücresi** — şikâyet form panelineydi; defterin açılış metni okumak için durulan yer.

**`BRANCH` satırındaki bayat yorum** *("the Madde 138 trial")* — sorusu sorulmuş, cevabı gelmemiş;
bu maddenin işi değil.

**`skip` / `xfail` yok.**
