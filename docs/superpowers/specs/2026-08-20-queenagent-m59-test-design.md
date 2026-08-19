# Madde 59 · Tur 1 (test) — Tasarım

**Madde:** [v4 yol haritası Madde 59](../plans/2026-08-20-queenagent-v4-colab-roadmap.md)
**Bu belgenin konusu:** yarım kalmayan bir yazmayı **ne tutacak**.

---

## Bugünkü hâl

[store.py:27](../../../queen-agent/backend/services/store/store.py#L27) tek yazma yolu:

```python
with open(full, "w", encoding="utf-8") as handle:
    handle.write(text)
```

`open(..., "w")` dosyayı **açar açmaz siler**. Yazma o noktadan sonra düşerse geriye boş ya da yarım
bir dosya kalır, ve eski içerik yoktur.

Bu, FOUNDATION'ın 1. ilkesiyle ("kullanıcının emeği kutsaldır") çarpışıyor. Yerel diskte pencere
mikrosaniye ve işletim sistemi nadiren düşer; Drive FUSE'da I/O hatası olağan bir olay, ve her mesaj
`<chat>.json`'ın tamamını yeniden yazıyor — yani pencere sohbet başına iki kere, her turda açılıyor.

## Testin sorması gereken üç şey

**1. Düşen bir yazma, üstüne yazdığı dosyayı bozmaz.**
Asıl güvence bu. Yazma gerçekten düşmeli — sahte bir hata enjekte edilerek değil, yazmanın kendisi
patlayarak. Bunun temiz yolu **kodlanamayan bir metin**: `"\ud800"` bir yalnız vekil (lone
surrogate), utf-8'e çevrilemez ve `handle.write` sırasında `UnicodeEncodeError` verir. Gerçek bir
hata, yamasız.

**2. Düşen bir yazma arkasında bir şey bırakmaz.**
Geçici dosya çöptür, delil değil — ve bu klasörler **arayüzde listeleniyor**
(`file_file_store.list_names` doğrudan `files/` dizinini okuyor). Kalan bir `.writing` dosyası
kullanıcının dosya listesinde görünür. Başarılı yazmadan sonra da aynı şey geçerli.

**3. Geçici dosya hedefinin yanında doğar.**
En kolay gözden kaçan ve Colab'da en pahalıya patlayan kural. `os.replace` **dosya sistemi
geçemez**; Colab'da kök bir Drive bağlaması, `/tmp` ise yerel disk. Geçici dosya sistemin temp
dizinine yazılırsa taşıma her seferinde `OSError` verir — ve bu, yerel makinede hiç görünmez.

Doğrudan sorulur: `os.replace`'in aldığı iki yol yakalanır ve aynı dizinde oldukları görülür.

## Sorulmayan

**Eşzamanlılık.** "Okuyan hiçbir zaman yarım dosya görmez" güvencesi `os.replace`'in atomikliğinden
geliyor; bunu deterministik bir testle göstermek yarış kurmayı gerektirir ve kırılgan bir test verir.
İşletim sisteminin garantisine dayanılıyor, ve bu burada yazılı olduğu için bilerek dayanılıyor.

## Nerede duracaklar

`test_store.py`'nin içinde, mevcut Store testlerinin yanında. Yeni dosya açılmaz: sorulan şey
Store'un yazma davranışı, ve o dosyanın konusu tam olarak bu.
