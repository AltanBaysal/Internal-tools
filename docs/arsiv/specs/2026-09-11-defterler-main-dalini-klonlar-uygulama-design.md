# Defterler `main` dalını klonlar — UYGULAMA turu spec'i

**Kaynak:** [TEST turu spec'i](2026-09-11-defterler-main-dalini-klonlar-testler-design.md) ve onun
commit'lediği dört kırmızı test. Sözleşme onlardan gelir, burada yeniden karar verilmez.

## Testlerin istediği

| Test | İstediği metin |
|---|---|
| queen-agent, `test_the_notebook_clones_the_branch_this_run_is_tried_on` | `queenagent.ipynb`'nin CONFIG hücresinde `BRANCH       = "main"` |
| queen-agent, `test_no_other_branch_name_is_left_lying_in_the_notebook` | defterin hiçbir hücresinde `feat/...` ile başlayan kelime yok |
| queen-editor, `test_the_notebook_clones_the_branch_this_tool_is_served_from` | `queeneditor.ipynb`'de `BRANCH       = "main"` |
| queen-editor, `test_no_other_branch_name_is_left_lying_in_the_notebook` | aynısı, queen-editor defteri için |

`BRANCH` ile `=` arasındaki yedi boşluk sözleşmenin parçası: testler tam metni arıyor.

## Değişen satırlar

**queen-agent/queenagent.ipynb, CONFIG hücresi.** `BRANCH` değeri `main` olur. Üstündeki yorum şu
an "bu satır denenen turu gösteriyor" diyor — satır `main`'i gösterdiği anda bu yanlış olur, ve bir
yorum yalnız şu an doğru olanı söyler. Yeniden yazılır: kural aynı kalır (bir deneme turu kendi
dalını yazar, tur inince geri gelir), ama varsayılanın `main` olduğunu söyleyerek.

**queen-editor/queeneditor.ipynb, CONFIG hücresi.** `BRANCH` değeri `main` olur. Satır sonundaki
`# DEV RUN: the Madde 138 trial. Back to main when it lands.` kalkar: o tur indi, cümle artık
olmayan bir denemeyi anlatıyor. Yerine satırın şu andaki halini söyleyen kısa bir not. Üstündeki
yorum bloğuna, queen-agent'ta olduğu gibi, adı tutan testin dosya adı eklenir — iki yerde duran bir
adın ikinci yerini okuyan kişi nerede olduğunu bilsin.

## Bu turda yapılmayan

- **Test dosyalarına dokunulmaz.** Kırmızıyı yeşile çeviren şey defterler.
- Dal adı hâlâ iki yerde (sabit + defter) ve `main` üzerinde eski bir `feat/` adı hâlâ kendi başına
  hiçbir testi düşürmüyor — TEST spec'inin "bilerek yapılmayan" bölümü aynen geçerli.
- Defterlerde başka hiçbir şey değişmiyor: ne hücre sırası, ne assert'ler, ne çıktı metinleri.
- Frontend `dist/` yeniden derlenmiyor: değişen tek şey defterlerin kendi metni, arayüz değil.

## Nasıl görülecek

Dört komut yeşil. Colab tarafında görülecek şey `main`'deki defterin artık `main`'i klonlaması, ve o
yalnız push'tan sonra görülebilir.
