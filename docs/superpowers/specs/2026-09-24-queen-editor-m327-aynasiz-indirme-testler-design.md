# Madde 327 — İndirmede HF aynası dosya başına kapanabiliyor, test turu

**Koşu:** [Queen Editor v7](../roadmaps/2026-09-21-queen-editor-v7-roadmap.md) · **Dal:**
`feat/queen-editor-v7` · **Tur:** 1/2 — yalnız testler, kırmızı commit'lenir.

**Kullanıcıdan gereken — yok.** Deneme kullanıcının, 328'le birlikte: aynası kapanan ilk dosya o.

## Bugün ne oluyor

`civitai_fetch` her Civitai dosyasını önce aynada arıyor *(`hf_fetch`, yol `<sürüm no>/<ad>`)*;
alınamazsa HF'nin cümlesini basıyor, dosyayı Civitai'den indiriyor ve aynaya yüklüyor *(madde 311)*.
Bir dosyayı bunun dışında tutmanın yolu yok.

## Kural

**`colab/downloads.py`'de aynasız dosyaların listesi var: `MIRRORLESS`.** Listedeki bir dosya için
ayna hiç kullanılmıyor — ne aranıyor ne yükleniyor. Dosya Civitai'den bugünkü yoldan iniyor
*(çerez, yoklama, `curl`)*, satırı özete giriyor *(madde 312)*, ve konsol onun aynasız indiğini
dosyanın adıyla söylüyor. Listede olmayan dosya bugünkü gibi. **Liste bu maddede boş**, yani bugünkü
dosyaların hiçbiri etkilenmiyor; ilk girdiyi 328 ekliyor. **Defter değişmiyor** *(kullanıcı —
"Notebook'a hiçbir şey eklenmesin")*, yani `civitai_fetch`'in çağrılışı da.

**Çerezsiz aynasız dosya Civitai'ye gitmeden duruyor**, 311'deki gibi — ama cümle *"aynada yok"*
demiyor: aynaya sorulmadı, ve olmayan bir sebep yazılmaz *(CLAUDE.md, Style)*.

**Liste dosya adıyla tutuluyor, Civitai sürüm no'suyla değil.** Sürüm no dosyanın adresi —
`civitai_url` onu adrese çeviriyor — ve adresler defterde duruyor *(FOUNDATION 9)*; CODE-STANDARD
bir adresi iki yerin bilmesini yasaklıyor. Ad adres değil, ve adlar zaten birden çok yerde duruyor
*(üreticiler paneli)*. Ad bir de yorumsuz okunuyor: `"MysticXXX_MMH3-V4.safetensors"` hangi dosya
olduğunu söylüyor, `3266628` söylemiyor. Bedeli: aynı adı taşıyan iki Civitai dosyası tek anahtarı
paylaşır — bugünkü listelerde ad tekrar etmiyor.

## Yazılacak testler

### `test_colab_downloads.py` — `civitai_fetch`, koşularak

Ağ 311'in sahteleriyle: `_mirror`, `_transfer`, `_probe`. Liste testte `monkeypatch` ile kuruluyor.

1. **Aynası kapalı dosya, aynada dursa da Civitai'den iniyor** — ayna dosyayı tutuyor; yine de tek
   indirme `curl`, istekte çerez var, ve satır bu inişin. Aynaya sorulsaydı dosya oradan gelirdi:
   aramanın olmadığını en açık bu gösteriyor.
2. **Aynası kapalı dosya aynaya yüklenmiyor** — Civitai'den indikten sonra yükleme yok.
3. **Konsol dosyanın aynasız indiğini söylüyor** — bir satırda dosyanın etiketi ve `aynasız`; HF'nin
   cümlesi *(`Entry Not Found`)* konsolda yok.
4. **Çerezsiz aynasız dosya Civitai'ye gitmeden duruyor** — hata `CIVITAI_COOKIE`'yi ve dosyayı
   adlandırıyor, `aynada yok` demiyor; ne yoklama ne indirme.
5. **Bir dosyanın aynası kapanınca ötekiler aynada kalıyor** — listede başka bir dosya varken
   aynadaki dosya HF'den iniyor, Civitai'ye gidilmiyor.

Beşi de bugün `MIRRORLESS` adı olmadığı için kırmızı: `monkeypatch.setattr` var olmayan bir adı
kurmuyor *(`AttributeError`)*.

**Değişen — yok.** Varsayılan açık; 311'in testleri listeye dokunmuyor ve modülün kendi listesiyle
koşuyor.

**Sorulmayan:** listenin boş olduğu — 328 ilk girdiyi ekleyince kırılacak bir test veri sorardı,
davranış değil; bugünkü dosyaların etkilenmediğini bekçiler tutuyor. Yerinde duran aynasız bir dosya
da ayrıca sorulmuyor: `fetch` onu kendi `zaten var`'ıyla yeniden indirmiyor.

**Bekçiler, bugün de yeşil:** 311'in altı ayna testi ve
`test_a_civitai_file_hands_back_the_row_of_the_road_it_took` — aynası açık dosya bugünkü gibi;
defterin `test_civitai_files_come_down_through_the_mirror` ve
`test_every_name_the_notebook_imports_from_its_code_exists` — defter ve çağrılışı değişmiyor.

## Bitti sayılır

Dört test satırı koşulur; `queen-editor` pytest kırmızı — yalnız 1–5, `MIRRORLESS` olmadığı için.
Geri kalan her şey yeşil.
