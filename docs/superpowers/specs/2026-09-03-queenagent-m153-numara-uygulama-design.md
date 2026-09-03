# Madde 153 — Uygulama turu tasarımı: kare kendi numarasını taşır

**Tarih:** 3 Eylül 2026 · **Tool:** queen-agent · **Tur:** uygulama *(yeşile götürür)*
**Kaynak:** [v7 yol haritası](../plans/2026-09-03-v7-roadmap.md), Madde 153 ·
[test turu tasarımı](2026-09-03-queenagent-m153-numara-testler-design.md)

---

## Altı kırmızı, tek bir yer

Hepsi `_add_frames`'in yazmadan hemen önceki anını bekliyor.

## `_renumber(frames)`

Listeyi baştan sona geçip her kareye sırasını basıyor, ve **numarayı başa alıyor**.

```python
def _renumber(frames):
    for place, frame in enumerate(frames, start=1):
        ...  # frame yerinde yeniden kuruluyor: {"frame": place, **kalanlar}
```

**Yerinde kurulması gerekiyor**, çünkü var olan bir karede `frame` zaten olabilir ve sözlükte
anahtar sırası ilk yazıldığı yerde kalır — üstüne yazmak numarayı güncellerdi ama başa almazdı.
Dosyayı açan kişi için numaranın ilk satırda olması bu maddenin yarısı.

**Hepsine birden basılıyor, yalnız yenisine değil.** Numaranın sıraya eşit kalmasını sağlayan tek
şey bu, ve o eşitlik numaranın bir kimlik değil damga olmasının tanımı.

**Ayrı bir fonksiyon**, çünkü 155 ve 157 kendi araçlarını eklerken aynı yerden geçecekler — kareler
listesine dokunan her yol buradan çıkacak.

## Çağrıldığı yer

`_add_frames` içinde, `frames.append(...)`'ten sonra ve `file_store.write(...)`'tan önce. Tek yer,
çünkü bugün kareler listesine dokunan tek araç bu.

## Cevap

```
Added frame 3 to scene.json.
```

Numara `len(frames)` — boşluk olmadığı için son karenin numarası listenin uzunluğu. İki ayrı sayı
söylemek gürültü olurdu.

`outcome` `1 frame` olarak kalıyor: kart bir kare girdiğini söylemeye devam ediyor.

## Dokunulmayanlar

- **Araç tanımı.** `frame` bir parametre değil ve olmayacak; 152'nin kapalı kümesi onu zaten
  reddediyor.
- **`build_prompts`.** Alanları adıyla okuyor, tanımadığını görmüyor — numara promptta hiç
  görünmüyor ve bunu söyleyen test bugün de yeşil.
- **`schema.py`.** Model numarayı ne yazıyor ne de veriyor; şemaya girmesi ona yazabileceğini
  öğretmek olurdu.
- **Numarasız eski dosyalar.** Bir araç kareler listesine dokunana kadar öyle kalıyorlar.

## Nasıl bakılacak

```
python -m pytest queen-agent -q
```

Altı kırmızı yeşile döner; defterin iki kırmızısı bilerek duruyor.
