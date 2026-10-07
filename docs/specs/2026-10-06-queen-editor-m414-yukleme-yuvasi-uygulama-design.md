# Madde 414 — Yüklenen resim tıklanan yuvaya, uygulama turu

**Koşu:** [Queen Editor v9](../roadmaps/2026-10-05-queen-editor-v9-roadmap.md) · **Dal:**
`feat/queen-editor-v9` · **Parça:** 414 · v9-6 · **Tur:** 2/2 — kod, takım yeşile döner.
**Testler:** [m414 test turu](2026-10-06-queen-editor-m414-yukleme-yuvasi-testler-design.md),
`a2db981e` ile kırmızı commit'lendi — kurallar ve sebebin izi orada.

**Kullanıcıdan gereken:** yok.

## Sebep — kanıtlandı

**Yüklenen dosyanın yeri sıra belgesine hiç yazılmıyor
*([add_references.py:60-64](../../queen-editor/backend/features/photo_generation/domain/usecases/add_references.py))*,
ve `placed` belgede adı olmayan dosyaları ad sırasıyla diziyor
*([references.py:88](../../queen-editor/backend/features/photo_generation/domain/references.py))*:**
hiç sürüklenmemiş bir satırda adı önce gelen yeni dosya 1. yuvaya iniyor.

**Kanıt:** test turunun üç testi kullanıcının adımlarını gerçek kapıdan ve gerçek klasörden yürüdü,
ve üçü de tam bu yerden kırmızı döndü — başka hiçbir test kırmızı değil:
`[('ayse.png', 1), ('zeynep.png', 2)]`, aynı adla `[('kadin-2.png', 1), ('kadin.png', 2)]`.

## Yaklaşımlar

1. **Seçilen — yükleme, dosyanın geldiği satırı sıra belgesine yazar.** Dosyalar yazıldıktan sonra,
   dosya gelen her satır için: satır havuzda o an durduğu gibi *(yuva sırasıyla)*, ardından gelenler
   *(basıştaki sırayla)*. Belgenin öteki satırlarına dokunulmaz. `held` zaten elde — havuz ikinci
   kez okunmuyor, kliplere fazladan `ffprobe` yok.
2. *Elendi —* yüklemede bütün satırları yazmak *(tek satırlık bir sözlük)*: kimsenin sürüklemediği,
   hiçbir şey yüklenmemiş satırların ad sırasını belgeye dondururdu — madde 321'in seçmediği yolun
   sebebi.
3. *Elendi —* belgedeki listeyi olduğu gibi tutup eksik adları sona eklemek: Drive'dan elle silinmiş
   bir adın aynı adla gelen yüklemeyi eski yerine çekmesi sürerdi — `remove_reference` ile
   `save_reference_order`'ın önlemek istediği şey.
4. *Elendi —* adı olmayan dosyaları yazılma zamanıyla dizmek: zaman damgası yazmalardan kaba, ve
   havuz iki makinede farklı okunurdu *([reference_store.py](../../queen-editor/backend/features/photo_generation/data/reference_store.py)'nin
   belgesi)*.
5. *Elendi —* ekranın yüklemeden sonra sırayı göndermesi: kural tarayıcıya girer *(FOUNDATION 4)*,
   ve iki istek arasında havuz başka bir sekmeden değişebilir.

## Dosyalar

### `domain/usecases/add_references.py`

Dosyalar yazıldıktan sonra, `list_references`'tan önce:

```python
order = orders.read(project)
for kind in {row["kind"] for row in arriving}:
    order[kind] = [row["name"] for row in held + arriving if row["kind"] == kind]
orders.write(project, order)
```

- **Dosyalardan sonra:** belge önce yazılıp bir dosya düşseydi, belgede dosyası olmayan ad kalırdı.
  Belge yazılamazsa dosyalar havuzda, yerleri bugünkü gibi ad sırasıyla.
- **Koşulsuz:** dosyasız bir istekte satır yok, belge aynı içerikle yeniden yazılır —
  `remove_reference`'ın da yaptığı.
- Satırın elle silinmiş adları satır yeniden yazılınca düşüyor: `held` yalnız havuzda duranları
  taşıyor.
- Modülün belgesi yeni kuralı ve sebebini söyler *(madde 414)*.

### Doğruluğunu yitiren belgeler

| Dosya | Olacak |
|---|---|
| `references.py` — `placed` | Adı olmayan dosya bir yükleme değil: Drive'dan elle konan, ya da hiçbir şeyin yazmadığı bir satır *(bu maddeden önceki havuzlar)* |
| `reference_order_store.py` — modül | Belge sürüklenen sırayı ve her yüklemenin satırın sonundaki yerini tutar |
| `remove_reference.py` — modül | Elle silinmiş ad artık yüklemeyi eski yerine çekemez — yükleme satırını havuzdan yazıyor; ad sıradan, belge yalnız duran dosyaları adlandırsın diye çıkıyor |
| `save_reference_order.py` — modül | Aynı: hayalet yüklemeyi çekemez; süzgeç belgeyi duran dosyalarla sınırlı tutuyor |

## Bilinçli olarak yapılmayan

- `placed`, ekran, kapı değişmiyor.
- `remove_reference`'ın ve `save_reference_order`'ın süzgeçleri kalıyor — yalnız belgeleri.
- Bir satırı sürüklemenin öteki satırların kaydını silmesi *(test turunun "Bulunan" bölümü)* bu
  maddede değil; koşuya bildirilir.
- `dist` kurulmaz — birleştirme commit'i kurar; yol haritasına dokunulmaz.

## Bitti sayılır

Dört test satırı yeşil; kod, spec ve plan tek commit.
