# Defterin adı aracının adı olsun · Tur 2 (uygulama) — Plan

**Tasarım:** [2026-09-01-defter-adi-uygulama-design.md](../specs/2026-09-01-defter-adi-uygulama-design.md)
**Dal:** `feat/defter-adi` *(tur 1'in üstüne)*
**Test dosyalarına dokunulmuyor.** Tur 1'de commit'lenen 21 kırmızının yeşile dönmesi bu turun
ölçüsü; testi değiştirmek ölçüyü değiştirmek olur.
**Test komutları (değişmez, dördü de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. Taşıma

- [ ] **A.1** `git mv queen-editor/app.ipynb queen-editor/queeneditor.ipynb`

Tek başına queen-editor'ün 20 kırmızısını yeşile döndürmesi bekleniyor.

## B. Defterin kendi metni — `NotebookEdit`, hücre `34c9ff58`

Kullanım adımlarının ilki:

```
1. Bu `app.ipynb`'yi Colab'a yükle (**File → Upload notebook**).
```

→ `queeneditor.ipynb`. Hücrenin geri kalanı aynen kalır.

- [ ] **B.1** `NotebookEdit` ile *(elle JSON değil — dosyanın ayrıştırılabilir kalması testin
      okumasının şartı)*.

## C. Ekranda görünen cümle

`queen-editor/frontend/src/features/producers/useProducers.js`:

```js
"Bu üretici Colab defterinden kurulur — queeneditor.ipynb'de kutusunu işaretleyip çalıştır."
```

- [ ] **C.1** `COLAB_INSTALL` yeni adı söyler. Ön yüzün tek kırmızısı bununla yeşile döner.

## D. Adı anan belgeler ve yorumlar

- [ ] **D.1** `queen-editor/README.md` — iki yer *(giriş paragrafı, "Before the first run"un ilk
      cümlesi)*.
- [ ] **D.2** `queen-editor/CODE-STANDARD.md` — üç yer. `api.ipynb` ve `photo_to_video.ipynb`
      **ellenmiyor**: onlar `collab-toolbox`'ın defterleri.
- [ ] **D.3** `queen-editor/backend/config.py` — `DRIVE_ROOT`'un üstündeki yorum.
- [ ] **D.4** `queen-editor/backend/services/drive/storage.py` — modül docstring'i.

## E. queen-agent'ın bayatlayan yorumu

`NOTEBOOK`'un üstündeki `# Not app.ipynb: …` bloğu **siliniyor**. Gerekçe artık
`test_the_notebook_carries_the_tool_s_own_name`'in docstring'inde, ve iki araçta da aynı cümlelerle;
`NOTEBOOK`'un başında ikinci bir kopya tutmak, bugün yanlışa düşen şeyin ta kendisiydi.

- [ ] **E.1** Yorum kalkar, `NOTEBOOK = os.path.join(TOOL, "queenagent.ipynb")` yalın kalır.

## F. Derleme

- [ ] **F.1** `npm run build --prefix queen-editor/frontend` — `dist` kaynakla aynı commit'e girer.

## G. Koşuldu: dördü de yeşil

| Komut | Sonuç |
|---|---|
| `python -m pytest queen-editor -q` | 721 yeşil |
| `python -m pytest queen-agent -q` | 659 yeşil |
| `npm test --prefix queen-editor/frontend` | 587 yeşil |
| `npm test --prefix queen-agent/frontend` | 570 yeşil |

Tur 1'in 21 kırmızısının hepsi döndü, ve sayılar da o turun sayıları: 701+20 = **721**, 586+1 =
**587**. Yani yeşile dönen tam olarak kırmızı olanlar — araya yeni bir test girmedi, hiçbiri
atlanmadı.

### Adı anan bir yer kaldı mı

`docs/` dışında depoda `app.ipynb` geçen tek bir satır kalmadı — arandı, hiç eşleşme yok. `docs/`
altındakiler bilerek duruyor *(tasarım)*.

## H. Commit

Tek commit: taşıma + defter + kaynak + belgeler + `dist`. Mesajda **tur 1'in commit başlığındaki
`@` bozukluğuna düzeltme notu** düşülür — geçmiş ellenmiyor *(kullanıcının kararı, 1 Eylül)*, o
yüzden not bir sonraki mesajda duruyor.

## Bilerek yapılmayanlar

Test dosyaları, `docs/superpowers/` altındaki geçmiş kayıtlar, defterin ad dışındaki içeriği.
