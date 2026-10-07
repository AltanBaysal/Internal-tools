# Madde 174 · uygulama turu — `update_frame` ve `remove_frame`

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m174-kare-testler-design.md).
Commit `7a24e64` 27 vak'ayı çiviledi.

---

## 173'ün süzgeci ikiye bölünüyor

`_frame_from` doğumda kadroyu ve mekânı sınıyordu; aynı sınama şimdi güncellemede de gerekiyor. İki
parça çıkarılıyor, ve her ikisi de **yazılacak hâli** döndürüyor:

- **`_cast_checked(people, number, structure, problems)`** — şekli sınıyor, adları arıyor, kanonik
  kadroyu döndürüyor *(listesiz kıyafet listeye çevrilmiş hâlde)*. Şekil yanlışsa `None`.
- **`_place_checked(place, number, structure, problems)`** — string mi, haritada var mı.

`_frame_from` ikisini çağırıyor. Böylece **bir kare hangi yoldan gelirse gelsin aynı süzgeçten
geçiyor** — doğarken ve değişirken — ve bir kural iki yerde ayrı ayrı yazılmıyor.

## `_numbered(wanted, source, many)`

Numara sınaması iki aracın da ilk işi, dolayısıyla tek yerde. `(number, refused)` dönüyor,
`_opened`'ın kalıbı.

`bool`, `int`'ten **önce** eleniyor: Python'da `True` bir `int`'tir, ve `frame=True` sessizce 1.
kareyi seçerdi. Rakamdan ibaret string tamsayıya çevriliyor — 173'ün bağışlaması.

## `update_frame` — verilen, verilmeyen, boş verilen

Üçü ayrı: `key in args` **verildi**, yokluğu **verilmedi**, boş değer **temizle**. `.get()` ile
sorulsaydı boş değer verilmemiş sayılırdı ve alan temizlenemezdi.

```python
given = {key: args[key] for key in ("scene", "characters", "location") if key in args}
```

Sıra sabit: cevabın *"scene and location"* deyişi çağrının anahtar sırasına göre değişmesin.

Boş değer alanı **siliyor** (`frame.pop`), yazmıyor. 173'te verilmeyen alan hiç yazılmıyordu;
temizlenen alan da kalmıyor, yoksa dosyada hiçliğin iki yazımı olurdu.

**`action` ve `number` imzada yok.** Birincisi 176'nın; ikincisi karenin yeri, ve yeri yalnız silme
oynatır. **Açıklama `action`'dan hiç söz etmiyor:** bugün onu yazan bir araç yok, ve olmayan bir
aracın adını açıklamaya koymak modele çağıramayacağı bir yol göstermek olurdu. Cümleyi 176 ekliyor —
173'ün aynı kararı.

## `remove_frame` — silen ve yeniden numaralayan

Siliyor, sonra kalanları **yerlerine göre** numaralıyor: `enumerate(frames, start=1)`. Okuyup değil
sayarak, çünkü 173'ten önce yazılmış karelerin `number`'ı yok — sayarak numaralama onları da onarıyor.

Kalan yoksa cümle numaralamadan söz etmiyor: *no frames left.*

Haritalara dokunmuyor. Kullanıcının 5 Eylül kararı: bu uygulamada model kimsenin adına silmiyor.

## Kip

İkisi de `EDIT`'in sormadan koştuğu listeye giriyor; `ask` ve `plan` kapıyı önlerinde tutuyor. Bir
silme, kalan her kareyi de değiştiriyor — kullanıcının okuduğu dosyada bu araçların yaptığı en geniş
değişiklik.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **770 yeşil**, ilk koşuda, tek kırmızı çıkmadan. 27 kırmızının hepsi döndü; 745'ten farkın 25
   olması, 27'nin ikisinin *(bildirim ve kip listesi)* zaten var olan testler olmasından.
3. Öteki üç takım rakamlarını korudu: **586 · 739 · 591.** `dist` derlenmedi.
