# Defterin adı aracının adı olsun · Tur 1 (test) — Plan

**Tasarım:** [2026-09-01-defter-adi-testler-design.md](../specs/2026-09-01-defter-adi-testler-design.md)
**Dal:** `feat/defter-adi` *(`main`'den)*
**Bu tur yalnız test dosyalarına dokunur.** Defter taşınmaz, `useProducers.js` değişmez, `dist`
derlenmez — hepsi ikinci turun işi.
**Test komutları (değişmez, dördü de):**
`python -m pytest queen-agent -q` · `npm test --prefix queen-agent/frontend`
`python -m pytest queen-editor -q` · `npm test --prefix queen-editor/frontend`

## A. `queen-editor/backend/tests/test_notebook_installs_the_producer_groups.py`

Bugün tek satır:

```python
NOTEBOOK = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "app.ipynb")
```

Yerine, aracın klasörü ayrı bir isim alıyor — yeni test onu klasör adını okumak için kullanacak:

```python
TOOL = os.path.dirname(          # queen-editor
    os.path.dirname(             # backend
        os.path.dirname(os.path.abspath(__file__))))  # tests
NOTEBOOK = os.path.join(TOOL, "queeneditor.ipynb")
```

Ve dosyanın sonuna, kuralın kendisi:

```python
def test_the_notebook_carries_the_tool_s_own_name():
    """Colab shows a notebook by its file name alone -- the title inside it never reaches the tab.
    Two tools open at once are told apart by that name and nothing else, and Run all in the wrong
    tab clones the wrong repo and starts the wrong app. Read from the folder rather than written
    down, so renaming a tool carries the rule with it.
    """
    found = sorted(name for name in os.listdir(TOOL) if name.endswith(".ipynb"))

    assert found == [os.path.basename(TOOL).replace("-", "") + ".ipynb"], \
        f"Defterin adı aracının adı değil: {found}"
```

- [ ] **A.1** `TOOL` ayrılır, `NOTEBOOK` yeni adı gösterir.
- [ ] **A.2** Test eklenir.

## B. `queen-agent/backend/tests/test_notebook.py`

Aynı `TOOL` ayrımı, aynı test — **tek fark defterin adı**, ve o da klasörden okunduğu için testin
metni birebir aynı kalıyor. Kopya bilerek: iki araç iki ayrı `pytest` koşusu, ve aralarında paylaşılan
bir yardımcı yok.

`NOTEBOOK`'un üstündeki `# Not app.ipynb: …` yorumu **bu turda ellenmiyor.** Bugün hâlâ doğru —
queen-editor'ün defteri bu turun sonunda hâlâ `app.ipynb`. Uygulama turunda ad değişince yanlışa
döner ve orada yeniden yazılır.

- [ ] **B.1** `TOOL` ayrılır, `NOTEBOOK` ondan türer *(ad `queenagent.ipynb` olarak kalır)*.
- [ ] **B.2** Aynı test eklenir — **ilk anda yeşil**, çünkü kural burada zaten tutuyor.

## C. Ön yüz — adı sabitleyen test yok, o yüzden yazılıyor

Plan `QueuePanel.test.jsx`'teki cümleyi değiştirip kırmızı bekliyordu. **Beklenti yanlıştı**:
`InstallCard`, `ProducersPanel` ve `useProducers` testlerinin tamamı `COLAB_INSTALL` **sabitinin
kendisini** okuyor, `QueuePanel`'inki de yalnız `"Colab defterinden kurulur"` parçasını arıyor. Yani
sabit hangi defter adını taşırsa taşısın hepsi yeşil — kullanıcıya gösterilen ad ön yüzde hiçbir
şeyin koruduğu bir şey değil.

`queen-editor/frontend/src/features/producers/useProducers.test.jsx` — sabitin metnine bakan tek
test:

```js
it("names the notebook the user actually has to open", () => {
  // The sentence IS the whole answer Kur gives, and it sends the user to a file by name. Pinned
  // here and nowhere else: every other test reads the constant, so it would agree with whatever
  // name the constant carried -- including one that is not in the repo any more.
  expect(COLAB_INSTALL).toContain("queeneditor.ipynb");
});
```

- [ ] **C.1** Test eklenir — **kırmızı**, sabit bugün `app.ipynb` diyor.
- [ ] **C.2** `QueuePanel.test.jsx`'teki kopya cümle de yeni adı yazar. Kırmızı üretmiyor *(o test
      cümlenin yalnız baş tarafını arıyor)*; düzeltiliyor çünkü elle yazılmış bir kopya ve yanlış
      kalırsa okuyanı yanıltır.

## D. Koşuldu: **21 kırmızı**, tam planlanan yerlerde

| Komut | Sonuç |
|---|---|
| `python -m pytest queen-editor -q` | **20 kırmızı**, 701 yeşil |
| `python -m pytest queen-agent -q` | 659 yeşil |
| `npm test --prefix queen-editor/frontend` | **1 kırmızı**, 586 yeşil |
| `npm test --prefix queen-agent/frontend` | 570 yeşil |

queen-editor'ün 20'si tek dosyadan: `NOTEBOOK` artık var olmayan bir yolu gösterdiği için o
dosyadaki 19 testin hepsi `FileNotFoundError` veriyor, ve 20.'si yeni ad testi. Bu geniş kırmızı
kasten — defterin taşınması onların hepsini birden yeşile döndürecek, yani ikinci turun taşımayı
gerçekten yaptığını gösteren şey bu.

queen-agent'ta hiç kırmızı yok ve olması da beklenmiyordu: aynı test orada **ilk anda yeşil**, çünkü
`queenagent.ipynb` kurala zaten uyuyor. 659 sayısı 658'e o yeşili ekliyor.

### Kırmızının kendisi de ölçüldü

Ön yüzün kırmızısı, sabitin bugün ne dediğini olduğu gibi bastı:

```
Received: "Bu üretici Colab defterinden kurulur — app.ipynb'de kutusunu işaretleyip çalıştır."
```

Yani test doğru şeye bakıyor: kullanıcıya gösterilen cümlenin içindeki dosya adına.

## E. Kırmızı commit.

## Bilerek yapılmayanlar

`skip`/`xfail` yok. Defter taşınmaz. `useProducers.js`, `README.md`, `CODE-STANDARD.md`,
`config.py`, `storage.py`, `dist/` ellenmez.
