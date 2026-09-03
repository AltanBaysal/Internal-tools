# Madde 154 — Uygulama turu tasarımı: dosyayı doğuran ve haritaları dolduran araçlar

**Tarih:** 3 Eylül 2026 · **Tool:** queen-agent · **Tur:** uygulama *(yeşile götürür)*
**Kaynak:** [v7 yol haritası](../plans/2026-09-03-v7-roadmap.md), Madde 154 ·
[test turu tasarımı](2026-09-03-queenagent-m154-haritalar-testler-design.md)

---

## On sekiz kırmızı, üç dosya

`tools.py` dört araç kazanıyor, `build_prompts.py` karakter girdisinin iki şeklini okumayı
öğreniyor, `modes.py`'nin `edit` listesi dört ad daha alıyor.

---

## `tools.py` — `structure_name`

```python
def structure_name(name):
    return f"{stem}.json"
```

`safe_name`'den sonra koşuyor: temizlemek onun işi, uzantıyı dayatmak bunun. `plan_name`'in
`write_plan` için yaptığının aynısı, ve aynı sebeple — araç kendi kuralına uymayan bir ad
üretemesin.

## `tools.py` — `create_structure`

Boş dört şeyi yazıyor, adı doluysa reddediyor, `created` dolduruyor.

`WRITES_FILES` kümesine giriyor: dosya doğuran araçlar kart çiziyor, ve bu araç dosya doğuruyor.

## `tools.py` — üç `set_` aracı, tek bir gövde

Üçü de aynı işi yapıyor: **bir haritada bir adın metnini yazmak.** Ayrı araç olmalarının sebebi
modele bakan taraf — adları, açıklamaları ve kuralları farklı. Kodun tarafında farkları yok, o yüzden
tek bir `_set_entry(file_store, project_id, args, which, value)` gövdesi:

- `which` — hangi harita
- `value` — girdiye yazılacak şey; karakterde `{"kind": …, "tags": …}`, diğer ikisinde düz metin

**Neden kod tarafında birleşiyor:** üç kopya, ilk değişiklikte üçe ayrılır. Modelin gördüğü üç ayrı
araç olması ile kodun tek bir yerden yazması birbiriyle çelişmiyor — biri sözleşme, diğeri tesisat.

**Sırayla:** dosya var mı → JSON okunuyor mu → ad boş mu → *(karakterse)* `kind` geçerli mi →
harita var mı *(yoksa doğuyor)* → yaz.

**Cevap:**

- Yeni: `Added lara to characters.`
- Var olan: `Changed aylin in characters; 2 frames name it.`

Kaç kare olduğu yalnız değişiklikte söyleniyor — yeni bir adı hiçbir kare anmıyor, ve `0 frames`
demek modele cevaplamadığı bir soruyu düşündürürdü.

`outcome`: `Added` / `Changed`.

## `tools.py` — `kind` kapalı küme

`("girl", "boy")`. Başkası reddediliyor ve cevap ikisini sayıyor.

Modül seviyesinde bir sabit, çünkü 156'nın sayımı aynı kümeden okuyacak.

## `build_prompts.py` — bir karakter girdisi iki şekilde okunuyor

```python
def _identity(entry):
    return entry.get("tags", "") if isinstance(entry, dict) else entry
```

`_looked_up` bulduğu şeyi olduğu gibi döndürüyor; aradaki bu adım metni çıkarıyor.

**İki yerde de gerekiyor** — `_block` üzerinden `build_prompts`, ve doğrudan
`build_character_prompts`.

**`kind` prompta girmiyor.** Sayım için var *(156)*, ve bir promptun içinde `girl` kelimesi karenin
kendi sayısıyla çakışırdı.

## `modes.py`

Dört ad `EDIT`'in listesine giriyor. `ask` ve `plan` onları listelemiyor, yani soruyorlar — kullanıcının
dosyasını değiştiren her araç gibi.

## Dokunulmayanlar

- `schema.py`. Şema hâlâ eski karakter şeklini gösteriyor — **bilerek**: 159 şemayı tamamen emekli
  ediyor, ve arada örneği güncellemek iki kez yazmak olurdu. Model zaten şekli yazmıyor, araçları
  çağırıyor.
- `skills.py`. Akış metinleri 155'te baştan yazılıyor.
- `add_frames`. Karakter adlarını haritada arıyor; girdinin şekli onu ilgilendirmiyor.

## Nasıl bakılacak

```
python -m pytest queen-agent -q
```

Defterin iki kırmızısı dışında hepsi yeşil.
