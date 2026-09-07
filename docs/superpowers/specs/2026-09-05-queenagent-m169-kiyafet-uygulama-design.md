# Madde 169 · uygulama turu — kıyafet yönetimi

**Kaynağı:** [test turu spec'i](2026-09-05-queenagent-m169-kiyafet-testler-design.md).
Commit `8473333` 18 vak'ayı çiviledi.

---

## Üç değişiklik, ve üçü de `which`'e dallanıyor

### 1 · `_frames_naming` — kıyafet dalı

Karakter için `cast_of`'un **adları**; kıyafet için o adların **listelerinin içi**. Aynı fonksiyon,
`which`'e bakan bir satır: bir karenin kadrosu zaten `(ad, kıyafetler)` çiftleri olarak geliyor, yani
iki soru da tek okumadan cevaplanıyor.

### 2 · `_renamed_in_frames` — kıyafet dalı

Karakter dalı anahtarı değiştiriyor; kıyafet dalı **değerin içindeki adı**. İki şekilde de:
listedeki bir eleman, ve tek adın listesiz yazıldığı hâl — ikincisinde yerine yazılan da listesiz
kalıyor, çünkü **bir yeniden adlandırma bir dönüştürme değil.** Kimsenin istemediği bir biçim
değişikliği, dosyayı açan kullanıcının tanımadığı bir dosya demek.

### 3 · Ret fiili bir eşleme oluyor

```python
_STILL_USED_IN = {
    "characters": "is still in frames",
    "outfits": "is still worn in frames",
    "locations": "is still the place in frames",
}
```

Üçü ayrı cümle çünkü üçü ayrı ilişki. Tek yerde, çünkü üç ayrı yerde duran üç cümle ayrı ayrı
bayatlar. `"locations"` satırı bugün kullanılmıyor — **170'in testleri onu çalıştıracak**, ve
eşlemenin tamamını burada yazmak üç satırlık bir tabloyu iki turda bölmekten iyi.

## Araç tanımları

Üç tanım, `add_character`'ın üçünün ardında. Açıklamaların taşıdığı fark:

- **Kıyafet kişi tarif etmiyor.** *No person here* — kim giydiği karenin işi, ve iki kişiyi birden
  giydiren tek girdi ikisinin kıyafetini birbirine karıştırır.
- **Sayı yok.** Kaç kişi olduğu karakterin girdisinde.
- **Silme reddi kimin giydiğini söylüyor**, kareyi değil sadece.

## `modes.py` ve `run_tool`

Üç ad `_WITHOUT_ASKING[EDIT]`'e; üç dal `run_tool`'a, karakterin üçünün ardında ve aynı gövdeleri
`"outfits"` ile çağırarak.

---

## Doğrulama

1. Dört sabit test satırı, sırayla, birebir.
2. **Beklenen: 18 kırmızının 18'i de yeşil**, `queen-agent` tarafında **743 yeşil** *(725 + 18)*.
3. Karakter testleri yeşil kalmalı: `_frames_naming` ve `_renamed_in_frames` dallandı, karakter
   yolu değişmedi. Düşerse dallanma karakteri de kesmiştir.
4. Öteki üç takım rakamlarını korur. `dist` derlenmez.

## Koşarken çıkan iki şey

**İngilizce belirteç.** Ortak gövde *"A {tekil} needs a name"* yazıyordu, ve `outfit` sesli harfle
başlıyor: *"A outfit"*. Üç harita üstünde tek cümle kullanmanın bedeli, ve `_article` ile ödendi —
tekil hâl gibi, bu da tek yerde.

**queen-editor'ün ön yüzünde bir flake.** `LayerPlayer > loops the video and starts paused` 5740ms
ile 5000ms'lik tavanı aştı. Bu koşu queen-editor'e hiç dokunmuyor; birebir tekrar koşuldu ve **591
yeşil** geldi. Makine yüküydü, kayda geçiyor.
